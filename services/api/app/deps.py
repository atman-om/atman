from dataclasses import dataclass

from fastapi import Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.api.app.core.config import Settings, get_settings
from services.api.app.services.vector_store import QdrantStore

admin_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    role: str


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Security(admin_bearer),
    x_atman_role: str = Header(default="admin"),
) -> Principal:
    settings = get_settings()
    if not settings.production_require_auth:
        return Principal(role="local-dev")

    if settings.jwt_secret == "change-me-in-production":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin auth is not configured",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    if credentials.credentials != settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid admin token")

    role = x_atman_role.strip().lower()
    if role not in {"admin", "operator"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin or operator role required")
    return Principal(role=role)


def get_vector_store() -> QdrantStore | None:
    settings = get_settings()
    if not settings.qdrant_url:
        return None
    return QdrantStore(
        url=settings.qdrant_url,
        collection=settings.qdrant_collection,
        dim=settings.embedding_dim,
    )
