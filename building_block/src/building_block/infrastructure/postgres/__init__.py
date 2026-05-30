"""PostgreSQL infrastructure."""

from building_block.core.base.base_sql_repository import BaseSqlRepository as BaseRepository
from building_block.infrastructure.postgres.base_postgre_repository import (
    BasePostgresRepository,
)
from building_block.infrastructure.postgres.client import postgres_client

__all__ = ["BaseRepository", "BasePostgresRepository", "postgres_client"]
