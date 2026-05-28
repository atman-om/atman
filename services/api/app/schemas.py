from __future__ import annotations
from typing import Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from services.api.app.domain.enums import (
    ArtifactType,
    ContentBatchStatus,
    ContentReviewStatus,
    ExportFormat,
    RightsStatus,
)


class SourceCreate(BaseModel):
    source_type: str = Field(min_length=2, max_length=64)
    title: str = Field(min_length=1, max_length=512)
    language: str | None = Field(default="hi", max_length=32)
    tradition_scope: list[str] = Field(default_factory=list)
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    source_metadata: dict[str, Any] = Field(default_factory=dict)
    text: str | None = Field(default=None, description="Optional plaintext to ingest immediately")


class SourceOut(BaseModel):
    id: str
    source_type: str
    title: str
    language: str | None
    tradition_scope: list[str]
    rights_status: str
    ingestion_status: str
    checksum_sha256: str | None
    source_metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class SourceDecision(BaseModel):
    decision: Literal[
        "reject",
        "needs_cleanup",
        "promote_z0_to_z1",
        "promote_z1_to_z2",
        "mark_reference_only",
        "mark_rights_red",
    ]
    reviewer_id: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


class ChunkOut(BaseModel):
    id: str
    source_id: str
    chunk_text: str
    token_count: int
    chunk_order: int
    citation_locator: dict[str, Any]
    quality_score: float
    review_status: str

    model_config = {"from_attributes": True}


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    language: str = Field(default="hi", max_length=16)
    top_k: int = Field(default=5, ge=1, le=20)
    require_citations: bool = True


