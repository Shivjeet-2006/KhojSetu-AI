
import streamlit as st

from database.database import (
    create_tables,
    add_report,
    get_reports
)

st.set_page_config(
    page_title="KhojSetu AI",
    page_icon="🔎",
    layout="wide"
)

create_tables()

st.title("🔎 KhojSetu AI")
st.subheader("Lost in words. Found through intelligence.")

st.write(
    "A multilingual lost-and-found platform "
    "powered by AI."
)

st.divider()

menu = st.sidebar.selectbox(
    "Choose an option",
    ["Report an Item", "Browse Reports"]
)

if menu == "Report an Item":

    st.header("Submit a Lost or Found Report")

    report_type = st.radio(
        "What happened?",
        ["Lost", "Found"],
        horizontal=True
    )

    with st.form("report_form"):

        description = st.text_area(
            "Describe the item",
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
        item_date = st.text_input(
            "Date (YYYY-MM-DD)"
        )

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
                    "Your report has been submitted!"
                )


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
