import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from endpoints import routers
from pydantic import BaseModel, Field

load_dotenv()


class UserPayload(BaseModel):
    name: str
    l_name: str


app = FastAPI(title="text2sql ✈")


app.include_router(routers)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
