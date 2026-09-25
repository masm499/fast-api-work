from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud_helpers
import database_models
from api_request_response_models import UserCreate, UserResponse
from database import SessionLocal, engine

database_models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

users = {}


@app.get("/users", status_code=200,response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):

    users = crud_helpers.get_all_users(db=db)

    if users is None or len(users) == 0:
        raise HTTPException(status_code=404, detail="No users found")

    return users


@app.get("/users/{user_id}", status_code=200, response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = crud_helpers.get_user_by_id( user_id=user_id,db=db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate,db: Session = Depends(get_db)):

  try:
    user =crud_helpers.create_user(user=user,db=db);
  except Exception as e:
    raise HTTPException(status_code=400, detail=f"{user.email} is already in use. {e}")
    
  return user;


@app.put("/users/{user_id}", status_code=200, response_model=UserResponse)
def update_user(user_id: int, user: UserCreate,db:Session=Depends(get_db)):
    
    user = crud_helpers.update_user(user_id=user_id,user=user,db=db);
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user;


@app.delete("/users/{user_id}", status_code=200)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if crud_helpers.delete_user(user_id=user_id, db=db):
        return {"message": "User has been deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

