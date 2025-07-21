from unittest.mock import MagicMock, patch
from your_package.westie_radio import sheets

SPREADSHEET_ID = "test-spreadsheet-id"


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_get_or_create_sheet_creates_when_missing(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    spreadsheet = {"sheets": [{"properties": {"title": "OtherSheet"}}]}
    service.spreadsheets().get().execute.return_value = spreadsheet

    sheets.get_or_create_sheet(SPREADSHEET_ID, "NewSheet")

    service.spreadsheets().batchUpdate.assert_called_once()


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_get_or_create_sheet_skips_if_exists(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    spreadsheet = {"sheets": [{"properties": {"title": "ExistingSheet"}}]}
    service.spreadsheets().get().execute.return_value = spreadsheet

    sheets.get_or_create_sheet(SPREADSHEET_ID, "ExistingSheet")

    service.spreadsheets().batchUpdate.assert_not_called()


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_ensure_sheet_exists_adds_headers(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service

    # Simulate no sheets exist yet
    service.spreadsheets().get().execute.return_value = {"sheets": []}

    # Simulate successful batchUpdate call for sheet creation
    service.spreadsheets().batchUpdate().execute.return_value = {}

    # Simulate update call for writing headers
    service.spreadsheets().values().update().execute.return_value = {}

    # Run the function
    sheets.ensure_sheet_exists(SPREADSHEET_ID, "TestSheet", headers=["Col1", "Col2"])

    # Verify both batchUpdate and header update are called
    service.spreadsheets().batchUpdate.assert_called()
    service.spreadsheets().values().update.assert_called_once()


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_append_rows(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service

    sheets.append_rows(SPREADSHEET_ID, "Sheet1!A1", [["one", "two"]])

    service.spreadsheets().values().append.assert_called_once()


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_write_sheet(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service

    sheets.write_sheet(SPREADSHEET_ID, "Sheet1!A1", [["x", "y"]])

    service.spreadsheets().values().update.assert_called_once()


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_read_sheet(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    service.spreadsheets().values().get().execute.return_value = {
        "values": [["A", "B"]]
    }

    result = sheets.read_sheet(SPREADSHEET_ID, "Sheet1!A1:B1")

    assert result == [["A", "B"]]


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_get_latest_processed_returns_latest(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    values = [["file1", "2024-01-01", "1234", "Title", "Artist"]]
    service.spreadsheets().values().get().execute.return_value = {"values": values}

    result = sheets.get_latest_processed(SPREADSHEET_ID)
    assert result == values[-1]


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_get_latest_processed_returns_none(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    service.spreadsheets().values().get().execute.return_value = {}

    result = sheets.get_latest_processed(SPREADSHEET_ID)
    assert result is None


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_log_processed_full(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service

    sheets.log_processed_full(
        SPREADSHEET_ID, "file.m3u", "2024-01-01T10:00", "5678", "Title", "Artist"
    )

    service.spreadsheets().values().append.assert_called_once()


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_get_sheet_metadata(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service
    metadata = {"sheets": [{"properties": {"title": "TestSheet"}}]}
    service.spreadsheets().get().execute.return_value = metadata

    result = sheets.get_sheet_metadata(SPREADSHEET_ID)
    assert result == metadata


@patch("your_package.westie_radio.sheets.get_sheets_service")
def test_delete_sheet_by_id(mock_get_service):
    service = MagicMock()
    mock_get_service.return_value = service

    sheets.delete_sheet_by_id(SPREADSHEET_ID, 123456)

    service.spreadsheets().batchUpdate.assert_called_once()
