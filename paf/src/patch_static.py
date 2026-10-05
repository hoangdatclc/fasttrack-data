# -*- coding: utf-8 -*-
"""Va CSS tinh cua element Wait Times + hero -- phan NGOAI vung dat:zone.

Chay khi CSS doi. update_zones.py khong dung toi khoi <style>, nen sua
render_blocks.py thoi se KHONG doi duoc mau cot Fast Track.

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

# 1. Mau so Fast Track trong bang -> mau xanh cua hero.
sub("color: #1a5c2e !important;", "color: #1a7a42 !important;", "mau .paf-wt-ft")

# 2. Nut CTA cuoi muc Wait Times gio dung MOT MINH -> noi ra cho can doi.
sub("padding: 15px 30px !important;", "padding: 18px 46px !important;", "padding nut")
old_fs = ("#wait-times .paf-wt-btn { display: inline-flex !important; align-items: center !important; "
          "gap: 8px !important; padding: 18px 46px !important; background: #C9A84C !important; "
          "background-image: none !important; color: #0B1F3A !important; "
          "font-family: 'DM Sans', sans-serif !important; font-size: 0.8rem !important;")
sub(old_fs, old_fs.replace("font-size: 0.8rem", "font-size: 0.86rem"), "font-size nut")

# 3. Quy tac .paf-wt-link thanh code chet -> xoa.
s, n = re.subn(r"#wait-times \.paf-wt-link \{[^}]*\}\n?", "", s)
if n != 1:
    sys.exit(f"quy tac .paf-wt-link: xoa duoc {n} lan")

# 4. CSS responsive cua hero chi nham the <a>, nhung nut vang la <button>.
#    Duoi 600px hang CTA thanh cot -> ca hai gian het be rong; <a> duoc can giua,
#    <button> roi ve flex-start -> chu lech trai. Giong het SAF/DAF.
sub(".paf-cta-row a {\n    justify-content: center !important;\n  }",
    ".paf-cta-row a,\n  .paf-cta-row button {\n    justify-content: center !important;\n  }",
    "quy tac .paf-cta-row a")

# 5. Fast Track doi tu "10 phut phang" sang HAI BAC (chot 05/10/2026) -> NAM cau cam ket
#    o phan TINH phai dong bo, neu khong trang se tu choi nhau: bang ghi 10-15 o cao diem
#    con van xuoi van hua ~10 moi khung. O DAF da phai sua 10 cho vi dung ly do nay.
#    KHONG dung toi "confirm within 10 minutes" (4 lan) -- do la thoi gian XAC NHAN DAT CHO,
#    khac han thoi gian qua cua khau.
for old, new in [
    ("Fast Track takes you through in about 10 minutes.",
     "Fast Track takes you through in about 10 minutes, and under 15 even at the busiest hours."),
    ("keeps you to about 10 minutes, whatever the crowd",
     "keeps you under 15 minutes, whatever the crowd"),
    ("Fast Track takes you through the priority lane in about 10 minutes.",
     "Fast Track takes you through the priority lane in about 10 minutes, under 15 at peak."),
    ("and gets you out in about 10 minutes.",
     "and gets you out in about 10 minutes, under 15 at peak."),
    ("you are through in about 10 minutes and on your way to",
     "you are through in about 10 minutes \u2014 under 15 even at peak \u2014 and on your way to"),
    # Hai cau duoi day noi thang ve luc CAO DIEM ("while the queue is still building",
    # "even when the charters land together") nen de lai ~10 phang la mau thuan nang nhat.
    ("Priority lane, paperwork handled, out in about 10 minutes \u2014 on your way to the resort",
     "Priority lane, paperwork handled, out in about 10 minutes \u2014 under 15 at peak \u2014 on your way to the resort"),
    ("through in about 10 minutes with a dedicated assistant, even when the charters land together.",
     "through in about 10 minutes with a dedicated assistant \u2014 under 15 even when the charters land together."),
]:
    sub(old, new, "cam ket Fast Track")

# KHONG dung toi loi khach trong review: mot danh gia co cau "in under 15 minutes".
# Do la lam khach noi, khong phai cam ket dich vu.

io.open(DST, "w", encoding="utf-8").write(s)
print(f"{before:,} -> {len(s):,} ky tu  ->  {DST}")
