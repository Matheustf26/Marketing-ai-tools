---
name: creator-weekly-brief
description: Use when someone asks for the weekly influencer brief, a leadership summary of the Creator Radar, or "what should we post this week". Turns the latest radar report into a one-page plan with actions and ROI.
---

# Creator weekly brief

Turns the newest Creator Radar report into a one-page brief a CEO can read in two minutes: what is happening, what we will post, who we will work with, and what it should return.

## Inputs

- The newest file in `reports/` (written every Monday and Friday by `.github/workflows/trend-radar.yml`). If the person names a date or segment, use that report.
- The ROI model in `core/roi.py`. Defaults: fee $1,500, 80,000 views, 1% click rate, 8% click to lead, $35 a lead. Use the person's numbers if they give them.
- Brands: Fast Loan Advance, Fast Loan Direct and Grace Loan Advance (positioning in `core/radar.py`, `DEFAULT_BRANDS`).

## Steps

1. Read the report. Pick the three trends with the strongest evidence and the lowest compliance risk.
2. For each trend, write one post idea, the brand it fits, and the format (Reel, carousel, green-screen explainer).
3. Run the ROI math for one sponsored post with `core.roi.project` and `core.roi.scenarios`, and include the pessimistic, realistic and optimistic profit plus the maximum fee worth paying.
4. List every compliance caution from the report under "Needs legal review".
5. Write the brief to `reports/briefs/<date>-weekly-brief.md` using the template below.

## Template

```markdown
# Weekly creator brief, week of <date>

**The one thing to know:** <headline from the report, one sentence>

## What we post this week
| Trend | Post idea | Brand | Format |
|---|---|---|---|

## What one sponsored post should return
<fee>, <views>: <leads> leads, <revenue> revenue, <profit> profit (pessimistic <x>, optimistic <y>). Don't pay more than <max fee>.

## Next steps
1. Shortlist creators for trend 1 in Creator Scout.
2. Model each creator in the ROI Planner and book only those who break even.
3. Give each creator a UTM link from the ROI Planner.

## Needs legal review
- <cautions>

Sources: <links from the report>
```

## Rules

- Use only facts, numbers and links that are in the report. Never invent engagement figures or creators.
- No promises of approval or guaranteed outcomes, and no pressure to borrow.
- Keep it to one page.
