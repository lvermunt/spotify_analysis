"""
Module used to test the Spotify class functionalities
"""

import json
from spotify_analysis.spotify import Spotify
from spotify_analysis.utils import get_spotify_history, modify_columns_spotify_history

df_songs = get_spotify_history('./')
df_songs = modify_columns_spotify_history(df_songs)

spotify_api = Spotify(reference='tracks')

# TODO: Test API (via both requests and aiohttp with github secrets)

with open('./Spotify_Response_Sample_Track.json', 'r', encoding='utf-8') as f:
    output = json.load(f)
    list_uri = ['2up3OPMp9Tb4dAKM2erWXQ']
    metadata = ['name', 'duration_ms', 'explicit', 'popularity']
    spotify_api.fill_metadata_dictionary(output, list_uri, metadata)

with open('./Spotify_Response_Sample_Tracks.json', 'r', encoding='utf-8') as f:
    output = json.load(f)
    list_uri = ['2up3OPMp9Tb4dAKM2erWXQ_v1', '2up3OPMp9Tb4dAKM2erWXQ_v2']
    metadata = ['name', 'duration_ms', 'explicit', 'popularity']
    spotify_api2 = Spotify(reference='tracks')
    spotify_api2.fill_metadata_dictionary(output, list_uri, metadata)

    metadata = [['artists', 'id']]
    spotify_api2.fill_metadata_dictionary(output, list_uri, metadata)