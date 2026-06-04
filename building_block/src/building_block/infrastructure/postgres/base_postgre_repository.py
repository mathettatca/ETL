"""Shared repository abstractions and PostgreSQL base implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from io import StringIO
import json
from typing import Any, Generic, Sequence, Type, TypeVar

from building_block.core.base.base_sql_repository import BaseSqlRepository
from building_block.infrastructure.postgres.client import PostgresClient, PostgresClientProxy
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json, RealDictCursor, execute_values

from building_block.core.base.base_model import CustomBaseModel
from building_block.infrastructure.postgres.client import postgres_client
from building_block.utils.logging import info, log_error

T = TypeVar("T", bound=CustomBaseModel)



class BasePostgresRepository(BaseSqlRepository[T], Generic[T]):
    model: Type[T]
    table_name: str
    primary_key_name: str

    def __init__(
        self,
        model: Type[T],
        table_name: str | None = None,
    ) -> None:
        self.model = model
        self.table_name = table_name or getattr(model, "table_name", "")
        self.client:PostgresClient = PostgresClientProxy() # lazy load

        if not self.table_name:
            raise Exception(f"Table name is not configured for model '{model.__name__}'.")

    
    def insert(self, data:pd.DataFrame | T | Sequence[T]):
        cols :str  = None
        sql :str= None
        values = []

        if isinstance(data,pd.DataFrame):
            if data.empty:
                return 0

            # StringIO là file-like object nằm trong RAM
            # newline="" tốt hơn newline=" "
            buffer = StringIO(newline="")

            # Ghi DataFrame thành CSV vào buffer
            data.to_csv(buffer, index=False, header=True)

            # Đưa con trỏ buffer về đầu file
            buffer.seek(0)

            copy_sql = sql.SQL("""
                COPY {} ({})
                FROM STDIN
                WITH (FORMAT CSV, HEADER TRUE)
            """).format(
                sql.Identifier(self.table_name),
                sql.SQL(", ").join(sql.Identifier(column) for column in data.columns),
            )

            with self.client.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.copy_expert(copy_sql, buffer)
                conn.commit()

        elif isinstance(data, self.model):
            with self.client.get_connection() as conn:
                with conn.cursor() as cursor:
                    dump = data._to_model()
                    cols = ", ".join(dump.keys())
                    vals = tuple(dump.values())
                    placeholders = ", ".join(["%s"] * len(dump))
                    sql = f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})"
                    cursor.execute(sql, vals)
        elif isinstance(data, Sequence) and len(data) > 0:
            first = data[0]
            if not isinstance(first, CustomBaseModel):
                raise TypeError(f"Sequence phải chứa BaseModel, nhận {type(first)}")
            dump = first.model_dump()
            cols = ", ".join(dump.keys())
            sql = f"INSERT INTO {self.table_name} ({cols}) VALUES %s"
            values = [tuple(d.model_dump().values()) for d in data]

        with self.client.get_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor,sql,values)

    def update(self, id, update_model: T) -> bool:
        try:
            dump = update_model.model_dump(exclude_unset=True)  # Chỉ lấy fields được set
            if not dump:
                return False

            cols = ", ".join(f"{k} = %s" for k in dump.keys())
            sql = f"UPDATE {self.table_name} SET {cols} WHERE id = %s"
            values = (*dump.values(), id)  # Unpack values + id ở cuối

            with self.client.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, values)
                    return cursor.rowcount > 0  # True nếu có row được update

        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to update {self.table_name}: {e}") from e

    def delete(self, id) -> bool:
        try:
            sql = f"DELETE FROM {self.table_name} WHERE id = %s"

            with self.client.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (id,))
                    return cursor.rowcount > 0  # True nếu có row được delete

        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to delete {self.table_name}: {e}") from e

    def search(self, **options):
        where_clause = ""
        values = tuple(options.values())
        if options:
            conditions = " AND ".join(f"{key} = %s" for key in options.keys())
            where_clause = f" WHERE {conditions}"

        query = f"SELECT * FROM {self.table_name}{where_clause}"
        with self.client.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, values)
                rows = cursor.fetchall()

        return [self.model._to_model(dict(row)) for row in rows]
