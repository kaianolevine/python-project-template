import pytest
from unittest.mock import patch, MagicMock
from your_package.westie_radio import spotify

TEST_URI = "spotify:track:123"
TEST_URIS = [TEST_URI]
TEST_PLAYLIST_ID = "test-playlist-id"


# --- Test get_spotify_client_from_refresh ---


@patch("your_package.westie_radio.spotify.SpotifyOAuth")
@patch("your_package.westie_radio.spotify.config")
def test_get_spotify_client_from_refresh(mock_config, mock_spotify_oauth):
    mock_config.SPOTIFY_CLIENT_ID = "id"
    mock_config.SPOTIFY_CLIENT_SECRET = "secret"
    mock_config.SPOTIFY_REDIRECT_URI = "http://localhost"
    mock_config.SPOTIFY_REFRESH_TOKEN = "refresh_token"

    mock_auth = MagicMock()
    mock_auth.refresh_access_token.return_value = {"access_token": "new_token"}
    mock_spotify_oauth.return_value = mock_auth

    client = spotify.get_spotify_client_from_refresh()
    assert client is not None


@patch("your_package.westie_radio.spotify.config")
def test_get_spotify_client_missing_env_vars(mock_config):
    mock_config.SPOTIFY_CLIENT_ID = None
    mock_config.SPOTIFY_CLIENT_SECRET = None
    mock_config.SPOTIFY_REDIRECT_URI = None
    mock_config.SPOTIFY_REFRESH_TOKEN = None

    with pytest.raises(ValueError):
        spotify.get_spotify_client_from_refresh()


# --- Test search_track ---


@patch("your_package.westie_radio.spotify.get_spotify_client_from_refresh")
def test_search_track_found(mock_get_client):
    mock_sp = MagicMock()
    mock_get_client.return_value = mock_sp
    mock_sp.search.return_value = {"tracks": {"items": [{"uri": TEST_URI}]}}

    result = spotify.search_track("Artist", "Title")
    assert result == TEST_URI


@patch("your_package.westie_radio.spotify.get_spotify_client_from_refresh")
def test_search_track_not_found(mock_get_client):
    mock_sp = MagicMock()
    mock_get_client.return_value = mock_sp
    mock_sp.search.return_value = {"tracks": {"items": []}}

    result = spotify.search_track("Artist", "Missing")
    assert result is None


# --- Test add_tracks_to_playlist ---


@patch("your_package.westie_radio.spotify.get_spotify_client_from_refresh")
@patch("your_package.westie_radio.spotify.config")
def test_add_tracks_to_playlist(mock_config, mock_get_client):
    mock_config.SPOTIFY_PLAYLIST_ID = TEST_PLAYLIST_ID
    mock_sp = MagicMock()
    mock_get_client.return_value = mock_sp

    spotify.add_tracks_to_playlist(TEST_URIS)
    mock_sp.playlist_add_items.assert_called_once_with(TEST_PLAYLIST_ID, TEST_URIS)


@patch("your_package.westie_radio.spotify.config")
def test_add_tracks_to_playlist_missing_env(mock_config):
    mock_config.SPOTIFY_PLAYLIST_ID = None

    with pytest.raises(EnvironmentError):
        spotify.add_tracks_to_playlist(TEST_URIS)


@patch("your_package.westie_radio.spotify.get_spotify_client_from_refresh")
@patch("your_package.westie_radio.spotify.config")
def test_add_tracks_to_playlist_empty_uris(mock_config, mock_get_client):
    mock_config.SPOTIFY_PLAYLIST_ID = TEST_PLAYLIST_ID
    spotify.add_tracks_to_playlist([])  # Should not raise or call anything


# --- Test trim_playlist_to_limit ---


@patch("your_package.westie_radio.spotify.get_spotify_client_from_refresh")
@patch("your_package.westie_radio.spotify.config")
def test_trim_playlist_no_removal(mock_config, mock_get_client):
    mock_config.SPOTIFY_PLAYLIST_ID = TEST_PLAYLIST_ID
    mock_sp = MagicMock()
    mock_get_client.return_value = mock_sp
    mock_sp.playlist_items.return_value = {"total": 150, "items": []}

    spotify.trim_playlist_to_limit(limit=200)
    mock_sp.playlist_remove_all_occurrences_of_items.assert_not_called()


@patch("your_package.westie_radio.spotify.get_spotify_client_from_refresh")
@patch("your_package.westie_radio.spotify.config")
def test_trim_playlist_removal(mock_config, mock_get_client):
    mock_config.SPOTIFY_PLAYLIST_ID = TEST_PLAYLIST_ID
    mock_sp = MagicMock()
    mock_get_client.return_value = mock_sp

    # Simulate 3 items, need to remove 1
    mock_sp.playlist_items.return_value = {
        "total": 3,
        "items": [
            {"track": {"uri": "spotify:track:1"}},
            {"track": {"uri": "spotify:track:2"}},
            {"track": {"uri": "spotify:track:3"}},
        ],
    }

    spotify.trim_playlist_to_limit(limit=2)
    mock_sp.playlist_remove_all_occurrences_of_items.assert_called_once_with(
        TEST_PLAYLIST_ID, ["spotify:track:1"]
    )


@patch("your_package.westie_radio.spotify.config")
def test_trim_playlist_missing_env(mock_config):
    mock_config.SPOTIFY_PLAYLIST_ID = None
    with pytest.raises(EnvironmentError):
        spotify.trim_playlist_to_limit()
