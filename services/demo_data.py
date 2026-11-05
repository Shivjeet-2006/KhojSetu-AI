"""Preloaded, clearly labelled demo fixtures for KhojSetu AI."""

import streamlit as st


@st.cache_data
def get_demo_image_suggestions():
    """Return a cached sample response for presentations.

    This fixture is NOT generated from the user's uploaded image and must
    never be presented as a live Gemini result.
    """
    return {
        "category": "Bottle",
        "color": "Blue",
        "description": "Reusable blue water bottle with a screw-on lid",
        "features": [
            "Cylindrical bottle body",
            "Silver-coloured lid",
            "Small mark near the lower side"
        ],
        "confidence": "medium"
    }
