from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.database import Base
from app import models  # noqa: F401 — register model metadata


def _upgrade(database_url: str, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")


def test_baseline_creates_schema_on_empty_database(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'fresh.db'}"
    _upgrade(database_url, monkeypatch)

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert {"enquiries", "booking_proposals", "alembic_version"} <= set(inspector.get_table_names())
    assert {column["name"] for column in inspector.get_columns("enquiries")} >= {
        "id", "name", "email", "property_address", "created_at"
    }
    assert "ix_booking_proposals_enquiry_id" in {
        index["name"] for index in inspector.get_indexes("booking_proposals")
    }
    engine.dispose()


def test_baseline_accepts_existing_create_all_schema(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'existing.db'}"
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO enquiries "
            "(name,email,phone,property_address,property_type,approximate_size_sqft,message,preferred_dates,status,created_at) "
            "VALUES ('Synthetic','synthetic@example.invalid','','100 Test Street','Detached',1200,'fixture','weekday','new',CURRENT_TIMESTAMP)"
        )
    _upgrade(database_url, monkeypatch)

    with engine.connect() as connection:
        row = connection.exec_driver_sql("SELECT name FROM enquiries").one()
    assert row[0] == "Synthetic"
    assert "alembic_version" in inspect(engine).get_table_names()
    engine.dispose()


def test_baseline_refuses_partial_existing_table(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'partial.db'}"
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE enquiries (id INTEGER PRIMARY KEY)")
    try:
        _upgrade(database_url, monkeypatch)
    except RuntimeError as exc:
        assert "missing expected columns" in str(exc)
    else:
        raise AssertionError("Expected a clear error for a partial pre-existing table")
    finally:
        engine.dispose()
