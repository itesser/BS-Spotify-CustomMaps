import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from spotpull import SpotPull
from to_mongo import ToMongo

folder_dir = f"{Path(__file__).parents[1]}\\data\\"
c = ToMongo()
df = pd.DataFrame(list(c.songs.find()))
st.set_page_config(layout="wide")
## setting up the dataframe for charts

df = df[
    [
        "title",
        "artist",
        "mapper_name",
        "duration_seconds",
        "upload_date",
        "difficulties",
        "album_released",
        "sp_artist",
        "sp_danceability",
        "sp_energy",
        "sp_key",
        "sp_loudness",
        "sp_speechiness",
        "sp_acousticness",
        "sp_instrumentalness",
        "sp_liveness",
        "sp_valence",
        "sp_tempo",
        "sp_popularity",
        "artist_match",
        "title_match",
        "duration_difference",
        "match_conclusion",
        "upvotes",
        "downvotes",
        "score",
        "last_fetched",
    ]
]

df["total_votes"] = df["upvotes"] + df["downvotes"]

hist_vars = [
    "duration_seconds",
    "difficulties",
    "album_released",
    "sp_energy",
    "sp_key",
    "sp_loudness",
    "sp_speechiness",
    "sp_acousticness",
    "sp_instrumentalness",
    "sp_liveness",
    "sp_valence",
    "sp_tempo",
    "sp_popularity",
    "upvotes",
    "downvotes",
    "total_votes",
    "score",
    "last_fetched",
]
scatter_vars_x = [
    "top_30_artists",
    "top_30_mappers",
    "duration_seconds",
    "upload_date",
    "album_released",
    "sp_danceability",
    "sp_energy",
    "sp_key",
    "sp_loudness",
    "sp_speechiness",
    "sp_acousticness",
    "sp_instrumentalness",
    "sp_liveness",
    "sp_valence",
    "sp_tempo",
    "sp_popularity",
    "upvotes",
    "downvotes",
    "total_votes",
    "score",
    "last_fetched",
]
scatter_vars_y = [
    "duration_seconds",
    "upload_date",
    "album_released",
    "sp_danceability",
    "sp_energy",
    "sp_key",
    "sp_loudness",
    "sp_speechiness",
    "sp_acousticness",
    "sp_instrumentalness",
    "sp_liveness",
    "sp_valence",
    "sp_tempo",
    "sp_popularity",
    "upvotes",
    "downvotes",
    "total_votes",
    "score",
    "last_fetched",
]

## PAGE CONTENT BEGINS

st.title("All Time Statistics")
st.write("... but just for songs that I know about")

st.caption(
    "Check Histogram - Upload Date to see gaps in my knowledge  \n then add a date via the Accumulate page to help fill things in ^_^"
)

match_choice = st.selectbox(
    "Show stats on which song type(s)?", options=["Matched", "Unmatched", "Both"]
)

if match_choice == "Matched":
    match_var = df[df["match_conclusion"] == True]
elif match_choice == "Unmatched":
    match_var = df[df["match_conclusion"] == False]
else:
    match_var = df


# Tof of the screen always shows a scatterplot
# Details: song date(x) vs map date (y) with score as size and difficulties as color
fig = px.scatter(
    match_var,
    x="album_released",
    y="upload_date",
    hover_data=["title", "artist"],
    color="difficulties",
    size="score",
    height=500,
)
fig.update_layout(legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01))
st.plotly_chart(fig, use_container_width=True, theme=None)

# dropdown has suggested graphs plus "pick my own"
graph_options = [
    "Pie - Matched/Unmatched",
    "Histogram - Upload Date",
    "Histogram - Danceability",
    "Scatter - Duration vs Album Release",
    "Scatter - Total Votes vs Spotify Popularity",
    "Scatter - Score vs Spotify Popularity",
    "------",
    "DIY - Histogram",
    "DIY - Scatterplot",
]

next_graph = st.selectbox("What would you like to see next?", options=graph_options)

if next_graph == "Histogram - Upload Date":
    st.plotly_chart(px.histogram(match_var, x="upload_date"))

elif next_graph == "Histogram - Danceability":
    st.plotly_chart(px.histogram(match_var, x="sp_danceability"))

elif next_graph == "Scatter - Duration vs Album Release":
    fig = px.scatter(
        match_var,
        x="album_released",
        y="duration_seconds",
        hover_data=["title", "artist"],
        size="score",
        height=550,
    )
    fig.update_layout(legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01))
    st.plotly_chart(fig, theme=None, use_container_width=True)

elif next_graph == "Scatter - Total Votes vs Spotify Popularity":
    fig = px.scatter(
        match_var,
        x="total_votes",
        y="sp_popularity",
        hover_data=["title", "artist"],
        size="score",
        height=550,
    )
    fig.update_layout(legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01))
    st.plotly_chart(fig, theme=None, use_container_width=True)

elif next_graph == "Scatter - Score vs Spotify Popularity":
    fig = px.scatter(
        match_var,
        x="score",
        y="sp_popularity",
        hover_data=["title", "artist"],
        size="total_votes",
        height=550,
    )
    fig.update_layout(legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01))
    st.plotly_chart(fig, theme=None, use_container_width=True)

elif next_graph == "Pie - Matched/Unmatched":
    good_songs = df["match_conclusion"].value_counts()
    valid_songs = pd.DataFrame(good_songs).reset_index()
    st.plotly_chart(px.pie(valid_songs, values="count", names="match_conclusion"))

elif next_graph == "DIY - Histogram":
    answer_x = st.selectbox(
        "Select a column to visualize distribution for:", options=hist_vars
    )
    st.plotly_chart(px.histogram(match_var, x=answer_x))

elif next_graph == "DIY - Scatterplot":
    scatter_x = st.selectbox("X Axis Variable", scatter_vars_x)
    scatter_y = st.selectbox("Y Axis Variable", scatter_vars_y)
    if st.button("See the Graph!"):
        if scatter_x == "top_30_artists":
            top_artists = list(
                match_var["sp_artist"]
                .value_counts(ascending=False)
                .head(30)
                .reset_index()["sp_artist"]
            )
            top_artist_df = match_var[match_var["sp_artist"].isin(top_artists)]
            fig = px.scatter(
                top_artist_df,
                x="artist",
                y=scatter_y,
                hover_data=["title", "artist"],
                height=550,
            )
            fig.update_layout(
                legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig, theme=None, use_container_width=True)
        elif scatter_x == "top_30_mappers":
            top_mappers = list(
                match_var["mapper_name"]
                .value_counts(ascending=False)
                .head(30)
                .reset_index()["mapper_name"]
            )
            top_mapper_df = match_var[match_var["mapper_name"].isin(top_mappers)]
            fig = px.scatter(
                top_mapper_df,
                x="mapper_name",
                y=scatter_y,
                hover_data=["title", "artist"],
                height=550,
            )
            fig.update_layout(
                legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig, theme=None, use_container_width=True)
        else:
            fig = px.scatter(
                match_var,
                x=scatter_x,
                y=scatter_y,
                hover_data=["title", "artist"],
                height=550,
            )
            fig.update_layout(
                legend=dict(yanchor="bottom", y=3.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig, theme=None, use_container_width=True)
