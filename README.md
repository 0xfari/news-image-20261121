# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/0xfari/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/0xfari/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

THE WORLD TODAY — one image summing up Saturday 21 November 2026: a drawn night scene over Manama as Iran strikes Bahrain, the Guards claiming hits on two US bases while Bahrain reports an industrial fire, plus the day's other big stories — the Kryvyi Rih missile and the two that fell in Poland, the capture of "El Chapo Isidro" in Mexico, COP31 running past its deadline in Antalya, the AI sell-off wiping out the Nasdaq's 2026 gains, the dengue breakthrough out of Brazil, and two tankers hit near Hormuz.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## How the image is made

`render.py` draws the front page with Pillow — masthead and date, the drawn Manama night scene (skyline, missile arcs, interceptors, industrial fire), six story cards with small drawn thumbnails, and an "also today" brief strip — and writes `entry.png`. It uses only the DejaVu fonts bundled in `fonts/`, loaded by a path relative to the script. `main.ts` runs the renderer, validates the PNG (signature, IHDR 1024x1024, chunk CRCs, IEND), and copies it to the output directory; it clears the output directory's contents but never removes the directory itself.

---

<sub>Entered on [make.fun](https://make.fun/?ref=0xfari&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
