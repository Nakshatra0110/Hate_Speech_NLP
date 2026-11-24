from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from backend.core.config import settings
from backend.core.security import verify_admin_token

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/")
def get_system_settings():
    return {
        "app": settings.app_config.get("app", {}),
        "compute": {
            "device": settings.device,
            "threads": settings.app_config.get("compute", {}).get("num_threads", 4),
            "batch_size": settings.app_config.get("compute", {}).get("batch_size", 16)
        },
        "reward_weights": settings.reward_weights,
        "languages": settings.languages_config.get("languages", {}).get("supported", [])
    }

@router.post("/", dependencies=[Depends(verify_admin_token)])
def update_system_settings(payload: Dict[str, Any]):
    if "reward_weights" in payload:
        for k, v in payload["reward_weights"].items():
            if k in settings.reward_weights:
                settings.reward_weights[k] = float(v)
    return {"status": "updated", "current_reward_weights": settings.reward_weights}

