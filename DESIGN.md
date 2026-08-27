# NearEats site — design system & findings

The visual/UX spec for **neareats.12f.dk**. Built from three sources:

1. **The app itself** — `/Users/robert/Git/nearEats` (its `claude.md`,
   `LIQUID_GLASS_UI_ENHANCEMENTS.md`, and the actual colours in
   `NearEats/Views/Components/*.swift`). **The site must look like the app.**
2. The two reference sites — `/Users/robert/Git/wrnty.12f.dk` and
   `/Users/robert/Git/snapdeck.12f.dk` — which supply the *structure*.
3. The App Store listing assets — `fastlane/screenshots_framed/` and
   `frame_screenshots.sh` — which supply the warm surround.

Companion doc: `CLAUDE.md` (what the project is, the blog pipeline, the content
rules). This file is *how it looks and behaves*.

> **Prime directive: the site's design and colours must match the app.** A visitor
> who scrolls the page and then opens the App Store screenshots must see the same
> product. Colours are taken from the app's icon and source, not invented — §2
> lists the exact mapping. The web build translates the app's **Liquid Glass**
> language into CSS (§3); it does not replace it with a generic marketing look.
>
> **The site leads with the icon's warm amber → coral, not the in-app blue**
> (decided 2026-08-27, issue #14). The icon is the most-repeated brand asset —
> App Store, home screen, favicon, header, hero — and it is warm; blue buttons
> under an amber pin read as two brands. Blue keeps its in-app job: links and
> secondary interactive.

---

## 1. Findings from the reference sites

Both sister sites are the **same system re-skinned**, which is the single most
useful finding: don't invent a stack, inherit one — then paint it in NearEats'
colours.

| Finding | What it means for us |
|---|---|
| **Zero build step, zero dependencies** for the pages. One `css/style.css` (~1150 lines), one `js/main.js` (~67 lines), hand-written HTML. | Do the same. `python3 -m http.server 8000` is the whole dev loop. No Tailwind, no Astro, no npm. |
| **CSS custom properties are the entire theming layer.** Tokens at the top, then a `@media (prefers-color-scheme: dark)` block that only re-declares tokens. | Re-skinning = changing hex values in one place. Never hard-code a colour below the token block. |
| **File order: tokens → reset/base → layout helpers → components → responsive → motion/print → blog.** | Keep that order; it's why the file stays navigable at 1000+ lines. |
| **One accent does all the "premium/attention" work** (wrnty amber, snapdeck gold). | Ours is the app's **orange** — and it already means something in the app ("closes soon", awards, brunch). See §2. |
| **A hand-drawn SVG highlighter** (`--marker`) + squiggly underline (`--underline`) as inline data-URIs behind hero words. | Keep the device, recoloured to brand amber `#FFB025` — *not* the semantic orange, or the highlighter reads as "closes soon". |
| **Sections alternate `.section` / `.section--soft`.** 96px vertical padding desktop, 68px mobile. | Same cadence. |
| **Phones are CSS-framed screenshots** — a `.phone` wrapper with radius, border, shadow and a `::before` notch/shine, rotated ±4–7° and overlapped. | Use the app's **raw** captures, not the store-framed ones with the title band burned in. |
| **`.fade-in` + IntersectionObserver** is the only scroll animation; everything else is a hover transform. | Restraint. Nothing autoplays, nothing parallaxes. |
| **App Store badge is self-hosted SVG**, 54px tall, hover `translateY(-2px) scale(1.02)`. | Copy `/images/app-store-badge.svg` across. |
| **`.vs` comparison table** with the "us" column tinted `color-mix(in srgb, var(--brand) 6%, var(--surface))`. | Strong converter. Ours: "Guessing on the street vs. NearEats". |
| **Personas, never testimonials** — both apps have no public ratings. | NearEats has **0 ratings**. Same treatment. Never fabricate stars or `aggregateRating`. |
| **FAQ is `<details>/<summary>`** with a CSS chevron — no JS, and it doubles as `FAQPage` schema. | Same. |
| **Closing CTA is a full-bleed brand-gradient band** with a radial `::before` highlight. | Same, in `--brand-deep` rust — the bright icon gradient cannot carry white copy. |
| **Every page**: skip-link, `.visually-hidden`, `:focus-visible` 3px outline, `prefers-reduced-motion` kill-switch, print stylesheet. | Non-negotiable, carry all of it. |

Register: **wrnty** is trustworthy-utility, **snapdeck** is playful. NearEats sits
with wrnty — a tool you trust when you're hungry in an unfamiliar city — but the
app's glass + system-blue look is closer to snapdeck's tech polish. Structurally,
**start from wrnty** (IndexNow already wired, cleaner blog templates,
`make-cover.py` fallback) and repaint.

---

## 2. Colour — taken from the app, verbatim

Two palettes come out of the app, and they do different jobs.

**The identity** is the app icon: an amber → coral map pin on charcoal, sampled
from the shipped 1024px artwork — `#FFB025` (pin top) → `#FF8740` (mid) →
`#FF6750` (tip), ground `#36333E`. This is the site's **brand**.

**The interface** is iOS system colours with `AccentColor` = system blue
(`sRGB 0.000, 0.478, 1.000` = `#007AFF`, identical in light and dark, per
`NearEats/Assets.xcassets/AccentColor.colorset`). Every colour in the table below
is the iOS system value for the colour the app actually names in code, so the
site's chips render the same hue as the screenshots sitting next to them. Blue
stays the **link and secondary** colour on the site, as it is in the app.

### 2.1 The app's semantic palette (source → meaning → web token)

| App code | Means (in the app) | Light | Dark | Web token |
|---|---|---|---|---|
| `.accentColor` / `.blue` (100+ uses) | Everything interactive; map pins; Apple Maps source | `#007AFF` | `#0A84FF` | `--blue` |
| `.purple` | A venue found in **both** OSM and Apple Maps ("Merged"); the other half of every glass gradient | `#AF52DE` | `#BF5AF2` | `--purple` |
| `.green` | **Open now**; OpenStreetMap source; vegan / vegetarian / organic | `#34C759` | `#30D158` | `--green` |
| `.orange` | **Closes soon**; awards/stars; gluten-free, dairy-free, breakfast, brunch, fireplace | `#FF9500` | `#FF9F0A` | `--orange` |
| `.red` | **Warnings** — cash only, not wheelchair accessible; saved/favourite | `#FF3B30` | `#FF453A` | `--red` |
| `.teal` | Halal | `#30B0C7` | `#40C8E0` | `--teal` |
| `.indigo` | Kosher; Wi-Fi | `#5856D6` | `#5E5CE6` | `--indigo` |
| `.pink` | Family-friendly | `#FF2D55` | `#FF375F` | `--pink` |
| `.brown` | Microbrewery; dog-friendly | `#A2845E` | `#AC8E68` | `--brown` |
| `.cyan` | Air conditioning | `#32ADE6` | `#64D2FF` | `--cyan` |
| `.yellow` | Outdoor seating | `#FFCC00` | `#FFD60A` | `--yellow` |
| `Color(red:0.72,green:0.55,blue:0.15)` (`VenueDetailView.swift:907`) | Michelin / Bib award badge, as a gradient from `#D9AE38` → `#B78C26` | `#B78C26` | same | `--gold` / `--gold-2` |

**The brand gradient is the icon, verbatim** — `#FFB025 → #FF6750` at 135°. Two
things follow from its luminance, and both are hard rules:

```css
--gradient: linear-gradient(135deg, #FFB025 0%, #FF6750 100%);
--on-gradient: #2A1500;   /* the ONLY safe ink on it: 9.53:1 / 6.06:1 */
```

1. **Never put white on `--gradient`.** White scores 1.83:1 at the amber end and
   2.87:1 at the coral end. Buttons on the brand gradient take dark ink.
2. Full-bleed bands that carry **white** copy use the deep ramp instead:
   ```css
   --brand-deep: linear-gradient(135deg, #C2410C 0%, #9A2A12 100%);  /* white: 5.18 / 7.74 */
   --warm-ink:   #A83A0C;   /* warm text on white / cream: 6.41 / 6.05 / 5.40 */
   ```
   So: bright icon gradient on **buttons** (dark ink), deep rust on **bands**
   (white copy). One warm family, two luminance ends.

The app's Liquid Glass components also carry a low-opacity **blue → purple** wash
(`LiquidGlassLoadingView`, `LiquidGlassRestaurantCard:573`,
`LiquidGlassDistanceFilter:128`). That stays a *glass tint* on the site, not the
brand gradient.

### 2.2 Surfaces — the App Store cream

`fastlane/frame_screenshots.sh` frames every store screenshot on a warm gradient
`#FDE8D6` → `#FFFDF9` with near-black `#1A1A1A` titles. The site adopts that as
its surface family, so the page and the listing are visibly the same campaign:
**cream is the surface, the icon gradient is the action, blue is the link.**

| Role | Light | Dark |
|---|---|---|
| `--bg` | `#FFFFFF` | `#0F0D0B` (warm-black — keeps the cream family) |
| `--bg-soft` | `#FFF7EF` (pale end of the store gradient) | `#17140F` |
| `--bg-sunk` | `#FDE8D6` (deep end — hero backdrop) | `#1F1A14` |
| `--surface` | `#FFFFFF` | `#1A1611` |
| `--glass` | `rgba(255,255,255,.62)` | `rgba(35,30,24,.58)` |
| `--ink` | `#1A1A1A` (the store titles' colour) | `#F7F2EC` |
| `--ink-2` | `#55575C` | `#B5AEA4` |
| `--ink-3` | `#85888E` | `#8C8578` |
| `--line` | `#EADFD3` (warm hairline — this is a cream page) | `#2E271F` |

> **`css/style.css` is the source of truth for the token values.** This document
> explains *why* each one is what it is; it does not duplicate the block, because
> a second copy only drifts. Read the `:root` block in the stylesheet for the
> exact list — including a matching `--*-ink` for every badge hue and the
> `--*-wash` set, all computed to clear AA (§2.3).

### 2.3 Colour rules

- **Semantics are inherited, not re-assigned.** Green means open, orange means
  closing soon or an award, red means a warning. Never use green as a decorative
  accent or red for anything that isn't a genuine caveat — it would contradict the
  screenshots directly beside it.
- **Brand warmth is always a gradient. Semantic orange is always a flat,
  bordered, icon-bearing chip.** This is the rule that keeps brand amber
  (`#FFB025`) from being read as "closes soon" (`#FF9500`) — the two hues are
  close, so the *form* has to separate them. Never a flat `#FFB025` chip; never a
  gradient in the badge row.
- Blue is not decoration either — it is links and secondary CTAs, mirroring the
  app. `.btn--blue` uses `--blue-strong`, because white on `#007AFF` is 4.02:1.
- Contrast: `#007AFF` fails AA on white for small text — that's what
  `--blue-strong` is for. Same for `--green-ink` / `--orange-ink` / `--red-ink` on
  their washes. Every button pair must clear **4.5:1**.
- Never rely on hue alone — the app pairs every badge with an SF Symbol and a
  word; the site does the same with an inline SVG icon and a label.

**Typography.** System stack only, no web fonts — the same faces the app renders
in: `-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`.

| Element | Size |
|---|---|
| `h1` | `clamp(2.5rem, 6.2vw, 4.4rem)`, 800, `letter-spacing: -0.03em` |
| `h2` | `clamp(1.9rem, 4vw, 2.9rem)`, 800, `-0.02em` |
| `h3` | `1.15–1.35rem`, 700 |
| `.lede` | `clamp(1rem, 2vw, 1.15rem)`, `--ink-2` |
| body | `1rem / 1.6` |
| meta / chips | `0.82–0.96rem` |

Two weights carry the page (650/800 emphasis, 400 body). Prose measure `62–70ch`.
The app leans on **semibold** for hierarchy — mirror that rather than going light.

---

## 3. Liquid Glass, on the web

The app's design system (`nearEats/claude.md`,
`LIQUID_GLASS_UI_ENHANCEMENTS.md`) is: `.ultraThinMaterial` surfaces, gradient
hairline borders (white 50% → 10%, top-leading → bottom-trailing), a top shine,
multi-layer shadows with a coloured glow, spring animations, 12–16pt radii. The
site echoes it with a `.glass` treatment used on the header, the feature cards,
the badge chips and the pricing card — **not** on every surface, or the page
turns to soup.

```css
.glass {
  background: var(--glass);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid transparent;
  border-radius: var(--r-md);
  background-clip: padding-box;
  box-shadow: var(--shadow-md);
  position: relative;
}
/* gradient hairline border, the app's white 50% → 10% */
.glass::after {
  content: ''; position: absolute; inset: 0; border-radius: inherit;
  padding: 1px; pointer-events: none;
  background: linear-gradient(135deg, rgba(255,255,255,.5), rgba(255,255,255,.1));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
}
/* top shine, the app's first-40px white gradient */
.glass::before {
  content: ''; position: absolute; inset: 0 0 auto; height: 40px;
  border-radius: inherit inherit 0 0; pointer-events: none;
  background: linear-gradient(180deg, rgba(255,255,255,.28), transparent);
}
```

- `backdrop-filter` needs something behind it: only put `.glass` over the cream
  washes, the gradient bands or a screenshot — never over flat `--bg`.
- Provide a solid `--surface` fallback via `@supports not (backdrop-filter: blur(1px))`.
- Selected/active states get the app's accent overlay (`--blue` at 12% → 4%) plus
  a soft outer glow, exactly like the app's cards.
- Press feedback mirrors the app's `scale(0.96–0.98)`; hovers lift 2–4px with a
  spring-ish `cubic-bezier(0.34, 1.56, 0.64, 1)`.

---

## 4. Components

Inherit wrnty's component set, repainted per §2 and glassed per §3.

- **`.btn`** — pill, `padding: 14px 26px`, 700, hover `translateY(-2px)`.
  Variants: `--primary` (the icon gradient, **dark ink `--on-gradient`**, warm
  `--shadow-brand`), `--blue` (flat `--blue-strong`, white — the secondary CTA),
  `--ghost` (transparent, `--line` border, warm hover), `--sm`.
- **`.app-badge`** — self-hosted SVG, 54px. *The* conversion element: header,
  hero, mid-page, pricing, closing CTA.
- **`.phone`** — CSS frame around a raw screenshot: `border-radius: 38px`, 4px
  `--surface` border, `--shadow-lg`, `::before` notch/shine. Hero uses three
  (−7° / centre / +7°); split sections use two at ±4°.
- **`.hero-trust`** — inline row under the hero sub: *No account · No ads · No
  tracking · Works anywhere*. Ticks in `--green`.
- **`.strip`** — thin `--brand-deep` band of proof numbers under the hero:
  **3 categories · 2 map sources · 49 languages · 0 accounts.**
- **`.feature-grid` / `.feature`** — 3-up glass cards, hover lift 4px, border
  tints toward `--blue`. Icon in a 46px rounded-square wash, using the *app's*
  colour for that concept (open-now icon green, warning icon red, …).
- **`.badge-row`** *(NearEats-specific, the most important visual on the page)* —
  the app's amenity badges rebuilt as static HTML chips in the exact app colours:
  green **Open now**, orange **Closes in 25 min**, green **Vegan**, teal
  **Halal**, indigo **Kosher**, orange **Gluten-free**, yellow **Outdoor
  seating**, brown **Dog-friendly**, indigo **Wi-Fi**, red **Cash only**, red
  **Not wheelchair accessible**, gold **Michelin**. Chip: `--r-pill`, `0.82rem`,
  wash background, matching ink, 1px border of the same hue at 30%, SF-Symbol-
  equivalent inline SVG on the left. Warning chips are the only ones with a
  filled red border, mirroring `AmenityBadges.swift`.
- **`.split`** — copy + phones, two columns, alternating side.
- **`.vs`** — comparison table, "us" column tinted blue at 6%.
- **`.persona-grid` / `.persona`** — emoji avatar in a wash circle, heading, body,
  tag chip. **Personas, not testimonials.**
- **`.plan`** — a *single* pricing card (the sisters have free/premium; NearEats
  has one price). `$1.99` at `2.3rem/800`, "once — yours forever", tick list of
  what "no subscription" buys, badge. `.plan-flag` in brand amber with dark ink:
  *One-time purchase*.
- **`.faq-item`** — `<details>`/`<summary>`, CSS chevron, no JS.
- **`.closing-cta`** — full-bleed `--brand-deep` band, radial `::before`
  highlight in brand amber, white copy, badge.
- **`.map-legend`** *(optional, small)* — mirrors `MapLegendView.swift`: green
  OpenStreetMap, blue Apple Maps, purple "In both — merged". A neat, honest way
  to show the two-source story.
- **Blog**: `.post-grid` (3-up, 1200×630 covers, `aspect-ratio` locked),
  `.post-card` (hover lift, whole-card link via `::after { inset: 0 }`), `.tag`,
  `.post-meta` with dot separators, `.article` + `.prose`.

---

## 5. Page anatomy & the conversion argument

Order is the argument. Each section kills the next objection a cold, hungry
stranger raises. An App Store badge is never more than one screen away.

| # | Section | Objection it kills |
|---|---|---|
| 1 | **Hero** — h1 with the brand-amber marker on the key phrase, sub, badge, trust row, three phones on the cream backdrop | "What is this?" |
| 2 | **Strip** — proof numbers | "Is it real?" |
| 3 | **Features** — 6 glass cards | "Isn't this just Maps?" |
| 4 | **How it works** — 3 steps, one being "you don't sign up" | "How much setup?" |
| 5 | **Right now** (split) — open/closing status, open-late filter, walking ETA | "Will it help me *tonight*?" |
| 6 | **Diet & accessibility** (split + `.badge-row`) — vegan, halal, kosher, gluten-free, step-free, plus the red warnings | "Can I even eat there?" — highest intent, highest differentiation |
| 7 | **Compare** (`.vs`) — Guessing on the street vs. NearEats | "Why not just wander?" |
| 8 | **Who it's for** — personas: the traveller, the coeliac, the wheelchair user, the coffee hunter, the group that can't decide | "Is this for me?" |
| 9 | **Pricing** — $1.99 once, yours forever + no-ads / no-tracking / no-subscription | "Why does it cost money?" |
| 10 | **Blog teaser** — 3 latest posts (generated) | SEO surface + depth signal |
| 11 | **FAQ** — why paid, why no reviews or photos, where the data comes from, what happens to my location | residual doubt |
| 12 | **Closing CTA** | — |

**Hero register** (not final copy): arrival + decision — *"Find somewhere good to
eat, ==wherever you just landed=="* — sub naming restaurants, cafes **and bars**,
hours, diet and step-free access, one-tap directions, no account.

**Copy constraints that are also design constraints** (full list in `CLAUDE.md`):
the word *free* never describes the app; no stars, review counts or
`aggregateRating`; nothing implies user photos or ratings — NearEats is a facts
directory, and the visual language must not borrow review-app furniture.

---

## 6. Motion, accessibility, responsive

**Motion.** `.fade-in` (opacity 0 → 1, `translateY(16px)`) via IntersectionObserver
(`threshold: 0.1, rootMargin: 0px 0px -40px`); hover lifts 2–4px; press
`scale(0.98)`; the header gaining a border and stronger blur past `scrollY > 8`.
That is the whole motion budget. Wrap the reveal CSS in
`@media (scripting: enabled)` so no-JS gets full opacity.
`prefers-reduced-motion: reduce` kills every transition, animation, smooth scroll
and hover transform — the app respects `accessibilityReduceMotion`, so the site
must too.

**Accessibility** (mandatory, all inherited from the reference sites):
- Skip link to `#main`; `.visually-hidden` utility.
- `:focus-visible { outline: 3px solid var(--amber); outline-offset: 3px }`.
- Semantic landmarks, one `h1`, no heading-level skips.
- Nav toggle carries `aria-expanded`; Escape closes and restores focus.
- Real alt text on every screenshot; decorative SVG `aria-hidden="true"`.
- AA contrast in both themes; never colour alone (icon + word on every chip).
- Check at 200% zoom and with VoiceOver rotor headings. The app is a
  VoiceOver/Dynamic Type citizen — the site should not be the weak link.

**Breakpoints** (max-width, matching the reference sites exactly):

| BP | Changes |
|---|---|
| `1024px` | feature grid 3→2, phones shrink, footer 4→2 cols |
| `860px` | steps / split / personas → single column, `.split-shots { order: -1 }` |
| `768px` | `--gutter: 20px`, sections 96→68px, desktop nav → hamburger sheet, hero phones become a horizontal scroll-snap row |
| `400px` | tighter card padding, smaller trust row |

Print stylesheet hides header, closing CTA and footer.

---

## 7. Assets

| Asset | Spec |
|---|---|
| Screenshots | `/Users/robert/Git/nearEats/fastlane/screenshots/en-US/` (**raw**, no store title band). Resize to **640px wide WebP** → `images/screenshots/en-US/`. Never ship 1290×2796 PNGs. |
| Which ones | `01-MapClusters` (hero centre), `02-MainList` (hero left), `05-VenueDetail` (hero right), `06-Amenities` + `07-Warnings` (diet/accessibility split), `09-OpenLate` (right-now split), `04-Surprise` (delight moment) |
| App icon | → `images/icon.png` + favicons (`favicon.ico`, 16/32 png, `apple-touch-icon.png`) |
| OG image | `images/og-image.jpg`, 1200×630 — cream gradient, icon, headline with the warm gradient on the key phrase, four real badge chips, one phone bleeding off the bottom-right. Built from `tools/og-image.html`; **JPEG, not PNG8** — PNG8 dithers the cream gradient visibly. |
| App Store badge | self-hosted `images/app-store-badge.svg`; never hotlink Apple's CDN |
| Blog covers | `images/blog/<slug>.png`, 1200×630, generated on ComfyUI (`http://spark-72aa.tail7196c.ts.net:8188`); `tools/make-cover.py` renders a cream / amber→coral gradient card as the fallback |
| Loading | hero eager; everything below `loading="lazy" decoding="async"` with explicit `width`/`height` to hold layout |

**Head boilerplate** on every page (copy wrnty's): title, description, keywords,
`robots` with `max-image-preview:large`, dual `theme-color`
(`#FFB025` light / `#0F0D0B` dark), `apple-itunes-app` app-id **6754101006**,
canonical, full OG + Twitter card set, favicons, RSS `<link>`, Umami preconnect +
script, and `SoftwareApplication` JSON-LD with `offers` at `1.99 USD` and **no**
`aggregateRating`.

---

## 8. Definition of done

- [ ] Side by side with the icon and the App Store screenshots, the page reads
      as the same product — same warm gradient, same badge colours, same cream.
- [ ] No white text anywhere on `--gradient`; bands that carry white use
      `--brand-deep`.
- [ ] Every colour on the page traces to a token in §2; no stray hex values.
- [ ] Badge semantics match the app (green = open, orange = closing soon/award,
      red = warning, purple = merged).
- [ ] Renders correctly in light and dark, 320px → 1440px.
- [ ] Lighthouse ≥ 95 across the board; no CLS from images.
- [ ] Keyboard-only pass: skip link, nav, FAQ, every CTA reachable and visibly focused.
- [ ] `prefers-reduced-motion` on → nothing moves.
- [ ] Zero occurrences of "free" describing the app; zero invented ratings or quotes.
- [ ] An App Store badge visible from any scroll position within one viewport.
- [ ] All screenshots are real, current app captures — no mock-ups, no retouching.
- [ ] `seo-geo-aeo` skill run against the deployed URL with no critical findings.
