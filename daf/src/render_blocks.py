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
# Fast Track doi theo bac: khung thuong ~10 phut, khung cao diem 10-15.
ft_of = lambda tier, c: (c["peak"] if tier == "busy" else c["base"]) if isinstance(c, dict) else c
# Bac cao diem hien HAI kieu, co y (chot 04/10/2026, hoc tu SAF):
#   o BANG   -> "10-15 min": cot hep, va bang la cho tra cuu theo khung gio.
#   HERO+van xuoi -> "Under 15": hero da co MOT dai so o dong Queue; them dai thu hai
#   ngay duoi lam yeu chinh cho tuong phan "dai va bap benh" vs "ngan va chac".
#   "Under 15" la tran, dung o MOI khung (quiet 10 < 15), khop dong phu
#   "every flight, every hour".
ftcell = lambda v: (f"{v[0]}&ndash;{v[1]}" if isinstance(v, (list, tuple)) else f"~{v}")
ftword = lambda v: (f"Under {v[1]}" if isinstance(v, (list, tuple)) else f"~{v}")
ftcap  = lambda c: (c["peak"][1] if isinstance(c.get("peak"), (list, tuple)) else c["peak"]) if isinstance(c, dict) else c
# Khung "de tho nhat" cua DAD van la 40-45 phut. Cau cu "you may not need us, and we
# will say so." vua sai vua ban re dich vu -> CHU SITE CAM dung lai (04/10/2026),
# o MOI site, moi thang. Khong con nhanh dieu kien: mot cau duy nhat, luon dung.
calm_line = lambda q: "the line is shorter, though rarely short."


def level(b):
    # BA bac, BA mau, thang VANG -> CAM DAT -> DO CHOI.
    # Quy tac: do CHOI phai TANG theo muc do, khong chi doi sac. Ban truoc dung cam
    # #C2410C cho Moderate va do sam #8B1A1A cho Busy -> cam bao hoa hon nen HUT MAT
    # HON ca khung cao diem, nguoc han y nghia. Gio Busy la mau choi nhat bang.
    # Tuong phan tren nen trang: vang 5,1:1 · cam dat 5,3:1 · do 5,5:1 -- deu dat WCAG AA.
    # Co y KHONG dung xanh la cho bac nhe vi #1a7a42 la mau cot Fast Track.
    return {"none":     ("none",  "#8a9ab0", "No regular international arrivals"),
            "quick":    ("light", "#8B6914", "Lighter"),
            "moderate": ("light", "#A8541A", "Moderate"),
            "busy":     ("busy",  "#C9281C", "Busy")}[b.get("tier", "quick")]


def cities(d, window):
    """Ten thanh pho trong `window`, xep theo SO CHUYEN (khong theo gio den som nhat).

    Cum busy cua DAD co 26 chuyen. Lay "bon cai dau theo gio" ra
    "Busan, Seoul, Kuala Lumpur va Singapore" -- ma Singapore chi 1 chuyen, con
    Bangkok 3 chuyen thi bi bo. Xep theo so chuyen ra dung thi truong, va khong
    nhay lung tung moi thang chi vi mot chuyen doi gio 5 phut. Hoa -> chuyen HA
    SOM HON dung truoc.
    """
    spans = [tuple(int(x[:2]) for x in r.split("-")) for r in window.split("|")]
    n, first = {}, {}
    for f in d["sample_flights"]:
        if any(a <= int(f["time"][:2]) < z for a, z in spans):
            c = d["cities"].get(f["from"], f["from"])
            n[c] = n.get(c, 0) + 1
            first.setdefault(c, f["time"])
    out = sorted(n, key=lambda c: (-n[c], first[c]))[:4]   # toi da 4 ten
    return ", ".join(out[:-1]) + " and " + out[-1] if len(out) > 1 else "".join(out)


