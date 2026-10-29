from core.roi import Plan, project, scenarios, utm_link


def test_project_basic():
    o = project(Plan(fee=1000, views=100000, ctr=0.01, lead_rate=0.1, revenue_per_lead=20))
    assert o.clicks == 1000
    assert o.leads == 100
    assert o.revenue == 2000
    assert o.profit == 1000
    assert o.roi == 1.0
    assert o.cost_per_lead == 10
    assert o.breakeven_leads == 50
    assert o.effective_cpm == 10


def test_zero_fee_and_zero_leads():
    assert project(Plan(0, 1000, 0.01, 0.1, 20)).roi is None
    assert project(Plan(500, 0, 0.01, 0.1, 20)).cost_per_lead is None


def test_scenarios_scale_leads_once():
    s = scenarios(Plan(1000, 100000, 0.01, 0.1, 20))
    assert s["Pessimistic"].leads == 50
    assert s["Optimistic"].leads == 150


def test_utm_link_keeps_query():
    link = utm_link("https://ex.com/apply?ref=1", "TikTok", "Creators Q4", "@Jane.Doe")
    assert link.startswith("https://ex.com/apply?ref=1&")
    assert "utm_source=tiktok" in link
    assert "utm_campaign=creators-q4" in link
    assert "utm_content=jane-doe" in link


def test_run_cost_counts_tokens_and_searches():
    from types import SimpleNamespace

    from core.llm import _track, reset_cost, run_cost

    reset_cost()
    usage = SimpleNamespace(
        input_tokens=100_000, output_tokens=10_000, cache_read_input_tokens=0, cache_creation_input_tokens=0,
        server_tool_use=SimpleNamespace(web_search_requests=8),
    )
    _track(SimpleNamespace(usage=usage))
    assert round(run_cost(), 2) == 0.68  # $0.40 input + $0.20 output + $0.08 searches


def test_quote_cost_uses_only_the_quote_and_real_averages():
    from core.roi import quote_cost

    c = quote_cost(price=600, videos=12, avg_views=5000, avg_likes=200, avg_comments=50)
    assert c.cost_per_video == 50
    assert c.total_views == 60000
    assert c.cpm == 10
    assert c.engagement_rate == 0.05
    assert c.cost_per_engagement == 0.2
    empty = quote_cost(0, 0, 0)
    assert empty.cost_per_video is None and empty.cpm is None and empty.cost_per_engagement is None


def test_compare_offers_picks_cheapest_good_fit():
    from core.roi import Offer, compare_offers

    rows = compare_offers(
        [
            Offer("@cheap_but_off", followers=90000, fit=5, price=300, videos=10, avg_views=20000),
            Offer("@solid", followers=40000, fit=8, price=800, videos=10, avg_views=16000, avg_likes=800, link_clicks=400),
            Offer("@pricey", followers=120000, fit=9, price=2000, videos=10, avg_views=25000),
            Offer("@no_quote", followers=10000, fit=9, price=0, videos=0, avg_views=0),
        ]
    )
    verdicts = {r["Creator"]: r["Verdict"] for r in rows}
    assert verdicts == {"@cheap_but_off": "Weak fit", "@solid": "Best value", "@pricey": "Option 2", "@no_quote": "Add quote and views"}
    solid = rows[1]
    assert solid["Cost per 1,000 views"] == 5 and solid["Engagement rate"] == 5 and solid["Cost per click"] == 2
