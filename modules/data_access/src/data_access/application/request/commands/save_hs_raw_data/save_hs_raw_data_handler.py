from data_access.adapter.ports.hs_raw_data_repository_port import HsRawDataRepositoryPort
from data_access.adapter.postgres_hs_raw_data_repository_adapter import PostgresHsRawDataRepositoryAdapter
from data_access.application.base.base_handler import BaseRequestHandler
from .save_hs_raw_data_command import SaveHsRawDataCommand
from .save_hs_raw_data_response import SaveHsRawDataCommandResponse


class SaveHsRawDataCommandHandler(
    BaseRequestHandler[SaveHsRawDataCommand, SaveHsRawDataCommandResponse]
):
    def __init__(self, repository: HsRawDataRepositoryPort | None = None):
        self.repository = repository or PostgresHsRawDataRepositoryAdapter()

    def handle(
        self,
        request: SaveHsRawDataCommand,
    ) -> SaveHsRawDataCommandResponse:
        dataframe = request.normalized_dataframe()
        inserted_count = 0
        if not dataframe.empty:
            inserted_count = self.repository.save_dataframe(dataframe)

        return SaveHsRawDataCommandResponse(
            status="success",
            message="Save HS raw data successfully",
            status_code=200,
            inserted_count=inserted_count,
        )
