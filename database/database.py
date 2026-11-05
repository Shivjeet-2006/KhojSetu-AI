"""Supabase-backed database helpers for KhojSetu AI."""

import os
from urllib.parse import urlsplit, urlunsplit

import streamlit as st
from supabase import create_client


def _read_secret(name):
    try:
        return st.secrets.get(name) or os.getenv(name)
    except Exception:
        return os.getenv(name)


@st.cache_resource
def get_supabase_client():
    """Create and cache a Supabase client using the project root URL."""
    raw_url = _read_secret("SUPABASE_URL")
    key = _read_secret("SUPABASE_KEY")

    if not raw_url or not key:
        raise RuntimeError(
            "Missing SUPABASE_URL or SUPABASE_KEY. Add both in "
            "Streamlit app Settings > Secrets."
        )

    raw_url = raw_url.strip().rstrip("/")
    parsed = urlsplit(raw_url)

    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise RuntimeError(
            "SUPABASE_URL must be the project root URL, for example "
            "https://your-project-ref.supabase.co"
        )

    # The Supabase Python client adds /rest/v1 itself. Remove it if the
    # copied URL already includes that suffix, preventing a duplicated path.
    path = parsed.path.rstrip("/")
    if path.endswith("/rest/v1"):
        path = path[:-len("/rest/v1")]
    if path:
        raise RuntimeError(
            "SUPABASE_URL contains an unexpected path. Use only the project "
            "root URL (https://your-project-ref.supabase.co), without "
            "/rest/v1, /dashboard, or any other path."
        )

    project_root_url = urlunsplit(
        (parsed.scheme, parsed.netloc, "", "", "")
    )
    return create_client(project_root_url, key)


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
        "Share these error fields only. Never share your Supabase URL or API key."
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
