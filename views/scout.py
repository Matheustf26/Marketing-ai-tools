import pandas as pd
import streamlit as st

from core.llm import ClaudeError, get_client, reset_cost, run_cost
from core.scout import build_research_prompt, clean_handle, format_followers, research, structure
from core.ui import header

SHOW_FROM = 4  # fit scores below this are hidden


def fit_label(score: int) -> str:
    return "Very good" if score >= 8 else "Good" if score >= 6 else "Regular"


header("scout", "Creator Scout", "Real creators found on the web, scored for fit and brand safety, with a first message ready to send.")

DEFAULT_BRANDS = """Fast Loan Advance: fast help for unexpected expenses. Direct, upbeat.
Fast Loan Direct: simple and transparent, compare offers and costs. Clear, no jargon.
Grace Loan Advance: second chances and financial education for people rebuilding credit. Warm, non-judgmental."""

trend = st.session_state.get("scout_trend")
if trend:
    st.info(f"Trend from Creator Radar: **{trend}**. Scout looks for creators in the niche whose content suits it.",
            icon=":material/radar:")

with st.form("scout"):
    niche = st.text_input(
        "Niche or product",
        value="Personal finance and budgeting for young adults, emergency expenses, rebuilding credit",
    )
    angle = st.text_input("Trend to build content around (optional)", value=trend or "")
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
    count = st.slider("How many creators", 3, 10, 5, help="Scout fills the list with good or regular fits when strong matches run out.")
    brands = st.text_area("Brands to match (one per line: name: positioning)", value=DEFAULT_BRANDS, height=100)
    submitted = st.form_submit_button("Find creators", type="primary")

if submitted:
    client = get_client()
    prompt = build_research_prompt(niche, platforms, country, size, brands, count, angle)
    reset_cost()
    try:
        with st.status("Searching the web…", expanded=True) as status:
            notes = research(client, prompt, on_progress=lambda q: st.markdown(f":material/search: {q}"))
            status.update(label="Organizing results…")
            result = structure(client, notes, count)
            status.update(label=f"Found {len(result.creators)} creators", state="complete", expanded=False)
    except ClaudeError as e:
        st.error(str(e))
        st.stop()
    st.session_state["scout_result"] = result
    st.session_state["scout_cost"] = run_cost()

result = st.session_state.get("scout_result")
if result:
    df = pd.DataFrame([c.model_dump() for c in result.creators])
    if df.empty:
        st.warning("No creators with a confirmed handle and follower count. Try a broader niche, another platform or another size.")
        st.caption(result.search_summary)
        st.stop()
    shown = df[df["fit_score"] >= SHOW_FROM]
    if shown.empty:
        st.warning("No creators with at least a regular fit. Try a broader niche, another platform or another size.")
        st.caption(result.search_summary)
        st.stop()
    if len(shown) < len(df):
        st.caption(f"Left out {len(df) - len(shown)} creators with a poor fit.")
    df = shown.copy()
    df["fit"] = df["fit_score"].map(fit_label)
    df["handle"] = df["handle"].map(clean_handle)
    df = df.sort_values(["fit_score", "followers"], ascending=False)
    df["followers_label"] = df["followers"].map(format_followers)
    df["views_label"] = df["avg_views"].map(lambda v: format_followers(v) if v else "Not reported")
    df["brand_safety"] = df["brand_safety_flags"].apply(lambda f: "; ".join(f) if f else "None found")

    st.subheader(f"{len(df)} creators")
    st.caption(result.search_summary)
    st.dataframe(
        df[["name", "handle", "platform", "followers_label", "views_label", "fit", "best_brand"]],
        column_config={
            "name": "Creator",
            "handle": "Handle",
            "platform": "Platform",
            "followers_label": "Followers",
            "views_label": "Avg views",
            "fit": "Fit",
            "best_brand": "Best brand",
        },
        hide_index=True,
        width="stretch",
    )

    st.subheader("Details and outreach")
    for _, row in df.iterrows():
        label = f"{row['name']}, {row['handle']}, {row['followers_label']} on {row['platform']}, {row['fit']} fit"
        with st.expander(label):
            st.write(f"**What they post:** {row['content_summary']}")
            st.write(f"**Why they fit:** {row['audience_fit']}")
            st.write(f"**Recent activity:** {row['recent_activity'] or 'Not confirmed'}")
            st.write(f"**Best brand:** {row['best_brand']}")
            st.write(f"**Brand safety:** {row['brand_safety']}")
            st.text_area("First message", row["outreach_message"], key=f"dm_{row.name}", height=110)

    export = df[
        ["name", "handle", "platform", "followers", "avg_views", "fit_score", "best_brand", "brand_safety",
         "recent_activity", "content_summary", "audience_fit", "outreach_message", "source_url"]
    ]
    c1, c2 = st.columns(2)
    c1.download_button("Download CSV", export.to_csv(index=False).encode(), file_name="creators.csv", mime="text/csv")
    if c2.button("Compare these creators in ROI Planner"):
        st.session_state["roi_creators"] = df[["name", "handle", "platform", "followers", "fit_score", "avg_views"]].to_dict("records")
        st.switch_page("views/roi.py")

    st.caption(
        "Follower counts come from public sources and can be out of date. Check each profile before outreach. "
        f"This search cost about ${st.session_state.get('scout_cost', 0):.2f} in Claude credits."
    )
