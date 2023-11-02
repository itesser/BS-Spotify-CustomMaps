import streamlit as st

st.header("Roadmap")
st.subheader("Where it comes from")

st.text(
    """
This app is a somewhat organic growth from the desire to 
passively explore the newest custom Beat Saber maps.
'Newest 50' was a good start, but limited, and it 
seemed like a waste to dump those 50 songs each time a 
new query came in. 

Enter... the database! 
Now each dip into the Beat Saver API is archived with 
links to the custom map, and the best match song that
Spotify has to offer.

At this time my knowledgebase of Beat Saber songs
is still just growing 50 entries at a time, in date-
bound chunks. Unfortunately, this means some of the
top mappers of yesteryear are underrepresented... 
...or not represented at all... yet.
"""
)

st.subheader("What it is")
st.text(
    """All this is made possible by the API offered by BeatSaver, 
  one of the top sources for custom Beat Saber maps/songs"""
)
st.text("Check them out at https://beatsaver.com/")

st.subheader("Where it is going")
st.text(" - fix all_stats graph")
st.text(" - add custom theme")
st.text(" - have top artists/mappers write in two columns")
st.text(
    " - simplified map difficulty (improve legibility of all stats default graph and analyse default graph)"
)
st.text(" - batching song detail requests (easier on Spotify API)")
st.text(" - query page -  view simplified or full results")
st.text(" - set dtypes of initial accumulation dataframe")
st.text(" - change dataframe in collect.py to match df in query.py")
st.text(" - collect by mapper")
st.text(" - collect by artist")
st.text(" - Oauth/playlist functionality")
