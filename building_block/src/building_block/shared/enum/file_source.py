from enum import Enum


class FileSource(str, Enum):
    """Enumeration of available file sources."""

    GOOGLE_DRIVE = "google_drive"
    S3 = "s3"
    API = "api"
