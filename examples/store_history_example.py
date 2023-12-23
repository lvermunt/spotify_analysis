"""
Example to store your spotify streaming history in .csv files. Additionally,
metadata corresponding to your tracks/artists is accessed
"""

import sys
import os
import argparse
import logging
import pandas as pd
from spotify_analysis.spotify import Spotify
from spotify_analysis.utils import get_spotify_history, modify_columns_spotify_history


def main():
    """
    Main function to store the spotify streaming history in corresponding .csv files
    """

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Analyse spotify input")
    parser.add_argument("input", type=str, help="Directory with input files")
    parser.add_argument("output", type=str, help="Directory to store output files")
    args = parser.parse_args()

    df_songs = get_spotify_history(args.input)
    df_songs = modify_columns_spotify_history(df_songs)

    # Print some first output to see if everything works properly
    logging.info("\nTop 20 most listened songs:")
    logging.info(df_songs["unique_tr"].value_counts().head(n=20))

    logging.info("\nTop 20 most listened artists:")
    logging.info(df_songs["artist_name"].value_counts().head(n=20))
    # Store this number-of-listens/artists in dataframe
    df_songs["c_unique_tr"] = df_songs.groupby("unique_tr")["unique_tr"].transform(
        "count"
    )
    df_songs["c_unique_ar"] = df_songs.groupby("artist_name")["artist_name"].transform(
        "count"
    )
    # And sort dataframe by most listened songs
    df_songs = df_songs.sort_values(by=["c_unique_tr"], ascending=False)

    # Save dataframe in .csv file
    df_songs.to_csv(os.path.join(args.output, "MySpotifyDataTable.csv"))

    # Setup class to extract metadata for tracks
    spotify_api_track = Spotify(reference="tracks")
    spotify_api_track.get_spotify_credentials(
        os.path.join(args.input, "spotify_secret.yaml")
    )
    spotify_api_track.get_spotify_access_token()

    # Setup class to extract artist uri from tracks metadata
    spotify_api_track2 = Spotify(reference="tracks")
    spotify_api_track2.cred = spotify_api_track.cred
    spotify_api_track2.access_token = spotify_api_track.access_token
    spotify_api_track2.headers = spotify_api_track.headers

    # Setup class to extract metadata for artist
    spotify_api_artist = Spotify(reference="artists")
    spotify_api_artist.cred = spotify_api_track.cred
    spotify_api_artist.access_token = spotify_api_track.access_token
    spotify_api_artist.headers = spotify_api_track.headers

    # Get metadata of listened songs (total is 19.9k songs)
    uri_list = df_songs.drop_duplicates("unique_tr")["track_uri"].to_list()
    metadata = ["name", "duration_ms", "explicit", "popularity"]
    spotify_api_track.access_spotify_api(uri_list, metadata, 50)

    # Convert dictionary into dataframe with track_uri as the first column
    df_meta_track = pd.DataFrame.from_dict(spotify_api_track.metadata, orient="index")
    df_meta_track.insert(0, "track_uri", df_meta_track.index)
    df_meta_track.reset_index(inplace=True, drop=True)

    # Save dataframe in .csv file
    df_meta_track.to_csv(os.path.join(args.output, "TrackMetadataTable.csv"))

    # Get artist uri listened artists (total is 7.3k artists)
    df_songs = df_songs.sort_values(by=["c_unique_ar"], ascending=False)
    uri_list = df_songs.drop_duplicates("artist_name")["track_uri"].to_list()
    metadata = [["artists", "id"]]
    spotify_api_track2.access_spotify_api(uri_list, metadata, 50)

    # Get metadata of listened artists (total is 7.3k artists)
    uri_list = []
    for meta_ar in spotify_api_track2.metadata.values():
        uri_list.append(meta_ar["id"])
    metadata = ["name", "genres", "popularity", "followers"]
    spotify_api_artist.access_spotify_api(uri_list, metadata, 50)

    # Convert dictionary into dataframe with artist_uri as the first column
    df_meta_artist = pd.DataFrame.from_dict(spotify_api_artist.metadata, orient="index")
    df_meta_artist.insert(0, "artist_uri", df_meta_artist.index)
    df_meta_artist.reset_index(inplace=True, drop=True)

    # Save dataframe in .csv file
    df_meta_artist.to_csv(os.path.join(args.output, "ArtistMetadataTable.csv"))
    df_meta_artist = df_meta_artist.explode("genres")
    df_meta_artist.to_csv(
        os.path.join(args.output, "ArtistMetadataTable_GenresExpanded.csv")
    )


if __name__ == "__main__":
    sys.exit(main())
