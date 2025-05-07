import os
import json
import requests
import streamlit as st
from configs import get_logger
logger = get_logger(__name__)


st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️", layout="wide")
# st.title("🌍 ADK-Powered Travel Planner")


# 初始化会话状态
if 'first_response' not in st.session_state:
    st.session_state.first_response = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = None

with st.sidebar:

    st.title("🔥Travel Planner")
    origin = st.text_input("Where are you flying from?", placeholder="e.g., New York")
    destination = st.text_input("Destination", placeholder="e.g., Paris")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    budget = st.number_input("Budget (in USD)", min_value=500, step=50)
    if st.button("Plan My Trip ✨"):

        if not all([origin, destination, start_date, end_date, budget]):
            st.warning("Please fill in all the details.")
        else:
            payload = {
                "origin": origin,
                "destination": destination,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "budget": budget,
            }
            response = requests.post("http://localhost:8090/plan", json=payload)
            if response.ok:
                st.session_state.first_response = response.json()
                # st.subheader("✈️ Flights")
                # st.markdown(st.session_state.first_response["flights_agent"])
                # st.subheader("🏨 Stays")
                # st.markdown(st.session_state.first_response["stay_agent"])
                # st.subheader("🗺️ Activities")
                # st.markdown(st.session_state.first_response["activities_agent"])
            else:
                st.error("Failed to fetch travel plan. Please try again.")


# if st.session_state.first_response is not None:
#     st.markdown(st.session_state.first_response)

col1, col2, col3 = st.columns(3)

if st.session_state.first_response is not None:
    resp = st.session_state.first_response
    if resp['code'] == 200:
        # 在第一栏中添加内容
        with col1:
            st.subheader("✈️ Flight")
            if "flight_agent" in resp['data']:
                st.markdown(resp['data']["flight_agent"])
            else:
                st.markdown("Failed to fetch this plan")

        # 在第二栏中添加内容
        with col2:
            st.subheader("🏨 Stay")
            if "stay_agent" in resp['data']:
                st.markdown(resp['data']["stay_agent"])
            else:
                st.markdown("Failed to fetch this plan")

        # 在第三栏中添加内容
        with col3:
            st.subheader("🗺️ Activities")
            if "activities_agent" in resp['data']:
                st.markdown(resp['data']["activities_agent"])
            else:
                st.markdown("Failed to fetch this plan")
    else:
        st.error("Failed to fetch travel plan. Please try again.")