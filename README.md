# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/0xfari/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/0xfari/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

THE WORLD TODAY — one image summing up Saturday 21 November 2026: a drawn night scene over Kyiv as about 100 missiles arc down in the overnight barrage, one landing in Poland, plus the day's other big stories — the EU's response, COP31 running into overtime in Antalya, Cyclone Akvan's aftermath, and two firsts in sport.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## How the image is made

`render.py` draws the front page with Pillow — masthead and date, the drawn Kyiv night scene, six story cards with small drawn thumbnails, and an "also today" brief strip — and writes `entry.png`. It uses only the DejaVu fonts bundled in `fonts/`, loaded by relative path. `main.ts` validates the PNG (signature, IHDR 1024×1024, chunk CRCs, IEND) and copies it to the output directory.

---

<sub>Entered on [make.fun](https://make.fun/?ref=0xfari&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
