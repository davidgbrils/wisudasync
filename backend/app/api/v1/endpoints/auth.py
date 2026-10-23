from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import StaffPrincipal, require_staff

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_400_BAD_REQUEST)
def register_staff():
    """Endpoint registrasi dinonaktifkan karena sistem disederhanakan menjadi Admin-Only tanpa login/register."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Fitur registrasi dinonaktifkan. Sistem beroperasi dalam mode Administrator langsung.",
    )


@router.get("/me")
def get_current_user(principal: StaffPrincipal = Depends(require_staff)):
    """Mengembalikan identitas profil aktif, secara default sebagai Administrator ITCC."""
    return {
        "success": True,
        "data": {
            "id": principal.user_id or "00000000-0000-0000-0000-000000000001",
            "display_name": principal.display_name or "Administrator ITCC",
            "role": "admin",
        },
    }
