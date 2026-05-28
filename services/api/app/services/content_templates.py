from __future__ import annotations
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class DefaultTemplate:
    name: str
    content_type: str
    language: str
    prompt_template: str
    output_schema: dict
    version: str = "0.4.0"
    active: bool = True
    id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


DEFAULT_TEMPLATES: tuple[DefaultTemplate, ...] = (
    DefaultTemplate(
        name="hi_notes_source_grounded_v1",
        content_type="notes",
        language="hi",
        prompt_template="Topic={topic}; difficulty={difficulty}; produce source-grounded Hindi notes with citations.",
        output_schema={"sections": ["summary", "key_points", "source_basis", "revision"]},
    ),
    DefaultTemplate(
        name="hi_mcq_source_grounded_v1",
        content_type="mcq",
        language="hi",
        prompt_template="Create Hindi MCQs from provided source chunks. Never invent scripture.",
        output_schema={"fields": ["question", "options", "answer", "explanation", "source_chunk_ids"]},
    ),
    DefaultTemplate(
        name="hi_flashcards_v1",
        content_type="flashcards",
        language="hi",
        prompt_template="Create concise Hindi flashcards grounded in sources.",
        output_schema={"fields": ["front", "back", "source_chunk_ids"]},
    ),
    DefaultTemplate(
        name="hi_qa_v1",
        content_type="qa",
        language="hi",
        prompt_template="Create Hindi Q&A pairs with source-grounded answers.",
        output_schema={"fields": ["question", "answer", "source_chunk_ids"]},
    ),
    DefaultTemplate(
        name="hi_lesson_plan_v1",
        content_type="lesson_plan",
        language="hi",
        prompt_template="Create a teacher-ready Hindi lesson plan from source chunks.",
        output_schema={"sections": ["objectives", "flow", "activity", "assessment"]},
    ),
    DefaultTemplate(
        name="hi_explainer_v1",
        content_type="explainer",
        language="hi",
        prompt_template="Explain the topic in simple Hindi with source discipline.",
        output_schema={"sections": ["short_answer", "detail", "source_basis"]},
    ),
    DefaultTemplate(
        name="hi_article_v1",
        content_type="article",
        language="hi",
        prompt_template="Write a structured Hindi article grounded in source chunks.",
        output_schema={"sections": ["title", "intro", "body", "citations"]},
    ),
    DefaultTemplate(
        name="hi_daily_wisdom_v1",
        content_type="daily_wisdom",
        language="hi",
        prompt_template="Create a short daily wisdom card in Hindi with source basis.",
        output_schema={"fields": ["title", "message", "reflection", "source_chunk_ids"]},
    ),
    DefaultTemplate(
        name="hi_worksheet_v1",
        content_type="worksheet",
        language="hi",
        prompt_template="Create a Hindi practice worksheet from source chunks.",
        output_schema={"sections": ["instructions", "questions", "answer_key"]},
    ),
    DefaultTemplate(
        name="hi_shorts_script_v1",
        content_type="shorts_script",
        language="hi",
        prompt_template="Create a safe short-video script from source chunks. No fake shloka.",
        output_schema={"sections": ["hook", "script", "cta", "source_basis"]},
    ),
    DefaultTemplate(
        name="hi_social_post_v1",
        content_type="social_post",
        language="hi",
        prompt_template="Create a concise Hindi social post with source-safe wording.",
        output_schema={"fields": ["post", "caption", "source_basis"]},
    ),
)


def get_default_template(content_type: str, language: str = "hi") -> DefaultTemplate:
    for template in DEFAULT_TEMPLATES:
        if template.content_type == content_type and template.language == language and template.active:
            return template
    for template in DEFAULT_TEMPLATES:
        if template.content_type == content_type and template.active:
            return template
    raise ValueError(f"no default template for content_type={content_type!r}")
