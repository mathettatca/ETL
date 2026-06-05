from building_block.core.domain.hs_raw_data_model import HsRawDataModel
from building_block.utils.file_utils import resolve_file_dest_path
from building_block.utils.logging import info, log_success
import pandas as pd
from mediator import Mediator, build_data_access_mediator
from building_block.shared.enum import FileDownloadStatus, FileSource
from application.request.commands.audit_file_download.audit_file_download_command import (
    AuditFileDownloadCommand,
)
from application.request.commands.save_hs_raw_data.save_hs_raw_data_command import SaveHsRawDataCommand

def init_data_access() -> Mediator:
    return build_data_access_mediator()


def run_create_file_use_case(mediator: Mediator):
    file_name = "data.csv"
    file_local_path = resolve_file_dest_path(file_name, "tmp")


    request = AuditFileDownloadCommand(
        file_name=file_name,
        file_local_path=file_local_path,
        file_source=FileSource.GOOGLE_DRIVE,
        download_status=FileDownloadStatus.PENDING,
        drive_file_id="1A2B3C4D5E",
        mime_type="text/csv",
        size=2048,
    )

    info(f"Create file request: {request._to_doc()}")

    response = mediator.send(request)

    log_success(f"Create file use case finished: {response._to_doc()}")
    return response

def run_hs_raw_data_usecase(mediator: Mediator):

    sample_hs_raw_data = HsRawDataModel(
        declaration_number="105678901230",
        transaction_date="2026-03-10",
        hs_code="55121900",
        product_description="Vải dệt thoi từ xơ staple tổng hợp",
        product_description_en="Woven fabrics of synthetic staple fibres",
        supplier_name="ABC TEXTILE CO., LTD",
        buyer_name="STS GARMENT VIETNAM CO., LTD",
        quantity=1500.5,
        quantity_unit="MTR",
        unit_price_usd=2.35,
        unit_price_foreign_currency=2.35,
        total_price_foreign_currency=3526.18,
        total_amount_usd=3526.18,
        exchange_rate=1.0,
        incoterms="CIF",
        payment_method="T/T",
        import_country="Vietnam",
        transport_mode="Sea",
        country_of_origin="China",
        customs_branch_code="02CI",
        customs_branch_name="Chi cục Hải quan Cảng Sài Gòn KV1",
        bill_id=987654321,
        buyer_country="Vietnam",
        customs_branch_code_secondary="02CI01",
        date="2026-03-10",
        exporter_country="China",
        foreign_currency="USD",
        importer_address_vn="Quận 2, TP. Hồ Chí Minh, Việt Nam",
        importer_name_en="STS GARMENT VIETNAM CO., LTD",
        importer_tel="02812345678",
        import_type="Import",
        data_source="google_drive",
        mongo_file_id="665f1a8c2f3b8a9d12345678",
        need_check=0,
    )
    df = pd.DataFrame([sample_hs_raw_data._to_doc()])
    request = SaveHsRawDataCommand(dataframe=df)
    info(f"Create file request: {df.info()}")

    response = mediator.send(request)

    log_success(f"Create file use case finished: {response._to_doc()}")
    return response


def main():
    log_success("Data access started")
    mediator = init_data_access()
    run_hs_raw_data_usecase(mediator)


if __name__ == "__main__":
   main()
