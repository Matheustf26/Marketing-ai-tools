import streamlit as st

from core.ui import card, header, setup, steps

setup("Home", "📣")
header(
    "Creator Suite",
    "Influencer marketing that pays for itself",
    "Three tools built with Claude: know what to talk about this week, find the right creators, "
    "and prove the return before you pay anyone.",
)

col1, col2, col3 = st.columns(3)
with col1:
    card(
        "📡",
        "Creator Radar",
        "What to talk about",
        "This week's top topics and standout creators in your segment, with a content idea for each brand. "
        "New report every Monday and Friday.",
        "pages/1_Creator_Radar.py",
        "Open Creator Radar",
    )
with col2:
    card(
        "🔎",
        "Creator Scout",
        "Who to work with",
        "Real creators found on the web, with a fit score, best brand match, brand-safety flags "
        "and a first outreach message.",
        "pages/2_Creator_Scout.py",
        "Open Creator Scout",
    )
with col3:
    card(
        "💰",
        "Creator ROI Planner",
        "How it makes money",
        "Cost per lead, ROI, break-even and the maximum fee worth paying, plus tracking links "
        "and a compliant campaign brief.",
        "pages/3_Creator_ROI_Planner.py",
        "Open ROI Planner",
    )

st.write("")
st.subheader("The workflow")
steps(
    [
        "Spot this week's trends",
        "Scout creators",
        "Model the ROI",
        "Pay only creators who break even",
        "Track each one with a UTM link",
        "Keep the ones that convert",
    ]
)
