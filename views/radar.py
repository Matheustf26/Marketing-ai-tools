import streamlit as st

from core.llm import get_client, reset_cost, run_cost
from core.radar import (
    DEFAULT_BRANDS,
    build_prompt,
    report_date,
    research,
    saved_reports,
    structure,
    to_markdown,
    today,
)
from core.ui import header

header("radar", "Creator Radar", "What your segment is talking about this week on Instagram and TikTok, with a content idea for each brand.")

tab_archive, tab_run = st.tabs(["This week's report", "Run a new scan"])

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
        reset_cost()
        try:
            with st.status("Scanning the web for this week's trends…", expanded=True) as status:
                notes = research(client, prompt, on_progress=lambda q: st.markdown(f":material/search: {q}"))
                status.update(label="Writing the report…")
                report = structure(client, notes)
                status.update(label=f"Found {len(report.trends)} trends", state="complete", expanded=False)
        except RuntimeError as e:
            st.error(str(e))
            st.stop()
        st.session_state["radar_md"] = to_markdown(report, segment, day)
        st.session_state["radar_cost"] = run_cost()

    if st.session_state.get("radar_md"):
        st.markdown(st.session_state["radar_md"])
        st.download_button("Download report (.md)", st.session_state["radar_md"], "trend-radar.md")
        st.caption(
            "Instagram and TikTok can't be read directly. Trends come from public pages that report on them. "
            f"This scan cost about ${st.session_state.get('radar_cost', 0):.2f} in Claude credits."
        )

with tab_archive:
    files = saved_reports()
    if not files:
        st.info("No weekly reports yet. The first one is generated automatically on the next Monday or Friday.")
    else:
        choice = st.selectbox("Report", files, format_func=report_date)
        st.caption(
            "Written automatically every Monday and Friday morning by a scheduled job. "
            "Reading a saved report is free; only a new scan uses Claude credits."
        )
        with st.container(border=True):
            # The page banner already names the tool, so the report's own title becomes a small heading.
            text = choice.read_text()
            st.markdown("#### " + text[2:] if text.startswith("# ") else text)
