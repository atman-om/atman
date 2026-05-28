from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from services.api.app.domain.enums import ContentReviewStatus
from services.api.app.services.safety import evaluate_query_and_answer


class ChunkLike(Protocol):
    chunk_id: str
    locator: dict[str, Any]
    text: str


class SettingsLike(Protocol):
    model_family: str
    content_model: str
    content_max_batch_items: int
    content_min_source_coverage: float


@dataclass(frozen=True)
class GeneratedContentDraft:
    title: str
    body: str
    item_index: int
    provenance: dict[str, Any]
    quality_report: dict[str, Any]


def source_basis(chunks: Sequence[ChunkLike]) -> str:
    if not chunks:
        return "स्रोत-आधार: अभी कोई सत्यापित स्रोत-खंड उपलब्ध नहीं है।"
    lines: list[str] = []
    for i, chunk in enumerate(chunks[:5], start=1):
        locator = chunk.locator.get("locator") if isinstance(chunk.locator, dict) else None
        label = locator or f"chunk:{chunk.chunk_id}"
        preview = chunk.text[:220].replace("\n", " ")
        lines.append(f"[{i}] {label} — {preview}")
    return "स्रोत-आधार:\n" + "\n".join(lines)


def evaluate_content_quality(
    *,
    body: str,
    source_chunk_ids: list[str],
    source_required: bool,
    quantity: int,
    min_source_coverage: float = 0.60,
) -> dict[str, Any]:
    citations_count = len(source_chunk_ids)
    safety = evaluate_query_and_answer("content_factory", body, citations_count=citations_count)
    length_score = min(1.0, max(0.0, len(body.strip()) / 900.0))
    citation_score = 1.0 if citations_count else 0.0
    source_coverage = min(1.0, citations_count / max(1, min(quantity, 5)))
    flags = list(safety.flags)
    if source_required and not source_chunk_ids:
        flags.append("SOURCE_REQUIRED_BUT_MISSING")
    if source_required and source_coverage < min_source_coverage:
        flags.append("LOW_SOURCE_COVERAGE")
    if len(body.strip()) < 120:
        flags.append("TOO_SHORT")
    score = round((0.40 * citation_score) + (0.30 * source_coverage) + (0.30 * length_score), 4)
    review_status = ContentReviewStatus.REVIEW_PENDING.value
    if not safety.allowed or "SOURCE_REQUIRED_BUT_MISSING" in flags:
        review_status = ContentReviewStatus.AUTO_BLOCKED.value
    elif flags:
        review_status = ContentReviewStatus.NEEDS_REVISION.value
    return {
        "score": score,
        "citations_count": citations_count,
        "source_coverage": round(source_coverage, 4),
        "length_score": round(length_score, 4),
        "flags": flags,
        "safety": {"allowed": safety.allowed, "reason": safety.reason},
        "recommended_review_status": review_status,
    }


def _mcq(topic: str, idx: int, chunks: Sequence[ChunkLike]) -> str:
    basis = chunks[(idx - 1) % len(chunks)].text[:260].replace("\n", " ") if chunks else topic
    return (
        f"प्रश्न {idx}: {topic} के संदर्भ में सही स्रोत-संगत कथन कौन-सा है?\n"
        f"A. {basis[:120]}\n"
        "B. बिना स्रोत के कोई भी शास्त्रीय दावा स्वीकार किया जा सकता है\n"
        "C. मनगढ़ंत संस्कृत श्लोक भी प्रमाण माना जाएगा\n"
        "D. परम्परा-भेद हमेशा छिपाना चाहिए\n"
        "उत्तर: A\n"
        "व्याख्या: सही उत्तर उपलब्ध स्रोत-खंड से जुड़ा है; अन्य विकल्प Atman नीति के विरुद्ध हैं।"
    )


