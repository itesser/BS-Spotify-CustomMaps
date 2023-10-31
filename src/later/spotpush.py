import spotipy
import os
import pandas as pd
from pathlib import Path
import streamlit as st

folder_dir = f"{Path(__file__).parents[0]}\\data\\"


class SpotPush:
    def __init__(self):
        # use the argument local_data = True to skip querying BeatSaver
        self.sp = self.spotify_connection()
        self.mega_playlist = "2IAYFqUH5Zj1TmwqvtSIAM"

    def spotify_connection(self):
        spot_id = st.secrets["SPOTCLIENT"]
        spot_key = st.secrets["SPOTSECRET"]
        client_credentials_manager = spotipy.SpotifyClientCredentials(
            client_id=spot_id, client_secret=spot_key
        )
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def add_to_mega(self, sp_id):
        self.sp.playlist_add_items(self.mega_playlist, sp_id, position=0)

    def new_playlist(self):
        self.current_playlist_num()
        recent_data = pd.read_csv(f"{folder_dir}clean_songs.csv")
        working_date = recent_data["upload_date"].iloc[0][:10]
        good_song_ids = recent_data[recent_data["match_conclusion"] == True][
            "spotify_id"
        ]
        self.new_play_id = self.sp.user_playlist_create(
            os.getenv("SPOTMYID"),
            f"BeatSaverList_{self.play_num}",
            description=f"Songs for custom beatsaver maps uploaded {working_date}",
        )

    def current_playlist_num(self):
        with open(f"{folder_dir}playlist_num.txt", "r") as file:
            self.play_num = int(file.read())
            next_num = self.play_num + 1
        with open(f"{folder_dir}playlist_num.txt", "w") as file:
            file.write(str(next_num))


if __name__ == "__main__":
    spu = SpotPush()
    spu.new_playlist()
    print(spu.new_play_id)
