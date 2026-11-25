[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/rendsstwn/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/rendsstwn/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# News image — Wednesday 25 November 2026

One image summing up the world's news of Wednesday 25 November
2026, drawn as a newspaper front page: **THE WORLD TODAY**.

The lead story is the attack in the Strait of Hormuz — two oil
tankers struck naval mines and caught fire early on Wednesday —
with 29 more stories from the day across world affairs, markets,
technology, sport and culture: Ukraine's refinery strikes, the
Dow closing above 50,000, Asia's chip sell-off, Dell's record
quarter, Shenzhou-24 docking with Tiangong, and GTA VI's
record-breaking debut.

## Files

- `main.py` — the entry program (Python 3.13, standard library
  only). It copies the bundled `entry.png` to `/output/entry.png`
  and verifies the copy by SHA-256.
- `entry.png` — the 1024x1024 front page itself (162,733 bytes).
- `gen.py` — the build-time script that drew `entry.png` from the
  thirty verified stories, using Pillow and the DejaVu fonts.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program reads nothing but the bundled picture, touches no
network, and writes the same bytes on every run: three runs in a
row produce byte-identical `entry.png` files (SHA-256
`a4a6ea39455c39f85920e661dd0b28e5adfa48c6fa9a5996bffd73c8e673b13c`).

## Verification

Every story on the page was checked against reporting dated
Wednesday 25 November 2026 before it was drawn — the lead, the
Hormuz tanker attack, happened early that Wednesday morning, and
no story on the page comes from an earlier day. The picture names
its day twice: in the masthead date line and in the footer.

## License

MIT — see `LICENSE`.
