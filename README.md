# ◈ INTU Monitor v2.2

**A standalone financial monitoring dashboard for Intuit (INTU) shareholders — built for the people most affected by the May 2026 layoffs and stock decline.**

Created by [Brian Mallon](https://www.linkedin.com/in/brian-mallon-68003240a/) working with AI.

---

## What It Does

INTU Monitor is a single HTML file you open in any browser. No installation, no account, no server. It connects to Finnhub's free API to deliver:

- **Live INTU price** with real-time quote refresh (configurable interval: 60s to manual)
- **Market overview strip** — Dow Jones (DIA), S&P 500 (SPY), NASDAQ 100 (QQQ) at a glance
- **Interactive charts** — price, HLC daily range, RSI, and MACD, each with independent timeframes and key event annotations
- **Dashboard** — 8 metric tiles, 52-week range bar (intraday-adjusted), Technical Analysis Summary, earnings countdown, analyst consensus, and latest headlines
- **Analysis tab** — analyst ratings, price targets, fundamental metrics, valuation context, and a full workforce/layoff history timeline
- **Segments tab** — revenue breakdown by business unit with Mailchimp highlighted, and health cards for each segment
- **Insider Trades tab** — executive buying and selling with hover context, filing dates, and a dashboard alert for major sells within the past 14 days or any upcoming scheduled sells
- **News tab** — company news feed with color-coded story highlighting (critical, bearish, bullish, and by subsidiary), SEC 8-K filings, competitive intelligence from H&R Block, and an About panel
- **My Portfolio tab** — RSU Tracker (pre-seeded with example grants, fully editable), Break-Even Calculator, Price Alerts with browser notifications, and a Hold vs Sell Modeler

---

## Getting Started

### 1. Get a free Finnhub API key

Go to [finnhub.io](https://finnhub.io) and create a free account. It takes about 90 seconds and requires no credit card. Copy your API key from the dashboard.

### 2. Open the tool

- **Online (always latest version):** [https://mallon42.github.io/intu-monitor/](https://mallon42.github.io/intu-monitor/)
- **Offline:** Download `intu_monitor.html` and open it directly in Chrome, Edge, Firefox, or Safari on Windows or Mac.

### 3. Paste your API key

The setup screen appears on first launch. Paste your Finnhub key and click **Launch INTU Monitor**. Your key is saved to your browser's local storage — it never leaves your computer.

---

## Privacy & Security

> **Your data stays on your computer. Period.**

- **API key** — stored in your browser's local storage only. Never transmitted to any server other than Finnhub to fetch market data.
- **Portfolio data** — RSU lots, price alerts, and all portfolio information are stored in your browser's local storage. They are never sent to any server, never visible to the author, and never visible to GitHub.
- **Market data** — fetched directly from [Finnhub.io](https://finnhub.io) using your own API key. Finnhub's free tier allows 60 API calls per minute.
- **Chart data** — fetched from Yahoo Finance via public CORS proxies when Finnhub's free tier doesn't cover candle data. No authentication required for this.

The tool is a static HTML file. GitHub only serves the file. Once loaded, everything runs locally in your browser.

---

## Portfolio Import / Export

Use the **My Portfolio → RSU Tracker** tab to manage your grants.

| Button | What it does |
|--------|-------------|
| **⬇ JSON** | Downloads a full backup of your RSU lots and price alerts as JSON. Use this before switching browsers or devices. |
| **⬇ CSV** | Downloads your RSU lots as a spreadsheet (Grant Year, Shares, Price, Notes). |
| **⬆ Import** | Accepts the tool's own JSON/CSV export, or an **E-Trade Gains & Losses CSV** export directly. |

**Before migrating from a local file to the hosted version:** export your portfolio as JSON, then import it in the hosted version. Your data does not transfer automatically between a local file and a hosted URL because each has its own browser storage.

---

## Keeping Up to Date

**If you use the hosted link** — you always have the latest version automatically. Nothing to do.

**If you use a local file** — open the **ⓘ v2.2** button in the top-right corner of the tool. Click **Check for updates**. If a newer version exists, you'll get a link to download it.

The tool also checks automatically on startup and shows a dismissible banner if your local copy is outdated.

---

## Charts Tab — Tips

Each of the four charts (Main, Daily Range H/L/C, RSI, MACD) has **independent timeframe controls**. Changing the timeframe on RSI doesn't affect the main chart. All four charts share a cached candle dataset, so switching to a previously-viewed timeframe on any chart is instant.

**Events toggle** — vertical dashed lines mark five key dates in INTU's decline. Hover over any line for a full description of what happened and why it matters.

---

## Frequently Asked Questions

**Do I need to pay for anything?**
No. Finnhub's free tier covers everything the tool uses. No credit card required anywhere.

**Will my portfolio data be shared with anyone?**
No. See [Privacy & Security](#privacy--security) above.

**Can I use this on both my work and home computer?**
Yes, but the portfolio data (RSU lots, alerts) is stored per-browser per-device. Use the JSON export/import to keep them in sync.

**The charts say "Chart data unavailable" — what do I do?**
Click the **↻ Retry** button inside the affected chart tile. If it keeps failing, the public CORS proxies used for Yahoo Finance chart data may be temporarily down. The Finnhub quote, news, and all dashboard data will continue to work regardless.

**Why does the Volume tile say "shares (prev day)"?**
Finnhub's free-tier quote endpoint doesn't include today's real-time volume. The tool falls back to the most recent daily candle's volume (yesterday's closing volume) and labels it clearly.

**Can I change the refresh interval?**
Yes — click the **⚙** gear icon in the bottom center of the tool. Options: 60s, 5 min (default), 15 min, 30 min, 1 hr, or Manual.

---

## Technical Notes

- Single HTML file, ~180KB, no build step, no dependencies to install
- All JavaScript runs in the browser; no Node.js or server required
- Chart.js 4.4.1 + chartjs-plugin-annotation 3.0.1 (loaded from CDN)
- IBM Plex Mono + Inter fonts (loaded from Google Fonts; falls back to system fonts offline)
- localStorage keys used: `intu_api_key`, `intu_rsus`, `intu_alerts`, `intu_refresh`, `intu_version`, `intu_price_history`, `intu_ph_date`
- Compatible with: Chrome, Edge, Firefox, Safari on Windows and macOS

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| v2.2 | 2026-06-09 | Independent chart timeframes, Export/Import (JSON/CSV/E-Trade), live clock, 52-week intraday correction, volume fallback, Today intraday chart, market overview, Insider Trades tab, About modal |
| v1.0 | 2026-06-04 | Initial GitHub upload |

---

## Disclaimer

This tool is for informational purposes only and is not financial advice. Market data is provided by Finnhub.io and Yahoo Finance. The author makes no guarantees about the accuracy, completeness, or timeliness of any data displayed. Always consult a licensed financial advisor before making investment decisions.

---

*INTU Monitor is not affiliated with, endorsed by, or connected to Intuit Inc. in any way.*
