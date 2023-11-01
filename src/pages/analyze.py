import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px


folder_dir = f"{Path(__file__).parents[1]}\\data\\"

df = pd.read_csv(f"{folder_dir}clean_songs.csv")

st.title("Analyze Recently Loaded Songs")

date = str(df["upload_date"].iloc[2])
st.subheader(f"Showing songs from {date[:10]}")
st.text("To change the date/sample, visit the Collection page")

st.subheader("Was there a match for each song?")
good_songs = df["match_conclusion"].value_counts()
valid_songs = pd.DataFrame(good_songs).reset_index()
st.plotly_chart(px.pie(valid_songs, values="count", names="match_conclusion"))

st.subheader("Let's look at song release date vs length:")
st.write("Hover points to see song title/artist")
st.text("Only showing songs with presumed Spotify matches")
fig = px.scatter(
    df[df["match_conclusion"] == True],
    x="album_released",
    y="upvotes",
    hover_data=["title", "artist"],
    color="difficulties",
    size="duration_seconds",
    height=550,
)

fig.update_layout(legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01))

st.plotly_chart(fig, theme=None, use_container_width=True)

st.subheader("Check out some histograms of the songs!")
histable = [
    "duration_seconds",
    "score",
    "upvotes",
    "sp_danceability",
    "sp_energy",
    "sp_key",
    "sp_loudness",
    "sp_mode",
    "sp_speechiness",
    "sp_acousticness",
    "sp_instrumentalness",
    "sp_liveness",
    "sp_valence",
    "sp_tempo",
    "sp_time_signature",
    "sp_popularity",
]
answer_x = st.selectbox(
    "Select a column to visualize distribution for:", options=histable
)

st.plotly_chart(px.histogram(df[df["match_conclusion"] == True], x=answer_x))
