
import os
import time
import requests
import streamlit as st


def get_api_key():

    key = os.getenv("GNANI_API_KEY")

    if not key:
        try:
            key = st.secrets["GNANI_API_KEY"]
        except Exception:
            key = None

    if not key:
        raise ValueError("Gnani API key is missing.")

    return key


def transcribe_audio(audio_path, language_code="hi-IN"):

    url = "https://api.vachana.ai/stt/v3"

    headers = {
        "X-API-Key-ID": get_api_key()
    }

    data = {
        "language_code": language_code,
        "preferred_language": language_code,
        "format": "transcribe",
        "itn_native_numerals": "true"
    }

    for attempt in range(2):

        try:
            with open(audio_path, "rb") as audio:

                response = requests.post(
                    url,
                    headers=headers,
                    data=data,
                    files={
                        "audio_file": (
                            os.path.basename(audio_path),
                            audio,
                            "audio/wav"
                        )
                    },
                    timeout=120
                )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException:

            if attempt == 0:
                time.sleep(5)
            else:
                raise

    return {}
