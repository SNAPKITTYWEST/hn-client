#!/usr/bin/env python3
"""
HN Post Helper — format and open a HackerNews submission.

Usage:
    python hn_post_helper.py --title "My cool thing" --url "https://..." --type show
    python hn_post_helper.py --title "Question about X?" --type ask
    python hn_post_helper.py --title "Just a link" --url "https://..."

Types: show, ask, plain (default: plain)
"""

import sys
import argparse
import webbrowser
import urllib.parse
from datetime import datetime, timezone, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DIVIDER = "-" * 55
MAX_TITLE_LEN = 80

HN_SUBMIT_URL = "https://news.ycombinator.com/submitlink"

# Optimal posting window: Tue–Thu, 9am–2pm US Eastern
# Days: Monday=0 … Sunday=6
GOOD_DAYS = {1, 2, 3}          # Tue, Wed, Thu
GOOD_HOUR_START = 9             # 9am EST
GOOD_HOUR_END = 14              # 2pm EST (exclusive)
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def format_title(raw_title, post_type):
    """Add Show HN / Ask HN prefix if needed."""
    t = raw_title.strip()
    if post_type == "show":
        prefix = "Show HN: "
        if t.lower().startswith("show hn"):
            return t
        return prefix + t
    elif post_type == "ask":
        prefix = "Ask HN: "
        if t.lower().startswith("ask hn"):
            return t
        return prefix + t
    return t


def validate_title(title):
    """Return (ok, message)."""
    n = len(title)
    if n > MAX_TITLE_LEN:
        return False, f"Title is {n} chars — exceeds {MAX_TITLE_LEN} char limit by {n - MAX_TITLE_LEN}"
    return True, f"{n}/{MAX_TITLE_LEN} chars OK"


def get_est_now():
    """Return current datetime in US Eastern (EST = UTC-5, no DST adjustment — conservative)."""
    utc_now = datetime.now(tz=timezone.utc)
    # Eastern Standard Time is UTC-5; Eastern Daylight is UTC-4.
    # Approximate: EDT runs mid-March to early Nov.
    year = utc_now.year
    # DST start: second Sunday of March
    dst_start = _nth_weekday(year, 3, 6, 2)   # month=3, weekday=6(Sun), n=2
    # DST end: first Sunday of November
    dst_end = _nth_weekday(year, 11, 6, 1)
    if dst_start <= utc_now.replace(tzinfo=None) < dst_end:
        offset = timedelta(hours=-4)   # EDT
    else:
        offset = timedelta(hours=-5)   # EST
    return utc_now + offset


def _nth_weekday(year, month, weekday, n):
    """Return the nth occurrence of weekday (0=Mon, 6=Sun) in the given month/year as naive datetime."""
    from calendar import monthrange
    first_day = datetime(year, month, 1)
    # Find first occurrence of weekday
    days_ahead = (weekday - first_day.weekday()) % 7
    first = first_day + timedelta(days=days_ahead)
    return first + timedelta(weeks=n - 1)


def posting_window_status(est_now):
    """Return (day_str, time_str, is_good, advice)."""
    day_idx = est_now.weekday()   # 0=Mon
    hour = est_now.hour
    minute = est_now.minute
    am_pm = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    day_str = DAY_NAMES[day_idx]
    time_str = f"{day_str} {display_hour}:{minute:02d} {am_pm}"

    is_good = (day_idx in GOOD_DAYS) and (GOOD_HOUR_START <= hour < GOOD_HOUR_END)
    return time_str, is_good


def build_submit_url(title, url):
    params = {"t": title}
    if url:
        params["u"] = url
    return HN_SUBMIT_URL + "?" + urllib.parse.urlencode(params)


def main():
    parser = argparse.ArgumentParser(
        description="HackerNews post helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--title", required=True, help="Story title (without Show/Ask HN prefix)")
    parser.add_argument("--url", default="", help="URL to submit")
    parser.add_argument(
        "--type",
        choices=["show", "ask", "plain"],
        default="plain",
        help="Post type: show (Show HN), ask (Ask HN), or plain",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser — just print the details",
    )

    args = parser.parse_args()

    title = format_title(args.title, args.type)
    ok, char_msg = validate_title(title)
    est_now = get_est_now()
    time_str, is_good = posting_window_status(est_now)

    # --- Output ---
    print(f"\n{DIVIDER}")
    print(" Show HN Post Helper" if args.type == "show" else
          " Ask HN Post Helper" if args.type == "ask" else
          " HN Post Helper")
    print(DIVIDER)
    print(f" Title: {title}")
    if args.url:
        print(f" URL:   {args.url}")
    if ok:
        print(f" Chars: {char_msg}")
    else:
        print(f" Chars: {char_msg}  <-- TOO LONG")

    print()
    print(f" Optimal posting window: Tue-Thu 9am-2pm EST")
    good_label = "GOOD TIME TO POST" if is_good else "suboptimal window"
    print(f" Current time (EST):     {time_str}  <- {good_label}")

    if not ok:
        print()
        print(f" [!] Title exceeds {MAX_TITLE_LEN} chars. Shorten before posting.")
        print(DIVIDER)
        sys.exit(1)

    print()
    if not args.no_browser:
        submit_url = build_submit_url(title, args.url)
        print(f" Opening HN submit page...")
        webbrowser.open(submit_url)

    print(f" Copy this title: {title}")
    print(DIVIDER)
    print()


if __name__ == "__main__":
    main()
