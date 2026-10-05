# -*- coding: utf-8 -*-
"""KIEM CSS TINH -- phan NGOAI vung dat:zone.

Vi sao file nay ton tai: khoi <style> cua element Wait Times va media query cua Hero
deu nam NGOAI vung dat:zone. `update_zones.py` khong dung toi chung. Sua mau trong
render_blocks.py ma quen dong bo vao trang la LOI AM -- khong ai bao, trang cu the dang.

O HAF khong phai VA gi ca: element Wait Times duoc port tu ban SAF da chuan (mau
#1a7a42 / #C9281C, nut 18px 46px / 0,86rem, da go quy tac chet .haf-wt-link), con
media query `.haf-cta-row a, button` da duoc port_page.py sua mot lan. Nen file nay
lam viec nguoc lai: NO KIEM, va bao dong neu thang nao do co nguoi sua lech di.

Chay:  python3 patch_static.py out/haf-home-2026-10.txt
"""
import io, re, sys

PAGE = sys.argv[1] if len(sys.argv) > 1 else "out/haf-home-2026-10.txt"
s = io.open(PAGE, encoding="utf-8").read()
err = []

def need(pat, n, why):
    got = len(re.findall(pat, s))
    if got != n:
        err.append(f"{why}: khop {got} lan, can {n}  [{pat}]")

# LUAT 1 -- bang dung dung hai ma mau cua hero, khong phai ma cu cua ban dau tien.
need(r"#wait-times \.haf-wt-ft \{[^}]*color: #1a7a42 !important;", 1, "mau Fast Track trong bang")
need(r"#1a5c2e", 0, "ma xanh cu con sot")
need(r"#C1272D", 0, "ma do cu con sot")
# So lan #C9281C thay doi theo so khung Busy cua thang (CSS tinh + moi dong Busy mot lan),
# nen chi kiem CO MAT, khong kiem so lan.
if "#C9281C" not in s:
    err.append("khong thay ma do #C9281C (mau khung bac Busy, lay tu hero)")

# Nut CTA cuoi muc Wait Times dung mot minh -> kich thuoc da noi ra cho can doi.
need(r"#wait-times \.haf-wt-btn \{[^}]*padding: 18px 46px !important;", 1, "padding nut Wait Times")
need(r"#wait-times \.haf-wt-btn \{[^}]*font-size: 0\.86rem !important;", 1, "font-size nut Wait Times")
need(r"#wait-times \.haf-wt-link", 0, "quy tac chet .haf-wt-link")

# LUAT 7 -- media query <= 600px phai phu CA <button>, khong chi <a>.
# Thieu dong nay thi nut vang cua hero lech trai tren dien thoai. Do bang probe.py.
need(r"\.haf-cta-row a,\s*\n\s*\.haf-cta-row button \{", 1, "media query .haf-cta-row a, button")

# Tieu de the hero "Why Choose HAN Fast Track?" la phan TINH, phai nam NGOAI vung
# wait-hero. Neu no lot vao trong vung thi thang sau update_zones.py se xoa mat.
z = re.search(r"<!--dat:zone:wait-hero-->(.*?)<!--/dat:zone:wait-hero-->", s, re.S)
if not z:
    err.append("khong tim thay vung wait-hero")
elif "Why Choose HAN Fast Track?" in z.group(1):
    err.append("tieu de 'Why Choose HAN Fast Track?' lot VAO TRONG vung wait-hero -- "
               "thang sau update_zones.py se xoa mat no")
elif s.count("Why Choose HAN Fast Track?") != 1:
    err.append(f"'Why Choose HAN Fast Track?' xuat hien {s.count('Why Choose HAN Fast Track?')} lan, can 1")

# Dong phu hang SAVE phai noi CA HAI dau cua phep tru -- xem ghi chu trong render_hero.
# run_qc.py cung kiem, nhung runbook co buoc chay rieng patch_static.py nen de o ca hai.
need(r"The standard immigration queue is estimated to reach&nbsp;\d+(?:&ndash;\d+)?&nbsp;minutes\.<br>", 1,
     "dong 1 hang SAVE (hang thuong)")
need(r"Fast Track gets you through in under&nbsp;\d+&nbsp;minutes\.", 1,
     "dong 2 hang SAVE (Fast Track)")
need(r"queue is estimated to reach&nbsp;", 1, "hai chu 'estimated' va 'reach'")

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
