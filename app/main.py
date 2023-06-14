from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published : bool = True

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


# def find_post(id):
#     for p in my_posts:
#         if p ["id"] == id:
#             return p
        
# def find_index(id):
#     for i, p in enumerate(my_posts):
#         if p['id'] == id:
#             return i

@app.get("/")
def read_root():
    return {"Message": "Welcome to my API 2.0"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}







# get request connected to PGDB
@app.get("/posts")
def get_posts():
    cursor.execute("""select * from post""")
    posts = cursor.fetchall()
    return {"data": posts}

# post request connected to PGDB
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""insert into post (title, content, published) values (%s, %s, %s)returning * """,
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

# get request one id connected to PGDB
@app.get("/posts/{id}")
def get_post(id : int, response: Response):
    cursor.execute("""select * from post where id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!")
    return {"post": post}

# delete request is connected to PGDB
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    #find the index in the array which has the required id
    #my_posts.pop(index)
    cursor.execute("""DELETE FROM POST WHERE ID = %s returning *""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist!")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# update request is connected to PGDB
@app.put("/posts/{id}")
def update_post(id : int, post : Post):
    cursor.execute("""UPDATE POST SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, (str(id))))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist!")

    return {'data': updated_post}
