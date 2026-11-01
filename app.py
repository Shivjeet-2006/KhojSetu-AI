
import streamlit as st

from database.database import (
    create_tables,
    add_report,
    get_reports
)

from services.voice_input import voice_to_text
from services.matching import find_matches


st.set_page_config(
    page_title="KhojSetu AI",
    page_icon="🔎",
    layout="wide"
)

create_tables()

st.title("🔎 KhojSetu AI")
st.subheader("Lost in words. Found through intelligence.")

st.write(
    "A multilingual, voice-powered lost-and-found platform."
)

st.divider()

menu = st.sidebar.selectbox(
    "Choose an option",
    [
        "Report an Item",
        "Browse Reports",
        "Find Matches"
    ]
)


# REPORT AN ITEM
if menu == "Report an Item":

    st.header("Submit a Lost or Found Report")

    report_type = st.radio(
        "What happened?",
        ["Lost", "Found"],
        horizontal=True
    )

    transcript = voice_to_text()

    with st.form("report_form"):

        description = st.text_area(
            "Describe the item",
            value=transcript,
            placeholder="Example: Black backpack with a red tag"
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
                "Other"
            ]
        )

        color = st.text_input("Item Colour")
        location = st.text_input("Location")
        item_date = st.text_input("Date (YYYY-MM-DD)")

        details = st.text_area(
            "Unique identifying details"
        )

        submitted = st.form_submit_button(
            "Submit Report"
        )

        if submitted:

            if not description.strip():
                st.error("Please describe the item.")

            elif not location.strip():
                st.error("Please enter the location.")

            else:
                add_report(
                    report_type.lower(),
                    description,
                    category,
                    color,
                    location,
                    item_date,
                    details
                )

                st.success(
                    "Your report has been submitted successfully!"
                )


# BROWSE REPORTS
elif menu == "Browse Reports":

    st.header("Lost and Found Reports")

    report_filter = st.selectbox(
        "Filter reports",
        ["All", "Lost", "Found"]
    )

    selected_type = (
        None if report_filter == "All"
        else report_filter.lower()
    )

    reports = get_reports(selected_type)

    if not reports:
        st.info("No reports available yet.")

    for report in reports:

        with st.container(border=True):

            st.subheader(
                f"{report['report_type'].upper()} - "
                f"{report['category'] or 'Other'}"
            )

            st.write(report["description"])
            st.write("📍 Location:", report["location"])
            st.write("🎨 Colour:", report["color"])

            st.caption(
                f"Report ID: {report['id']} | "
                f"Date: {report['created_at']}"
            )


# FIND MATCHES
elif menu == "Find Matches":

    st.header("🤖 AI-Powered Item Matching")

    st.write(
        "Find possible matches between lost and found items."
    )

    all_reports = get_reports()

    lost_items = [
        item for item in all_reports
        if item["report_type"] == "lost"
    ]

    found_items = [
        item for item in all_reports
        if item["report_type"] == "found"
    ]

    if not lost_items:
        st.warning("No lost-item reports available.")

    elif not found_items:
        st.warning("No found-item reports available.")

    else:

        selected_lost = st.selectbox(
            "Select a lost item",
            lost_items,
            format_func=lambda x: (
                f"Report #{x['id']} - {x['description'][:65]}"
            )
        )

        if st.button("🔍 Find Possible Matches"):

            try:
                with st.spinner(
                    "AI is comparing item descriptions..."
                ):

                    matches = find_matches(
                        selected_lost["description"],
                        found_items,
                        top_k=3
                    )

                if not matches:
                    st.info("No possible matches found.")

                else:
                    st.success("Matching analysis completed!")

                    for index, match in enumerate(matches, 1):

                        item = match["item"]
                        score = match["similarity_score"]

                        with st.container(border=True):

                            st.subheader(
                                f"Possible Match #{index}"
                            )

                            st.metric(
                                "Description Similarity",
                                f"{score}%"
                            )

                            st.write(
                                "**Found item:**",
                                item["description"]
                            )

                            st.write(
                                "**Category:**",
                                item["category"]
                            )

                            st.write(
                                "**Colour:**",
                                item["color"]
                            )

                            st.write(
                                "**Location:**",
                                item["location"]
                            )

                            st.caption(
                                "This is an AI similarity ranking, "
                                "not a confirmed match or probability."
                            )

            except Exception as error:
                st.error(
                    f"Matching failed: {error}"
                )
                st.info(
                    "Check the deployment logs and dependencies."
                )
