"""Render 3 vùng từ {site}-wait-YYYY-MM.json."""
import json, os, sys
from datetime import date

MONTHS = ["January","February","March","April","May","June","July",
          "August","September","October","November","December"]

fmt_date = lambda d: f"{d.day} {MONTHS[d.month - 1]} {d.year}"
# window có thể gồm nhiều cụm rời, nối bằng '|'. Một cụm thì kết quả y hệt bản cũ.
dash  = lambda w: " and ".join("&ndash;".join(r.split("-")) for r in w.split("|"))
words = lambda w: ", or between ".join(" and ".join(r.split("-")) for r in w.split("|"))
# Mot dau thay vi hai khi hai dau bang nhau. O HAN khung 00:00-06:00 ra 35-35 vi luoi
# 22 kich ban deu cho cung mot so -- "35&ndash;35 min" doc nhu loi dinh dang, khong nhu
# ket qua chac chan. Ba site kia chua tung cham truong hop nay nen khong lo ra.
rng   = lambda p: (f"{p[0]}" if p[0] == p[1] else f"{p[0]}&ndash;{p[1]}")
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
    """Khac bon site kia: KHONG in the tieu de va KHONG in doan `basis`.

    1. Tieu de the ("Why Choose Fast Track?") la phan TINH nam ngoai vung -- chu site
       chot 05/10/2026 giu nguyen nhu trang goc. Xem SKILL.md muc 3b.
    2b. HAI DONG PHU CUA HAI HANG THOI GIAN PHAI SONG SONG NHAU.
       hang QUEUE      -> "Through immigration in the busiest hours - {thang} estimate"
       hang FAST TRACK -> "Through immigration with our service"
       Ca the nay ton tai de nguoi ta so 69-91 voi duoi 15. Phep so chi dung neu hai
       con so cung do MOT thu. Ban cu ghi "{thang} estimate - passengers landing in the
       busiest hours": no tra loi AI va KHI NAO, khong tra loi "69-91 phut cua CAI GI",
       nen doc canh dong duoi (co tra loi) thi hai hang nhu do hai thu khac nhau.
       Chu "Through immigration" lap lai o hai dong la CO Y -- chinh no lam phep so
       doc duoc trong mot nhip mat. Dung "gon" bang cach bo mot trong hai.
       Luu y nhan "QUEUE" hep hon con so that (69-91 da gom xuong may bay va di bo),
       nen dong phu PHAI noi "through immigration" de bu lai.

    2. Bo doan `basis`: dung mot minh ngay duoi tieu de no doc nhu loi dan khong co
       ngu canh -- chua noi so nao da giai thich cach tinh so. Gop phan can thiet
       (thang + chu "estimate") vao dong phu cua hang QUEUE, ngay canh con so no
       mo ta. The ngan di ba dong.
       `d["basis"]` van nam trong JSON de ghi lai phuong phap cua thang, va ban day
       du cua no la cau "How we estimate" ngay duoi bang -- KHONG mat thong tin.
    """
    h = d["headline"]
    # HAN: cum busy TACH BACH khoi cac bac duoi (san 69 > tran Moderate 65) nen
    # cong bo CA CUM (h["busy"]) theo chuan SAF/CAF. Khac DAF -- o DAD cum busy co mot
    # khung dao dong manh keo san xuong duoi ca khung Moderate nen DAF phai dung h["peak"].
    #
    # O HAN cum busy keo LIEN TUC 13:00-24:00, tuc 11 tieng va 72/120 chuyen. Day la
    # dac diem nhan dang cua Noi Bai: no KHONG co dinh, no co mot nua ngay deu bang nhau.
    # Dung "sua" cho giong site khac bang cach keo nguong len de bot khung Busy --
    # bang se dep hon ma sai: khach ha luc 21:00 that su cho ngang khach ha luc 14:00.
    busy = h["busy"]
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
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[haf_price service="fast_track"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

      </div>

      <p style="font-family:'DM Sans',sans-serif; font-size:0.74rem; color:#5A5A72; margin:0; padding:0;">Updated {fmt_date(updated)} &middot; <a href="#wait-times" style="color:#8B6914; font-weight:600; text-decoration:none; border-bottom:1px solid rgba(201,168,76,0.4);">Hour by hour</a></p>
'''


def render_section(d, updated):
    """Doan dan cua HAF khac bon site kia o HAI cho (chot 05/10/2026):

    1. `d["basis"]` la MENH DE MO DAU, chen ngay sau "In {thang}," va TRUOC con so.
       Chu site chot 05/10/2026: khach phai biet day la can cu uoc tinh TRUOC khi doc
       con so, khong phai sau. Dat sau (dang gach dai o cuoi cau) thi nguoi doc da
       kip tin "69-91 minutes" la so DO duoc roi moi thay lo i giai thich.
       => viet thuong o chu dau, KHONG cham cuoi, KHONG nhac lai ten thang.
          Mau dat: "based on flight schedules and official airport data from 2025-2026"
       Dung chung cho CA doan dan LAN FAQ. The hero khong in no nua.

    2. Fast Track chi neu MOT nguong: "under {tran} minutes at any hour".
       Ban cu neu hai con so ("about 10 ... and under 15 even at the busiest hours")
       -- dai hon ma khong ro hon, va dat canh dai 69-91 thi hai con so lam loang
       chinh diem manh. Mot tran dung cho moi khung la cau ngan nhat ma van dung.
    """
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
        <div class="haf-wt-row haf-wt-none" role="row">
          <div class="haf-wt-band" role="rowheader"><strong>{label}</strong><span class="haf-wt-flights">{tag}</span></div>
          <div class="haf-wt-queue" role="cell" data-label="Standard queue"><span class="haf-wt-num" style="color:#8a9ab0 !important;">&mdash;</span><span class="haf-wt-sub">{d["notes"]["empty_band_note"]}</span></div>
          <div class="haf-wt-cell haf-wt-ft" role="cell" data-label="With Fast Track">&mdash;</div>
        </div>''')
            continue
        n = b["flights"]
        width = max(10, round(100 * b["standard"][1] / top))
        rows.append(f'''
        <div class="haf-wt-row haf-wt-{lvl}" role="row">
          <div class="haf-wt-band" role="rowheader"><strong>{label}</strong><span class="haf-wt-flights">{n} international arrival{"s" if n != 1 else ""} &middot; {tag}</span></div>
          <div class="haf-wt-queue" role="cell" data-label="Standard queue">
            <span class="haf-wt-num" style="color:{color} !important;">{rng(b["standard"])} min</span>
            <span class="haf-wt-track" aria-hidden="true"><span class="haf-wt-fill" style="width:{width}% !important; background:{color} !important;"></span></span>
          </div>
          <div class="haf-wt-cell haf-wt-ft" role="cell" data-label="With Fast Track">{ftcell(ft_of(b.get("tier","quick"), ft))} min</div>
        </div>''')
    return f'''
    <div class="haf-wt-head">
      <span class="haf-wt-eyebrow">Immigration wait times &middot; {d["month_label"]} &middot; updated {fmt_date(updated)}</span>
      <h2 id="haf-h2-wait">How Long Is the Immigration Queue at Noi Bai Airport in {d["month_label"]}?</h2>
      <div aria-hidden="true" style="width:44px; height:3px; background:#C9A84C; margin:14px auto 20px;"></div>
      <p class="haf-wt-lead">In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Noi Bai International Airport (HAN) could spend <strong>{rng(busy["range"])} minutes</strong> completing immigration procedures. With Fast Track, this time is under {ftcap(ft)} minutes at any hour.</p>
    </div>

    <div class="haf-wt-table" role="table" aria-label="Estimated time from landing to leaving immigration at Noi Bai Airport by arrival time, {d["month_label"]}">
      <div class="haf-wt-row haf-wt-header" role="row">
        <div role="columnheader">Landing time</div>
        <div role="columnheader">Standard queue &mdash; last passengers</div>
        <div role="columnheader">With Fast Track</div>
      </div>{"".join(rows)}
    </div>

    <div class="haf-wt-cards">
      <div class="haf-wt-card haf-wt-card-gold">
        <h3>When Fast Track matters most</h3>
        <p>Flights landing {dash(busy["window"])}, when arrivals from {cities(d, busy["window"])} land minutes apart. Land {dash(quiet["window"])} &mdash; {calm_line(quiet)}</p>
      </div>
      <div class="haf-wt-card">
        <h3>{d["month_label"]} notes</h3>
        <p>{d["notes"]["month_notes"]}</p>
      </div>
    </div>

    <p class="haf-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a representative {d["month_label"].split()[0]} day, counting deplaning and the walk to the hall. Checked three ways: against the daily immigration volume Noi Bai publishes, against the measured time a manual counter takes per passenger, and against the capacity of the arrivals hall itself.</p>

    <div class="haf-wt-cta">
      <button type="button" class="haf-pick-btn haf-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="haf-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
    </div>
'''


def render_faq(d, updated, faq_id="haf-faq-a12"):
    """Khoi de bi AI trich nguyen van nhat tren ca trang -> phai TU DUNG MOT MINH.

    Nen no nhac lai viec day la UOC TINH -- dung chung menh de `d["basis"]` voi doan
    dan (mot nguon duy nhat, va menh de 12 tu lap lai thi khong chuong tai).
    KHAC doan dan o mot cho: FAQ GIU con so khung vang. Doan dan la tieu diem nen chi
    neu con so te nhat; FAQ la cau tra loi day du nen phai co ca hai dau dai.
    """
    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = h["busy"]   # FAQ bam theo hero: ca cum, khong ten khung
    return f'''
        <div class="haf-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="haf-faq-btn" type="button" onclick="hafFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="haf-faq-q" itemprop="name">How long is the immigration queue at Noi Bai Airport in {d["month_label"]}?</h3>
            <span class="haf-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="haf-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Noi Bai Airport could spend <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> completing immigration procedures, and {rng(quiet["range"])} minutes at quieter hours.</p>
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
    main(sys.argv[1] if len(sys.argv) > 1 else "haf-wait.json",
         date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today())