def render_hero(d, updated):
    """Khac ban dau tien o HAI cho (chot 05/10/2026, ap chung ca 5 site):

    1. KHONG in the tieu de. Tieu de la phan TINH nam NGOAI vung, khong mang ten thang.
       Vung wait-hero bat dau ngay SAU the tieu de.
    2. KHONG in doan `basis`. Dung mot minh ngay duoi tieu de, no doc nhu loi dan khong
       co ngu canh -- giai thich cach tinh truoc khi nguoi doc thay con so nao.
       `basis` chuyen xuong DOAN DAN duoi H2 (xem render_section).

    Dong phu cua hang QUEUE va hang FAST TRACK PHAI SONG SONG nhau:
        QUEUE      -> "Through immigration in the busiest hours - {thang} estimate"
        FAST TRACK -> "Through immigration with our service"
    Ca the nay ton tai de nguoi ta so hai con so; phep so chi dung neu chung cung do MOT
    thu. Chu "Through immigration" lap o hai dong la CO Y -- dung "gon" bang cach bo mot.
    """

    h = d["headline"]
    # Con so: khung BAN NHAT (h["peak"]). Text: KHONG ghi ten khung ra trang.
    # Khac SAF, va co ly do: cum busy cua DAD gom mot khung DAO DONG MANH
    # (10:00-13:00, trung vi 50 nhung kich ban xau 77) nen bien duoi cua ca cum
    # tut xuong 50 -- thap hon ca mot khung Moderate (52-62) ngay duoi bang.
    # Chu site chot 04/10/2026: lay khung ban nhat, giu cach noi chung.
    busy = h.get("peak") or h["busy"]
    return f'''


      <div style="display: flex; flex-direction: column; gap: 0;">

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Queue</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#C9281C; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{rng(busy["range"])} min</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Through immigration in the busiest hours &middot; {d["month_label"]} estimate</span>
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
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[daf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; color:#5A5A72; margin:0; padding:0;">Updated {fmt_date(updated)} &middot; <a href="#wait-times" style="color:#8B6914; font-weight:600; text-decoration:none; border-bottom:1px solid rgba(201,168,76,0.4);">Hour by hour</a></p>
'''


