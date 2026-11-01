
import os
import tempfile
import streamlit as st

from services.prisma_stt import transcribe_audio


def voice_to_text():

    st.subheader("🎙️ Report using your voice")

    language = st.selectbox(
        "Choose your language",
        ["hi-IN", "mr-IN", "en-IN"]
    )

    audio_file = st.audio_input(
        "Record your lost or found item description"
    )

    if audio_file is not None:

        st.audio(audio_file)

        if st.button("Convert Speech to Text"):

            if not os.getenv("GNANI_API_KEY"):
                st.error("Gnani API key is missing.")
                return None

            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as temp:
                    temp.write(audio_file.getvalue())
                    temp_path = temp.name

                with st.spinner("Transcribing your voice..."):

                    result = transcribe_audio(
                        temp_path,
                        language_code=language
                    )

                transcript = result.get("text", "")

                if transcript:
                    st.success("Speech converted successfully!")
                    st.write("Your description:")
                    st.info(transcript)
                    return transcript

                st.warning("No speech detected.")

            except Exception as error:
                st.error(f"Transcription failed: {error}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    return None
