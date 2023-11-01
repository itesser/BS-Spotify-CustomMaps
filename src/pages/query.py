import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from to_mongo import ToMongo
from tag_manip import get_tags

def release_era(yo):
    eras_dict = {
        '2011-2018': match_var[(match_var['album_year'] >= '2011') & (match_var['album_year'] <= '2018')],
        '00s': match_var[(match_var['album_year'] >= '2000') & (match_var['album_year'] <= '2010')],
        '90s': match_var[(match_var['album_year'] >= '1990') & (match_var['album_year'] <= '1999')],
        '80s': match_var[(match_var['album_year'] >= '1980') & (match_var['album_year'] <= '1989')],
        'Older': match_var[match_var['album_year'] <= '1979'] 
    }
    if len(yo) == 4:
        return match_var[match_var['album_year']==yo]
    else:
        return eras_dict[yo]

folder_dir = f"{Path(__file__).parents[1]}\\data\\"

c = ToMongo()
pure_frame = pd.DataFrame(list(c.songs.find()))
good_cols = ['match_conclusion', 'title', 'artist', 'mapper_name',
       'duration_seconds', 'upload_date', 'upvotes',
       'downvotes', 'score', 'bs_map_link', 'spotify_link', 
       'difficulties', 'sp_title', 'sp_artist', 'sp_popularity',
       'album', 'album_released', 'sp_duration',
       'sp_danceability', 'sp_energy', 'sp_key', 'sp_loudness', 'sp_mode',
       'sp_speechiness', 'sp_acousticness', 'sp_instrumentalness',
       'sp_liveness', 'sp_valence', 'sp_tempo', 'sp_time_signature',
        'artist_match', 'title_match', 'duration_difference', 'last_fetched']

df = pure_frame[good_cols]

df['duration_seconds'] = round(df['duration_seconds']/60,2)
df = df.rename(columns={'duration_seconds': 'duration_mins'})
df[['upload_year', 'upload_mo', 'upload_day']] = df.upload_date.str.split("-", expand=True)
df[['album_year', 'album_mo', 'album_day']] = df.album_released.str.split("-", expand=True)
df['total_votes'] = df['upvotes'] + df['downvotes']
df['score'] = df['score']*100

# streamlit decor
# Intro text

# Do you want to look at matched songs, unmatched songs, or all?
match_choice = st.selectbox("Show stats on which song type(s)?", options=['Matched', 'Unmatched', 'Both'])

# match_var filters the loaded dataframe, match key will be used when displaying mongo query results
if match_choice == 'Matched':
    match_var = df[df["match_conclusion"] == True]
    match_key = True
elif match_choice == 'Unmatched':
    match_var = df[df['match_conclusion'] == False]
    match_key = False
else:
    match_var = df
    match_key = 'all'

# choose a column to filter by
col_filter_options = ['Pick from this list!', 'Duration', 'Artist', 'Album Release Date', 'Map Score', 'Mapper Name', 'Song Tags', 'Map Difficulty']
query_type = st.selectbox("How To Divvy up the Data?", options=col_filter_options)

# Duration
if query_type == 'Duration':
    dur_sort = st.radio("Which type of duration?", options=["Long", "Short"], horizontal = True)
    year_filter = st.selectbox("Limit to Upload Year?", options=['All years', '2018', '2019', '2020','2021', '2022', '2023'])
    if year_filter == "All years":
        dur_display = match_var.sort_values('duration_mins', ascending=(dur_sort=="Short"))
    else:
        dur_display = match_var[match_var['upload_year']==year_filter].sort_values('duration_mins', ascending=(dur_sort=="Short"))
    st.dataframe(dur_display)

# Artist:
elif query_type == "Artist":
    distinct_artists = list(c.songs.distinct('sp_artist'))
    artist_count = len(distinct_artists)
    total_maps = df.shape[0]
    st.write(f"I have only collected data for {total_maps} custom maps and identified {artist_count} distinct artists.")
    st.write("Here are the top 20 (but you can search for any artist you'd like)")
    top_artists = list(match_var['sp_artist'].value_counts(ascending=False).head(20).reset_index()['sp_artist'])
    for artist in top_artists:
        st.write(artist)
    search_artist = st.text_input('Artist to search for (partial name ok, case sensitive)')
    if st.button('Search!'):
        aq_reply = list(c.songs.find({"artist":{'$regex':search_artist}}))
        if len(aq_reply) < 1:
            st.write(f'Sorry, could not find any artist matches for {search_artist}!')
        else:
            aq_display = pd.DataFrame(aq_reply)
            aq_display = aq_display[good_cols]
            if match_key != 'all':
                aq_display = aq_display[aq_display['match_conclusion']==match_key]
            st.dataframe(aq_display)

