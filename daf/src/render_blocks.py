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


def ft_floor_cap(ft):
    """San va tran cua Fast Track, nhan ca hai hinh dang cau hinh dang dung:

      hai bac  {"base": 10, "peak": [10, 15]}            -> (10, 15)   PAF/DAF/CAF/HAF
      ba bac   {"quick": 10, "moderate": 15, "busy": 20} -> (10, 20)   SAF
      mot so   10                                        -> (10, 10)

    Mot ham dung chung ca 5 site de the hero khong lech nhau khi mot site doi so bac.
    """
    if isinstance(ft, dict):
        if "base" in ft:
            peak = ft.get("peak", ft["base"])
            return ft["base"], (peak[1] if isinstance(peak, (list, tuple)) else peak)
        vals = [v for v in ft.values() if isinstance(v, (int, float))]
        return min(vals), max(vals)
    return ft, ft


def headline_range(d, min_gap=10):
    """Dai hang thuong ma trang cong bo: DINH va SO LON THU NHI TRONG BANG.

    Chu site chot 06/10/2026 (ban thu tu, va la ban dung).

        can tren = so LON NHAT trong bang
        can duoi = so LON NHAT con lai ma NHO HON can tren it nhat {min_gap} phut

    Xet TAT CA cac so hien trong cot "Standard queue" -- ca can duoi LAN can tren cua
    moi khung, khong chi tran. Nho vay can duoi luon la mot con so khach DOC DUOC
    trong bang ngay ben duoi, do lai duoc.

    Thang 10/2026:
      PQC  moi so 94 69 59 56 48 46 44 42 38 37        -> dinh 94, lon nhat <=84 la 69  -> 69-94
      DAD  moi so 79 77 68 66 62 60 52 50 49 45 44 40  -> dinh 79, lon nhat <=69 la 68  -> 68-79
      CXR  moi so 83 77 71 70 64 54 50 44 43 30 28     -> dinh 83, lon nhat <=73 la 71  -> 71-83

    BA BAN TRUOC DA BO, DUNG QUAY LAI:
      1. nguyen dai cua khung ban nhat -- can duoi la SAN cua chinh khung do, chi noi
         "khach may man nhat trong khung te nhat", khong noi gi ve ca ngay.
      2. ghep hai TRAN cao nhat ca ngay -- o DAD hai khung ban nhat co tran gan bang
         nhau (77 va 79) nen dai co lai con 2 phut, doc nhu so DO chinh xac.
      3. tran bac Moderate -> tran bac Busy -- o CXR cac khung Moderate nhe that
         (tran 50) nen can duoi tut qua sau, tiet kiem roi xuong duoi 1 gio.
    Ban thu tu bo han khai niem "bac" va "tran": chi lay hai con so lon nhat trong
    bang con cach nhau du xa. On dinh voi moi hinh dang ngay.

    CONG CHAN: khong tim duoc so nao nho hon can tren >= {min_gap} phut -> DUNG, khong
    giao trang. Ngay hom do phang that; mot dai hep se noi doi ve do chac chan cua
    con so.

    Khong can loc theo bac: can duoi la so LON NHAT du dieu kien, nen no khong the
    roi vao mot khung nhe hon trong khi con mot khung ban hon dang o giua.
    """
    nums = sorted({v for b in d["bands"] if b.get("standard") for v in b["standard"]},
                  reverse=True)
    if not nums:
        raise SystemExit("KHONG CO KHUNG NAO CO SO -- khong dung duoc dai cong bo.")
    hi = nums[0]
    lo = next((v for v in nums if v <= hi - min_gap), None)
    if lo is None:
        raise SystemExit(
            f"DAI CONG BO QUA HEP: dinh la {hi}, khong so nao trong bang nho hon no "
            f">= {min_gap} phut (cac so: {nums}). Ngay nay phang that -- mot dai hep se "
            "noi doi ve do chac chan cua con so. Hoi chu site truoc khi giao.")
    return [lo, hi]


