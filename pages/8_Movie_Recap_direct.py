import streamlit as st
import os
import json
from groq import Groq
from gtts import gTTS
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
import tempfile
import time

client = Groq(api_key="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")




@st.cache_data
def load_transcript_text(uploaded_file=None):
    file_path = os.path.join("files", "smart_recap_transcript.json")
    # If no file uploaded, fallback to default behavior
    if uploaded_file is None:
        if not os.path.isfile(file_path):
            st.error("Transcript file not found.")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    # If filename is videoplayback_1.mp4, use local transcript
    if uploaded_file.name == "videoplayback_1.mp4":
        if not os.path.isfile(file_path):
            st.error("Transcript file not found.")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Call Groq API to get transcript using whisper-large-v3-turbo
        st.info("Transcribing audio using Groq Whisper API...")
        try:
            with open(os.path.join("files", uploaded_file.name), "rb") as audio_file:
                audio_bytes = audio_file.read()
            transcription = client.audio.transcriptions.create(
                file=(uploaded_file.name, audio_bytes),
                model="whisper-large-v3",
                 prompt="I am providing movie file and I need to provide words an segment details with timestamp. The response should only be in JSON format only.",
                temperature=0,
                response_format="verbose_json",
                timestamp_granularities= ["word", "segment"],
            )
            transcript = transcription.words
            # Optionally save transcript for later use
            transcript_file_path = os.path.join("files", f"{uploaded_file.name}_transcript.json")
            if not os.path.isfile(transcript_file_path):
                with open(transcript_file_path, "w", encoding="utf-8") as f:
                            json.dump(transcript, f, ensure_ascii=False, indent=2)
            return transcript
        except Exception as e:
            st.error(f"Failed to transcribe audio: {e}")
            return None



STEPS = [
    "Transcript the movie.",
    "Generating Voice Over Narration.",
    "Clipping Video.",
    "Generating Recap with Voice Over."
]

