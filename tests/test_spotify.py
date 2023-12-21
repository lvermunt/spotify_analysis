"""
Module used to test the Spotify class functionalities
"""

import json
from spotify_analysis.spotify import Spotify
from spotify_analysis.utils import get_spotify_history,     modify_columns_spotify_history


def test_loading_spotify_history():
    """
    Testing the functionalities for loading and modifying of Spotify's history
    """

    df_songs = get_spotify_history('./tests/')
    assert len(df_songs) == 3
    df_songs = modify_columns_spotify_history(df_songs)
    assert len((df_songs.columns)) == 21 + 2


# pylint: disable=consider-using-dict-items
def test_retrieving_spotify_metadata():
    """
    Testing the functionalities for retrieving Spotify's metadata
    """

    spotify_api = Spotify(reference='tracks')
    # TODO: Test API (via both requests and aiohttp with github secrets)

    fname = './tests/Spotify_Response_Sample_Track.json'
    with open(fname, 'r', encoding='utf-8') as f:
        output = json.load(f)
        list_uri = ['2up3OPMp9Tb4dAKM2erWXQ']
        metadata = ['name', 'duration_ms', 'explicit', 'popularity']
        spotify_api.fill_metadata_dictionary(output, list_uri, metadata)
        for key in spotify_api.metadata:
            assert spotify_api.metadata[key]['duration_ms'] == 0

    fname = './tests/Spotify_Response_Sample_Tracks.json'
    with open(fname, 'r', encoding='utf-8') as f:
        output = json.load(f)
        list_uri = ['2up3OPMp9Tb4dAKM2erWXQ_v1', '2up3OPMp9Tb4dAKM2erWXQ_v2']
        metadata = ['name', 'duration_ms', 'explicit', 'popularity']
        spotify_api2 = Spotify(reference='tracks')
        spotify_api2.fill_metadata_dictionary(output, list_uri, metadata)
        assert len(spotify_api2.metadata) == 2

        metadata = [['artists', 'id']]
        spotify_api2.fill_metadata_dictionary(output, list_uri, metadata)
        for key in spotify_api2.metadata:
            assert spotify_api2.metadata[key]['id'] == 'string'