def saved(busy, ft):
    """Muc tiet kiem: dai hang thuong TRU Fast Track.

    CA HAI DAU deu tru TRAN Fast Track, khong phai san (chot 06/10/2026):
        can duoi = dai THAP - tran FT     can tren = dai CAO - tran FT
    Ly do: the hero chi cong bo MOT con so Fast Track -- "under {tran} minutes" o
    dong 2. Neu can tren tru SAN (10) thi khach lay giay but tinh lai theo dong phu
    se ra con so khac cai in to phia tren, khong kiem chung duoc. Bon site kia van
    tru san o can tren (luat 9); PAF di rieng vi bac nua tieng lam cho chenh lech
    do nhin thay ro. Thang 10/2026 hai cach ra y het nhau (1-1.5 hours).

    DAF IN THEO GIO, BAC NUA TIENG (chu site chot 06/10/2026, theo sau PAF):
    1 - 1.5 - 2 - 2.5 - 3 ... Lam tron ve bac GAN NHAT (62 phut -> 1; 64 phut -> 1),
    khong phai lam tron len. HAF/SAF/CAF van in phut hoac gio tron -- xem luat 9.

    CONG CHAN 1: can duoi phai >= 15 phut (so SUY RA, khong co trong du lieu).
    CONG CHAN 2: sau khi lam tron, can duoi phai >= 1.0 gio. Chu site muon "toi thieu
    la 1 gio", nhung 1 gio phai la KET QUA lam tron, khong phai mot cai san ep vao.
    Lam tron ve bac gan nhat chi ra >= 1.0 khi can duoi that >= 45 phut. Thang nao
    tut xuong duoi 45 phut ma van in "1 hour" la trang noi qua >25% -- dung luon,
    hoi chu site xem chuyen ve phut hay xem lai mo hinh.
    """
    base, cap = ft_floor_cap(ft)
    lo, hi = busy["range"][0] - cap, busy["range"][1] - cap
    if lo < 15:
        raise SystemExit(
            f"MUC TIET KIEM VO LY: {lo}-{hi} phut. Can duoi phai >= 15 phut. "
            "Khung ban da tut xuong gan tran Fast Track -- xem lai mo hinh, "
            "dung dang the hero voi con so nay.")
    half = lambda m: round(m / 30.0) / 2.0        # bac nua tieng, lam tron GAN NHAT
    h_lo, h_hi = half(lo), half(hi)
    fmt = lambda v: (f"{v:.0f}" if v == int(v) else f"{v:.1f}")
    if h_lo < 1.0:
        # Can duoi tut xuong duoi 1 gio. Ep no thanh "1 hour" la noi qua (CXR thang
        # 10/2026: can duoi that 35 phut -> "1 hour" la noi qua 71%), nen KHONG ep.
        # Chu site chot 06/10/2026: chuyen sang dang TRAN -- "Up to ~{tran} hour".
        # Dang nay chi hua CAN TREN nen khong the noi qua o can duoi, van giu duoc don
        # vi gio va nguong toi thieu 1 gio. Danh doi: the doi tu mot DAI sang mot TRAN.
        if h_hi < 1.0:
            raise SystemExit(
                f"KHONG IN DUOC THEO GIO: tiet kiem that la {lo}-{hi} phut, ca hai can "
                f"deu tron ve duoi 1 gio ({h_lo} va {h_hi}). Den dang 'Up to' cung khong "
                "cuu duoc. Dung lai -- hoi chu site: chuyen the hero ve phut thang nay, "
                "hay xem lai mo hinh?")
        return f"Up to ~{fmt(h_hi)} hour" + ("" if h_hi == 1.0 else "s")
    if h_lo == h_hi:
        # Mot gia tri thi phai co dau xap xi: "1 hour" tran doc nhu con so DO duoc,
        # trong khi no la hai can khac nhau (vi du 51 va 64 phut) cung tron ve 1.0.
        # Dung dau "~" cho khop cot Fast Track trong bang ("~10 min").
        return f"~{fmt(h_lo)} hour" + ("" if h_lo == 1.0 else "s")
    return f"{fmt(h_lo)}&ndash;{fmt(h_hi)} hours"


