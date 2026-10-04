# -*- coding: utf-8 -*-
"""Va CSS tinh cua element Wait Times -- phan NGOAI vung dat:zone.

CHAY MOT LAN moi khi doi CSS tinh. update_zones.py khong dung toi khoi <style>,
nen sua render_blocks.py thoi se KHONG doi duoc mau cot Fast Track.
Hoc tu SAF (port_page.py muc 2c).
"""
import io, re, sys

SRC = "page-live-2026-10.txt"
DST = "page-in.txt"

s = io.open(SRC, encoding="utf-8").read()
before = len(s)

def sub(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit(f"[{why}] khop {n} lan, can dung 1: {old[:70]!r}")
    s = s.replace(old, new)

# 1. Mau so Fast Track trong bang -> dung mau xanh cua hero (#1a7a42).
sub("color: #1a5c2e !important;", "color: #1a7a42 !important;", "mau .daf-wt-ft")

# 2. Nut CTA cuoi muc Wait Times gio dung MOT MINH (da bo link WhatsApp o renderer)
#    -> noi ra cho can doi, giong SAF: 18px 46px / 0.86rem.
sub("padding: 15px 30px !important;", "padding: 18px 46px !important;", "padding nut")
old_fs = ("#wait-times .daf-wt-btn { display: inline-flex !important; align-items: center !important; "
          "gap: 8px !important; padding: 18px 46px !important; background: #C9A84C !important; "
          "background-image: none !important; color: #0B1F3A !important; "
          "font-family: 'DM Sans', sans-serif !important; font-size: 0.8rem !important;")
sub(old_fs, old_fs.replace("font-size: 0.8rem", "font-size: 0.86rem"), "font-size nut")

# 3b. (A) CSS responsive cua hero chi nham the <a>, nhung nut vang la <button>.
#     Do <600px hang CTA thanh cot -> ca hai gian het 342px; <a> duoc can giua,
#     <button> roi ve flex-start -> chu lech trai trong nen vang trai het man hinh.
#     Do duoc o 390 va 599px: button justify-content=normal, a=center. Giong het SAF.
old_css = ".daf-cta-row a {\n    justify-content: center !important;\n  }"
new_css = ".daf-cta-row a,\n  .daf-cta-row button {\n    justify-content: center !important;\n  }"
sub(old_css, new_css, "quy tac .daf-cta-row a")

# 3. Quy tac .daf-wt-link thanh code chet -> xoa, dung de lai rac.
s, n = re.subn(r"#wait-times \.daf-wt-link \{[^}]*\}\n?", "", s)
if n != 1:
    sys.exit(f"quy tac .daf-wt-link: xoa duoc {n} lan")

io.open(DST, "w", encoding="utf-8").write(s)
print(f"{before:,} -> {len(s):,} bytes  ->  {DST}")
