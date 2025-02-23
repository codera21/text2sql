from fastapi import APIRouter
from endpoints import conversation_group , conversation


routers = APIRouter()

routers.include_router(
    conversation.router, prefix="", tags=["conversation"]
)


routers.include_router(
    conversation_group.router, prefix="/conversation-group", tags=["conversation group"]
)
