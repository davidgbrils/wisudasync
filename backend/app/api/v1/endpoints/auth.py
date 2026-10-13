import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.auth import StaffPrincipal, require_staff
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/auth", tags=["Auth"])

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterStaffRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    display_name: str = Field(min_length=2, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Format email tidak valid.")
        return clean



@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_staff(payload: RegisterStaffRequest):
    supabase = get_supabase()
    clean_email = payload.email.strip().lower()
    clean_name = payload.display_name.strip()

    # 1. Buat user di Supabase Auth melalui Admin API
    try:
        user_resp = supabase.auth.admin.create_user({
            "email": clean_email,
            "password": payload.password,
            "email_confirm": True,
            "user_metadata": {"display_name": clean_name},
        })
        user = getattr(user_resp, "user", None)
        user_id = getattr(user, "id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gagal membuat user di sistem autentikasi.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        err_str = str(exc).lower()
        if "already registered" in err_str or "already been registered" in err_str or "unique constraint" in err_str or "exists" in err_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah terdaftar dalam sistem.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registrasi gagal: {str(exc)}",
        )

    # 2. Catat di tabel public.profiles (role staff, is_active true)
    try:
        supabase.table("profiles").upsert({
            "id": str(user_id),
            "display_name": clean_name,
            "role": "staff",
            "is_active": True,
        }).execute()
    except Exception as exc:
        # Rollback: hapus user dari Auth agar tidak tertinggal akun tanpa profil
        try:
            supabase.auth.admin.delete_user(str(user_id))
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Akun belum dapat dicatat di database karena tabel 'public.profiles' belum tersedia. "
                "Silakan jalankan database/SETUP_ALL_TABLES.sql di SQL Editor Supabase."
            ),
        )


    return {
        "success": True,
        "message": "Registrasi akun petugas berhasil dan tercatat di database.",
        "data": {
            "id": str(user_id),
            "email": clean_email,
            "display_name": clean_name,
            "role": "staff",
        },
    }


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
