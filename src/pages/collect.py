import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from spotpull import SpotPull
from to_mongo import ToMongo

st.title("Collect Some Songs")
st.text("Enter a date to check 50 random songs posted on that date")
st.text("Empty or invalid dates will return the most recent 50 songs")

st.header("Please use YYYY-MM-DD format")
st.text("results may take 60 seconds to appear")
date = st.text_input("Enter date here")
if st.button("Get Songs"):
    s = SpotPull(date)
    s.lookit_me = s.bs_data[s.bs_data["match_conclusion"]]
    st.dataframe(
        s.lookit_me[
            [
                "title",
                "artist",
                "mapper_name",
                "difficulties",
                "bs_map_link",
                "spotify_link",
            ]
        ]
    )
    st.subheader("What's next?")
    s.local_save()
    st.text("Local CSV ready! - Go to the Analyze page to see stats on these songs")
    tm = ToMongo()
    tm.update_stats()
    tm.upload_one_by_one(s.bs_data)
    st.text(
        "Mongo upload done! - These songs will be incorporated in Stats - All Time and Query results"
    )
    tm.client.close()
    st.text
