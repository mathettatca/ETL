# Data Loader

`data_loader` la module noi bo dung de tai file tu cac nguon ben ngoai ve local storage. Package dung `src` layout, da bo layer `controllers` va bo Command/CommandHandler; caller goi truc tiep entrypoint cua package, entrypoint dua `file_source` vao dispatcher de chon downloader phu hop.

## Quy trinh chuan

```text
caller
  -> data_loader.run_data_loader(file_source, dest_path, **params)
  -> DownloaderDispatcher.get_file_info(file_source, **params)
  -> DownloaderDispatcher.download(file, dest_path, **params)
  -> for each DownloadResponse: data_access mediator.send(AuditFileDownloadCommand)
  -> list[dict] JSON-safe
```

Ket qua return la list dict JSON-safe, duoc tao tu `_to_doc()` cua response model noi bo.
Audit file download duoc goi sau khi download xong. Neu mot phan audit fail,
flow van return ket qua download; chi raise khi tat ca audit command deu fail.

## Cau truc hien tai

```text
modules/data_loader/
├── pyproject.toml
├── README.md
├── entrypoints.py              # compatibility wrapper for uv run entrypoints.py
├── google_tokens/              # local credentials/tokens, not packaged
└── src/
    └── data_loader/
        ├── __init__.py
        ├── entrypoints.py
        └── applications/
            ├── models/
            │   └── download_response.py
            └── services/
                └── downloaders/
                    ├── ports/
                    │   └── downloader.py
                    └── adapters/
                        ├── file_dispatcher.py
                        └── google_drive_downloader.py
```

## Layer responsibilities

| Layer | Trach nhiem |
|-------|-------------|
| `src/data_loader/entrypoints.py` | Nhan tham so tu caller, parse `file_source`, goi dispatcher, return JSON-safe dict. |
| `src/data_loader/applications/models` | DTO noi bo cho ket qua download. |
| `src/data_loader/applications/services/downloaders/ports` | Contract `Downloader` cho moi source downloader. |
| `src/data_loader/applications/services/downloaders/adapters` | Dispatcher registry va downloader implementation cu the. |
| `building_block` | Shared domain model, enum, setting, logging, Google Drive service va file service. |

## Entry point

```python
from data_loader import run_data_loader

results = run_data_loader(
    file_source="google_drive",
    dest_path="downloads/google_drive",
    file_id="1da6amH_Hd9oj1elZaWcc9Ptfah1JiA42",
)
```

Vi du return:

```python
[
    {
        "id": "1da6amH_Hd9oj1elZaWcc9Ptfah1JiA42",
        "file_id": "1da6amH_Hd9oj1elZaWcc9Ptfah1JiA42",
        "local_path": "downloads/google_drive/data.csv",
        "file_download_status": "success",
    }
]
```

## Them source moi

1. Tao downloader moi implement contract `Downloader`.
2. Implement `get_file_info(...)` de lay metadata va build `FileModel` phu hop.
3. Implement `download(file, dest_path, **kwargs)` de tai file va tra list response model.
4. Register downloader moi trong `DownloaderDispatcher.regist_all()`.
5. Caller truyen `file_source` va params cua source moi vao `run_data_loader(...)`.

## Init package

`data_loader` dung `src` layout. Chay script tu repo root neu can init package tu dau:

```bash
bash scripts/init_data_loader.sh
```

Khi chay/test import-only:

```bash
cd modules/data_loader
uv run python -c 'from data_loader import run_data_loader; print(run_data_loader.__name__)'
```

## Environment variables

Google Drive va Mongo flow can cac bien moi truong do `building_block` doc. Chi liet ke ten bien, khong commit gia tri that:

```env
MONGO_HOST=
MONGO_PORT=
MONGO_USERNAME=
MONGO_PASSWORD=
MONGO_DATABASE=
GOOGLE_CREDENTIALS=
GOOGLE_TOKEN=
GOOGLE_DRIVE_FOLDER_ID=
```
