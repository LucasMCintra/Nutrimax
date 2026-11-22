from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.db import Base, get_db
from app.main import app
from app.core.config import settings
from app.models import Client, NutritionTarget, User  # noqa: F401  (ensure models register on metadata)

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


Base.metadata.create_all(engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    settings.upload_dir = str(tmp_path / "uploads")
    return TestClient(app)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()