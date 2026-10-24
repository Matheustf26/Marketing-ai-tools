"""Campaign brief generator."""

import anthropic

from core.llm import check_refusal, create, text_of

BRIEF_SYSTEM = """You write influencer campaign briefs that creators actually follow.

Every brief must:
- Be short and skimmable, with clear do's and don'ts.
- Require clear paid-partnership disclosure that follows FTC Endorsement Guides: #ad or "Paid partnership" at the start of the caption and said out loud in video, plus the platform's paid-partnership label.
- In financial products, ban promises of guaranteed approval, "no credit check" claims unless verified, specific rates or amounts not provided by the brand, and urgency that pressures people into borrowing.
- End with a "Needs legal review" list of every claim that should be checked before going live."""


def write_brief(client: anthropic.Anthropic, brand: str, product: str, goal: str, creators: str, tracking: str) -> str:
    prompt = f"""Write a campaign brief.

Brand and positioning: {brand}
Product / offer: {product}
Campaign goal and KPI: {goal}
Creators: {creators}
Tracking: each creator gets their own UTM link. {tracking}

Sections: Objective, Key message, Talking points, Content format and deliverables, Do's, Don'ts,
Disclosure rules, Link and tracking, Timeline, Needs legal review."""
    response = create(
        client,
        max_tokens=16000,
        system=BRIEF_SYSTEM,
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )
    check_refusal(response)
    return text_of(response)
