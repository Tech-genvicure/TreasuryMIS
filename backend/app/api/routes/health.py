from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health():
    return {
        "status": "ok",
        "service": "Genvicure Treasury MIS",
    }


@router.get("/protected")
def protected_health(
    current_user: User = Depends(get_current_user),
):
    return {
        "status": "ok",
        "authenticated": True,
        "username": current_user.username,
    }