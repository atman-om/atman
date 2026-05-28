from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./atman.db"
DEFAULT_SYNC_DATABASE_URL = "sqlite:///./atman.db"


def _replace_scheme(url: str, scheme: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((scheme, parsed.netloc, parsed.path, parsed.query, parsed.fragment))


def _strip_query_keys(url: str, keys: set[str]) -> str:
    parsed = urlsplit(url)
    query = urlencode(
        [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key not in keys]
    )
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))


def _postgres_scheme(url: str, driver: str) -> str:
    if url.startswith(("postgresql://", "postgres://")):
        return _replace_scheme(url, f"postgresql+{driver}")
    if url.startswith("postgresql+"):
        return _replace_scheme(url, f"postgresql+{driver}")
    return url


def _ssl_required(url: str) -> bool:
    parsed = urlsplit(url)
    query = dict(parse_qsl(parsed.query))
    sslmode = query.get("sslmode")
    if sslmode:
        return sslmode != "disable"
    return "neon.tech" in parsed.hostname if parsed.hostname else False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ATMAN_", extra="ignore")

    env: str = "local"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = DEFAULT_ASYNC_DATABASE_URL
    sync_database_url: str = DEFAULT_SYNC_DATABASE_URL
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "atman_chunks"
    object_store_endpoint: str = "http://localhost:9000"
    object_store_bucket: str = "atman-corpus"
    object_store_access_key: str = "atman"
    object_store_secret_key: str = "atman-secret"
    jwt_secret: str = "change-me-in-production"
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002"

    # Canonical model lock: Qwen working family; Atman-Prod remains release-gated.
    model_family: str = "Qwen"
    runtime_model: str = "Atman-Lab-Qwen-14B-v1.0"
    content_model: str = "Atman-Lab-Qwen-14B-v1.0"
    embedding_model: str = "Atman-RAG-QwenEmbedding-v1.0"
    reranker_model: str = "Atman-RAG-QwenReranker-v1.0"
    embedding_dim: int = Field(default=384, ge=32, le=4096)

    # Qwen runtime modes:
    # deterministic      = offline/local fallback, no model download, safe for tests
    # openai_compatible = vLLM/Ollama/LM Studio/TGI-compatible /v1/chat/completions
    # transformers      = optional local Hugging Face transformers execution
    qwen_runtime_mode: str = "openai_compatible"
    qwen_model_id: str = "Qwen/Qwen3-14B"
    qwen_small_model_id: str = "Qwen/Qwen3-4B"
    qwen_base_url: str | None = None  # remote Qwen /v1-compatible base URL
    qwen_api_key: str | None = None
    qwen_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    qwen_max_tokens: int = Field(default=900, ge=64, le=8192)
    qwen_request_timeout_seconds: float = Field(default=60.0, ge=5.0, le=600.0)
    qwen_enable_transformers_runtime: bool = False

    # Legacy aliases retained for v0.4 compatibility.
    llm_base_url: str | None = None
    llm_api_key: str | None = None

    enable_network_crawl: bool = False
    content_export_dir: str = "./generated/exports"
    content_max_batch_items: int = Field(default=250, ge=1, le=5000)
    content_min_source_coverage: float = Field(default=0.60, ge=0.0, le=1.0)

    public_app_name: str = "Atman"
    public_default_language: str = "hi"
    public_enable_streaming: bool = True

    # Corpus ingestion / review controls.
    upload_dir: str = "./generated/uploads"
    max_upload_bytes: int = Field(default=25_000_000, ge=1_000, le=250_000_000)
    enable_pdf_extraction: bool = True
    enable_ocr_placeholder: bool = True
    corpus_default_rights_status: str = "UNKNOWN"
    corpus_require_rights_for_z2: bool = True

    # v0.7 evaluation hardening controls.
    eval_default_benchmark: str = "nyayabench_hardened"
    eval_approval_threshold: float = Field(default=0.92, ge=0.0, le=1.0)
    eval_min_citation_alignment: float = Field(default=0.95, ge=0.0, le=1.0)
    eval_fake_shloka_max_failures: int = Field(default=0, ge=0, le=1000)
    eval_source_required_for_public_answers: bool = True
    source_explorer_public_limit: int = Field(default=50, ge=1, le=250)


    # v0.8 web-to-corpus and OCR controls.
    crawler_user_agent: str = "AtmanBot/1.0 (+source-governed-corpus; contact=admin@atman.local)"
    crawler_max_bytes: int = Field(default=5_000_000, ge=10_000, le=100_000_000)
    crawler_timeout_seconds: float = Field(default=20.0, ge=3.0, le=120.0)
    crawler_require_rights_for_fetch: bool = True
    web_quality_min_score: float = Field(default=0.65, ge=0.0, le=1.0)
    ocr_mode: str = "deterministic"  # deterministic|tesseract|paddle|external
    ocr_min_confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    ocr_output_dir: str = "./generated/ocr"

    # v0.9 Qwen training / ModelOps controls.
    training_artifact_dir: str = "./generated/training"
    training_allow_real_jobs: bool = False
    training_default_base_model: str = "Qwen/Qwen3-14B"
    training_default_adapter_method: str = "qlora"
    training_lora_rank: int = Field(default=64, ge=1, le=512)
    training_lora_alpha: int = Field(default=128, ge=1, le=1024)
    training_learning_rate: float = Field(default=2e-5, gt=0.0, le=1e-2)
    training_epochs: int = Field(default=3, ge=1, le=20)
    training_min_samples_for_real_run: int = Field(default=500, ge=1, le=1_000_000)
    model_release_min_eval_score: float = Field(default=0.92, ge=0.0, le=1.0)
    model_release_require_no_hard_failures: bool = True


    # v1.0.1 Qwen serving controls.
    qwen_model_cache_dir: str = "./generated/models/qwen"
    qwen_vllm_image: str = "vllm/vllm-openai:latest"
    qwen_ollama_model: str = "qwen3:14b"
    qwen_serving_profile: str = "deterministic"  # deterministic|vllm|ollama|lm_studio|tgi
    qwen_gpu_required: bool = False

    # v1.0.1 relaxed discovery + canonical corpus controls.
    relaxed_discovery_enabled: bool = True
    discovery_store_full_text_in_quarantine: bool = True
    discovery_allow_public_web_fetch: bool = False
    quarantine_default_zone: str = "Z1_QUARANTINE"
    canonical_default_citation_mode: str = "hidden"  # hidden|source|scholar
    canonical_min_claim_support_score: float = Field(default=0.55, ge=0.0, le=1.0)
    canonical_answer_min_evidence_grade: str = "C"
    canonical_bulk_import_max_passages: int = Field(default=10000, ge=1, le=1000000)

    # v1.0 production controls.
    production_mode: bool = False
    production_require_auth: bool = False
    production_rate_limit_per_minute: int = Field(default=60, ge=1, le=100000)
    backup_dir: str = "./generated/backups"
    readiness_require_qwen_when_production: bool = True



    # v1.0.5 remote-Qwen chatbot product controls.
    remote_qwen_default_provider: str = "qwen_api"
    remote_qwen_cost_per_1k_input_tokens_usd: float = Field(default=0.0, ge=0.0, le=1000.0)
    remote_qwen_cost_per_1k_output_tokens_usd: float = Field(default=0.0, ge=0.0, le=1000.0)
    chat_default_citation_mode: str = "hidden"  # hidden|source|scholar
    chat_max_messages_per_session: int = Field(default=200, ge=1, le=10000)
    chat_store_retrieval_traces: bool = True
    chat_enable_public_feedback: bool = True
    analytics_default_window_days: int = Field(default=30, ge=1, le=3650)
    publishing_export_dir: str = "./generated/publishing"
    acquisition_quarantine_dir: str = "./generated/quarantine"
    billing_currency: str = "USD"
    enable_demo_auth: bool = True

    # v2.0 Dharma Knowledge OS + parallel Model Lab controls.
    product_version: str = "2.0.0"
    product_codename: str = "Dharma Knowledge OS with Model Lab"
    enable_model_lab: bool = True
    model_lab_mode: str = "parallel"  # parallel|disabled|production_candidate
    model_lab_min_verified_samples: int = Field(default=250, ge=1, le=10_000_000)
    model_lab_min_rejected_samples: int = Field(default=50, ge=0, le=10_000_000)
    model_lab_release_gate_score: float = Field(default=0.93, ge=0.0, le=1.0)
    model_lab_default_dataset_mix: str = "verified_qa:0.45,reviewed_content:0.25,failure_corrections:0.20,adversarial:0.10"
    learning_default_language: str = "hi"
    learning_enable_paths: bool = True
    correctness_min_public_grade: str = "B"
    correctness_block_grade: str = "F"
    os_launch_surface: str = "chatbot,library,learning,content,model_lab,analytics"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_qwen_base_url(self) -> str | None:
        return self.qwen_base_url or self.llm_base_url

    @property
    def resolved_qwen_api_key(self) -> str | None:
        return self.qwen_api_key or self.llm_api_key

    @property
    def sqlalchemy_database_url(self) -> str:
        url = _postgres_scheme(self.database_url, "asyncpg")
        if url.startswith("postgresql+asyncpg://"):
            return _strip_query_keys(url, {"sslmode", "channel_binding"})
        return url

    @property
    def sqlalchemy_sync_database_url(self) -> str:
        source_url = self.sync_database_url
        if source_url == DEFAULT_SYNC_DATABASE_URL and self.database_url != DEFAULT_ASYNC_DATABASE_URL:
            source_url = self.database_url
        return _postgres_scheme(source_url, "psycopg")

    @property
    def database_connect_args(self) -> dict[str, bool]:
        if self.sqlalchemy_database_url.startswith("postgresql+asyncpg://") and _ssl_required(self.database_url):
            return {"ssl": True}
        return {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
