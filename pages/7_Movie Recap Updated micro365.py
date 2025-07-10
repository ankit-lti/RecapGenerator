import streamlit as st
import os
import json
from groq import Groq
from gtts import gTTS
import base64
from moviepy import *
import time
import threading
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

client = Groq(api_key="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")  # Replace with your actual key or env var

def detect_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30.0))
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    return [(start.get_seconds(), end.get_seconds()) for start, end in scene_list]

@st.cache_data
def load_transcript_text(uploaded_file=None):
    file_path = os.path.join("files", "Minute Time Machine_ _ DUST.mp4_transcript.json")
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
            transcript = transcription.text
            # Optionally save transcript for later use
            transcript_file_path = os.path.join("files", f"{uploaded_file.name}_transcript.json")
            if not os.path.isfile(transcript_file_path):
                with open(transcript_file_path, "w", encoding="utf-8") as f:
                            json.dump(transcript, f, ensure_ascii=False, indent=2)
            return transcript
        except Exception as e:
            st.error(f"Failed to transcribe audio: {e}")
            return None

def show_auto_modal_progress():
    steps = [
        "Transcript the movie.",
        "Generating Voice Over Narration.",
        "Clipping Video.",
        "Generating Recap with Voice Over."
    ]
    modal_html_base = """
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .modal {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;
        animation: fadeIn 0.5s;
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
        animation: fadeIn 0.7s;
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
            <div class="progress-bar-fill" style="width: {bar_fill_width}%;"></div>
            {steps_html}
        </div>
      </div>
    </div>
    """

    modal_placeholder = st.empty()
    total_steps = len(steps)
    # Loop through steps, showing each as active, then finally all as completed
    for i in range(total_steps + 1):
        steps_html = ""
        for j, step in enumerate(steps):
            if i == total_steps:  # Final state: all completed
                circle_class = "progress-circle completed"
                step_class = "progress-step"
                circle_content = ""
            elif j < i:
                circle_class = "progress-circle completed"
                step_class = "progress-step"
                circle_content = ""
            elif j == i:
                circle_class = "progress-circle active"
                step_class = "progress-step active"
                circle_content = str(j+1)
            else:
                circle_class = "progress-circle"
                step_class = "progress-step"
                circle_content = str(j+1)
            steps_html += (
                f'<div class="{step_class}">'
                f'  <div class="{circle_class}">{circle_content}</div>'
                f'  <div class="progress-label">{step}</div>'
                f'</div>'
            )
        # Progress bar fill
        if total_steps == 1:
            bar_fill_width = 100
        else:
            bar_fill_width = (i) / (total_steps) * 100
        modal_html = modal_html_base.format(steps_html=steps_html, bar_fill_width=bar_fill_width)
        modal_placeholder.markdown(modal_html, unsafe_allow_html=True)
        time.sleep(1)
    # Pause briefly on all-completed state, then close modal
    time.sleep(0.7)
    modal_placeholder.empty()

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


    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1,1])
    generate_recap = col1.button("🚀 Generate Recap")
    play_audio = col2.button("🔊 Play VoiceOver")
    play_video = col3.button("🎞️ Play Recap Video")
    voice_over_video = col4.button("🎤 VoiceOver Video")
    scenes_detect = col5.button("🔍 Detect Scenes")
    if generate_recap:
        st.info("Generating full recap pipeline...")
        # Show modal progress window for a fixed time, then continue processing in background        
        try:
            # --- STEP 1: Generate Summary ---
            #transcript_text = load_transcript_text()
            transcript_text = load_transcript_text(uploaded_file)
            if not transcript_text:
                st.warning("Transcript not available.")
            else:
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
                st.success("✅ Summary generated")
                st.markdown("### 🗣️ Recap VoiceOver")
                st.markdown(json.loads(full_response).get("VoiceOver", ""))

            # --- STEP 2: Generate Timestamps ---
            full_response = json.loads(st.session_state.get("full_response", "{}"))
            voiceover = full_response.get("VoiceOver", "")

            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
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
            st.markdown("### 🎞️ Visual Recap Segments")
            st.json(output)

        except Exception as e:
            st.error("Recap generation failed")
            st.exception(e)

    if play_audio and "full_response" in st.session_state:
        try:
            #voiceover_text = json.loads(st.session_state["full_response"]).get("VoiceOver", "")
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
                        clip = video_clip.subclipped(start, end)
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

    # ...existing code...


    if voice_over_video:
        try:
            # 1. Get the voiceover text and generate TTS audio
            voiceover_text = json.loads(st.session_state["full_response"]).get("VoiceOver", "")
            if not voiceover_text:
                st.warning("VoiceOver text not found.")
            else:
                tts = gTTS(voiceover_text)
                tts.save("voiceover_temp.mp3")

                # 2. Load the recap video and the TTS audio
                video_clip = VideoFileClip("recap_video.mp4")
                voiceover_audio = AudioFileClip("voiceover_temp.mp3")

                # 3. Set the audio of the video to the TTS audio (suppress original audio)
                # If the voiceover is shorter than the video, loop or pad as needed
                if voiceover_audio.duration < video_clip.duration:
                    # Optionally, you can loop or pad the audio; here we just set it as is
                    final_audio = voiceover_audio
                else:
                    final_audio = voiceover_audio.subclipped(0, video_clip.duration)

                final_video = video_clip.with_audio(final_audio)
                output_path = "recap_video_voiceover.mp4"
                final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
                final_video.close()
                video_clip.close()
                voiceover_audio.close()

                # 4. Display the final video in Streamlit
                with open(output_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    st.markdown("### 🎬 Recap Video with VoiceOver")
                    st.video(video_bytes)
        except Exception as e:
            st.error("Failed to overlay voiceover on video.")
            st.exception(e)

    # Scene detection button
    if scenes_detect:
        try:
            # Load transcript text
            transcript_text = load_transcript_text(uploaded_file)
            if not transcript_text:
                st.warning("Transcript not available.")
            else:
                # Detect scenes using Groq API
                scene_boundaries = detect_scenes(file_path)
                st.session_state["scene_boundaries"] = scene_boundaries
                st.write(f"Detected {len(scene_boundaries)} scenes.")

                # Show detected scenes
                st.markdown("### 📽️ Detected Scenes")
                st.json(scene_boundaries)

                response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                  messages=[
                {
                    "role": "system",
                "content": (
                    "You are a brilliant transcript analysis engine. Transcript segment details and scene boundaries will be shared with you. "
                    "Your task is to extract only the most meaningful segments that will be used to generate a recap. "
                    "Do not provide your reasoning. Output only JSON in the format: {\"genre\": ..., \"visual_recap\": ...}"
                        )
                },
                {
                    "role": "user",
                    "content": f"""
                    TASK:
                    1. Analyze the transcript and scene boundaries.
                    2. Select only segments that contain major plot developments, emotional turning points, character introductions, decisions, or conflicts.
                    3. Exclude filler dialogue, transitions, or repetitive scenes.
                    4. If a scene contains multiple lines, summarize them into one meaningful segment if possible.
                    5. Limit output to the top 10-15 most meaningful segments.
                    6. calculate the Total timestamp (start and end )length of all segments should be less than 90 seconds.
                    7. Each segment should include 'start', 'end', and 'description'.
                    8. Output only JSON format.

                    Scene Boundaries: {scene_boundaries}
                    Transcript: {transcript_text}
                    """
        }
    ],
                response_format={"type": "json_object"},
                max_completion_tokens=6000,
                temperature=0.6
            )
            output = json.loads(response.choices[0].message.content)
            st.session_state["visual_recap"] = output  # Store only the list of scenes
            st.json(output)
            st.info("Scene detection completed successfully.")
            st.info("Now you can use the detected segment details to generate the voiceover")
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a brilliant movie analysis API that performs transcript analysis with timestamp detail. Create Voiceover narration based on the important segment provided. Do not provide your reasoning in the Output. Output only JSON forma as given: {\"genre\": ..., \"VoiceOver\": ...}"},
                    {"role": "user", "content": f"""
                        I am sharing a complete transcript of a movie and evenful segment details.
                        Analyze the segment details provided and generate a compelling, cinematic voice-over-style narrative recap of everything that has happened from the beginning up to [HH:MM:SS]. 
                        If no timestamp is specified, assume a full-movie recap is requested.
                        Your output must follow these rules:
                        1. Automatically determine the movie's genre (e.g., action, thriller, comedy, sci-fi, romance, horror) by analyzing the tone, events, and characters in the transcript.
                        2. Match the narration tone to the genre:
                        3. Summarize only the essential plot points: Introduce main characters, settings, their goals, conflicts, and major events—not every line of dialogue.
                        4. Identify the names of main characters from the transcript segments and use them consistently in the voiceover narration.
                        5. Avoid using generic terms like “the protagonist”, “someone”, or “the main character”.
                        6. Use continuous prose, as if a cinematic narrator is guiding the viewer through the story. Refer to characters by name. No bullet points.
                        7. Use timestamps sparingly—only if critical to the context or scene transitions.
                        8. Keep it engaging and immersive for someone who missed the first half and wants to catch up quickly before watching the rest.
                        9. End the voiceover with a confident, descriptive summary of what has happened so far. 
                        Do not end with a question, teaser, or speculative statement. 
                        This is a recap, not a preview or trailer.
                        10. Please ensure the generated voice-over narration is approximately N seconds long, which is the same length as the trailer.
                        Use approximately 2.5 words per second to guide your word count (e.g., 150 seconds trailer = ~375 words).
                        11. Output only JSON format.
                        Important segments : {output}
                        Transcript: {transcript_text}
                        """
                    }
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=6000,
                temperature=0.8
            )
            full_response = response.choices[0].message.content
            full_response_json = json.loads(full_response)

            final_response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a brilliant movie analysis API that performs segment analysis with timestamp detail and voiceover. Do not provide your reasoning in the Output. Output only JSON forma as given: {\"genre\": ..., \"visual_recap\":[{\"start\":...,\"end\":...}], \"VoiceOver\": ...}"},
                    {"role": "user", "content": f"""
                        I am sharing a eventful timestamp and recap voiceover of a movie and evenful segment details.
                        Your output must follow these rules:
                        1. If any segment exceeds the voiceover duration, trim it to fit.
                        2. Total duration of all segements will be calculated based on this formulae. total_duration +=end-start for each timestamp.
                        3. Compare both video timestamp duration and voiceover duration should match. Use formulae to calculate the total duration of all segments and compare it with voiceover duration 2.5 words per second.
                        4. Store and display only the aligned recap.   
                        5. Trim or drop segments beyond the voiceover end.
                        6. Output only JSON format.
                        voiceover : {full_response_json}
                        timestamp: {output}
                        """
                    }
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=6000,
                temperature=0.5
            )

            final_response_json = json.loads(final_response.choices[0].message.content)
            st.markdown("### 🗣️ Final Response")
            st.markdown(final_response_json)
            st.session_state["full_response"] = json.dumps(full_response_json)
            #st.markdown("### 🗣️ Recap VoiceOver")
            #st.markdown(full_response_json.get("VoiceOver", ""))
        except Exception as e:
            st.error("Scene detection failed")
            st.exception(e)