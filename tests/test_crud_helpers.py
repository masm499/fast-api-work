import pytest
from sqlalchemy.orm import Session

import crud_helpers
from database import SessionLocal


# 1. Create a pytest fixture to handle the database session life cycle
@pytest.fixture(scope="function")
def db_session():
    """Provides a transactional database session for a single test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. Pass the fixture name directly as an argument to your test
def test_verify_credentials(db_session: Session):
    # Act
    user = crud_helpers.verify_login_credentials(
        "sandleeb@example.com", "string", db=db_session
    )

    # Assert
    assert user
