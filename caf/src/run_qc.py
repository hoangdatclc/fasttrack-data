# -*- coding: utf-8 -*-
"""Cong QC cho trang chu CAF (Nha Trang / Cam Ranh)."""
import sys, qc

LABELS = ["Nav Bar", "Hero Banner", "Wait Times", "What Is Fast Track?", "Services",
          "Booking", "Reviews", "FAQs", "Footer", "Smooth Scroll", "Whatsapp Float",
          "Mobile Book Now", "Booking Picker"]

MUSTS = ['add-to-cart=311', 'add-to-cart=313',
         '[caf_price service="fast_track_arrival"]', '[caf_price service="fast_track_departure"]',
         'id="wait-times"', 'id="caf-pick-tpl"', 'id="caf-marquee"',
         'https://schema.org/FAQPage']

COUNTS = {
    r'<img': 16,
    r'https://schema\.org/Question': 13,
    r'https://schema\.org/Answer': 13,
    r'class="caf-faq-item"': 13,
    r'class="caf-pick-btn[" ]': 3,          # 2 hero + 1 wait-times  (DAF cung 3)
    r'add-to-cart=311': 3,                  # Services + Footer + Booking Picker (DAF cung 3)
    r'add-to-cart=313': 3,
}

ZONES = ["wait-hero", "wait-section", "wait-faq"]

if __name__ == "__main__":
    sys.exit(qc.main(sys.argv[1], LABELS, MUSTS, COUNTS, ZONES))
