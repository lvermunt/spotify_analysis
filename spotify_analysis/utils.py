"""
Module with some utility functions
"""
import os
import pandas as pd


def get_spotify_history(inputdir):
    """
    Loads the .json files containing your spotify streaming history and
    converts them to a single pandas dataframe

    Parameters
    ----------
    inputdir : str
        The path to the input directory where your spotify streaming
        history json files are stored

    Return
    ------
    pandas.Series
        Full spotify streaming history
    """

    # Find the input files
    input_file = []
    for filename in os.listdir(inputdir):
        if filename.endswith(".json") and filename.startswith("Streaming"):
            input_file.append(os.path.join(inputdir, filename))

    # Convert json files to pandas dataframes
    df_array = []
    for ifile in input_file:
        df_array.append(pd.read_json(ifile))

    # Merge into single pandas dataframe
    df = pd.concat(df_array, ignore_index=True)

    return df


def modify_columns_spotify_history(df):
    """
    Modifies some of the default names of the spotify streaming history
    Includes a unique track ID column (consisting out of artist and track)
    Stores the single uri in a separate column

    Parameters
    ----------
    df : pandas.Series
        Pandas dataframe containing the full spotify streaming history as
        loaded by `get_spotify_history(inputdir)`

    Return
    ------
    pandas.Series
        Updated Pandas dataframe with spotify streaming history
    """

    # Remove some prefixes for easier naming
    df.columns = df.columns.str.replace("master_metadata_album_", "")
    df.columns = df.columns.str.replace("master_metadata_", "")

    # Define unique track ID (artist + track)
    df["unique_tr"] = df["artist_name"] + " : " + df["track_name"]

    # Store track_uri without prefix
    df["track_uri"] = df["spotify_track_uri"].str.split(":", expand=True)[2]

    # Remove the non-tracks from history (e.g. podcasts)
    df = df.loc[df["track_uri"].notnull()]

    return df