def render_section(d, updated):
    """`d["basis"]` la MENH DE MO DAU, chen ngay sau "In {thang}," va TRUOC con so.

    Khach phai biet day la can cu uoc tinh TRUOC khi doc con so. Dat sau (kieu gach dai
    cuoi cau) thi nguoi doc da kip tin con so la so DO duoc roi moi thay loi giai thich.
    => `basis` viet thuong o chu dau, KHONG cham cuoi, KHONG nhac lai ten thang.

    Fast Track chi neu MOT nguong ("under N minutes at any hour"). Neu hai con so thi dai
    hon ma khong ro hon, va dat canh dai hang thuong thi chung lam loang chinh diem manh.
    Bang ben duoi van hien day du cac bac -- do moi la cho phan bac.
    """

    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    peak = h.get("peak") or h["busy"]   # doan dan: con so cua khung ban nhat
    busy = h["busy"]                     # the vang: ca cum, va the vang DUOC ghi khung gio
    bands = d["bands"]
    top = max(b["standard"][1] for b in bands if b["standard"])
    rows = []
    for b in bands:
        lvl, color, tag = level(b)
        label = dash(b["band"])
        if b["standard"] is None:
            rows.append(f'''
        <div class="daf-wt-row daf-wt-none" role="row">
          <div class="daf-wt-band" role="rowheader"><strong>{label}</strong><span class="daf-wt-flights">{tag}</span></div>
          <div class="daf-wt-queue" role="cell" data-label="Standard queue"><span class="daf-wt-num" style="color:#8a9ab0 !important;">&mdash;</span><span class="daf-wt-sub">{d["notes"]["empty_band_note"]}</span></div>
          <div class="daf-wt-cell daf-wt-ft" role="cell" data-label="With Fast Track">&mdash;</div>
        </div>''')
            continue
        n = b["flights"]
        width = max(10, round(100 * b["standard"][1] / top))
        rows.append(f'''
        <div class="daf-wt-row daf-wt-{lvl}" role="row">
          <div class="daf-wt-band" role="rowheader"><strong>{label}</strong><span class="daf-wt-flights">{n} international arrival{"s" if n != 1 else ""} &middot; {tag}</span></div>
          <div class="daf-wt-queue" role="cell" data-label="Standard queue">
            <span class="daf-wt-num" style="color:{color} !important;">{rng(b["standard"])} min</span>
            <span class="daf-wt-track" aria-hidden="true"><span class="daf-wt-fill" style="width:{width}% !important; background:{color} !important;"></span></span>
          </div>
          <div class="daf-wt-cell daf-wt-ft" role="cell" data-label="With Fast Track">{ftcell(ft_of(b.get("tier","quick"), ft))} min</div>
        </div>''')
    return f'''
    <div class="daf-wt-head">
      <span class="daf-wt-eyebrow">Immigration wait times &middot; {d["month_label"]} &middot; updated {fmt_date(updated)}</span>
      <h2 id="daf-h2-wait">How Long Is the Immigration Queue at Da Nang Airport in {d["month_label"]}?</h2>
      <div aria-hidden="true" style="width:44px; height:3px; background:#C9A84C; margin:14px auto 20px;"></div>
      <p class="daf-wt-lead">In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Da Nang International Airport (DAD) could spend <strong>{rng(peak["range"])} minutes</strong> completing immigration procedures. With Fast Track, this time is under {ftcap(ft)} minutes at any hour.</p>
    </div>

    <div class="daf-wt-table" role="table" aria-label="Estimated time from landing to leaving immigration at Da Nang Airport by arrival time, {d["month_label"]}">
      <div class="daf-wt-row daf-wt-header" role="row">
        <div role="columnheader">Landing time</div>
        <div role="columnheader">Standard queue &mdash; last passengers</div>
        <div role="columnheader">With Fast Track</div>
      </div>{"".join(rows)}
    </div>

    <div class="daf-wt-cards">
      <div class="daf-wt-card daf-wt-card-gold">
        <h3>When Fast Track matters most</h3>
        <p>Flights landing {dash(busy["window"])}, when arrivals from {cities(d, busy["window"])} land minutes apart. Land {dash(quiet["window"])} &mdash; {calm_line(quiet)}</p>
      </div>
      <div class="daf-wt-card">
        <h3>{d["month_label"]} notes</h3>
        <p>{d["notes"]["month_notes"]}</p>
      </div>
    </div>

    <p class="daf-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a typical {d["month_label"].split()[0]} weekday, counting deplaning and the walk to the hall, and checked against the waits travellers report.</p>

    <div class="daf-wt-cta">
      <button type="button" class="daf-pick-btn daf-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="daf-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
    </div>
'''


def render_faq(d, updated, faq_id="daf-faq-a12"):
    """Khoi de bi AI trich nguyen van nhat -> phai TU DUNG MOT MINH.

    Dung chung menh de `d["basis"]` voi doan dan. KHAC doan dan dung mot cho: FAQ GIU
    con so khung vang, vi no la cau tra loi day du; doan dan la tieu diem nen chi neu
    con so te nhat.
    """

    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = h.get("peak") or h["busy"]   # FAQ bam theo hero
    return f'''
        <div class="daf-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="daf-faq-btn" type="button" onclick="dafFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="daf-faq-q" itemprop="name">How long is the immigration queue at Da Nang Airport in {d["month_label"]}?</h3>
            <span class="daf-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="daf-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Da Nang Airport could spend <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> completing immigration procedures, and {rng(quiet["range"])} minutes at quieter hours.</p>
            <p style="margin-top:10px !important;">With Fast Track, this time is under {ftcap(ft)} minutes at any hour. <a href="#wait-times" style="color:#C9A84C; font-weight:600; text-decoration:none;">See the estimate for your landing time</a> (updated {fmt_date(updated)}).</p>
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
    main(sys.argv[1] if len(sys.argv) > 1 else "daf-wait.json",
         date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today())
