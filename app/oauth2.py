from jose import JWTError, jwt
from datetime  import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
#secret ket
#Algorithm
#Expiration time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "yweghj326yu287e46y3uwdjsxbgdyue3r4tf674832r6yfegdwuhbwue8r7u"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credential_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credential_exception
    
        token_data = schemas.TokenData(id = id)

    except JWTError:
        raise credential_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session =  Depends(database.get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", 
                                         headers={"WWW_Authenticate": "Bearer"})
    
    token = verify_access_token(token, credential_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
