import streamlit as st
import pandas as pd
import json

# Create a file uploader component
uploaded_files = st.file_uploader(
    "Choose CSV Files", type="json", accept_multiple_files=True)

# Create a drop-down menu for selecting columns
if uploaded_files is not None:
    with open(uploaded_files[0]) as chapter:
        parsed_json = json.load(chapter)
        approaches = parsed_json[os.path.splitext(os.path.basename(chapter))[0]]



genre = st.radio("Select Approach",('Comedy', 'Drama', 'Documentary'))
