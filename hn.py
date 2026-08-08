#!/usr/bin/env python3
"""
HackerNews terminal client — pure stdlib, no external deps.
Usage:
    python hn.py top              # top stories
    python hn.py new              # newest stories
    python hn.py show             # Show HN
    python hn.py best             # best stories
    python hn.py ask              # Ask HN
    python hn.py read <id>        # story + comments
    python hn.py user <username>  # user profile
    python hn.py search <query>   # filter top 200 stories
    python hn.py watch            # poll top 30 every 60s
    python hn.py stats <id>       # score/comment/rank/velocity
"""

import sys
import json
import time
import re
import urllib.request
from datetime import datetime, timezone

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "https://hacker-news.firebaseio.com/v0"
DIVIDER = "-" * 65


# ── Network helpers ───────────────────────────────────────────────────────────

def fetch_json(path):
    url = f"{BASE_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[error] fetch failed for {path}: {e}", file=sys.stderr)
        return None


def fetch_item(item_id):
    return fetch_json(f"/item/{item_id}.json")


def fetch_story_ids(feed):
    feeds = {
        "top":  "/topstories.json",
        "new":  "/newstories.json",
        "show": "/showstories.json",
        "best": "/beststories.json",
        "ask":  "/askstories.json",
    }
    if feed not in feeds:
        print(f"[error] unknown feed: {feed}")
        sys.exit(1)
    return fetch_json(feeds[feed]) or []


# ── Formatting helpers ────────────────────────────────────────────────────────

def time_ago(unix_ts):
    if unix_ts is None:
        return "unknown"
    now = time.time()
    diff = int(now - unix_ts)
    if diff < 60:
        return f"{diff} seconds ago"
    elif diff < 3600:
        m = diff // 60
        return f"{m} minute{'s' if m != 1 else ''} ago"
    elif diff < 86400:
        h = diff // 3600
        return f"{h} hour{'s' if h != 1 else ''} ago"
    else:
        d = diff // 86400
        return f"{d} day{'s' if d != 1 else ''} ago"


def extract_domain(url):
    if not url:
        return ""
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else ""


def strip_html(text):
    if not text:
        return ""
    # Step 1: convert block-level tags to whitespace BEFORE stripping
    text = text.replace("<p>", "\n\n")
    text = text.replace("<br>", "\n")
    text = text.replace("<br/>", "\n")
    text = text.replace("<br />", "\n")
    # Step 2: strip all remaining HTML tags (real markup, not entities)
    text = re.sub(r"<[^>]+>", "", text)
    # Step 3: decode HTML entities (after tag stripping so &lt;foo&gt; stays as <foo>)
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#x27;", "'")
    text = text.replace("&#39;", "'")
    text = text.replace("&apos;", "'")
    return text.strip()


def wrap_text(text, width=72, indent=""):
    words = text.split()
    lines = []
    current = indent
    for word in words:
        if len(current) + len(word) + 1 > width:
            if current.strip():
                lines.append(current.rstrip())
            current = indent + word + " "
        else:
            current += word + " "
    if current.strip():
        lines.append(current.rstrip())
    return "\n".join(lines)


def print_story_row(n, item):
    title = item.get("title", "(no title)")
    score = item.get("score", 0)
    comments = item.get("descendants", 0)
    by = item.get("by", "?")
    when = time_ago(item.get("time"))
    domain = extract_domain(item.get("url", ""))

    print(DIVIDER)
    header = f" {n:>2}. {title}"
    score_part = f"(score: {score}, comments: {comments})"
    # keep score on same line if it fits, else wrap
    if len(header) + len(score_part) + 2 <= 80:
        print(f"{header}  {score_part}")
    else:
        print(header)
        print(f"      {score_part}")
    meta = f"     by: {by} | {when}"
    if domain:
        meta += f" | {domain}"
    print(meta)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list(feed, count=30):
    ids = fetch_story_ids(feed)[:count]
    if not ids:
        print("No stories found.")
        return
    print(f"\nHackerNews — {feed.upper()} stories (top {len(ids)})\n")
    for n, story_id in enumerate(ids, 1):
        item = fetch_item(story_id)
        if item:
            print_story_row(n, item)
    print(DIVIDER)


def cmd_read(story_id, comment_limit=10):
    item = fetch_item(story_id)
    if not item:
        print(f"Item {story_id} not found.")
        return

    title = item.get("title", "(no title)")
    url = item.get("url", "")
    score = item.get("score", 0)
    by = item.get("by", "?")
    when = time_ago(item.get("time"))
    comments = item.get("descendants", 0)
    text = strip_html(item.get("text", ""))

    print(f"\n{DIVIDER}")
    print(f" {title}")
    print(DIVIDER)
    if url:
        print(f" URL:      {url}")
    print(f" Score:    {score}    Comments: {comments}")
    print(f" Author:   {by}    {when}")
    if text:
        print()
        for para in text.split("\n\n"):
            if para.strip():
                print(wrap_text(para.strip(), indent=" "))
                print()

    # Comments
    kids = item.get("kids", [])
    if not kids:
        print("\n (no comments)")
        return

    print(f"\n{DIVIDER}")
    print(f" Top {min(comment_limit, len(kids))} comments")
    print(DIVIDER)

    for kid_id in kids[:comment_limit]:
        comment = fetch_item(kid_id)
        if not comment or comment.get("deleted") or comment.get("dead"):
            continue
        c_by = comment.get("by", "?")
        c_when = time_ago(comment.get("time"))
        c_text = strip_html(comment.get("text", ""))
        print(f"\n  [{c_by}] {c_when}")
        if c_text:
            for para in c_text.split("\n\n"):
                if para.strip():
                    print(wrap_text(para.strip(), indent="    "))
                    print()

    print(DIVIDER)


