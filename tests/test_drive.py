import pytest
from unittest.mock import patch, MagicMock, mock_open
from your_package.westie_radio import drive

TEST_FOLDER_ID = "test-folder-id"
TEST_FILE_ID = "test-file-id"
TEST_FILE_NAME = "2025-06-11.m3u"
TEST_DEST_PATH = "/tmp/test.m3u"


@patch("your_package.westie_radio.drive.get_drive_service")
def test_find_latest_m3u_file_found(mock_get_drive_service):
    mock_service = MagicMock()
    mock_get_drive_service.return_value = mock_service

    mock_files = [
        {"id": "1", "name": "2025-06-11.m3u", "modifiedTime": "2025-06-11T12:00:00Z"},
        {"id": "2", "name": "2025-06-10.m3u", "modifiedTime": "2025-06-10T12:00:00Z"},
    ]
    mock_list = mock_service.files.return_value.list
    mock_list.return_value.execute.return_value = {"files": mock_files}

    result = drive.find_latest_m3u_file(TEST_FOLDER_ID)

    assert result["id"] == "1"
    assert result["name"] == "2025-06-11.m3u"


@patch("your_package.westie_radio.drive.get_drive_service")
def test_find_latest_m3u_file_not_found(mock_get_drive_service):
    mock_service = MagicMock()
    mock_get_drive_service.return_value = mock_service

    mock_list = mock_service.files.return_value.list
    mock_list.return_value.execute.return_value = {"files": []}

    result = drive.find_latest_m3u_file(TEST_FOLDER_ID)
    assert result is None


@patch("your_package.westie_radio.drive.get_drive_service")
def test_list_files_in_folder_no_filter(mock_get_drive_service):
    mock_service = MagicMock()
    mock_get_drive_service.return_value = mock_service

    mock_files = [{"id": "1", "name": "file1"}, {"id": "2", "name": "file2"}]
    mock_list = mock_service.files.return_value.list
    mock_list.return_value.execute.return_value = {"files": mock_files}

    results = drive.list_files_in_folder(TEST_FOLDER_ID)
    assert len(results) == 2
    assert results[0]["name"] == "file1"


@patch("your_package.westie_radio.drive.get_drive_service")
def test_list_files_in_folder_with_filter(mock_get_drive_service):
    mock_service = MagicMock()
    mock_get_drive_service.return_value = mock_service

    mock_files = [{"id": "1", "name": "filtered_file"}]
    mock_list = mock_service.files.return_value.list
    mock_list.return_value.execute.return_value = {"files": mock_files}

    results = drive.list_files_in_folder(TEST_FOLDER_ID, mime_type_filter="audio/mpeg")
    assert len(results) == 1
    assert results[0]["name"] == "filtered_file"


@patch("your_package.westie_radio.drive.get_drive_service")
@patch("your_package.westie_radio.drive.io.FileIO", new_callable=mock_open)
def test_download_file_success(mock_file_io, mock_get_drive_service):
    mock_service = MagicMock()
    mock_get_drive_service.return_value = mock_service
    mock_request = MagicMock()
    mock_service.files.return_value.get_media.return_value = mock_request

    mock_downloader = MagicMock()
    mock_downloader.next_chunk.side_effect = [
        (MagicMock(progress=lambda: 0.5), False),
        (MagicMock(progress=lambda: 1.0), True),
    ]

    with patch(
        "your_package.westie_radio.drive.MediaIoBaseDownload",
        return_value=mock_downloader,
    ):
        drive.download_file(TEST_FILE_ID, TEST_DEST_PATH)

    mock_file_io.assert_called_with(TEST_DEST_PATH, "wb")
    mock_downloader.next_chunk.assert_called()


@patch("your_package.westie_radio.drive.get_drive_service")
@patch("your_package.westie_radio.drive.io.FileIO", side_effect=IOError("disk error"))
def test_download_file_io_error(mock_file_io, mock_get_drive_service):
    with pytest.raises(IOError):
        drive.download_file(TEST_FILE_ID, TEST_DEST_PATH)


@patch("your_package.westie_radio.drive.get_drive_service")
@patch("your_package.westie_radio.drive.io.FileIO", new_callable=mock_open)
def test_download_file_download_error(mock_file_io, mock_get_drive_service):
    mock_service = MagicMock()
    mock_get_drive_service.return_value = mock_service
    mock_request = MagicMock()
    mock_service.files.return_value.get_media.return_value = mock_request

    mock_downloader = MagicMock()
    mock_downloader.next_chunk.side_effect = Exception("Download failed")

    with patch(
        "your_package.westie_radio.drive.MediaIoBaseDownload",
        return_value=mock_downloader,
    ), pytest.raises(Exception, match="Download failed"):
        drive.download_file(TEST_FILE_ID, TEST_DEST_PATH)
