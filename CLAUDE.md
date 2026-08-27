# NearEats landing page + blog

Marketing site and blog for the **NearEats** iOS app (restaurant, cafe & bar
finder), deployed via **GitHub Pages** at **neareats.12f.dk**. Built by 12F ApS.

- App Store: <https://apps.apple.com/us/app/neareats-restaurant-finder/id6754101006>
  (app id `6754101006`, Food & Drink, iOS 18+, **paid $1.99**, currently 0 ratings)
- App repo: `12fdk/NearEats` (local: `/Users/robert/Git/nearEats`) — separate repo,
  this one is the marketing site only.
- Site repo: `12fdk/neareats.12f.dk`

## The one job of this site

**Convert cold traffic into paid App Store downloads.** Every decision — layout,
copy, section order, blog topic — is judged on "does this make a hungry stranger
tap Download and pay $1.99?" There is no other goal: no newsletter, no lead
capture, no community, no docs.

Two funnels feed it:

1. **Direct / App Store referral** — the landing page has to do the whole selling
   job in one scroll, because there is no free trial (paid-upfront app).
2. **Search + AI answer engines** — the blog earns organic visibility for
   "where to eat" style queries and pipes readers into the same CTA.

Because the app is **paid-upfront with no trial**, the page must overcome
sight-unseen commitment: lead with the payoff, show real screenshots early,
make the price feel like an impulse ("less than a coffee, yours forever"),
and put risk-reduction (no ads, no account, no tracking, no subscription) next
to every CTA.

## Hard content rules

- **Never claim the app is "free"** anywhere — not "free to download", "no cost",
  "100% free", "no paywall". It is $1.99 paid-upfront. See
  `/Users/robert/Git/nearEats/MONETIZATION_STRATEGY.md` §6 for the canonical
  wording that was reconciled across all 49 App Store locales.
  *(Known drift: the app repo's `fastlane/screenshots_framed/*/title.strings`
  slot `10-Cafes` still reads "Free & Private" — do not copy that string onto
  this site; the approved replacement is "Private, No Ads".)*
  Allowed claims: "No ads", "No tracking / no account", "No subscription",
  "Buy once, yours forever".
- **No invented testimonials or star ratings.** The app has **0 public ratings**.
  Use *personas* ("For the traveller who just landed…"), like the sister sites do.
  Swap in real quotes only when they exist.
- **NearEats is a directory, not a review platform.** It has no ratings, reviews,
  photos or price levels from users — never imply otherwise. The honest pitch is
  *facts, not noise*: hours, diet, accessibility, amenities, awards, walking time.
- Everything on the page must be true of the shipped app. When in doubt, check
  `/Users/robert/Git/nearEats/fastlane/metadata/en-US/description.txt` and the
  app's `claude.md`.

## The product, factually (source of truth for all copy)

NearEats is an iPhone app that finds **restaurants, cafes and bars near you** and
tells you the things that decide where you actually go. Fully client-side — no
backend, no account, no tracking. Data comes from **OpenStreetMap (Overpass)** and
**Apple Maps**, merged so a venue found in both appears **once** with the best
fields of each. 30-day on-device cache, so it is fast and works offline-ish.

Shipped features worth selling (mirrors the 10-slot screenshot plan in
`/Users/robert/Git/nearEats/fastlane/SCREENSHOT_PLAN.md`):

| Feature | The line that sells it |
|---|---|
| Clustered map + synced list | Hundreds of places, one clear map |
| Smart open/closing status | Know what's open right now ("Closes in 25 min") |
| Restaurants / Cafes / **Bars** | The whole "where should we go" question |
| **Surprise me** | Can't decide? One tap picks for you |
| Venue detail | Michelin/Bib awards, hours, route-accurate walking ETA |
| Diet + accessibility badges | Vegan, halal, kosher, gluten-free, step-free — upfront |
| Warning badges | Cash only / not wheelchair accessible — the gotchas others bury |
| Search + filters | Search everything you've found; "Open late" filter |
| Visited "Been here" journal | Remember the good ones |
| Privacy | No account, no ads, no tracking, works anywhere |

App is localized into **49 storefront languages**; the *site* ships English-only
for now (revisit hreflang only if a storefront shows real organic demand).

## Brand — must match the app

**The site's design and colours are the app's.** Two palettes come out of the
app and they do different jobs:

- **The identity is the app icon** — an amber → coral map pin on charcoal,
  sampled from the shipped artwork: `#FFB025` → `#FF8740` → `#FF6750`, ground
  `#36333E`. **This is the site's brand.** It is the most-repeated asset a user
  sees (App Store, home screen, favicon, header, hero), and warm reads as
  appetising for a food app.
- **The interface is iOS system colours**, `AccentColor` = `#007AFF`. On the
  site, blue keeps exactly its in-app job: **links and secondary CTAs**.

The App Store screenshots are framed on a warm cream gradient (`#FDE8D6` →
`#FFFDF9`, ink `#1A1A1A`), which the site adopts as its surfaces. So:
**cream is the surface, the icon gradient is the action, blue is the link.**

