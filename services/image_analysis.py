"""Gemini Vision helpers for suggesting lost/found item details.

Images are analysed in memory and are not uploaded to Supabase or stored by
this application. The user must review every suggestion before submission.
"""

import json
import os
import re
import time

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MODEL_NAMES = ("gemini-3.8-flash", "gemini-3.5-flash-lite")

CATEGORY_OPTIONS = [
    "Bag", "Bottle", "Mobile Phone", "Wallet", "Laptop",
    "Documents", "Keys", "Clothing", "Jewellery", "Watch",
    "Books", "Electronics", "Accessories", "Other"
]


def _get_api_key():
    """Read Gemini key from Streamlit secrets or environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            key = None

    if not key:
        raise ValueError(
            "Gemini API key is not configured. Add GEMINI_API_KEY "
            "to Streamlit Community Cloud > App settings > Secrets."
        )
    return str(key).strip()


def _extract_json(text):
    """Parse JSON even if a model wraps it in a Markdown code fence."""
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^\x60{3}(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\x60{3}$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("Gemini returned an unreadable analysis response.")
        return json.loads(match.group(0))


def analyse_item_image(image_bytes, mime_type):
    """Return editable item suggestions from a JPEG, PNG or WebP image."""
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Please upload a JPG, PNG or WEBP image.")

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("Image size must be 5 MB or smaller.")

    try:
        with Image.open(__import__("io").BytesIO(image_bytes)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValueError("The uploaded file is not a valid image.")

    client = genai.Client(
        api_key=_get_api_key(),
        http_options=types.HttpOptions(timeout=30000)
    )

    prompt = """
You are assisting a lost-and-found reporting application.
Inspect the uploaded item photograph and return ONLY a valid JSON object
with these exact keys:
{
  "category": "one best category",
  "color": "main visible color or empty string",
  "description": "short factual description of the visible item",
  "features": ["visible distinctive feature 1", "visible feature 2"],
  "confidence": "high, medium, or low"
}

Allowed categories:
Bag, Bottle, Mobile Phone, Wallet, Laptop, Documents, Keys, Clothing,
Jewellery, Watch, Books, Electronics, Accessories, Other.

Rules:
- Describe only details clearly visible in the photograph.
- Do not infer ownership, brand, model, contents, identity, location, or value.
- Do not guess hidden details. Use Other if the category is unclear.
- Keep description concise and useful for a lost-and-found report.
- Return no markdown and no extra commentary.
"""

    request_contents = [
        prompt,
        types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )
    ]
    request_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
        max_output_tokens=400
    )

    # Keep the user-facing wait bounded: one request per model. The SDK
    # already has built-in retry handling for transient API failures.
    response = None
    last_error = None
    for model_name in MODEL_NAMES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=request_contents,
                config=request_config
            )
            break
        except Exception as error:
            last_error = error
            error_text = str(error).lower()
            is_temporary = any(
                marker in error_text
                for marker in ("503", "429", "500", "502", "504", "unavailable", "resource_exhausted", "deadline")
            )
            if not is_temporary:
                raise

    if response is None:
        raise RuntimeError(
            "Gemini is temporarily busy. Please wait 30–60 seconds and try again. "
            "No report has been submitted."
        ) from last_error

    result = _extract_json(response.text or "")

    category = str(result.get("category", "Other")).strip()
    if category not in CATEGORY_OPTIONS:
        category = "Other"

    color = str(result.get("color", "")).strip()[:80]
    description = str(result.get("description", "")).strip()[:500]

    features = result.get("features", [])
    if not isinstance(features, list):
        features = []
    features = [
        str(feature).strip()[:120]
        for feature in features
        if str(feature).strip()
    ][:6]

    confidence = str(result.get("confidence", "low")).lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    return {
        "category": category,
        "color": color,
        "description": description,
        "features": features,
        "confidence": confidence
    }
