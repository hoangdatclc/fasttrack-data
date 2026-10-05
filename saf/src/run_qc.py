# -*- coding: utf-8 -*-
"""Cong QC cho trang chu SAF (Ho Chi Minh / Tan Son Nhat)."""
import sys, qc

LABELS = ["Nav Bar", "Hero Banner", "Wait Times", "What Is Fast Track?", "Services",
          "Booking", "Reviews", "FAQs", "Footer", "Smooth Scroll", "Whatsapp & Mess",
          "Book Now Button", "Booking Picker"]

MUSTS = ['add-to-cart=311', 'add-to-cart=313',
         '[saf_price service="fast_track_arrival"]',
         '[saf_price service="fast_track_departure"]',
         '[saf_price service="connection"]',
         'id="wait-times"', 'id="sgn-pick-tpl"', 'id="sgn-carousel-track"',
         'https://schema.org/FAQPage',
         # SAF cong bo "under 20 minutes" -- khac quy uoc ~10 / 10-15 cua ba site kia.
         # Neu renderer bi be ve quy uoc kia thi chuoi nay bien mat va QC bat duoc.
         'Under 20 min', 'under 20 minutes']

COUNTS = {
    r'<img': 15,
    r'https://schema\.org/Question': 12,
    r'https://schema\.org/Answer': 12,
    r'class="sgn-faq-item"': 12,
    r'class="sgn-review-card"': 16,
    r'class="sgn-pick-btn[" ]': 3,          # 2 hero + 1 wait-times (nhu DAF/CAF)
    r'add-to-cart=311': 3,                  # Services + Footer + Booking Picker
    r'add-to-cart=313': 3,
    # SAF co BA dich vu. Dong Connection trong picker dan sang trang dich vu rieng,
    # khong phai add-to-cart -- dem rieng de khong ai lang le bo mat.
    # 6 = Nav x2 + Hero + Services + FAQs + Footer. KHONG co trong picker.
    # Thanh 7 nghia la ai do da them Connection tro lai picker -- xem ly do trong
    # port_page.py truoc khi doi con so nay.
    r'ho-chi-minh-airport-connecting-flight-service': 6,
}

ZONES = ["wait-hero", "wait-section", "wait-faq"]

# Fast Track o SAF co BA bac: Lighter ~10 · Moderate ~15 · Busy "Under 20".
# Dem cung so lan tung chuoi la gion: so khung moi bac doi theo thang. Thay vao do
# kiem BAT BIEN -- cot Fast Track chi duoc chua ba chuoi nay (hoac dau gach khi khung rong).
FT_ALLOWED = {"~10 min", "~15 min", "15&ndash;20 min", "\u2014"}


def check_ft_column(path):
    import re
    s = open(path, encoding="utf-8").read()
    vals = re.findall(r'class="sgn-wt-cell sgn-wt-ft" role="cell" data-label="With Fast Track">([^<]*)<', s)
    if not vals:
        return ["khong tim thay o nao cua cot Fast Track"]
    bad = sorted(set(vals) - FT_ALLOWED)
    if bad:
        return [f"cot Fast Track co gia tri la: {bad} (chi duoc {sorted(FT_ALLOWED)})"]
    # bac cang ban thi so cang lon -- thu tu phai khong giam theo bang? KHONG dung,
    # vi khung ban co the xen ke khung vang. Chi can co it nhat mot o "Under 20 min":
    # SGN thang nao cung co khung Busy; khong co tuc la hieu chuan da troi.
    if "15&ndash;20 min" not in vals:
        return ["khong co khung Busy nao -- hieu chuan co ve da troi, dung lai kiem"]
    return []


if __name__ == "__main__":
    rc = qc.main(sys.argv[1], LABELS, MUSTS, COUNTS, ZONES)
    errs = check_ft_column(sys.argv[1])
    for e in errs:
        print(" -", e)
    sys.exit(rc or bool(errs))
