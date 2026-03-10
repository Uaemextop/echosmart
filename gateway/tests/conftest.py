import os
import sys
import pytest

# Ensure gateway root is on path so `from src.…` imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SQLITE_PATH", ":memory:")


@pytest.fixture
def config():
    from src.config import Config
    return Config()


@pytest.fixture
def local_db():
    from src.local_db import LocalDB
    db = LocalDB(":memory:")
    yield db
    db.close()
