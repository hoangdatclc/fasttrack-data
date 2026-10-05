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


def level(b):
    # BA bac, BA mau, thang VANG -> CAM DAT -> DO CHOI. Dong bo voi DAF 02/10/2026.
    # Quy tac: do CHOI phai TANG theo muc do, khong chi doi sac.
    #   Ban cu dung CUNG mot mau vang cho quick va moderate -> ba nhan ma hai mau,
    #   doc bang khong phan biet duoc hai bac. Va #8B1A1A (do sam) cho Busy lai KHONG
    #   choi hon vang bao nhieu, nen bac nang nhat khong noi len.
    # Tuong phan tren nen trang: vang 5,1:1 - cam dat 5,3:1 - do 5,8:1, deu dat WCAG AA.
    # Co y KHONG dung xanh la cho bac nhe vi #1a7a42 la mau cot Fast Track.
    return {"none":     ("none",  "#8a9ab0", "No regular international arrivals"),
            "quick":    ("light", "#8B6914", "Usually quick"),
            "moderate": ("light", "#A8541A", "Moderate"),
            "busy":     ("busy",  "#C1272D", "Busy")}[b.get("tier", "quick")]


def cities(d, window):
    spans = [tuple(int(x[:2]) for x in r.split("-")) for r in window.split("|")]
    out = []
    for f in d["sample_flights"]:
        if any(a <= int(f["time"][:2]) < z for a, z in spans):
            c = d["cities"].get(f["from"], f["from"])
            if c not in out:
                out.append(c)
    out = out[:4]                                      # tối đa 4 tên, dài hơn là lê thê
    return ", ".join(out[:-1]) + " and " + out[-1] if len(out) > 1 else "".join(out)


