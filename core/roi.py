"""Creator ROI math. Pure functions so they are easy to test."""

from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

SCENARIOS = {"Pessimistic": 0.5, "Realistic": 1.0, "Optimistic": 1.5}


@dataclass
class Plan:
    fee: float  # what we pay the creator, USD
    views: float  # expected views of the post
    ctr: float  # link clicks / views, as a fraction
    lead_rate: float  # leads / clicks, as a fraction
    revenue_per_lead: float  # what a lead is worth to us, USD


@dataclass
class Outcome:
    clicks: float
    leads: float
    revenue: float
    profit: float
    roi: float | None  # profit / fee
    cost_per_lead: float | None
    breakeven_leads: float | None
    max_fee: float  # the most we could pay and still break even
    effective_cpm: float | None


def project(plan: Plan, multiplier: float = 1.0) -> Outcome:
    """Project results. The multiplier scales clicks (and so leads) for scenarios."""
    clicks = plan.views * plan.ctr * multiplier
    leads = clicks * plan.lead_rate
    revenue = leads * plan.revenue_per_lead
    profit = revenue - plan.fee
    return Outcome(
        clicks=clicks,
        leads=leads,
        revenue=revenue,
        profit=profit,
        roi=profit / plan.fee if plan.fee else None,
        cost_per_lead=plan.fee / leads if leads else None,
        breakeven_leads=plan.fee / plan.revenue_per_lead if plan.revenue_per_lead else None,
        max_fee=revenue,
        effective_cpm=plan.fee / plan.views * 1000 if plan.views else None,
    )


def scenarios(plan: Plan) -> dict[str, Outcome]:
    return {name: project(plan, m) for name, m in SCENARIOS.items()}


def slug(text: str) -> str:
    cleaned = "".join(c if c.isalnum() else "-" for c in text.lower().lstrip("@"))
    return "-".join(part for part in cleaned.split("-") if part)


def utm_link(base_url: str, source: str, campaign: str, content: str, medium: str = "influencer") -> str:
    """Add UTM parameters to a landing page URL, keeping any existing query."""
    parts = urlparse(base_url)
    query = dict(parse_qsl(parts.query))
    query.update(
        {
            "utm_source": slug(source),
            "utm_medium": slug(medium),
            "utm_campaign": slug(campaign),
            "utm_content": slug(content),
        }
    )
    return urlunparse(parts._replace(query=urlencode(query)))
