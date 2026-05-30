"""Shared SQL repository abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

import pandas as pd

from building_block.core.base.base_model import CustomBaseModel

T = TypeVar("T", bound=CustomBaseModel)


class BaseSqlRepository(ABC, Generic[T]):
    """Generic SQL repository contract used by the application layer."""

    @abstractmethod
    def insert(self, data: pd.DataFrame | T | Sequence[T]) -> None:
        """Insert one model, many models, or a dataframe into storage."""

    @abstractmethod
    def update(self, id, update_model: T) -> bool:
        """Update a single model in storage."""

    @abstractmethod
    def delete(self,id) ->bool:
        """Delete model with id in storage."""

    @abstractmethod
    def search(self,**options):
        """Search model from storage"""
