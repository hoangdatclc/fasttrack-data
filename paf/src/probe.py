# -*- coding: utf-8 -*-
"""DO can le hang CTA cua hero o 390 / 599 / 768px. Xem presentation.md §6.
PAF KHONG co media query `.paf-cta-row a` nen du kien khong dinh loi cua SAF/DAF --
script nay de XAC MINH dieu do bang so do, khong doan bang mat.
Chay: python3 probe.py out/paf-home-2026-10.txt
"""
import re, sys, asyncio, pathlib
from playwright.async_api import async_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/paf-home-2026-10.txt"
TMP = pathlib.Path("/tmp/paf-probe.html")
src = open(PAGE, encoding="utf-8").read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', src, re.S))
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700"
        "&family=DM+Sans:wght@400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>body{margin:0}</style></head><body>" + els["Hero Banner"] + "</body></html>")
html = re.sub(r"\[paf_price[^\]]*\]", "$39", html)
TMP.write_text(html, encoding="utf-8")

async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (390, 599, 768):
            pg = await b.new_page(viewport={"width": w, "height": 900})
            await pg.goto(TMP.as_uri()); await pg.wait_for_timeout(1500)
            rows = await pg.evaluate("""() => {
              const r = document.querySelector('.paf-cta-row');
              if (!r) return null;
              return [...r.children].map(el => ({tag: el.tagName,
                jc: getComputedStyle(el).justifyContent,
                w: Math.round(el.getBoundingClientRect().width),
                txt: el.textContent.trim().slice(0,22)}));
            }""")
            print(f"{w}px:", "khong co .paf-cta-row" if not rows else "")
            for r in rows or []:
                print(f"    {r}")
                if w <= 599 and r["w"] > 300 and r["jc"] != "center":
                    bad.append((w, r["tag"]))
            await pg.close()
        await b.close()
    print("FAIL:" if bad else "PASS:", bad or "khong co phan tu nao gian het be rong ma lech trai")

asyncio.run(main())
