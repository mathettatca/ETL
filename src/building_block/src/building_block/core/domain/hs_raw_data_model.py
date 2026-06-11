from typing import ClassVar

from building_block.core.base.base_model import CustomBaseModel


class HsRawDataModel(CustomBaseModel):
    schema_name: ClassVar[str] = "bronze"
    table_name: ClassVar[str] = "hs_raw_data"

    declaration_number: str | None = None
    transaction_date: str | None = None
    hs_code: str | None = None
    product_description: str | None = None
    product_description_en: str | None = None
    supplier_name: str | None = None
    buyer_name: str | None = None
    quantity: float | None = None
    quantity_unit: str | None = None
    unit_price_usd: float | None = None
    unit_price_foreign_currency: float | None = None
    total_price_foreign_currency: float | None = None
    total_amount_usd: float | None = None
    exchange_rate: float | None = None
    incoterms: str | None = None
    payment_method: str | None = None
    import_country: str | None = None
    transport_mode: str | None = None
    country_of_origin: str | None = None
    customs_branch_code: str | None = None
    customs_branch_name: str | None = None
    bill_id: int | None = None
    buyer_country: str | None = None
    customs_branch_code_secondary: str | None = None
    date: str | None = None
    exporter_country: str | None = None
    foreign_currency: str | None = None
    importer_address_vn: str | None = None
    importer_name_en: str | None = None
    importer_tel: str | None = None
    import_type: str | None = None
    data_source: str | None = None
    mongo_file_id: str | None = None
    need_check: int | None = None

    @classmethod
    def insert_columns(cls) -> tuple[str, ...]:
        return tuple(cls.model_fields.keys())

