from .. import models, schemas
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# get request connected to PGDB
@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# post request connected to PGDB
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # **post.dict() automatically unpacks the fields
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# get request one id connected to PGDB
@router.get("/{id}", response_model=schemas.Post)
def get_post(id : int, db: Session = Depends(get_db)):
    # cursor.execute("""select * from post where id = %s""", (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found!")
    return post

# delete request is connected to PGDB
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.put("/{id}", response_model=schemas.Post)
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



# paused at 7:28:08 on 6/21/23