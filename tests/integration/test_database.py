import importlib
import sys
from unittest.mock import patch

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


DATABASE_MODULE = "app.database"


def reload_database_module():
    if DATABASE_MODULE in sys.modules:
        del sys.modules[DATABASE_MODULE]
    return importlib.import_module(DATABASE_MODULE)


def test_base_declaration():
    database = reload_database_module()
    Base = database.Base
    assert Base is not None


def test_get_engine_success():
    database = reload_database_module()
    engine = database.get_engine(database.database_url if hasattr(database, "database_url") else "postgresql://postgres:postgres@localhost:5432/fastapi_db")
    assert isinstance(engine, Engine)


def test_get_engine_failure():
    database = reload_database_module()
    with patch("app.database.create_engine", side_effect=SQLAlchemyError("Engine error")):
        with pytest.raises(SQLAlchemyError, match="Engine error"):
            database.get_engine("postgresql://postgres:postgres@localhost:5432/fastapi_db")


def test_get_sessionmaker():
    database = reload_database_module()
    engine = database.get_engine("postgresql://postgres:postgres@localhost:5432/fastapi_db")
    SessionLocal = database.get_sessionmaker(engine)
    assert isinstance(SessionLocal, sessionmaker)


def test_get_db():
    database = reload_database_module()
    db_gen = database.get_db()
    db = next(db_gen)
    assert db is not None
    try:
        next(db_gen)
    except StopIteration:
        pass