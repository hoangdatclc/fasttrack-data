# -*- coding: utf-8 -*-
"""Do dong phu hang QUEUE cua the hero SAF: xuong may dong, be o dau.

Vi sao can: dong nay dai (mo ta + ngay). Chu site hoi co nen ep ngay luon nam cung
mot dong khong. Cau tra loi phu thuoc be rong THAT cua cot, khong doan duoc.
Cum ngay da boc white-space:nowrap -> phai xac nhan no khong bao gio bi be giua.

Chay: python3 probe_sub.py out/saf-home-2026-10.txt
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
TMP = pathlib.Path("/tmp/claude-0/sgn-sub.html"); TMP.parent.mkdir(parents=True, exist_ok=True)
TMP.write_text(html, encoding="utf-8")

JS = r"""() => {
  const out = [];
  const want = ['Estimated standard immigration queue at peak',
                'Priority lane, escorted by our staff',
                'Per person'];
  for (const sp of document.querySelectorAll('span')) {
    const t = sp.textContent.trim();
    if (!want.some(w => t.startsWith(w))) continue;
    if (sp.querySelector('span') === null && t.startsWith('·')) continue;
    const rects = [...sp.getClientRects()];
    // tach chu theo tung dong: dung Range tren moi tu
    const words = [];
    const walk = document.createTreeWalker(sp, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walk.nextNode())) {
      let i = 0;
      for (const m of n.textContent.matchAll(/\S+/g)) {
        const r = document.createRange();
        r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        words.push([m[0], Math.round(r.getBoundingClientRect().top)]);
      }
    }
    const lines = [];
    for (const [w, top] of words) {
      if (!lines.length || lines[lines.length-1][0] !== top) lines.push([top, [w]]);
      else lines[lines.length-1][1].push(w);
    }
    out.push({text: t.slice(0,46), boxes: rects.length,
              w: Math.round(sp.getBoundingClientRect().width),
              lines: lines.map(l => l[1].join(' '))});
  }
  return out;
}"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 1180, 992, 768, 430, 390, 360, 320):
            pg = await b.new_page(viewport={"width": w, "height": 2400})
            await pg.goto(TMP.as_uri()); await pg.wait_for_timeout(500)
            res = await pg.evaluate(JS)
            print(f"\n=== viewport {w}px ===")
            for r in res:
                print(f"  cot rong {r['w']}px · {len(r['lines'])} dong")
                for i, l in enumerate(r["lines"], 1):
                    print(f"     {i}| {l}")
            await pg.close()
        await b.close()

asyncio.run(main())
