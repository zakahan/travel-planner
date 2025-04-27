import requests
import streamlit as st
from configs import get_logger
logger = get_logger(__name__)


st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️")
st.title("🌍 ADK-Powered Travel Planner")

# 初始化会话状态
if 'first_response' not in st.session_state:
    st.session_state.first_response = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = None

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
        response = requests.post("http://localhost:8000/run", json=payload)
        if response.ok:
            st.session_state.first_response = response.json()
            st.subheader("✈️ Flights")
            st.markdown(st.session_state.first_response["flights"])
            st.subheader("🏨 Stays")
            st.markdown(st.session_state.first_response["stay"])
            st.subheader("🗺️ Activities")
            st.markdown(st.session_state.first_response["activities"])
        else:
            st.error("Failed to fetch travel plan. Please try again.")

if st.session_state.first_response is not None:
    user_input = st.chat_input("Do you want to booking?")
    if user_input and st.session_state.user_input is None:
        st.session_state.user_input = user_input
        req = {
            "plan": f"""'flight': {st.session_state.first_response["flights"]}, 'stay':{st.session_state.first_response["stay"]}, 'activities': {st.session_state.first_response["activities"]}""",
            "message": user_input
        }

        logger.info("__REQ__"+str(req))
        response2 = requests.post('http://localhost:8004/run', json=req)
        if response2.ok:
            data = response2.json()
            st.subheader("Booking:")
            st.markdown(data['summary'])