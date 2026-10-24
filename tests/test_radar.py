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
