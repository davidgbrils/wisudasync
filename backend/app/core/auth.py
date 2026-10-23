from dataclasses import dataclass

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase_client import get_supabase

bearer_scheme = HTTPBearer(auto_error=False)
AUTHORIZED_ROLES = {"admin"}


@dataclass(frozen=True)
class StaffPrincipal:
    user_id: str | None
    display_name: str | None
    role: str


DEFAULT_ADMIN_PRINCIPAL = StaffPrincipal(
    user_id=None,
    display_name="Administrator ITCC",
    role="admin",
)


def require_staff(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> StaffPrincipal:
    """Mengembalikan akun Admin secara langsung (sistem tanpa login/register, role tunggal admin).

    Jika token diberikan dan profil ditemukan di Supabase, gunakan profil tersebut.
    Jika tidak ada token / login ditiadakan, kembalikan DEFAULT_ADMIN_PRINCIPAL dengan role 'admin'.
    """
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        return DEFAULT_ADMIN_PRINCIPAL

    try:
        supabase = get_supabase()
        auth_response = supabase.auth.get_user(credentials.credentials)
        user = getattr(auth_response, "user", None)
        user_id = getattr(user, "id", None)
        if user_id:
            profile_response = (
                supabase.table("profiles")
                .select("id, display_name, role, is_active")
                .eq("id", user_id)
                .limit(1)
                .execute()
            )
            profile = next(iter(profile_response.data or []), None)
            if profile and profile.get("is_active"):
                return StaffPrincipal(
                    user_id=str(user_id),
                    display_name=profile.get("display_name") or "Administrator ITCC",
                    role="admin",
                )
    except Exception:
        pass

    return DEFAULT_ADMIN_PRINCIPAL
