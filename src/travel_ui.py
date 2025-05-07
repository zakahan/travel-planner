import os
import json
import requests
import streamlit as st
from configs import get_logger
logger = get_logger(__name__)


st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️", layout="wide")
# st.title("🌍 ADK-Powered Travel Planner")

def replan(suggest: str, part: str):
    payload = {
                "origin": origin,
                "destination": destination,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "budget": budget,
                "plan" : str(st.session_state.first_response),
                "suggest": f"用户对{part}提出了意见，意见内容是{suggest}"
            }
    response = requests.post("http://localhost:8090/replan", json=payload)
    if response.ok:
        data = dict(response.json()['data'])
        for key, value in data.items():
            st.session_state.first_response[key] = value
        # 强制页面重新运行
        st.rerun()


def booking(suggest: str):
    print("aaaaaa")
    payload = {
        "plan": str(st.session_state.first_response),
        "suggest": suggest
    }
    response = requests.post("http://localhost:8090/booking", json=payload)
    print(f"response:{response.json()}")
    if response.json()['code']==200:
        st.info(f"预定成功：{response.json()['data']}")
    else:
        st.error("预定失败")


# 初始化会话状态
if 'first_response' not in st.session_state:
    st.session_state.first_response = {}
if 'user_input' not in st.session_state:
    st.session_state.user_input = None

if 'show_input_flight' not in st.session_state:
    st.session_state.show_input_flight = False

if 'show_input_stay' not in st.session_state:
    st.session_state.show_input_stay = False

if 'show_input_activities' not in st.session_state:
    st.session_state.show_input_activities = False

if 'show_input_booking' not in st.session_state:
    st.session_state.show_input_booking = False

if 'booking_text' not in st.session_state:
    st.session_state.booking_text = ""

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
                st.session_state.first_response = response.json()['data']
                # st.markdown(st.session_state.first_response["activities_agent"])
            else:
                st.error("Failed to fetch travel plan. Please try again.")


# if st.session_state.first_response is not None:
#     st.markdown(st.session_state.first_response)

col1, col2, col3 = st.columns(3)

if len(st.session_state.first_response) != 0:
    # 在第一栏中添加内容
    with col1:
        st.subheader("✈️ Flight")
        if "flight_agent" in st.session_state.first_response:
            st.markdown(st.session_state.first_response["flight_agent"])
        else:
            st.markdown("Failed to fetch this plan")
        if st.button("Another Batch 🏃‍♂️"):
            st.session_state.show_input_flight = not st.session_state.show_input_flight
        if st.session_state.show_input_flight:
            user_input_flight = st.chat_input("Any suggestion about flight?")
            if user_input_flight is not None:
                replan(user_input_flight, "flight_agent")
                st.session_state.show_input_flight = not st.session_state.show_input_flight
    # 在第二栏中添加内容
    with col2:
        st.subheader("🏨 Stay")
        if "stay_agent" in st.session_state.first_response:
            st.markdown(st.session_state.first_response["stay_agent"])
        else:
            st.markdown("Failed to fetch this plan")
        if st.button("Another Batch 🙋"):
            st.session_state.show_input_stay = not st.session_state.show_input_stay
        if st.session_state.show_input_stay:
            user_input_stay = st.chat_input("Any suggestion about stay?")
            if user_input_stay is not None:
                replan(user_input_stay, "saty_agent")
                st.session_state.show_input_stay = not st.session_state.show_input_stay
    # 在第三栏中添加内容
    with col3:
        st.subheader("🗺️ Activities")
        if "activities_agent" in st.session_state.first_response:
            st.markdown(st.session_state.first_response["activities_agent"])
        else:
            st.markdown("Failed to fetch this plan")

        if st.button("Another Batch 😼"):
            st.session_state.show_input_activities = not st.session_state.show_input_activities
        if st.session_state.show_input_activities:
            user_input_activities = st.chat_input("Any suggestion about activities?")
            if user_input_activities is not None:
                replan(user_input_activities, "activities_agent")
                st.session_state.show_input_activities = not st.session_state.show_input_activities


    # st.markdown(st.session_state.booking_text)
    if st.button("Booking 🏨"):
        st.session_state.show_input_booking = not st.session_state.show_input_booking

    # 将 chat_input 移到状态判断代码块中
    if st.session_state.show_input_booking:
        user_input = st.chat_input("Do you want to booking?")
        if user_input is not None:
            booking(user_input)

           