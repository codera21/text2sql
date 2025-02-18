from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from services import GeminiService


class UserPrompt(BaseModel):
    prompt_message: str


app = FastAPI(title="text2sql ✈")


templates = Jinja2Templates(directory="src/templates")

gemini_service = GeminiService()


@app.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):

    context = {"request": request}
    return templates.TemplateResponse("index.html", context=context)


@app.post("/query", response_class=HTMLResponse)
async def process_query(request: Request, prompt_message: str = Form(...)):

    conversation_history = [
        {
            "user_prompt": prompt_message,
            "llm_response": """```sql SELECT * from `a21`  ```""",
            # "llm_response": gemini_service.generate_sql_query_content(prompt_message),
        }
    ]

    return templates.TemplateResponse(
        "chat-messages.html",
        context={"request": request, "conversation_history": conversation_history},
    ).body.decode("utf-8")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
