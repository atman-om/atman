from services.api.app.services.content_templates import DEFAULT_TEMPLATES, get_default_template


def test_default_templates_cover_core_content_types() -> None:
    types = {template.content_type for template in DEFAULT_TEMPLATES}
    assert {"notes", "mcq", "qa", "flashcards", "lesson_plan"}.issubset(types)


def test_get_default_template() -> None:
    template = get_default_template("notes")
    assert template.name.startswith("hi_notes")
