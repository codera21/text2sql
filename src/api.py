from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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


@app.post("/query")
async def process_querty(user_prompt: UserPrompt):
    # request json
    user_prompt = user_prompt.prompt_message

    return {
        "user_prompt": user_prompt,
        "response_text": gemini_service.generate_sql_query_content(user_prompt),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
