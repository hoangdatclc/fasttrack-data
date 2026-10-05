# -*- coding: utf-8 -*-
"""Nang trang SAF tu 11 len 13 element: them Wait Times + Booking Picker, khoanh 3 vung.

CHAY MOT LAN. Sau lan nay quy trinh hang thang chi dung update_zones.py.

BA cho de sai, da chan san:
  1. caf_price -> saf_price dung GACH DUOI, sed 's/caf-/sgn-/' KHONG bat duoc.
     O CAF tung de lot va shortcode in nguyen van ra trang. O day thay tuong minh.
  2. Nut hero phai KHONG co !important (hoc tu DAF): nut co !important va nut khong
     nam canh nhau se phan ung khac nhau voi CSS cua theme -> mot cai to be ra.
  3. SAF co BA dich vu (CAF/DAF chi hai). Panel picker phai co dong Connection,
     va no KHONG mua bang add-to-cart ma dan sang trang dich vu rieng.
"""
import re, sys

SRC = "/home/claude/saf/page-orig.txt"
CAF = "/home/claude/caf/run-2026-10/out/caf-home-2026-10.txt"
DST = "page-in.txt"

SITE = "https://hochiminhairportfasttrack.com"
WA = "https://wa.me/84368938081"


def blocks(s):
    return re.findall(r'(\[ux_html label="([^"]+)"\]\n)(.*?)(\n\[/ux_html\])', s, re.S)


def caf_to_saf(h):
    """Doi tien to. THU TU QUAN TRONG: cai co gach duoi phai di truoc."""
    pairs = [
        ('caf_price', 'saf_price'),            # (1) gach duoi -- phai truoc 'caf-'
        ('cafFaqToggle', 'sgnFaqToggle'),
        ('cafCarouselMove', 'sgnCarouselMove'),
        ('caf-', 'sgn-'),
        ('#caf', '#sgn'), ('"caf', '"sgn'), ("'caf", "'sgn"),
        ('https://nhatrangairportfasttrack.com', SITE),
        ('Cam Ranh International Airport (CXR)', 'Tan Son Nhat International Airport (SGN)'),
        ('Cam Ranh International Airport', 'Tan Son Nhat International Airport'),
        ('Cam Ranh Airport', 'Tan Son Nhat Airport'),
        ('Cam Ranh', 'Tan Son Nhat'),
        ('CXR', 'SGN'),
        ('Nha Trang', 'Ho Chi Minh City'),
        ('CAF HOMEPAGE', 'SAF HOMEPAGE'),
    ]
    for a, b in pairs:
        h = h.replace(a, b)
    return h


def audit(h, where):
    bad = re.findall(r'caf[-_A-Za-z]*|CXR|Cam Ranh|nhatrangairportfasttrack', h)
    if bad:
        sys.exit(f"[{where}] con sot tien to CAF: {sorted(set(bad))}")


# ---------------------------------------------------------------- 1. nguon
page = open(SRC, encoding="utf-8").read()
caf = open(CAF, encoding="utf-8").read()
cafb = {n: b for _, n, b, _ in blocks(caf)}

# ---------------------------------------------------------------- 2. Wait Times
wait = caf_to_saf(cafb["Wait Times"])
wait = wait.replace('aria-labelledby="sgn-h2-wait"', 'aria-labelledby="sgn-h2-wait"')
audit(wait, "Wait Times")

# 2b. Nut CTA cuoi muc Wait Times gio dung MOT MINH (da bo link WhatsApp o renderer).
#     Mot minh giua hang rong thi nut 15x30 trong lac long -> noi ra cho can doi.
#     Quy tac .sgn-wt-link thanh code chet -> xoa luon, dung de lai rac.
old_btn = "padding: 15px 30px !important;"
assert wait.count(old_btn) == 1, "khong khop padding nut Wait Times"
wait = wait.replace(old_btn, "padding: 18px 46px !important;")
old_fs = ("#wait-times .sgn-wt-btn { display: inline-flex !important; align-items: center !important; "
          "gap: 8px !important; padding: 18px 46px !important; background: #C9A84C !important; "
          "background-image: none !important; color: #0B1F3A !important; "
          "font-family: 'DM Sans', sans-serif !important; font-size: 0.8rem !important;")
