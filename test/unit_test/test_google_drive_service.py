import pytest

from building_block.shared.services.google_drive_service import GoogleDriveService


def setup_function():
    GoogleDriveService.reset()


def test_google_drive_service_requires_stage_client():
    with pytest.raises(RuntimeError, match="stage client is required"):
        GoogleDriveService()


def test_google_drive_service_wraps_initialized_stage_client():
    drive_client = object()

    service = GoogleDriveService(service=drive_client)

    assert service.service is drive_client
    assert GoogleDriveService().service is drive_client


def test_google_drive_service_can_update_stage_client():
    first_client = object()
    second_client = object()

    service = GoogleDriveService(service=first_client)
    same_singleton = GoogleDriveService(service=second_client)

    assert service is same_singleton
    assert service.service is second_client
