from dataclasses import dataclass

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.errors import AuthApiError

from app.core.supabase_client import get_supabase

bearer_scheme = HTTPBearer(auto_error=False)
AUTHORIZED_ROLES = {"staff", "admin"}


@dataclass(frozen=True)
class StaffPrincipal:
    user_id: str
    display_name: str | None
    role: str


def require_staff(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> StaffPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token akses diperlukan.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase = get_supabase()
    try:
        auth_response = supabase.auth.get_user(credentials.credentials)
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token akses tidak valid atau kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except Exception:
        # Gangguan jaringan/Auth bukan token tidak valid; tetap gagal tertutup.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Layanan autentikasi sementara tidak tersedia.",
        ) from None

    user = getattr(auth_response, "user", None)
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token akses tidak valid atau kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        profile_response = (
            supabase.table("profiles")
            .select("id, display_name, role, is_active")
            .eq("id", user_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pemeriksaan akses sementara tidak tersedia.",
        ) from None

    profile = next(iter(profile_response.data or []), None)
    if not profile or profile.get("role") not in AUTHORIZED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak memiliki izin petugas ITCC.",
        )

    return StaffPrincipal(
        user_id=str(user_id),
        display_name=profile.get("display_name"),
        role=profile["role"],
    )
