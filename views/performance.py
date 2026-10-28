from html import escape

import streamlit as st

from core.performance import BLANK, LIMITS, Post, compare, fmt, recommend
from core.ui import header

header("performance", "Creator Performance", "Compare two posts by what people did per 1,000 views, not by raw views, and decide what to post next.")

FIELDS = [
    ("views", "Views"),
    ("shares", "Shares"),
    ("visits", "Profile visits"),
    ("saves", "Saves (optional)"),
    ("clicks", "Link clicks (optional)"),
]


def clear():
    for side, values in BLANK.items():
        for key, value in values.items():
            st.session_state[f"{side}_{key}"] = value


if "A_views" not in st.session_state:
    clear()

st.subheader("Enter results")
with st.container(border=True):
    head = st.columns([1.3, 2, 2], vertical_alignment="center")
    head[0].markdown("**Post**")
    names = {side: col.text_input(f"Post {side}", key=f"{side}_name", label_visibility="collapsed") or f"Post {side}"
             for side, col in zip("AB", head[1:])}
    values = {"A": {}, "B": {}}
    for key, label in FIELDS:
        row = st.columns([1.3, 2, 2], vertical_alignment="center")
        row[0].markdown(label)
        for side, col in zip("AB", row[1:]):
            values[side][key] = col.number_input(
                f"{label}, post {side}", min_value=0, step=100, key=f"{side}_{key}", label_visibility="collapsed"
            )
    posts = {side: Post(name=names[side], **values[side]) for side in "AB"}
st.button("Clear", icon=":material/restart_alt:", on_click=clear)

a, b = posts["A"], posts["B"]
if not (a.views and b.views):
    st.info("Enter the views and the shares or profile visits of two posts to compare them.", icon=":material/edit:")
    st.caption("This tool runs no Claude call, so it costs nothing to use.")
else:
    rates = compare(a, b)

    st.subheader("Rates per 1,000 views")
    rows = "".join(
        f"<tr><td>{r.label}</td>"
        f'<td class="{"win" if r.winner == "A" else ""}">{fmt(r.a)}</td>'
        f'<td class="{"win" if r.winner == "B" else ""}">{fmt(r.b)}</td>'
        f"<td>{r.ratio}</td></tr>"
        for r in rates
    )
    st.html(
        '<table class="rates"><thead><tr><th>Rate</th>'
        f"<th>{escape(a.name)}</th><th>{escape(b.name)}</th><th>Difference</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )
    st.caption(f"Views: {escape(a.name)} {a.views:,}, {escape(b.name)} {b.views:,}. The higher rate in each row is in green.")

    st.subheader("Recommendation")
    with st.container(border=True):
        for paragraph in recommend(a, b, rates):
            st.markdown(paragraph)

    st.subheader("What these numbers can't tell you")
    st.markdown("\n".join(f"- {item}" for item in LIMITS))
    st.caption("Hook ideas are hypotheses to test. This tool doesn't predict virality. It runs no Claude call, so it costs nothing to use.")
