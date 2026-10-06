# -*- coding: utf-8 -*-
"""Chup RIENG the hero (3 hang chi so) o 1440 / 375 / 360 / 320px.

Dung de nhin dong phu hang SAVE -- ba dong, moi dong phai vua mot dong. Hai nac
media query (<=420px va <=345px) chi thay duoc o 375/360 va 320.
Chay: python3 shot_card.py out/caf-home-2026-10.txt
"""
import re, sys, asyncio, pathlib
from playwright.async_api import async_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/caf-home-2026-10.txt"
src = open(PAGE, encoding="utf-8").read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', src, re.S))
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700"
        "&family=DM+Sans:wght@400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>body{margin:0}</style></head><body>" + els["Hero Banner"] + "</body></html>")
html = re.sub(r"\[caf_price[^\]]*\]", "$39", html)
TMP = pathlib.Path("/tmp/caf-card.html")
TMP.write_text(html, encoding="utf-8")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 375, 360, 320):
            # Khung nhin phai CAO: o 320px hai nac media query gop the thanh mot cot nen
            # the dai ra, va hero can giua man hinh -> the tut xuong duoi day khung nhin.
            # 1200px tung lam ca lenh chet voi "Clipped area ... outside the resulting
            # image" dung o nac 320. Cao 2200 + scroll_into_view cho moi be rong.
            pg = await b.new_page(viewport={"width": w, "height": 2200})
            await pg.goto(TMP.as_uri()); await pg.wait_for_timeout(2200)
            el = await pg.query_selector(".caf-hero-row")
            await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(250)
            box = await (await el.evaluate_handle("e => e.parentElement")).as_element().bounding_box()
            pad = 10
            await pg.screenshot(path=f"card-{w}.png", clip={
                "x": max(0, box["x"] - pad), "y": max(0, box["y"] - pad),
                "width": min(w, box["width"] + 2 * pad), "height": box["height"] + 2 * pad})
            print(f"card-{w}.png  cao {round(box['height'])}px  rong {round(box['width'])}px")
            await pg.close()
        await b.close()

asyncio.run(main())
