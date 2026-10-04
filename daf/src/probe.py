import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (390, 599, 768):
            pg = await b.new_page(viewport={'width': w, 'height': 900})
            await pg.goto('file:///tmp/daf-v2.html'); await pg.wait_for_timeout(1500)
            r = await pg.evaluate("""() => {
              const row = document.querySelector('.daf-cta-row');
              if (!row) return 'no row';
              return [...row.children].map(el => {
                const cs = getComputedStyle(el);
                const b = el.getBoundingClientRect();
                return {tag: el.tagName, jc: cs.justifyContent,
                        w: Math.round(b.width), left: Math.round(b.left),
                        txt: el.textContent.trim().slice(0,22)};
              });
            }""")
            print(w, 'px:')
            for x in r if isinstance(r, list) else [r]: print('   ', x)
            await pg.close()
        await b.close()
asyncio.run(main())
