from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
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


def find_post(id):
    for p in my_posts:
        if p ["id"] == id:
            return p
        
def find_index(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
def read_root():
    return {"Message": "Welcome to my API 2.0"}

@app.get("/posts")
def get_posts():
    cursor.execute("""select * from post""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""insert into post (title, content, published) values (%s, %s, %s)returning * """,
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id : int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!")
    return {"post": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    #find the index in the array which has the required id
    #my_posts.pop(index)
    index = find_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist!")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id : int, post : Post):

    index = find_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist!")
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {'data': post_dict}
