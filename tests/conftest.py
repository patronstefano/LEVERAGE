"""Isolate the application database before any test module imports the app."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory


_database_directory = TemporaryDirectory(prefix="leverage-pytest-")
TEST_DATABASE = Path(_database_directory.name) / "test_leverage.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE}"


def pytest_sessionstart(session):
    from app.database import engine

    if Path(engine.url.database).resolve() != TEST_DATABASE.resolve():
        raise RuntimeError("Refusing to run tests against a non-isolated database")
