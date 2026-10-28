"""Shared look: Fast Loan Advance branding, top bar with menu, page banner and footer.

Design rules live in .claude/skills/fla-brand-ui/SKILL.md.
"""

import base64

import streamlit as st

from core.llm import api_key_menu

BRAND = "Fast Loan Advance"
LOGO = "https://www.fastloanadvance.com/images/fla-logo.svg"

# Inline stroke icons, so they look the same in every browser.
ICONS = {
    "radar": '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/>'
    '<path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/><path d="M17.99 11.66A6 6 0 0 1 15.77 16.67"/>'
    '<circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>',
    "scout": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/><circle cx="11" cy="9.5" r="2.5"/>'
    '<path d="M7 15a4.5 4.5 0 0 1 8 0"/>',
    "roi": '<circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 18V6"/>',
    "performance": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
}

CSS = """
<style>
:root {--teal: #043D46; --mist: #EEF4F3; --line: #D5E2E0; --slate: #4E6466; --signal: #18B37E;}
.block-container {padding-top: 1.6rem; max-width: 1120px;}
header[data-testid="stHeader"] {display: none;}
.topbar {display: flex; align-items: center; gap: 14px; min-height: 44px;}
.topbar img {height: 32px; width: auto; color: var(--teal); font-weight: 800; font-size: 1.1rem;}
.topbar .sep {width: 1px; height: 24px; background: var(--line);}
.topbar .suite {font-weight: 700; color: var(--teal); font-size: 1rem;}
.band {background: var(--teal); color: #fff; border-radius: 20px; padding: 28px 32px; margin: 4px 0 1.6rem;}
.band-row {display: flex; gap: 20px; align-items: center;}
.band-icon {flex: 0 0 56px; height: 56px; border-radius: 16px; border: 1px solid rgba(255,255,255,.25);
  display: flex; align-items: center; justify-content: center;}
.band-icon img {width: 28px; height: 28px;}
.band h1 {color: #fff; font-size: 2.1rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.12; margin: 0 0 6px; padding: 0;}
.band p {color: rgba(255,255,255,.82); font-size: 1.02rem; margin: 0; max-width: 680px;}
.chain {display: grid; grid-template-columns: repeat(5, 1fr); margin-top: 26px; border-top: 1px solid rgba(255,255,255,.2);}
.chain div {padding: 16px 16px 0 0;}
.chain b {display: block; font-size: 1.7rem; font-weight: 800; letter-spacing: -.02em;}
.chain span {color: rgba(255,255,255,.7); font-size: .88rem;}
.chain .win b {color: #7BE3BC;}
.latest span {color: var(--signal); font-weight: 700; font-size: .92rem;}
.latest ol {color: var(--teal); font-weight: 700; font-size: 1.05rem; line-height: 1.6; margin: 6px 0 0; padding-left: 1.3rem;}
.tool {display: flex; gap: 18px; align-items: flex-start;}
.tool-icon {flex: 0 0 48px; height: 48px; border-radius: 14px; background: var(--mist); display: flex;
  align-items: center; justify-content: center;}
.tool-icon img {width: 24px; height: 24px;}
.tool h3 {font-size: 1.15rem; font-weight: 800; color: var(--teal); margin: 0 0 2px; padding: 0;}
.tool .q {color: var(--signal); font-weight: 700; font-size: .92rem; margin-bottom: 4px;}
.tool p {color: var(--slate); margin: 0; line-height: 1.5;}
.rates {width: 100%; border-collapse: collapse; font-size: 1rem;}
.rates th {text-align: left; color: var(--slate); font-weight: 600; font-size: .88rem; padding: 10px 12px; border-bottom: 1px solid var(--line);}
.rates td {padding: 12px; border-bottom: 1px solid var(--line); color: var(--teal);}
.rates td.win {color: var(--signal); font-weight: 800;}
[data-testid="stMetric"] {background: var(--mist); border-radius: 14px; padding: 14px 18px; min-height: 120px;}
[data-testid="stMetricValue"] {font-weight: 800; color: var(--teal);}
.footer {margin-top: 3rem; padding-top: 14px; border-top: 1px solid var(--line); color: var(--slate); font-size: .82rem;}
@media (max-width: 640px) {
  .band {padding: 22px;} .band h1 {font-size: 1.55rem;} .band-icon, .topbar .sep, .topbar .suite {display: none;}
  .chain {grid-template-columns: repeat(2, 1fr);}
}
</style>
"""


def icon(name: str, color: str = "#043D46") -> str:
    """An <img> with the SVG inlined as data, since st.html strips raw <svg> tags."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'
    )
    return f'<img alt="" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'



# path, title, menu icon, url, what it answers
PAGES = [
    ("views/home.py", "Home", ":material/home:", "", "Overview"),
    ("views/radar.py", "Creator Radar", ":material/radar:", "creator-radar", "What should we talk about?"),
    ("views/scout.py", "Creator Scout", ":material/person_search:", "creator-scout", "Who should we work with?"),
    ("views/roi.py", "Creator ROI Planner", ":material/payments:", "creator-roi-planner", "Does it make money?"),
    ("views/performance.py", "Creator Performance", ":material/insights:", "creator-performance", "What actually worked?"),
]


def navigation():
    """Set up the app shell (styles, top bar, menu) and return the page to run. Called once, from Home.py."""
    st.set_page_config(page_icon=":material/bolt:", layout="wide", initial_sidebar_state="collapsed")
    pages = [st.Page(path, title=title, icon=ic, url_path=url or None, default=not url) for path, title, ic, url, _ in PAGES]
    current = st.navigation(pages, position="hidden")
    st.html(CSS)

    left, right = st.columns([5, 1], vertical_alignment="center")
    with left:
        st.html(
            f'<div class="topbar"><img src="{LOGO}" alt="{BRAND}"><span class="sep"></span>'
            '<span class="suite">Creator Suite</span></div>'
        )
    with right, st.popover("Menu", icon=":material/menu:", width="stretch"):
        for page, (*_, question) in zip(pages, PAGES):
            st.page_link(page, help=question, width="stretch")
        st.divider()
        api_key_menu()
    return current


def header(icon_name: str, title: str, subtitle: str) -> None:
    st.html(
        f'<div class="band"><div class="band-row"><div class="band-icon">{icon(icon_name, "#FFFFFF")}</div>'
        f"<div><h1>{title}</h1><p>{subtitle}</p></div></div></div>"
    )


def footer() -> None:
    st.html(
        f'<div class="footer">Creator Suite is a concept demo for {BRAND}, built by Matheus Falcão with Claude. '
        "Internal marketing tool, not a customer-facing page.</div>"
    )
