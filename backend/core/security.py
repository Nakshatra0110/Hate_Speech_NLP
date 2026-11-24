import os
from typing import Optional
from fastapi import Header, HTTPException, status
from backend.core.config import settings

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN") or settings.app_config.get("admin_token", "cset346-academic-admin")

def verify_admin_token(
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Security Dependency: Restricts destructive endpoints (/reset, /run-all, settings updates)
    to authorized researchers and administrative operators.
    """
    token = x_admin_token
    if not token and authorization:
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        else:
            token = authorization.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrative authorization token required in 'X-Admin-Token' or 'Authorization: Bearer <token>' header."
        )

    if token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid administrative token. Access denied for destructive operation."
        )

    return True
