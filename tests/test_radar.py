import datetime as dt

from core.radar import Example, RadarReport, Trend, slug, to_markdown


def test_to_markdown_lists_trends_and_sources():
    report = RadarReport(
        headline="Cash stuffing is back.",
        trends=[
            Trend(
                topic="Cash stuffing",
                why_now="Inflation posts went viral.",
                signal="2M views on a top video",
                examples=[Example(creator="@budgetgirl", platform="TikTok", what_they_did="Envelope tour",
                                  engagement="2M views", url="https://example.com/a")],
                content_idea="Show a weekly envelope budget.",
                caution="None",
            )
        ],
        formats=["Green-screen explainers"],
        sources_note="Media coverage of TikTok.",
    )
    md = to_markdown(report, "personal finance", dt.date(2026, 10, 26))
    assert "# Creator Radar: personal finance" in md
    assert "## 1. Cash stuffing" in md
    assert "[source](https://example.com/a)" in md
    assert "Caution" not in md
    assert "- Green-screen explainers" in md


def test_slug():
    assert slug("Personal finance, budgeting & credit") == "personal-finance-budgeting-credit"


def test_saved_reports_have_a_date_and_headline():
    from core.radar import report_date, report_trends, saved_reports

    latest = saved_reports()[0]
    assert report_date(latest).split(",")[0] in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    assert len(report_trends(latest)) >= 3


def test_searches_are_shown_once():
    from types import SimpleNamespace
    from unittest.mock import patch

    from core import scout

    block = SimpleNamespace(type="server_tool_use", input={"query": "personal finance tiktok"})
    events = [SimpleNamespace(type="content_block_stop", content_block=block)] * 3
    final = SimpleNamespace(content=[], stop_reason="end_turn")

    def fake_stream(client, on_event, **kw):
        for e in events:
            on_event(e)
        return final

    shown = []
    with patch.object(scout, "stream", fake_stream), patch.object(scout, "text_of", lambda r: ""):
        scout.research(None, "prompt", on_progress=shown.append)
    assert shown == ["personal finance tiktok"]
    assert scout.build_research_prompt("x", ["TikTok"], "US", "Micro", "b", 5).startswith("Today is ")
