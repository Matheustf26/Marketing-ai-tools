"""Creator Scout: find candidate creators for a niche with Claude + web search."""

from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from core.llm import check_refusal, parse, stream, text_of
from core.roi import GOOD_FIT

WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 12}
MAX_CONTINUATIONS = 5


class Creator(BaseModel):
    name: str = Field(description="Creator's name only, with no channel name or notes in parentheses")
    handle: str = Field(description="Their @handle on this platform, starting with @")
    platform: Literal["Instagram", "TikTok", "YouTube", "X"] = Field(description="The platform the follower count is for")
    followers: int = Field(description="Follower count on that platform as a whole number, e.g. 61300")
    content_summary: str = Field(description="One sentence on what they post")
    audience_fit: str = Field(description="Why their audience matches the brief")
    avg_views: int = Field(default=0, description="Average views per post if a source reports it, otherwise 0")
    recent_activity: str = Field(
        default="", description="A recent post or source showing they are active in this niche, with its date if known"
    )
    fit_score: int = Field(description="1 to 10, how well they match the brief")
    best_brand: str = Field(description="Which of the listed brands fits best, or 'Any'")
    brand_safety_flags: list[str] = Field(
        description="Risks: misleading money claims, controversy, competitor deals, low engagement. Empty if none found."
    )
    outreach_message: str = Field(description="Short, personal first DM (3 to 4 sentences)")
    source_url: str = Field(description="Page where the handle or follower count was found")


class ScoutResult(BaseModel):
    search_summary: str = Field(description="One short sentence on where the creators were found")
    creators: list[Creator]


def clean_handle(handle: str) -> str:
    """'instagram.com/jane/' or 'jane' -> '@jane'."""
    handle = handle.strip().rstrip("/").split("/")[-1].lstrip("@")
    return f"@{handle}" if handle else ""


def format_followers(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}K".replace(".0K", "K")
    return str(n)


RESEARCH_SYSTEM = """You are an influencer marketing researcher. You find real creators with web search.

Rules:
- Only list creators you actually found in search results. Never invent names, handles, URLs or numbers.
- Prefer lists, articles and directories that name creators in the niche (e.g. "top personal finance TikTokers"), then confirm each profile.
- Every creator you list needs three things from a source: their @handle, the platform, and a follower count on
  that platform. For promising creators, run one quick search on their handle (e.g. "@handle tiktok followers")
  to find them. If you can't find all three, leave the creator out.
- Confirm every creator with a search on their own handle. Prefer sources from the last 12 months.
- Only keep creators who post about this niche regularly and were active in the last 90 days. Note a recent post or
  source as proof, with its date when you have it. If a source reports average views per post, note it.
- Leave out brand accounts, agencies, inactive accounts and anyone whose fit would be below 7 out of 10.
  Fewer strong matches are better than a long list of weak ones: return fewer than asked rather than pad the list.
- Flag brand-safety risks honestly: get-rich-quick claims, controversies, promoting competitors, signs of fake followers.
- In regulated categories (finance, health), note anything that could create compliance risk."""


def build_research_prompt(niche: str, platforms: list[str], country: str, size: str, brands: str, count: int) -> str:
    return f"""Find up to {count} creators for this influencer campaign. Only strong, verified matches.

Niche / product: {niche}
Platforms: {", ".join(platforms)}
Country / audience: {country}
Creator size: {size}

Brands we might pair them with:
{brands}

For each creator, give: name, @handle, platform, follower count on that platform, average views per post if a
source reports it, a recent post that proves they are active in the niche, what they post, why the audience fits,
a 1-10 fit score, the best brand match, brand-safety flags, and the source URL.
Then write a short, personal first outreach DM for each one."""


def research(client: anthropic.Anthropic, prompt: str, on_progress=None) -> str:
    """Run the web-search research turn, resuming if the server pauses a long turn."""
    messages = [{"role": "user", "content": prompt}]

    def show_search(event):
        # Each finished web search block carries its query: show it as it happens.
        if on_progress and event.type == "content_block_stop" and event.content_block.type == "server_tool_use":
            query = event.content_block.input
            text = query.get("query", "") if isinstance(query, dict) else ""
            if text:  # other server tools (e.g. result filtering) have no query
                on_progress(text)

    response = None
    for _ in range(MAX_CONTINUATIONS + 1):
        response = stream(
            client,
            on_event=show_search,
            max_tokens=16000,
            system=RESEARCH_SYSTEM,
            tools=[WEB_SEARCH],
            output_config={"effort": "medium"},
            messages=messages,
        )
        check_refusal(response)
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})
    return text_of(response)


def structure(client: anthropic.Anthropic, notes: str) -> ScoutResult:
    """Turn the research notes into a validated table."""
    response = parse(
        client,
        max_tokens=16000,
        output_config={"effort": "low"},
        output_format=ScoutResult,
        messages=[
            {
                "role": "user",
                "content": "Convert these research notes into the schema. Keep only creators whose notes give an "
                "@handle, one platform and a follower count on that platform, and who fit the brief well. Leave out everyone else, and "
                "do not add anyone new.\n\n" + notes,
            }
        ],
    )
    check_refusal(response)
    result = response.parsed_output
    for c in result.creators:
        c.handle = clean_handle(c.handle)
    result.creators = [c for c in result.creators if c.handle and c.followers > 0 and c.fit_score >= GOOD_FIT]
    return result
