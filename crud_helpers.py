from sqlalchemy.orm import Session

from api_request_response_models import UserCreate
from database_models import Users
from security_helper import hash_password, verify_password

# This module only executes queries and return results or exceptions,
# no validation or further processing is performed here


def verify_login_credentials(email: str, password: str, db: Session):
    # 1. Look up the user by email first
    user = db.query(Users).filter(Users.email == email).first()

    # 2. If user doesn't exist, return None
    if not user:
        return None

    # 3. Use Passlib to securely verify the raw password against the stored hash
    # user.password contains the Argon2 hash retrieved from the database
    is_password_correct = verify_password(password, user.password)

    if not is_password_correct:
        return None

    return user


def get_all_users(db: Session):
    return db.query(Users).all()


def get_user_by_id(user_id: int, db: Session):
    return db.query(Users).filter(Users.id == user_id).first()


def get_user_by_email(email: str, db: Session):
    return db.query(Users).filter(Users.email == email).first()


def create_user(user: UserCreate, db: Session):
    db_user = Users(
        name=user.name, email=user.email, password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(user_id: int, user: UserCreate, db: Session):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if db_user:
        setattr(db_user, "name", user.name)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None


def delete_user(user_id: int, db: Session):
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
