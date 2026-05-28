from types import SimpleNamespace

from pathlib import Path
from services.api.app.schemas import ChatSessionCreate, PublicationCreateRequest
from services.api.app.services.model_gateway import estimate_cost, estimate_tokens, select_model_route
from services.api.app.services.wide_acquisition import assess_acquisition_candidate


def settings(**overrides):
    base = dict(
        remote_qwen_cost_per_1k_input_tokens_usd=0.01,
        remote_qwen_cost_per_1k_output_tokens_usd=0.02,
        remote_qwen_default_provider="qwen_api",
        qwen_model_id="qwen-plus",
        qwen_small_model_id="qwen-turbo",
        qwen_runtime_mode="openai_compatible",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_v105_routers_are_registered_in_main() -> None:
    text = Path("services/api/app/main.py").read_text()
    for router_name in ["chat", "model_gateway", "analytics", "publishing", "wide_acquisition", "accounts"]:
        assert f"app.include_router({router_name}.router" in text


def test_cost_estimation_uses_remote_qwen_pricing() -> None:
    s = settings()
    assert estimate_tokens("कर्म योग क्या है?") > 0
    assert estimate_cost(s, input_tokens=1000, output_tokens=500) == 0.02


def test_model_route_defaults_to_remote_qwen_chat() -> None:
    route = select_model_route(settings(), "chat")
    assert route.provider == "qwen_api"
    assert route.runtime_mode == "openai_compatible"
    assert route.reason == "primary_chat_runtime"


def test_wide_acquisition_promotes_only_quality_rights_clean_candidates() -> None:
    assessment = assess_acquisition_candidate(
        uri="https://example.org/bhagavad-gita",
        text="Bhagavad Gita गीता वेद उपनिषद कर्म योग " * 300,
        rights_signal="PUBLIC_DOMAIN_VERIFIED",
        mode="wide_discovery",
    )
    assert assessment.zone == "Z2_CANDIDATE_CANONICAL"
    assert assessment.quality_score >= 0.75


def test_v105_schemas_lock_chat_and_publication_contracts() -> None:
    chat = ChatSessionCreate(citation_mode="hidden", mode="simple")
    pub = PublicationCreateRequest(title="Daily Wisdom", body="कर्म पर छोटा विचार")
    assert chat.language == "hi"
    assert pub.status == "DRAFT"
