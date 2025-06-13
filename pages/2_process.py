import streamlit as st
import requests
import os
from groq import Groq
import json
client = Groq(
    api_key = "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" # Set your Groq API key as an environment variable
)
def generate_transcript():
    st.info(f"Generating trailer")
    
    filename = os.path.join("files", "videoplayback.mp4")
    if not os.path.isfile(filename):
        st.error(f"File not found: {os.path.abspath(filename)}")
    st.write("Looking for file at:", os.path.abspath(filename))
    
    try:
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                temperature=0,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
        print(json.dumps(transcription, indent=2, default=str))
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)  


def generate_summary():
    st.info(f"Generating summary")
    
    filename = os.path.join("files", "videoplayback.mp4")
    if not os.path.isfile(filename):
        st.error(f"File not found: {os.path.abspath(filename)}")
    st.write("Looking for file at:", os.path.abspath(filename))
    
    try:
        with open(filename, "rb") as file:
            summary = client.audio.summaries.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                temperature=0,
                response_format="verbose_json",
            )
        print(json.dumps(summary, indent=2, default=str))
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)


st.title("Generate Recap of the Video")

st.button("Generate Transcribe",on_click=generate_transcript)

st.button("Generate Summary",on_click=generate_summary)
