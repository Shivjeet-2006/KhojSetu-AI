
import streamlit as st

from database.database import (
    create_tables,
    add_report,
    get_reports
)

from services.voice_input import voice_to_text
from services.matching import find_matches


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="KhojSetu AI",
    page_icon="🔎",
    layout="wide"
)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

create_tables()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🔎 KhojSetu AI")

st.subheader("Lost in words. Found through intelligence.")

st.write(
    "A multilingual, AI-powered lost-and-found platform "
    "that helps people reconnect with their lost belongings."
)

st.divider()


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

menu = st.sidebar.radio(
    "Navigation",
    [
        "Report an Item",
        "Browse Reports",
        "Find Matches"
    ]
)


# ==================================================
# 1. REPORT AN ITEM
# ==================================================

if menu == "Report an Item":

    st.header("📝 Report a Lost or Found Item")

    report_type = st.radio(
        "Select report type",
        ["Lost", "Found"],
        horizontal=True
    )

    st.write("### 🎙️ Voice Reporting")

    transcript = voice_to_text()

    st.write("### Item Information")

    with st.form("report_form"):

        description = st.text_area(
            "Describe the item",
            value=transcript,
            placeholder="Example: I lost my black backpack with a red tag."
        )

        category = st.selectbox(
            "Item Category",
            [
                "Bag",
                "Mobile Phone",
                "Wallet",
                "Laptop",
                "Documents",
                "Keys",
                "Accessories",
                "Other"
            ]
        )

        color = st.text_input(
            "Item Color",
            placeholder="Example: Black"
        )

        location = st.text_input(
            "Location",
            placeholder="Example: Near college entrance"
        )

        item_date = st.date_input(
            "Date when item was lost or found"
        )

        identifying_details = st.text_area(
            "Identifying Details",
            placeholder="Example: Small red tag, sticker, scratches, etc."
        )

        submitted = st.form_submit_button(
            "Submit Report",
            use_container_width=True
        )

        if submitted:

            if not description.strip():
                st.error("Please enter an item description.")

            elif not location.strip():
                st.error("Please enter the location.")

            else:

                report_id = add_report(
                    report_type=report_type.lower(),
                    description=description.strip(),
                    category=category,
                    color=color.strip(),
                    location=location.strip(),
                    item_date=str(item_date),
                    identifying_details=identifying_details.strip()
                )

                st.success(
                    f"Your {report_type.lower()} report was submitted successfully!"
                )

                st.info(f"Your Report ID is: {report_id}")


# ==================================================
# 2. BROWSE REPORTS
# ==================================================

elif menu == "Browse Reports":

    st.header("📋 Browse Lost and Found Reports")

    report_filter = st.selectbox(
        "Filter Reports",
        [
            "All Reports",
            "Lost Items",
            "Found Items"
        ]
    )

    if report_filter == "Lost Items":
        reports = get_reports("lost")

    elif report_filter == "Found Items":
        reports = get_reports("found")

    else:
        reports = get_reports()

    if not reports:

        st.info("No reports available yet.")

    else:

        for report in reports:

            report_label = (
                "🔴 LOST"
                if report["report_type"] == "lost"
                else "🟢 FOUND"
            )

            with st.expander(
                f'{report_label} | Report #{report["id"]}'
            ):

                st.write(
                    f'**Description:** {report["description"]}'
                )

                st.write(
                    f'**Category:** {report.get("category") or "Not specified"}'
                )

                st.write(
                    f'**Color:** {report.get("color") or "Not specified"}'
                )

                st.write(
                    f'**Location:** {report.get("location") or "Not specified"}'
                )

                st.write(
                    f'**Date:** {report.get("item_date") or "Not specified"}'
                )

                st.write(
                    "**Identifying Details:** "
                    + (
                        report.get("identifying_details")
                        or "Not specified"
                    )
                )


# ==================================================
# 3. FIND AI MATCHES
# ==================================================

elif menu == "Find Matches":

    st.header("🤖 AI-Powered Item Matching")

    st.write(
        "Select a lost item to find similar found-item reports."
    )

    all_reports = get_reports()

    lost_items = [
        report for report in all_reports
        if report["report_type"] == "lost"
    ]

    found_items = [
        report for report in all_reports
        if report["report_type"] == "found"
    ]

    if not lost_items:

        st.warning("No lost-item reports are available.")

    elif not found_items:

        st.warning("No found-item reports are available yet.")

    else:

        selected_lost = st.selectbox(
            "Select a Lost Item",
            lost_items,
            format_func=lambda item: (
                f'Report #{item["id"]} - '
                f'{item["description"][:65]}'
            )
        )

        if st.button(
            "🔍 Find Possible Matches",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "AI is comparing item descriptions and details..."
                ):

                    matches = find_matches(
                        lost_description=selected_lost["description"],
                        found_items=found_items,
                        top_k=3,
                        lost_item=selected_lost
                    )

                if not matches:

                    st.warning("No possible matches found.")

                else:

                    st.success(
                        f"Found {len(matches)} possible match(es)."
                    )

                    for index, match in enumerate(matches, start=1):

                        item = match["item"]

                        with st.container(border=True):

                            st.subheader(
                                f"Match #{index}"
                            )

                            st.metric(
                                "Matching Score",
                                f'{match["similarity_score"]}%'
                            )

                            st.write(
                                f'**Found Report ID:** {item["id"]}'
                            )

                            st.write(
                                f'**Description:** {item["description"]}'
                            )

                            st.write(
                                f'**Category:** {item.get("category") or "Not specified"}'
                            )

                            st.write(
                                f'**Color:** {item.get("color") or "Not specified"}'
                            )

                            st.write(
                                f'**Location:** {item.get("location") or "Not specified"}'
                            )

                            st.write("**Matching Factors:**")

                            st.write(
                                f'- Description similarity: '
                                f'{match["description_score"]}%'
                            )

                            st.write(
                                f'- Category match: '
                                f'{"Yes" if match["category_match"] else "No"}'
                            )

                            st.write(
                                f'- Color match: '
                                f'{"Yes" if match["color_match"] else "No"}'
                            )

                            st.write(
                                f'- Location match: '
                                f'{"Yes" if match["location_match"] else "No"}'
                            )

                            st.write(
                                f'- Identifying details match: '
                                f'{"Yes" if match["details_match"] else "No"}'
                            )

                    st.caption(
                        "Note: Matching scores are ranking scores, "
                        "not probabilities. Always verify ownership "
                        "before returning an item."
                    )

            except Exception as error:

                st.error(
                    f"Matching failed: {error}"
                )

                st.info(
                    "Please try again. The AI model may need time "
                    "to load on its first run."
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "KhojSetu AI | Powered by Gnani AI voice technology "
    "and multilingual machine learning."
)