class Citation(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    locator: dict[str, Any]
    score: float
    text_preview: str


class SafetyReport(BaseModel):
    allowed: bool
    flags: list[str] = Field(default_factory=list)
    reason: str | None = None


class RagQueryResponse(BaseModel):
    query_id: str | None = None
    answer: str
    citations: list[Citation]
    safety_report: SafetyReport
    model_name: str
    latency_ms: int


ContentTypeLiteral = Literal[
    "notes",
    "qa",
    "mcq",
    "flashcards",
    "explainer",
    "lesson_plan",
    "article",
    "daily_wisdom",
    "worksheet",
    "shorts_script",
    "social_post",
]


class ContentGenerateRequest(BaseModel):
    content_type: ContentTypeLiteral
    topic: str = Field(min_length=2, max_length=512)
    language: str = Field(default="hi", max_length=16)
    difficulty: Literal["basic", "intermediate", "advanced"] = "intermediate"
    quantity: int = Field(default=5, ge=1, le=100)
    source_required: bool = True
    template_id: str | None = None
    generation_config: dict[str, Any] = Field(default_factory=dict)


class ContentTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    content_type: ContentTypeLiteral
    language: str = "hi"
    prompt_template: str = Field(min_length=10)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    version: str = "0.4.0"
    active: bool = True


class ContentTemplateOut(BaseModel):
    id: str | None = None
    name: str
    content_type: str
    language: str
    prompt_template: str
    output_schema: dict[str, Any]
    version: str
    active: bool

    model_config = {"from_attributes": True}


class ContentBatchCreate(BaseModel):
    name: str = Field(min_length=2, max_length=256)
    content_type: ContentTypeLiteral
    topic: str = Field(min_length=2, max_length=512)
    language: str = "hi"
    difficulty: Literal["basic", "intermediate", "advanced"] = "intermediate"
    quantity: int = Field(default=10, ge=1, le=5000)
    template_id: str | None = None
    source_required: bool = True
    generation_config: dict[str, Any] = Field(default_factory=dict)
    created_by: str | None = None


class ContentBatchOut(BaseModel):
    id: str
    name: str
    content_type: str
    topic: str
    language: str
    difficulty: str
    quantity: int
    template_id: str | None
    status: str
    generation_config: dict[str, Any]
    metrics: dict[str, Any]

    model_config = {"from_attributes": True}


class ContentItemOut(BaseModel):
    id: str
    batch_id: str | None = None
    template_id: str | None = None
    item_index: int = 0
    title: str | None = None
    content_type: str
    topic: str
    language: str
    body: str
    source_chunk_ids: list[str]
    quality_report: dict[str, Any]
    review_status: str
    export_status: str = "NOT_EXPORTED"
    version: int = 1
    provenance: dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class ContentReviewDecision(BaseModel):
    decision: ContentReviewStatus
    reviewer_id: str | None = None
    reason: str | None = None
    checklist: dict[str, Any] = Field(default_factory=dict)


class ContentReviewEventOut(BaseModel):
    id: str
    item_id: str
    reviewer_id: str | None
    decision: str
    reason: str | None
    checklist: dict[str, Any]

    model_config = {"from_attributes": True}


class ContentExportRequest(BaseModel):
    export_format: ExportFormat = ExportFormat.JSONL
    batch_id: str | None = None
    review_status: ContentReviewStatus | None = ContentReviewStatus.APPROVED
    include_manifest: bool = True


class ContentExportOut(BaseModel):
    id: str
    batch_id: str | None
    export_format: str
    file_path: str
    item_count: int
    manifest: dict[str, Any]

    model_config = {"from_attributes": True}


class EvalRunRequest(BaseModel):
    benchmark_name: str = "nyayabench_seed"
    model_version: str = "Atman-Lab-Qwen-14B-v0.1"


class EvalRunOut(BaseModel):
    id: str
    model_version: str
    benchmark_name: str
    score: dict[str, Any]
    hard_failures: list[dict[str, Any]]
    approved: bool

    model_config = {"from_attributes": True}


class ReleaseGateRequest(BaseModel):
    artifact_type: ArtifactType
    artifact_version: str
    metrics: dict[str, Any]
    hard_failures: list[dict[str, Any]] = Field(default_factory=list)
    required_approvals: list[str] = Field(default_factory=list)


class ReleaseGateOut(BaseModel):
    id: str
    artifact_type: str
    artifact_version: str
    allowed: bool
    metrics: dict[str, Any]
    hard_failures: list[dict[str, Any]]
    required_approvals: list[str]

    model_config = {"from_attributes": True}


class WebSourceRequest(BaseModel):
    url: HttpUrl
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    fetch_now: bool = False


class WebSourceOut(BaseModel):
    id: str
    url: str
    title: str | None
    robots_status: str
    tos_status: str
    rights_status: str
    content_hash: str | None
    quality_score: float
    provenance: dict[str, Any]

    model_config = {"from_attributes": True}


# --- v0.5 public app and Qwen runtime schemas ---
class PublicAskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    language: str = Field(default="hi", max_length=16)
    top_k: int = Field(default=5, ge=1, le=10)
    mode: Literal["simple", "scholar"] = "simple"


class PublicAskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    safety_report: SafetyReport
    model_name: str
    latency_ms: int
    ui_hints: dict[str, Any] = Field(default_factory=dict)


class QwenRuntimeStatus(BaseModel):
    model_family: str
    runtime_model: str
    qwen_model_id: str
    mode: str
    ready: bool
    network_required: bool
    weights_bundled: bool
    base_url_configured: bool | None = None
    api_key_configured: bool | None = None
    enabled: bool | None = None


class QwenChatRequest(BaseModel):
    messages: list[dict[str, str]] = Field(min_length=1)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=64, le=8192)


class QwenChatResponse(BaseModel):
    text: str
    model_name: str
    provider: str
    latency_ms: int
    usage: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


# --- v0.6 corpus ingestion and review schemas ---
class SourceFileOut(BaseModel):
    id: str
    source_id: str
    original_filename: str
    content_type: str | None
    byte_size: int
    checksum_sha256: str
    storage_uri: str
    extraction_status: str
    extraction_report: dict[str, Any]

    model_config = {"from_attributes": True}


