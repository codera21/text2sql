from fastapi import APIRouter
from endpoints import conversation_group


routers = APIRouter()

routers.include_router(
    conversation_group.router, prefix="/conversation-group", tags=["conversation group"]
)
