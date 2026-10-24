"""Smoke tests: pages render, and Scout works end to end with a fake Claude client."""

from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from core.scout import Creator, ScoutResult


def test_home_and_roi_render():
    for page in ["Home.py", "pages/2_Creator_ROI_Planner.py"]:
        at = AppTest.from_file("../" + page, default_timeout=30).run()
        assert not at.exception, at.exception


def test_scout_flow():
    creator = Creator(
        name="Jane Money", handle="@janemoney", platform="TikTok", profile_url="https://tiktok.com/@janemoney",
        followers="85K", content_summary="Budgeting tips", audience_fit="Young adults on tight budgets",
        fit_score=8, best_brand="Grace Loan Advance", brand_safety_flags=[], outreach_message="Hi Jane!",
        source_url="https://example.com/list",
    )
    search = SimpleNamespace(type="server_tool_use", input={"query": "personal finance tiktok creators"})
    text = SimpleNamespace(type="text", text="notes")
    fake = SimpleNamespace(
        beta=SimpleNamespace(
            messages=SimpleNamespace(
                create=lambda **kw: SimpleNamespace(content=[search, text], stop_reason="end_turn"),
                parse=lambda **kw: SimpleNamespace(
                    parsed_output=ScoutResult(search_summary="Found on lists.", creators=[creator]),
                    stop_reason="end_turn",
                ),
            )
        )
    )
    with patch("anthropic.Anthropic", return_value=fake):
        at = AppTest.from_file("../pages/1_Creator_Scout.py", default_timeout=30)
        at.session_state["api_key"] = "test"
        at.run()
        at.button[0].click().run()
        assert not at.exception, at.exception
        assert at.session_state["scout_result"].creators[0].handle == "@janemoney"