class CorpusUploadOut(BaseModel):
    source: SourceOut
    source_file: SourceFileOut
    extraction: dict[str, Any]
    ingestion_report: dict[str, Any]


class RightsDecisionRequest(BaseModel):
    rights_status: RightsStatus
    reviewer_id: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = Field(default=None, max_length=4000)


class SourcePromotionRequest(BaseModel):
    target_status: Literal["APPROVED_Z1", "APPROVED_Z2", "BLOCKED", "DEPRECATED"]
    reviewer_id: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = Field(default=None, max_length=4000)


class SourceReviewEventOut(BaseModel):
    id: str
    source_id: str
    reviewer_id: str | None
    decision: str
    rights_status: str | None
    ingestion_status: str | None
    evidence: dict[str, Any]
    notes: str | None

    model_config = {"from_attributes": True}


class ChunkReviewDecision(BaseModel):
    decision: Literal["approve", "reject", "needs_revision", "revise", "deprecate"]
    reviewer_id: str | None = None
    revised_text: str | None = Field(default=None, min_length=1)
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    checklist: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = Field(default=None, max_length=4000)


class ChunkReviewEventOut(BaseModel):
    id: str
    chunk_id: str
    reviewer_id: str | None
    decision: str
    previous_status: str | None
    new_status: str
    previous_text_hash: str | None
    revised_text_hash: str | None
    checklist: dict[str, Any]
    notes: str | None

    model_config = {"from_attributes": True}


class CorpusDashboardOut(BaseModel):
    sources_total: int
    files_total: int
    chunks_total: int
    pending_source_reviews: int
    pending_chunk_reviews: int
    approved_z2_sources: int
    indexed_sources: int
    rights_distribution: dict[str, int]
    ingestion_distribution: dict[str, int]

# --- v0.7 eval hardening and source explorer schemas ---
class EvalHardeningRunRequest(BaseModel):
    benchmark_name: str = "nyayabench_hardened"
    model_version: str = "Atman-Lab-Qwen-14B-v0.7"
    dataset_glob: str = "nyayabench_*_seed.jsonl"
    include_runtime_probe: bool = False
    persist_cases: bool = True


class EvalCaseResultOut(BaseModel):
    id: str | None = None
    eval_run_id: str | None = None
    case_id: str
    category: str
    passed: bool
    severity: str
    score: float
    grader: str
    findings: dict[str, Any]
    answer_preview: str | None = None

    model_config = {"from_attributes": True}


class EvalHardeningRunOut(BaseModel):
    run: EvalRunOut
    results: list[EvalCaseResultOut]
    category_scores: dict[str, Any]
    release_readiness: dict[str, Any]


class CitationCheckRequest(BaseModel):
    answer_text: str = Field(min_length=1, max_length=12000)
    citations: list[dict[str, Any]] = Field(default_factory=list)
    strict: bool = True


class CitationCheckResponse(BaseModel):
    alignment_score: float
    passed: bool
    findings: dict[str, Any]
    run_id: str | None = None


class FakeShlokaCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    citations: list[dict[str, Any]] = Field(default_factory=list)
    strict: bool = True


class FakeShlokaCheckResponse(BaseModel):
    passed: bool
    risk_score: float
    findings: dict[str, Any]


class SourceExplorerSearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=512)
    language: str | None = Field(default=None, max_length=32)
    rights_status: list[str] = Field(default_factory=list)
    ingestion_status: list[str] = Field(default_factory=list)
    public_only: bool = True
    limit: int = Field(default=25, ge=1, le=250)


class SourceExplorerChunkOut(BaseModel):
    id: str
    source_id: str
    chunk_text: str
    token_count: int
    chunk_order: int
    citation_locator: dict[str, Any]
    quality_score: float
    review_status: str
    highlight: str | None = None

    model_config = {"from_attributes": True}


