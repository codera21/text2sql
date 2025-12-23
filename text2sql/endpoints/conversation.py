from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from services import DbService, GeminiService
from models import ConversationHistoryItem
from os import getenv

router = APIRouter()
# impliment to store username
username = getenv("USER", "a21")


templates = Jinja2Templates(directory="text2sql/templates")

# dependencies
gemini_service = GeminiService()
db_service = DbService()


@router.post("/query", response_class=HTMLResponse)
async def process_query(
    request: Request,
    conversation_group_id: str = Form(...),
    prompt_message: str = Form(...),
):

    try:
        llm_response = gemini_service.generate_suitable_sql(prompt_message)
    except Exception as e:
        return {"message": "Something Went Wrong"}

    conversation_history_item = ConversationHistoryItem(
        user_prompt=prompt_message,
        response=llm_response,
        username=username,
        conversation_group_id=conversation_group_id,
    )

    query_exec = db_service.execute_llm_sql(llm_response)

    db_service.add_converation_history(conversation_history_item)

    conversation_history = [
        {
            "user_prompt": prompt_message,
            "response": llm_response,
            "query_execution": query_exec,
        }
    ]

    return templates.TemplateResponse(
        "partials/chat-messages.html",
        context={"request": request, "conversation_history": conversation_history},
    )
