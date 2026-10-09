from fastapi import APIRouter, Depends

from app.core.auth import StaffPrincipal, require_staff

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
def get_current_user(principal: StaffPrincipal = Depends(require_staff)):
    return {
        "success": True,
        "data": {
            "id": principal.user_id,
            "display_name": principal.display_name,
            "role": principal.role,
        },
    }
