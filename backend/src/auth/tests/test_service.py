"""Tests for :class:`~src.auth.service.AuthService`.

Uses an **in-memory SQLite** database so tests are fast and isolated
— no external services required.

Fixtures
--------
- ``test_engine`` / ``test_db`` — per-module engine + per-test session
- ``seed_serial``  — inserts an available serial for registration tests
- ``registered_user`` — a pre-registered user for login / profile tests
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from src.auth.service import AuthService
from src.database import Base
from src.models.serial import Serial, SerialStatus
from src.models.tenant import Tenant
from src.models.user import User
from src.shared.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from src.shared.security import hash_password

# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

TEST_SERIAL = "ES-202603-0001"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "SecureP@ss123"
TEST_NAME = "Test User"


@pytest.fixture(scope="module")
def test_engine():
    """Create an in-memory SQLite engine with FK support enabled."""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # SQLite does not enforce FKs by default — enable them.
    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def test_db(test_engine):
    """Provide a fresh, rolled-back session per test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def seed_serial(test_db: Session) -> Serial:
    """Insert an AVAILABLE serial for registration tests."""
    serial = Serial(
        id=uuid.uuid4(),
        code=TEST_SERIAL,
        status=SerialStatus.AVAILABLE,
    )
    test_db.add(serial)
    test_db.flush()
    return serial


@pytest.fixture()
def registered_user(test_db: Session, seed_serial: Serial) -> User:
    """Register a user through the service so all side-effects happen."""
    service = AuthService(test_db)
    user = service.register(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        full_name=TEST_NAME,
        serial_code=TEST_SERIAL,
    )
    return user


# -----------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------


