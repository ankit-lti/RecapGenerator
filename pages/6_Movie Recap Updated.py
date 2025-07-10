import streamlit as st
import os
import json
from groq import Groq
from gtts import gTTS
import base64
from moviepy import *

client = Groq(api_key="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")  # Replace with your actual key

@st.cache_data
def load_transcript_text():
    file_path = os.path.join("files", "smart_recap_transcript.json")
    if not os.path.isfile(file_path):
        st.error("Transcript file not found.")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# UI Layout
st.set_page_config(page_title="Smart Movie Recap", layout="centered")
st.title("🎬 Smart Recap Generator")
st.markdown("Upload a trailer to generate voice-over and visual recap with scene timestamps.")

uploaded_file = st.file_uploader("📂 Upload a trailer video", type=["mp4"])
file_path = ""

if uploaded_file:
    file_path = os.path.join("files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File saved: {uploaded_file.name}")

    st.markdown("### 📄 File Summary")
    st.dataframe({ "Serial No.": [1], "File Name": [uploaded_file.name] })

    # Only show Generate Recap first
    if "recap_done" not in st.session_state:
        st.session_state.recap_done = False

    if not st.session_state.recap_done:
        if st.button("🚀 Generate Recap"):
            st.info("⏳ Generating recap, please wait...")
            try:
                transcript_text = load_transcript_text()
                if not transcript_text:
                    st.warning("Transcript missing.")
                else:
                    # --- Summary ---
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Summarize transcript into voice-over. Output JSON with genre and VoiceOver."},
                            {"role": "user", "content": f"Transcript:\n{transcript_text}"}
                        ],
                        response_format={"type": "json_object"},
                        max_completion_tokens=6000,
                        temperature=0.6
                    )
                    full_response = response.choices[0].message.content
                    st.session_state["full_response"] = full_response
                    st.markdown("### 🗣️ VoiceOver")
                    st.markdown(json.loads(full_response).get("VoiceOver", ""))

                    # --- Timestamps ---
                    voiceover = json.loads(full_response).get("VoiceOver", "")
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                             {
                        "role": "system",
                        "content": "You are a brilliant movie analysis API that maps narration to transcript timestamps. Output only JSON with genre and visual_recap."
                    },
                    {
                        "role": "user",
                        "content": (
                            "TASK:\n"
                            "1️. Analyze narration and transcript: For each key event or concept in the voice-over, identify the transcript segment that most closely represents it. Focus on meaning and context rather than exact word match.\n"
                            "2. Use only the timestamps provided in the transcript to determine the start and end times.\n"
                            "Do not estimate or invent timestamps.\n"
                            "Extract the exact start and end values from the transcript data.\n"
                            "3. Maintain order: List segments chronologically as they appear in the transcript.\n"
                            "4. Write description: Provide a short, accurate description of the scene or dialogue that aligns with the voice-over.\n"
                            "5. Stick to JSON: Output only the JSON structure, no additional text or explanation.\n\n"
                            f"VoiceOver: {voiceover}\n\nTranscript: {transcript_text}"
                        )
                    }                        ],
                        response_format={"type": "json_object"},
                        max_completion_tokens=8000,
                        temperature=0.6
                    )
                    output = json.loads(response.choices[0].message.content)
                    st.session_state["visual_recap"] = output
                    st.success("✅ Recap generation complete.")
                    st.markdown("### 🧠 Recap Segments")
                    st.json(output)
                    st.session_state.recap_done = True
            except Exception as e:
                st.error("Recap generation failed.")
                st.exception(e)

    # Buttons shown AFTER recap is generated
    if st.session_state.recap_done:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔊 Play VoiceOver"):
                try:
                    voiceover_text = json.loads(st.session_state["full_response"]).get("VoiceOver", "")
                    if voiceover_text:
                        tts = gTTS(voiceover_text)
                        tts.save("voiceover.mp3")
                        with open("voiceover.mp3", "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                            st.markdown(f"""
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.error("VoiceOver playback failed.")
                    st.exception(e)

        with col2:
            if st.button("🎞️ Play Recap Video"):
                try:
                    scenes = st.session_state.get("visual_recap", {}).get("visual_recap", [])
                    video_clip = VideoFileClip(file_path)
                    clips = []
                    for scene in scenes:
                        try:
                            start = float(scene["start"])
                            end = float(scene["end"])
                            if start < end:
                                clip = video_clip.subclipped(start, end)
                                if clip.duration > 0.5:
                                    clips.append(clip)
                        except Exception as e:
                            st.warning(f"Scene skipped: {e}")

                    if clips:
                        final_clip = concatenate_videoclips(clips)
                        final_path = "recap_video.mp4"
                        final_clip.write_videofile(final_path, codec="libx264")
                        with open(final_path, "rb") as f:
                            st.video(f.read())
                    else:
                        st.warning("No valid scenes to stitch.")
                except Exception as e:
                    st.error("Recap video playback failed.")
                    st.exception(e)
