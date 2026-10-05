# -*- coding: utf-8 -*-
"""Chup Hero + Wait Times + Booking Picker o CA 1440px VA 390px.

Chup xong PHAI NHIN. Cong QC tung cho qua mot trang in chu `None` giua the vang
(ham cities() mat dong return) -- may khong bat duoc, mat bat duoc.

Chay: python3 shot.py out/haf-home-YYYY-MM.txt
"""
import re, sys, asyncio, pathlib
from playwright.async_api import async_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/haf-home-2026-10.txt"
src = open(PAGE, encoding="utf-8").read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', src, re.S))
want = ["Hero Banner", "Wait Times", "Booking Picker"]
missing = [w for w in want if w not in els]
if missing:
    sys.exit(f"thieu element: {missing}")
html = ("<!doctype html><html><head><meta charset=\'utf-8\'>"
        "<meta name=\'viewport\' content=\'width=device-width,initial-scale=1\'>"
        "<link href=\'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700"
        "&family=DM+Sans:wght@400;500;600;700&display=swap\' rel=\'stylesheet\'>"
        "<style>body{margin:0}</style></head><body>"
        + "".join(els[w] for w in want) + "</body></html>")
# shortcode gia khong chay ngoai WordPress -> thay bang gia mau de xem bo cuc
html = re.sub(r"\[haf_price[^\]]*\]", "$39", html)
TMP = pathlib.Path("/tmp/haf-shot.html")
TMP.write_text(html, encoding="utf-8")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, tag in ((1440, "d"), (390, "m")):
            pg = await b.new_page(viewport={"width": w, "height": 1000})
            await pg.goto(TMP.as_uri())
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f"shot-hero-{tag}.png",
                                clip={"x": 0, "y": 0, "width": w, "height": 1000})
            await (await pg.query_selector("#wait-times")).screenshot(path=f"shot-wait-{tag}.png")
            await pg.evaluate("document.querySelector(\'.haf-pick-btn\').click()")
            await pg.wait_for_timeout(700)
            await pg.screenshot(path=f"shot-pick-{tag}.png")
            await pg.close()
        await b.close()
    print("da chup: shot-{hero,wait,pick}-d.png (1440px) va -m.png (390px). GIO NHIN DI.")

asyncio.run(main())
