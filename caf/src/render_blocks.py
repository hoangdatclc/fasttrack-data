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
# Bac cao diem hien HAI kieu, co y (chot 05/10/2026, theo chuan SAF/DAF):
#   o BANG   -> "10-15 min": cot hep tren dien thoai.
#   HERO+van xuoi -> "Under 15": hero da co MOT dai so o dong Queue; them dai thu hai
#   ngay duoi lam yeu tuong phan "dai va bap benh" vs "ngan va chac". "Under 15" la
#   tran, dung o MOI khung, khop dong phu "every flight, every hour".
ftcell = lambda v: (f"{v[0]}&ndash;{v[1]}" if isinstance(v, (list, tuple)) else f"~{v}")
ftword = lambda v: (f"Under {v[1]}" if isinstance(v, (list, tuple)) else f"~{v}")
ftcap  = lambda c: (c["peak"][1] if isinstance(c.get("peak"), (list, tuple)) else c["peak"]) if isinstance(c, dict) else c
# Fast Track doi theo bac: khung thuong ~10 phut, khung cao diem 10-15.
ft_of = lambda tier, c: (c["peak"] if tier == "busy" else c["base"]) if isinstance(c, dict) else c
# Cau o the vang phai khop voi con so that cua khung de tho nhat. O PQC khung do la
# 37-46 phut nen "ban co the khong can chung toi" la dung. O DAD khung de tho nhat
# van la 43-65 phut -- noi cau do thanh ra sai, va ban re chinh dich vu cua minh.
# O CXR khung 16:00-20:00 chi co 1 chuyen va ra 28-30 phut -- that su ngan, nen cau
# "co the ban khong can chung toi" o day la DUNG. De no tu dong theo tier, dung ep.
# Chu site CAM cau "you may not need us, and we will say so." tu 04/10/2026, o MOI site.
# Rieng CXR khung de tho nhat that su nhanh (28-30 phut) nen cau do se DUNG o day --
# nhung lenh cam la lenh cam, va mot cau dung cho ca 5 site thi de bao tri hon.
calm_line = lambda q: "the line is shorter, though rarely short."


def level(b):
    # BA bac, BA mau, thang VANG -> CAM DAT -> DO CHOI.
    # Quy tac: do CHOI phai TANG theo muc do, khong chi doi sac. Ban truoc dung cam
    # #C2410C cho Moderate va do sam #8B1A1A cho Busy -> cam bao hoa hon nen HUT MAT
    # HON ca khung cao diem, nguoc han y nghia. Gio Busy la mau choi nhat bang.
    # Tuong phan tren nen trang: vang 5,1:1 · cam dat 5,3:1 · do 5,8:1 -- deu dat WCAG AA.
    # Co y KHONG dung xanh la cho bac nhe vi #1a7a42 la mau cot Fast Track.
    return {"none":     ("none",  "#8a9ab0", "No regular international arrivals"),
            "quick":    ("light", "#8B6914", "Lighter"),
            "moderate": ("light", "#A8541A", "Moderate"),
            "busy":     ("busy",  "#C9281C", "Busy")}[b.get("tier", "quick")]


def cities(d, window):
    """Ten thanh pho trong `window`, xep theo SO CHUYEN (khong theo gio den som nhat).

    Lay "bon cai dau theo gio" se bo qua thi truong lon chi vi no ha muon hon, va
    nhay lung tung moi thang chi vi mot chuyen doi gio 5 phut. Hoa -> chuyen HA SOM
    HON dung truoc. Toi da 4 ten.
    """
    spans = [tuple(int(x[:2]) for x in r.split("-")) for r in window.split("|")]
    def inside(h):
        return any((a <= h < z) if a < z else (h >= a or h < z) for a, z in spans)
    n, first = {}, {}
    for f in d["sample_flights"]:
        if inside(int(f["time"][:2])):
            c = d["cities"].get(f["from"], f["from"])
            n[c] = n.get(c, 0) + 1
            first.setdefault(c, f["time"])
    out = sorted(n, key=lambda c: (-n[c], first[c]))[:4]
    return ", ".join(out[:-1]) + " and " + out[-1] if len(out) > 1 else "".join(out)


