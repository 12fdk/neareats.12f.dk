#!/usr/bin/env python3
"""reddit-topics.py — what people are actually asking about where to eat,
eating out with dietary requirements, and finding food while travelling.

Feeds the weekly blog job (see prompt.md) with real reader demand instead of
whatever the model imagines hungry travellers worry about.

    python3 tools/reddit-topics.py                 # ranked digest, ~60 lines
    python3 tools/reddit-topics.py --json          # same data, machine-readable
    python3 tools/reddit-topics.py --refresh       # ignore the cache

WHY RSS AND NOT THE JSON API: reddit.com/r/<sub>/top.json returns 403 to both a
datacenter IP and a home IP now. The Atom feed at /r/<sub>/top/.rss is still
served, so that is what this uses. It is rate-limited though: hammer it and you
get 429s, which is why requests are paced, retried with backoff, and cached to
.cache/ for a day.

WHY A SCRIPT AND NOT A FEW CURL COMMANDS IN THE BRIEF: the Hermes agent's
terminal blocks `-c` / `-e` flags, so `python3 -c '...'` and clever one-liners
fail at runtime with BLOCKED. And raw feeds are ~50 KB each — a dozen of them
would bury the model's context. A plain command that prints a small digest
survives both constraints.

Failure is not fatal: if every feed fails, this exits 2 having printed a clear
message, and the brief falls back to the ranked topic bank in prompt.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "reddit-topics"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
ATOM = {"a": "http://www.w3.org/2005/Atom"}

# ORDER MATTERS. Reddit rate-limits hard and the time budget truncates the tail:
# a real run reached only 5 subs before --max-seconds ran out. So this is a
# priority list, highest-value first. The dietary and accessibility subs come
# first because they are where this app is most differentiated and where the
# questions are most specific; the general travel subs are the ones we can
# afford to lose.
SUBREDDITS = [
    "Celiac", "glutenfree", "HalalFood", "FoodAllergies", "wheelchairs",
    "vegan", "kosher", "disability",
    "solotravel", "travel", "digitalnomad", "AskCulinary",
]
WINDOWS = ["month", "year"]

# Theme buckets. A title can land in several; each is counted once per theme.
# Keep these lowercase and substring-matched — cheap, and good enough to rank.
THEMES: dict[str, tuple[str, list[str]]] = {
    "where-to-eat-new-city": ("Finding somewhere to eat in an unfamiliar city", [
        "where to eat", "where should i eat", "food recommendations", "restaurant recommendations",
        "any recommendations", "good places to eat", "first time in", "just arrived",
        "visiting", "few days in", "worth eating"]),
    "tourist-traps": ("Avoiding tourist traps and overpriced areas", [
        "tourist trap", "touristy", "overpriced", "avoid the", "rip off", "ripoff",
        "where do locals", "local spots", "not touristy", "authentic"]),
    "gluten-free": ("Eating gluten-free, especially away from home", [
        "gluten free", "gluten-free", "celiac", "coeliac", "cross contamination",
        "gf options", "safe to eat", "dedicated fryer", "gluten in"]),
    "halal-kosher": ("Finding halal or kosher food away from home", [
        "halal", "kosher", "muslim friendly", "halal restaurant", "kosher restaurant",
        "halal options", "is it halal", "find halal", "find kosher"]),
    "vegan-vegetarian": ("Eating vegan or vegetarian out", [
        "vegan", "vegetarian", "plant based", "veggie options", "vegan options",
        "vegan friendly", "anything vegan"]),
    "allergies": ("Eating out with allergies", [
        "allergy", "allergic", "nut allergy", "dairy free", "lactose",
        "anaphyla", "epipen", "allergen", "shellfish"]),
    "accessibility": ("Wheelchair access and step-free eating out", [
        "wheelchair", "accessible", "step free", "step-free", "ramp", "accessible toilet",
        "disabled access", "mobility", "can i get in"]),
    "opening-hours": ("Opening hours, late night and 'is it actually open'", [
        "open late", "late night", "still open", "opening hours", "what time do",
        "closes at", "open now", "kitchen closes", "open on sunday", "public holiday",
        "bank holiday"]),
    "coffee-cafes": ("Finding a decent coffee or a workable cafe", [
        "coffee shop", "cafe", "good coffee", "specialty coffee", "flat white",
        "work from a cafe", "laptop friendly", "wifi cafe"]),
    "bars-nights-out": ("Bars, pubs and where to go in the evening", [
        "bar", "pub", "craft beer", "brewery", "cocktail", "night out",
        "where to drink", "good bars"]),
    "with-kids": ("Eating out with children", [
        "with kids", "with a toddler", "child friendly", "kid friendly",
        "family friendly", "high chair", "changing table", "baby"]),
    "group-decisions": ("Deciding as a group, and decision fatigue", [
        "cant decide", "can't decide", "nobody can decide", "group of", "everyone wants",
        "picking a restaurant", "how do you choose", "decision"]),
    "solo-dining": ("Eating alone without awkwardness", [
        "eating alone", "solo dining", "dine alone", "table for one", "by myself",
        "awkward eating"]),
    "paying": ("Cash, cards, tipping and paying the bill", [
        "cash only", "card only", "do they take card", "tipping", "service charge", "leave a tip",
        "split the bill", "contactless"]),
    "new-in-town": ("Just moved somewhere and finding regular spots", [
        "just moved", "new to the city", "new in town", "moved here", "relocating",
        "my new neighbourhood", "my new neighborhood", "local recommendations"]),
    "map-apps": ("Map and restaurant apps, reviews and their limits", [
        "google maps", "yelp", "tripadvisor", "openstreetmap", "review", "reviews",
        "star rating", "fake reviews", "app for finding", "best app"]),
    "dog-friendly": ("Eating out with a dog", [
        "dog friendly", "dog-friendly", "with my dog", "bring my dog", "pet friendly"]),
}

# Titles that are jokes, screenshots, brag-posts or venting. On these subs the
# "my X lasted 20 years" story posts dominate /top and carry no query intent.
NOISE = [
    "haha", "lol", "lmao", "meme", "rate my", "my setup", "look what", "found this",
    "haul", "unboxing", "day in the life", "psa:", "just wanted to share",
    "guess the", "who else", "relatable", "me when", "pov", "before and after",
    "update:", "trip report", "photo dump", "pics from", "my trip", "i made",
    "made this", "homemade", "first attempt", "recipe", "cooked", "look at this",
    "[oc]", "album", "sunset", "what did i eat",
    # Rhetorical and venting posts. These carry a "?" or a question word, so
    # is_useful() waved them through on a real run — "One of the Best Perks of
    # Being Vegan? Creativity.", "Is it just me or are doctors…", "My favourite
    # part of being celiac is…". They are community discourse, not queries.
    "is it just me", "am i the only", "anyone else feel", "does anyone else feel",
    "my favourite part", "my favorite part", "best perks", "perks of being",
    "rant", "vent", "unpopular opinion", "am i wrong", "aita", ", right?",
    "why do you", "why do people", "so tired of", "i'm done with", "im done with",
    "the audacity", "you won't believe", "you wont believe",
]

# Rhetorical tag questions ending a title — "…, right?", "…, isn't it?". These
# are agreement-fishing, not queries, and a plain NOISE substring can't catch
# them reliably because of intervening quote marks.
TAG_QUESTION = re.compile(
    r"\b(right|isn'?t it|aren'?t they|am i wrong|or is it just me)\s*[?!]+\s*$")
QUESTION_WORDS = [
    "how", "what", "why", "when", "which", "anyone", "does", "do you", "should",
    "tips", "advice", "help", "is it", "can i", "any way", "best way", "struggl",
    "cant", "can't", "trouble", "problem", "recommend", "worth", " vs ", "or replace",
]


def cache_path(sub: str, window: str) -> Path:
    return CACHE / f"{sub}-{window}.xml"


def read_cache(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def save_cache(path: Path, body: str, verbose: bool) -> None:
    """Best effort. A read-only checkout must not cost us a fetched feed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    except OSError as e:
        if verbose:
            print(f"  (cache not written: {e.__class__.__name__})", file=sys.stderr)