- **Brand gradient** `linear-gradient(135deg, #FFB025, #FF6750)` — the icon,
  verbatim. **Never white on it** (1.8–2.9:1); buttons take dark ink `#2A1500`.
- **Deep ramp** `#C2410C → #9A2A12` for full-bleed bands carrying white copy
  (the closing CTA, the proof strip). One warm family, two luminance ends.
- **Green** `#34C759` = open now · **Orange** `#FF9500` = closes soon / award ·
  **Red** `#FF3B30` = warnings · **Purple** `#AF52DE` = found in both sources.
  These are semantics, not decoration — never re-assign them.
- **The rule that keeps brand amber apart from semantic orange:** brand warmth is
  always a *gradient*; semantic orange is always a *flat, bordered, icon-bearing
  chip*. Never a flat `#FFB025` chip, never a gradient in the badge row.
- System font stack; no web fonts, no frameworks, no build step for the pages.
- Light **and** dark mode via CSS custom properties + `prefers-color-scheme`.
- The app's Liquid Glass language translates to a `.glass` CSS treatment
  (backdrop blur, gradient hairline border, top shine) on the header, feature
  cards, chips and pricing card.

**The full spec — every token, component, breakpoint and the findings from the
reference sites — is in `DESIGN.md`. Read it before writing any CSS or HTML.**
`css/style.css` is the source of truth for the token *values*.

## Planned structure (mirrors snapdeck.12f.dk / wrnty.12f.dk)

```
CLAUDE.md             this file — what the project is and the rules
DESIGN.md             the design system: tokens, components, page anatomy
index.html            landing page
posts/<slug>.md       BLOG SOURCE OF TRUTH — frontmatter + markdown, one per post
prompt.md             the brief the automated blog job follows
blog/index.html       GENERATED from posts/ by tools/build.py
blog/<slug>/index.html GENERATED — never hand-edit
privacy-policy.html   privacy policy (app collects nothing; say so plainly)
404.html
css/style.css         the whole design system (tokens → components → responsive)
js/main.js            scroll reveals, sticky-header state, mobile nav
images/               app icon, favicons, OG image, App Store badge,
                      screenshots/en-US/, blog/<slug>.png
tools/build.py        renders the blog + every file that lists posts
tools/make-cover.py   branded gradient cover card (Pillow) — ComfyUI-down fallback
tools/reddit-topics.py what people are actually asking about eating out, ranked
feed.xml              RSS (generated)
CNAME                 neareats.12f.dk
robots.txt sitemap.xml llms.txt llms-full.txt   SEO + AI crawlers (blog parts generated)
b0b687723d7b1c12e407c2dfb52947d1.txt            IndexNow key
.github/workflows/indexnow.yml                  IndexNow submit on deploy
```

Use **absolute paths** (`/css/style.css`, `/images/...`) so blog subfolders resolve.

### Landing page anatomy (in order — order is the conversion argument)

1. **Hero** — headline + subhead + App Store badge + price reassurance line,
   phone screenshot right/below. Answers "what is it" in under two seconds.
2. **Features** — the depth that thin directories don't have (grid, 6 items).
3. **How it works** — three steps, one of which is "you don't sign up".
4. **Right now** — the open/closing-status + open-late story (the traveller's
   real question).
5. **Diet & accessibility** — vegan/halal/kosher/gluten-free/step-free, upfront.
   High-intent, high-differentiation, and a strong long-tail SEO surface.
6. **Compare** — "Guessing on the street vs. NearEats" table.
7. **Who it's for** — personas (traveller, dietary needs, wheelchair user,
   coffee-hunter, night out). **Not testimonials.**
8. **Pricing** — "$1.99 once. Yours forever." with the no-ads/no-tracking/
   no-subscription trio directly under it.
9. **Blog teaser** — 3 latest posts (generated).
10. **FAQ** — "Fair questions", incl. why it costs money, why no reviews/photos,
    where the data comes from, what happens to my location.
11. **Download** — final CTA.

CTA rule: an App Store button is always within one screen of the reader — hero,
mid-page, pricing, footer. Every page carries the Apple **Smart App Banner**
(`<meta name="apple-itunes-app" content="app-id=6754101006">`).

## Blog — `posts/*.md` is the source of truth

The blog exists to **buy organic visibility**, and it is written by an **external
LLM job**, not by hand. The contract:

- Write markdown to `posts/<slug>.md` (frontmatter schema documented in
  `prompt.md` §5 and **enforced by the build**), generate a cover, then build.
- **Never hand-edit `blog/<slug>/index.html`** — it is overwritten.

```bash
python3 tools/make-cover.py <slug> "<Title>" <tag>   # → images/blog/<slug>.png
python3 tools/build.py --check                        # validate (schema, links, lengths)
python3 tools/build.py                                # write everything
python3 -m http.server 8000                           # preview
```

