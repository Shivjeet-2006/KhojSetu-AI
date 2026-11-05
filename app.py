import streamlit as st

from database.database import create_tables, add_report, get_reports
from services.voice_input import voice_to_text
from services.matching import find_matches


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="KhojSetu AI | Lost & Found",
    page_icon="K",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PROFESSIONAL THEME
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background: #f6f8fb;
        color: #172033;
    }
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7ebf2;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: #173b68;
        font-size: 1.45rem;
    }
    .main .block-container {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #172b4d;
        letter-spacing: -0.025em;
    }
    .hero {
        background: linear-gradient(120deg, #173b68 0%, #245b91 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.6rem;
    }
    .hero h1 {
        color: white !important;
        font-size: 2.1rem;
        margin: 0 0 .35rem 0;
    }
    .hero p {
        color: #e5effa;
        font-size: 1rem;
        margin: 0;
    }
    .section-card {
        background: #ffffff;
        border: 1px solid #e7ebf2;
        border-radius: 14px;
        padding: 1.15rem 1.25rem;
        margin-bottom: 1rem;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background: #1d4f82;
        color: white;
        border: 1px solid #1d4f82;
        border-radius: 9px;
        min-height: 2.8rem;
        font-weight: 600;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background: #153d67;
        color: white;
        border-color: #153d67;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        border-radius: 8px;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e7ebf2;
        padding: 1rem;
        border-radius: 12px;
    }
    [data-testid="stExpander"] {
        background: white;
        border: 1px solid #e7ebf2;
        border-radius: 10px;
    }
    .muted {
        color: #64748b;
        font-size: .92rem;
    }
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------
create_tables()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "report_form_version" not in st.session_state:
    st.session_state.report_form_version = 0

if "report_success_message" not in st.session_state:
    st.session_state.report_success_message = None

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
with st.sidebar:
    st.markdown("# KhojSetu AI")
    st.caption("Multilingual Lost & Found Platform")
    st.divider()

    menu = st.radio(
        "MAIN MENU",
        ["Report an Item", "Browse Reports", "Find Matches"],
        label_visibility="visible"
    )

    st.divider()
    st.caption("Helping people reconnect with their belongings.")

# --------------------------------------------------
# HOME / PAGE HEADER
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>KhojSetu AI</h1>
        <p>A smarter way to report, discover and reconnect lost belongings.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 1. REPORT AN ITEM
# ==================================================
if menu == "Report an Item":
    st.header("Report an Item")
    st.markdown(
        '<p class="muted">Provide accurate details to help others identify and return the item.</p>',
        unsafe_allow_html=True
    )

    if st.session_state.report_success_message:
        st.success(st.session_state.report_success_message)
        st.session_state.report_success_message = None

    st.markdown("### Choose report type")
    st.caption("Select the option that describes your situation.")

    report_type = st.radio(
        "Report type",
        ["lost", "found"],
        format_func=lambda option: (
            "I LOST an item" if option == "lost"
            else "I FOUND an item"
        ),
        horizontal=True,
        key="report_type_choice",
        label_visibility="collapsed"
    )

    form_version = st.session_state.report_form_version

    with st.expander("Voice-assisted description", expanded=False):
        transcript = voice_to_text(widget_key_suffix=str(form_version))
        st.caption("Record in Hindi, English or Marathi. You can edit the recognised text in the description field.")

    st.subheader("Item details")

    category_options = [
        "Bag", "Bottle", "Mobile Phone", "Wallet", "Laptop",
        "Documents", "Keys", "Clothing", "Jewellery", "Watch",
        "Books", "Electronics", "Accessories", "Other"
    ]

    # Keep category controls outside the form so selecting Other
    # immediately displays the custom category field.
    category = st.selectbox(
        "Item category *",
        category_options,
        key=f"category_{form_version}"
    )

    custom_category = ""
    if category == "Other":
        custom_category = st.text_input(
            "Enter item category *",
            placeholder="Example: Umbrella, lunch box, sports equipment",
            key=f"custom_category_{form_version}"
        )

    with st.form(f"report_form_{form_version}", clear_on_submit=False):
        description = st.text_area(
            "Item description *",
            value=transcript,
            placeholder="Example: Black backpack with a red tag and two front pockets.",
            height=100,
            key=f"description_{form_version}"
        )

        col1, col2 = st.columns(2)
        with col1:
            color = st.text_input(
                "Item colour",
                placeholder="Example: Black",
                key=f"color_{form_version}"
            )
        with col2:
            location = st.text_input(
                "Location *",
                placeholder="Example: College library, Nagpur",
                key=f"location_{form_version}"
            )

        item_date = st.date_input(
            "Date when the item was lost or found",
            key=f"item_date_{form_version}"
        )

        identifying_details = st.text_area(
            "Additional identifying details",
            placeholder="Brand, model, marks, stickers or other unique features.",
            height=90,
            key=f"details_{form_version}"
        )

        st.caption("* Required fields")

        submitted = st.form_submit_button(
            "Submit report",
            use_container_width=True
        )

    if submitted:
        final_category = custom_category.strip() if category == "Other" else category

        if not description.strip():
            st.error("Please enter an item description.")
        elif not location.strip():
            st.error("Please enter the location.")
        elif category == "Other" and not final_category:
            st.error("Please enter the item category.")
        else:
            try:
                report_id = add_report(
                    report_type=report_type.lower(),
                    description=description.strip(),
                    category=final_category,
                    color=color.strip(),
                    location=location.strip(),
                    item_date=str(item_date),
                    identifying_details=identifying_details.strip()
                )

                st.session_state[f"voice_transcript_{form_version}"] = ""
                st.session_state.report_form_version += 1
                st.session_state.report_success_message = (
                    f"{report_type} item report submitted successfully. "
                    f"Your report ID is #{report_id}."
                )
                st.rerun()
            except Exception as error:
                st.error(f"Unable to submit the report: {error}")

# ==================================================
# 2. BROWSE REPORTS
# ==================================================
elif menu == "Browse Reports":
    st.header("Browse Reports")
    st.markdown(
        '<p class="muted">Explore items reported as lost or found.</p>',
        unsafe_allow_html=True
    )

    report_filter = st.selectbox(
        "Show reports",
        ["All Reports", "Lost Items", "Found Items"]
    )

    if report_filter == "Lost Items":
        reports = get_reports("lost")
    elif report_filter == "Found Items":
        reports = get_reports("found")
    else:
        reports = get_reports()

    total = len(reports)
    lost_count = sum(1 for report in reports if report["report_type"] == "lost")
    found_count = sum(1 for report in reports if report["report_type"] == "found")

    c1, c2, c3 = st.columns(3)
    c1.metric("Reports shown", total)
    c2.metric("Lost items", lost_count)
    c3.metric("Found items", found_count)

    if not reports:
        st.info("No reports found for this selection.")
    else:
        for report in reports:
            label = "LOST ITEM" if report["report_type"] == "lost" else "FOUND ITEM"
            with st.expander(f"{label}  |  Report #{report['id']}"):
                left, right = st.columns(2)
                with left:
                    st.write("**Description**")
                    st.write(report.get("description") or "Not specified")
                    st.write("**Category**")
                    st.write(report.get("category") or "Not specified")
                    st.write("**Colour**")
                    st.write(report.get("color") or "Not specified")
                with right:
                    st.write("**Location**")
                    st.write(report.get("location") or "Not specified")
                    st.write("**Date**")
                    st.write(report.get("item_date") or "Not specified")
                    st.write("**Additional details**")
                    st.write(report.get("identifying_details") or "Not specified")

# ==================================================
# 3. FIND AI MATCHES
# ==================================================
elif menu == "Find Matches":
    st.header("AI-Powered Item Matching")
    st.markdown(
        '<p class="muted">Compare lost-item reports with similar found-item reports.</p>',
        unsafe_allow_html=True
    )

    all_reports = get_reports()
    lost_items = [r for r in all_reports if r["report_type"] == "lost"]
    found_items = [r for r in all_reports if r["report_type"] == "found"]

    c1, c2 = st.columns(2)
    c1.metric("Lost reports", len(lost_items))
    c2.metric("Found reports", len(found_items))

    if not lost_items:
        st.info("There are no lost-item reports to compare yet.")
    elif not found_items:
        st.info("There are no found-item reports to compare yet.")
    else:
        selected_lost = st.selectbox(
            "Select a lost-item report",
            lost_items,
            format_func=lambda item: (
                f"Report #{item['id']} — {item['description'][:65]}"
            )
        )

        if st.button("Find possible matches", use_container_width=True):
            try:
                with st.spinner("Analysing item descriptions and details..."):
                    matches = find_matches(
                        lost_description=selected_lost["description"],
                        found_items=found_items,
                        top_k=3,
                        lost_item=selected_lost
                    )

                if not matches:
                    st.warning("No possible matches were found.")
                else:
                    st.success(f"{len(matches)} possible match(es) found.")

                    for index, match in enumerate(matches, start=1):
                        item = match["item"]
                        with st.container(border=True):
                            st.subheader(f"Possible match {index}")
                            st.metric("Matching score", f"{match['similarity_score']}%")

                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Found report ID:** #{item['id']}")
                                st.write(f"**Description:** {item['description']}")
                                st.write(f"**Category:** {item.get('category') or 'Not specified'}")
                            with col2:
                                st.write(f"**Colour:** {item.get('color') or 'Not specified'}")
                                st.write(f"**Location:** {item.get('location') or 'Not specified'}")
                                st.write(f"**Date:** {item.get('item_date') or 'Not specified'}")

                            st.write("**Matching factors**")
                            st.write(
                                f"- Description similarity: {match['description_score']}%"
                            )
                            st.write(
                                f"- Category: {'Match' if match['category_match'] else 'No match'}"
                            )
                            st.write(
                                f"- Colour: {'Match' if match['color_match'] else 'No match'}"
                            )
                            st.write(
                                f"- Location: {'Match' if match['location_match'] else 'No match'}"
                            )
                            st.write(
                                f"- Identifying details: {'Match' if match['details_match'] else 'No match'}"
                            )

                    st.caption(
                        "Matching scores help rank similar reports; they are not probabilities. "
                        "Verify ownership before returning an item."
                    )
            except Exception as error:
                st.error(f"Matching failed: {error}")
                st.info("Please try again. The AI model may take a little time to load.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    "KhojSetu AI | Multilingual lost-and-found assistance powered by "
    "voice technology and machine learning."
)