def fetch(sub: str, window: str, pace: float, ttl: int, refresh: bool,
          verbose: bool, deadline: float) -> tuple[str | None, bool]:
    """Return (xml, from_cache). None means this feed is unavailable.

    Reddit rate-limits anonymous RSS hard — 429 is the normal response to any
    enthusiasm — so requests are paced, backed off, and finally given up on.
    Progress goes to stderr on every feed: a scheduled run is killed after 600s
    of silence, and the backoffs alone can exceed that.
    """
    path = cache_path(sub, window)
    if not refresh and path.exists() and (time.time() - path.stat().st_mtime) < ttl:
        cached = read_cache(path)
        if cached:
            if verbose:
                print(f"  r/{sub:<16} [{window}] cached", file=sys.stderr)
            return cached, True

    url = f"https://www.reddit.com/r/{sub}/top/.rss?t={window}"
    for attempt in range(4):
        if time.time() > deadline:
            if verbose:
                print(f"  r/{sub:<16} [{window}] skipped (time budget spent)", file=sys.stderr)
            break
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept": "application/atom+xml"})
            with urllib.request.urlopen(req, timeout=25) as r:
                body = r.read().decode("utf-8", "replace")
            save_cache(path, body, verbose)
            if verbose:
                print(f"  r/{sub:<16} [{window}] ok", file=sys.stderr)
            time.sleep(pace)
            return body, False
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                wait = 30 * (attempt + 1)
                if verbose:
                    print(f"  r/{sub:<16} [{window}] {e.code} — waiting {wait}s",
                          file=sys.stderr)
                time.sleep(min(wait, max(0.0, deadline - time.time())))
                continue
            if verbose:
                print(f"  r/{sub:<16} [{window}] unavailable (HTTP {e.code})", file=sys.stderr)
            break
        except Exception as e:                                    # network, DNS, timeout
            if verbose:
                print(f"  r/{sub:<16} [{window}] unavailable ({type(e).__name__})",
                      file=sys.stderr)
            break

    stale = read_cache(path) if path.exists() else None            # stale beats nothing
    if stale:
        if verbose:
            print(f"  r/{sub:<16} [{window}] using stale cache", file=sys.stderr)
        return stale, True
    return None, False


