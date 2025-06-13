import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Set your Hugging Face API token
api_token = "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"
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
#API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
headers = {"Authorization": f"Bearer {api_token}"}

st.set_page_config(layout="wide")  # Set the layout to wide
st.markdown(
    """
    <style>
    th, td {
        word-wrap: break-word;
        white-space: normal;
    }
    th {
        text-align: left !important;
    }
    td {
        text-align: left !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🤖 AIML Resume Analyzer")

uploaded_files = st.file_uploader("📂 Upload Resumes", accept_multiple_files=True, type=["txt", "docx","pdf"])

if uploaded_files:
    data = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split(".")[-1]
        
        # Extract text based on file type
        if file_type == "txt":
            resume_text = uploaded_file.read()      
        else:
            st.error(f"Unsupported file format: {file_type}")
            continue

        # Extract candidate name (assuming first non-empty line)
        candidate_name = next((line.strip() for line in resume_text.split("\n") if line.strip()), "Unknown")

