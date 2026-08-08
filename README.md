# hn-client

HackerNews terminal client. Zero dependencies — pure Python stdlib.

```bash
python hn.py show              # Show HN right now
python hn.py top               # front page
python hn.py new               # newest
python hn.py best              # best
python hn.py read <id>         # story + top comments
python hn.py user <username>   # profile + karma
python hn.py search <query>    # filter top 200 stories
python hn.py stats <id>        # score, velocity, front page rank
python hn.py watch             # live trending, refreshes every 60s
```

---

## Show HN post helper

Formats your title, checks the 80-char limit, checks the posting window, and opens the HN submit page.

```bash
python hn_post_helper.py \
  --title "Your thing here" \
  --url "https://github.com/you/your-repo" \
  --type show

# --no-browser  print only, don't open the browser
# --type ask    Ask HN prefix
# --type plain  no prefix (default)
```

Optimal posting window: **Tuesday–Thursday, 9am–2pm US Eastern.** The helper tells you where you are right now.

---

## Install

No install required. Clone and run:

```bash
git clone https://github.com/SNAPKITTYWEST/hn-client
cd hn-client
python hn.py top
```

Requires Python 3.9+. No pip install. No venv.

---

## Commands

| Command | What it does |
|---------|-------------|
| `top` | Front page top 30 |
| `new` | Newest 30 |
| `show` | Show HN feed |
| `best` | Best stories feed |
| `ask` | Ask HN feed |
| `read <id>` | Story text + top 10 comments |
| `user <name>` | Karma, join date, about, submission count |
| `search <query>` | Title search across top 200 stories |
| `stats <id>` | Score, comments, velocity (pts/hr), front page rank |
| `watch` | Poll top 30 every 60s — shows new entries and rank changes |

---

Built by Ahmad Ali Parr × SnapKitty.
