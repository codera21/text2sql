from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from services import GeminiService, DbService
from models import ConversationHistoryItem, GroupedConversationItem
from endpoints import routers


class User(BaseModel):
    username: str


app = FastAPI(title="text2sql ✈")
app.include_router(routers)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
