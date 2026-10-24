---
name: fla-brand-ui
description: Use when changing the look of the Creator Suite app (any page, component or style), so every screen follows the Fast Loan Advance brand and the app's layout rules.
---

# Fast Loan Advance UI for Creator Suite

The app is an internal marketing tool for Fast Loan Advance. People who open it are the marketing team and leadership, and the job of every screen is to answer one question fast: what to talk about, who to work with, or whether it makes money.

These rules were set with Anthropic's `frontend-design` skill and apply on top of it.

## Tokens

All colors live in `.streamlit/config.toml` (Streamlit widgets) and in `CSS` in `core/ui.py` (custom HTML). Change them in both places.

| Token | Hex | Use |
|---|---|---|
| Teal | `#043D46` | Fast Loan Advance's brand color (their site's theme color). Page bands, primary buttons, headings, metric values |
| Mist | `#EEF4F3` | Inputs, metric boxes, icon tiles |
| Line | `#D5E2E0` | Borders and dividers |
| Slate | `#4E6466` | Secondary text |
| Signal | `#18B37E` | Money and good news only: profit, positive ROI, the question each tool answers |

Typeface: Manrope for everything, weights 400 to 800. Headlines are 800 with slight negative tracking.

## Layout

- Every page runs through `Home.py`, which calls `core.ui.navigation()`. Never call `st.set_page_config` in a view.
- Navigation is the **Menu** popover (three lines icon) at top right. No sidebar. To add a page, add a row to `PAGES` in `core/ui.py` and a file in `views/`.
- Each tool page starts with `header(icon, title, subtitle)`: one teal band, one icon, one sentence.
- The home page has one bold element, the money chain (views, clicks, leads, revenue, profit), computed from `core.roi` so it always matches the ROI Planner.

## Rules

- Write custom HTML with `st.html`, never `st.markdown(..., unsafe_allow_html=True)`. It showed raw code on Streamlit Cloud.
- `st.html` strips `<svg>`. Use `core.ui.icon(name)`, which inlines the SVG as an image. Add new icons to `ICONS`.
- No gradients, no all-caps labels, no middle dots between words, no arrows typed into button text (use the `icon` argument).
- Buttons say what happens: "Scan this week", "Find creators", "Write brief".
- Errors say what went wrong and how to fix it.
- Keep the footer: it says this is a concept demo and not a customer-facing page.

## Check your work

1. `pytest` and `ruff check . --line-length 130`.
2. Run `streamlit run Home.py`, open every page at desktop width and at 390px wide, and open the menu.
3. Look at the screenshots before pushing.
