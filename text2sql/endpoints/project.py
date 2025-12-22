from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from services import DbService
from models import ProjectItem, GroupedConversationItem
from os import getenv


router = APIRouter()

username = getenv("USER", "a21")

db_service = DbService()


@router.post("/new", response_class=RedirectResponse)
async def create_project(project_name: str = Form(default="New Project")):
    project_title = project_name.strip() if project_name else ""
    project = ProjectItem(
        username=username,
        project_name=project_title or "New Project",
    )
    db_service.add_new_project(project)

    first_group = GroupedConversationItem(
        username=username, project_id=project.project_id
    )
    conversation_group = db_service.add_new_conversation_group(first_group)

    return RedirectResponse(
        f"/conversation-group/{conversation_group.conversation_group_id}?project_id={project.project_id}",
        status_code=303,
    )


@router.get("/{project_id}")
async def open_project(project_id: str):
    try:
        db_service.get_project_detail(project_id)
    except ValueError:
        default_project = db_service.get_or_create_default_project(username)
        project_id = default_project.project_id

    conversation_group = db_service.get_conversation_group(username, project_id)

    if conversation_group:
        target_group_id = conversation_group[0]["conversation_group_id"]
    else:
        grouped_conversation_item = GroupedConversationItem(
            username=username, project_id=project_id
        )
        convo_grp = db_service.add_new_conversation_group(grouped_conversation_item)
        target_group_id = convo_grp.conversation_group_id

    return RedirectResponse(
        f"/conversation-group/{target_group_id}?project_id={project_id}",
        status_code=303,
    )
