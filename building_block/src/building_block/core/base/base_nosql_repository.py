"""Shared repository abstractions and MongoDB base implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from building_block.core.base.base_model import CustomBaseModel

T = TypeVar("T", bound=CustomBaseModel)


class BaseNoSqlRepository(ABC, Generic[T]):
    """Generic repository contract used by the application layer."""

    @abstractmethod
    def get(self, **filter_options: Any) -> T | None:
        """
        Find a single item that matches the provided filters.
        
        Returns:
            Model instance or None if not found
        """

    @abstractmethod
    def find_many(self, **filter_options: Any) -> list[T]:
        """
        Find multiple items that match the provided filters.
        
        Returns:
            List of model instances
        """

    @abstractmethod
    def insert_one(self, model: T) -> str | None:
        """
        Insert a single model by converting it to document using model._to_doc().
        
        Args:
            model: Model instance to persist (will call model._to_doc() internally)
            
        Returns:
            Document ID or None if insert fails
        """

    @abstractmethod
    def insert_many(self, models: list[T]) -> bool:
        """
        Insert multiple models by converting them to documents using _to_doc().
        
        Args:
            models: List of model instances (each will call _to_doc() internally)
            
        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    def update_one(self, update_model: T) -> bool:
        """
        Update a single model by converting it to document using update_model._to_doc().
        
        Args:
            update_model: Model instance to update (will call _to_doc() internally)
            
        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    def delete_one(self, **filter_options: Any) -> bool:
        """
        Delete a single item matching the provided filters.
        
        Returns:
            True if successful, False otherwise
        """
