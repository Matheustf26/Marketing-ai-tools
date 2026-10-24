import streamlit as st

from core.llm import api_key_sidebar

st.set_page_config(page_title="Marketing AI Tools", page_icon="📣", layout="wide")
api_key_sidebar()

st.title("Marketing AI Tools")
st.write(
    "Three tools built with Claude to turn influencer marketing into a measurable acquisition channel: "
    "know what's trending, find the right creators, then prove the money before you pay them."
)

col0, col1, col2 = st.columns(3)
with col0:
    st.subheader("📡 Trend Radar")
    st.write(
        "What's getting attention in your segment this week: topics, standout creators and posts, "
        "and a content idea for each brand. A new report every Monday and Friday."
    )
    st.page_link("pages/3_Trend_Radar.py", label="Open Trend Radar", icon="📡")
with col1:
    st.subheader("🔎 Creator Scout")
    st.write(
        "Describe a niche or product. Claude searches the web and returns real creators with audience fit, "
        "best brand match, brand-safety flags and a first outreach message. Export to CSV."
    )
    st.page_link("pages/1_Creator_Scout.py", label="Open Creator Scout", icon="🔎")
with col2:
    st.subheader("💰 Creator ROI Planner")
    st.write(
        "Answer “how do we make money with this?”: cost per lead, ROI and break-even per creator, "
        "three scenarios, UTM links for tracking and a compliant campaign brief."
    )
    st.page_link("pages/2_Creator_ROI_Planner.py", label="Open ROI Planner", icon="💰")

st.divider()
st.markdown(
    "**The workflow:** Spot this week's trends → Scout creators → send the shortlist to the ROI Planner → set fees and expected results → "
    "pay only creators who can break even → track every creator with their own UTM link → "
    "keep the ones that convert."
)
