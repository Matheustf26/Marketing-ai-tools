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
