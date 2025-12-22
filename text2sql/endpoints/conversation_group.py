from fastapi import APIRouter, Request, Form, Response, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from services import DbService
from models import GroupedConversationItem

from os import getenv


router = APIRouter()

# impliment to store username
username = getenv("USER", "a21")


templates = Jinja2Templates(directory="text2sql/templates")

# dependencies
db_service = DbService()


@router.post("/new", response_class=HTMLResponse)
async def create_new_chat(request: Request, project_id: str = Form(...)):
    grouped_conversation_item = GroupedConversationItem(
        username=username, project_id=project_id
    )
    conversation_group_item = db_service.add_new_conversation_group(
        grouped_conversation_item
    )

    conversation_group = db_service.get_conversation_group(username, project_id)

    return templates.TemplateResponse(
        "partials/conversation-group.html",
        context={
            "request": request,
            "conversation_group": conversation_group,
            "conversation_group_id": conversation_group_item.conversation_group_id,
            "project_id": project_id,
        },
        headers={
            "HX-Redirect": f"/conversation-group/{conversation_group_item.conversation_group_id}?project_id={project_id}"
        },
    )


@router.post("/clear", response_class=RedirectResponse)
async def clear_chat_history(project_id: str = Form(...)):

    db_service.delete_conversation_group(username=username, project_id=project_id)
    return RedirectResponse(f"/project/{project_id}", status_code=303)


@router.post("/edit", response_class=RedirectResponse)
async def edit_conversation_group_action(
    conversation_group_id: str = Form(...),
    new_conversation_group_name: str = Form(...),
    project_id: str = Form(...),
):
    db_service.edit_conversation_group(
        conversation_group_id=conversation_group_id,
        new_conversation_group_name=new_conversation_group_name,
    )

    return RedirectResponse(
        f"/conversation-group/{conversation_group_id}?project_id={project_id}",
        status_code=303,
    )


@router.post(
    "/{conversation_group_id}/delete",
    response_class=RedirectResponse,
)
async def delete_conversation_group_action(
    request: Request, conversation_group_id: str, project_id: str = Form(...)
):
    db_service.delete_conversation_by_id(
        conversation_group_id=conversation_group_id,
    )

    return Response(
        status_code=200,
        headers={"HX-Redirect": f"/project/{project_id}"},
    )


@router.get("/{conversation_group_id}", response_class=HTMLResponse)
async def show_conversation_page(
    request: Request,
    conversation_group_id: str,
    project_id: str | None = Query(default=None),
):

    conversation_group_detail = db_service.get_conversation_group_detail(
        conversation_group_id
    )

    detail_project_id = conversation_group_detail.get("project_id")
    active_project_id = (
        project_id if project_id and project_id == detail_project_id else detail_project_id
    )

    if not active_project_id:
        project = db_service.get_or_create_default_project(username)
        active_project_id = project.project_id

    projects = db_service.get_projects(username)
    if not projects:
        project = db_service.get_or_create_default_project(username)
        projects = [project.model_dump()]

    conversation_group = db_service.get_conversation_group(username, active_project_id)

    if len(conversation_group) == 0:
        grouped_conversation_item = GroupedConversationItem(
            username=username, project_id=active_project_id
        )
        new_group = db_service.add_new_conversation_group(grouped_conversation_item)
        return RedirectResponse(
            f"/conversation-group/{new_group.conversation_group_id}?project_id={active_project_id}"
        )

    conversation_history = db_service.get_conversation_history(conversation_group_id)

    conversation_history = [
        {
            "user_prompt": item["user_prompt"],
            "response": item["response"],
            "query_execution": db_service.execute_llm_sql(item["response"]),
        }
        for item in conversation_history
    ]

    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "conversation_group": conversation_group,
            "conversation_history": conversation_history,
            "conversation_group_name": conversation_group_detail[
                "conversation_group_name"
            ],
            "conversation_group_id": conversation_group_detail["conversation_group_id"],
            "projects": projects,
            "active_project_id": active_project_id,
            "project_name": conversation_group_detail.get("project_name"),
            "project_id": active_project_id,
        },
    )