def titles_from(xml: str) -> list[str]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    out = []
    for entry in root.findall("a:entry", ATOM):
        node = entry.find("a:title", ATOM)
        if node is not None and node.text:
            out.append(re.sub(r"\s+", " ", node.text).strip())
    return out


# Reddit titles are full of smart punctuation. Normalise it before matching, or
# a pattern like ", right?" misses «Being "Abused," Right?» purely on quote style.
_SMART = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                        "\u2013": "-", "\u2014": "-", "\u2026": "..."})


def normalise(title: str) -> str:
    return title.translate(_SMART)


def is_useful(title: str) -> bool:
    low = f" {normalise(title).lower()} "
    if len(title) < 20:
        return False
    # _matches, not `in` — plain substring matching had "rant" killing every
    # title containing "restaurants", which is most of the useful ones.
    if any(_matches(n, low) for n in NOISE):
        return False
    if TAG_QUESTION.search(low):
        return False
    # All-caps venting posts carry no query intent.
    if sum(c.isupper() for c in title) > len(title) * 0.6:
        return False
    return any(_matches(w, low) for w in QUESTION_WORDS) or "?" in title


# Short keywords must match on word boundaries, with an optional plural "s".
# Plain substring matching put "bathroom" under bars ("bar") and "multiple"
# under paying ("tip") — both seen in a real run — while a strict boundary
# missed "Best bars in Berlin?". Multi-word phrases stay substring matches,
# since those are specific enough on their own.
_BOUNDARY_CACHE: dict[str, re.Pattern] = {}


def _matches(word: str, low: str) -> bool:
    if " " in word or len(word) > 9:
        return word in low
    pat = _BOUNDARY_CACHE.get(word)
    if pat is None:
        pat = _BOUNDARY_CACHE[word] = re.compile(rf"(?<![a-z]){re.escape(word)}s?(?![a-z])")
    return bool(pat.search(low))


def themes_of(title: str) -> list[str]:
    low = f" {normalise(title).lower()} "
    return [key for key, (_, words) in THEMES.items()
            if any(_matches(w, low) for w in words)]


