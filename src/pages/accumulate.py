import streamlit as st
import os
import sys
from pathlib import Path
import datetime

sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from spotpull import SpotPull
from to_mongo import ToMongo

st.title("Collect Some Songs")
st.write("Enter a date to check 50 maps posted on that date")
date = st.date_input(
    "Map Upload Date",
    value="today",
    min_value=datetime.date(2018, 5, 9),
    max_value=datetime.date.today(),
)
date = str(date)
if st.button("Get Those Songs"):
    st.write("Please be patient, results may take 60 seconds to appear")
    try:
        s = SpotPull(date)
        s.lookit_me = s.bs_data
        st.caption(
            """Buttons in the upper-right corner of the table can be used to:
            Download as CSV, Search, or View Full Screen"""
        )

        st.dataframe(
            s.lookit_me[
                [
                    "match_conclusion",
                    "title",
                    "artist",
                    "mapper_name",
                    "difficulties",
                    "bs_map_link",
                    "spotify_link",
                ]
            ].set_index(s.lookit_me.columns[40])
        )
        st.subheader("What's next?")
        st.text("Wait just a bit longer for me to digest this data...")
        s.local_save()
        st.write(
            "Local CSV ready! - Go to the Analyze page to see stats on these songs"
        )
        st.text("...adding songs to database...")
        tm = ToMongo()
        tm.update_stats()
        tm.upload_one_by_one(s.bs_data)
        st.write(
            "Mongo upload done! - These songs will be incorporated in Stats - All Time and Query results"
        )
    except:
        st.write(
            "Unable to find songs on that date. Please select a new date and try again"
        )
        st.write("If the problem persists, try reloading this webpage.")
