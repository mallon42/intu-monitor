#!/usr/bin/env python3
"""
Daily morning status script:
- Reads SolarWinds "nightcheck" pages for ATL and SUW
- Fetches current primary on-call user(s) from PagerDuty schedules
- Summarizes active SolarWinds alerts (excluding IT-prefixed)
- Posts to Slack (or prints with --print-only)
"""
from bs4 import BeautifulSoup
import argparse
import os
import datetime
import requests
import random
import traceback
import logging
import time
import gather
from mcnet import solarwinds, auth

def solarwinds_nightcheck(url):
    """Return a short status string for a given SolarWinds nightcheck URL."""
    now = datetime.datetime.now()
    # Retry on transient HTTP/network issues
    last_error = None
    for attempt in range(1, 4):
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            ok_errors = soup.find_all(text="Errors: 0")
            dater = f"{now.month}/{now.day}/{now.year}"
            dater_results = soup.find_all(text=dater)
            if ok_errors == []:
                logging.error("Nightcheck reported errors: %s", url)
                return f"Errors Detected.{url} :sadpanda:"
            if dater_results != []:
                logging.warning("Nightcheck date not updated for: %s (expected %s)", url, dater)
                return "Unable to verify backups. Date has not updated :waiting:"
            return "Backups Look Great!"
        except Exception as e:
            last_error = e
            # Short backoff before retry
            if attempt < 3:
                time.sleep(2 * attempt)
            continue
    logging.exception("Nightcheck request failed for %s: %s", url, last_error)
    return f"Unable to read {url} Please review "


def pagerduty_oncall_names(schedule_ids):
    """
    Return list of primary on-call user names across the given schedule IDs.
    Reads token from mcnet.auth or env: PAGERDUTY_API_TOKEN.
    """
    try:
        token = auth.returnables("pagerduty", "token")
    except BaseException:
        token = os.environ.get("PAGERDUTY_API_TOKEN")
    if not token or not schedule_ids:
        if not token:
            logging.error("PagerDuty token missing (set auth.returnables('pagerduty','token') or PAGERDUTY_API_TOKEN)")
        if not schedule_ids:
            logging.error("PagerDuty schedule IDs missing (set auth.returnables('pagerduty','schedule_ids') or PAGERDUTY_SCHEDULE_IDS)")
        return []

    url = "https://api.pagerduty.com/oncalls"
    headers = {
        "Authorization": f"Token token={token}",
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Content-Type": "application/json",
    }
    params = [("time_zone", "UTC"), ("include[]", "users")]
    for sid in schedule_ids:
        params.append(("schedule_ids[]", sid))

    try:
        logging.debug("Requesting PagerDuty oncalls for schedules: %s", ",".join(schedule_ids))
        r = requests.get(url, headers=headers, params=params, timeout=15)
        logging.debug("PagerDuty response status: %s", r.status_code)
        r.raise_for_status()
        data = r.json()
        primary = []
        for oc in data.get("oncalls", []) or []:
            if int(oc.get("escalation_level") or 0) == 1:
                user = oc.get("user") or {}
                name = user.get("summary") or user.get("name")
                if name:
                    primary.append(name)
        # stable dedupe
        seen = set()
        out = []
        for n in primary:
            if n not in seen:
                seen.add(n)
                out.append(n)
        return out
    except Exception as e:
        logging.exception("PagerDuty oncalls request failed: %s", e)
        return []


def pagerduty_next_oncall_names(schedule_ids):
    """
    Return list of the next primary on-call user(s) after now for the given schedules.
    Uses the schedules endpoint rendered entries and selects the first entry starting after now.
    """
    try:
        token = auth.returnables("pagerduty", "token")
    except BaseException:
        token = os.environ.get("PAGERDUTY_API_TOKEN")
    if not token or not schedule_ids:
        if not token:
            logging.error("PagerDuty token missing (set auth.returnables('pagerduty','token') or PAGERDUTY_API_TOKEN)")
        if not schedule_ids:
            logging.error("PagerDuty schedule IDs missing (set auth.returnables('pagerduty','schedule_ids') or PAGERDUTY_SCHEDULE_IDS)")
        return []

    headers = {
        "Authorization": f"Token token={token}",
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Content-Type": "application/json",
    }

    now = datetime.datetime.utcnow().replace(microsecond=0)
    since_iso = now.isoformat() + "Z"
    until_iso = (now + datetime.timedelta(days=14)).isoformat() + "Z"

    next_names = []
    try:
        for sid in schedule_ids:
            url = f"https://api.pagerduty.com/schedules/{sid}"
            params = {
                "since": since_iso,
                "until": until_iso,
                "time_zone": "UTC",
                "overflow": "true",
            }
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            entries = (data.get("schedule", {})
                            .get("final_schedule", {})
                            .get("rendered_schedule_entries", []))
            upcoming = [e for e in entries if e.get("start") and e["start"] > since_iso]
            if not upcoming:
                continue
            upcoming.sort(key=lambda e: e["start"])
            user = (upcoming[0].get("user") or {})
            name = user.get("summary") or user.get("name")
            if name:
                next_names.append(name)
        # dedupe preserve order
        seen = set()
        out = []
        for n in next_names:
            if n not in seen:
                seen.add(n)
                out.append(n)
        return out
    except Exception as e:
        logging.exception("PagerDuty schedules request failed: %s", e)
        return []


