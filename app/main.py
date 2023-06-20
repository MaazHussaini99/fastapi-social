from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi-social', 
                            user='postgres', password='1962', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB Conn was successful!")
        break
    except Exception as error:
        print("Connecting to DB failed")
        print("Error", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, 
            {"title": "favorite foods", "content": "i like pizza", "id": 2}]


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"Message": "Welcome to my API 2.0"}


