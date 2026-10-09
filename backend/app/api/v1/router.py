from fastapi import APIRouter

from app.api.v1.endpoints import auth, certiport, health, sitasi, sync

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(sitasi.router)
api_router.include_router(certiport.router)
api_router.include_router(sync.router)
