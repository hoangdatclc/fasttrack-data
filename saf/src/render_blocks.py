"""Render 3 vùng từ {site}-wait-YYYY-MM.json."""
import json, os, sys
from datetime import date

MONTHS = ["January","February","March","April","May","June","July",
          "August","September","October","November","December"]

fmt_date = lambda d: f"{d.day} {MONTHS[d.month - 1]} {d.year}"
# window có thể gồm nhiều cụm rời, nối bằng '|'. Một cụm thì kết quả y hệt bản cũ.
dash  = lambda w: " and ".join("&ndash;".join(r.split("-")) for r in w.split("|"))
words = lambda w: ", or between ".join(" and ".join(r.split("-")) for r in w.split("|"))
rng   = lambda p: f"{p[0]}&ndash;{p[1]}"
# Fast Track BA BAC o SAF: Lighter ~10 · Moderate ~15 · Busy "Under 20".
# "Under" chu khong phai "~" o bac Busy vi do la cam ket TRAN, khong phai uoc tinh.
# Bang tra cuu tuong minh, khong dung quy tac ngam (v>=20 thi "Under") -- quy tac ngam
# se im lang doi nghia khi ai do chinh con so trong FT.
FT_WORD = {10: "~10", 15: "~15", 20: "Under 20"}          # hero + van xuoi
# O BANG dung "15-20" thay cho "Under 20". Ly do thuan hien thi: cot Fast Track hep,
# tren dien thoai "Under 20 min" xuong hai dong, nhin nhu loi. "15-20" ngan hon ma
# KHONG noi khac di -- bac Moderate la 15, bac Busy tran 20, nen dai 15-20 chinh la
# cai bang dang mo ta. Hero rong nen van giu "Under 20 min" (chu cam ket manh hon).
FT_CELL = {10: "~10", 15: "~15", 20: "15&ndash;20"}
ftxt   = lambda v: FT_WORD.get(v, f"~{v}")
ftcell = lambda v: FT_CELL.get(v, f"~{v}")
ft_of = lambda tier, c: c.get(tier, c["busy"]) if isinstance(c, dict) else c
# Cau o the vang phai khop voi con so that cua khung de tho nhat. O PQC khung do la
# 37-46 phut nen "ban co the khong can chung toi" la dung. O DAD khung de tho nhat
# van la 43-65 phut -- noi cau do thanh ra sai, va ban re chinh dich vu cua minh.
# O SGN khung 16:00-20:00 chi co 1 chuyen va ra 28-30 phut -- that su ngan, nen cau
# "co the ban khong can chung toi" o day la DUNG. De no tu dong theo tier, dung ep.
# O ba site kia cau nay bam theo BAC. O SAF bam theo bac se SAI: khung "quick" cua SGN
# van la 51-55 phut, noi "co the ban khong can chung toi" la noi sai va ban re dich vu.
# => bam theo CON SO THAT. Nguong 35 phut: duoi do thi khach that su khong can.
calm_line = lambda q: ("you may not need us, and we will say so."
                       if q["range"][1] <= 35
                       else "the line is shorter, though rarely short.")


def level(b):
    # BA bac, BA mau, thang VANG -> CAM DAT -> DO CHOI.
    # Quy tac: do CHOI phai TANG theo muc do, khong chi doi sac. Ban truoc dung cam
    # #C2410C cho Moderate va do sam #8B1A1A cho Busy -> cam bao hoa hon nen HUT MAT
    # HON ca khung cao diem, nguoc han y nghia. Gio Busy la mau choi nhat bang.
    # Tuong phan tren nen trang: vang 5,1:1 · cam dat 5,3:1 · do 5,5:1 -- deu dat WCAG AA.
    # Co y KHONG dung xanh la cho bac nhe vi #1a7a42 la mau cot Fast Track.
    return {"none":     ("none",  "#8a9ab0", "No regular international arrivals"),
            # "Usually quick" la nhan cua PAF/DAF/CAF. O SGN khung nhe nhat van 51-55 phut
            # nen chu "quick" la noi doi. "Lighter" dung ca ve tuong doi lan tuyet doi.
            "quick":    ("light", "#8B6914", "Lighter"),
            "moderate": ("light", "#A8541A", "Moderate"),
            "busy":     ("busy",  "#C9281C", "Busy")}[b.get("tier", "quick")]