assert wait.count(old_fs) == 1, "khong khop font-size nut Wait Times"
wait = wait.replace(old_fs, old_fs.replace("font-size: 0.8rem", "font-size: 0.86rem"))
import re as _re
wait, n = _re.subn(r"#wait-times \.sgn-wt-link \{[^}]*\}\n?", "", wait)
assert n == 1, f"quy tac .sgn-wt-link: xoa duoc {n} lan"

# 2c. Mau so Fast Track trong bang: #1a5c2e -> #1a7a42, dung dung mau xanh cua hero.
#     Hero da dung #1a7a42 9 lan; bang dung mot ma khac khien hai cho "xanh khac nhau".
old_ft = "color: #1a5c2e !important;"
assert wait.count(old_ft) == 1, f"mau .sgn-wt-ft: khop {wait.count(old_ft)} lan"
wait = wait.replace(old_ft, "color: #1a7a42 !important;")


# ---------------------------------------------------------------- 3. Booking Picker
pick = caf_to_saf(cafb["Booking Picker"])
audit(pick, "Booking Picker")

# PICKER CHI CO HAI THE. Connection KHONG nam trong picker, ke ca duoi dang dong chan.
#
# Quyet dinh cua chu site 04/10/2026, sau khi thu ca hai ban (the thu ba, roi dong chan).
# Ly do, de lan sau khong ai "bo sung cho du ba dich vu":
#
#   1. Chinh trang da tach no ra. Muc Services mo dau bang "BOTH services include..."
#      roi dat Connection trong mot dai rieng nhan "A different journey -- that is a
#      SEPARATE service". Bay no vao picker la choi voi kien truc cua chinh trang.
#
#   2. Connection CHUA Arrival. "What's included" cua no mo dau bang "Agent meets you
#      in the T2 arrival hall / Escorted through the priority immigration lane" --
#      dung la Fast Track Arrival. $30 chenh lech mua them phan chi terminal + check-in
#      chang hai. Trong mot dropdown khong co bang tinh nang, khach noi chuyen doc
#      "$45 priority immigration lane" roi mua cai re hon la ket qua TU NHIEN.
#      Picker ve ban chat khong cho noi thong tin de chon dung giua hai cai nay.
#
#   3. Connection van con SAU loi vao khac tren trang: Nav bar x2 (desktop + mobile),
#      Hero (dong rieng ngay duoi hai nut), Services (ca mot dai), FAQs, Footer.
#      Picker khong phai be mat kham pha cua no.
#
# => Picker giu dung MOT cau hoi nhi phan: dang den hay dang di. Chevron ">" chi con
#    mot nghia duy nhat (bam la mua). Khong co ngoai le nao de bao tri.
#
# Chot chan: run_qc ghim so lan xuat hien URL trang Connection = 6. Ai them lai vao
# picker thi thanh 7 va QC FAIL ngay.

pick = pick.replace("Priority immigration lane &middot; SGN", "Priority immigration lane &middot; T2")

# ---------------------------------------------------------------- 4. Hero Banner
hero = next(b for _, n, b, _ in blocks(page) if n == "Hero Banner")
orig_hero = hero

# 4a. vung wait-hero: tu the dau card den truoc "Service mini tiles"
a = hero.index('<!-- Card header -->')
z = hero.index('<!-- Service mini tiles -->')
hero = hero[:a] + "<!--dat:zone:wait-hero-->\n<!--/dat:zone:wait-hero-->\n\n      " + hero[z:]

