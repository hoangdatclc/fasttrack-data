# -*- coding: utf-8 -*-
"""Nang trang HAF tu 11 len 13 element: them Wait Times + Booking Picker, khoanh 3 vung.

CHAY MOT LAN. Sau lan nay quy trinh hang thang chi dung update_zones.py.

NAM cho de sai o HAF, da chan san bang assert:
  1. TIEN TO: HAF dung MOT tien to `haf-` cho CSS VA `haf_price` cho shortcode.
     SAF dung HAI (`sgn-` cho CSS, `saf_price` cho shortcode). Doi `sgn-`->`haf-`
     truoc se KHONG dong gi toi `saf_price` -- phai doi ca hai, va `saf_price`
     (gach duoi) phai di TRUOC de khong bi `saf-` nuot mat.
  2. TEN DICH VU KHAC: SAF dung fast_track_arrival / fast_track_departure.
     HAF dung fast_track / vip_departure. Doi sai thi shortcode in nguyen van ra trang.
  3. NUT HERO: HAF dang la <a href="#book-now">, va media query chi co
     `.haf-cta-row a`. Doi sang <button> MA KHONG sua media query = nut lech trai
     o man hinh <= 600px (luat 7). Hai viec phai di cung nhau, assert ca hai.
  4. BANG REVIEW: track 16 the, animation translateX(-50%) -- tuc no gia dinh hai
     nua GIONG HET. Thuc te 16 the deu khac nhau (11 review goc + 5 ban viet lai),
     nen bang GIAT moi vong 50 giay. Nhan doi thanh 32 the (16+16) de hai nua bang
     nhau. KHONG bo the nao -- khong mat noi dung nao ca.
  5. VAN XUOI TINH: "1-3 hour" xuat hien 5 lan va "under 10 minutes" 1 lan NGOAI
     vung zone. Quy trinh hang thang khong cham toi, nen neu de nguyen thi chung
     choi voi bang vinh vien (luat 5). Thay het bang cach dien dat khong co so.
"""
import re, sys, pathlib

SRC = "/home/claude/haf/page-orig.txt"
SAF = "/home/claude/saf/run-2026-10/out/saf-home-2026-10.txt"
DST = "page-in.txt"

SITE = "https://hanoiairportfasttrack.com"


def blocks(s):
    return re.findall(r'(\[ux_html label="([^"]+)"\]\n)(.*?)(\n\[/ux_html\])', s, re.S)


def saf_to_haf(h):
    """Doi tien to SAF -> HAF. THU TU QUAN TRONG: cai co gach duoi phai di truoc."""
    pairs = [
        # (1) shortcode -- gach duoi, phai truoc moi thu khac
        ('saf_price service="fast_track_arrival"',  'haf_price service="fast_track"'),
        ('saf_price service="fast_track_departure"', 'haf_price service="vip_departure"'),
        ('saf_price', 'haf_price'),
        # (2) ten ham JS
        ('sgnFaqToggle', 'hafFaqToggle'),
        ('sgnCarouselMove', 'hafCarouselMove'),
        # (3) tien to CSS
        ('sgn-', 'haf-'),
        ('#sgn', '#haf'), ('"sgn', '"haf'), ("'sgn", "'haf"),
        # (4) ten rieng
        ('https://hochiminhairportfasttrack.com', SITE),
        ('Tan Son Nhat International Airport (SGN)', 'Noi Bai International Airport (HAN)'),
        ('Tan Son Nhat International Airport', 'Noi Bai International Airport'),
        ('Tan Son Nhat Airport', 'Noi Bai Airport'),
        ('Tan Son Nhat', 'Noi Bai'),
        ('SGN', 'HAN'),
        ('Ho Chi Minh City', 'Hanoi'),
        ('SAF HOMEPAGE', 'HAF HOMEPAGE'),
    ]
    for a, b in pairs:
        h = h.replace(a, b)
    return h


def audit(h, where):
    bad = re.findall(r'sgn[-_A-Za-z]*|saf[-_A-Za-z]*|SGN|Tan Son Nhat|Ho Chi Minh|hochiminhairportfasttrack',
                     h)
    bad = [x for x in bad if x.lower() not in ("safe", "safety", "safely")]
    if bad:
        sys.exit(f"[{where}] con sot tien to SAF: {sorted(set(bad))}")


page = open(SRC, encoding="utf-8").read()
safp = open(SAF, encoding="utf-8").read()
sb = {n: b for _, n, b, _ in blocks(safp)}
hb = {n: b for _, n, b, _ in blocks(page)}
ORDER_OLD = [n for _, n, _, _ in blocks(page)]
assert ORDER_OLD == ["Nav Bar", "Hero Banner", "What Is Fast Track?", "Services", "Booking",
                     "Reviews", "FAQs", "Footer", "Smooth Scroll", "Whatsapp & Mess",
                     "Book Now Button"], ORDER_OLD

# ---------------------------------------------------------------- 1. Wait Times
wait = saf_to_haf(sb["Wait Times"])
audit(wait, "Wait Times")

