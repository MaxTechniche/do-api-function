import uvicorn
import os
import dotenv
import psycopg2
from requests import get

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

dotenv.load_dotenv()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="localhost")


class SETTINGS:
    POSTGRES_USER: str = os.getenv("user")
    POSTGRES_PASSWORD = os.getenv("password")
    POSTGRES_HOST: str = os.getenv("host")
    POSTGRES_PORT: str = os.getenv("port")
    POSTGRES_DB: str = os.getenv("database")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    DATABASE_QUERY: str = os.getenv("QUERY")


settings = SETTINGS()


def token_authorized(token):
    return token == os.environ.get("TOKEN")


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

    ip = get('https://api.ipify.org').content.decode('utf8')
    return {"The IP address for this function is": ip}
