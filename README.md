[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/rendsstwn/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/rendsstwn/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# The World Today — 25 November 2026

One image summing up the world's news of Wednesday 25 November
2026, drawn as a newspaper front page: **THE WORLD TODAY**.

The lead story is the day's biggest official economic move —
the USTR's proposal of tariffs of up to 35% on fourteen
economies at once, with named rates per economy. The Strait of
Hormuz tanker fires stay on the page, but as a CLAIM: Reuters
reported them on 25 November with no independent verification,
and a claim must not lead. Fifty stories in all — three large
leads, twelve grid cards and thirty-five more in the ALSO ON
list — across ten regions and twenty fields, with a BY THE
NUMBERS strip, a world map with numbered dots, and a DATE CHECK
footer that names what was left out as earlier news.

## Files

- `main.py` — the entry program (Python 3.13, standard library
  only). It copies the bundled `entry.png` to `/output/entry.png`
  and verifies the copy by SHA-256.
- `entry.png` — the 1024x1024 front page itself (217,552 bytes,
  SHA-256 `acf773c8f977e279a741f854eacea5206949021a9ae62db00a4ea738f60a6161`).
- `gen.py` — the build-time script that drew `entry.png` from the
  fifty verified stories, using Pillow and the DejaVu fonts.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program reads nothing but the bundled picture, touches no
network, and writes the same bytes on every run: three runs in a
row produce byte-identical `entry.png` files (SHA-256
`acf773c8f977e279a741f854eacea5206949021a9ae62db00a4ea738f60a6161`).

## Verification

Every story on the page was checked against reporting dated
Wednesday 25 November 2026 before it was drawn. The page names
its day three times — the masthead date, the stat strip and the
DATE CHECK footer — and the footer lists the previous-day items
it deliberately left out: the Huawei verdict (Tue 24), Nvidia's
record surge (Mon 23), and US Thanksgiving (Thu 26). Each story
carries a status tag: OFFICIAL for an authority's own figure or
act, REPORTED for a press report, CLAIM for one side's account.

## License

MIT — see `LICENSE`.
