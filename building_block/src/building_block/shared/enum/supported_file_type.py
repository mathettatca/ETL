from enum import Enum


class SupportedFileType(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
