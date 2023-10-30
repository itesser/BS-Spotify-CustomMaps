import spotipy
from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path
from beats import Beats

folder_dir = f"{Path(__file__).parents[0]}\\data\\"

class SpotPull(Beats):

    def __init__(self, date='today', local_data=False):
        # use the argument local_data = True to skip querying BeatSaver
        if not local_data:
            Beats.__init__(self, date)
        self.sp = self.spotify_connection()
        self.bs_data = pd.read_csv(f'{folder_dir}beatsaver_songs.csv')
        self.get_sp_data()
        self.cleanup()

    def spotify_connection(self):
        load_dotenv()
        spot_id = os.getenv("SPOTCLIENT")
        spot_key = os.getenv("SPOTSECRET")
        client_credentials_manager = spotipy.SpotifyClientCredentials(client_id=spot_id, client_secret=spot_key)
        return spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    def get_sp_data(self):
        '''
        This function takes in the beat saver dataframe and acts on each row to add 24 columns of Spotify data.
        
        For each line in the dataframe, the Spotify API is queried 4 times, each with 1 internal function.
        1) get_spot_data: Use Beat Saver Title/Artist to get 1 (one) Spotify Track ID
        - Track ID saved in dataframe

        2) all_spot_track_info: Use track ID to get all track info from Spotify
        - SP Track Title
        - SP Track Artist/Artist ID
        - Album
        - Release Date
        - Duration
        - Popularity

        3) get_spot_audio: Use Track ID to information about the song
        - dancability
        - energy
        - key
        - loudness
        - mode
        - speechiness
        - acousticness
        - instrumentalness
        - liveness
        - valence
        - tempo
        - time_signature

        4) get_artist_info: Use Artist ID (from all_track_info)

        '''
        # Defining Internal Functions
        def get_spot_data(artist, title):
            '''Transforms Beat Saber Artist and Title into a spotify Track ID'''
            spot_search = self.sp.search(f'{artist} {title}')
            return spot_search['tracks']['items'][0]['id']

        def all_spot_track_info(sp_id):
            '''Uses spotify Track ID to get details on that track'''
            return self.sp.track(sp_id)

        def get_spot_audio(sp_id):
            '''Uses spotify track ID to get audio features of that track'''
            return self.sp.audio_features(sp_id)

        def get_artist_info(art_id):
            '''Uses spotify Artist ID (from Track) to get artist data (for genre)'''
            return self.sp.artist(art_id)
        
        # Actually Getting Data. 
        # Throughout, BS map ID will be used as the key to consistently update the same row.
        for i in range(len(self.bs_data)):
#        for i in range(10):
            title = self.bs_data['title'].iloc[i]  # these lines used for spotify search
            artist = self.bs_data['artist'].iloc[i]
            try:    #If the initial Spotify Query has no results, this codeblock is skipped.
                spot_result = get_spot_data(artist, title)
                track_dict = all_spot_track_info(spot_result)
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'spotify_id'] = spot_result
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'sp_title'] = track_dict['name']
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'sp_artist'] = track_dict['artists'][0]['name']
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'sp_artist_id'] = track_dict['artists'][0]['id']
                artist_info = get_artist_info(track_dict['artists'][0]['id'])
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'artist_genres'] = str(artist_info['genres'])
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'album'] = track_dict['album']['name']
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'album_released'] = track_dict['album']['release_date']
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'album_type'] = track_dict['album']['type']
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'sp_duration'] = track_dict['duration_ms']
                track_audio = get_spot_audio(spot_result)
                audio_vars = ['danceability', 'energy', 'key','loudness','mode', 'speechiness','acousticness','instrumentalness', 'liveness','valence','tempo','time_signature']
                for x in audio_vars:
                    self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], f'sp_{x}'] = track_audio[0][x]
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'sp_popularity'] = track_dict['popularity']
                bs_url = 'https://beatsaver.com/maps/'
                spo_url = 'http://open.spotify.com/track/'
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'bs_map_link'] = f"{bs_url}{self.bs_data['bs_map_id'].iloc[i]}"
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'spotify_link'] = f"{spo_url}{spot_result}"
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'artist_match'] = (self.bs_data['artist'].iloc[i].lower().strip() == self.bs_data['sp_artist'].iloc[i].lower().strip()) or ((self.bs_data['artist'].iloc[i].lower().strip() in self.bs_data['sp_artist'].iloc[i].lower().strip())) or (self.bs_data['sp_artist'].iloc[i].lower().strip()) in (self.bs_data['artist'].iloc[i].lower().strip())
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'title_match'] = (self.bs_data['title'].iloc[i].lower().strip() == self.bs_data['sp_title'].iloc[i].lower().strip()) or ((self.bs_data['title'].iloc[i].lower().strip() in self.bs_data['sp_title'].iloc[i].lower().strip())) or (self.bs_data['sp_title'].iloc[i].lower().strip()) in (self.bs_data['title'].iloc[i].lower().strip())
            except:
                self.bs_data.loc[self.bs_data.bs_map_id == self.bs_data.bs_map_id[i], 'spotify_id'] = 'No artist/title results on Spotify'

    def cleanup(self):
        # genres had to be transformed into a string, changing it back into a list
        self.bs_data.drop(columns='Unnamed: 0', inplace=True)
        self.bs_data.set_index('bs_map_id', inplace=True)
        try:
            self.bs_data['artist_genres'] = self.bs_data['artist_genres'].apply(eval)
        except:
            pass
        # comparing duration in seconds (BeatSaver) to duration in miliseconds (Spotify)
        # This is a major factor in determinging if the songs are the same
        self.bs_data['duration_difference'] = abs(self.bs_data['sp_duration']/1000 - self.bs_data['duration_seconds'])
        # Songs are considered the same IF: title and artist match OR duration is within 20 seconds and either title or artist matches.
        self.bs_data['match_conclusion'] = ((self.bs_data[['artist_match','title_match']].all(axis=1)) | 
                                    ((self.bs_data['duration_difference'] < 20) & (self.bs_data[['artist_match', 'title_match']].any(axis=1)))).astype(bool)
    def local_save(self):
        self.bs_data.to_csv(f'{folder_dir}clean_songs.csv')

if __name__ == '__main__':
   s = SpotPull(local_data=True)
   s.local_save()