class SourceExplorerSourceOut(BaseModel):
    id: str
    title: str
    source_type: str
    language: str | None
    rights_status: str
    ingestion_status: str
    tradition_scope: list[str]
    source_metadata: dict[str, Any]
    chunk_count: int = 0
    matched_chunk_count: int = 0
    locators: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str | None = None

    model_config = {"from_attributes": True}


class SourceExplorerSearchResponse(BaseModel):
    query: str | None
    total: int
    sources: list[SourceExplorerSourceOut]
    chunks: list[SourceExplorerChunkOut]
    filters: dict[str, Any]


class SourceExplorerDetailOut(BaseModel):
    source: SourceExplorerSourceOut
    chunks: list[SourceExplorerChunkOut]
    rights_explanation: dict[str, Any]
    provenance: dict[str, Any]


# --- v0.8 web-to-corpus and OCR schemas ---
class OCRAnalyzeResponse(BaseModel):
    filename: str
    status: str
    engine: str
    text: str | None = None
    text_hash: str | None = None
    confidence: float
    page_count: int
    warnings: list[str] = Field(default_factory=list)
    report: dict[str, Any] = Field(default_factory=dict)


class WebQualityScoreRequest(BaseModel):
    url: HttpUrl
    text: str = Field(min_length=1, max_length=200_000)
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    robots_status: str = "UNKNOWN"


class WebQualityScoreResponse(BaseModel):
    score: float
    verdict: str
    components: dict[str, Any]
    allowed_usage: dict[str, Any]


class WebCrawlJobRequest(BaseModel):
    url: HttpUrl
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    fetch_now: bool = False
    force: bool = False
    notes: str | None = Field(default=None, max_length=2000)


class WebCrawlJobOut(BaseModel):
    id: str
    url: str
    status: str
    robots_status: str
    rights_status: str
    fetch_requested: bool
    fetched_bytes: int
    extracted_text_hash: str | None
    quality_score: float
    error: str | None
    result: dict[str, Any]

    model_config = {"from_attributes": True}


class ProvenanceEventOut(BaseModel):
    id: str
    object_type: str
    object_id: str
    event_type: str
    actor_id: str | None
    evidence: dict[str, Any]

    model_config = {"from_attributes": True}