# ---------------------------------------------------------------- 2. Booking Picker
pick = saf_to_haf(sb["Booking Picker"])
audit(pick, "Booking Picker")
assert pick.count("add-to-cart=311") == 1 and pick.count("add-to-cart=313") == 1
assert '[haf_price service="fast_track"]' in pick
assert '[haf_price service="vip_departure"]' in pick
# nhan "Fast Track Departure" cua HAF o muc Services la "Fast Track Departure" -- khop san

pathlib.Path("_wait.html").write_text(wait, encoding="utf-8")
pathlib.Path("_pick.html").write_text(pick, encoding="utf-8")
print("Wait Times :", len(wait), "bytes")
print("Booking Picker:", len(pick), "bytes")


# ---------------------------------------------------------------- 3. Hero Banner
hero = hb["Hero Banner"]

# 3a. Khoanh vung wait-hero: thay dau the "Why Choose Fast Track?" + 3 dong chi so
#     (Save / From / 24/7) bang vung may ghi. Giu nguyen cac o dich vu ben duoi.
k = hero.index("Why Choose Fast Track?")
start = hero.rindex('      <div style="', 0, k)
end = hero.index('      <div style="display: flex; gap: 8px;">')
cut = hero[start:end]
assert cut.count("1 - 3 hours") == 1, "khong tim thay dong 'Save 1 - 3 hours'"
assert cut.count('[haf_price service="fast_track"]') == 1
assert "24/7" in cut and "Support" in cut
assert hero.count('      <div style="display: flex; gap: 8px;">') == 1
hero = hero[:start] + (
    "<!--dat:zone:wait-hero-->\n"
    "      <!-- May ghi. Dung sua tay: update_zones.py se ghi de moi thang. -->\n"
    "<!--/dat:zone:wait-hero-->\n\n"
) + hero[end:]

# 3b. Nut vang o hero -> <button class="haf-pick-btn"> de mo panel chon dich vu.
#     Bo transform o hover (hoc tu SAF): nut co transform lam panel neo lech cho.
old_a_open = '''        <a href="#book-now" style="
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 15px 32px;
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
          transition: all 0.3s ease;
          box-sizing: border-box;
          line-height: 1;
        " onmouseover="this.style.background='#E2C07A';this.style.borderColor='#E2C07A';this.style.transform='translateY(-2px)'"
           onmouseout="this.style.background='#C9A84C';this.style.borderColor='#C9A84C';this.style.transform='translateY(0)'">'''
assert hero.count(old_a_open) == 1, "khong khop nut vang hero"
new_btn_open = '''        <button type="button" class="haf-pick-btn" aria-haspopup="true" aria-expanded="false" style="
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
           onmouseout="this.style.background='#C9A84C';this.style.borderColor='#C9A84C'">'''
hero = hero.replace(old_a_open, new_btn_open)
old_a_close = '''          Book Fast Track Now
        </a>'''
assert hero.count(old_a_close) == 1
hero = hero.replace(old_a_close, '''          Book Fast Track Now
          <svg class="haf-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>''')

# 3c. LUAT 7 -- media query phai phu ca <button>, khong chi <a>.
#     Thieu dong nay = nut lech trai o man hinh <= 600px. Do bang probe.py.
old_mq = """  .haf-cta-row a {
    justify-content: center !important;
  }"""
assert hero.count(old_mq) == 1, "khong khop media query .haf-cta-row a"
hero = hero.replace(old_mq, """  .haf-cta-row a,
  .haf-cta-row button {
    justify-content: center !important;
  }""")

# 3d. LUAT 5 -- bo con so cung trong van xuoi hero.
for a, b in [
    ("skip the 1&#8211;3 hour immigration queue", "skip the main immigration queue"),
    ("skip the 1–3 hour immigration queue", "skip the main immigration queue"),
    ("Priority immigration lane — avoid the 1–3 hour queue",
     "Priority immigration lane — straight past the main queue"),
    ("Priority immigration lane &#8212; avoid the 1&#8211;3 hour queue",
     "Priority immigration lane &#8212; straight past the main queue"),
]:
    hero = hero.replace(a, b)
assert "1–3 hour" not in hero and "1 - 3 hours" not in hero, "con sot '1-3 hour' trong hero"
assert hero.count("haf-pick-btn") == 1
assert hero.count("<!--dat:zone:wait-hero-->") == 1
print("Hero Banner: ok,", len(hero), "bytes")


# ---------------------------------------------------------------- 4. FAQs: vung wait-faq
faq = hb["FAQs"]
# Dat vao CUOI COT TRAI, khong phai cot phai: cot trai dang co 5 muc, cot phai 7.
# Them vao cot phai thanh 5/8 -- lech han mot nua man hinh. Vao cot trai thanh 6/7.
anchor = "      </div><!-- /LEFT -->"
assert faq.count(anchor) == 1, "khong tim thay cuoi cot trai cua FAQ"
assert "haf-faq-a12" not in faq, "da co FAQ a12 roi"
assert len(re.findall(r'class="haf-faq-item"', faq)) == 11
faq = faq.replace(anchor,
    "<!--dat:zone:wait-faq-->\n"
    "        <!-- May ghi. Dung sua tay: update_zones.py se ghi de moi thang. -->\n"
    "<!--/dat:zone:wait-faq-->\n\n" + anchor)

