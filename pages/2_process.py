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

def generate_transcript(file_path):
    st.info(f"Generating Transcript")
    
    filename = os.path.join("files", "videoplayback.mp4")
    if not os.path.isfile(filename):
        st.error(f"File not found: {os.path.abspath(filename)}")
    st.write("Looking for file at:", os.path.abspath(filename))
    
    try:
        with open(file_path, "rb") as file:
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
            #model="deepseek-r1-distill-llama-70b",
            model="llama-3.3-70b-versatile",
            messages=[
            {
                "role": "system",
                "content": "You are a brilliant movie analysis API that performs analysis based on provided transcript of the movie with the timestamp and its segment detail as well. Respond only with JSON in this exact format: {\"genre\": \"Action|Comedy|Drama|Fantasy|Horror|Mystery|Romance|Thriller\",\"VoiceOver\": \"Recap VoiceOver\"}.\n "
                            "Do not include any other text outside of the JSON."
            },
            {
                "role": "user",
                "content": "I have a complete transcript of the movie “[Movie Title]” (runtime ≈ 2 h 30 m). I’ve watched up through timestamp **[HH:MM:SS]** (about 1 hour in)."
                           "Using the transcript, please generate a **concise, coherent narrative recap** of everything that’s happened **from the very beginning up to [HH:MM:SS]**, suitable for a listener who wants to catch up in **under five minutes**. "
                           "Your recap should:\n"
                           "1. **Summarize only the key plot beats**, major character introductions and relationships, setting the tone and stakes.\n"
                           "2. **Use continuous prose** (no bullet lists), as if a voice-over narrator is speaking.\n"
                           "3. **Keep it engaging but efficient**—aim for roughly 600–800 words (about a 5-minute read aloud).\n"
                           "4. **Reference timestamps sparingly**, e.g. “By 00:15, our hero has already…”, but don’t over-timestamp every line."
                           "5. **Avoid spoilers beyond [HH:MM:SS]**—only cover events up to that point."
                           "6. **If [HH:MM:SS] is not provided, assume it is a request for a recap of the entire movie (from start to finish).**\n"
                           "7. **Include the film's genre in the recap and use a voice-over narration style that matches that genre's tone."
                           "For example, you might start:"
                           "> “At dawn in the sleepy town of Elmwood (00:00–00:05), we meet Alice, a curious archivist..."
                           "and conclude around:"
                           "> By 01:00:00, Alice has uncovered the first cryptic clue and narrowly escaped the antagonist's agents..."
                           "Now here is the transcript." + transcript_content            
            }
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
            max_completion_tokens=6000,
            top_p=0.95,
            stream=False,
            stop=None,
        )
        st.write(completion.choices[0].message.content)
        full_response = completion.choices[0].message.content
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
        print(words)
    if segments_match:
        segments_str = segments_match.group(1)
        segments = json.loads(segments_str)
        print(segments)
    try:
        full_response = st.session_state.get('full_response', '')
        print(full_response)
        full_response = json.loads(full_response)
        genre_str = full_response.get("genre")
        print(genre_str)
        voiceover_str = full_response.get("VoiceOver")
        print(voiceover_str)
        #json_match = re.search(r'(\{.*"movie_analysis".*\})', content_str, re.DOTALL)
        #if json_match:
        #    movie_json_str = json_match.group(1)
        #    movie_json = json.loads(movie_json_str)
        #    movie_analysis = movie_json.get("movie_analysis", {})
        #    print(movie_analysis)
        #    genre = movie_analysis.get("genre")
        #    print(genre)
        #    key_phrases = movie_analysis.get("key_phrases")
        #    print(key_phrases)
        #    summary = movie_analysis.get("summary")
        #    print(summary)
        #     Now you can use genre, key_phrases, and summary as needed
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a brilliant movie analysis API that finds relevant transcript timestamps to support a given voice-over narration. Respond only with JSON in this exact format:  {\"genre\": \"Action|Comedy|Drama|Fantasy|Horror|Mystery|Romance|Thriller\", \"visual_recap\": [{\"start\": \"HH:MM:SS\", \"end\": \"HH:MM:SS\", \"description\": \"Scene description matching the voice-over segment\"}, …]}. Do not include any text outside of the JSON. "       
            },
            {
                "role": "user",
                "content": "TASK:\n 1️. Analyze narration and transcript: For each key event or concept in the voice-over, identify the transcript segment that most closely represents it. Focus on meaning and context rather than exact word match.\n 2. Determine timestamps:\n- Use the start of the first word and the end of the last word in the selected transcript segment.\n- Use actual timestamps from the transcript; do not create or assume timestamps.\n- Convert timestamps to HH:MM:SS (zero-padded to two digits per section).\n 3. Maintain order: List segments chronologically as they appear in the transcript.\n 4. Write description: Provide a short, accurate description of the scene or dialogue that aligns with the voice-over.\n 5. Stick to JSON: Output only the JSON structure, no additional text or explanation.\n\n### INPUTS:\nVoice-Over Narration: \nTranscript (with timestamps): \n\n### NOTE:\n Do not invent timestamps.\n Timestamps must be from the transcript.\n Do not assume duration; base it only on transcript data.\n Output valid JSON exactly as specified."
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.6,
        max_completion_tokens=10000,
        top_p=0.95,
        stream=False,
        stop=None,
        )
        st.write(completion.choices[0].message)
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.exception(e)

uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])
if uploaded_file is not None:
    file_path = os.path.join("files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("Uploaded file:", uploaded_file.name)
    
    if st.button("Generate Recap"):
        with st.spinner("Processing..."):
            transcription = generate_transcript(file_path)
            if transcription:
                transcript_content = json.dumps(transcription)  # Assuming the transcription is in JSON format
                summary = generate_summary(transcript_content)
                if summary:
                    voiceover_str = summary.get("VoiceOver", "")
                    words = transcription.get("words", [])
                    segments = transcription.get("segments", [])
                    generate_timestamp(voiceover_str, words, segments) 

st.button("Generate Transcribe",on_click=generate_transcript)

st.button("Generate Summary",on_click=generate_summary)

st.button("Generate shortVideo Timestamp",on_click=generate_timestamp)
