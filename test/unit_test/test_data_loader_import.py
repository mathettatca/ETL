from data_loader import run_data_loader


def test_data_loader_public_import_exports_run_data_loader():
    assert run_data_loader.__name__ == "run_data_loader"