# ---------------------------------------------------------------- 5. Reviews: nhan doi bang
# Bang chay bang `animation: haf-scroll` -> `translateX(-50%)`, tuc no gia dinh track
# gom HAI NUA GIONG HET: chay het nua dau thi nhay ve 0 va khong ai thay. Thuc te track
# co 16 the KHAC NHAU (11 the co moc <!-- R1..R11 --> + 5 ban viet lai khong co moc),
# nen moi 50 giay bang GIAT mot cai. Nhan ca 16 the lam ban sao -> 32 the, hai nua bang
# nhau. KHONG bo the nao: khong mat mot dong review nao ca.
rev = hb["Reviews"]
OPEN = '<div class="haf-marquee-track">'
start = rev.index(OPEN)
depth = 0
for m in re.finditer(r'<(/?)div\b[^>]*>', rev[start:]):
    depth += -1 if m.group(1) else 1
    if depth == 0:
        end = start + m.end()
        break
else:
    sys.exit("khong dong duoc the haf-marquee-track")
inner = rev[start + len(OPEN):end - len("</div>")]
assert inner.count('<div class="haf-review-card') == 16, inner.count('<div class="haf-review-card')
assert inner.count("</div>") - inner.count("<div") == 0, "ruot track khong can bang the"
clone = inner.replace('<div class="haf-review-card"',
                      '<div class="haf-review-card" aria-hidden="true"')
assert clone.count('aria-hidden="true"') - inner.count('aria-hidden="true"') == 16
rev = rev[:start + len(OPEN)] + inner + "\n<!-- ban sao de bang chay lien mach -->\n" + clone + rev[end - len("</div>"):]
assert len(re.findall(r'<div class="haf-review-card', rev)) == 32
print("Reviews: 16 -> 32 the (hai nua giong het nhau)")

# ---------------------------------------------------------------- 6. Van xuoi tinh (luat 5)
PROSE = {
    "What Is Fast Track?": [
        (">Save 1&#8211;3 Hours<", ">Save Over an Hour<"),
        (">Save 1–3 Hours<", ">Save Over an Hour<"),
        ("you're through in under 10 minutes.", "you&rsquo;re through in 10 to 15 minutes."),
        ("you&rsquo;re through in under 10 minutes.", "you&rsquo;re through in 10 to 15 minutes."),
        ("Stand in immigration queues for 1–3 hours, especially after busy flights",
         "Stand in the immigration queue for over an hour after the busiest flights"),
        ("Stand in immigration queues for 1&#8211;3 hours, especially after busy flights",
         "Stand in the immigration queue for over an hour after the busiest flights"),
    ],
    "Services": [
        ("Immigration in 15–20 min, not 1–3 hours", "Immigration in 10&#8211;15 min, not over an hour"),
        ("Immigration in 15&#8211;20 min, not 1&#8211;3 hours", "Immigration in 10&#8211;15 min, not over an hour"),
    ],
    "Footer": [
        ("Skip the 1–3 hour immigration queue and", "Skip the main immigration queue and"),
        ("Skip the 1&#8211;3 hour immigration queue and", "Skip the main immigration queue and"),
    ],
}
patched = {}
for name, subs in PROSE.items():
    t = hb[name]
    hits = 0
    for a, b in subs:
        if a in t:
            hits += t.count(a)
            t = t.replace(a, b)
    assert hits > 0, f"[{name}] khong thay cau nao de sua"
    patched[name] = t
    print(f"{name}: sua {hits} cau")

# ---------------------------------------------------------------- 7. Lap lai trang 13 element
NEW = {"Hero Banner": hero, "Wait Times": wait, "Booking Picker": pick,
       "FAQs": faq, "Reviews": rev, **patched}
ORDER = ["Nav Bar", "Hero Banner", "Wait Times", "What Is Fast Track?", "Services", "Booking",
         "Reviews", "FAQs", "Footer", "Smooth Scroll", "Whatsapp & Mess", "Book Now Button",
         "Booking Picker"]
out = ["<!-- wp:flatsome/uxbuilder -->"]
for n in ORDER:
    body = NEW.get(n, hb.get(n))
    assert body is not None, f"thieu element {n}"
    out.append(f'[ux_html label="{n}"]\n{body}\n[/ux_html]')
out.append("\n<!-- /wp:flatsome/uxbuilder -->")
res = "\n".join(out)
pathlib.Path(DST).write_text(res, encoding="utf-8")
print(f"\n{DST}: {len(res)} bytes, {len(ORDER)} element")

# ---------------------------------------------------------------- 8. Kiem nhanh
for mark in ("wait-hero", "wait-section", "wait-faq"):
    print(f"  dat:zone:{mark} mo/dong:",
          res.count(f"<!--dat:zone:{mark}-->"), res.count(f"<!--/dat:zone:{mark}-->"))
for pat in ("1–3 hour", "1 - 3 hours", "1&#8211;3 hour", "15–20 min", "haf-pick-btn",
            "haf-pick-tpl", 'id="wait-times"'):
    print(f"  {pat!r}: {res.count(pat)}")
