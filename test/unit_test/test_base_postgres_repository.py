from pathlib import Path
import sys

import pandas as pd
from psycopg2 import sql as pg_sql


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "building_block" / "src"))

from building_block.core.base.base_model import CustomBaseModel
from building_block.infrastructure.postgres.base_postgre_repository import (
    BasePostgresRepository,
)


class FakeModel(CustomBaseModel):
    id: int | None = None
    name: str | None = None


class FakeCursor:
    def __init__(self, rows=None, rowcount=1):
        self.rows = rows or []
        self.rowcount = rowcount
        self.executed_query = None
        self.executed_values = None
        self.copied_query = None
        self.copied_buffer = None
        self.cursor_factory = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, values=None):
        self.executed_query = query
        self.executed_values = values

    def copy_expert(self, query, buffer):
        self.copied_query = query
        self.copied_buffer = buffer

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor

    def cursor(self, **kwargs):
        self.cursor_instance.cursor_factory = kwargs.get("cursor_factory")
        return self.cursor_instance


class FakeConnectionContext:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeClient:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_connection(self):
        return FakeConnectionContext(FakeConnection(self.cursor))


def build_repository(cursor):
    repository = BasePostgresRepository(
        model=FakeModel,
        schema="bronze",
        table_name="hs_raw_data",
    )
    repository.client = FakeClient(cursor)
    return repository


def test_init_sets_schema_qualified_table_identifier():
    repository = BasePostgresRepository(
        model=FakeModel,
        schema="bronze",
        table_name="hs_raw_data",
    )

    assert repository.schema == "bronze"
    assert repository.table_name == "hs_raw_data"
    assert isinstance(repository.schema_table, pg_sql.Identifier)


def test_insert_dataframe_empty_returns_zero_without_copy():
    cursor = FakeCursor()
    repository = build_repository(cursor)

    inserted_count = repository.insert(pd.DataFrame())

    assert inserted_count == 0
    assert cursor.copied_query is None


def test_insert_dataframe_uses_copy_expert():
    cursor = FakeCursor()
    repository = build_repository(cursor)
    dataframe = pd.DataFrame(
        [
            {
                "declaration_number": "A001",
                "hs_code": "0101",
            }
        ]
    )

    inserted_count = repository.insert(dataframe)

    assert inserted_count == 1
    assert cursor.copied_query is not None
    assert cursor.copied_buffer.getvalue().startswith("declaration_number,hs_code")


def test_insert_single_model_executes_insert_query():
    cursor = FakeCursor(rowcount=1)
    repository = build_repository(cursor)

    inserted_count = repository.insert(FakeModel(id=1, name="item"))

    assert inserted_count == 1
    assert cursor.executed_query is not None
    assert cursor.executed_values == (1, "item")


def test_insert_many_uses_execute_values(monkeypatch):
    cursor = FakeCursor()
    repository = build_repository(cursor)
    execute_values_call = {}

    def fake_execute_values(cursor_arg, query_arg, values_arg):
        execute_values_call["cursor"] = cursor_arg
        execute_values_call["query"] = query_arg
        execute_values_call["values"] = values_arg

    monkeypatch.setattr(
        "building_block.infrastructure.postgres.base_postgre_repository.execute_values",
        fake_execute_values,
    )

    inserted_count = repository.insert(
        [
            FakeModel(id=1, name="first"),
            FakeModel(id=2, name="second"),
        ]
    )

    assert inserted_count == 2
    assert execute_values_call["cursor"] is cursor
    assert execute_values_call["query"] is not None
    assert execute_values_call["values"] == [(1, "first"), (2, "second")]


def test_update_executes_schema_qualified_update():
    cursor = FakeCursor(rowcount=1)
    repository = build_repository(cursor)

    updated = repository.update(1, FakeModel(name="updated"))

    assert updated is True
    assert cursor.executed_query is not None
    assert cursor.executed_values == ("updated", 1)


def test_delete_executes_delete():
    cursor = FakeCursor(rowcount=1)
    repository = build_repository(cursor)

    deleted = repository.delete(1)

    assert deleted is True
    assert cursor.executed_query is not None
    assert cursor.executed_values == (1,)


def test_search_returns_models_from_rows():
    cursor = FakeCursor(rows=[{"id": 1, "name": "item"}])
    repository = build_repository(cursor)

    result = repository.search(name="item")

    assert result == [FakeModel(id=1, name="item")]
    assert cursor.executed_query is not None
    assert cursor.executed_values == ("item",)
    assert cursor.cursor_factory is not None