def covered_themes() -> dict[str, list[str]]:
    """Map theme -> [slugs] for themes an existing post already addresses.

    Matched against the title and keywords only — a summary that mentions
    coffee in passing is not a post about finding a decent coffee.
    """
    out: dict[str, list[str]] = {}
    posts_dir = ROOT / "posts"
    if not posts_dir.is_dir():
        return out
    for path in sorted(posts_dir.glob("*.md")):
        head = path.read_text(encoding="utf-8")[:3000].split("\n---", 1)[0]
        subject = " ".join(
            line.split(":", 1)[1] for line in head.split("\n")
            if line.split(":", 1)[0].strip() in ("title", "keywords") and ":" in line
        )
        for key in themes_of(f"{subject} {path.stem.replace('-', ' ')}"):
            out.setdefault(key, []).append(path.stem)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subs", help="comma-separated subreddits (default: the consumer set)")
    ap.add_argument("--windows", default=",".join(WINDOWS), help="top windows: month,year")
    ap.add_argument("--pace", type=float, default=8.0, help="seconds between requests")
    ap.add_argument("--max-seconds", type=float, default=600.0,
                    help="total time budget; stops fetching and reports what it has")
    ap.add_argument("--ttl", type=int, default=20 * 3600, help="cache lifetime in seconds")
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    ap.add_argument("--themes", type=int, default=8, help="how many themes to report")
    ap.add_argument("--examples", type=int, default=3, help="example titles per theme")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true", help="no progress on stderr")
    a = ap.parse_args()

    subs = [s.strip() for s in (a.subs.split(",") if a.subs else SUBREDDITS) if s.strip()]
    windows = [w.strip() for w in a.windows.split(",") if w.strip()]
    verbose = not a.quiet

    if verbose:
        print(f"Reading {len(subs)} subreddits x {len(windows)} windows "
              f"(~{a.pace:.0f}s apart, cached {a.ttl // 3600}h, "
              f"{a.max_seconds:.0f}s budget)...", file=sys.stderr)

    deadline = time.time() + a.max_seconds
    seen: set[str] = set()
    entries: list[tuple[str, str, int]] = []          # (title, sub, rank)
    ok = cached = failed = 0
    # Windows outer, subs inner: with a budget that truncates, every subreddit
    # should get its "month" feed before any subreddit gets its "year".
    for window in windows:
        for sub in subs:
            xml, from_cache = fetch(sub, window, a.pace, a.ttl, a.refresh, verbose, deadline)
            if xml is None:
                failed += 1
                continue
            ok += 1
            cached += 1 if from_cache else 0
            for rank, title in enumerate(titles_from(xml)):
                key = re.sub(r"[^a-z0-9]+", "", title.lower())[:60]
                if key in seen:
                    continue
                seen.add(key)
                entries.append((title, sub, rank))

    if not entries:
        print("reddit-topics: every feed failed (Reddit is blocking or offline).\n"
              "Fall back to the ranked topic bank in prompt.md — that is expected "
              "and fine.", file=sys.stderr)
        return 2

    useful = [(t, s, r) for t, s, r in entries if is_useful(t)]
    covered = covered_themes()

    buckets: dict[str, dict] = {}
    for title, sub, rank in useful:
        for key in themes_of(title):
            b = buckets.setdefault(key, {"key": key, "label": THEMES[key][0],
                                         "count": 0, "weight": 0.0,
                                         "titles": [], "covered_by": covered.get(key, [])})
            b["count"] += 1
            b["weight"] += 1.0 / (rank + 3)           # higher in /top = stronger demand
            b["titles"].append(title)

    ranked = sorted(buckets.values(), key=lambda b: (b["weight"], b["count"]), reverse=True)
    for b in ranked:
        b["weight"] = round(b["weight"], 2)
        b["titles"] = sorted(b["titles"], key=len)[-a.examples * 3:][::-1][:a.examples]

    fresh_themes = [b for b in ranked if not b["covered_by"]]
    done_themes = [b for b in ranked if b["covered_by"]]

    if a.as_json:
        print(json.dumps({
            "feeds_ok": ok, "feeds_failed": failed, "feeds_from_cache": cached,
            "posts_seen": len(entries), "posts_useful": len(useful),
            "themes": ranked,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"REDDIT DEMAND — {ok} feeds ({cached} cached, {failed} unavailable), "
          f"{len(entries)} posts, {len(useful)} carrying a real question")
    print()
    print(f"UNCOVERED THEMES — strongest demand first")
    if not fresh_themes:
        print("  (every theme is already covered — write a fresher angle on a top one)")
    for i, b in enumerate(fresh_themes[:a.themes], 1):
        print(f"{i:2}. {b['label']}  [{b['key']}]  {b['count']} posts, weight {b['weight']}")
        for t in b["titles"]:
            print(f"      · {t[:110]}")
    print()
    print("ALREADY COVERED")
    for b in done_themes[:8]:
        print(f"  - {b['label']} ({b['count']}) → {', '.join(sorted(set(b['covered_by'])))}")
    print()
    print("TOP QUESTION TITLES VERBATIM — the reader's own words, use them")
    on_topic = [e for e in useful if themes_of(e[0])]
    for title, sub, rank in sorted(on_topic, key=lambda e: e[2])[:15]:
        print(f"  · [r/{sub}] {title[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
