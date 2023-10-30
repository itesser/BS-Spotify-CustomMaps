from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

folder_dir = f"{Path(__file__).parents[0]}\\data\\"

class ToMongo():

    def __init__(self):
        # initialize an instance of our inherited class
        load_dotenv()
        self.__mongo_url = os.getenv("MONGOURL")
        # connect to Mongo
        self.client = MongoClient(self.__mongo_url)
        # create/connect to database
        self.db = self.client.db
        # create/connect to collection
        self.songs = self.db.songs


    def upload_one_by_one(self, df):
        """
        uploads all items in dataframe to mongoDB one by one
        this method will take longer, but will ensure all our data is correctly uploaded
        """
        df.reset_index(inplace=True)
        as_dict = df.to_dict(orient ='records')
        for d in as_dict:
            map_id = d['bs_map_id']
            existing = self.songs.find_one({'bs_map_id':map_id})
            if existing is None:
                self.songs.insert_one(d)

    def upload_collection(self):
        """
        uploads an entire collection of documents to mongoDB
        max upload size is 16777216 bytes
        """
        self.cards.insert_many(self.df.to_dict())

    def drop_collection(self, coll_name: str = "cards"):
        self.db.drop_collection(coll_name)



if __name__ == '__main__':
    local_data = pd.read_csv(f'{folder_dir}clean_songs.csv')
    c = ToMongo()
    c.upload_one_by_one(local_data)