# --- v0.9 training and ModelOps schemas ---
class TrainingSampleIn(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    completion: str = Field(min_length=1, max_length=12000)
    source_ids: list[str] = Field(default_factory=list)
    chunk_ids: list[str] = Field(default_factory=list)
    rights_status: str = "USER_OWNED"
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrainingDatasetBuildRequest(BaseModel):
    name: str = Field(min_length=2, max_length=256)
    base_model: str = "Qwen/Qwen3-14B"
    samples: list[TrainingSampleIn] = Field(default_factory=list)
    include_reviewed_content: bool = True
    include_approved_chunks: bool = True


class TrainingDatasetOut(BaseModel):
    id: str
    name: str
    base_model: str
    sample_count: int
    artifact_uri: str
    manifest: dict[str, Any]
    status: str

    model_config = {"from_attributes": True}


class TrainingRunStartRequest(BaseModel):
    dataset_id: str | None = None
    base_model: str = "Qwen/Qwen3-14B"
    adapter_method: Literal["lora", "qlora"] = "qlora"
    simulate: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class TrainingRunOut(BaseModel):
    id: str
    dataset_id: str | None
    base_model: str
    adapter_method: str
    status: str
    config: dict[str, Any]
    metrics: dict[str, Any]
    checkpoint_id: str | None

    model_config = {"from_attributes": True}


class ModelCheckpointOut(BaseModel):
    id: str
    run_id: str | None
    model_name: str
    base_model: str
    adapter_uri: str
    checksum_sha256: str | None
    eval_summary: dict[str, Any]
    release_status: str

    model_config = {"from_attributes": True}


class ModelReleaseRequest(BaseModel):
    release_name: str = Field(min_length=2, max_length=256)
    environment: Literal["dev", "staging", "production"] = "staging"
    eval_summary: dict[str, Any] = Field(default_factory=dict)
    required_approvals: list[str] = Field(default_factory=list)


class ModelReleaseOut(BaseModel):
    id: str
    checkpoint_id: str
    release_name: str
    environment: str
    allowed: bool
    gate_report: dict[str, Any]
    rollback_target: str | None

    model_config = {"from_attributes": True}


class ServingProfileOut(BaseModel):
    id: str
    name: str
    model_name: str
    runtime_mode: str
    endpoint_url: str | None
    config: dict[str, Any]
    active: bool

    model_config = {"from_attributes": True}


# --- v1.0 production/ops schemas ---
class ProductionReadinessOut(BaseModel):
    ready: bool
    environment: str
    production_mode: bool
    checks: dict[str, Any]
    hard_failures: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BackupRunOut(BaseModel):
    id: str
    status: str
    backup_type: str
    artifact_uri: str | None
    manifest: dict[str, Any]

    model_config = {"from_attributes": True}


class IncidentCreateRequest(BaseModel):
    severity: Literal["P0", "P1", "P2", "P3"] = "P3"
    title: str = Field(min_length=2, max_length=256)
    description: str | None = Field(default=None, max_length=5000)
    evidence: dict[str, Any] = Field(default_factory=dict)


class IncidentOut(BaseModel):
    id: str
    severity: str
    title: str
    status: str
    description: str | None
    evidence: dict[str, Any]

    model_config = {"from_attributes": True}

# --- v1.0.5 remote-Qwen chatbot product, accounts, publishing, analytics schemas ---
class UserCreateRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    display_name: str | None = Field(default=None, max_length=256)
    role: Literal["owner", "admin", "corpus_reviewer", "dharma_reviewer", "content_editor", "viewer"] = "viewer"
    preferences: dict[str, Any] = Field(default_factory=dict)


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str | None
    role: str
    status: str
    preferences: dict[str, Any]

    model_config = {"from_attributes": True}


class ChatSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=512)
    user_id: str | None = None
    mode: Literal["simple", "source", "scholar", "teacher", "admin_debug"] = "simple"
    language: str = Field(default="hi", max_length=32)
    citation_mode: Literal["hidden", "source", "scholar"] = "hidden"
    session_metadata: dict[str, Any] = Field(default_factory=dict)


