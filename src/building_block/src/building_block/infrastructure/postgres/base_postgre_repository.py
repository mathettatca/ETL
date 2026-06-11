"""Shared repository abstractions and PostgreSQL base implementation."""

from __future__ import annotations

from io import StringIO
from typing import Generic, Sequence, Type, TypeVar

import pandas as pd
import psycopg2
from psycopg2 import sql as pg_sql
from psycopg2.extras import RealDictCursor, execute_values

from building_block.core.base.base_model import CustomBaseModel
from building_block.core.base.base_sql_repository import BaseSqlRepository
from building_block.infrastructure.postgres.client import (
    PostgresClient,
    PostgresClientProxy,
)

T = TypeVar("T", bound=CustomBaseModel)


class BasePostgresRepository(BaseSqlRepository[T], Generic[T]):
    model: Type[T]
    schema: str
    table_name: str
    primary_key_name: str

    def __init__(
        self,
        model: Type[T],
        schema: str,
        table_name: str,
    ) -> None:
        if not schema:
            raise ValueError(f"Schema is not configured for model '{model.__name__}'.")
        if not table_name:
            raise ValueError(f"Table name is not configured for model '{model.__name__}'.")

        self.model = model
        self.schema = schema
        self.table_name = table_name
        self.schema_table = pg_sql.Identifier(schema, table_name)
        self.client: PostgresClient = PostgresClientProxy()

    def insert(self, data: pd.DataFrame | T | Sequence[T]) -> int:
        if isinstance(data, pd.DataFrame):
            return self._insert_dataframe(data)

        if isinstance(data, self.model):
            return self._insert_model(data)

        if isinstance(data, Sequence):
            return self._insert_many(data)

        raise TypeError(f"Unsupported insert data type: {type(data)}")

    def _insert_dataframe(self, dataframe: pd.DataFrame) -> int:
        if dataframe.empty:
            return 0

        buffer = StringIO(newline="")
        dataframe.to_csv(buffer, index=False, header=True)
        buffer.seek(0)

        copy_sql = pg_sql.SQL(
            """
            COPY {} ({})
            FROM STDIN
            WITH (FORMAT CSV, HEADER TRUE)
            """
        ).format(
            self.schema_table,
            pg_sql.SQL(", ").join(
                pg_sql.Identifier(column) for column in dataframe.columns
            ),
        )

        with self.client.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.copy_expert(copy_sql, buffer)

        return len(dataframe)

    def _insert_model(self, data: T) -> int:
        dump = data._to_doc()
        if not dump:
            return 0

        columns = list(dump.keys())
        values = tuple(dump[column] for column in columns)
        placeholders = pg_sql.SQL(", ").join(pg_sql.Placeholder() for _ in columns)
        insert_sql = pg_sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            self.schema_table,
            pg_sql.SQL(", ").join(pg_sql.Identifier(column) for column in columns),
            placeholders,
        )

        with self.client.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_sql, values)
                return cursor.rowcount

    def _insert_many(self, data: Sequence[T]) -> int:
        if len(data) == 0:
            return 0

        first = data[0]
        if not isinstance(first, CustomBaseModel):
            raise TypeError(f"Sequence must contain CustomBaseModel, received {type(first)}")

        rows = []
        columns = list(first._to_doc().keys())
        for item in data:
            if not isinstance(item, CustomBaseModel):
                raise TypeError(f"Sequence must contain CustomBaseModel, received {type(item)}")
            dump = item._to_doc()
            rows.append(tuple(dump.get(column) for column in columns))

        if not columns:
            return 0

        insert_sql = pg_sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
            self.schema_table,
            pg_sql.SQL(", ").join(pg_sql.Identifier(column) for column in columns),
        )

        with self.client.get_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, insert_sql, rows)

        return len(rows)

    def update(self, id, update_model: T) -> bool:
        try:
            dump = update_model.model_dump(exclude_unset=True, mode="json")
            if not dump:
                return False

            assignments = pg_sql.SQL(", ").join(
                pg_sql.SQL("{} = %s").format(pg_sql.Identifier(column))
                for column in dump.keys()
            )
            update_sql = pg_sql.SQL("UPDATE {} SET {} WHERE id = %s").format(
                self.schema_table,
                assignments,
            )
            values = (*dump.values(), id)

            with self.client.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(update_sql, values)
                    return cursor.rowcount > 0

        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to update {self.schema}.{self.table_name}: {e}") from e

    def delete(self, id) -> bool:
        try:
            delete_sql = pg_sql.SQL("DELETE FROM {} WHERE id = %s").format(
                self.schema_table,
            )

            with self.client.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(delete_sql, (id,))
                    return cursor.rowcount > 0

        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to delete {self.schema}.{self.table_name}: {e}") from e

    def search(self, **options):
        values = tuple(options.values())
        query = pg_sql.SQL("SELECT * FROM {}").format(self.schema_table)

        if options:
            conditions = pg_sql.SQL(" AND ").join(
                pg_sql.SQL("{} = %s").format(pg_sql.Identifier(column))
                for column in options.keys()
            )
            query = pg_sql.SQL("{} WHERE {}").format(query, conditions)

        with self.client.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, values)
                rows = cursor.fetchall()

        return [self.model._to_model(dict(row)) for row in rows]