# ===== Holiday helpers (optional, self-contained) =====

def _parse_holiday_line(line, default_year):
    """
    Parse a single holiday line into (date, name).
    Accepts formats like:
      - 2025-12-25 Christmas Day
      - 12/25/2025 Christmas Day
      - 12/25 Christmas Day        (assumes default_year)
      - Dec 25, 2025 Christmas Day
      - Dec 25 Christmas Day       (assumes default_year)
    Returns (date, name) or None on failure.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    import re
    import datetime as _dt

    # Try to split "date + name" with flexible date token
    m = re.match(r"^([A-Za-z]{3,}\s+\d{1,2}(?:,?\s*\d{4})?|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}(?:/\d{4})?)\s+(.*)$", line)
    if not m:
        return None
    date_str = m.group(1).strip()
    name = m.group(2).strip() or "Company Holiday"

    fmts = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%b %d, %Y",
        "%b %d %Y",
        "%B %d, %Y",
        "%B %d %Y",
        "%m/%d",
        "%b %d",
        "%B %d",
    ]
    dt = None
    for fmt in fmts:
        try:
            parsed = _dt.datetime.strptime(date_str, fmt)
            if "%Y" not in fmt:
                parsed = parsed.replace(year=default_year)
            dt = parsed.date()
            break
        except Exception:
            continue
    if not dt:
        return None
    return (dt, name)


def _load_holidays_for_year(base_dir, year):
    """
    Load holidays from Daily/<year> Holidays.txt. Returns (path, list[(date, name)]).
    Logs and returns empty list on error.
    """
    import os
    path = os.path.join(base_dir, f"{year} Holidays.txt")
    holidays = []
    try:
        with open(path, "r") as f:
            for line in f:
                item = _parse_holiday_line(line, default_year=year)
                if item:
                    holidays.append(item)
        return (path, holidays)
    except FileNotFoundError:
        # Missing file is expected when next year's holidays are not published yet
        return (path, [])
    except Exception as e:
        logging.exception("Holiday file read failed for %s: %s", path, e)
        return (path, [])


def next_company_holiday_line():
    """
    Compute the next upcoming company day off as one line, or '' if unavailable.
    Looks at Daily/<current_year> Holidays.txt, then falls back to next year.
    """
    import os as _os
    import datetime as _dt

    base_dir = _os.path.dirname(_os.path.realpath(__file__))
    today = _dt.date.today()
    year = today.year

    # Current year
    path_cur, hol_cur = _load_holidays_for_year(base_dir, year)
    # Select holidays strictly after today, so on a holiday date we show the next day off
    future_cur = sorted([h for h in hol_cur if h[0] > today], key=lambda x: x[0])
    if future_cur:
        dt, name = future_cur[0]
        pretty = dt.strftime("%b %d")
        return f"Upcoming Company Day Off: {pretty} - {name}"

    # Next year
    path_next, hol_next = _load_holidays_for_year(base_dir, year + 1)
    future_next = sorted([h for h in hol_next if h[0] >= today], key=lambda x: x[0])
    if future_next:
        dt, name = future_next[0]
        pretty = dt.strftime("%b %d")
        return f"Upcoming Company Day Off: {pretty} - {name}"

    return ""

# ===== End holiday helpers =====


def _wmo_to_slack_emoji(code, precip_prob):
    """
    Map WMO weather code and precipitation probability to a Slack emoji.
    Returns '' if unclear.
    """
    try:
        c = int(code) if code is not None else None
    except Exception:
        c = None

    # Thunderstorm
    if c in (95, 96, 99):
        return ":thunder_cloud_and_rain:"
    # Snow
    if c in (71, 73, 75, 77, 85, 86):
        return ":snowflake:"
    # Drizzle/Rain/Showers
    if c in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return ":umbrella_with_rain_drops:"
    # Fog
    if c in (45, 48):
        return ":fog:"
    # Overcast
    if c == 3:
        return ":cloud:"
    # Mainly clear / Partly cloudy
    if c in (1, 2):
        return ":partly_sunny:"
    # Clear
    if c == 0:
        return ":sunny:"

    # Heuristic: high precip probability suggests rain
    try:
        if precip_prob is not None and float(precip_prob) >= 60:
            return ":umbrella_with_rain_drops:"
    except Exception:
        pass
    return ""


def weather_brief_atl():
    """
    Return a concise ATL weather line for zip 30308 using Open-Meteo.
    Example: 'ATL Weather: now 60°F, H 68°/L 52°, precip 20% :umbrella_with_rain_drops:'.
    On any error, return '' so the section is omitted.
    """
    try:
        # Midtown Atlanta approximate coords for 30308
        lat, lon = 33.78, -84.38
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
        }
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        current = data.get("current", {}) or {}
        daily = data.get("daily", {}) or {}

        now_f = current.get("temperature_2m")
        curr_code = current.get("weather_code")
        hi = (daily.get("temperature_2m_max") or [None])[0]
        lo = (daily.get("temperature_2m_min") or [None])[0]
        p = (daily.get("precipitation_probability_max") or [None])[0]
        day_code = (daily.get("weather_code") or [None])[0]
        if now_f is None or hi is None or lo is None or p is None:
            return ""
        # Prefer day's forecast code; fallback to current code
        code = day_code if day_code is not None else curr_code
        emoji = _wmo_to_slack_emoji(code, p)
        line = f"ATL Weather: now {int(round(now_f))}°F, H {int(round(hi))}°/L {int(round(lo))}°, precip {int(round(p))}%"
        if emoji:
            line += f" {emoji}"
        return line
    except Exception as e:
        logging.exception("Weather fetch failed: %s", e)
        return ""


def days_until_oct30():
    """
    Return a countdown line for Oct 30 of the current year.
    If the date has passed, return '' so the line is omitted.
    """
    today = datetime.date.today()
    target = datetime.date(today.year, 10, 30)
    if today > target:
        return ""
    days_left = (target - today).days
    return f"Remaining days until Oct 30: {days_left}"


def read_random_quote(quotes_filename):
    """Load a random quote from a local file; fail quietly if missing/unreadable."""
    try:
        with open(quotes_filename, 'r') as f:
            txt = f.read()
        lines = txt.split('\n.\n')
        return ':::: Random Quote:' + random.choice(lines) + '::::'
    except Exception:
        return ''


def build_message(schedule_ids):
    """Assemble the multi-line morning message body."""
    # Backups (ATL, SUW)
    msg_atl = 'ATL Network backup status: ' + solarwinds_nightcheck("http://10.132.226.247/nightcheck.htm")
    msg_suw = 'SUW Network backup status: ' + solarwinds_nightcheck("http://10.132.226.247/Suwanee/nightcheck.htm")

    # On-call
    oncall_names = pagerduty_oncall_names(schedule_ids)
    oncall_line = "OnCall: " + (", ".join(oncall_names) if oncall_names else "Unknown (no on-call found)")
    # Next up on-call
    next_names = pagerduty_next_oncall_names(schedule_ids)
    oncall_next_line = "OnCall Next: " + (", ".join(next_names) if next_names else "Unknown")

    # SolarWinds active alerts (exclude IT - ...)
    messages = []
    count = 0
    try:
        cursor = solarwinds._fetch_mssql_statement(
            "SELECT TriggeredMessage From AlertActive WHERE TriggeredMessage NOT LIKE 'IT - %'"
        )
        for row in cursor:
            messages.append(row['TriggeredMessage'] + "\n")
            count += 1
    except Exception as e:
        # Fail soft if DB unavailable
        logging.exception("SolarWinds DB query failed: %s", e)
    triggers_detail = "Triggers:" + "\n" + ''.join(messages)
    active_count = f"Solarwinds Active Alert Count: {count}"

    # Daily report
    daily_report = "Yesterdays Alerts: http://10.132.226.247/DailyReport.pdf"

    # Optional concise weather line
    wx = weather_brief_atl()

    # Holiday line
    holiday_line = next_company_holiday_line()
    # Countdown line
    countdown_line = days_until_oct30()

    parts = [
        msg_atl,
        msg_suw,
        oncall_line,
        oncall_next_line,
        (wx if wx else None),
        (holiday_line if holiday_line else None),
        (countdown_line if countdown_line else None),
        active_count,
        triggers_detail,
        '\n',
        daily_report,
    ]
    return '\n'.join([p for p in parts if p])


def parse_schedule_ids():
    """Read PagerDuty schedule IDs from mcnet.auth or PAGERDUTY_SCHEDULE_IDS env (comma-separated)."""
    # Preferred config via mcnet.auth; fallback to env
    raw = None
    try:
        raw = auth.returnables("pagerduty", "schedule_ids")
    except BaseException:
        raw = os.environ.get("PAGERDUTY_SCHEDULE_IDS")
    if not raw:
        logging.warning("No PagerDuty schedule IDs configured")
        return []
    return [s.strip() for s in str(raw).split(",") if s.strip()]


def main():
    # CLI flags: print-only (no Slack) and debug logging for troubleshooting
    parser = argparse.ArgumentParser(description="Morning status with PagerDuty on-call and SolarWinds")
    parser.add_argument("--print-only", action="store_true", help="Print instead of posting to Slack")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging to stderr")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.ERROR,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    schedule_ids = parse_schedule_ids()
    body = build_message(schedule_ids)
    quote = read_random_quote(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'quotes.txt'))

    if args.print_only:
        print(body)
        if quote:
            print(quote)
        return

    try:
        gather.send_slack('netwerking', body)
        if quote:
            gather.send_slack('netwerking', quote)
    except Exception as e:
        logging.exception("Slack send error: %s", e)


if __name__ == "__main__":
    main()


