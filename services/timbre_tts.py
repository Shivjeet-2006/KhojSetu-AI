
import os
import io
import soundfile as sf
from transformers import pipeline

_tts = None


def get_tts():
    global _tts

    if _tts is None:
        if not os.getenv("GNANI_API_KEY"):
            raise ValueError("GNANI_API_KEY is not configured.")

        _tts = pipeline(
            "text-to-speech",
            model="gnani/gnani",
            trust_remote_code=True
        )

    return _tts


def generate_speech(text, language="hi-IN", voice="Nalini"):

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    tts = get_tts()

    result = tts(
        text,
        voice=voice,
        model="timbre-v2.5",
        language=language,
        tts_mode="rest",
        sample_rate=16000,
        container="wav",
        encoding="linear_pcm"
    )

    audio_buffer = io.BytesIO()

    sf.write(
        audio_buffer,
        result["audio"],
        result["sampling_rate"],
        format="WAV"
    )

    audio_buffer.seek(0)

    return audio_buffer
