import streamlit as st
#genuinely hate the existence of this file, but i need to interact with the streamlit secrets feature for deployment purposes
live_games_api_url = st.secrets["api_football"]["live_games_api_url"]
team_history_api_url = st.secrets["api_football"]["team_history_api_url"]
fixture_statistics_api_url = st.secrets["api_football"]["fixture_statistics_api_url"]
standings_api_url = st.secrets["api_football"]["standings_api_url"]
headers = {
     "x-rapidapi-key": st.secrets["api_football"]["x_rapidapi_key"],
     "x-rapidapi-host": st.secrets["api_football"]["x_rapidapi_host"]
    }





