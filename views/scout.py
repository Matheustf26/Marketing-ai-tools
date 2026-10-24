import pandas as pd
import streamlit as st

from core.llm import ClaudeError, get_client
from core.scout import build_research_prompt, research, structure
from core.ui import header

header("scout", "Creator Scout", "Real creators found on the web, scored for fit and brand safety, with a first message ready to send.")

DEFAULT_BRANDS = """Fast Loan Advance: fast help for unexpected expenses. Direct, upbeat.
Fast Loan Direct: simple and transparent, compare offers and costs. Clear, no jargon.
Grace Loan Advance: second chances and financial education for people rebuilding credit. Warm, non-judgmental."""

with st.form("scout"):
    niche = st.text_input(
        "Niche or product",
        value="Personal finance and budgeting for young adults, emergency expenses, rebuilding credit",
    )
    c1, c2, c3 = st.columns(3)
    platforms = c1.multiselect(
        "Platforms", ["Instagram", "TikTok", "YouTube", "X"], default=["Instagram", "TikTok"]
    )
    country = c2.text_input("Country / audience", value="United States")
    size = c3.selectbox(
        "Creator size",
        ["Nano (1K-10K)", "Micro (10K-100K)", "Mid (100K-500K)", "Macro (500K+)", "Any"],
        index=1,
    )
    count = st.slider("How many creators", 5, 20, 10)
    brands = st.text_area("Brands to match (one per line: name: positioning)", value=DEFAULT_BRANDS, height=100)
    submitted = st.form_submit_button("Find creators", type="primary")

if submitted:
    client = get_client()
    prompt = build_research_prompt(niche, platforms, country, size, brands, count)
    try:
        with st.status("Searching the web…", expanded=True) as status:
            notes = research(client, prompt, on_progress=lambda q: st.markdown(f":material/search: {q}"))
            status.update(label="Organizing results…")
            result = structure(client, notes)
            status.update(label=f"Found {len(result.creators)} creators", state="complete", expanded=False)
    except ClaudeError as e:
        st.error(str(e))
        st.stop()
    st.session_state["scout_result"] = result

result = st.session_state.get("scout_result")
if result:
    st.info(result.search_summary)
    df = pd.DataFrame([c.model_dump() for c in result.creators])
    if df.empty:
        st.warning("No creators found. Try a broader niche or another platform.")
        st.stop()
    df = df.sort_values("fit_score", ascending=False)
    df["brand_safety_flags"] = df["brand_safety_flags"].apply(lambda f: "; ".join(f) if f else "None found")

    st.dataframe(
        df[["name", "handle", "platform", "followers", "fit_score", "best_brand", "brand_safety_flags", "profile_url"]],
        column_config={
            "name": "Name",
            "handle": "Handle",
            "platform": "Platform",
            "followers": "Followers",
            "best_brand": "Best brand",
            "brand_safety_flags": st.column_config.TextColumn("Brand safety", width="large"),
            "profile_url": st.column_config.LinkColumn("Profile"),
            "fit_score": st.column_config.ProgressColumn("Fit", min_value=0, max_value=10, format="%d"),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Details and outreach")
    for _, row in df.iterrows():
        with st.expander(f"{row['name']} ({row['handle'] or row['platform']}), fit {row['fit_score']}/10"):
            st.write(f"**What they post:** {row['content_summary']}")
            st.write(f"**Why they fit:** {row['audience_fit']}")
            st.write(f"**Best brand:** {row['best_brand']}")
            st.write(f"**Brand safety:** {row['brand_safety_flags']}")
            st.write(f"**Source:** {row['source_url']}")
            st.text_area("First message", row["outreach_message"], key=f"dm_{row.name}", height=110)

    c1, c2 = st.columns(2)
    c1.download_button(
        "Download CSV", df.to_csv(index=False).encode(), file_name="creators.csv", mime="text/csv"
    )
    if c2.button("Send shortlist to ROI Planner"):
        st.session_state["roi_creators"] = df[["name", "handle", "platform", "followers"]].to_dict("records")
        st.switch_page("views/roi.py")

    st.caption("Follower counts come from public sources and can be out of date. Check each profile before outreach.")
