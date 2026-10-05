# -*- coding: utf-8 -*-
"""Cong QC cho trang chu HAF (Ha Noi / Noi Bai). Chay sau update_zones.py."""
import sys, qc

LABELS = ["Nav Bar", "Hero Banner", "Wait Times", "What Is Fast Track?", "Services",
          "Booking", "Reviews", "FAQs", "Footer", "Smooth Scroll", "Whatsapp & Mess",
          "Book Now Button", "Booking Picker"]

# HAF dung TEN DICH VU KHAC ba site kia: fast_track (den) / vip_departure (di) /
# connection (noi chuyen). Khong phai fast_track_arrival / fast_track_departure.
MUSTS = ['add-to-cart=311', 'add-to-cart=313',
         '[haf_price service="fast_track"]',
         '[haf_price service="vip_departure"]',
         '[haf_price service="connection"]',
         'id="wait-times"', 'id="haf-pick-tpl"', 'id="haf-carousel-track"',
         'class="haf-marquee-track"', 'https://schema.org/FAQPage']

COUNTS = {
    r'<img': 17,
    r'https://schema\.org/Question': 12,     # 11 viet tay + 1 trong vung wait-faq
    r'https://schema\.org/Answer': 12,
    r'class="haf-faq-item"': 12,
    r'class="haf-pick-btn[" ]': 2,           # 1 hero + 1 cuoi muc Wait Times
    r'add-to-cart=311': 3,                   # Services + Footer + Booking Picker
    r'add-to-cart=313': 3,
    # Bang review chay bang translateX(-50%) -> PHAI la so CHAN va hai nua giong het.
    # 16 the goc + 16 ban sao aria-hidden. Them/bot the le = bang giat moi vong.
    r'class="haf-review-card': 32,
    # Luat 5: khong con con so cung nao trong van xuoi tinh.
    r'1&#8211;3 hour': 0, r'1–3 hour': 0, r'15–20 min': 0,
    # Luat 3 va 4: hai cau bi cam vinh vien.
    r'you may not need us': 0, r'Usually quick': 0,
    # Luat 1: khong con ma mau cu nao.
    r'#1a5c2e': 0, r'#C1272D': 0,
    # Luat 7: media query phai phu ca <button>.
    r'\.haf-cta-row button': 1,
    # Tieu de the hero giu nguyen nhu trang goc (chu site chot 05/10/2026) va nam
    # NGOAI vung zone -> quy trinh hang thang khong duoc lam mat no.
    r'Why Choose HAN Fast Track\?': 1,
    # The hero HAF la Save / From / 24-7 (ba ly do khac nhau), khong phai bang so sanh.
    # Dong phu hang SAVE phai noi CA HAI dau cua phep tru -- mat mot dau thi con so
    # tiet kiem dung tran, khach khong biet no tru tu dau. Hai dong, hai dau:
    r'Through immigration in the busiest hours: an&nbsp;estimated&nbsp;\d+(?:&ndash;\d+)?&nbsp;min<br>': 1,
    r'With Fast Track: under \d+ min, any hour': 1,
    # Chu "estimated" la cong bo bat buoc, khong duoc bo trong lan viet lai nao.
    r'an&nbsp;estimated&nbsp;\d+(?:&ndash;\d+)?&nbsp;min': 1,
    r'>Save</span>': 1, r'>24/7</span>': 1,
}

ZONES = ["wait-hero", "wait-section", "wait-faq"]

if __name__ == "__main__":
    sys.exit(qc.main(sys.argv[1], LABELS, MUSTS, COUNTS, ZONES))
