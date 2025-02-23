from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from services import GeminiService, DbService
from models import ConversationHistoryItem, GroupedConversationItem


class User(BaseModel):
    username: str


app = FastAPI(title="text2sql ✈")


# impliment to store username
username = "a21"


templates = Jinja2Templates(directory="src/templates")

# dependencies
gemini_service = GeminiService()
db_service = DbService()


@app.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):

    conversation_history = db_service.get_convesation_history(username)
    query_exec = db_service.execute_llm_sql("select * from flights")

    conversation_group = db_service.get_conversation_group(username="a21")

    conversation_history = [
        {
            "user_prompt": item["user_prompt"],
            "response": item["response"],
            "query_execution": query_exec,
        }
        for item in conversation_history
    ]

    context = {
        "request": request,
        "conversation_history": conversation_history,
        "query_exec": query_exec,
        "conversation_group": conversation_group,
    }
    return templates.TemplateResponse("index.html", context=context)


@app.post("/query", response_class=HTMLResponse)
async def process_query(request: Request, prompt_message=Form(...)):

    # llm_response =   gemini_service.generate_sql_query_content(prompt_message)
    llm_response = """SELECT * from `flights` """

    conversation_history_item = ConversationHistoryItem(
        user_prompt=prompt_message, response=llm_response, username=username
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
        "chat-messages.html",
        context={"request": request, "conversation_history": conversation_history},
    )


@app.post("/conversation-group/new", response_class=HTMLResponse)
async def create_new_chat(request: Request, username=Form(...)):
    grouped_conversation_item = GroupedConversationItem(username=username)
    db_service.add_new_conversation_group(grouped_conversation_item)

    conversation_group = db_service.get_conversation_group(username)

    return templates.TemplateResponse(
        "partials/conversation-group.html",
        context={"request": request, "conversation_group": conversation_group},
    )


@app.post("/clear-chat-history")
async def clear_chat_history(request: Request, username=Form(...)):
    return {"username": username}


@app.post("/edit/conversaton-group")
async def edid_conversation_group_action(request: Request):
    pass


@app.get("/conversation-group/{conversation_group_id}", response_class=HTMLResponse)
async def show_conversation_page(request: Request, conversation_group_id: str):

    conversation_group = db_service.get_conversation_group(username)

    conversation_group_detail = db_service.get_conversation_group_detail(
        conversation_group_id
    )

    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "conversation_group": conversation_group,
            "conversation_grouped_name": conversation_group_detail["conversation_grouped_name"],
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
