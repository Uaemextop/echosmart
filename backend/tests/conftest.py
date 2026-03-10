import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from src.database import Base, get_db
from src.main import app
from src.middleware.auth import create_access_token
from src.models.tenant import Tenant
from src.models.user import User
from src.services.auth_service import hash_password

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def tenant(db):
    t = Tenant(
        id=str(uuid.uuid4()),
        name="Test Corp",
        slug="test-corp",
        plan="pro",
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@pytest.fixture
def admin_user(db, tenant):
    u = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        email="admin@test.com",
        password_hash=hash_password("password123"),
        full_name="Admin User",
        role="admin",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def operator_user(db, tenant):
    u = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        email="operator@test.com",
        password_hash=hash_password("password123"),
        full_name="Operator User",
        role="operator",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def viewer_user(db, tenant):
    u = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        email="viewer@test.com",
        password_hash=hash_password("password123"),
        full_name="Viewer User",
        role="viewer",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_token(user: User) -> str:
    return create_access_token(
        {
            "sub": user.id,
            "email": user.email,
            "tenant_id": user.tenant_id,
            "role": user.role,
        }
    )


@pytest.fixture
def admin_token(admin_user):
    return _make_token(admin_user)


@pytest.fixture
def operator_token(operator_user):
    return _make_token(operator_user)


@pytest.fixture
def viewer_token(viewer_user):
    return _make_token(viewer_user)


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def operator_headers(operator_token):
    return {"Authorization": f"Bearer {operator_token}"}


@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}
