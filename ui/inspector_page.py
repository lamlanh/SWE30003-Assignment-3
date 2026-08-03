import streamlit as st
import os
import json

def render(system):
    st.title("Live JSON Data Inspector")
    st.info("This page shows the raw contents of our database for marking purposes.")

    # Locate the data/ folder
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    # If the folder doesn't exist yet, there's nothing to show
    if not os.path.exists(data_dir):
        st.warning("Data directory has not been created yet. Register a user to create it!")
        return

    # List all the files in the data folder (e.g., customers.json, orders.json)
    files = os.listdir(data_dir)
    json_files = [f for f in files if f.endswith('.json')]

    if not json_files:
        st.warning("No JSON files found yet.")
        return

    # Create a nice dropdown menu to select which file to view
    selected_file = st.selectbox("Select a JSON file to inspect:", json_files)

    if selected_file:
        file_path = os.path.join(data_dir, selected_file)

        try:
            # Open the file and read the raw text
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # Streamlit has a built-in function that formats JSON beautifully!
            st.json(raw_data)

        except Exception as e:
            st.error(f"Could not read {selected_file}: {e}")