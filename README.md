# Friday 20 November 2026 — The Day in World News

[![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261120)
[![Built with Muse](https://img.shields.io/badge/built%20with-Muse-7c3aed)](https://muse.ai)

One page, 45 stories, 7 regions: the whole of Friday 20 November 2026 in
world news, as a newspaper front page.

## The day in brief

- **Europe** — Russian ballistic missiles smash three Dnipro bridges in
  Kyiv, 3 killed, hours after the Shenzhen "peace declaration".
- **Asia** — Cyclone Akvan makes landfall near Gopalpur, Odisha, with
  gusts to 90 km/h, the third cyclone to hit India in a month.
- **World** — COP31 enters its final day in Antalya with no deal in sight:
  21 issues unresolved, fossil-fuel language dropped from the draft.

## What is on the page

- Masthead with the date and the story/region count.
- **The Day in Numbers**: 3 Kyiv bridges hit · 10,091 Ebola cases in
  DR Congo · 4.8% Nikkei plunge · $48.3bn US–Iran war cost · 21 COP31
  issues unresolved · 90 km/h Akvan gusts.
- Three headline cards with original illustrations.
- A world map with 11 numbered pins for the stories' locations.
- **Also on Friday 20 November**: stories 4–45 in region order.
- **Date Check**: eight stories that look like 20 November news but
  happened on other dates (ICJ Rohingya ruling, Shenzhen summit,
  Anthropic IPO, the PIF Tower strike, GTA 6 launch-day sales, the
  Iran war-powers vote, VP Gibran's resignation, Kenya's last Ebola
  patient) — deliberately left out.
- Sources footer: Reuters, CNN, Le Monde, Toronto Star, UN News,
  Phys.org, The Hindu, Daily Baku, AppiSToS, RNZ Pacific, Dubai Standard.

## How to run

```bash
python3 main.py
```

This renders `entry.png` (1024 × 1024). It needs Python 3 and Pillow
(`pip install pillow`). Headline pictures are read from `illustrations/`
and the map from `map.jpg` when present; if any asset file is missing,
a programmatic drawing is used instead, so the program still exits 0.

## Files

- `main.py` — the renderer (Pillow only, no network).
- `illustrations/` — original headline drawings (Kyiv, Akvan, COP31).
- `map.jpg` — the world map used behind the pins.
- `entry.png` — the rendered front page.

## Bounty

Built for the make.fun bounty
[news-image-20261120](https://make.fun/bounty/news-image-20261120)
— "Sum up 20 November's world news in one image".
