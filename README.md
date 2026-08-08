<p align="center">

```
██╗  ██╗███╗   ██╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗
██║  ██║████╗  ██║    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝
███████║██╔██╗ ██║    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║
██╔══██║██║╚██╗██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║
██║  ██║██║ ╚████║    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║
╚═╝  ╚═╝╚═╝  ╚═══╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝
```

</p>

<h3 align="center">Hacker News in your terminal. Zero dependencies.</h3>

<p align="center">
  <img src="https://img.shields.io/badge/language-Python-3776AB?style=flat-square"/>
  <img src="https://img.shields.io/badge/deps-zero-black?style=flat-square"/>
  <img src="https://img.shields.io/badge/API-HN_Firebase-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/install-clone_and_run-brightgreen?style=flat-square"/>
</p>

---

## What Is This?

A terminal client for Hacker News that does everything the website does — and more — from your command line. Pure Python stdlib. No pip install. No venv. No API key. Clone it and go.

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  $ python hn.py top                                              ║
║                                                                  ║
║   1. [342] Show HN: I built a terminal HN client               ║
║      ↳ news.ycombinator.com  ·  142 comments  ·  3h ago         ║
║                                                                  ║
║   2. [287] The unreasonable effectiveness of Common Lisp        ║
║      ↳ blog.author.com  ·  98 comments  ·  5h ago              ║
║                                                                  ║
║   3. [201] PostgreSQL 17 released                                ║
║      ↳ postgresql.org  ·  67 comments  ·  2h ago               ║
║                                                                  ║
║  $ python hn.py watch                                            ║
║  [LIVE] Refreshing every 60s... new entries highlighted          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Install

```bash
git clone https://github.com/SNAPKITTYWEST/hn-client
cd hn-client
python hn.py top
```

That's it. Python 3.9+. Nothing else.

---

## Commands

```
╔═══════════════╦════════════════════════════════════════════════════════╗
║  COMMAND       ║  WHAT IT DOES                                         ║
╠═══════════════╬════════════════════════════════════════════════════════╣
║  top           ║  Front page — top 30 stories ranked by HN algorithm  ║
║  new           ║  Newest 30 — freshly submitted, chronological        ║
║  best          ║  Best — highest score all-time (curated by HN)       ║
║  show          ║  Show HN — community projects and launches           ║
║  ask           ║  Ask HN — questions to the community                 ║
╠═══════════════╬════════════════════════════════════════════════════════╣
║  read <id>     ║  Full story text + top 10 comments, threaded         ║
║  user <name>   ║  Profile: karma, join date, about, submission count  ║
║  search <q>    ║  Title search across top 200 stories                 ║
║  stats <id>    ║  Score, comment count, velocity (pts/hr), FP rank    ║
║  watch         ║  Live mode — polls every 60s, highlights changes     ║
╚═══════════════╩════════════════════════════════════════════════════════╝
```

---

## User Guide

### Browse the front page

```bash
python hn.py top          # what's hot right now
python hn.py new          # latest submissions
python hn.py best         # all-time best
```

### Read a story and its comments

```bash
python hn.py read 41234567
```

Shows the story text (if any), URL, score, and top 10 comments with threading.

### Check someone's profile

```bash
python hn.py user dang
```

Shows karma, account age, bio, and recent submission count.

### Search stories

```bash
python hn.py search "rust async"
python hn.py search "Show HN"
```

Searches title text across the top 200 active stories.

### Track a story's performance

```bash
python hn.py stats 41234567
```

```
╔══════════════════════════════════════════╗
║  Score: 342  |  Comments: 142           ║
║  Velocity: 57 pts/hr                    ║
║  Front page rank: #3                    ║
║  Age: 3h 12m                            ║
╚══════════════════════════════════════════╝
```

### Live watch mode

```bash
python hn.py watch
```

Polls the front page every 60 seconds. Highlights new entries and rank changes. `Ctrl+C` to exit.

---

## Show HN Post Helper

Planning to post your project? The helper formats your title, validates the 80-char limit, checks what day/time it is, and tells you if you're in the optimal posting window.

```bash
python hn_post_helper.py \
  --title "Show HN: Nekomata — AI-native container engine in Common Lisp" \
  --url "https://github.com/SNAPKITTYWEST/nekomata" \
  --type show
```

```
╔══════════════════════════════════════════════════════════════╗
║  TITLE:  Show HN: Nekomata — AI container engine in CL     ║
║  CHARS:  52/80                                              ║
║  DAY:    Tuesday                                            ║
║  TIME:   10:32 AM ET                                       ║
║  WINDOW: OPTIMAL (Tue-Thu, 9am-2pm ET)                     ║
║                                                              ║
║  Opening HN submit page...                                  ║
╚══════════════════════════════════════════════════════════════╝
```

Options:
- `--type show` — prepends "Show HN: "
- `--type ask` — prepends "Ask HN: "
- `--type plain` — no prefix (default)
- `--no-browser` — print analysis only, don't open browser

**Optimal posting window:** Tuesday-Thursday, 9am-2pm US Eastern.

---

## How It Works

```
  python hn.py <command>
        │
        ▼
  HN Firebase API (https://hacker-news.firebaseio.com/v0/)
        │
        ├── /topstories.json      → list of story IDs
        ├── /item/{id}.json       → story/comment details
        └── /user/{name}.json     → user profile
        │
        ▼
  Format + colorize + print to terminal
```

No scraping. No authentication. Uses the official HN API directly over HTTPS via `urllib.request` from Python stdlib.

---

## Files

```
hn-client/
├── hn.py               Main client — all commands (280 lines)
├── hn_post_helper.py   Show HN posting assistant
├── requirements.txt    Empty — zero dependencies
└── README.md           This file
```

---

<p align="center"><b>Built by Ahmad Ali Parr + SnapKitty</b></p>
<p align="center"><i>Read HN without leaving the terminal.</i></p>
