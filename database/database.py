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
            "Supabase connection details are missing. Add SUPABASE_URL "
            "and SUPABASE_KEY in Streamlit app Settings > Secrets."
        )

    return create_client(url, key)


def create_tables():
    """
    The reports table is created in the Supabase SQL Editor.
    This function checks the connection when the app starts.
    """
    try:
        get_supabase_client().table("reports").select("id").limit(1).execute()
    except Exception as exc:
        raise RuntimeError(
            "Could not connect to the Supabase 'reports' table. "
            "Check your Streamlit secrets and Supabase table/RLS settings. "
            f"Details: {exc}"
        ) from exc


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
