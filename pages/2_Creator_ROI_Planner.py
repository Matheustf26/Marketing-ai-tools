import pandas as pd
import streamlit as st

from core.brief import write_brief
from core.llm import ClaudeError, api_key_sidebar, get_client
from core.roi import Plan, project, scenarios, utm_link

st.set_page_config(page_title="Creator ROI Planner", page_icon="💰", layout="wide")
api_key_sidebar()

st.title("💰 Creator ROI Planner")
st.caption("How does an influencer campaign make money? Model it before you pay anyone.")


def money(x):
    if x is None:
        return "n/a"
    return f"-${-x:,.2f}" if x < 0 else f"${x:,.2f}"


tab_one, tab_many, tab_links, tab_brief = st.tabs(
    ["Single creator", "Campaign (many creators)", "Tracking links", "Campaign brief"]
)

with tab_one:
    st.markdown("Every post is a small lead-gen campaign: **views → clicks → leads → revenue**.")
    c1, c2, c3, c4, c5 = st.columns(5)
    fee = c1.number_input("Creator fee ($)", min_value=0.0, value=1500.0, step=100.0)
    views = c2.number_input("Expected views", min_value=0.0, value=80000.0, step=5000.0)
    ctr = c3.number_input("Link CTR (%)", min_value=0.0, value=1.0, step=0.1) / 100
    lead_rate = c4.number_input("Click → lead (%)", min_value=0.0, value=8.0, step=0.5) / 100
    rpl = c5.number_input("Revenue per lead ($)", min_value=0.0, value=35.0, step=1.0)
    plan = Plan(fee, views, ctr, lead_rate, rpl)

    base = project(plan)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Leads", f"{base.leads:,.0f}")
    m2.metric("Cost per lead", money(base.cost_per_lead))
    m3.metric("Profit", money(base.profit), delta=None if base.roi is None else f"{base.roi:.0%} ROI")
    m4.metric("Break-even", "n/a" if base.breakeven_leads is None else f"{base.breakeven_leads:,.0f} leads")

    if base.profit >= 0:
        st.success(f"Worth it at this fee. You could pay up to **{money(base.max_fee)}** and still break even.")
    else:
        st.error(
            f"Loses money at this fee. Offer at most **{money(base.max_fee)}**, "
            "or move to a performance deal (flat fee + bonus per lead)."
        )

    st.subheader("Scenarios")
    rows = []
    for name, o in scenarios(plan).items():
        rows.append(
            {
                "Scenario": name,
                "Clicks": round(o.clicks),
                "Leads": round(o.leads),
                "Revenue": money(o.revenue),
                "Profit": money(o.profit),
                "ROI": "n/a" if o.roi is None else f"{o.roi:.0%}",
                "Cost per lead": money(o.cost_per_lead),
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption("Pessimistic and optimistic scale clicks by 0.5x and 1.5x. Use your own past campaign data when you have it.")

with tab_many:
    st.markdown("Plan a whole campaign. Edit the table, add rows, and see which creators earn their fee.")
    seeded = st.session_state.get("roi_creators")
    if seeded:
        start = pd.DataFrame(
            [
                {"Creator": r["handle"] or r["name"], "Platform": r["platform"], "Fee ($)": 1000.0,
                 "Expected views": 50000.0, "CTR (%)": 1.0, "Click→lead (%)": 8.0}
                for r in seeded
            ]
        )
        st.success(f"Loaded {len(seeded)} creators from Creator Scout.")
    else:
        start = pd.DataFrame(
            [
                {"Creator": "@creator_one", "Platform": "TikTok", "Fee ($)": 800.0, "Expected views": 60000.0, "CTR (%)": 0.8, "Click→lead (%)": 8.0},
                {"Creator": "@creator_two", "Platform": "Instagram", "Fee ($)": 2500.0, "Expected views": 90000.0, "CTR (%)": 1.2, "Click→lead (%)": 10.0},
                {"Creator": "@creator_three", "Platform": "YouTube", "Fee ($)": 4000.0, "Expected views": 40000.0, "CTR (%)": 2.5, "Click→lead (%)": 12.0},
            ]
        )
    rpl_many = st.number_input("Revenue per lead ($)", min_value=0.0, value=35.0, step=1.0, key="rpl_many")
    table = st.data_editor(start, num_rows="dynamic", hide_index=True, use_container_width=True)

    results = []
    for _, r in table.dropna(subset=["Fee ($)"]).iterrows():
        o = project(Plan(r["Fee ($)"], r["Expected views"], r["CTR (%)"] / 100, r["Click→lead (%)"] / 100, rpl_many))
        results.append(
            {
                "Creator": r["Creator"],
                "Leads": round(o.leads),
                "Cost per lead": money(o.cost_per_lead),
                "Profit": o.profit,
                "Max fee": money(o.max_fee),
                "Verdict": "✅ Book" if o.profit >= 0 else "⚠️ Renegotiate",
            }
        )
    if results:
        out = pd.DataFrame(results)
        total_fee = table["Fee ($)"].sum()
        total_profit = out["Profit"].sum()
        t1, t2, t3 = st.columns(3)
        t1.metric("Total spend", money(total_fee))
        t2.metric("Total leads", f"{out['Leads'].sum():,}")
        t3.metric("Campaign profit", money(total_profit))
        out["Profit"] = out["Profit"].apply(money)
        st.dataframe(out, hide_index=True, use_container_width=True)

with tab_links:
    st.markdown("Give every creator their own link, so you know who actually brings leads.")
    base_url = st.text_input("Landing page URL", value="https://www.example.com/apply")
    campaign = st.text_input("Campaign name", value="creators-q4")
    default_handles = (
        "\n".join(f"{r['platform']},{r['handle'] or r['name']}" for r in seeded)
        if seeded
        else "TikTok,@creator_one\nInstagram,@creator_two\nYouTube,@creator_three"
    )
    lines = st.text_area("One per line: platform,handle", value=default_handles, height=120)
    links = []
    for line in lines.splitlines():
        if "," in line:
            platform, handle = (p.strip() for p in line.split(",", 1))
            links.append({"Creator": handle, "Platform": platform, "Link": utm_link(base_url, platform, campaign, handle)})
    if links:
        links_df = pd.DataFrame(links)
        st.dataframe(links_df, hide_index=True, use_container_width=True)
        st.download_button("Download links CSV", links_df.to_csv(index=False).encode(), "utm-links.csv", "text/csv")
        st.caption("In GA4, filter by utm_medium = influencer and break down by utm_content to see leads per creator.")

with tab_brief:
    st.markdown("Generate a brief creators can follow, with FTC disclosure rules and a legal-review list.")
    brand = st.text_input("Brand and positioning", value="Grace Loan Advance: second chances and financial education for people rebuilding credit")
    product = st.text_input("Product / offer", value="Free tool to compare personal loan offers from a lender network")
    goal = st.text_input("Goal and KPI", value="Qualified leads, tracked per creator; target cost per lead under $20")
    creators = st.text_input("Creators", value="3 micro creators on TikTok and Instagram, personal finance niche")
    if st.button("Write brief", type="primary"):
        client = get_client()
        try:
            with st.spinner("Writing the brief…"):
                st.session_state["brief"] = write_brief(client, brand, product, goal, creators, f"Campaign: {campaign}.")
        except ClaudeError as e:
            st.error(str(e))
    if st.session_state.get("brief"):
        st.markdown(st.session_state["brief"])
        st.download_button("Download brief (.md)", st.session_state["brief"], "campaign-brief.md")
