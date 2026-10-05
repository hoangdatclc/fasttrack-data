# -*- coding: utf-8 -*-
"""Va CSS tinh cua element Wait Times -- phan NGOAI vung dat:zone.

Chay khi CSS doi. update_zones.py khong dung toi khoi <style>, nen sua
render_blocks.py thoi se KHONG doi duoc mau cot Fast Track. Hoc tu DAF/SAF.

Chay:  python3 patch_static.py <trang-goc> page-in.txt
"""
import io, re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "page-live.txt"
DST = sys.argv[2] if len(sys.argv) > 2 else "page-in.txt"

s = io.open(SRC, encoding="utf-8").read()
before = len(s)

def sub(old, new, why):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit(f"[{why}] khop {n} lan, can dung 1: {old[:70]!r}")
    s = s.replace(old, new)

# 1. Mau so Fast Track trong bang -> dung mau xanh cua hero (#1a7a42).
sub("color: #1a5c2e !important;", "color: #1a7a42 !important;", "mau .caf-wt-ft")

# 2. Nut CTA cuoi muc Wait Times gio dung MOT MINH (da bo link WhatsApp o renderer)
#    -> noi ra cho can doi, giong SAF/DAF: 18px 46px / 0.86rem.
sub("padding: 15px 30px !important;", "padding: 18px 46px !important;", "padding nut")
old_fs = ("#wait-times .caf-wt-btn { display: inline-flex !important; align-items: center !important; "
          "gap: 8px !important; padding: 18px 46px !important; background: #C9A84C !important; "
          "background-image: none !important; color: #0B1F3A !important; "
          "font-family: 'DM Sans', sans-serif !important; font-size: 0.8rem !important;")
sub(old_fs, old_fs.replace("font-size: 0.8rem", "font-size: 0.86rem"), "font-size nut")

# 3. Quy tac .caf-wt-link thanh code chet -> xoa, dung de lai rac.
s, n = re.subn(r"#wait-times \.caf-wt-link \{[^}]*\}\n?", "", s)
if n != 1:
    sys.exit(f"quy tac .caf-wt-link: xoa duoc {n} lan")

# CAF KHONG co media query `.caf-cta-row a` nen khong dinh loi nut mobile
# cua SAF/DAF -- da kiem 05/10/2026, khong can va.

io.open(DST, "w", encoding="utf-8").write(s)
print(f"{before:,} -> {len(s):,} ky tu  ->  {DST}")
