import streamlit as st
import requests
import os
from groq import Groq
import json
import ast
import re
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
        st.session_state['full_response'] = full_response
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)

def generate_timestamp():
    st.info(f"Generating Timestamp for short video")
    with open("files/smart_recap_transcript.json", "r") as f:
        content = f.read().strip()

    # Extract the words array (greedy match between "words": [ and the closing ])
    words_match = re.search(r'"words"\s*:\s*(\[[^\]]*\])', content, re.DOTALL)
    segments_match = re.search(r'"segments"\s*:\s*([^\n,\}\]]+)', content)
    words = []
    segments = []
    if words_match:
        words_str = words_match.group(1)
        words = json.loads(words_str)
    if segments_match:
        segments_str = segments_match.group(1)
        segments = json.loads(segments_str)
    try:
        full_response = st.session_state.get('full_response', '')
        full_response = {
    "content": "<think>\nOkay, I need to analyze this movie transcript ...\n</think>\n\n"
               "{\"movie_analysis\": {\"genre\": \"Thriller\", \"confidence_score\": 0.95, "
               "\"key_phrases\": [{\"phrase\": \"CIA black fault break-in\", \"sentiment\": \"negative\"}, "
               "{\"phrase\": \"The Kremlin bombing\", \"sentiment\": \"negative\"}, "
               "{\"phrase\": \"Your team has been betrayed\", \"sentiment\": \"negative\"}, "
               "{\"phrase\": \"Our lives are the sum of our choices\", \"sentiment\": \"positive\"}], "
               "\"summary\": \"The transcript suggests a high-stakes thriller involving espionage, betrayal, and critical decision-making. "
               "The dialogue hints at a character named Ethan facing a world on the brink of crisis, with themes of destiny and trust. "
               "The mention of CIA operations, bombings, and compromised secrets indicates a complex plot with intense consequences.\"}}",
    "role": "assistant"
}
        content_str = full_response["content"]
        json_match = re.search(r'(\{.*"movie_analysis".*\})', content_str, re.DOTALL)
        if json_match:
            movie_json_str = json_match.group(1)
            movie_json = json.loads(movie_json_str)
            movie_analysis = movie_json.get("movie_analysis", {})
            genre = movie_analysis.get("genre")
            key_phrases = movie_analysis.get("key_phrases")
            summary = movie_analysis.get("summary")
            # Now you can use genre, key_phrases, and summary as needed
            completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
            {
                "role": "system",
                "content": "You are a brilliant movie analysis API that provide key timestamps of the movie  based on provided transcript of the movie with the timestamp, movie segment detail, genre , key phrase in the movie and its summary. Key timestamps will be used to create short video which should not more than 45 seconds. Respond only with JSON using this format: {\"movie_timestamp\": {\"timestamps\": [{\"start\": \"start videostamp\", \"end\": \"end timestamp\"}]\}"
            },
            {
                "role": "user",
                "content": "Provide movie timestamp to generate short video. Here are the details: \n\nGenre: " + genre + "\n\nKey Phrases: " + str(key_phrases) + "\n\nSummary: " + summary + "\n\nTranscript: " + str(words) + "\n\nSegments: " + str(segments)
            }
            ],
            temperature=0.6,
            max_completion_tokens=10000,
            top_p=0.95,
            stream=False,
            stop=None,
        )
            st.write(completion.choices[0].message)
        else:
            st.error("movie_analysis JSON not found in the response.")
    except json.JSONDecodeError as e:
         st.error(f"Error decoding JSON: {e}")

st.title("Generate Recap of the Video")

st.button("Generate Transcribe",on_click=generate_transcript)

st.button("Generate Summary",on_click=generate_summary)

st.button("Generate shortVideo Timestamp",on_click=generate_timestamp)
