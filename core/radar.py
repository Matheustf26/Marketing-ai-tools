"""Trend Radar: what's working in a social media segment this week, with content ideas.

Runs from the Streamlit page on demand, or from the command line on a schedule:
    python -m core.radar --segment "personal finance" --out reports
"""

import argparse
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic
from pydantic import BaseModel, Field

from core.llm import parse, stream, text_of

WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 20}
MAX_CONTINUATIONS = 5


class Example(BaseModel):
    creator: str = Field(description="Creator name or @handle")
    platform: str
    what_they_did: str = Field(description="One sentence on the post or format")
    engagement: str = Field(description="Views, likes or comments as reported by the source, or 'not reported'")
    url: str = Field(description="Source URL where this was found")


class Trend(BaseModel):
    topic: str = Field(description="Short name of the trend or topic")
    why_now: str = Field(description="Why it's getting attention this week, in one or two sentences")
    signal: str = Field(description="Evidence of momentum: numbers, coverage, platform data, as reported")
    examples: list[Example] = Field(description="Up to 3 posts or creators that stood out on this topic")
    content_idea: str = Field(description="A concrete post idea for our brands built on this trend")
    caution: str = Field(description="Compliance or brand-safety risk, or 'None'")


class RadarReport(BaseModel):
    headline: str = Field(description="The single most important takeaway this week, one sentence")
    trends: list[Trend]
    formats: list[str] = Field(description="Content formats performing well this week (e.g. 'green-screen explainers')")
    sources_note: str = Field(description="One sentence on which kinds of sources were used and their limits")


RADAR_SYSTEM = """You are a social media trend analyst for a marketing team.

Rules:
- Use web search to find what is getting attention in the given segment on Instagram and TikTok in the last 7 days:
  news and viral moments, trend roundups, creator posts covered by media, platform trend pages, Reddit and Google Trends coverage.
- You cannot open Instagram or TikTok directly. Rely on public pages that report on them, and say so.
- Only report creators, posts and numbers you found in sources. Never invent engagement figures.
- Prefer recent sources. If something is older than two weeks, say so or leave it out.
- Content ideas must fit a regulated financial brand: no guaranteed outcomes, no pressure to borrow."""


def build_prompt(segment: str, platforms: list[str], audience: str, brands: str, count: int, today: dt.date) -> str:
    return f"""Today is {today.isoformat()}. Build this week's trend radar.

Segment: {segment}
Platforms: {", ".join(platforms)}
Audience: {audience}
Our brands:
{brands}

Find the top {count} topics or trends in this segment right now. For each: why it's trending now, the evidence,
up to 3 creators or posts that stood out (with source links and engagement if reported), one content idea for our
brands, and any compliance risk. Also list the content formats that are performing well."""


def research(client: anthropic.Anthropic, prompt: str, on_progress=None) -> str:
    messages = [{"role": "user", "content": prompt}]

    def show_search(event):
        if on_progress and event.type == "content_block_stop" and event.content_block.type == "server_tool_use":
            query = event.content_block.input
            on_progress(query.get("query", "") if isinstance(query, dict) else "")

    response = None
    for _ in range(MAX_CONTINUATIONS + 1):
        response = stream(
            client,
            on_event=show_search,
            max_tokens=16000,
            system=RADAR_SYSTEM,
            tools=[WEB_SEARCH],
            output_config={"effort": "medium"},
            messages=messages,
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("Claude declined this request. Try rephrasing the segment.")
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})
    return text_of(response)


def structure(client: anthropic.Anthropic, notes: str) -> RadarReport:
    response = parse(
        client,
        max_tokens=16000,
        output_config={"effort": "low"},
        output_format=RadarReport,
        messages=[
            {
                "role": "user",
                "content": "Convert these trend research notes into the schema. Keep every source URL. "
                "Do not add anything that is not in the notes.\n\n" + notes,
            }
        ],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request. Try rephrasing the segment.")
    return response.parsed_output


def to_markdown(report: RadarReport, segment: str, today: dt.date) -> str:
    lines = [f"# Trend Radar: {segment}", "", f"_Week of {today.isoformat()}_", "", f"**{report.headline}**", ""]
    for i, t in enumerate(report.trends, 1):
        lines += [f"## {i}. {t.topic}", "", f"**Why now:** {t.why_now}", "", f"**Signal:** {t.signal}", ""]
        for e in t.examples:
            lines.append(f"- **{e.creator}** ({e.platform}): {e.what_they_did} · {e.engagement} · [source]({e.url})")
        lines += ["", f"**Content idea:** {t.content_idea}", ""]
        if t.caution and t.caution.lower() != "none":
            lines += [f"**Caution:** {t.caution}", ""]
    if report.formats:
        lines += ["## Formats working this week", ""] + [f"- {f}" for f in report.formats] + [""]
    lines += [f"_{report.sources_note}_", ""]
    return "\n".join(lines)


def today() -> dt.date:
    """The team works in Los Angeles."""
    return dt.datetime.now(tz=ZoneInfo("America/Los_Angeles")).date()


def slug(text: str) -> str:
    return "-".join("".join(c if c.isalnum() else " " for c in text.lower()).split())[:40]


DEFAULT_BRANDS = """Fast Loan Advance: fast help for unexpected expenses. Direct, upbeat.
Fast Loan Direct: simple and transparent, compare offers and costs. Clear, no jargon.
Grace Loan Advance: second chances and financial education for people rebuilding credit. Warm, non-judgmental."""


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a trend radar report to a markdown file.")
    parser.add_argument("--segment", default="personal finance, budgeting, credit and money tips")
    parser.add_argument("--audience", default="United States, ages 22-40")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()

    day = today()
    client = anthropic.Anthropic()
    prompt = build_prompt(args.segment, ["Instagram", "TikTok"], args.audience, DEFAULT_BRANDS, args.count, day)
    notes = research(client, prompt, on_progress=lambda q: print("search:", q))
    report = structure(client, notes)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{day.isoformat()}-{slug(args.segment)}.md"
    path.write_text(to_markdown(report, args.segment, day))
    print("wrote", path)


if __name__ == "__main__":
    main()
