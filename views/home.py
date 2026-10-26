from html import escape

import streamlit as st

from core.radar import report_date, report_trends, saved_reports
from core.roi import Plan, project
from core.ui import PAGES, icon

# The ROI Planner's default example, so the numbers on the home page match the tool.
example = Plan(fee=1500, views=80000, ctr=0.01, lead_rate=0.08, revenue_per_lead=35)
out = project(example)

st.html(
    '<div class="band"><h1>Influencer marketing that pays for itself</h1>'
    "<p>Know what to talk about this week, find the right creators, and prove the return before paying anyone.</p>"
    '<div class="chain">'
    f"<div><b>{example.views:,.0f}</b><span>views</span></div>"
    f"<div><b>{out.clicks:,.0f}</b><span>link clicks at 1%</span></div>"
    f"<div><b>{out.leads:,.0f}</b><span>leads at 8%</span></div>"
    f"<div><b>${out.revenue:,.0f}</b><span>revenue at $35 a lead</span></div>"
    f'<div class="win"><b>+${out.profit:,.0f}</b><span>profit on a ${example.fee:,.0f} post</span></div>'
    "</div></div>"
)

reports = saved_reports()
if reports:
    with st.container(border=True):
        left, right = st.columns([5, 1], vertical_alignment="center")
        trends = "".join(f"<li>{escape(t)}</li>" for t in report_trends(reports[0])[:3])
        left.html(
            f'<div class="latest"><span>Top trends this week, from the Radar report of {report_date(reports[0])}</span>'
            f"<ol>{trends}</ol></div>"
        )
        right.page_link(PAGES[1][0], label="Read", icon=":material/arrow_forward:", icon_position="right")

TOOLS = [
    (
        "radar",
        (
            "Spots this week's top topics and standout creators in your segment, with a content idea for each brand. "
            "A new report lands every Monday and Friday."
        ),
    ),
    (
        "scout",
        (
            "Finds real creators on the web and scores their fit, matches each one to a brand, flags brand-safety "
            "risks and drafts the first message."
        ),
    ),
    (
        "roi",
        (
            "Turns a post into views, clicks, leads and revenue, shows the most a creator is worth, and builds "
            "tracking links and a compliant brief."
        ),
    ),
]

st.subheader("Three steps, one tool each")
for (name, text), (path, title, *_, question) in zip(TOOLS, PAGES[1:]):
    with st.container(border=True):
        left, right = st.columns([5, 1], vertical_alignment="center")
        with left:
            st.html(
                f'<div class="tool"><div class="tool-icon">{icon(name)}</div>'
                f'<div><h3>{title}</h3><div class="q">{question}</div><p>{text}</p></div></div>'
            )
        right.page_link(path, label="Open", icon=":material/arrow_forward:", icon_position="right")

st.caption(
    "Opening the suite and using the ROI Planner is free. Claude runs only when you press a research button, "
    "at about $1 a scan, and every result shows what it cost."
)
