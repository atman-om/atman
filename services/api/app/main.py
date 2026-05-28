from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.app.core.config import get_settings
from services.api.app.deps import require_admin
from services.api.app.routers import (
    accounts,
    analytics,
    correctness,
    canonical,
    chat,
    content,
    corpus,
    eval,
    health,
    knowledge_os,
    learning,
    model_gateway,
    model_lab,
    ocr,
    ops,
    public,
    publishing,
    qwen_serving,
    rag,
    release,
    runtime,
    source_explorer,
    sources,
    training,
    web,
    web_to_corpus,
    wide_acquisition,
)

settings = get_settings()

app = FastAPI(
    title="Atman Platform API",
    version="2.0.0",
    description="Atman v2.0 Dharma Knowledge OS with remote-Qwen chatbot, canonical corpus library, learning/product surfaces, content studio, analytics, and parallel Qwen Model Lab for fine-tuning R&D.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(public.router)
app.include_router(source_explorer.router)
app.include_router(knowledge_os.router)
admin_dependencies = [Depends(require_admin)]
app.include_router(sources.router, dependencies=admin_dependencies)
app.include_router(corpus.router, dependencies=admin_dependencies)
app.include_router(rag.router, dependencies=admin_dependencies)
app.include_router(runtime.router, dependencies=admin_dependencies)
app.include_router(content.router, dependencies=admin_dependencies)
app.include_router(eval.router, dependencies=admin_dependencies)
app.include_router(release.router, dependencies=admin_dependencies)
app.include_router(web.router, dependencies=admin_dependencies)
app.include_router(web_to_corpus.router, dependencies=admin_dependencies)
app.include_router(ocr.router, dependencies=admin_dependencies)
app.include_router(training.router, dependencies=admin_dependencies)
app.include_router(ops.router, dependencies=admin_dependencies)
app.include_router(canonical.router, dependencies=admin_dependencies)
app.include_router(qwen_serving.router, dependencies=admin_dependencies)
app.include_router(chat.router, dependencies=admin_dependencies)
app.include_router(model_gateway.router, dependencies=admin_dependencies)
app.include_router(accounts.router, dependencies=admin_dependencies)
app.include_router(publishing.router, dependencies=admin_dependencies)
app.include_router(analytics.router, dependencies=admin_dependencies)
app.include_router(wide_acquisition.router, dependencies=admin_dependencies)
app.include_router(correctness.router, dependencies=admin_dependencies)
app.include_router(learning.router, dependencies=admin_dependencies)
app.include_router(model_lab.router, dependencies=admin_dependencies)
