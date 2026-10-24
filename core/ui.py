"""Shared look: page setup, header banner, cards and sidebar."""

import streamlit as st

from core.llm import api_key_sidebar

CSS = """
<style>
.block-container {padding-top: 3.6rem; max-width: 1180px;}
.hero {
  background: linear-gradient(120deg, #5B3DF5 0%, #8B5CF6 55%, #F472B6 100%);
  border-radius: 20px; padding: 28px 32px; margin-bottom: 1.4rem; color: #fff;
  box-shadow: 0 12px 32px -18px rgba(91, 61, 245, .55);
}
.hero .eyebrow {font-size: .78rem; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; opacity: .85;}
.hero .title {font-family: "Plus Jakarta Sans", sans-serif; font-size: 2.3rem; font-weight: 800; line-height: 1.15; margin: 6px 0 8px;}
.hero .subtitle {font-size: 1.05rem; opacity: .92; max-width: 760px; margin: 0;}
.card-icon {
  width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; background: #EFEBFF; margin-bottom: 10px;
}
.card-title {font-family: "Plus Jakarta Sans", sans-serif; font-weight: 700; font-size: 1.15rem; margin-bottom: 4px;}
.card-tag {color: #5B3DF5; font-weight: 600; font-size: .85rem; margin-bottom: 8px;}
.card-text {color: #55536B; font-size: .95rem; line-height: 1.5; min-height: 96px;}
.steps {display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: 6px;}
.step {background: #F5F4FC; border: 1px solid #E7E5F3; border-radius: 999px; padding: 7px 14px; font-size: .9rem; font-weight: 500;}
.arrow {color: #A5A1C4; font-weight: 700;}
[data-testid="stMetric"] {
  background: #F5F4FC; border: 1px solid #E7E5F3; border-radius: 14px; padding: 14px 18px; min-height: 128px;
}
[data-testid="stMetricValue"] {font-family: "Plus Jakarta Sans", sans-serif; font-weight: 800;}
.brand {font-family: "Plus Jakarta Sans", sans-serif; font-weight: 800; font-size: 1.25rem; color: #1B1A2E;}
.brand span {color: #5B3DF5;}
.brand-sub {color: #6E6B88; font-size: .85rem; margin-bottom: 4px;}
</style>
"""


def setup(page_title: str, icon: str) -> None:
    """Call first on every page."""
    st.set_page_config(page_title=f"{page_title} · Creator Suite", page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.sidebar.markdown(
        '<div class="brand">Creator <span>Suite</span></div>'
        '<div class="brand-sub">Influencer marketing tools built with Claude</div>',
        unsafe_allow_html=True,
    )
    api_key_sidebar()


def header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{eyebrow}</div>'
        f'<div class="title">{title}</div><p class="subtitle">{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def card(icon: str, title: str, tag: str, text: str, page: str, link_label: str) -> None:
    with st.container(border=True):
        st.markdown(
            f'<div class="card-icon">{icon}</div><div class="card-title">{title}</div>'
            f'<div class="card-tag">{tag}</div><div class="card-text">{text}</div>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label=link_label, icon=":material/arrow_forward:")


def steps(items: list[str]) -> None:
    parts = []
    for i, item in enumerate(items):
        if i:
            parts.append('<span class="arrow">→</span>')
        parts.append(f'<span class="step">{item}</span>')
    st.markdown(f'<div class="steps">{"".join(parts)}</div>', unsafe_allow_html=True)
