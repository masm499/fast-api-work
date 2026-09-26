import logging
from typing import Optional

from fastapi import (  # Response allows us to set response headers and cookies
    Depends, FastAPI, HTTPException, Request, Response)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import crud_helpers
import database_models
import security_helper
from api_request_response_models import UserCreate, UserResponse
from database import SessionLocal, engine

logger = logging.getLogger("uvicorn.error")

database_models.Base.metadata.create_all(bind=engine)

# OAuth2PasswordBearer is a class provided by FastAPI that helps with
# implementing OAuth2 authentication. It is used to extract the access token
# from the request's Authorization header and validate it.
# The tokenUrl parameter specifies the endpoint
# where clients can obtain the access token.
# In this case, it is set to "token",
# which corresponds to the /token endpoint defined in the application.

oauth_header_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.post("/token", status_code=200)
def get_token(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # This is the token issuer when a user logs in using username and password via oauth2.
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


def get_current_user(
    request: Request,
    token: str = Depends(oauth_header_scheme),
    db: Session = Depends(get_db),
):

    try:
        if token is None:  # No token in the header, lets check the httpCookie

            token = request.cookies.get("access_token")
            # logger.info(f"Cookie Token:{token}");

            if token is None:
                raise HTTPException(
                    status_code=401, detail="Invalid credentials. No token found."
                )

        payload = security_helper.jwt.decode(
            token, security_helper.SECRET_STRING, security_helper.ALGORITHM
        )

        email: str = payload.get("username", None)

        # logger.info(f"Email retrieved : {email}")

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials: Invalid Token",
            )

    except security_helper.JWTError:
        raise HTTPException(
            status_code=400, detail="Invalid authentication credentials : Invalid Token"
        )

    user = crud_helpers.get_user_by_email(email=email, db=db)

    if user is None:

        raise HTTPException(
            status_code=400, detail="Invalid authentication credentials : Invalid Token"
        )

    return user


@app.get("/users/me", response_model=UserResponse)
def read_user_me(current_user: UserResponse = Depends(get_current_user)):
    # 2. oauth2_scheme automatically redirects the request here.
    return current_user


@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Next update is to use depends with create user.
    try:
        user = crud_helpers.create_user(user=user, db=db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{user.email} is already in use.")

    return user


@app.post("/login", status_code=200)
def user_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = crud_helpers.verify_login_credentials(
        form_data.username, form_data.password, db=db
    )

    if user is None:
        raise HTTPException(
            status_code=404, detail="The username/password credentials are not valid."
        )

    token = security_helper.generate_access_token(({"username": form_data.username}))

    response.set_cookie(
        key="access_token",
        value=token,
        max_age=1800,
        expires=1800,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Session has been successfully initiated."}


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


@app.get("/logout", status_code=200)
def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "session has been closed successfully"}