#Album Release
elif query_type == "Album Release Date":
    year_options = ['2023', '2022', '2021', '2020', '2019', '2011-2018', '00s', '90s', '80s', 'Older']
    month_options = {
        'All': 0,
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
        }
    
    release_year = st.selectbox("Pick a Year or Era", options = year_options)
    release_month = st.selectbox("Filter By Month (or not)", options = month_options.keys())
    selected_year_df = release_era(release_year)
    if release_month == 'All':
        st.dataframe(selected_year_df)
    else:
        st.dataframe(selected_year_df[selected_year_df['album_mo']==month_options[release_month]])


elif query_type == "Map Score":
    year_list = ['All']
    for i in range(2018,2024):
        year_list.append(str(i))
    view_year = st.selectbox("Upload Year", year_list)
    vote_min = match_var.sort_values('total_votes', ascending=False).iloc[20]['total_votes']
    min_votes = st.slider("Minimum Map Votes", max_value = vote_min)
    if st.button("View Results"):
        if view_year == 'All':
            score_df = match_var[match_var['total_votes']>= min_votes]
        else:
            score_df = match_var[(match_var['total_votes']>= min_votes)& (match_var['upload_year']==view_year)]
        if (len(score_df)) < 1:
            st.write("No maps from that year have that many votes!")
        else:
            st.dataframe(score_df.sort_values('score', ascending=False))

#Mapper Name:
elif query_type == "Mapper Name":
    distinct_mappers = list(c.songs.distinct('mapper_name'))
    mapper_count = len(distinct_mappers)
    total_maps = df.shape[0]
    st.write(f"I have only collected data for {total_maps} custom maps and identified {mapper_count} distinct mappers.")
    st.write("Here are the top 20 (but you can search for any mapper you'd like)")
    top_mappers = list(match_var['mapper_name'].value_counts(ascending=False).head(20).reset_index()['mapper_name'])
    for mapper in top_mappers:
        st.write(mapper)
    search_mapper = st.text_input('Mapper to search for (partial name ok, case sensitive)')
    if st.button('Search!'):
        mq_reply = list(c.songs.find({"mapper_name":{'$regex':search_mapper}}))
        if len(mq_reply) < 1:
            st.write(f'Sorry, could not find any mapper name matches for {search_mapper}!')
        else:
            mq_display = pd.DataFrame(mq_reply)
            mq_display = mq_display[good_cols]
            if match_key != 'all':
                mq_display = mq_display[mq_display['match_conclusion']==match_key]
            st.dataframe(mq_display)

elif query_type == "Song Tags":
    tag_qty = st.slider("See top X tags", min_value = 20)
    tag_list = get_tags(pure_frame, tag_qty)
    query_tag = st.selectbox("Search for a tag", options = tag_list)
    if st.button("Get matching songs"):
        tag_reply = list(c.songs.find({"tags":{'$regex':query_tag}}))
        tag_display = pd.DataFrame(tag_reply)
        tag_display = tag_display[good_cols]
        if match_key != 'all':
            tag_display = tag_display[tag_display['match_conclusion']==match_key]
        st.dataframe(tag_display)

elif query_type == "Map Difficulty":
    difficulty_list = ['Easy', 'Normal', 'Hard', 'Expert', 'ExpertPlus']
    map_query = st.selectbox("Find mpas for which difficulty?", options = difficulty_list)
    if st.button("Show those maps!"):
        map_reply = list(c.songs.find({'difficulties':{'$regex':map_query}}))
        map_display = pd.DataFrame(map_reply)
        map_display = map_display[good_cols]
        if match_key != 'all':
            map_display = map_display[map_display['match_conclusion']==match_key]
        st.dataframe(map_display)
