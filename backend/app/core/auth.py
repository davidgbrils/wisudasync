from dataclasses import dataclass

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase_client import get_supabase

bearer_scheme = HTTPBearer(auto_error=False)
AUTHORIZED_ROLES = {"staff", "admin"}


@dataclass(frozen=True)
class StaffPrincipal:
    user_id: str | None
    display_name: str | None
    role: str


def require_staff(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> StaffPrincipal:
    """Validasi access token dan profil petugas aktif sebelum mengakses data."""
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesi login diperlukan.")

    try:
        supabase = get_supabase()
        auth_response = supabase.auth.get_user(credentials.credentials)
        user = getattr(auth_response, "user", None)
        user_id = getattr(user, "id", None)
    except Exception:
        raise HTTPException(status_code=401, detail="Token login tidak valid.") from None

    if not user_id:
        raise HTTPException(status_code=401, detail="Token login tidak valid.")

    try:
        profile_response = (
            supabase.table("profiles")
            .select("id, display_name, role, is_active")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
    except Exception:
        raise HTTPException(status_code=503, detail="Profil petugas belum dapat diperiksa.") from None

    profile = next(iter(profile_response.data or []), None)
    if not profile or not profile.get("is_active") or profile.get("role") not in AUTHORIZED_ROLES:
        raise HTTPException(status_code=403, detail="Akun tidak memiliki akses petugas aktif.")
    return StaffPrincipal(
        user_id=str(user_id),
        display_name=profile.get("display_name") or "Petugas ITCC",
        role=profile["role"],
    )
