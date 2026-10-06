# -*- coding: utf-8 -*-
"""DO nguong ngat dong cua dong 1 (dong phu hang SAVE) tren the hero SAF.

Cach do: dung chinh DONG 1 lam phep do -- boc rieng chu truoc the <br> dau tien vao
mot <span> do tam, roi DEM SO DONG bang so hinh chu nhat client rect. 1 = vua mot dong.
Thu be dan be rong khung nhin de tim nguong chuyen 1 -> 2.

CANH BAO DA DO THUC TE: harness nay KHONG co CSS container cua Flatsome nen cot phai
RONG HON tren trang that khoang 15px. Nguong o day la can DUOI lac quan; tru 15px khi
suy ra hanh vi tren trang that.

Chay: python3 probe_wrap.py out/saf-home-2026-10.txt
"""
import re, sys, asyncio, pathlib
from playwright.async_api import async_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/saf-home-2026-10.txt"
TMP = pathlib.Path("/tmp/sgn-wrap.html")
src = open(PAGE, encoding="utf-8").read()
els = dict(re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', src, re.S))
html = ("<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link href='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700"
        "&family=DM+Sans:wght@400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>body{margin:0}</style></head><body>" + els["Hero Banner"] + "</body></html>")
html = re.sub(r"\[saf_price[^\]]*\]", "$39", html)
TMP.write_text(html, encoding="utf-8")

# Boc tung dong cua dong phu ra <span> rieng -> dem duoc so dong cua TUNG dong.
JS = """() => {
  const cap = [...document.querySelectorAll('.sgn-hero-row > span')]
      .find(s => s.textContent.trim().startsWith('Peak immigration'));
  if (!cap) return null;
  if (!cap.dataset.probed) {
    const parts = cap.innerHTML.split('<br>');
    cap.innerHTML = parts.map(p => '<span class="pl">' + p + '</span>').join('<br>');
    cap.dataset.probed = '1';
  }
  return [...cap.querySelectorAll('.pl')].map(s => ({
      lines: s.getClientRects().length,
      w: Math.round(s.getBoundingClientRect().width),
      txt: s.textContent.trim().slice(0, 34),
  })).concat([{col: Math.round(cap.getBoundingClientRect().width)}]);
}"""


async def measure(b, w):
    pg = await b.new_page(viewport={"width": w, "height": 1000})
    await pg.goto(TMP.as_uri()); await pg.wait_for_timeout(900)
    r = await pg.evaluate(JS)
    await pg.close()
    return r


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 430, 390, 375, 360, 345, 330, 320):
            r = await measure(b, w)
            if r is None:
                print(f"{w}px: KHONG TIM THAY dong phu"); continue
            col = r[-1]["col"]
            flag = "OK " if all(x["lines"] == 1 for x in r[:-1]) else "VO "
            print(f"{flag}{w}px  cot {col}px  " +
                  " | ".join(f'{x["lines"]}d "{x["txt"]}"' for x in r[:-1]))
        # tim nguong: be nhat con giu 1 dong cho CA BA dong
        lo, hi = 280, 500
        while lo < hi:
            mid = (lo + hi + 1) // 2
            r = await measure(b, mid)
            if r and all(x["lines"] == 1 for x in r[:-1]):
                hi = mid - 1
            else:
                lo = mid
        print(f"\nNGUONG (harness): vo dong o <= {lo}px, con mot dong tu {lo + 1}px")
        print("Tren trang that cong them ~15px -> uoc khoang", lo + 15, "px")
        await b.close()

asyncio.run(main())
