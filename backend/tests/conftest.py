"""Pytest fixtures and test database configuration."""
import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import Organization, User

# In-memory SQLite for rapid unit and isolation testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_org_and_users(db):
    org = Organization(name="Test Law Firm", slug="test-firm", is_active=True)
    db.add(org)
    db.flush()

    admin_user = User(
        organization_id=org.id,
        email="admin@test.local",
        hashed_password=get_password_hash("password123"),
        full_name="Admin Partner",
        role="admin",
        is_active=True,
        is_verified=True,
    )
    attorney_1 = User(
        organization_id=org.id,
        email="attorney1@test.local",
        hashed_password=get_password_hash("password123"),
        full_name="Attorney Alpha",
        role="attorney",
        is_active=True,
        is_verified=True,
    )
    attorney_2 = User(
        organization_id=org.id,
        email="attorney2@test.local",
        hashed_password=get_password_hash("password123"),
        full_name="Attorney Beta",
        role="attorney",
        is_active=True,
        is_verified=True,
    )
    db.add_all([admin_user, attorney_1, attorney_2])
    db.commit()

    return {
        "org": org,
        "admin": admin_user,
        "attorney_1": attorney_1,
        "attorney_2": attorney_2,
    }
