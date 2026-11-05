"""Supabase-backed database helpers for KhojSetu AI."""

import os
import streamlit as st
from supabase import create_client


@st.cache_resource
def get_supabase_client():
    """Create and cache the Supabase client for this Streamlit session."""
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    except Exception:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Missing SUPABASE_URL or SUPABASE_KEY. Add both in "
            "Streamlit app Settings > Secrets."
        )

    return create_client(url, key)


def _show_supabase_error(exc):
    """Show useful API error fields without exposing connection secrets."""
    error_data = exc.args[0] if getattr(exc, "args", None) else None

    if isinstance(error_data, dict):
        code = error_data.get("code", "")
        message = error_data.get("message", str(exc))
        details = error_data.get("details", "")
        hint = error_data.get("hint", "")
    else:
        code = getattr(exc, "code", "")
        message = getattr(exc, "message", "") or str(exc)
        details = getattr(exc, "details", "")
        hint = getattr(exc, "hint", "")

    st.error("KhojSetu AI could not connect to the Supabase reports table.")
    st.write("**Supabase error code:**", code or "Not provided")
    st.write("**Message:**", message or "No message provided")
    if details:
        st.write("**Details:**", details)
    if hint:
        st.write("**Hint:**", hint)
    st.info(
        "Please share these error fields (code, message, details and hint). "
        "Do not share your Supabase URL or API key."
    )
    st.stop()


def create_tables():
    """Check that the Supabase reports table is reachable."""
    try:
        get_supabase_client().table("reports").select("id").limit(1).execute()
    except Exception as exc:
        _show_supabase_error(exc)


def add_report(report_type, description, category="",
               color="", location="", item_date="",
               identifying_details=""):
    """Insert a lost/found report and return its generated ID."""
    if report_type not in ("lost", "found"):
        raise ValueError("Report type must be lost or found.")

    payload = {
        "report_type": report_type,
        "description": description,
        "category": category,
        "color": color,
        "location": location,
        "item_date": item_date,
        "identifying_details": identifying_details,
    }

    response = (
        get_supabase_client()
        .table("reports")
        .insert(payload)
        .select("id")
        .execute()
    )

    if not response.data:
        raise RuntimeError("Supabase did not return the new report ID.")

    return response.data[0]["id"]


def get_reports(report_type=None):
    """Return reports as a list of dictionaries, newest first."""
    query = get_supabase_client().table("reports").select("*")

    if report_type:
        query = query.eq("report_type", report_type)

    response = query.order("created_at", desc=True).execute()
    return response.data or []
