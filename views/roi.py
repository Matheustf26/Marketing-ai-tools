import pandas as pd
import streamlit as st

from core.brief import write_brief
from core.llm import ClaudeError, get_client, reset_cost, run_cost
from core.roi import GOOD_FIT, Offer, Plan, compare_offers, project, quote_cost, scenarios, utm_link
from core.ui import header

header("roi", "Creator ROI Planner", "Compare creators by their real quotes and real numbers, and see which one is worth closing.")


def money(x):
    if x is None:
        return "n/a"
    return f"-${-x:,.2f}" if x < 0 else f"${x:,.2f}"


tab_many, tab_one, tab_links, tab_brief = st.tabs(
    ["Compare creators", "One quote in detail", "Tracking links", "Campaign brief"]
)
seeded = st.session_state.get("roi_creators")

with tab_one:
    st.markdown("Fill this in once a creator sends a quote. Every number comes from the quote, their profile or our past campaigns.")

    st.subheader("1. The quote")
    q1, q2, q3 = st.columns(3)
    price = q1.number_input("Total price ($)", min_value=0, value=0, step=100)
    videos = q2.number_input("Videos or posts in the package", min_value=0, value=0, step=1)
    where = q3.radio("Where the videos go live", ["Creator's account", "Our accounts (UGC)"], horizontal=True)

    st.subheader("2. Real numbers")
    whose = "their" if where == "Creator's account" else "our"
    st.caption(
        f"Averages of {whose} last 10 to 20 posts, from the profile, a media kit or our analytics. "
        "Use the median if a single viral post skews the average."
    )
    r1, r2, r3 = st.columns(3)
    avg_views = r1.number_input("Average views per post", min_value=0, value=0, step=1000)
    avg_likes = r2.number_input("Average likes per post", min_value=0, value=0, step=100)
    avg_comments = r3.number_input("Average comments per post", min_value=0, value=0, step=10)

    if not (price and videos and avg_views):
        st.info("Enter the price, the number of videos and the average views to see what the quote buys.", icon=":material/edit:")
    else:
        cost = quote_cost(price, videos, avg_views, avg_likes, avg_comments)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Cost per video", money(cost.cost_per_video))
        k2.metric("Expected views", f"{cost.total_views:,.0f}", help="Average views per post times the number of videos.")
        k3.metric("Cost per 1,000 views", money(cost.cpm))
        k4.metric(
            "Cost per engagement",
            money(cost.cost_per_engagement),
            delta=None if cost.engagement_rate is None or not (avg_likes or avg_comments) else f"{cost.engagement_rate:.1%} engagement",
            delta_color="off",
        )

        st.subheader("3. Does it pay back?")
        st.caption("Our own funnel numbers from past campaigns: how many viewers click, how many clicks become leads, what a lead is worth.")
        f1, f2, f3 = st.columns(3)
        ctr = f1.number_input("Link CTR (%)", min_value=0.0, value=0.0, step=0.1, format="%.1f") / 100
        lead_rate = f2.number_input("Click → lead (%)", min_value=0.0, value=0.0, step=0.5, format="%.1f") / 100
        rpl = f3.number_input("Revenue per lead ($)", min_value=0, value=0, step=1)

        if not (ctr and lead_rate and rpl):
            st.info("Add our funnel numbers to see leads, profit and the most this quote is worth.", icon=":material/edit:")
        else:
            plan = Plan(price, cost.total_views, ctr, lead_rate, rpl)
            base = project(plan)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Leads", f"{base.leads:,.0f}")
            m2.metric("Cost per lead", money(base.cost_per_lead))
            m3.metric("Profit", money(base.profit), delta=None if base.roi is None else f"{base.roi:.0%} ROI")
            m4.metric("Break-even", "n/a" if base.breakeven_leads is None else f"{base.breakeven_leads:,.0f} leads")

            if base.profit >= 0:
                st.success(f"Worth it at this price. The package could cost up to **{money(base.max_fee)}** and still break even.")
            else:
                st.error(
                    f"Loses money at this price. Offer at most **{money(base.max_fee)}**, fewer videos, "
                    "or a performance deal (flat fee + bonus per lead)."
                )

            rows = []
            for name, o in scenarios(plan).items():
                rows.append(
                    {
                        "Scenario": name,
                        "Clicks": round(o.clicks),
                        "Leads": round(o.leads),
                        "Revenue": o.revenue,
                        "Profit": o.profit,
                        "ROI": None if o.roi is None else o.roi * 100,
                        "Cost per lead": o.cost_per_lead,
                    }
                )
            st.dataframe(
                pd.DataFrame(rows),
                hide_index=True,
                width="stretch",
                column_config={
                    "Clicks": st.column_config.NumberColumn(format="localized"),
                    "Revenue": st.column_config.NumberColumn(format="dollar"),
                    "Profit": st.column_config.NumberColumn(format="dollar"),
                    "ROI": st.column_config.NumberColumn(format="%.0f%%"),
                    "Cost per lead": st.column_config.NumberColumn(format="dollar"),
                },
            )
            st.caption("Pessimistic and optimistic scale clicks by 0.5x and 1.5x, since one campaign is never exactly average.")

