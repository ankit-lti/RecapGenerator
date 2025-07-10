import streamlit as st
import os
import json
from groq import Groq
from gtts import gTTS
import base64
from moviepy import VideoFileClip, concatenate_videoclips

client = Groq(api_key="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")  # Replace with your actual key or env var

@st.cache_data
def load_transcript_text():
    file_path = os.path.join("files", "smart_recap_transcript.json")
    if not os.path.isfile(file_path):
        st.error("Transcript file not found.")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

st.set_page_config(page_title="Smart Movie Recap", layout="centered")
st.title("🎬 Smart Recap Generator")
st.markdown("Upload a trailer and generate a narrative voice-over with matching scene timestamps.")

uploaded_file = st.file_uploader("📂 Upload a video file", type=["mp4"])
file_path = ""

if uploaded_file:
    file_path = os.path.join("files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File saved: {uploaded_file.name}")

    # Show table of uploaded files
    st.markdown("### 📋 Uploaded Files")
    st.table({"Serial No.": [1], "File Name": [uploaded_file.name]})

    col1, col2, col3 = st.columns([3, 1, 1])
    generate_recap = col1.button("🚀 Generate Recap")
    play_audio = col2.button("🔊 Play VoiceOver")
    play_video = col3.button("🎞️ Play Recap Video")

    if generate_recap:
        st.info("Generating full recap pipeline...")

        try:
            # --- STEP 1: Generate Summary ---
            transcript_text = load_transcript_text()
            if not transcript_text:
                st.warning("Transcript not available.")
            else:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a brilliant movie analysis API that performs transcript analysis with timestamp detail. Output only JSON: {\"genre\": ..., \"VoiceOver\": ...}"},
                        {"role": "user", "content": f"I have a transcript. Please summarize key plot points into a voice-over style recap and infer the genre.\nTranscript:\n{transcript_text}"}
                    ],
                    response_format={"type": "json_object"},
                    max_completion_tokens=6000,
                    temperature=0.6
                )
                full_response = response.choices[0].message.content
                st.session_state["full_response"] = full_response
                st.success("✅ Summary generated")
                st.markdown("### 🗣️ Recap VoiceOver")
                st.markdown(json.loads(full_response).get("VoiceOver", ""))

            # --- STEP 2: Generate Timestamps ---
            full_response = json.loads(st.session_state.get("full_response", "{}"))
            voiceover = full_response.get("VoiceOver", "")

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
                    }
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=8000,
                temperature=0.6
            )
            output = json.loads(response.choices[0].message.content)
            st.session_state["visual_recap"] = output
            st.markdown("### 🎞️ Visual Recap Segments")
            st.json(output)

        except Exception as e:
            st.error("Recap generation failed")
            st.exception(e)

    if play_audio and "full_response" in st.session_state:
        try:
            voiceover_text = json.loads(st.session_state["full_response"]).get("VoiceOver", "")
            if voiceover_text:
                tts = gTTS(voiceover_text)
                tts.save("voiceover.mp3")

                with open("voiceover.mp3", "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    audio_html = f"""
                        <audio autoplay controls>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        </audio>
                    """
                    st.markdown("### ▶️ VoiceOver Playback")
                    st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.warning("VoiceOver text not found.")
        except Exception as e:
            st.error("Failed to generate or play voiceover.")
            st.exception(e)

    if play_video and "visual_recap" in st.session_state:
        try:
            scenes = st.session_state.get("visual_recap", {}).get("visual_recap", [])
            video_clip = VideoFileClip(file_path)
            clips = []

            for idx, scene in enumerate(scenes):
                try:
                    st.write(f"Scene {idx + 1} raw: {scene}")
                    start = float(scene["start"])
                    end = float(scene["end"] + 0.5)
                    if start < end:
                        clip = video_clip.subclip(start, end)
                        if clip.duration > 0.5:
                           clips.append(clip)
                        else:
                            st.warning(f"Clip {idx+1} too short.")
                    else:
                      st.warning(f"Clip {idx + 1} has invalid timing: start={start}, end={end}")
                except Exception as e:
                    st.error(f"Clip {idx + 1} failed: {e}")

            if clips:
                final_clip = concatenate_videoclips(clips)
                final_output_path = "recap_video.mp4"
                final_clip.write_videofile(final_output_path, codec="libx264")
                final_clip.close()
                video_clip.close()

                with open(final_output_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)
            else:
                st.warning("No valid timestamp segments found to create video.")
        except Exception as e:
            st.error("Failed to generate or play recap video.")
            st.exception(e)
