from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import StaffPrincipal, require_staff

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_400_BAD_REQUEST)
def register_staff():
    """Akun petugas dibuat oleh administrator melalui Supabase Auth."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Fitur registrasi dinonaktifkan. Hubungi administrator ITCC.",
    )


@router.get("/me")
def get_current_user(principal: StaffPrincipal = Depends(require_staff)):
    """Mengembalikan identitas profil petugas yang telah divalidasi."""
    return {
        "success": True,
        "data": {
            "id": principal.user_id,
            "display_name": principal.display_name,
            "role": principal.role,
        },
    }
