from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from services import GeminiService, DbService
from models import ConversationHistoryItem


class UserPrompt(BaseModel):
    prompt_message: str


app = FastAPI(title="text2sql ✈")
db_service = DbService()


templates = Jinja2Templates(directory="src/templates")

gemini_service = GeminiService()


@app.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):

    username = "a21"
    conversation_history = db_service.get_convesation_history(username)

    context = {"request": request, "conversation_history": conversation_history}
    return templates.TemplateResponse("index.html", context=context)


@app.post("/query", response_class=HTMLResponse)
async def process_query(request: Request, prompt_message=Form(...)):

    username = "a21"
    # llm_response =   gemini_service.generate_sql_query_content(prompt_message)
    llm_response = """```sql SELECT * from `a21`  ```"""

    conversation_history_item = ConversationHistoryItem(
        user_prompt=prompt_message, response=llm_response, username=username
    )

    db_service.add_converation_history(conversation_history_item)

    conversation_history = [
        {"user_prompt": prompt_message, "response": llm_response}
    ]

    return templates.TemplateResponse(
        "chat-messages.html",
        context={"request": request, "conversation_history": conversation_history},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