class TestRegister:
    """Tests for ``AuthService.register``."""

    def test_register_with_valid_serial(
        self, test_db: Session, seed_serial: Serial
    ) -> None:
        service = AuthService(test_db)
        user = service.register(
            email="new@example.com",
            password="ValidPass123",
            full_name="New User",
            serial_code=TEST_SERIAL,
        )

        assert user.email == "new@example.com"
        assert user.full_name == "New User"
        assert user.role == "user"
        assert user.serial_number == TEST_SERIAL
        assert user.is_active is True

        # Serial must now be REGISTERED
        serial = (
            test_db.query(Serial)
            .filter(Serial.code == TEST_SERIAL)
            .first()
        )
        assert serial is not None
        assert serial.status == SerialStatus.REGISTERED
        assert serial.user_id == user.id

    def test_register_creates_tenant(
        self, test_db: Session, seed_serial: Serial
    ) -> None:
        service = AuthService(test_db)
        user = service.register(
            email="tenant@example.com",
            password="ValidPass123",
            full_name="Tenant User",
            serial_code=TEST_SERIAL,
        )

        tenant = test_db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        assert tenant is not None
        assert tenant.is_active is True

    def test_register_with_nonexistent_serial(self, test_db: Session) -> None:
        service = AuthService(test_db)
        with pytest.raises(ValidationError, match="does not exist"):
            service.register(
                email="fail@example.com",
                password="ValidPass123",
                full_name="Fail User",
                serial_code="INVALID-CODE",
            )

    def test_register_with_already_used_serial(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        with pytest.raises(ConflictError, match="not available"):
            service.register(
                email="other@example.com",
                password="ValidPass123",
                full_name="Other User",
                serial_code=TEST_SERIAL,
            )

    def test_register_duplicate_email(
        self, test_db: Session, seed_serial: Serial
    ) -> None:
        service = AuthService(test_db)
        # First registration succeeds
        service.register(
            email="dup@example.com",
            password="ValidPass123",
            full_name="First",
            serial_code=TEST_SERIAL,
        )

        # Insert a second available serial for the duplicate-email test
        serial2 = Serial(
            id=uuid.uuid4(),
            code="ES-202603-0002",
            status=SerialStatus.AVAILABLE,
        )
        test_db.add(serial2)
        test_db.flush()

        with pytest.raises(ConflictError, match="already registered"):
            service.register(
                email="dup@example.com",
                password="ValidPass123",
                full_name="Second",
                serial_code="ES-202603-0002",
            )


# -----------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------


class TestLogin:
    """Tests for ``AuthService.login``."""

    def test_login_valid_credentials(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        result = service.login(email=TEST_EMAIL, password=TEST_PASSWORD)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["user_id"] == str(registered_user.id)
        assert result["role"] == "user"

    def test_login_wrong_password(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            service.login(email=TEST_EMAIL, password="WrongPassword")

    def test_login_nonexistent_email(self, test_db: Session) -> None:
        service = AuthService(test_db)
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            service.login(email="nobody@example.com", password="whatever")

    def test_login_inactive_account(
        self, test_db: Session, registered_user: User
    ) -> None:
        registered_user.is_active = False
        test_db.flush()

        service = AuthService(test_db)
        with pytest.raises(AuthenticationError, match="deactivated"):
            service.login(email=TEST_EMAIL, password=TEST_PASSWORD)

    def test_login_suspended_account(
        self, test_db: Session, registered_user: User
    ) -> None:
        registered_user.is_suspended = True
        test_db.flush()

        service = AuthService(test_db)
        with pytest.raises(AuthenticationError, match="suspended"):
            service.login(email=TEST_EMAIL, password=TEST_PASSWORD)


# -----------------------------------------------------------------------
# Admin login
# -----------------------------------------------------------------------


class TestAdminLogin:
    """Tests for ``AuthService.admin_login``."""

    def test_admin_login_requires_admin_role(
        self, test_db: Session, registered_user: User
    ) -> None:
        # registered_user has role "user", not "admin"
        service = AuthService(test_db)
        with pytest.raises(AuthorizationError, match="Admin access"):
            service.admin_login(email=TEST_EMAIL, password=TEST_PASSWORD)

    def test_admin_login_success(
        self, test_db: Session, registered_user: User
    ) -> None:
        registered_user.role = "admin"
        test_db.flush()

        service = AuthService(test_db)
        result = service.admin_login(email=TEST_EMAIL, password=TEST_PASSWORD)

        assert "access_token" in result
        assert result["role"] == "admin"

    def test_admin_login_2fa_required(
        self, test_db: Session, registered_user: User
    ) -> None:
        registered_user.role = "admin"
        registered_user.two_factor_enabled = True
        test_db.flush()

        service = AuthService(test_db)
        with pytest.raises(AuthenticationError, match="Two-factor"):
            service.admin_login(email=TEST_EMAIL, password=TEST_PASSWORD)


# -----------------------------------------------------------------------
# Profile
# -----------------------------------------------------------------------


class TestProfile:
    """Tests for ``AuthService.get_profile`` and ``update_profile``."""

    def test_get_profile(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        profile = service.get_profile(registered_user.id)

        assert profile.email == TEST_EMAIL
        assert profile.full_name == TEST_NAME

    def test_get_profile_not_found(self, test_db: Session) -> None:
        service = AuthService(test_db)
        with pytest.raises(NotFoundError):
            service.get_profile(uuid.uuid4())

    def test_update_profile(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        updated = service.update_profile(
            registered_user.id, {"full_name": "Updated Name", "phone": "+1234567890"}
        )

        assert updated.full_name == "Updated Name"
        assert updated.phone == "+1234567890"

    def test_update_profile_ignores_forbidden_fields(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        updated = service.update_profile(
            registered_user.id, {"role": "admin", "is_active": False}
        )

        # Forbidden fields must be unchanged
        assert updated.role == "user"
        assert updated.is_active is True


# -----------------------------------------------------------------------
# Change password
# -----------------------------------------------------------------------


class TestChangePassword:
    """Tests for ``AuthService.change_password``."""

    def test_change_password_success(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        service.change_password(
            user_id=registered_user.id,
            old_password=TEST_PASSWORD,
            new_password="NewSecureP@ss456",
        )

        # Verify login works with new password
        result = service.login(email=TEST_EMAIL, password="NewSecureP@ss456")
        assert "access_token" in result

    def test_change_password_wrong_old(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        with pytest.raises(AuthenticationError, match="Current password"):
            service.change_password(
                user_id=registered_user.id,
                old_password="WrongOld",
                new_password="NewSecureP@ss456",
            )


# -----------------------------------------------------------------------
# Token refresh
# -----------------------------------------------------------------------


class TestRefreshToken:
    """Tests for ``AuthService.refresh_token``."""

    def test_refresh_with_valid_token(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        login_result = service.login(email=TEST_EMAIL, password=TEST_PASSWORD)

        refreshed = service.refresh_token(login_result["refresh_token"])

        assert "access_token" in refreshed
        assert "refresh_token" in refreshed
        assert refreshed["token_type"] == "bearer"
        assert refreshed["user_id"] == str(registered_user.id)
        assert refreshed["role"] == registered_user.role

    def test_refresh_with_access_token_fails(
        self, test_db: Session, registered_user: User
    ) -> None:
        service = AuthService(test_db)
        login_result = service.login(email=TEST_EMAIL, password=TEST_PASSWORD)

        with pytest.raises(AuthenticationError, match="refresh token"):
            service.refresh_token(login_result["access_token"])
