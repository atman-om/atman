from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Literal

import httpx

from services.api.app.core.config import Settings

MessageRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str


@dataclass(frozen=True)
class QwenGenerationResult:
    text: str
    model_name: str
    provider: str
    latency_ms: int
    usage: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class QwenRuntimeError(RuntimeError):
    pass


class QwenRuntime:
    """Runtime facade for Atman-Lab-Qwen.

    The default deterministic mode is intentionally offline and dependency-light. Production can switch
    ATMAN_QWEN_RUNTIME_MODE=openai_compatible and point ATMAN_QWEN_BASE_URL to a vLLM/Ollama/LM Studio/TGI
    compatible server exposing /v1/chat/completions. A guarded transformers mode is included but disabled
    unless ATMAN_QWEN_ENABLE_TRANSFORMERS_RUNTIME=true.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.mode = settings.qwen_runtime_mode.strip().lower()
        self.model_id = settings.gemini_model_id if self.mode == "gemini" else settings.qwen_model_id
        self.public_name = settings.runtime_model

    async def health(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model_family": self.settings.model_family,
            "runtime_model": self.settings.runtime_model,
            "qwen_model_id": self.model_id,
            "mode": self.mode,
            "ready": True,
            "network_required": self.mode in {"openai_compatible", "gemini", "transformers"},
            "weights_bundled": False,
        }
        if self.mode == "openai_compatible":
            payload["base_url_configured"] = bool(self.settings.resolved_qwen_base_url)
            payload["api_key_configured"] = bool(self.settings.resolved_qwen_api_key)
            payload["ready"] = bool(self.settings.resolved_qwen_base_url)
        if self.mode == "gemini":
            payload["provider"] = "gemini_openai_compatible"
            payload["gemini_model_id"] = self.settings.gemini_model_id
            payload["base_url_configured"] = bool(self.settings.gemini_base_url)
            payload["api_key_configured"] = bool(self.settings.resolved_gemini_api_key)
            payload["ready"] = bool(self.settings.gemini_base_url and self.settings.resolved_gemini_api_key)
        if self.mode == "transformers":
            payload["enabled"] = self.settings.qwen_enable_transformers_runtime
            payload["ready"] = self.settings.qwen_enable_transformers_runtime
        return payload

    async def generate(
        self,
        messages: Sequence[ChatMessage | dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> QwenGenerationResult:
        started = perf_counter()
        normalized = _normalize_messages(messages)
        warnings: list[str] = []
        try:
            if self.mode == "openai_compatible":
                text, usage = await self._generate_chat_completions(
                    normalized,
                    temperature=self.settings.qwen_temperature if temperature is None else temperature,
                    max_tokens=self.settings.qwen_max_tokens if max_tokens is None else max_tokens,
                    base_url=self.settings.resolved_qwen_base_url,
                    api_key=self.settings.resolved_qwen_api_key,
                    model_id=self.settings.qwen_model_id,
                    missing_base_url_error="ATMAN_QWEN_BASE_URL or ATMAN_LLM_BASE_URL is required",
                    empty_choices_error="OpenAI-compatible Qwen server returned no choices",
                    empty_text_error="OpenAI-compatible Qwen server returned empty text",
                )
                provider = "qwen_openai_compatible"
            elif self.mode == "gemini":
                text, usage = await self._generate_chat_completions(
                    normalized,
                    temperature=self.settings.qwen_temperature if temperature is None else temperature,
                    max_tokens=self.settings.qwen_max_tokens if max_tokens is None else max_tokens,
                    base_url=self.settings.gemini_base_url,
                    api_key=self.settings.resolved_gemini_api_key,
                    model_id=self.settings.gemini_model_id,
                    missing_base_url_error="ATMAN_GEMINI_BASE_URL is required",
                    missing_api_key_error="ATMAN_GEMINI_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY is required",
                    empty_choices_error="Gemini OpenAI-compatible endpoint returned no choices",
                    empty_text_error="Gemini OpenAI-compatible endpoint returned empty text",
                )
                provider = "gemini_openai_compatible"
            elif self.mode == "transformers":
                text, usage = await self._generate_transformers(
                    normalized,
                    temperature=self.settings.qwen_temperature if temperature is None else temperature,
                    max_tokens=self.settings.qwen_max_tokens if max_tokens is None else max_tokens,
                )
                provider = "qwen_transformers"
            else:
                text, usage = self._generate_deterministic(normalized)
                provider = "qwen_deterministic_fallback"
                warnings.append("deterministic_fallback_no_model_weights")
        except Exception as exc:
            text, usage = self._generate_deterministic(normalized)
            provider = "qwen_deterministic_fallback_after_error"
            warnings.extend(["runtime_error_fallback", str(exc)[:240]])
        latency_ms = int((perf_counter() - started) * 1000)
        return QwenGenerationResult(
            text=text,
            model_name=self.model_id if self.mode == "gemini" else self.settings.runtime_model,
            provider=provider,
            latency_ms=latency_ms,
            usage=usage,
            warnings=warnings,
        )

    async def stream_generate(
        self,
        messages: Sequence[ChatMessage | dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        # Stable streaming facade: production can later replace this with true provider streaming.
        result = await self.generate(messages, temperature=temperature, max_tokens=max_tokens)
        for token in _stream_chunks(result.text):
            yield token
            await asyncio.sleep(0)

    async def _generate_chat_completions(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
        base_url: str | None,
        api_key: str | None,
        model_id: str,
        missing_base_url_error: str,
        empty_choices_error: str,
        empty_text_error: str,
        missing_api_key_error: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        if not base_url:
            raise QwenRuntimeError(missing_base_url_error)
        if missing_api_key_error and not api_key:
            raise QwenRuntimeError(missing_api_key_error)
        url = base_url.rstrip("/")
        if not url.endswith("/v1/chat/completions"):
            url = f"{url}/chat/completions" if url.endswith("/openai") else f"{url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        timeout = httpx.Timeout(self.settings.qwen_request_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise QwenRuntimeError(empty_choices_error)
        message = choices[0].get("message") or {}
        content = message.get("content") or choices[0].get("text") or ""
        if not isinstance(content, str) or not content.strip():
            raise QwenRuntimeError(empty_text_error)
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        return content.strip(), usage

    async def _generate_transformers(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, dict[str, Any]]:
        if not self.settings.qwen_enable_transformers_runtime:
            raise QwenRuntimeError("transformers runtime disabled by ATMAN_QWEN_ENABLE_TRANSFORMERS_RUNTIME=false")

        def _sync_generate() -> str:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
                import torch  # type: ignore
            except Exception as exc:  # pragma: no cover - optional dependency path
                raise QwenRuntimeError(f"transformers/torch unavailable: {exc}") from exc

            tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype="auto",
                device_map="auto",
                trust_remote_code=True,
            )
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
            generated = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=temperature > 0,
                temperature=max(temperature, 1e-5),
            )
            output_ids = generated[0][len(inputs.input_ids[0]):]
            return tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        text = await asyncio.to_thread(_sync_generate)
        if not text:
            raise QwenRuntimeError("transformers runtime returned empty text")
        return text, {"runtime": "transformers", "max_new_tokens": max_tokens}

    def _generate_deterministic(self, messages: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
        user_text = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        source_count = prompt.count("[SOURCE:")
        text = (
            "संक्षिप्त उत्तर: यह Atman-Lab-Qwen का deterministic local fallback उत्तर है। "
            "वास्तविक Qwen serving के लिए ATMAN_QWEN_RUNTIME_MODE=openai_compatible और "
            "ATMAN_QWEN_BASE_URL सेट करें।\n\n"
            f"प्रश्न: {user_text[:500]}\n\n"
            "स्रोत-आधारित नीति: Atman केवल उपलब्ध citations के आधार पर उत्तर देगा; "
            "यदि पर्याप्त स्रोत नहीं हैं तो निश्चित शास्त्रीय दावा नहीं करेगा।\n"
            f"उपलब्ध स्रोत-खंड: {source_count}\n"
            f"trace_id: qwen-fallback-{digest}"
        )
        return text, {"prompt_hash": digest, "source_count": source_count}


def build_rag_messages(*, question: str, source_blocks: Sequence[dict[str, Any]], language: str = "hi") -> list[ChatMessage]:
    source_text = "\n\n".join(
        f"[SOURCE:{idx}] title={block.get('title')} locator={json.dumps(block.get('locator', {}), ensure_ascii=False)}\n{block.get('text', '')}"
        for idx, block in enumerate(source_blocks, start=1)
    )
    system = (
        "तुम Atman Acharya हो: Hindi-first, source-governed Dharma AI. "
        "कभी भी fake Sanskrit, fake citation, या unsupported शास्त्रीय claim मत बनाओ। "
        "जहाँ स्रोत अपर्याप्त हो, स्पष्ट अनिश्चितता बताओ। उत्तर सरल हिन्दी में दो।"
    )
    user = (
        f"भाषा: {language}\n"
        f"प्रश्न: {question}\n\n"
        "नीचे केवल स्वीकृत स्रोत-खंड दिए गए हैं। इन्हीं पर आधारित उत्तर दो।\n\n"
        f"{source_text if source_text else '[NO_VERIFIED_SOURCE_BLOCKS]'}"
    )
    return [ChatMessage(role="system", content=system), ChatMessage(role="user", content=user)]


def _normalize_messages(messages: Sequence[ChatMessage | dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for item in messages:
        if isinstance(item, ChatMessage):
            normalized.append({"role": item.role, "content": item.content})
        else:
            role = item.get("role", "user")
            if role not in {"system", "user", "assistant"}:
                role = "user"
            normalized.append({"role": role, "content": str(item.get("content", ""))})
    if not normalized:
        normalized.append({"role": "user", "content": ""})
    return normalized


def _stream_chunks(text: str, *, max_chars: int = 96) -> list[str]:
    chunks: list[str] = []
    current = ""
    for part in text.split(" "):
        candidate = f"{current} {part}".strip()
        if len(candidate) > max_chars and current:
            chunks.append(current + " ")
            current = part
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