def cities(d, window):
    """Ten thanh pho cua cac chuyen ha canh trong `window`, theo thu tu GIO.

    Hai cho tung sai, deu sua o day:
      1. CUA SO VAT QUA NUA DEM bi bo im. "20:00-06:00" cho ra span (20,6) va phep
         kiem `20 <= h < 6` KHONG BAO GIO dung -> toan bo cum dem khong duoc tinh.
         O SGN day dung la cum quan trong nhat (11 chuyen Han 20:20-00:35), nen the
         "When Fast Track matters most" ke ten cac thanh pho ban ngay. Khong ai bao.
      2. Lay 4 ten DAU TIEN theo thu tu trong file lich bay, khong phai theo gio ->
         danh sach doi khi khi sap xep lai file. Gio sap theo gio ha canh.
    """
    spans = [tuple(int(x[:2]) for x in r.split("-")) for r in window.split("|")]

    def inside(h):
        for a, z in spans:
            if a < z:
                if a <= h < z:
                    return True
            else:                      # vat qua nua dem: [a,24) hop [0,z)
                if h >= a or h < z:
                    return True
        return False

    picked = [f for f in d["sample_flights"] if inside(int(f["time"][:2]))]
    picked.sort(key=lambda f: f["time"])

    # KHAC BA SITE KIA: chon theo SO CHUYEN, khong theo chuyen den som nhat.
    # O CXR/DAD mot khung chi co 2-11 chuyen nen "bon cai dau theo gio" la dai dien duoc.
    # O SGN khung 16:00-24:00 co 59 chuyen: bon cai dau theo gio ra "Perth, Bangkok,
    # Sydney va Melbourne" -- dung tung chu nhung sai ve y, va se nhay lung tung moi
    # thang chi vi mot chuyen doi gio 5 phut. Xep theo so chuyen cho ra "Bangkok,
    # Singapore, Taipei va Hong Kong": dung thi truong that cua khung do va on dinh.
    # Hoa thi chuyen nao HA SOM HON dung truoc -> ket qua van tat dinh.
    order, count = {}, {}
    for f in picked:
        c = d["cities"].get(f["from"], f["from"])
        count[c] = count.get(c, 0) + 1
        order.setdefault(c, f["time"])
    out = sorted(count, key=lambda c: (-count[c], order[c]))[:4]
    return ", ".join(out[:-1]) + " and " + out[-1] if len(out) > 1 else "".join(out)


def render_hero(d, updated):
    h = d["headline"]
    # Hero lay CA CUM BAC CAO NHAT (h["busy"]), khong phai mot khung te nhat (h["peak"]).
    # Thang 10/2026: hai khung Busy 16:00-20:00 (93-113) va 20:00-24:00 (78-97) -> 78-113.
    # Lay mot khung thi con so hero (93-113) khong phu duoc ca gio cao diem, khach ha
    # luc 21:00 doc hero se thay so khong khop voi bang ngay ben duoi.
    busy = h["busy"]
    return f'''
      <div style="
        display: flex;
        align-items: center;
        gap: 9px;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #0B1F3A;
        padding-bottom: 10px;
      ">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        SGN Immigration &mdash; {d["month_label"]}
      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; line-height:1.55; color:#5A5A72; margin:0; padding:0 0 14px; border-bottom:1px solid #E8E4DE;">{d["basis"]}</p>

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Queue</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#C9281C; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{rng(busy["range"])} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Last passengers off a flight landing in the busiest hours &mdash; from touchdown to leaving immigration</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Fast Track</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{ftxt(ft_of(busy.get("tier","busy"), h["fast_track"]))} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Through immigration with our service &mdash; every flight, every hour</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[saf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; color:#5A5A72; margin:0; padding:0;">Updated {fmt_date(updated)} &middot; <a href="#wait-times" style="color:#8B6914; font-weight:600; text-decoration:none; border-bottom:1px solid rgba(201,168,76,0.4);">Hour by hour</a></p>
'''