def build_content_body(
    request: Any,
    grounded_answer: str,
    chunks: Sequence[ChunkLike],
    *,
    item_index: int = 1,
) -> str:
    basis = source_basis(chunks)
    topic = request.topic
    difficulty = request.difficulty
    header = f"# {topic}\n\nभाषा: हिन्दी\nस्तर: {difficulty}\nआइटम: {item_index}\n\n"

    if request.content_type == "mcq":
        count = min(getattr(request, "quantity", 5), 10)
        return header + "\n\n".join(_mcq(topic, i, chunks) for i in range(1, count + 1)) + "\n\n" + basis
    if request.content_type == "flashcards":
        cards = []
        for i in range(1, min(getattr(request, "quantity", 5), 20) + 1):
            source = chunks[(i - 1) % len(chunks)].text[:180].replace("\n", " ") if chunks else "स्रोत उपलब्ध नहीं"
            cards.append(f"कार्ड {i}\nसामने: {topic} — मुख्य संकेत?\nपीछे: {source}")
        return header + "\n\n".join(cards) + "\n\n" + basis
    if request.content_type == "qa":
        qas = []
        for i in range(1, min(getattr(request, "quantity", 5), 20) + 1):
            qas.append(f"Q{i}. {topic} को सरल शब्दों में समझाइए।\nA{i}. {grounded_answer[:650]}")
        return header + "\n\n".join(qas) + "\n\n" + basis
    if request.content_type == "lesson_plan":
        return header + (
            "## उद्देश्य\n- स्रोत-आधारित समझ विकसित करना।\n- गलत धारणाओं को अलग करना।\n\n"
            "## कक्षा प्रवाह\n1. प्रारम्भिक प्रश्न\n2. स्रोत-पाठ अवलोकन\n3. सरल व्याख्या\n4. misconception check\n5. अभ्यास\n\n"
            "## अभ्यास\nविद्यार्थी स्रोत-आधारित 3 बिंदु लिखें।\n\n"
            f"## आधार\n{grounded_answer}\n\n{basis}"
        )
    if request.content_type == "article":
        return header + (
            f"## भूमिका\n{topic} को समझने के लिए स्रोत-आधारित दृष्टि आवश्यक है।\n\n"
            f"## मुख्य विवेचन\n{grounded_answer}\n\n"
            "## सावधानी\nजहाँ स्रोत उपलब्ध न हो, Atman निश्चित शास्त्रीय दावा नहीं करेगा।\n\n"
            f"{basis}"
        )
    if request.content_type == "daily_wisdom":
        return header + (
            f"आज का चिंतन: {topic} को जीवन में लागू करने से पहले उसके स्रोत-आधार को समझना चाहिए।\n\n"
            f"संकेत: {grounded_answer[:500]}\n\n{basis}"
        )
    if request.content_type == "worksheet":
        return header + (
            "## निर्देश\nस्रोत-आधारित उत्तर दें।\n\n"
            f"1. {topic} का एक वाक्य में अर्थ लिखें।\n"
            f"2. {topic} से जुड़ी एक गलत धारणा लिखें।\n"
            "3. स्रोत से समर्थित 3 बिंदु लिखें।\n\n"
            f"## उत्तर-संकेत\n{grounded_answer}\n\n{basis}"
        )
    if request.content_type == "shorts_script":
        return header + (
            f"Hook: क्या {topic} को हम बिना स्रोत समझ सकते हैं?\n"
            f"Script: {grounded_answer[:700]}\n"
            "CTA: ऐसे और स्रोत-आधारित explanations के लिए Atman पर सीखें।\n\n"
            f"{basis}"
        )
    if request.content_type == "social_post":
        return header + (
            f"{topic}: स्रोत के साथ समझें, अनुमान से नहीं।\n\n"
            f"{grounded_answer[:520]}\n\n{basis}"
        )
    return header + grounded_answer + "\n\n" + basis


def build_drafts(
    request: Any,
    *,
    chunks: Sequence[ChunkLike],
    settings: SettingsLike,
    template_name: str,
    grounded_answer: str,
) -> list[GeneratedContentDraft]:
    source_chunk_ids = [chunk.chunk_id for chunk in chunks]
    batch_quantity = max(1, int(getattr(request, "quantity", 1)))
    item_count = 1 if request.content_type in {"mcq", "flashcards", "qa"} else min(batch_quantity, settings.content_max_batch_items)
    drafts: list[GeneratedContentDraft] = []
    for index in range(1, item_count + 1):
        body = build_content_body(request, grounded_answer, chunks, item_index=index)
        quality = evaluate_content_quality(
            body=body,
            source_chunk_ids=source_chunk_ids,
            source_required=getattr(request, "source_required", True),
            quantity=batch_quantity,
            min_source_coverage=settings.content_min_source_coverage,
        )
        provenance = {
            "model_family": settings.model_family,
            "content_model": settings.content_model,
            "template_name": template_name,
            "source_chunk_ids": source_chunk_ids,
            "generator": "deterministic_v0_4_template_renderer",
            "external_llm_used": False,
        }
        drafts.append(
            GeneratedContentDraft(
                title=f"{request.topic} — {request.content_type} #{index}",
                body=body,
                item_index=index,
                provenance=provenance,
                quality_report=quality,
            )
        )
    return drafts