with tab_many:
    st.markdown(
        "Put the quotes side by side. One row per creator: their price, how many videos, their real averages "
        "and how well they fit. Link clicks are optional, if the creator shares results from past campaigns."
    )
    columns = ["Creator", "Platform", "Followers", "Fit (1-10)", "Price ($)", "Videos", "Avg views", "Avg likes",
               "Avg comments", "Link clicks"]
    if seeded:
        start = pd.DataFrame(
            [
                {"Creator": r["handle"] or r["name"], "Platform": r["platform"], "Followers": r["followers"],
                 "Fit (1-10)": r.get("fit_score", 0), "Price ($)": 0, "Videos": 0, "Avg views": r.get("avg_views", 0),
                 "Avg likes": 0, "Avg comments": 0, "Link clicks": 0}
                for r in seeded
            ],
            columns=columns,
        )
        st.success(f"Loaded {len(seeded)} creators from Creator Scout. Add each one's quote and averages.")
    else:
        start = pd.DataFrame(
            [{c: 0 for c in columns} | {"Creator": f"Creator {i}", "Platform": "TikTok"} for i in (1, 2, 3)],
            columns=columns,
        )
    table = st.data_editor(
        start,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "Platform": st.column_config.SelectboxColumn(options=["Instagram", "TikTok", "YouTube", "X"]),
            "Followers": st.column_config.NumberColumn(min_value=0, format="localized"),
            "Fit (1-10)": st.column_config.NumberColumn(min_value=0, max_value=10, step=1),
            "Price ($)": st.column_config.NumberColumn(min_value=0, format="dollar"),
            **{c: st.column_config.NumberColumn(min_value=0, format="localized")
               for c in ["Videos", "Avg views", "Avg likes", "Avg comments", "Link clicks"]},
        },
    )

    offers = [
        Offer(
            creator=str(r["Creator"]), followers=r["Followers"], fit=r["Fit (1-10)"], price=r["Price ($)"],
            videos=r["Videos"], avg_views=r["Avg views"], avg_likes=r["Avg likes"], avg_comments=r["Avg comments"],
            link_clicks=r["Link clicks"],
        )
        for r in table.fillna(0).to_dict("records")
        if str(r["Creator"]).strip()
    ]
    rows = compare_offers(offers)
    best = next((r for r in rows if r["Verdict"] == "Best value"), None)
    if best:
        st.success(
            f"**Best value: {best['Creator']}.** {money(best['Cost per 1,000 views'])} per 1,000 views "
            f"and {money(best['Cost per video'])} a video, with a fit of {best['Fit']:.0f}/10.".replace("$", "\\$")
        )
    else:
        st.info(f"Fill in the price, videos and average views for creators with a fit of {GOOD_FIT} or more to see the best value.",
                icon=":material/edit:")
    ready = [r for r in rows if r["Verdict"] != "Add quote and views"]
    if ready:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Creator": r["Creator"],
                        "Verdict": r["Verdict"],
                        "Fit": r["Fit"],
                        "Cost per video": money(r["Cost per video"]),
                        "Per 1,000 views": money(r["Cost per 1,000 views"]),
                        "Engagement": "n/a" if r["Engagement rate"] is None or not r["Cost per engagement"] else f"{r['Engagement rate']:.1f}%",
                        "Per engagement": money(r["Cost per engagement"]),
                        "Per click": money(r["Cost per click"]),
                    }
                    for r in ready
                ]
            ),
            hide_index=True,
            width="stretch",
            column_config={"Fit": st.column_config.ProgressColumn(min_value=0, max_value=10, format="%d/10")},
        )
    st.caption(
        f"Best value is the lowest cost per 1,000 views among creators with a fit of {GOOD_FIT} or more. "
        "Check engagement and cost per click too: cheap views that nobody acts on are not a bargain. "
        "Use the median of their last 10 to 20 posts, so one viral video doesn't skew it."
    )

with tab_links:
    st.markdown("Give every creator their own link, so you know who actually brings leads.")
    base_url = st.text_input("Landing page URL", value="https://www.fastloanadvance.com/")
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
        st.dataframe(links_df, hide_index=True, width="stretch")
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
        reset_cost()
        try:
            with st.spinner("Writing the brief…"):
                st.session_state["brief"] = write_brief(client, brand, product, goal, creators, f"Campaign: {campaign}.")
                st.session_state["brief_cost"] = run_cost()
        except ClaudeError as e:
            st.error(str(e))
    if st.session_state.get("brief"):
        st.markdown(st.session_state["brief"])
        st.download_button("Download brief (.md)", st.session_state["brief"], "campaign-brief.md")
        st.caption(f"This brief cost about ${st.session_state.get('brief_cost', 0):.2f} in Claude credits.")