def render_hero(d, updated):
    h = d["headline"]
    busy = h.get("peak") or h["busy"]   # hero: chi khung te nhat
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
        PQC Immigration &mdash; {d["month_label"]}
      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; line-height:1.55; color:#5A5A72; margin:0; padding:0 0 14px; border-bottom:1px solid #E8E4DE;">{d["basis"]}</p>

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Queue</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#C9281C; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{rng(busy["range"])} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Last passengers off a flight landing {dash(busy["window"])} &mdash; from touchdown to leaving immigration</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Fast Track</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">~{h["fast_track"]} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Through immigration with our service &mdash; every flight, every hour</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[paf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; color:#5A5A72; margin:0; padding:0;">Updated {fmt_date(updated)} &middot; <a href="#wait-times" style="color:#8B6914; font-weight:600; text-decoration:none; border-bottom:1px solid rgba(201,168,76,0.4);">Hour by hour</a></p>
'''


def render_section(d, updated):
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    peak = h.get("peak") or h["busy"]   # doan dan: khung te nhat
    busy = h["busy"]                     # the vang: toan bo cum cao diem
    bands = d["bands"]
    top = max(b["standard"][1] for b in bands if b["standard"])
    rows = []
    for b in bands:
        lvl, color, tag = level(b)
        label = dash(b["band"])
        if b["standard"] is None:
            rows.append(f'''
        <div class="paf-wt-row paf-wt-none" role="row">
          <div class="paf-wt-band" role="rowheader"><strong>{label}</strong><span class="paf-wt-flights">{tag}</span></div>
          <div class="paf-wt-queue" role="cell" data-label="Standard queue"><span class="paf-wt-num" style="color:#8a9ab0 !important;">&mdash;</span><span class="paf-wt-sub">{d["notes"]["empty_band_note"]}</span></div>
          <div class="paf-wt-cell paf-wt-ft" role="cell" data-label="With Fast Track">&mdash;</div>
        </div>''')
            continue
        n = b["flights"]
        width = max(10, round(100 * b["standard"][1] / top))
        rows.append(f'''
        <div class="paf-wt-row paf-wt-{lvl}" role="row">
          <div class="paf-wt-band" role="rowheader"><strong>{label}</strong><span class="paf-wt-flights">{n} international arrival{"s" if n != 1 else ""} &middot; {tag}</span></div>
          <div class="paf-wt-queue" role="cell" data-label="Standard queue">
            <span class="paf-wt-num" style="color:{color} !important;">{rng(b["standard"])} min</span>
            <span class="paf-wt-track" aria-hidden="true"><span class="paf-wt-fill" style="width:{width}% !important; background:{color} !important;"></span></span>
          </div>
          <div class="paf-wt-cell paf-wt-ft" role="cell" data-label="With Fast Track">~{ft} min</div>
        </div>''')
    return f'''
    <div class="paf-wt-head">
      <span class="paf-wt-eyebrow">Immigration wait times &middot; {d["month_label"]} &middot; updated {fmt_date(updated)}</span>
      <h2 id="paf-h2-wait">How Long Is the Immigration Queue at Phu Quoc Airport in {d["month_label"]}?</h2>
      <div aria-hidden="true" style="width:44px; height:3px; background:#C9A84C; margin:14px auto 20px;"></div>
      <p class="paf-wt-lead">In {d["month_label"]}, the last passengers off a flight landing between {words(peak["window"])} need an estimated <strong>{rng(peak["range"])} minutes</strong> from touchdown to leaving immigration at Phu Quoc International Airport (PQC). Flights landing {dash(quiet["window"])} clear in {rng(quiet["range"])} minutes. With Fast Track it is about {ft} minutes, whenever you land.</p>
    </div>

    <div class="paf-wt-table" role="table" aria-label="Estimated time from landing to leaving immigration at Phu Quoc Airport by arrival time, {d["month_label"]}">
      <div class="paf-wt-row paf-wt-header" role="row">
        <div role="columnheader">Landing time</div>
        <div role="columnheader">Standard queue &mdash; last passengers</div>
        <div role="columnheader">With Fast Track</div>
      </div>{"".join(rows)}
    </div>

    <div class="paf-wt-cards">
      <div class="paf-wt-card paf-wt-card-gold">
        <h3>When Fast Track matters most</h3>
        <p>Flights landing {dash(busy["window"])}, when arrivals from {cities(d, busy["window"])} land minutes apart. Land {dash(quiet["window"])} &mdash; you may not need us, and we will say so.</p>
      </div>
      <div class="paf-wt-card">
        <h3>{d["month_label"]} notes</h3>
        <p>{d["notes"]["month_notes"]}</p>
      </div>
    </div>

    <p class="paf-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a typical {d["month_label"].split()[0]} weekday, counting deplaning and the walk to the hall, and checked against the waits travellers report here. Estimates, not measurements &mdash; season by season in our <a href="{d["links"]["guide"]}" style="color:#8B6914 !important; font-weight:600 !important; border-bottom:1px solid rgba(201,168,76,0.4) !important;">Phu Quoc Airport wait-time guide</a>.</p>

    <div class="paf-wt-cta">
      <button type="button" class="paf-pick-btn paf-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="paf-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
      <a class="paf-wt-link" href="https://wa.me/84368938081?text=Hi%2C%20I%27d%20like%20to%20check%20the%20immigration%20queue%20for%20my%20flight%20to%20Phu%20Quoc." target="_blank" rel="noopener">Send us your flight number &mdash; we will tell you if you need it</a>
    </div>
'''


def render_faq(d, updated, faq_id="paf-faq-a12"):
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = h.get("peak") or h["busy"]   # FAQ bam theo hero
    return f'''
        <div class="paf-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="paf-faq-btn" type="button" onclick="pafFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="paf-faq-q" itemprop="name">How long is the immigration queue at Phu Quoc Airport in {d["month_label"]}?</h3>
            <span class="paf-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="paf-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, the last passengers off a flight landing between {words(busy["window"])} need an estimated <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> from touchdown to leaving immigration. Flights landing {dash(quiet["window"])} clear in {rng(quiet["range"])} minutes.</p>
            <p style="margin-top:10px !important;">With Fast Track it is about {ft} minutes at any hour. <a href="#wait-times" style="color:#C9A84C; font-weight:600; text-decoration:none;">See the estimate for your landing time</a> (updated {fmt_date(updated)}).</p>
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
    main(sys.argv[1] if len(sys.argv) > 1 else "paf-wait.json",
         date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today())
