cd src


# repare vector
python3 tools/prepare/prepare_vector.py

uvicorn apis:app --port 8090 &


streamlit run travel_ui.py