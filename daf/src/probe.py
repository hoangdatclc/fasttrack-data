# -*- coding: utf-8 -*-
"""DO can le hang CTA cua hero o 390 / 599 / 768px -- khong doan bang mat.

Loi da dinh that: CSS responsive chi nham `.daf-cta-row a`, nhung nut vang la
<button>. Duoi 600px hang CTA thanh cot, ca hai gian het chieu ngang; <a> duoc
can giua con <button> roi ve flex-start -> chu lech trai. Desktop binh thuong
nen RAT de bo sot bang mat.

DAT khi ca BUTTON lan A deu ra justify-content=center o 390 va 599px.

Chay:  python3 probe.py out/daf-home-2026-10.txt
"""
import re, sys, asyncio, pathlib
from playwright.async_api import async_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/daf-home-2026-10.txt"
TMP = pathlib.Path("/tmp/daf-probe.html")

src = open(PAGE, encoding="utf-8").read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', src, re.S))
assert "Hero Banner" in els, f"{PAGE}: khong tim thay element Hero Banner"
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700"
        "&family=DM+Sans:wght@400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>body{margin:0}</style></head><body>" + els["Hero Banner"] + "</body></html>")
html = re.sub(r"\[daf_price[^\]]*\]", "$39", html)
TMP.write_text(html, encoding="utf-8")


async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (390, 599, 768):
            pg = await b.new_page(viewport={"width": w, "height": 900})
            await pg.goto(TMP.as_uri())
            await pg.wait_for_timeout(1500)
            rows = await pg.evaluate("""() => {
              const row = document.querySelector('.daf-cta-row');
              if (!row) return null;
              return [...row.children].map(el => ({
                tag: el.tagName, jc: getComputedStyle(el).justifyContent,
                w: Math.round(el.getBoundingClientRect().width),
                txt: el.textContent.trim().slice(0, 22)}));
            }""")
            assert rows, "khong tim thay .daf-cta-row"
            print(f"{w}px:")
            for r in rows:
                print(f"    {r}")
            if w <= 599 and any(r["jc"] != "center" for r in rows):
                bad.append(w)
            await pg.close()
        await b.close()
    if bad:
        sys.exit(f"FAIL: o {bad}px co phan tu KHONG duoc can giua -- xem presentation.md §6")
    print("PASS: 390 va 599px deu can giua")


asyncio.run(main())
