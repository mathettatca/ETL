"""PostgreSQL client singleton."""

from __future__ import annotations

from contextlib import contextmanager
from threading import Lock

import psycopg2
from psycopg2.extensions import connection
from psycopg2.pool import ThreadedConnectionPool
from typing import Any, Generator               # cho type hint contextmanager

from building_block.utils.logging import log_success
from building_block.shared.setting import PostgresSetting

class PostgresClient:
    _instance: "PostgresClient | None" = None
    _pool: ThreadedConnectionPool | None = None  # ✅ Khai báo đúng
    _lock = Lock()

    def __new__(cls) -> "PostgresClient":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize PostgreSQL connection pool."""
        try:
            setting = PostgresSetting()

            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=setting.connection_string
            )

            conn = self._pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            conn.commit()
            self._pool.putconn(conn)

            log_success(
                f"Connected to PostgreSQL pool successfully | DB: {setting.postgres_db}"
            )
        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to initialize PostgreSQL pool: {e}") from e

    @contextmanager
    def get_connection(self) ->Generator[connection,None,None]:
        """Lấy connection từ pool, tự động trả lại sau khi dùng xong."""
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def close(self) -> None:
        """Đóng toàn bộ pool khi shutdown."""
        if self._pool:
            self._pool.closeall()
            self._pool = None

    @classmethod                        # ✅ Thêm reset() vào PostgresClient
    def reset(cls) -> None:
        """Reset singleton, dùng cho testing."""
        with cls._lock:
            if cls._instance:
                cls._instance.close()
            cls._instance = None


class PostgresClientProxy:
    """Lazy proxy that initializes the Postgres client only on first use."""

    def __getattr__(self, name: str):
        return getattr(PostgresClient(), name)

    def close(self) -> None:
        PostgresClient().close()   # ✅ Singleton nên vẫn là instance gốc

    def reset(self) -> None:
        PostgresClient.reset()     # ✅ Giờ method đã tồn tại


postgres_client = PostgresClientProxy()

class PostgresClientProxy:
    """Lazy proxy that initializes the Postgres client only on first use."""

    def __getattr__(self, name: str):
        return getattr(PostgresClient(), name)

    def close(self) -> None:
        PostgresClient().close()

    def reset(self) -> None:
        PostgresClient.reset()


postgres_client = PostgresClientProxy()