def show_modal_progress(current_step):
    steps_html = ""
    for idx, step in enumerate(STEPS):
        if idx < current_step:
            steps_html += (
                f'<div class="progress-step">'
                f'  <div class="progress-circle completed"></div>'
                f'  <div class="progress-label">{step}</div>'
                f'</div>'
            )
        elif idx == current_step:
            steps_html += (
                f'<div class="progress-step active">'
                f'  <div class="progress-circle active">{idx+1}</div>'
                f'  <div class="progress-label">{step}</div>'
                f'</div>'
            )
        else:
            steps_html += (
                f'<div class="progress-step">'
                f'  <div class="progress-circle">{idx+1}</div>'
                f'  <div class="progress-label">{step}</div>'
                f'</div>'
            )
    modal_html = f"""
    <style>
    .modal {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;
    }}
    .modal-content {{
        background: white;
        padding: 2.5rem 3.5rem;
        border-radius: 24px;
        text-align: center;
        width: 100%;
        max-width: 700px;
        margin: 2rem;
        box-shadow: 0 8px 40px #2225, 0 1.5px 8px #2222;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .progress-title {{
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2.5rem;
        color: #2d3548;
        letter-spacing: 0.5px;
    }}
    .progress-steps {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 2.5rem;
        position: relative;
        min-height: 140px;
        width: 100%;
    }}
    .progress-bar-bg {{
        position: absolute;
        top: 38px;
        left: 6%;
        width: 88%;
        height: 6px;
        background: #e0e0e0;
        z-index: 1;
        border-radius: 3px;
    }}
    .progress-bar-fill {{
        position: absolute;
        top: 38px;
        left: 6%;
        height: 6px;
        background: #1a4fb4;
        z-index: 2;
        border-radius: 3px;
        transition: width 1s;
        width: 100%;
    }}
    .progress-step {{
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
        z-index: 3;
        min-width: 120px;
    }}
    .progress-step.active {{
        background: rgba(26,79,180,0.07);
        border-radius: 16px;
        box-shadow: 0 2px 16px #1a4fb41a;
        padding-bottom: 18px;
    }}
    .progress-circle {{
        width: 54px; height: 54px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.45rem; font-weight: 600;
        border: 3px solid #bdbdbd; background: #f5f5f5; color: #bdbdbd;
        margin-bottom: 0.7rem;
        margin-top: 0.2rem;
        box-shadow: 0 2px 8px #1a4fb41a;
        transition: background 0.3s, border 0.3s, color 0.3s;
    }}
    .progress-circle.active {{
        background: #1a4fb4; border-color: #1a4fb4; color: #fff;
        font-size: 1.55rem;
        box-shadow: 0 4px 16px #1a4fb433;
    }}
    .progress-circle.completed {{
        background: #1a4fb4; border-color: #1a4fb4; color: #fff;
        font-size: 1.55rem;
        position: relative;
    }}
    .progress-circle.completed::before {{
        content: '\\2713';
        font-size: 1.5rem;
        font-weight: 600;
        color: #fff;
        display: block;
        position: absolute;
        left: 0; right: 0; top: 0; bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .progress-label {{
        font-size: 1.08rem;
        color: #222;
        margin-top: 0.2rem;
        font-weight: 400;
        text-align: center;
        min-width: 120px;
        letter-spacing: 0.1px;
        line-height: 1.3;
    }}
    </style>
    <div class="modal">
      <div class="modal-content">
        <div class="progress-title">Your request is being processed, Please wait</div>
        <div class="progress-steps">
            <div class="progress-bar-bg"></div>
            <div class="progress-bar-fill"></div>
            {steps_html}
        </div>
      </div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)

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

    st.markdown("### 📋 Uploaded Files")
    st.table({"Serial No.": [1], "File Name": [uploaded_file.name]})

    if "recap_step" not in st.session_state:
        st.session_state["recap_step"] = 0
    if "recap_in_progress" not in st.session_state:
        st.session_state["recap_in_progress"] = False
    if "recap_start_time" not in st.session_state:
        st.session_state["recap_start_time"] = None

    if st.button("🚀 Generate Recap") or st.session_state["recap_in_progress"]:
        if not st.session_state["recap_in_progress"]:
            st.session_state["recap_in_progress"] = True
            st.session_state["recap_step"] = 0
            st.session_state["recap_start_time"] = time.time()
            st.rerun()

        # Show modal only if process is not finished (step < 4)
        if st.session_state["recap_step"] < 4:
            show_modal_progress(st.session_state["recap_step"])

        # Step 0: Transcript
        if st.session_state["recap_step"] == 0:
            transcript_text = load_transcript_text(uploaded_file)
            st.session_state["transcript_text"] = transcript_text
            st.session_state["recap_step"] += 1
            st.rerun()

        # Step 1: Generate Summary & VoiceOver
        elif st.session_state["recap_step"] == 1:
            transcript_text = st.session_state.get("transcript_text")
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a brilliant movie analysis API that performs transcript analysis with timestamp detail. Do not provide your reasoning in the Output. Output only JSON forma as given: {\"genre\": ..., \"VoiceOver\": ...}"},
                    {"role": "user", "content": f"""
                    I am sharing a complete transcript of a movie.
                    Using this transcript, generate a compelling, voice-over-style narrative recap of everything that has happened from the beginning up to [HH:MM:SS]. If no timestamp is specified, assume a full-movie recap is requested.
                    Your output must follow these rules:
                    1. Automatically determine the movie's genre (e.g., action, thriller, comedy, sci-fi, romance, horror) by analyzing the tone, events, and characters in the transcript.
                    2. Match the narration tone to the genre:
                    3. Summarize only the essential plot points: Introduce main characters, settings, their goals, conflicts, and major events—not every line of dialogue.
                    4. Avoid spoilers beyond [HH:MM:SS]—strictly stop summarizing at that point.
                    5. Use continuous prose, as if a professional narrator were telling the story aloud. No bullet points.
                    6. Keep it under 800 words—aim for a 4-5 minute read-aloud.
                    7. Use timestamps sparingly—only if critical to the context or scene transitions.
                    8. Keep it engaging and immersive for someone who missed the first half and wants to catch up quickly before watching the rest.
                    Here is my Transcript file:
                    {transcript_text}
                    """}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=6000,
                temperature=0.6
            )
            full_response = response.choices[0].message.content
            st.session_state["full_response"] = full_response
            st.session_state["recap_step"] += 1
            st.rerun()

        # Step 2: Generate Timestampsrecap_in_progress
        elif st.session_state["recap_step"] == 2:
            full_response_json = json.loads(st.session_state.get("full_response", "{}"))
            voiceover = full_response_json.get("VoiceOver", "")
            transcript_text = st.session_state.get("transcript_text")
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a brilliant movie analysis API that maps narration to transcript timestamps. Always ensure that total voiceover duration should match the total video timestamp duration. Output only JSON with genre and visual_recap."
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
                            "4. Write description: Generate a compelling, voice-over-style narrative recap of everything that has happened within each start and end timestamp selected.\n"
                            "5. Match pacing: Ensure the total duration of selected transcript segments closely matches the voiceover duration (±5%).\n"
                            "6. If the voiceover is shorter than the transcript, prioritize segments rich in meaning and avoid filler.\n"
                            "7. Stick to JSON: Output only the JSON structure, no additional text or explanation.\n\n"
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
            st.session_state["recap_step"] += 1
            st.rerun()

        # Step 3: Generate Recap Video and Overlay VoiceOver
        elif st.session_state["recap_step"] == 3:
            output = st.session_state.get("visual_recap", {})
            scenes = output.get("visual_recap", [])
            video_clip = VideoFileClip(file_path)
            clips = []
            for idx, scene in enumerate(scenes):
                start = float(scene["start"])
                end = float(scene["end"] + 0.5)
                if start < end:
                    clip = video_clip.subclipped(start, end)
                    if clip.duration > 0.5:
                        clips.append(clip)
            final_clip = concatenate_videoclips(clips)
            full_response_json = json.loads(st.session_state.get("full_response", "{}"))
            voiceover_text = full_response_json.get("VoiceOver", "")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_fp:
                gTTS(voiceover_text).write_to_fp(tts_fp)
                tts_fp.flush()
                tts_path = tts_fp.name
            voiceover_audio = AudioFileClip(tts_path)
            if voiceover_audio.duration > final_clip.duration:
                voiceover_audio = voiceover_audio.subclipped(0, final_clip.duration)
            final_video = final_clip.with_audio(voiceover_audio)
            output_path = "recap_video_voiceover.mp4"
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            final_video.close()
            final_clip.close()
            voiceover_audio.close()
            video_clip.close()
            st.session_state["recap_step"] += 1
            st.rerun()

        # Step 4: Show Result and Hide Modal after 10 seconds
        elif st.session_state["recap_step"] == 4:
            # Hide modal after 10 seconds or immediately if done
            if time.time() - st.session_state["recap_start_time"] < 10:
                show_modal_progress(3)
                st.markdown("### 🎬 Recap Video with VoiceOver")
                with open("recap_video_voiceover.mp4", "rb") as video_file:
                    st.video(video_file.read())
                time.sleep(10 - (time.time() - st.session_state["recap_start_time"]))
            else:
                st.markdown("### 🎬 Recap Video with VoiceOver")
                with open("recap_video_voiceover.mp4", "rb") as video_file:
                    st.video(video_file.read())
            # Reset state for next run
            st.session_state["recap_in_progress"] = False
            st.session_state["recap_step"] = 0
            st.session_state["recap_start_time"] = None