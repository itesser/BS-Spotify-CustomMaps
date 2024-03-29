import requests
import pandas as pd
import re
from pathlib import Path
from random import randint
from datetime import date

folder_dir = f"{Path(__file__).parents[0]}/data/"


class Beats:
    """
    This class handles pulling data from the Beat Saver API.

    INPUT:
    Date (Optional)
    -- No date/incorrect format: Most recent 50 songs.
    -- Date on/after 2019-01-01: 50 songs posted at a random time on that date (hours/minutes each generated by rand int)
    -- Date before 2019-01-01: 50 songs posted at a random time on that date (hours/minutes each generated by rand int)
    ----- Beat Saver data goes back to 2018-05-09, so dates before then will just show the first 50 songs podsted.

    ATTRIBUTES:
    df = Pandas Dataframe (50 rows, 10 columns)

    METHODS:
    none

    OUTPUT:
    CSV file of dataframe, stored in data subdirectory
    """

    def __init__(self, date="", time_h=-1, time_m=-1):
        ready_date = self.check_date(date, time_h, time_m)
        url_start = "https://api.beatsaver.com/maps/latest?"
        url_end = "pageSize=50"
        self.full_url = f"{url_start}{ready_date}{url_end}"
        # print(self.full_url)
        error_chec = requests.get(self.full_url)
        self.response = error_chec.json()
        self.df = self.org_data(self.response)
        print(error_chec)
        self.df.to_csv(f"{folder_dir}beatsaver_songs.csv")

    def org_data(self, json_obj):
        bs_map_list = json_obj["docs"]
        bs_songs = []
        for i in range(len(bs_map_list)):
            song = {}
            song["bs_map_id"] = bs_map_list[i]["id"]
            song["title"] = bs_map_list[i]["metadata"]["songName"]
            if len(bs_map_list[i]["metadata"]["songAuthorName"]) > 1:
                song["artist"] = bs_map_list[i]["metadata"]["songAuthorName"]
            else:
                song["artist"] = "__No Artist Listed"
            song["mapper_name"] = bs_map_list[i]["uploader"]["name"]
            song["mapper_id"] = bs_map_list[i]["uploader"]["id"]
            song["duration_seconds"] = bs_map_list[i]["metadata"]["duration"]
            song["auto_mapped"] = bs_map_list[i]["automapper"]
            song["upload_date"] = bs_map_list[i]["lastPublishedAt"]
            song["upvotes"] = int(bs_map_list[i]["stats"]["upvotes"])
            song["downvotes"] = int(bs_map_list[i]["stats"]["downvotes"])
            song["score"] = float(bs_map_list[i]["stats"]["score"])
            try:
                song["tags"] = json_obj["docs"][i]["tags"]
            except:
                song["tags"] = ["none"]
            song["difficulties"] = [
                json_obj["docs"][i]["versions"][0]["diffs"][x]["difficulty"]
                for x in range(len(json_obj["docs"][i]["versions"][0]["diffs"]))
            ]
            song["last_fetched"] = str(date.today())
            bs_songs.append(song)
        return pd.DataFrame(bs_songs)

    def get_stats(self, map_id):
        bs_map_url = "https://api.beatsaver.com/maps/id/"
        response = requests.get(f"{bs_map_url}{map_id}").json()
        up = response["stats"]["upvotes"]
        down = response["stats"]["downvotes"]
        score = response["stats"]["score"]
        return [up, down, score]

    def check_date(self, date, hr=25, mn=99):
        if hr >= 0:
            hour = hr
        else:
            hour = randint(0, 23)
        hour = str(hour)
        if len(hour) == 1:
            hour = "0" + hour
        if mn >= 0:
            minute = mn
        else:
            minute = randint(0, 59)
        minute = str(minute)
        if len(minute) == 1:
            minute = "0" + minute
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        if re.match(date_pattern, date):
            if int(date[:4]) < 2019:
                return f"after={date}T{hour}%3A{minute}%3A36.874Z&"
            else:
                return f"before={date}T{hour}%3A{minute}%3A36.874Z&"
        else:
            return ""


if __name__ == "__main__":
    query_date = input(
        "enter YYYY-MM-DD for a specific date. improper date formats will show most recent songs"
    )  ## This will turn into a button on streamlit
    b = Beats(query_date)
    print(b.df.head())
    print(b.df.shape)
