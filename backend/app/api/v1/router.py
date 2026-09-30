from fastapi import APIRouter

from app.api.v1.endpoints import certiport, health, sitasi

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(sitasi.router)
api_router.include_router(certiport.router)
