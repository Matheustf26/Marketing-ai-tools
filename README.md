# Marketing AI Tools

AI-powered marketing tools built with Claude: creator discovery and influencer ROI planning.

Influencer marketing usually stalls on two questions: **who should we work with?** and **how does this make money?** These two tools answer both, and they're built to work together.

![Home](docs/home.png)

## 🔎 Creator Scout

Describe a niche or product, choose platforms, country and creator size. Claude searches the web and returns real creators it found, with:

- handle, platform, profile link and follower count (as published)
- what they post and why their audience fits
- a 1 to 10 fit score and the best brand match from your brand list
- brand-safety flags (get-rich-quick claims, controversies, competitor deals)
- a personal first outreach message

Export everything to CSV, or send the shortlist straight to the ROI Planner.

![Creator Scout](docs/scout.png)

**How it works:** one Claude call with the web search tool does the research, and a second call turns the notes into a validated table (structured outputs). The prompt only allows creators found in search results, so it doesn't invent names or numbers.

## 💰 Creator ROI Planner

Treats every sponsored post as a small lead-gen campaign: **views → clicks → leads → revenue**.

- **Single creator:** cost per lead, profit, ROI, break-even leads and the maximum fee worth paying, with pessimistic, realistic and optimistic scenarios.
- **Campaign:** an editable table of creators that shows which ones to book and which to renegotiate (or move to a flat fee + bonus per lead).
- **Tracking links:** a UTM link per creator, so GA4 shows exactly who brings leads.
- **Campaign brief:** Claude writes a brief with FTC disclosure rules, finance-specific don'ts (no guaranteed approval claims) and a "needs legal review" list.

![ROI Planner](docs/roi.png)

## Run it locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Paste your Anthropic API key in the sidebar, or set it once in `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Web search has to be enabled for your organization in the [Claude Console](https://console.anthropic.com) settings.

## Deploy (free)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. **Create app** → pick this repository, branch `main`, main file `Home.py`.
3. Under **Advanced settings → Secrets**, paste `ANTHROPIC_API_KEY = "sk-ant-..."`.
4. Deploy and share the link.

## Project layout

```
Home.py                         landing page
pages/1_Creator_Scout.py        creator discovery UI
pages/2_Creator_ROI_Planner.py  ROI, scenarios, UTM links, brief
core/scout.py                   web research + structured extraction
core/roi.py                     ROI math and UTM builder (pure functions)
core/brief.py                   campaign brief prompt
core/llm.py                     Claude client, API key handling
tests/                          unit tests and page smoke tests
```

Run the tests with `pytest`.

Built with [Claude](https://claude.ai) and [Streamlit](https://streamlit.io).
