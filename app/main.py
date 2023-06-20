from typing import List
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db

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

# get request connected to PGDB
@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# post request connected to PGDB
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # **post.dict() automatically unpacks the fields
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# get request one id connected to PGDB
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id : int, db: Session = Depends(get_db)):
    # cursor.execute("""select * from post where id = %s""", (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!")
    return post

# delete request is connected to PGDB
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int, db: Session = Depends(get_db)):
    #find the index in the array which has the required id
    #my_posts.pop(index)
    # cursor.execute("""DELETE FROM POST WHERE ID = %s returning *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist!")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# update request is connected to PGDB
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id : int, update_post : schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE POST SET title = %s, content = %s, 
    # published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, (str(id))))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!")
    
    post_query.update(update_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


# Users API Paths
# post request for create user
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# paused at 6:11:08 on 6/19/23