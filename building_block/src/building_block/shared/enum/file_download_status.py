from enum import Enum


class FileDownloadStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    SUCCESS = "success"
    FAILED = "failed"
    UPDATE = "update"
