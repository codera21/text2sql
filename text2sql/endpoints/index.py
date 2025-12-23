from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services import DbService
from os import getenv

router = APIRouter()
username = getenv("USER", "a21")

templates = Jinja2Templates(directory="text2sql/templates")

db_service = DbService()


@router.get("/", response_class=HTMLResponse)
async def show_project_selection_page(request: Request):

    projects = db_service.get_projects(username)

    return templates.TemplateResponse(
        "project-select.html",
        context={
            "request": request,
            "projects": projects,
            "conversation_group": [],
            "conversation_group_id": None,
            "project_id": None,
            "active_project_id": None,
            "show_sidebar": False,
        },
    )
