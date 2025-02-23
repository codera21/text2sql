from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from services import DbService, GeminiService
from models import GroupedConversationItem

from os import getenv


router = APIRouter()

# impliment to store username
username = getenv("USER", "a21")


templates = Jinja2Templates(directory="src/templates")

# dependencies
gemini_service = GeminiService()
db_service = DbService()


@router.post("/new", response_class=HTMLResponse)
async def create_new_chat(request: Request):
    grouped_conversation_item = GroupedConversationItem(username=username)
    conversation_group_item = db_service.add_new_conversation_group(
        grouped_conversation_item
    )

    conversation_group = db_service.get_conversation_group(username)

    return templates.TemplateResponse(
        "partials/conversation-group.html",
        context={
            "request": request,
            "conversation_group": conversation_group,
            "conversation_group_id": conversation_group_item.conversation_group_id,
        },
        headers={"HX-Redirect": "/"},
    )


@router.post("/clear", response_class=RedirectResponse)
async def clear_chat_history(request: Request):

    db_service.delete_conversation_group(username=username)
    return RedirectResponse("/", status_code=303)


@router.post("/edit", response_class=RedirectResponse)
async def edit_conversation_group_action(
    conversation_group_id: str = Form(...),
    new_conversation_group_name: str = Form(...),
):
    db_service.edit_conversation_group(
        conversation_group_id=conversation_group_id,
        new_conversation_group_name=new_conversation_group_name,
    )

    return RedirectResponse(
        f"/conversation-group/{conversation_group_id}", status_code=303
    )


@router.post(
    "/{conversation_group_id}/delete",
    response_class=RedirectResponse,
)
async def delete_conversation_group_action(
    request: Request, conversation_group_id: str
):
    db_service.delete_conversation_by_id(
        conversation_group_id=conversation_group_id,
    )

    return Response(status_code=200, headers={"HX-Redirect": "/"})


@router.get("/{conversation_group_id}", response_class=HTMLResponse)
async def show_conversation_page(request: Request, conversation_group_id: str):

    conversation_group = db_service.get_conversation_group(username)

    conversation_group_detail = db_service.get_conversation_group_detail(
        conversation_group_id
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
        },
    )
