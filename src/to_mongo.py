from pymongo.mongo_client import MongoClient
import os
import pandas as pd
from pathlib import Path
from beats import Beats
from datetime import date
import pymongo
import streamlit as st

folder_dir = f"{Path(__file__).parents[0]}\\data\\"


class ToMongo:
    def __init__(self):
        # initialize an instance of our inherited class
        self.__mongo_url = st.secrets["MONGOURL"]
        # connect to Mongo
        self.client = MongoClient(self.__mongo_url)
        # create/connect to database
        self.db = self.client.db
        # create/connect to collection
        self.songs = self.db.songs
        self.get_oldest_date()
        self.update_stats()

    def get_oldest_date(self):
        self.oldest_date = (
            self.songs.find()
            .sort("last_fetched", pymongo.ASCENDING)
            .limit(1)[0]["last_fetched"]
        )

    def upload_one_by_one(self, df):
        """
        uploads all items in dataframe to mongoDB one by one
        this method will take longer, but will ensure all our data is correctly uploaded
        """
        df.reset_index(inplace=True)
        as_dict = df.to_dict(orient="records")
        for d in as_dict:
            map_id = d["bs_map_id"]
            existing = self.songs.find_one({"bs_map_id": map_id})
            if existing is None:
                self.songs.insert_one(d)
            else:
                self.songs.update_one(d)
        self.update_stats()

    def upload_collection(self):
        """
        uploads an entire collection of documents to mongoDB
        max upload size is 16777216 bytes
        """
        pass

    def update_stats(self, qty=5):
        """
        uses the oldest fetch-date in the db and updates beatsaver map ratings of some of those oldest records.
        """
        bs = Beats()
        try:
            for i in range(qty):
                id_to_update = self.songs.find_one({"last_fetched": self.oldest_date})[
                    "bs_map_id"
                ]
                map_stats = bs.get_stats(id_to_update)
                self.songs.update_one(
                    {"bs_map_id": id_to_update},
                    {
                        "$set": {
                            "upvotes": map_stats[0],
                            "downvotes": map_stats[1],
                            "score": map_stats[2],
                            "last_fetched": str(date.today()),
                        }
                    },
                )
        except:
            self.get_oldest_date()


if __name__ == "__main__":
    c = ToMongo()
    c.update_stats(10)
