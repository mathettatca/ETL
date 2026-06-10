"""Schema configuration for HS-code processing."""

from __future__ import annotations

from building_block.utils.logging import info

COLUMN_IMP_MAPPING = {
    "Declaration No": "declaration_number",
    "Transaction Date": "transaction_date",
    "HS Code": "hs_code",
    "Product Description": "product_description",
    "Product Desc(EN)": "product_description_en",
    "Supplier": "supplier_name",
    "Buyer": "buyer_name",
    "quantity": "quantity",
    "Quantity unit": "quantity_unit",
    "Unit Price(USD)": "unit_price_usd",
    "Unit Price(Currency)": "unit_price_foreign_currency",
    "Total Price(Currency)": "total_price_foreign_currency",
    "Amount": "total_amount_usd",
    "Exchange Rate": "exchange_rate",
    "Incoterms": "incoterms",
    "Payment Method": "payment_method",
    "Import Country": "import_country",
    "Mode of Transport": "transport_mode",
    "Country of Origin": "country_of_origin",
    "Customs Br Code": "customs_branch_code",
    "Customs Br Name": "customs_branch_name",
    "bill_id": "bill_id",
    "buyer_country": "buyer_country",
    "customs_branch_code_2": "customs_branch_code_secondary",
    "date": "date",
    "exporter_country": "exporter_country",
    "foreign_currency": "foreign_currency",
    "importer_address_vn": "importer_address_vn",
    "importer_name_en": "importer_name_en",
    "importer_tel": "importer_tel",
    "type_of_import": "import_type",
}

COLUMN_IMP_TYPES = {
    "Declaration No": "int",
    "Transaction Date": "str",
    "HS Code": "int",
    "Product Description": "str",
    "Product Desc(EN)": "str",
    "Supplier": "str",
    "Buyer": "str",
    "quantity": "float64",
    "Quantity unit": "str",
    "Unit Price(USD)": "float64",
    "Unit Price(Currency)": "float64",
    "Total Price(Currency)": "float64",
    "Amount": "float64",
    "Exchange Rate": "float",
    "Incoterms": "str",
    "Payment Method": "str",
    "Import Country": "str",
    "Mode of Transport": "str",
    "Country of Origin": "str",
    "Customs Br Code": "str",
    "Customs Br Name": "str",
    "bill_id": "int",
    "buyer_country": "str",
    "customs_branch_code_2": "str",
    "date": "str",
    "exporter_country": "str",
    "foreign_currency": "str",
    "importer_address_vn": "str",
    "importer_name_en": "str",
    "importer_tel": "str",
    "type_of_import": "str",
}

COLUMN_TYPES = {
    COLUMN_IMP_MAPPING[source_column]: column_type
    for source_column, column_type in COLUMN_IMP_TYPES.items()
}

def mapped_columns() -> list[str]:
    """Return canonical columns in source mapping order."""
    return list(COLUMN_IMP_MAPPING.values())
