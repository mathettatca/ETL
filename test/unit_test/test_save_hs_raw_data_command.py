from pathlib import Path
import sys

import pandas as pd
import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "building_block" / "src"))
sys.path.insert(0, str(ROOT_DIR / "modules" / "data_access"))
sys.path.insert(0, str(ROOT_DIR / "modules"))

from application.request.commands.save_hs_raw_data import (
    HS_RAW_DATA_INSERT_COLUMNS,
    SaveHsRawDataCommand,
    SaveHsRawDataCommandHandler,
)
from application.models.hs_raw_data_model import HsRawDataModel
from mediator.mediatory_registry import build_data_access_registry


class FakeHsRawDataRepository:
    def __init__(self):
        self.saved_dataframes: list[pd.DataFrame] = []

    def save_dataframe(self, dataframe: pd.DataFrame) -> int:
        self.saved_dataframes.append(dataframe)
        return len(dataframe)


def build_dataframe(**overrides) -> pd.DataFrame:
    row = {column: None for column in HS_RAW_DATA_INSERT_COLUMNS}
    row.update(
        {
            "declaration_number": "DECL-001",
            "transaction_date": "2026-06-04",
            "hs_code": "0101",
            "quantity": 10.5,
            "bill_id": 1001,
            "need_check": 0,
        }
    )
    row.update(overrides)
    return pd.DataFrame([row], columns=list(row.keys()))


def test_command_to_doc_summarizes_dataframe():
    dataframe = build_dataframe()
    command = SaveHsRawDataCommand(dataframe=dataframe)

    assert command._to_doc() == {
        "row_count": 1,
        "columns": list(dataframe.columns),
    }


def test_insert_columns_come_from_hs_raw_data_model():
    assert HS_RAW_DATA_INSERT_COLUMNS == HsRawDataModel.insert_columns()
    assert SaveHsRawDataCommand.insert_columns == HsRawDataModel.insert_columns()


def test_handler_saves_dataframe_with_schema_column_order():
    repository = FakeHsRawDataRepository()
    handler = SaveHsRawDataCommandHandler(repository=repository)
    command = SaveHsRawDataCommand(dataframe=build_dataframe())

    response = handler.handle(command)

    assert response._to_doc() == {
        "status": "success",
        "message": "Save HS raw data successfully",
        "status_code": 200,
        "inserted_count": 1,
    }
    assert len(repository.saved_dataframes) == 1
    assert tuple(repository.saved_dataframes[0].columns) == HS_RAW_DATA_INSERT_COLUMNS


def test_handler_fills_missing_columns_with_null():
    repository = FakeHsRawDataRepository()
    handler = SaveHsRawDataCommandHandler(repository=repository)
    dataframe = pd.DataFrame(
        [
            {
                "declaration_number": "DECL-001",
                "hs_code": "0101",
            }
        ]
    )

    handler.handle(SaveHsRawDataCommand(dataframe=dataframe))

    saved = repository.saved_dataframes[0]
    assert tuple(saved.columns) == HS_RAW_DATA_INSERT_COLUMNS
    assert saved.loc[0, "declaration_number"] == "DECL-001"
    assert saved.loc[0, "hs_code"] == "0101"
    assert saved.loc[0, "transaction_date"] is None


def test_handler_rejects_extra_columns():
    repository = FakeHsRawDataRepository()
    handler = SaveHsRawDataCommandHandler(repository=repository)
    dataframe = build_dataframe(unknown_column="bad")

    with pytest.raises(ValueError, match="unsupported columns: unknown_column"):
        handler.handle(SaveHsRawDataCommand(dataframe=dataframe))

    assert repository.saved_dataframes == []


def test_handler_empty_dataframe_returns_zero_without_repository_call():
    repository = FakeHsRawDataRepository()
    handler = SaveHsRawDataCommandHandler(repository=repository)
    dataframe = pd.DataFrame(columns=["declaration_number", "hs_code"])

    response = handler.handle(SaveHsRawDataCommand(dataframe=dataframe))

    assert response._to_doc()["inserted_count"] == 0
    assert repository.saved_dataframes == []


def test_registry_resolves_save_hs_raw_data_handler():
    registry = build_data_access_registry()

    handler = registry.resolve(SaveHsRawDataCommand)

    assert isinstance(handler, SaveHsRawDataCommandHandler)
