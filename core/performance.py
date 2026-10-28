"""Creator Performance math: compare two posts by what people did per 1,000 views. No Claude call."""

from dataclasses import dataclass

# The page starts empty: the team types in the numbers of two real posts.
BLANK = {
    "A": {"name": "Post 1", "views": 0, "shares": 0, "visits": 0, "saves": 0, "clicks": 0},
    "B": {"name": "Post 2", "views": 0, "shares": 0, "visits": 0, "saves": 0, "clicks": 0},
}

# metric key, label. Saves and link clicks are optional and only compared when someone entered them.
METRICS = [("shares", "Shares"), ("visits", "Profile visits"), ("saves", "Saves"), ("clicks", "Link clicks")]
OPTIONAL = {"saves", "clicks"}

LIMITS = [
    "How long people watched (retention and completion rate).",
    "Where the views came from: followers, non-followers, or paid promotion.",
    "Whether profile visits turned into entries, sign-ups or link clicks.",
    "Comment sentiment, including trust questions like \"is this legit?\".",
    "Whether the sample is large enough. A single post is a signal, not proof.",
]


@dataclass
class Post:
    name: str
    views: int
    shares: int
    visits: int
    saves: int = 0
    clicks: int = 0


@dataclass
class Rate:
    label: str
    a: float
    b: float
    winner: str | None  # "A", "B" or None when equal
    ratio: str


def per_1k(count: float, views: float) -> float:
    return count / views * 1000 if views > 0 else 0.0


def fmt(n: float) -> str:
    return f"{n:,.1f}".removesuffix(".0")


def ratio(a: float, b: float, name_a: str = "A", name_b: str = "B") -> str:
    if a == b:
        return "Same"
    if a == 0:
        return f"Only {name_b} has activity"
    if b == 0:
        return f"Only {name_a} has activity"
    r = b / a
    return f"{name_b} is {fmt(r)}x {name_a}" if r >= 1 else f"{name_a} is {fmt(1 / r)}x {name_b}"


def compare(a: Post, b: Post) -> list[Rate]:
    rates = []
    for key, label in METRICS:
        ca, cb = getattr(a, key), getattr(b, key)
        if key in OPTIONAL and not (ca or cb):
            continue
        ra, rb = per_1k(ca, a.views), per_1k(cb, b.views)
        winner = "A" if ra > rb else "B" if rb > ra else None
        rates.append(Rate(f"{label} per 1,000 views", ra, rb, winner, ratio(ra, rb, a.name, b.name)))
    return rates


def recommend(a: Post, b: Post, rates: list[Rate]) -> list[str]:
    """Plain-language next step. It reads the rates; it never predicts virality."""
    score = sum((r.winner == "B") - (r.winner == "A") for r in rates)
    if score == 0:
        return ["The posts perform about the same per view. Test a new hook before choosing a direction."]
    side = "B" if score > 0 else "A"
    win, lose = (b, a) if side == "B" else (a, b)
    won = [r.label.split(" per ")[0].lower() for r in rates if r.winner == side]
    text = [
        (
            f"**Build on {win.name}.** Per view, it got more {', '.join(won[:-1]) + ' and ' if len(won) > 1 else ''}"
            f"{won[-1]}. People acting on a post, not just seeing it, is what carries it beyond our followers."
        )
    ]
    if lose.views > win.views:
        text.append(
            f"{lose.name} reached more people but few acted. Keep its hook as a reach idea, "
            f"and pair it with {win.name}'s message."
        )
    text.append(
        f"**Follow-up post:** a new version of {win.name} with the same angle and one clear call to action. "
        "Put a small boost behind it to test whether the share rate holds with people who don't follow us yet."
    )
    return text
