import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from spotpull import SpotPull
from to_mongo import ToMongo

st.title("Collect Some Songs")
st.text("enter a date to check the last 50 songs posted on that date")
st.text("empty or invalid dates will return the most recent 50 songs")

st.header("Please use YYYY-MM-DD format")
st.text("results may take 60 seconds to appear")
date = st.text_input("Enter date here")
if st.button("Get Songs"):
    s = SpotPull(date)
    s.lookit_me = s.bs_data[s.bs_data['match_conclusion']]
    st.dataframe(s.lookit_me[['title', 'artist', 'mapper_name', 'difficulties','bs_map_link','spotify_link']])
    st.subheader("What's next?")
    s.local_save()
    st.text('local csv ready!')
    tm = ToMongo()
    tm.upload_one_by_one(s.bs_data)
    st.text('mongo upload done!')
