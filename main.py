from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import crud_helpers
import database_models
from api_request_response_models import UserCreate, UserResponse
from database import SessionLocal, engine
import security_helper

database_models.Base.metadata.create_all(bind=engine)

# OAuth2PasswordBearer is a class provided by FastAPI that helps with
# implementing OAuth2 authentication. It is used to extract the access token
# from the request's Authorization header and validate it.
# The tokenUrl parameter specifies the endpoint
# where clients can obtain the access token.
# In this case, it is set to "token",
# which corresponds to the /token endpoint defined in the application.

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.post("/token", status_code=200)
def user_login(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    verified_user = crud_helpers.verify_login_credentials(
        user.username, user.password, db=db
    )

    if verified_user is None:
        raise HTTPException(
            status_code=400,
            detail="Username or password is not valid.",
            headers={"www-authenticate": "bearer"},
        )

    access_token = security_helper.generate_access_token({"username": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users", status_code=200, response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):

    users = crud_helpers.get_all_users(db=db)

    if users is None or len(users) == 0:
        raise HTTPException(status_code=404, detail="No users found")

    return users


@app.get("/users/{user_id}", status_code=200, response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = crud_helpers.get_user_by_id(user_id=user_id, db=db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    try:
        user = crud_helpers.create_user(user=user, db=db)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"{user.email} is already in use. {e}"
        )

    return user


@app.put("/users/{user_id}", status_code=200, response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):

    user = crud_helpers.update_user(user_id=user_id, user=user, db=db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.delete("/users/{user_id}", status_code=200)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if crud_helpers.delete_user(user_id=user_id, db=db):
        return {"message": "User has been deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
