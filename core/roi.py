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


@dataclass
class QuoteCost:
    """What a creator's quote buys, from the price and the creator's real averages. No guesses."""

    cost_per_video: float | None
    total_views: float
    cpm: float | None  # cost per 1,000 views
    engagement_rate: float | None  # (likes + comments) / views
    cost_per_engagement: float | None


def quote_cost(price: float, videos: int, avg_views: float, avg_likes: float = 0, avg_comments: float = 0) -> QuoteCost:
    total_views = avg_views * videos
    engagements = (avg_likes + avg_comments) * videos
    return QuoteCost(
        cost_per_video=price / videos if videos else None,
        total_views=total_views,
        cpm=price / total_views * 1000 if total_views else None,
        engagement_rate=(avg_likes + avg_comments) / avg_views if avg_views else None,
        cost_per_engagement=price / engagements if engagements else None,
    )


GOOD_FIT = 7  # fit score (1-10) a creator needs to be recommended


@dataclass
class Offer:
    """One creator's quote and real numbers, as typed into the comparison."""

    creator: str
    followers: float
    fit: float  # 1-10, from Creator Scout or our own review
    price: float
    videos: float
    avg_views: float
    avg_likes: float = 0
    avg_comments: float = 0
    link_clicks: float = 0  # total link clicks the package is expected to bring, if the creator shares past results


def compare_offers(offers: list[Offer]) -> list[dict]:
    """Cost of each quote side by side, and which good-fit creator gives the most for the money."""
    rows = []
    for o in offers:
        c = quote_cost(o.price, int(o.videos), o.avg_views, o.avg_likes, o.avg_comments)
        complete = bool(o.price and o.videos and o.avg_views)
        rows.append(
            {
                "Creator": o.creator,
                "Cost per video": c.cost_per_video,
                "Cost per 1,000 views": c.cpm,
                "Engagement rate": None if c.engagement_rate is None else c.engagement_rate * 100,
                "Cost per engagement": c.cost_per_engagement,
                "Cost per click": o.price / o.link_clicks if o.link_clicks else None,
                "Fit": o.fit,
                "_complete": complete,
            }
        )
    ranked = sorted(
        (r for r in rows if r["_complete"] and r["Fit"] >= GOOD_FIT),
        key=lambda r: r["Cost per 1,000 views"],
    )
    for r in rows:
        if not r["_complete"]:
            r["Verdict"] = "Add quote and views"
        elif r["Fit"] < GOOD_FIT:
            r["Verdict"] = "Weak fit"
        elif r is ranked[0]:
            r["Verdict"] = "Best value"
        else:
            r["Verdict"] = f"Option {ranked.index(r) + 1}"
        del r["_complete"]
    return rows


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
