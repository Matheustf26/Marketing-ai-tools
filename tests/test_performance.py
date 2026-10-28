from core.performance import BLANK, Post, compare, ratio, recommend


def test_rates_and_recommendation():
    a = Post("Post 1", views=50_000, shares=50, visits=25)
    b = Post("Post 2", views=10_000, shares=200, visits=100)
    rates = compare(a, b)
    assert [(r.a, r.b, r.winner, r.ratio) for r in rates] == [
        (1.0, 20.0, "B", "Post 2 is 20x Post 1"),
        (0.5, 10.0, "B", "Post 2 is 20x Post 1"),
    ]
    text = " ".join(recommend(a, b, rates))
    assert "Build on Post 2" in text
    assert "Post 1 reached more people" in text


def test_optional_metrics_and_ties():
    a = Post("A", views=1000, shares=10, visits=5, saves=3)
    b = Post("B", views=1000, shares=10, visits=5)
    rates = compare(a, b)
    assert [r.label for r in rates] == ["Shares per 1,000 views", "Profile visits per 1,000 views", "Saves per 1,000 views"]
    assert ratio(2, 2) == "Same"
    assert ratio(0, 3) == "Only B has activity"
    tie = recommend(Post("A", 1000, 1, 1), Post("B", 1000, 1, 1), compare(Post("A", 1000, 1, 1), Post("B", 1000, 1, 1)))
    assert tie[0].startswith("The posts perform about the same")


def test_page_starts_blank():
    assert all(v == 0 for side in BLANK.values() for k, v in side.items() if k != "name")
