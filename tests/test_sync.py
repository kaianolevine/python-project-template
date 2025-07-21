from unittest.mock import patch, MagicMock, ANY
from your_package.westie_radio import sync


@patch("your_package.westie_radio.sync.parse_m3u")
@patch("your_package.westie_radio.sync.initialize_spreadsheet")
@patch("your_package.westie_radio.sync.sheets")
@patch("your_package.westie_radio.sync.spotify")
@patch("your_package.westie_radio.sync.drive")
def test_main_flow(
    mock_drive, mock_spotify, mock_sheets, mock_initialize_spreadsheet, mock_parse_m3u
):
    mock_initialize_spreadsheet.return_value = None
    mock_sheets.initialize_spreadsheet = MagicMock()

    # Setup mock for list_files_in_folder
    mock_drive.list_files_in_folder.return_value = [
        {"name": "2025-06-11.m3u", "id": "file123"},
    ]

    # Mock loaded m3u data
    mock_parse_m3u.return_value = [("Misterwives", "Superbloom", "<EXTVDJ_LINE>")]

    # Mock search results
    mock_spotify.search_track.side_effect = lambda artist, title: {
        "id": f"track_{artist}_{title}" if artist and title else None
    }

    # Mock processed sheet contents
    mock_sheets.read_sheet.return_value = []

    # Run sync
    sync.main()

    # Ensure expected methods were called
    mock_initialize_spreadsheet.assert_called()
    mock_drive.list_files_in_folder.assert_called()
    mock_parse_m3u.assert_called()


@patch("your_package.westie_radio.sync.sheets")
def test_initialize_spreadsheet(mock_sheets):
    mock_sheets.get_sheet_metadata.return_value = {
        "sheets": [{"properties": {"title": "Sheet1", "sheetId": 0}}]
    }

    spreadsheet_id = "spreadsheet_test_id"
    sync.spreadsheet_id = spreadsheet_id

    sync.initialize_spreadsheet()

    mock_sheets.delete_sheet_by_id.assert_called_with(spreadsheet_id, 0)
    mock_sheets.ensure_sheet_exists.assert_any_call(
        spreadsheet_id, "Processed", headers=ANY
    )
    mock_sheets.ensure_sheet_exists.assert_any_call(
        spreadsheet_id, "Songs Added", headers=ANY
    )
    mock_sheets.ensure_sheet_exists.assert_any_call(
        spreadsheet_id, "Songs Not Found", headers=ANY
    )