class ChatSessionOut(BaseModel):
    id: str
    user_id: str | None
    title: str
    mode: str
    language: str
    citation_mode: str
    status: str
    session_metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class ChatMessageSend(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    top_k: int = Field(default=5, ge=1, le=20)
    citation_mode: Literal["hidden", "source", "scholar"] | None = None
    force_remote_model: bool = True
    request_metadata: dict[str, Any] = Field(default_factory=dict)


class ChatMessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model_name: str | None
    provider: str | None
    citation_mode: str
    visible_citations: list[dict[str, Any]]
    internal_evidence: list[dict[str, Any]]
    safety_report: dict[str, Any]
    latency_ms: int
    usage: dict[str, Any]

    model_config = {"from_attributes": True}


class ChatTurnOut(BaseModel):
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    trace_id: str | None
    usage_log_id: str | None
    ui_hints: dict[str, Any] = Field(default_factory=dict)


class ChatSessionDetailOut(BaseModel):
    session: ChatSessionOut
    messages: list[ChatMessageOut]


class ChatFeedbackRequest(BaseModel):
    rating: Literal["up", "down", "neutral", "wrong", "unsafe", "excellent"] = "neutral"
    user_id: str | None = None
    reason: str | None = Field(default=None, max_length=4000)
    correction: str | None = Field(default=None, max_length=12000)
    feedback_metadata: dict[str, Any] = Field(default_factory=dict)


class ChatFeedbackOut(BaseModel):
    id: str
    message_id: str
    user_id: str | None
    rating: str
    reason: str | None
    correction: str | None
    feedback_metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class ChatDebugOut(BaseModel):
    message: ChatMessageOut
    retrieval_trace: dict[str, Any] | None = None
    model_usage: dict[str, Any] | None = None
    claim_checks: list[dict[str, Any]] = Field(default_factory=list)


class RemoteModelProviderOut(BaseModel):
    provider: str
    model_id: str
    mode: str
    base_url_configured: bool
    api_key_configured: bool
    ready: bool
    default_for: list[str] = Field(default_factory=list)


class ModelUsageLogOut(BaseModel):
    id: str
    provider: str
    model_name: str
    feature: str
    user_id: str | None
    session_id: str | None
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    currency: str
    latency_ms: int
    status: str
    usage_metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class PublishingChannelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    channel_type: Literal["manual_export", "web", "pwa", "whatsapp", "instagram", "youtube", "newsletter"] = "manual_export"
    active: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class PublishingChannelOut(BaseModel):
    id: str
    name: str
    channel_type: str
    active: bool
    config: dict[str, Any]

    model_config = {"from_attributes": True}


class PublicationCreateRequest(BaseModel):
    content_item_id: str | None = None
    channel_id: str | None = None
    title: str = Field(min_length=2, max_length=512)
    body: str = Field(min_length=1, max_length=100000)
    status: Literal["DRAFT", "REVIEW_READY", "SCHEDULED", "PUBLISHED", "ARCHIVED"] = "DRAFT"
    scheduled_at: str | None = None
    public_slug: str | None = Field(default=None, max_length=256)
    publication_metadata: dict[str, Any] = Field(default_factory=dict)


class PublicationOut(BaseModel):
    id: str
    content_item_id: str | None
    channel_id: str | None
    title: str
    body: str
    status: str
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    public_slug: str | None
    export_uri: str | None
    publication_metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class AcquisitionJobCreate(BaseModel):
    source_uri: str = Field(min_length=2, max_length=2048)
    mode: Literal["wide_discovery", "quarantine_import", "canonical_candidate", "manual_bulk_import"] = "wide_discovery"
    discovered_title: str | None = Field(default=None, max_length=512)
    extracted_text: str | None = Field(default=None, max_length=500000)
    rights_signal: str = "UNKNOWN"
    canonical_candidate: dict[str, Any] = Field(default_factory=dict)


class AcquisitionJobOut(BaseModel):
    id: str
    source_uri: str
    mode: str
    status: str
    zone: str
    discovered_title: str | None
    quality_score: float
    rights_signal: str
    canonical_candidate: dict[str, Any]
    report: dict[str, Any]

    model_config = {"from_attributes": True}


class AnalyticsOverviewOut(BaseModel):
    window_days: int
    chats: dict[str, Any]
    corpus: dict[str, Any]
    content: dict[str, Any]
    model_usage: dict[str, Any]
    publishing: dict[str, Any]
    acquisition: dict[str, Any]
    billing: dict[str, Any]


class ProductReadinessOut(BaseModel):
    version: str
    ready_for_demo: bool
    ready_for_public_beta: bool
    checks: dict[str, Any]
    blockers: list[str]
    warnings: list[str]

# --- v2.0 Dharma Knowledge OS + Model Lab schemas ---
class KnowledgeOSStatusOut(BaseModel):
    version: str
    codename: str
    primary_runtime: str
    live_brain: str
    parallel_model_lab: bool
    launch_surfaces: list[str]
    capability_map: dict[str, Any]
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class LearningPathCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=160)
    title: str = Field(min_length=2, max_length=512)
    language: str = Field(default="hi", max_length=32)
    difficulty: Literal["beginner", "intermediate", "advanced", "scholar"] = "beginner"
    description: str | None = Field(default=None, max_length=5000)
    canonical_work_keys: list[str] = Field(default_factory=list)
    modules: list[dict[str, Any]] = Field(default_factory=list)
    status: Literal["DRAFT", "PUBLISHED", "ARCHIVED"] = "DRAFT"


