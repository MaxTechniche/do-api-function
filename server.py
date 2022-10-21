import uvicorn
import os
import dotenv
import psycopg2
import urllib.request

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

dotenv.load_dotenv()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="localhost")


class SETTINGS:
    POSTGRES_USER: str = os.getenv("USER")
    POSTGRES_PASSWORD = os.getenv("PASSWORD")
    POSTGRES_HOST: str = os.getenv("HOST")
    POSTGRES_PORT: str = os.getenv("PORT")
    POSTGRES_DB: str = os.getenv("DATABASE")
    DATABASE_QUERY: str = os.getenv("QUERY")
    TOKEN: str = os.getenv("TOKEN")


settings = SETTINGS()


def token_authorized(token):
    return token == settings.TOKEN


def get_data():
    conn = psycopg2.connect(
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        port=settings.POSTGRES_PORT,
    )
    query = settings.DATABASE_QUERY
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"data": data}

@app.get("/")
async def read_items(token: str = Depends(oauth2_scheme)):
    if not token_authorized(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    data = get_data()
    return data

@app.get("/ip")
async def get_ip(token: str = Depends(oauth2_scheme)):
    if not token_authorized(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')

    return {"data": external_ip, "error": "ip request"}
