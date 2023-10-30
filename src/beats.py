import requests
import pandas as pd
import re
from pathlib import Path

folder_dir = f"{Path(__file__).parents[0]}\\data\\"

class Beats:
    '''
    This class handles pulling data from the Beat Saver API.

    INPUT:
    Date (Optional)
    -- No date/incorrect format: Most recent 50 songs.
    -- Date on/after 2019-01-01: last 50 songs posted on that date (*time flexibility not currently implemented*)
    -- Date before 2019-01-01: last 50 songs posted BEFORE 11:59pm on that date (*Beat Saver data goes back to 2018-05-09*)
    
    ATTRIBUTES:
    df = Pandas Dataframe (50 rows, 10 columns)

    METHODS:
    none

    OUTPUT:
    CSV file of dataframe, stored in data subdirectory
    '''
    def __init__(self, date=''):
        ready_date = self.check_date(date)
        url_start = 'https://api.beatsaver.com/maps/latest?' 
        url_end = 'pageSize=50'
        self.full_url = f'{url_start}{ready_date}{url_end}'
        self.response = requests.get(self.full_url).json()
        self.df = self.org_data(self.response)
        self.df.to_csv(f'{folder_dir}beatsaver_songs.csv') 

    def org_data(self, json_obj):
        bs_songs = []
        for i in range(len(json_obj['docs'])):
            song = {}
            song['bs_map_id'] = json_obj['docs'][i]['id']
            song['title'] = json_obj['docs'][i]['metadata']['songName']
            song['artist'] = json_obj['docs'][i]['metadata']['songAuthorName']
            song['mapper_name'] = json_obj['docs'][i]['uploader']['name']
            song['mapper_id'] = json_obj['docs'][i]['uploader']['id']
            song['duration_seconds'] = json_obj['docs'][i]['metadata']['duration']
            song['auto_mapped'] = json_obj['docs'][i]['automapper']
            song['upload_date'] = json_obj['docs'][i]['lastPublishedAt']
            try: 
                song['tags'] = json_obj['docs'][i]['tags']
            except:
                song['tags'] = ['none']
            song['difficulties'] = [json_obj['docs'][i]['versions'][0]['diffs'][x]['difficulty'] for x in range(len(json_obj['docs'][i]['versions'][0]['diffs']))]
            bs_songs.append(song)
        return pd.DataFrame(bs_songs)


    def check_date(self, date):
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        if re.match(date_pattern, date):
            if int(date[:4]) < 2019:
                return f'after={date}T00%3A00%3A36.874Z&'
            else:
                return f'before={date}T23%3A59%3A36.874Z&'
        else:
            return ''



if __name__ == '__main__':
    query_date = input('enter YYYY-MM-DD for a specific date. improper date formats will show most recent songs') ## This will turn into a button on streamlit
    b = Beats(query_date)
    print(b.df.head())
    print(b.df.shape)