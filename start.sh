cd src

# repare vector
python3 tools/prepare/prepare_vector.py

uvicorn agents.host_agent.__main__:app --port 8000 &
uvicorn agents.flight_agent.__main__:app --port 8001 &
uvicorn agents.stay_agent.__main__:app --port 8002 &      
uvicorn agents.activities_agent.__main__:app --port 8003 &
uvicorn agents.booking_agent.__main__:app --port 8004 &
streamlit run travel_ui.py