def render_hero(d, updated):
    """The hero: BA HANG LA BA LY DO -- Save / From / 24-7. Chot 05/10/2026, chung ca 5 site.

    Ban truoc la the SO SANH (Queue / Fast Track / From). Bo vi no tieu HAI trong ba
    hang cho CUNG MOT THU (thoi gian, do hai lan), nen the chi con hai ly do, va hang
    24/7 khong co cho -- tren mot cai the ten la "Why Choose ... Fast Track?" thi bot
    mot ly do la bot dung thu no di ban.

    1. Tieu de the la phan TINH, nam NGOAI vung wait-hero. render_hero() KHONG sinh
       tieu de; no bat dau thang bang ba hang chi so.

    2. Hang SAVE chi in MOT con so -- muc tiet kiem -- de khach khong phai tru nham.
       Nhung mot con so tiet kiem dung tran trui thi khach khong biet no tru tu dau,
       nen dong phu PHAI noi ca HAI dau. Cau do CHU SITE viet (ban tieng Viet:
       "Hang cho nhap canh tieu chuan uoc tinh co the len toi X phut. Fast Track giup
       ban hoan thanh duoi Y phut."):

         The standard immigration queue is estimated to reach {X} minutes.
         Fast Track gets you through in under {Y} minutes.

       Hai dong, ngat bang <br>, moi dong mot dau cua phep tru.
       DO DAI LA RANG BUOC CUNG (chot 06/10/2026): moi dong phai vua MOT DONG o
       ca 1440px (cot 262px) lan 390px (cot 240px). Ban cu la mot cau day du
       ("The standard immigration queue is estimated to reach X minutes.") --
       no vo thanh 4 dong, va cum &nbsp; lam dong 2 de lai mot khoang trong lon
       ben phai, trong nhu loi hien thi. Da do bang Playwright: chi dang nhan:gia-tri
       moi vua mot dong. "within 15 minutes" va "in 10-15 minutes" DEU KHONG cuu
       duoc (van 2 dong o 240px) -- dung de xuat lai.
       Hai chu bat buoc giu trong moi lan viet lai sau nay:
       a. "estimated" -- cong bo bat buoc, bo di la trang noi mot con so DO duoc.
       b. "reach" -- chinh chu nay ganh ve "o luc cao diem" ("len toi" ban tieng Viet).
          Dong phu KHONG co cum "in the busiest hours", nen doi "reach" thanh
          "is"/"takes" la the hero tuyen bo dai do la hang chuan CA NGAY, trong khi
          khung vang ngan hon nhieu va doan dan ngay duoi van ghi "landing during
          the busiest hours". Doi chu nay la trang tu mau thuan voi chinh no.

    3. KHONG in thang trong the: dong "Updated {ngay}" ngay duoi da noi ky hon.
    4. KHONG in doan `basis`: no la menh de mo dau cua doan dan ben duoi (render_section).
    5. Hai cum so noi bang &nbsp; de khong bao gio bi ngat khoi dong cua no.
    6. Dong "Updated {ngay} - Hour by hour" nam TRONG dong phu hang SAVE, khong
       phai o day the. Chu site chot 06/10/2026: ngay do dong dau thoi diem cua
       UOC TINH, ma uoc tinh nam o hang SAVE. De duoi day the, no doc nhu footer
       cua ca the -- ham y gia va gio ho tro cung "cap nhat 5/10", khong phai y do.
       Link "Hour by hour" DA BO 06/10/2026 theo quyet dinh cua chu site: bang Wait
       Times nam ngay section ke duoi hero nen link chi tiet kiem mot cu cuon, va chu
       site se dua muc nay vao NAV khi can. Dung tu them lai.
    """
    h = d["headline"]
    # Con so: khung BAN NHAT (h["peak"]). Text: KHONG ghi ten khung ra trang.
    # Khac SAF, va co ly do: cum busy cua DAD gom mot khung DAO DONG MANH
    # (10:00-13:00, trung vi 50 nhung kich ban xau 77) nen bien duoi cua ca cum
    # tut xuong 50 -- thap hon ca mot khung Moderate (52-62) ngay duoi bang.
    # Chu site chot 04/10/2026: lay khung ban nhat, giu cach noi chung.
    # Dai cong bo = ghep hai dinh cao nhat ca ngay (headline_range, chot 06/10/2026),
    # KHONG phai nguyen dai cua mot khung. Hero / doan dan / FAQ dung CHUNG ham nay
    # -- lech nhau la trang tu mau thuan.
    busy = {"range": headline_range(d)}
    return f'''

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Save</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{saved(busy, h["fast_track"])}</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; line-height:1.45; color:#5A5A72; margin-top:3px;">Estimated peak queue: {rng(busy["range"])}&nbsp;min.<br>With Fast Track: under&nbsp;{ft_floor_cap(h["fast_track"])[1]}&nbsp;min.<br><span style="font-size:0.72rem;">Updated {fmt_date(updated)}</span></span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[daf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">24/7</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">Support</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">WhatsApp &amp; Email</span>
        </div>

      </div>
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
    peak = {"range": headline_range(d)}  # doan dan: dai cong bo, dung het voi hero
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
    busy = {"range": headline_range(d)}  # FAQ bam theo hero
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
