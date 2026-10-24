from pathlib import Path

import streamlit as st

from core.llm import get_client
from core.radar import DEFAULT_BRANDS, build_prompt, research, structure, to_markdown, today
from core.ui import header, setup

setup("Creator Radar", "📡")
header(
    "📡 Creator Radar · What to talk about",
    "This week's trends, every Monday and Friday",
    "The topics, creators and formats getting attention in your segment right now, "
    "with a content idea for each brand.",
)

REPORTS = Path(__file__).parent.parent / "reports"

tab_run, tab_archive = st.tabs(["Run a radar now", "Weekly reports"])

with tab_run:
    with st.form("radar"):
        segment = st.text_input("Segment", value="Personal finance, budgeting, credit and money tips")
        c1, c2, c3 = st.columns(3)
        platforms = c1.multiselect("Platforms", ["Instagram", "TikTok", "YouTube"], default=["Instagram", "TikTok"])
        audience = c2.text_input("Audience", value="United States, ages 22-40")
        count = c3.slider("How many trends", 3, 8, 5)
        brands = st.text_area("Our brands", value=DEFAULT_BRANDS, height=100)
        submitted = st.form_submit_button("Scan this week", type="primary")

    if submitted:
        client = get_client()
        day = today()
        prompt = build_prompt(segment, platforms, audience, brands, count, day)
        try:
            with st.status("Scanning the web for this week's trends…", expanded=True) as status:
                notes = research(client, prompt, on_progress=lambda q: st.write(f"🔍 {q}"))
                status.update(label="Writing the report…")
                report = structure(client, notes)
                status.update(label=f"Found {len(report.trends)} trends", state="complete", expanded=False)
        except RuntimeError as e:
            st.error(str(e))
            st.stop()
        st.session_state["radar_md"] = to_markdown(report, segment, day)

    if st.session_state.get("radar_md"):
        st.markdown(st.session_state["radar_md"])
        st.download_button("Download report (.md)", st.session_state["radar_md"], "trend-radar.md")
        st.caption("Instagram and TikTok can't be read directly. Trends come from public pages that report on them.")

with tab_archive:
    files = sorted(REPORTS.glob("*.md"), reverse=True) if REPORTS.exists() else []
    if not files:
        st.info("No weekly reports yet. The first one is generated automatically on the next Monday or Friday.")
    else:
        choice = st.selectbox("Report", files, format_func=lambda p: p.stem)
        st.markdown(choice.read_text())
