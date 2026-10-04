import re, sys, asyncio
from playwright.async_api import async_playwright

page_src = open('out/daf-home-2026-10.txt', encoding='utf-8').read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', page_src, re.S))
want = ['Hero Banner', 'Wait Times']
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<style>body{margin:0;font-family:'DM Sans',sans-serif}</style></head><body>"
        + "".join(els[w] for w in want) + "</body></html>")
# shortcode gia khong chay ngoai WordPress -> thay bang gia mau de xem bo cuc
html = re.sub(r'\[daf_price[^\]]*\]', '$39', html)
open('/tmp/preview.html', 'w', encoding='utf-8').write(html)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1440, 'height': 1000})
        await pg.goto('file:///tmp/preview.html')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path='shot-hero.png', clip={'x':0,'y':0,'width':1440,'height':1000})
        wt = await pg.query_selector('#wait-times')
        await wt.screenshot(path='shot-wait.png')
        await b.close()
asyncio.run(main())
print("da chup")
