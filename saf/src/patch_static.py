# -*- coding: utf-8 -*-
"""KIEM CSS TINH -- phan NGOAI vung dat:zone.

Vi sao file nay ton tai: khoi <style> cua element Wait Times va media query cua Hero deu
nam NGOAI vung dat:zone. `update_zones.py` khong dung toi chung. Sua mau trong
render_blocks.py ma quen dong bo vao trang la LOI AM -- khong ai bao, trang cu the dang.

TRUOC 05/10/2026 file nay la bo VA mot lan (doi #1a5c2e -> #1a7a42...). Va xong roi thi
no luon bao loi vi khong con gi de va, trong khi runbook van bao chay va phai PASS --
tuc mot canh bao gia moi thang. Gio no lam viec nguoc lai: NO KIEM.

Chay:  python3 patch_static.py out/saf-home-YYYY-MM.txt
"""
import io, re, sys

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/saf-home-2026-10.txt"
s = io.open(PAGE, encoding="utf-8").read()
err = []

def need(pat, n, why):
    got = len(re.findall(pat, s))
    if got != n:
        err.append(f"{why}: khop {got} lan, can {n}  [{pat}]")

# LUAT 1 -- bang dung dung hai ma mau cua hero, khong phai ma cu cua ban dau tien.
need(r"#wait-times \.sgn-wt-ft \{[^}]*color: #1a7a42 !important;", 1, "mau Fast Track trong bang")
need(r"#1a5c2e", 0, "ma xanh cu con sot")
need(r"#C1272D", 0, "ma do cu con sot")
if "#C9281C" not in s:
    err.append("khong thay ma do #C9281C (mau khung bac Busy, lay tu hero)")

# ===================================================================================
# THE HERO CUA SAF — CAU TRUC RIENG, KHONG GIONG BON SITE KIA
# ===================================================================================
# Chu site chot 06/10/2026: SGN la site manh nhat ve SEO/AEO nen GIU cau truc goc
# (ba hang Queue / Fast Track / From), KHONG doi sang form Save / From / 24-7.
# Moi phep kiem duoi day la cua rieng SAF. DUNG chep tu patch_static cua site khac sang.

# 1. TIEU DE NAM TRONG VUNG — nguoc voi bon site kia.
#    O PQC/DAD/CXR/HAN tieu de la phan TINH ngoai vung, va cong ben do bat loi neu no
#    lot VAO trong. O SAF toan bo ruot the nam trong wait-hero, nen tieu de PHAI o TRONG.
#    Dao chieu phep kiem, khong xoa: de trong thi thang sau render_hero mat tieu de ma
#    khong ai bao.
TITLE = "Why Choose SGN Fast Track?"
z = re.search(r"<!--dat:zone:wait-hero-->(.*?)<!--/dat:zone:wait-hero-->", s, re.S)
if not z:
    err.append("khong tim thay vung wait-hero")
elif TITLE not in z.group(1):
    err.append(f"tieu de {TITLE!r} KHONG nam trong vung wait-hero -- o SAF no phai o TRONG")
elif s.count(TITLE) != 1:
    err.append(f"tieu de {TITLE!r} xuat hien {s.count(TITLE)} lan, can 1")
need(r"SGN Immigration &mdash; \w+ \d{4}", 0, "tieu de cu mang ten thang da bo (06/10/2026)")

# 2. BA HANG, dung thu tu Queue -> Fast Track -> From.
need(r">Queue</span>", 1, "hang QUEUE")
need(r">Fast Track</span>", 1, "hang FAST TRACK")
need(r">From</span>", 1, "hang FROM")
need(r">Save</span>", 0, "hang SAVE la cua form bon site kia, SAF khong dung")

# 3. DONG PHU HANG QUEUE gop ca cau `basis` lan ngay (chot 06/10/2026).
#    Truoc do ba cho noi ve do tin cay nam tan mat: mot doan `basis` rieng o dau the,
#    dong phu "Last passengers off a flight...", va "Updated {ngay} - Hour by hour" o day.
#    Gio gop lam MOT, dat ngay duoi con so ma no mo ta.
need(r"Estimated peak standard immigration queue &middot; Updated ", 1,
     "dong phu hang QUEUE (gop basis + ngay)")
need(r"Estimated from the .* arrival schedule", 0, "doan basis rieng o dau the da bo")
need(r"Last passengers off a flight landing in the busiest hours", 0,
     "dong phu cu cua hang QUEUE da bo")
need(r"Hour by hour", 0, "dong 'Updated ... Hour by hour' o day the da bo")

# 4. HANG FAST TRACK giu dang nhan "Under 20 min" — SAF la cho DUY NHAT con dung dang nay.
need(r">Under 20 min<", 1, "gia tri hang FAST TRACK")
# LUAT 8 cam cum "Through immigration with our service" o BON site kia, noi no la dong phu
# cua mot hang da bi bo. O SAF hang FAST TRACK VAN CON nen cum nay VAN DUNG CHO.
# Chu site chot 06/10/2026: giu. Dao chieu phep kiem tu `=0` thanh `=1`.
need(r"Through immigration with our service", 1, "dong phu hang FAST TRACK (SAF giu, luat 8 khong ap)")

# 5. Cac thu cua form bon site kia KHONG duoc xuat hien o SAF.
need(r"Peak immigration queue: ", 0, "dong phu form Save/From/24-7 — SAF khong dung")
need(r"class=\"sgn-hero-row\"", 0, "class cua form bon site kia — SAF khong dung")
need(r"grid-template-columns: 40px 1fr !important", 0,
     "CSS thu cot cua form bon site kia — SAF giu bo cuc goc")

# LUAT 8 — hai cum con lai VAN cam o SAF (chung thuoc hang QUEUE cu, da bo that).
need(r"touchdown", 0, "cum '- from touchdown to leaving immigration' da bo")
need(r"every flight, every hour", 0, "cum '- every flight, every hour' da bo")
# LUAT 3 — chuoi chu site cam, o MOI site.
need(r"you may not need us", 0, "chuoi bi cam (luat 3)")

print("CSS TINH: PASS" if not err else "CSS TINH: FAIL")
for e in err:
    print(" -", e)
sys.exit(1 if err else 0)