`tools/build.py` rewrites every derived file: post pages, the blog index grid +
schema.org, the homepage teaser, `feed.xml`, blog URLs in `sitemap.xml`, and the
`## Blog` sections of `llms.txt` / `llms-full.txt`. Generated regions inside
hand-written files are fenced with `BLOG:*:START` / `BLOG:*:END` markers — leave
them in place.

Tags (edit `TAGS` in `build.py` to change the set): `city-guides`,
`eating-out`, `dietary`, `travel-tips`.

### The brief lives in `prompt.md`

`prompt.md` is the **authoritative brief** the automated job reads fresh on every
run — audience, the factual app description (see the table above), topic
selection, tone, the one-mention nudge budget, factual-accuracy rules, frontmatter
schema, images, publishing. The scheduler is a thin wrapper that only says "read
prompt.md and follow it", so **change strategy by editing `prompt.md` here, in
git** — never by editing the job. Same pattern as snapdeck.12f.dk,
wrnty.12f.dk, home-stories.12f.dk, event-stories.12f.dk, meugrana.12f.dk.

Non-negotiables to encode in `prompt.md`:

- The post must be worth reading **even if the app did not exist**; at most one
  natural mention + one CTA.
- Never call the app free; never invent reviews, ratings or venue photos.
- Local facts (opening hours, whether a place still exists) go stale — write
  evergreen guidance, not scrapeable listings, and never assert a specific
  venue's hours.
- Target the queries a hungry stranger actually types: "where to eat near me",
  "vegan restaurants in <city>", "wheelchair accessible restaurants", "late night
  food", "best coffee near me", "halal food while travelling".

Topic research: `python3 tools/reddit-topics.py` (Atom feeds, not the JSON API —
it 403s; paces, backs off on 429, caches to `.cache/` for a day, fails
gracefully). `prompt.md` falls back to a ranked topic bank when the scrape fails.

## SEO / GEO / AEO

- `sitemap.xml`, `robots.txt`, canonical URLs, OG + Twitter cards on every page.
- Schema.org: `SoftwareApplication` on the homepage (with `offers` at 1.99 USD —
  and **no** `aggregateRating` until real ratings exist), `Article` + `BreadcrumbList`
  on posts, `FAQPage` on the FAQ section.
- `llms.txt` / `llms-full.txt` for AI answer engines — this is where the app's
  factual description lives for LLM citation.
- **IndexNow** on every deploy: shared public key `b0b687723d7b1c12e407c2dfb52947d1`
  at the site root as `b0b687723d7b1c12e407c2dfb52947d1.txt`, plus the universal
  `.github/workflows/indexnow.yml` copied from `12fdk/wrnty.12f.dk`. Submits to
  Bing/Yandex/Seznam/Naver/Yep (Google doesn't participate — Search Console +
  sitemap covers it).
- The `seo-geo-aeo` skill audits the live site; run it after any significant
  content change.

## Assets

- Screenshots: take the framed ones from
  `/Users/robert/Git/nearEats/fastlane/screenshots_framed/en-US/*.png`, or the raw
  device captures from `fastlane/screenshots/en-US/` when the site should show the
  UI without the store title band. Resize to **640px WebP** into
  `images/screenshots/en-US/`. Never ship 1290×2796 PNGs to the browser.
- App icon → `images/` + favicons; OG image at `images/og.png` (1200×630).
- App Store badge is **self-hosted** at `/images/app-store-badge.svg` (never
  hotlink Apple's CDN).
- Blog covers are generated on the spark's ComfyUI
  (`http://spark-72aa.tail7196c.ts.net:8188`), with `tools/make-cover.py` as the
  fallback when it's down.

## Development & deployment

```bash
python3 -m http.server 8000     # no build tools for the static pages
```

Push to `main` → GitHub Pages auto-deploys → IndexNow workflow submits changed
URLs. Per repo convention: **branch per task, GitHub issues are the task tracker**
(`gh issue list`), keep issue bodies updated as work progresses.

## Analytics

Umami (privacy-focused) at umami.robert-jensen.dk — the tag belongs on **every**
page, including generated blog pages (put it in `tools/templates/post.html`).
Track the App Store CTA clicks as events so the funnel is measurable per section
and per blog post.

## Status

Greenfield — the repo is empty. Suggested build order:

1. `css/style.css` tokens (straight from `DESIGN.md` §2) + `index.html`
   hero/features/pricing/download — ship the converting page first.
2. Assets: screenshots, icon, favicons, OG, App Store badge, CNAME.
3. SEO plumbing: robots, sitemap, llms.txt, IndexNow key + workflow, Umami.
4. `privacy-policy.html`, `404.html`.
5. Blog engine: `posts/`, `tools/build.py`, `tools/templates/post.html`,
   `feed.xml`, blog teaser on the homepage.
6. `prompt.md` + the weekly cron job on the spark.

Start from `wrnty.12f.dk` — it is the closest sibling (same static stack, same
blog generator, IndexNow already wired) — and re-skin, rather than writing from
scratch.