def render_section(d, updated):
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    # CA BA cho tren trang (hero · doan dan · FAQ) deu lay h["busy"] -- toan bo cum bac
    # cao nhat -- va deu goi la "the busiest hours", khong ke ten khung.
    # h["peak"] (mot khung te nhat) van nam trong JSON nhung KHONG cho ra trang nua:
    # ba cho noi ba con so khac nhau cho cung mot cau hoi thi doc len thanh mau thuan,
    # va khach ha luc 21:00 se thay so o hero khong khop voi so o doan dan.
    # Khung gio cu the da co day du o BANG ngay ben duoi; doan dan khong can lap lai.
    busy = h["busy"]
    bands = d["bands"]
    top = max(b["standard"][1] for b in bands if b["standard"])
    rows = []
    for b in bands:
        lvl, color, tag = level(b)
        label = dash(b["band"])
        if b["standard"] is None:
            rows.append(f'''
        <div class="sgn-wt-row sgn-wt-none" role="row">
          <div class="sgn-wt-band" role="rowheader"><strong>{label}</strong><span class="sgn-wt-flights">{tag}</span></div>
          <div class="sgn-wt-queue" role="cell" data-label="Standard queue"><span class="sgn-wt-num" style="color:#8a9ab0 !important;">&mdash;</span><span class="sgn-wt-sub">{d["notes"]["empty_band_note"]}</span></div>
          <div class="sgn-wt-cell sgn-wt-ft" role="cell" data-label="With Fast Track">&mdash;</div>
        </div>''')
            continue
        n = b["flights"]
        width = max(10, round(100 * b["standard"][1] / top))
        rows.append(f'''
        <div class="sgn-wt-row sgn-wt-{lvl}" role="row">
          <div class="sgn-wt-band" role="rowheader"><strong>{label}</strong><span class="sgn-wt-flights">{n} international arrival{"s" if n != 1 else ""} &middot; {tag}</span></div>
          <div class="sgn-wt-queue" role="cell" data-label="Standard queue">
            <span class="sgn-wt-num" style="color:{color} !important;">{rng(b["standard"])} min</span>
            <span class="sgn-wt-track" aria-hidden="true"><span class="sgn-wt-fill" style="width:{width}% !important; background:{color} !important;"></span></span>
          </div>
          <div class="sgn-wt-cell sgn-wt-ft" role="cell" data-label="With Fast Track">{ftcell(ft_of(b.get("tier","quick"), ft))} min</div>
        </div>''')
    return f'''
    <div class="sgn-wt-head">
      <span class="sgn-wt-eyebrow">Immigration wait times &middot; {d["month_label"]} &middot; updated {fmt_date(updated)}</span>
      <h2 id="sgn-h2-wait">How Long Is the Immigration Queue at Tan Son Nhat Airport in {d["month_label"]}?</h2>
      <div aria-hidden="true" style="width:44px; height:3px; background:#C9A84C; margin:14px auto 20px;"></div>
      <p class="sgn-wt-lead">In {d["month_label"]}, the last passengers off a flight landing in the busiest hours need an estimated <strong>{rng(busy["range"])} minutes</strong> from touchdown to leaving immigration at Tan Son Nhat International Airport (SGN). At quieter hours it is {rng(quiet["range"])} minutes. With Fast Track it is about {ft_of("quick", ft)} minutes, and under {ft_of("busy", ft)} even at peak.</p>
    </div>

    <div class="sgn-wt-table" role="table" aria-label="Estimated time from landing to leaving immigration at Tan Son Nhat Airport by arrival time, {d["month_label"]}">
      <div class="sgn-wt-row sgn-wt-header" role="row">
        <div role="columnheader">Landing time</div>
        <div role="columnheader">Standard queue &mdash; last passengers</div>
        <div role="columnheader">With Fast Track</div>
      </div>{"".join(rows)}
    </div>

    <div class="sgn-wt-cards">
      <div class="sgn-wt-card sgn-wt-card-gold">
        <h3>When Fast Track matters most</h3>
        <p>Flights landing {dash(busy["window"])}, when arrivals from {cities(d, busy["window"])} land minutes apart. Land {dash(quiet["window"])} &mdash; {calm_line(quiet)}</p>
      </div>
      <div class="sgn-wt-card">
        <h3>{d["month_label"]} notes</h3>
        <p>{d["notes"]["month_notes"]}</p>
      </div>
    </div>

    <p class="sgn-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a representative {d["month_label"].split()[0]} day, counting deplaning and the walk to the hall, and checked against the daily immigration volume the airport publishes. Estimates, not measurements.</p>

    <div class="sgn-wt-cta">
      <button type="button" class="sgn-pick-btn sgn-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="sgn-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
    </div>
'''


def render_faq(d, updated, faq_id="sgn-faq-a12"):
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = h["busy"]   # FAQ bam theo hero va doan dan -- cung mot con so, cung mot cach noi
    return f'''
        <div class="sgn-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="sgn-faq-btn" type="button" onclick="sgnFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="sgn-faq-q" itemprop="name">How long is the immigration queue at Tan Son Nhat Airport in {d["month_label"]}?</h3>
            <span class="sgn-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="sgn-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, the last passengers off a flight landing in the busiest hours need an estimated <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> from touchdown to leaving immigration. At quieter hours it is {rng(quiet["range"])} minutes.</p>
            <p style="margin-top:10px !important;">With Fast Track it is under {ft_of("busy", ft)} minutes even at the busiest hours, and about {ft_of("quick", ft)} when the hall is lighter. <a href="#wait-times" style="color:#C9A84C; font-weight:600; text-decoration:none;">See the estimate for your landing time</a> (updated {fmt_date(updated)}).</p>
            </div>
          </div>
        </div>
'''


def main(json_path, updated):
    d = json.load(open(json_path, encoding="utf-8"))
    os.makedirs("zones", exist_ok=True)
    open("zones/wait-hero.html", "w", encoding="utf-8").write(render_hero(d, updated))
    open("zones/wait-section.html", "w", encoding="utf-8").write(render_section(d, updated))
    open("zones/wait-faq.html", "w", encoding="utf-8").write(render_faq(d, updated))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "saf-wait-2026-10.json",
         date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today())
