import uvicorn
import os
import dotenv
import ibis
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import create_engine

dotenv.load_dotenv("./.env")

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="localhost")


class SETTINGS:
    POSTGRES_USER: str = os.getenv("user")
    POSTGRES_PASSWORD = os.getenv("password")
    POSTGRES_HOST: str = os.getenv("host")
    POSTGRES_PORT: str = os.getenv("port")
    POSTGRES_DB: str = os.getenv("database")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


settings = SETTINGS()


def token_authorized(token):
    return token == os.environ.get("TOKEN")


def get_data():
    conn = ibis.postgres.connect(
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        port=settings.POSTGRES_PORT,
    )
    return {"Tables": conn.list_tables()}


@app.get("/")
async def read_items(token: str = Depends(oauth2_scheme)):
    if not token_authorized(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    data = get_data()
    return data

@app.get("/<query>")
async def send_query(token: str = Depends(oauth2_scheme)):
    if not token_authorized(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    data = get_data(query)

uvicorn.run("__main__:app", host="localhost", port=8000)
