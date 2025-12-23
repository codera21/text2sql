from fastapi import APIRouter
from endpoints import conversation_group, conversation, project, index


routers = APIRouter()

routers.include_router(
    index.router, prefix="", tags=["index"]
)

routers.include_router(
    conversation.router, prefix="", tags=["conversation"]
)


routers.include_router(
    conversation_group.router, prefix="/conversation-group", tags=["conversation group"]
)

routers.include_router(
    project.router, prefix="/project", tags=["project"]
)
