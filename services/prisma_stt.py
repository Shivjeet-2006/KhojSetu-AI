import os
import requests


def transcribe_audio(audio_path, language_code="hi-IN"):

    import streamlit as st

api_key = os.getenv("GNANI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GNANI_API_KEY"]
    except Exception:
        api_key = None

    if not api_key:
        raise ValueError("GNANI_API_KEY is not configured.")

    url = "https://api.vachana.ai/stt/v3"

    headers = {
        "X-API-Key-ID": api_key
    }

    data = {
        "language_code": language_code,
        "preferred_language": language_code,
        "format": "transcribe",
        "itn_native_numerals": "true"
    }

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
