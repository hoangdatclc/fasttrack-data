# -*- coding: utf-8 -*-
"""KIEM CSS TINH -- phan NGOAI vung dat:zone.

Vi sao file nay ton tai: khoi <style> cua element Wait Times va media query cua Hero deu
nam NGOAI vung dat:zone. `update_zones.py` khong dung toi chung. Sua mau trong
render_blocks.py ma quen dong bo vao trang la LOI AM -- khong ai bao, trang cu the dang.

TRUOC 05/10/2026 file nay la bo VA mot lan (doi #1a5c2e -> #1a7a42...). Va xong roi thi
no luon bao loi vi khong con gi de va, trong khi runbook van bao chay va phai PASS --
tuc mot canh bao gia moi thang. Gio no lam viec nguoc lai: NO KIEM.

Chay:  python3 patch_static.py out/caf-home-YYYY-MM.txt
"""
import io, re, sys

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/caf-home-2026-10.txt"
s = io.open(PAGE, encoding="utf-8").read()
err = []

def need(pat, n, why):
    got = len(re.findall(pat, s))
    if got != n:
        err.append(f"{why}: khop {got} lan, can {n}  [{pat}]")

# LUAT 1 -- bang dung dung hai ma mau cua hero, khong phai ma cu cua ban dau tien.
need(r"#wait-times \.caf-wt-ft \{[^}]*color: #1a7a42 !important;", 1, "mau Fast Track trong bang")
need(r"#1a5c2e", 0, "ma xanh cu con sot")
need(r"#C1272D", 0, "ma do cu con sot")
if "#C9281C" not in s:
    err.append("khong thay ma do #C9281C (mau khung bac Busy, lay tu hero)")

# Tieu de the hero la phan TINH, phai nam NGOAI vung wait-hero. Lot vao trong thi thang
# sau update_zones.py xoa mat ma khong ai bao.
TITLE = "Why Choose CXR Fast Track?"
z = re.search(r"<!--dat:zone:wait-hero-->(.*?)<!--/dat:zone:wait-hero-->", s, re.S)
if not z:
    err.append("khong tim thay vung wait-hero")
elif TITLE in z.group(1):
    err.append(f"tieu de {TITLE!r} lot VAO TRONG vung wait-hero -- thang sau se bi xoa")
elif s.count(TITLE) != 1:
    err.append(f"tieu de {TITLE!r} xuat hien {s.count(TITLE)} lan, can 1")

# Dong phu hang SAVE phai noi CA HAI dau cua phep tru, moi dau mot dong --
# xem ghi chu trong render_hero. Hai chu "estimated" va "reach" khong duoc mat:
#   estimated -> day la uoc tinh, khong phai so do duoc
#   reach     -> dai nay la luc CAO DIEM, khong phai hang chuan ca ngay
need(r"Estimated peak standard queue: \d+(?:&ndash;\d+)?&nbsp;min\.<br>", 1,
     "dong 1 hang SAVE (hang thuong)")
need(r"With Fast Track: under&nbsp;\d+&nbsp;min\.", 1,
     "dong 2 hang SAVE (Fast Track)")
need(r"Estimated peak standard queue:", 1, "hai chu 'Estimated' va 'peak'")

# LUAT 8 -- ba cum chu da bo hang khoi the hero, cong chan de khong ai them lai.
# Truoc 05/10/2026 KHONG cong nao kiem ba cum nay nen chung troi im lang mot vong.
# Dung cum DAY DU "Through immigration with our service": grep "Through immigration"
# tran se bat nham review khach ("Through immigration in no time") o DAF/CAF/SAF.
need(r"touchdown", 0, "cum '- from touchdown to leaving immigration' da bo")
need(r"every flight, every hour", 0, "cum '- every flight, every hour' da bo")
need(r"Through immigration with our service", 0, "dong phu hang FAST TRACK cu da bo")

print("CSS TINH: PASS" if not err else "CSS TINH: FAIL")
for e in err:
    print(" -", e)
sys.exit(1 if err else 0)