# 4b. nut vang CTA -> nut picker. KHONG dung !important (xem docstring, diem 2).
old_cta = hero[hero.index('<a href="#book-now" style="'):]
old_cta = old_cta[:old_cta.index('</a>') + 4]
new_cta = '''<button type="button" class="sgn-pick-btn" aria-haspopup="true" aria-expanded="false" style="
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 15px 32px;
          margin: 0;
          background: #C9A84C;
          color: #0B1F3A;
          font-family: 'DM Sans', sans-serif;
          font-size: 0.82rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          text-decoration: none;
          border-radius: 3px;
          border: 2px solid #C9A84C;
          box-sizing: border-box;
          line-height: 1;
          cursor: pointer;
        " onmouseover="this.style.background='#E2C07A';this.style.borderColor='#E2C07A'"
           onmouseout="this.style.background='#C9A84C';this.style.borderColor='#C9A84C'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
          Book Fast Track Now
          <svg class="sgn-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>'''
assert hero.count(old_cta) == 1
hero = hero.replace(old_cta, new_cta)

# 4d. CSS responsive cua hero chi nham vao THE <a>:
#         @media (max-width: 600px) { .sgn-cta-row a { justify-content: center } }
#     Duoi 600px hang CTA chuyen thanh cot nen hai con GIAN HET CHIEU NGANG. The <a>
#     duoc can giua, con <button> vua doi o 4b thi KHONG khop selector -> noi dung dat
#     o flex-start, chu nam lech sang trai trong mot nen vang trai het man hinh.
#     Day DUNG la cai bay da gap o CAF: doi the ma khong doi selector di kem.
#     DAF cung dang dinh y het (.daf-cta-row a) -- chua sua vi chua duoc yeu cau.
old_css = ".sgn-cta-row a {\n    justify-content: center !important;\n  }"
new_css = ".sgn-cta-row a,\n  .sgn-cta-row button {\n    justify-content: center !important;\n  }"
assert hero.count(old_css) == 1, "khong tim thay dung 1 lan quy tac .sgn-cta-row a"
hero = hero.replace(old_css, new_css)

# 4c. nut "Book Now" trong the info -> nut picker
i = hero.index('<a href="#services" style="\n        display: flex;')
old_bn = hero[i:hero.index('</a>', i) + 4]
new_bn = '''<button type="button" class="sgn-pick-btn" aria-haspopup="true" aria-expanded="false" style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        padding: 15px 18px;
        margin: 0;
        background: #C9A84C;
        color: #0B1F3A;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        text-decoration: none;
        border-radius: 3px;
        border: 2px solid #C9A84C;
        box-sizing: border-box;
        line-height: 1;
        cursor: pointer;
      " onmouseover="this.style.background='#E2C07A'" onmouseout="this.style.background='#C9A84C'">
        Book Now &mdash; Response in 10 min
        <svg class="sgn-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </button>'''
assert hero.count(old_bn) == 1
hero = hero.replace(old_bn, new_bn)

# ---------------------------------------------------------------- 5. FAQs: them muc 12
faq = next(b for _, n, b, _ in blocks(page) if n == "FAQs")
items = [m.start() for m in re.finditer(r'<div class="sgn-faq-item"', faq)]
assert len(items) == 11, f"cho 11 muc FAQ, thay {len(items)}"
# chen sau muc cuoi cung: tim </div> dong muc cuoi bang cach dem the
last = items[-1]
depth, j = 0, last
for m in re.finditer(r'<div\b|</div>', faq[last:]):
    depth += 1 if m.group(0) != "</div>" else -1
    if depth == 0:
        j = last + m.end()
        break
faq = faq[:j] + "\n<!--dat:zone:wait-faq-->\n<!--/dat:zone:wait-faq-->\n" + faq[j:]

# ---------------------------------------------------------------- 6. rap lai
out, seen = [], []
for full, name, body, close in blocks(page):
    if name == "Hero Banner":
        body = hero
    elif name == "FAQs":
        body = faq
    out.append(full + body + close)
    seen.append(name)
    if name == "Hero Banner":
        out.append('[ux_html label="Wait Times"]\n' + wait + '\n[/ux_html]')
        seen.append("Wait Times")
out.append('[ux_html label="Booking Picker"]\n' + pick + '\n[/ux_html]')
seen.append("Booking Picker")

res = "\n".join(out) + "\n"
open(DST, "w", encoding="utf-8").write(res)
print(len(seen), "element:", " · ".join(seen))
print(f"{len(page):,} -> {len(res):,} bytes")
