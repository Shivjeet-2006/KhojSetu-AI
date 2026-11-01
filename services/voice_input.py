
import os
import tempfile
import streamlit as st

from services.prisma_stt import transcribe_audio


def voice_to_text():

    if "voice_transcript" not in st.session_state:
        st.session_state.voice_transcript = ""

    st.subheader("🎙️ Report using your voice")

    language = st.selectbox(
        "Choose your language",
        ["hi-IN", "mr-IN", "en-IN"]
    )

    audio_file = st.audio_input(
        "Record your item description",
        sample_rate=16000
    )

    if audio_file is not None:

        st.audio(audio_file)

        if st.button("Convert Speech to Text"):

            api_key = os.getenv("GNANI_API_KEY")

            if not api_key:
                try:
                    api_key = st.secrets["GNANI_API_KEY"]
                except Exception:
                    api_key = None

            if not api_key:
                st.error("Gnani API key is missing.")
                return st.session_state.voice_transcript

            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False
                ) as temp:
                    temp.write(audio_file.getvalue())
                    temp_path = temp.name

                with st.spinner("Converting speech..."):

                    result = transcribe_audio(
                        temp_path,
                        language_code=language
                    )

                transcript = (
                    result.get("transcript")
                    or result.get("text")
                    or ""
                )

                if transcript:
                    st.session_state.voice_transcript = transcript
                    st.success("Transcription successful!")
                    st.info(transcript)
                else:
                    st.warning("No speech detected.")

            except Exception as error:
                st.error(f"Transcription failed: {error}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    return st.session_state.voice_transcript