def cmd_user(username):
    data = fetch_json(f"/user/{username}.json")
    if not data:
        print(f"User '{username}' not found.")
        return

    karma = data.get("karma", 0)
    created = data.get("created", 0)
    about = strip_html(data.get("about", ""))
    submitted = data.get("submitted", [])
    created_str = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d") if created else "?"

    print(f"\n{DIVIDER}")
    print(f" User: {username}")
    print(DIVIDER)
    print(f" Karma:       {karma}")
    print(f" Member since: {created_str}")
    print(f" Submissions:  {len(submitted)}")
    if about:
        print(f"\n About:")
        print(wrap_text(about, indent="   "))
    print(DIVIDER)


def cmd_search(query, count=200):
    ids = fetch_story_ids("top")[:count]
    q = query.lower()
    matches = []
    print(f"Searching top {count} stories for: \"{query}\"")
    for story_id in ids:
        item = fetch_item(story_id)
        if item and q in item.get("title", "").lower():
            matches.append(item)

    if not matches:
        print("No matches found.")
        return

    print(f"\nFound {len(matches)} match{'es' if len(matches) != 1 else ''}:\n")
    for n, item in enumerate(matches, 1):
        print_story_row(n, item)
    print(DIVIDER)


def cmd_watch(interval=60, count=30):
    print(f"Watching top {count} stories — refreshing every {interval}s. Ctrl+C to exit.\n")
    prev_ids = []
    try:
        while True:
            ids = fetch_story_ids("top")[:count]
            if prev_ids:
                new_entries = [i for i in ids if i not in prev_ids]
                rank_changes = []
                for i, sid in enumerate(ids):
                    if sid in prev_ids:
                        old_rank = prev_ids.index(sid) + 1
                        new_rank = i + 1
                        if old_rank != new_rank:
                            rank_changes.append((sid, old_rank, new_rank))

                ts = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{ts}] Refresh")
                if new_entries:
                    print(f"  New on front page ({len(new_entries)}):")
                    for sid in new_entries:
                        item = fetch_item(sid)
                        if item:
                            title = item.get("title", "(no title)")[:60]
                            score = item.get("score", 0)
                            rank = ids.index(sid) + 1
                            print(f"    #{rank:>2}  {title}  (score: {score})")
                if rank_changes:
                    print(f"  Rank changes ({len(rank_changes)}):")
                    for sid, old_r, new_r in rank_changes[:5]:
                        item = fetch_item(sid)
                        title = item.get("title", "(no title)")[:50] if item else str(sid)
                        arrow = "up" if new_r < old_r else "dn"
                        print(f"    {arrow} #{old_r} -> #{new_r}  {title}")
                if not new_entries and not rank_changes:
                    print("  No changes.")
            else:
                # first fetch — show current top 5
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] Initial fetch — top 5:")
                for i, sid in enumerate(ids[:5], 1):
                    item = fetch_item(sid)
                    if item:
                        title = item.get("title", "(no title)")[:60]
                        score = item.get("score", 0)
                        print(f"  #{i:>2}  {title}  (score: {score})")

            prev_ids = list(ids)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWatch stopped.")


def cmd_stats(story_id):
    item = fetch_item(story_id)
    if not item:
        print(f"Item {story_id} not found.")
        return

    title = item.get("title", "(no title)")
    score = item.get("score", 0)
    comments = item.get("descendants", 0)
    by = item.get("by", "?")
    ts = item.get("time", 0)
    when = time_ago(ts)

    # velocity = score per hour since posted
    age_hours = (time.time() - ts) / 3600 if ts else 1
    velocity = score / age_hours if age_hours > 0 else 0

    # check rank on front page
    rank = None
    top_ids = fetch_story_ids("top")[:30]
    if int(story_id) in top_ids:
        rank = top_ids.index(int(story_id)) + 1

    print(f"\n{DIVIDER}")
    print(f" Stats: {title[:60]}")
    print(DIVIDER)
    print(f" Score:      {score}")
    print(f" Comments:   {comments}")
    print(f" Author:     {by}")
    print(f" Posted:     {when}")
    print(f" Velocity:   {velocity:.1f} points/hour")
    if rank:
        print(f" Front page: #{rank}")
    else:
        print(f" Front page: not in top 30")
    print(DIVIDER)


# ── Entry point ───────────────────────────────────────────────────────────────

def usage():
    print(__doc__)
    sys.exit(0)


def main():
    args = sys.argv[1:]
    if not args:
        usage()

    cmd = args[0].lower()

    if cmd in ("top", "new", "show", "best", "ask"):
        cmd_list(cmd)
    elif cmd == "read":
        if len(args) < 2:
            print("Usage: python hn.py read <story_id>")
            sys.exit(1)
        cmd_read(args[1])
    elif cmd == "user":
        if len(args) < 2:
            print("Usage: python hn.py user <username>")
            sys.exit(1)
        cmd_user(args[1])
    elif cmd == "search":
        if len(args) < 2:
            print("Usage: python hn.py search <query>")
            sys.exit(1)
        cmd_search(" ".join(args[1:]))
    elif cmd == "watch":
        cmd_watch()
    elif cmd == "stats":
        if len(args) < 2:
            print("Usage: python hn.py stats <story_id>")
            sys.exit(1)
        cmd_stats(args[1])
    elif cmd in ("-h", "--help", "help"):
        usage()
    else:
        print(f"Unknown command: {cmd}")
        usage()


if __name__ == "__main__":
    main()
