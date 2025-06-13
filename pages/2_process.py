import streamlit as st
import requests
import os
from groq import Groq
import json
client = Groq(
    api_key = "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" # Set your Groq API key as an environment variable
)
def generate_transcript():
    st.info(f"Generating Transcript")
    
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
                timestamp_granularities= ["word", "segment"],
            )
        print(json.dumps(transcription, indent=2, default=str))
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)  


def generate_summary():
    st.info(f"Generating summary")

    try:
        # Load transcript from file
        transcript_file = os.path.join("files", "smart_recap_transcript.json")
        if not os.path.isfile(transcript_file):
            st.error(f"Transcript file not found: {os.path.abspath(transcript_file)}")
            return

        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript_content = f.read()

        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
            {
                "role": "system",
                "content": "You are a brilliant movie analysis API that performs analysis based on provided transcript of the movie with the timestamp and its segment detail as well. Respond only with JSON using this format: {\"movie_analysis\": {\"genre\": \"Action|Comedy|Drama|Fantasy|Horror|Mystery|Romance|Thriller\", \"confidence_score\": 0.95, \"key_phrases\": [{\"phrase\": \"detected key phrase\", \"sentiment\": \"positive|negative|neutral\"}], \"summary\": \"Detail summary of the movie transcript\"}}"
            },
            {
                "role": "user",
                "content": transcript_content
            }
            ],
            temperature=0.6,
            max_completion_tokens=6000,
            top_p=0.95,
            stream=False,
            stop=None,
        )
        st.write(completion.choices[0].message)
        full_response = completion.choices[0].message
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)


st.title("Generate Recap of the Video")

st.button("Generate Transcribe",on_click=generate_transcript)

st.button("Generate Summary",on_click=generate_summary)
