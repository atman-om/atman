import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from services.api.app import deps
from services.api.app.core.config import Settings
from services.api.app.services.source_explorer import PUBLIC_RIGHTS


def test_admin_guard_allows_local_dev_without_token(monkeypatch):
    monkeypatch.setattr(deps, "get_settings", lambda: Settings(production_require_auth=False))
    principal = deps.require_admin(credentials=None)
    assert principal.role == "local-dev"


def test_admin_guard_requires_valid_bearer_token_in_production(monkeypatch):
    monkeypatch.setattr(
        deps,
        "get_settings",
        lambda: Settings(production_require_auth=True, jwt_secret="rotated-secret"),
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="rotated-secret")
    principal = deps.require_admin(credentials=credentials, x_atman_role="operator")
    assert principal.role == "operator"


def test_admin_guard_rejects_invalid_role_in_production(monkeypatch):
    monkeypatch.setattr(
        deps,
        "get_settings",
        lambda: Settings(production_require_auth=True, jwt_secret="rotated-secret"),
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="rotated-secret")
    with pytest.raises(HTTPException) as exc:
        deps.require_admin(credentials=credentials, x_atman_role="viewer")
    assert exc.value.status_code == 403


def test_public_rights_exclude_user_owned_private_sources():
    assert "USER_OWNED" not in PUBLIC_RIGHTS
