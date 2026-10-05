import re, sys, asyncio
from playwright.async_api import async_playwright

page_src = open('out/saf-home-2026-10.txt', encoding='utf-8').read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', page_src, re.S))
want = ['Hero Banner', 'Wait Times', 'FAQs', 'Booking Picker']
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<link href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&family=DM+Sans:wght@400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>body{margin:0;font-family:'DM Sans',sans-serif}</style></head><body>"
        + "".join(els[w] for w in want) + "</body></html>")
html = re.sub(r'\[saf_price service="connection"\]', '$55', html)
html = re.sub(r'\[saf_price[^\]]*\]', '$39', html)
open('/tmp/saf-preview.html', 'w', encoding='utf-8').write(html)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1440, 'height': 1000})
        await pg.goto('file:///tmp/saf-preview.html')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path='shot-hero.png', clip={'x':0,'y':0,'width':1440,'height':1000})
        await (await pg.query_selector('#wait-times')).screenshot(path='shot-wait.png')
        # mo picker tu nut trong bang wait-times de xem panel 3 dich vu
        btn = await pg.query_selector('#wait-times .sgn-pick-btn')
        if btn:
            await btn.click(); await pg.wait_for_timeout(600)
            await pg.screenshot(path='shot-picker.png')
        await b.close()
asyncio.run(main())
print("da chup")
