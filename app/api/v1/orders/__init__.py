from fastapi import APIRouter

from .orders import router

orders_router = APIRouter()
orders_router.include_router(router, tags=["生产管理"])

__all__ = ["orders_router"]