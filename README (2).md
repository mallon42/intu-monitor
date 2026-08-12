# ◈ Stock Monitor v3.0

**A standalone financial monitoring dashboard for Intuit (INTU) and SpaceX (SPCX) — built for shareholders who want a fast, private, single-file view of the stocks they care about.**

Created by [Brian Mallon](https://www.linkedin.com/in/brian-mallon-68003240a/) working with AI.

---

## What It Does

Stock Monitor is a single HTML file you open in any browser. No installation, no login, no server. It connects to Finnhub's free API for live data and gives you a professional-grade view of two companies. Switch between them anytime using the dropdown in the top-left corner.

- **Two companies, one tool** — click the title in the top-left to switch between **INTU Monitor** (Intuit) and **SPACEX Monitor** (SpaceX). Every panel — price, charts, segments, analyst data, earnings, peer comparison — swaps to the selected company.
- **Live price** with real-time quote refresh (configurable: 60 seconds to manual) and a pre-market / after-hours / market-open session badge
- **Market overview strip** — Dow Jones (DIA), S&P 500 (SPY), NASDAQ 100 (QQQ) at a glance
- **Nine interactive charts** — price (line or candlestick), daily range, RSI, MACD, OBV, ATR volatility, earnings history, peer comparison, and rolling S&P 500 correlation. Each chart has its own independent timeframe.
- **Fibonacci retracement** overlay and key-event annotations on the main price chart
- **Dashboard** — metric tiles for price, day range, 52-week high/low (with dates), volume, market cap, P/E, ATR, dividend yield, short interest, and distance from all-time high, plus a 52-week range bar, technical-analysis summary, earnings countdown, analyst consensus, and latest headlines
- **Analysis tab** — analyst ratings, price targets, fundamentals, and valuation context
- **Segments tab** — revenue breakdown by business unit with health assessments (Intuit: QuickBooks, Mailchimp, TurboTax, Credit Karma, ProConnect · SpaceX: Starlink, Space/Launch, AI/xAI, Starshield)
- **Insider Trades tab** — executive buying and selling with filing dates and major-sale alerts
- **News tab** — company news with color-coded story highlighting, SEC filings, and competitive intelligence
- **My Portfolio tab** — RSU Tracker with import/export, Break-Even Calculator, Price Alerts, a Hold vs Sell Modeler, and a vesting timeline by grant year

---

## Getting Started

### 1. Get a free Finnhub API key

Go to [finnhub.io](https://finnhub.io) and create a free account. It takes about 90 seconds and requires no credit card. Copy your API key from the dashboard.

### 2. Open the tool

- **Online (always the latest version):** [https://mallon42.github.io/intu-monitor/](https://mallon42.github.io/intu-monitor/)
- **Offline:** Download `index.html` and open it directly in Chrome, Edge, Firefox, or Safari on Windows or Mac.

### 3. Paste your API key

The setup screen appears on first launch. Paste your Finnhub key and click to launch. Your key is saved to your browser's local storage — it never leaves your computer.

### 4. Switch companies

Click the title in the top-left corner (**◈ INTU MONITOR ▼**). A dropdown lets you switch to SpaceX and back. Your choice is remembered the next time you open the tool.

---

## Privacy & Security

> **Your data stays on your computer. Period.**

- **API key** — stored in your browser's local storage only. Never transmitted anywhere except to Finnhub to fetch market data.
- **Portfolio data** — RSU lots, price alerts, and all portfolio information are stored in your browser's local storage. They are never sent to any server, never visible to the author, and never visible to GitHub.
- **Market data** — fetched directly from [Finnhub.io](https://finnhub.io) using your own API key. Chart history comes from public sources (Yahoo Finance / Stooq) via CORS proxies; no authentication required for those.

The tool is a static HTML file. GitHub only serves the file. Once loaded, everything runs locally in your browser.

---

## Portfolio Import / Export

Use the **My Portfolio → RSU Tracker** tab to manage your grants.

| Button | What it does |
|--------|-------------|
| **⬇ JSON** | Downloads a full backup of your RSU lots and price alerts as JSON. Use this before switching browsers or devices. |
| **⬇ CSV** | Downloads your RSU lots as a spreadsheet (Grant Year, Shares, Price, Notes). |
| **⬆ Import** | Accepts the tool's own JSON/CSV export, or an **E-Trade Gains & Losses CSV** export directly. |

**Before migrating from a local file to the hosted version:** export your portfolio as JSON, then import it in the hosted version. Data does not transfer automatically between a local file and a hosted URL because each has its own browser storage.

---

## Keeping Up to Date

**If you use the hosted link** — you always have the latest version automatically. Nothing to do.

**If you use a local file** — the tool checks for updates on startup and shows a dismissible banner if your copy is outdated. You can also open the **ⓘ** button in the top-right corner and check manually.

---

## Understanding the Charts

Each of the charts on the Charts tab has **independent timeframe controls** — changing one doesn't affect the others. All charts share a cached dataset, so switching to a previously-viewed timeframe is instant.

- **Main price chart** — toggle between line and candlestick with the **Candle** button. Turn on **Fib** for Fibonacci retracement levels. **Events** marks key dates with hover-for-detail annotations.
- **Daily Range (H/L/C)** — the day's high-low range as floating bars with the close overlaid, auto-scaled so the price action fills the chart.
- **RSI** — momentum oscillator; below 30 is oversold, above 70 is overbought.
- **MACD** — trend/momentum crossovers.
- **OBV (On-Balance Volume)** — whether volume is flowing into or out of the stock; watch for divergence from price.
- **ATR (Average True Range)** — daily volatility in dollars; useful for setting meaningful price alerts.
- **Earnings History** — quarterly EPS actual vs. estimate; green bars beat, red bars missed.
- **Peer Comparison** — the stock vs. its closest competitor, indexed to 100 (INTU vs. H&R Block · SpaceX vs. Rocket Lab).
- **S&P 500 Correlation** — rolling correlation of daily returns; high = market-driven moves, low = company-specific moves.

---

## A Note on SpaceX Data

SpaceX (SPCX) began trading on the Nasdaq on **June 12, 2026**, following the largest IPO in history. Because it is a very new public company:

- **Live price, charts, and news** are fully real-time from the same feeds that power Intuit.
- **Segment revenue and key-event data** are curated from SpaceX's S-1 filing and news reporting, and are clearly labeled as estimates in the tool. SpaceX does not report segment revenue the way a long-established public company does.
- **Technical indicators and correlation** become more meaningful as trading history accumulates.

---

## Frequently Asked Questions

**Do I need to pay for anything?**
No. Finnhub's free tier covers everything the tool uses. No credit card required anywhere.

**Will my portfolio data be shared with anyone?**
No. See [Privacy & Security](#privacy--security) above.

**Why does the Volume tile say "shares (prev day)"?**
Finnhub's free-tier quote endpoint doesn't include today's real-time volume, so the tool falls back to the most recent daily candle's volume and labels it clearly.

**The charts say "data unavailable" — what do I do?**
Click the **↻ Retry** button inside the affected chart. If it keeps failing, the public data proxies may be temporarily down; the live quote, news, and dashboard data will continue to work regardless. Note that charts require the file to be served over HTTPS (the hosted GitHub Pages link) — opening the raw file directly from your hard drive blocks the data proxies for security reasons.

**Can I change the refresh interval?**
Yes — click the **⚙** gear icon in the bottom center. Options: 60s, 5 min (default), 15 min, 30 min, 1 hr, or Manual.

---

## Technical Notes

- Single HTML file, no build step, no dependencies to install
- All JavaScript runs in the browser; no server required
- Chart.js + chartjs-plugin-annotation (loaded from CDN, with a graceful fallback message if the CDN is ever unavailable)
- Compatible with Chrome, Edge, Firefox, and Safari on Windows and macOS
- Company selection and all portfolio data persist in browser local storage

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| **v3.0** | 2026-08-12 | **Multi-company support** — switch between INTU and SPCX from the top-left dropdown, each with its own segments, events, analyst data, earnings countdown, price levels, and peer comparison. Major reliability pass: fixed chart data loading, added Chart.js CDN fallback, per-company earnings/price-level data, and internal state consistency. Reviewed for cross-browser behavior and long-term stability. |
| v2.4 | 2026-06-15 | Candlestick toggle, Fibonacci retracement, pre/after-hours session badge, earnings history chart, short interest, OBV, ATR, peer comparison, dividend yield, RSU vesting timeline, S&P 500 correlation. |
| v2.3 | 2026-06-09 | GitHub Pages launch. Single-source version system; all version displays driven from one value. |
| v2.2 | 2026-06-09 | Independent chart timeframes, portfolio import/export (JSON/CSV/E-Trade), live clock, 52-week intraday correction, volume fallback, "Today" intraday chart, market overview strip, Insider Trades tab, About modal. |
| v1.0 | 2026-06-04 | Initial GitHub upload. |

---

## Disclaimer

This tool is for informational purposes only and is not financial advice. Market data is provided by Finnhub.io and public data sources. The author makes no guarantees about the accuracy, completeness, or timeliness of any data displayed. Always consult a licensed financial advisor before making investment decisions.

---

*This tool is not affiliated with, endorsed by, or connected to Intuit Inc. or Space Exploration Technologies Corp. in any way. All company names and trademarks are the property of their respective owners.*
