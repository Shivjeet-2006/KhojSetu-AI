
import os
import tempfile
import streamlit as st

from services.prisma_stt import transcribe_audio


def voice_to_text():

    if "voice_transcript" not in st.session_state:
        st.session_state.voice_transcript = ""

    st.subheader("🎤 Voice Input")

    language = st.selectbox(
        "Select Language",
        ["Hindi", "English", "Marathi"],
        key="voice_language"
    )

    language_codes = {
        "Hindi": "hi-IN",
        "English": "en-IN",
        "Marathi": "mr-IN"
    }

    audio_file = st.audio_input(
        "Record your voice",
        sample_rate=16000
    )

    if audio_file is not None:
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as temp_file:
                temp_file.write(audio_file.getvalue())
                temp_path = temp_file.name

            with st.spinner("Converting voice to text..."):
                result = transcribe_audio(
                    temp_path,
                    language_code=language_codes[language]
                )

            transcript = (
                result.get("transcript")
                or result.get("text")
                or ""
            )

            if transcript:
                st.session_state.voice_transcript = transcript
                st.success("Voice converted successfully!")
                st.info(transcript)
            else:
                st.warning("No speech detected. Try recording again.")

        except Exception as error:
            st.error(f"Voice transcription failed: {error}")

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    return st.session_state.voice_transcript
