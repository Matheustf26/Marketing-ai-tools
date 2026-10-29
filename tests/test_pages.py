"""Smoke tests: pages render, and Scout works end to end with a fake Claude client."""

from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from core.scout import Creator, ScoutResult


def test_every_page_renders():
    at = AppTest.from_file("../Home.py", default_timeout=30).run()
    assert not at.exception, at.exception
    for page in ["views/radar.py", "views/scout.py", "views/roi.py", "views/performance.py"]:
        at.switch_page(page).run()
        assert not at.exception, (page, at.exception)


def test_scout_flow():
    creator = Creator(
        name="Jane Money", handle="@janemoney", platform="TikTok",
        followers=85000, content_summary="Budgeting tips", audience_fit="Young adults on tight budgets",
        fit_score=8, best_brand="Grace Loan Advance", brand_safety_flags=[], outreach_message="Hi Jane!",
        source_url="https://example.com/list",
    )
    search = SimpleNamespace(type="server_tool_use", input={"query": "personal finance tiktok creators"})
    text = SimpleNamespace(type="text", text="notes")
    final = SimpleNamespace(content=[search, text], stop_reason="end_turn")
    events = [SimpleNamespace(type="content_block_stop", content_block=search)]

    class FakeStream:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def __iter__(self):
            return iter(events)

        def get_final_message(self):
            return final

    fake = SimpleNamespace(
        beta=SimpleNamespace(
            messages=SimpleNamespace(
                stream=lambda **kw: FakeStream(),
                parse=lambda **kw: SimpleNamespace(
                    parsed_output=ScoutResult(search_summary="Found on lists.", creators=[creator]),
                    stop_reason="end_turn",
                ),
            )
        )
    )
    with patch("anthropic.Anthropic", return_value=fake):
        at = AppTest.from_file("../Home.py", default_timeout=30)
        at.session_state["api_key"] = "test"
        at.run()
        at.switch_page("views/scout.py").run()
        at.button[0].click().run()
        assert not at.exception, at.exception
        assert at.session_state["scout_result"].creators[0].handle == "@janemoney"
        assert any("personal finance tiktok creators" in m.value for m in at.markdown)
        next(b for b in at.button if b.label == "Compare these creators in ROI Planner").click().run()
        assert not at.exception, at.exception
        assert any("Loaded 1 creators" in s.value for s in at.success)


def test_handles_and_followers_are_standardized():
    from core.scout import clean_handle, format_followers

    assert clean_handle("https://www.instagram.com/janemoney/") == "@janemoney"
    assert clean_handle("janemoney") == "@janemoney"
    assert clean_handle("") == ""
    assert format_followers(61300) == "61.3K"
    assert format_followers(1_000_000) == "1M"


def test_radar_trend_opens_scout_prefilled():
    at = AppTest.from_file("../Home.py", default_timeout=30).run()
    at.switch_page("views/radar.py").run()
    trend = at.selectbox(key="trend_saved").value
    at.button(key="scout_saved").click().run()
    assert not at.exception, at.exception
    assert at.session_state["scout_trend"] == trend
    assert any(trend in t.value for t in at.text_input)
