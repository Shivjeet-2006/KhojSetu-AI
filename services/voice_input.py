import hashlib
import os
import tempfile
import streamlit as st

from services.prisma_stt import transcribe_audio


def voice_to_text(widget_key_suffix=""):
    """Capture speech and return its transcript for the report description."""

    transcript_key = f"voice_transcript_{widget_key_suffix}"
    language_key = f"voice_language_{widget_key_suffix}"
    audio_key = f"voice_audio_{widget_key_suffix}"

    if transcript_key not in st.session_state:
        st.session_state[transcript_key] = ""

    st.subheader("Voice input")

    language = st.selectbox(
        "Recording language",
        ["Hindi", "English", "Marathi"],
        key=language_key
    )

    language_codes = {
        "Hindi": "hi-IN",
        "English": "en-IN",
        "Marathi": "mr-IN"
    }

    audio_file = st.audio_input(
        "Record a description",
        sample_rate=16000,
        key=audio_key
    )

    processed_key = f"processed_audio_hash_{widget_key_suffix}"
    if audio_file is not None:
        audio_bytes = audio_file.getvalue()
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()

        # Streamlit reruns the script after interactions. Avoid sending the
        # same recorded clip to the transcription service more than once.
        if st.session_state.get(processed_key) == audio_hash:
            return st.session_state[transcript_key]

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            with st.spinner("Converting speech to text..."):
                result = transcribe_audio(
                    temp_path,
                    language_code=language_codes[language]
                )

            transcript = (
                result.get("transcript")
                or result.get("text")
                or ""
            )

            st.session_state[processed_key] = audio_hash

            if transcript:
                st.session_state[transcript_key] = transcript
                st.success("Voice description is ready.")
                st.text_area(
                    "Recognised text",
                    value=transcript,
                    height=90,
                    disabled=True,
                    key=f"voice_preview_{widget_key_suffix}"
                )
            else:
                st.warning("No speech was detected. Please try recording again.")

        except Exception as error:
            st.error(f"Voice transcription failed: {error}")

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    return st.session_state[transcript_key]
