from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check():
    return {"success": True, "message": "API berjalan"}