class LearningPathOut(BaseModel):
    id: str
    slug: str
    title: str
    language: str
    difficulty: str
    description: str | None
    canonical_work_keys: list[str]
    modules: list[dict[str, Any]]
    status: str

    model_config = {"from_attributes": True}


class LessonProgressUpdate(BaseModel):
    user_id: str
    learning_path_id: str
    lesson_key: str = Field(min_length=1, max_length=256)
    status: Literal["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "REVIEW"] = "IN_PROGRESS"
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    progress_metadata: dict[str, Any] = Field(default_factory=dict)


class LessonProgressOut(BaseModel):
    id: str
    user_id: str
    learning_path_id: str
    lesson_key: str
    status: str
    score: float
    progress_metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class SavedAnswerCreate(BaseModel):
    user_id: str | None = None
    message_id: str | None = None
    title: str = Field(min_length=2, max_length=512)
    answer_text: str = Field(min_length=1, max_length=100000)
    tags: list[str] = Field(default_factory=list)
    source_summary: list[dict[str, Any]] = Field(default_factory=list)


class SavedAnswerOut(BaseModel):
    id: str
    user_id: str | None
    message_id: str | None
    title: str
    answer_text: str
    tags: list[str]
    source_summary: list[dict[str, Any]]

    model_config = {"from_attributes": True}


class ClaimCheckRequest(BaseModel):
    claim: str = Field(min_length=2, max_length=12000)
    candidate_evidence: list[dict[str, Any]] = Field(default_factory=list)
    strictness: Literal["loose", "normal", "strict"] = "normal"
    public_answer: bool = True


class ClaimCheckOut(BaseModel):
    claim: str
    support_grade: str
    verdict: str
    confidence: float
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ModelLabDatasetPlanRequest(BaseModel):
    name: str = Field(min_length=2, max_length=256)
    base_model: str = "Qwen/Qwen3-14B"
    target_sample_count: int = Field(default=1000, ge=1, le=10_000_000)
    verified_qa: int = Field(default=0, ge=0)
    reviewed_content: int = Field(default=0, ge=0)
    failure_corrections: int = Field(default=0, ge=0)
    adversarial: int = Field(default=0, ge=0)
    include_raw_scraped: bool = False


class ModelLabDatasetPlanOut(BaseModel):
    name: str
    base_model: str
    target_sample_count: int
    observed_samples: dict[str, int]
    recommended_mix: dict[str, float]
    allowed_for_training: bool
    blockers: list[str]
    warnings: list[str]
    manifest: dict[str, Any]


class ModelLabExperimentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=256)
    base_model: str = "Qwen/Qwen3-14B"
    objective: Literal["instruction_tuning", "rag_obedience", "hindi_style", "verifier", "content_factory"] = "instruction_tuning"
    dataset_plan: dict[str, Any] = Field(default_factory=dict)
    training_config: dict[str, Any] = Field(default_factory=dict)
    eval_plan: dict[str, Any] = Field(default_factory=dict)
    owner_id: str | None = None


class ModelLabExperimentOut(BaseModel):
    id: str
    name: str
    base_model: str
    objective: str
    status: str
    dataset_plan: dict[str, Any]
    training_config: dict[str, Any]
    eval_plan: dict[str, Any]
    gate_report: dict[str, Any]
    owner_id: str | None

    model_config = {"from_attributes": True}


class ModelLabReadinessOut(BaseModel):
    mode: str
    live_app_runtime: str
    fine_tuning_lane: str
    production_replacement_allowed: bool
    counts: dict[str, int]
    readiness_score: float
    blockers: list[str]
    warnings: list[str]
    next_actions: list[str]


class ModelComparisonOut(BaseModel):
    baseline: dict[str, Any]
    candidates: list[dict[str, Any]]
    decision: str
    release_rule: str