def render_hero(d, updated):
    h = d["headline"]
    # CXR: cum busy TACH BACH khoi cac bac duoi (san 54 > tran Moderate 50) nen
    # cong bo CA CUM theo chuan SAF. Khac DAF -- o DAD cum busy co mot khung dao
    # dong manh keo san xuong duoi ca khung Moderate nen DAF phai dung h["peak"].
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
        CXR Immigration &mdash; {d["month_label"]}
      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; line-height:1.55; color:#5A5A72; margin:0; padding:0 0 14px; border-bottom:1px solid #E8E4DE;">{d["basis"]}</p>

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Queue</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#C9281C; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{rng(busy["range"])} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Last passengers off a flight landing in the busiest hours</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Fast Track</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{ftword(ft_of(busy.get("tier","busy"), h["fast_track"]))} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Through immigration with our service</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[caf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; color:#5A5A72; margin:0; padding:0;">Updated {fmt_date(updated)} &middot; <a href="#wait-times" style="color:#8B6914; font-weight:600; text-decoration:none; border-bottom:1px solid rgba(201,168,76,0.4);">Hour by hour</a></p>
'''


def render_section(d, updated):
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    # doan dan dung CA CUM, giong hero. The vang van ghi khung gio (ngoai le).
    busy = h["busy"]                     # the vang: toan bo cum cao diem
    bands = d["bands"]
    top = max(b["standard"][1] for b in bands if b["standard"])
    rows = []
    for b in bands:
        lvl, color, tag = level(b)
        label = dash(b["band"])
        if b["standard"] is None:
            rows.append(f'''
        <div class="caf-wt-row caf-wt-none" role="row">
          <div class="caf-wt-band" role="rowheader"><strong>{label}</strong><span class="caf-wt-flights">{tag}</span></div>
          <div class="caf-wt-queue" role="cell" data-label="Standard queue"><span class="caf-wt-num" style="color:#8a9ab0 !important;">&mdash;</span><span class="caf-wt-sub">{d["notes"]["empty_band_note"]}</span></div>
          <div class="caf-wt-cell caf-wt-ft" role="cell" data-label="With Fast Track">&mdash;</div>
        </div>''')
            continue
        n = b["flights"]
        width = max(10, round(100 * b["standard"][1] / top))
        rows.append(f'''
        <div class="caf-wt-row caf-wt-{lvl}" role="row">
          <div class="caf-wt-band" role="rowheader"><strong>{label}</strong><span class="caf-wt-flights">{n} international arrival{"s" if n != 1 else ""} &middot; {tag}</span></div>
          <div class="caf-wt-queue" role="cell" data-label="Standard queue">
            <span class="caf-wt-num" style="color:{color} !important;">{rng(b["standard"])} min</span>
            <span class="caf-wt-track" aria-hidden="true"><span class="caf-wt-fill" style="width:{width}% !important; background:{color} !important;"></span></span>
          </div>
          <div class="caf-wt-cell caf-wt-ft" role="cell" data-label="With Fast Track">{ftcell(ft_of(b.get("tier","quick"), ft))} min</div>
        </div>''')
    return f'''
    <div class="caf-wt-head">
      <span class="caf-wt-eyebrow">Immigration wait times &middot; {d["month_label"]} &middot; updated {fmt_date(updated)}</span>
      <h2 id="caf-h2-wait">How Long Is the Immigration Queue at Cam Ranh Airport in {d["month_label"]}?</h2>
      <div aria-hidden="true" style="width:44px; height:3px; background:#C9A84C; margin:14px auto 20px;"></div>
      <p class="caf-wt-lead">In {d["month_label"]}, the last passengers off a flight landing in the busiest hours need an estimated <strong>{rng(busy["range"])} minutes</strong> from touchdown to leaving immigration at Cam Ranh International Airport (CXR). At quieter hours it is {rng(quiet["range"])} minutes. With Fast Track it is about {ft_of("quick", ft)} minutes, and under {ftcap(ft)} even at the busiest hours.</p>
    </div>

    <div class="caf-wt-table" role="table" aria-label="Estimated time from landing to leaving immigration at Cam Ranh Airport by arrival time, {d["month_label"]}">
      <div class="caf-wt-row caf-wt-header" role="row">
        <div role="columnheader">Landing time</div>
        <div role="columnheader">Standard queue &mdash; last passengers</div>
        <div role="columnheader">With Fast Track</div>
      </div>{"".join(rows)}
    </div>

    <div class="caf-wt-cards">
      <div class="caf-wt-card caf-wt-card-gold">
        <h3>When Fast Track matters most</h3>
        <p>Flights landing {dash(busy["window"])}, when arrivals from {cities(d, busy["window"])} land minutes apart. Land {dash(quiet["window"])} &mdash; {calm_line(quiet)}</p>
      </div>
      <div class="caf-wt-card">
        <h3>{d["month_label"]} notes</h3>
        <p>{d["notes"]["month_notes"]}</p>
      </div>
    </div>

    <p class="caf-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a representative {d["month_label"].split()[0]} day, counting deplaning and the walk to the hall, and checked against the waits travellers report. Estimates, not measurements.</p>

    <div class="caf-wt-cta">
      <button type="button" class="caf-pick-btn caf-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="caf-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
    </div>
'''


def render_faq(d, updated, faq_id="caf-faq-a12"):
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = h["busy"]   # FAQ bam theo hero: ca cum, khong ten khung
    return f'''
        <div class="caf-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="caf-faq-btn" type="button" onclick="cafFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="caf-faq-q" itemprop="name">How long is the immigration queue at Cam Ranh Airport in {d["month_label"]}?</h3>
            <span class="caf-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="caf-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, the last passengers off a flight landing in the busiest hours need an estimated <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> from touchdown to leaving immigration. At quieter hours it is {rng(quiet["range"])} minutes.</p>
            <p style="margin-top:10px !important;">With Fast Track it is under {ftcap(ft)} minutes even at the busiest hours, and about {ft_of("quick", ft)} when the hall is lighter. <a href="#wait-times" style="color:#C9A84C; font-weight:600; text-decoration:none;">See the estimate for your landing time</a> (updated {fmt_date(updated)}).</p>
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
    main(sys.argv[1] if len(sys.argv) > 1 else "caf-wait.json",
         date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today())
