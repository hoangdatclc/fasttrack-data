# -*- coding: utf-8 -*-
"""Chup RIENG the hero SAF (tieu de + 3 hang Queue/Fast Track/From).

SAF GIU CAU TRUC HERO GOC nen KHONG co class .sgn-hero-row (do la class cua form
Save/From/24-7 o bon site kia). Ban truoc cua file nay query '.sgn-hero-row' -> luon
None -> AttributeError. Gio bat the qua chinh chu "Why Choose SGN Fast Track?".

Chay: python3 shot_card.py out/saf-home-2026-10.txt
"""
import re, sys, asyncio, pathlib
from playwright.async_api import async_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/saf-home-2026-10.txt"
src = open(PAGE, encoding="utf-8").read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', src, re.S))
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<style>body{margin:0}</style></head><body>" + els["Hero Banner"] + "</body></html>")
html = re.sub(r"\[saf_price[^\]]*\]", "$39", html)
TMP = pathlib.Path("/tmp/claude-0/sgn-card.html"); TMP.parent.mkdir(parents=True, exist_ok=True)
TMP.write_text(html, encoding="utf-8")

# Fonts DM Sans / Cormorant Garamond phai co SAN trong may (fonts.googleapis.com bi
# chan boi allowlist). Thieu -> Chromium am tham thay font khac va moi so do deu sai.
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 430, 390, 360, 320):
            # Khung nhin phai CAO: o nac hep the dai ra va hero can giua man hinh.
            pg = await b.new_page(viewport={"width": w, "height": 2400})
            await pg.goto(TMP.as_uri()); await pg.wait_for_timeout(600)
            el = await pg.query_selector("xpath=//div[contains(., 'Why Choose SGN Fast Track?')]"
                                         "[not(.//div[contains(., 'Why Choose SGN Fast Track?')])]")
            card = await (await el.evaluate_handle("e => e.parentElement")).as_element().bounding_box()
            await pg.evaluate("y => window.scrollTo(0, Math.max(0, y - 40))", card["y"])
            await pg.wait_for_timeout(200)
            card = await (await el.evaluate_handle("e => e.parentElement")).as_element().bounding_box()
            pad = 12
            await pg.screenshot(path=f"card-{w}.png", clip={
                "x": max(0, card["x"] - pad), "y": max(0, card["y"] - pad),
                "width": min(w, card["width"] + 2 * pad), "height": card["height"] + 2 * pad})
            print(f"card-{w}.png  cao {round(card['height'])}px  rong {round(card['width'])}px")
            await pg.close()
        await b.close()

asyncio.run(main())
