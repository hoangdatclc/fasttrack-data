"""Render 3 vùng từ {site}-wait-YYYY-MM.json."""
import json, os, sys
from datetime import date

MONTHS = ["January","February","March","April","May","June","July",
          "August","September","October","November","December"]

fmt_date = lambda d: f"{d.day} {MONTHS[d.month - 1]} {d.year}"
# Ban rut gon, CHI dung trong the hero: cot o do hep nhat trang, moi ky tu dang
# gia. Doan dan va FAQ van dung fmt_date day du -- chung co ca chieu rong dong van.
fmt_short = lambda d: f"{d.day} {MONTHS[d.month - 1][:3]} {d.year}"
# window có thể gồm nhiều cụm rời, nối bằng '|'. Một cụm thì kết quả y hệt bản cũ.
dash  = lambda w: " and ".join("&ndash;".join(r.split("-")) for r in w.split("|"))
# Mot dau thay vi hai khi hai dau bang nhau: "35&ndash;35 min" doc nhu loi dinh dang,
# khong nhu ket qua chac chan. Xay ra khi luoi kich ban deu cho cung mot so o mot khung.
# HAF la site DUY NHAT co nhanh nay; bon site kia van la f"{p[0]}&ndash;{p[1]}" tran.
# TINH DEN 10/2026 NHANH NAY CHUA CHAY LAN NAO -- khong khung nao cua nam site co
# lo == hi (khung 00:00-06:00 cua HAN ra 35-36, khong phai 35-35 nhu ban comment cu ghi).
# Giu lai lam phong xa; dung tuong no dang co tac dung.
rng   = lambda p: (f"{p[0]}" if p[0] == p[1] else f"{p[0]}&ndash;{p[1]}")
# Bac cao diem hien HAI kieu, co y (chot 05/10/2026, theo chuan SAF/DAF):
#   o BANG   -> "10-15 min": cot hep tren dien thoai.
#   HERO+van xuoi -> "Under 15": hero da co MOT dai so o dong Queue; them dai thu hai
#   ngay duoi lam yeu tuong phan "dai va bap benh" vs "ngan va chac". "Under 15" la
#   tran, dung o MOI khung, khop dong phu "every flight, every hour".
ftcell = lambda v: (f"{v[0]}&ndash;{v[1]}" if isinstance(v, (list, tuple)) else f"~{v}")
def ft_floor_cap(ft):
    """San va tran cua Fast Track, nhan ca hai hinh dang cau hinh dang dung:

      hai bac  {"base": 10, "peak": [10, 15]}            -> (10, 15)   PAF/DAF/CAF/HAF
      ba bac   {"quick": 10, "moderate": 15, "busy": 20} -> (10, 20)   SAF
      mot so   10                                        -> (10, 10)

    Mot ham dung chung ca 5 site (luat 9). Ban cu cua HAF tu tay lay ft["peak"][1]
    va ft["base"]: thang 10/2026 ra ket qua y het, nhung neu HAN doi sang ba bac kieu
    SAF thi no KeyError thay vi tinh dung.
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

    Chu site chot 06/10/2026. HAN la site CUOI CUNG chuyen (sau PQC, DAD, CXR, SGN).

        can tren = so LON NHAT trong bang
        can duoi = so LON NHAT con lai ma NHO HON can tren it nhat {min_gap} phut

    Xet TAT CA cac so hien trong cot "Standard queue" -- ca can duoi LAN can tren cua
    moi khung, khong chi tran. Nho vay can duoi luon la mot con so khach DOC DUOC
    trong bang ngay ben duoi, do lai duoc.

    Thang 10/2026:
      PQC  94 69 59 56 48 46 44 42 38 37            -> dinh 94,  <=84  la 69  -> 69-94
      DAD  79 77 68 66 62 60 52 50 49 45 44 40      -> dinh 79,  <=69  la 68  -> 68-79
      CXR  83 77 71 70 64 54 50 44 43 30 28         -> dinh 83,  <=73  la 71  -> 71-83
      SGN  113 97 93 78 77 70 58 56 55 52 51        -> dinh 113, <=103 la 97  -> 97-113
      HAN  110 109 107 97 90 77 70 53 51 36 35      -> dinh 110, <=100 la 97  -> 97-110

    O HAN ba khung Busy sat nhau (97-109, 90-107, 90-110) nen BA so dau tien deu nam
    trong vong 3 phut cua dinh; luat >= 10 phut bo qua ca ba va lay 97 -- san cua khung
    Busy ban nhat. Day dung la ly do luat ton tai: ghep hai TRAN cao nhat se ra 109-110,
    mot dai mot phut, doc nhu so DO chinh xac.

    THAY cho h["busy"] (90-110) ma HAF dung truoc 06/10/2026: 90 la san cua khung Busy
    NHE NHAT trong cum, tuc tu ha thap dinh cua chinh minh. h["busy"] VAN duoc dung cho
    the vang (window + cities) -- xem render_section.

    BA BAN TRUOC DA BO, DUNG QUAY LAI: (a) nguyen dai khung ban nhat; (b) ghep hai tran
    cao nhat ca ngay; (c) tran bac Moderate -> tran bac Busy. Ly do o skill me, SSITE: PAF.

    CONG CHAN: khong tim duoc so nao nho hon can tren >= {min_gap} phut -> DUNG, khong
    giao trang. Ngay hom do phang that; mot dai hep se noi doi ve do chac chan cua con so.
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
    Ly do: the hero chi cong bo MOT con so Fast Track -- "under {tran} min" o dong 2.
    Neu can tren tru SAN thi khach lay giay but tinh lai theo dong phu se ra con so
    khac cai in to phia tren, khong kiem chung duoc.

    HAF IN THEO GIO, BAC NUA TIENG (chu site chot 06/10/2026, theo sau bon site kia):
    1 - 1.5 - 2 - 2.5 - 3 ... Lam tron ve bac GAN NHAT, khong phai lam tron len.
    HAN thang 10/2026: 97-110 tru tran 15 -> 82-95 phut -> ca hai tron ve 1.5
    -> nhanh "~1.5 hours".

    Ban cu doi sang gio khi can duoi >= 60 phut va giu phut khi duoi 60. Bo vi hai
    don vi trong cung mot o lam the hero doc khac nhau moi thang; bac nua tieng giu
    don vi GIO quanh nam, va nhanh "Up to ~" ben duoi lo not truong hop thap.

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
        # Can duoi tut xuong duoi 1 gio. Ep thanh "1 hour" la noi qua, nen KHONG ep.
        # Chuyen sang dang TRAN -- "Up to ~{tran} hour": chi hua can tren nen khong the
        # noi qua o can duoi, van giu don vi gio va nguong toi thieu 1 gio.
        if h_hi < 1.0:
            raise SystemExit(
                f"KHONG IN DUOC THEO GIO: tiet kiem that la {lo}-{hi} phut, ca hai can "
                f"deu tron ve duoi 1 gio ({h_lo} va {h_hi}). Den dang 'Up to' cung khong "
                "cuu duoc. Dung lai -- hoi chu site: chuyen the hero ve phut thang nay, "
                "hay xem lai mo hinh?")
        return f"Up to ~{fmt(h_hi)} hour" + ("" if h_hi == 1.0 else "s")
    if h_lo == h_hi:
        # Mot gia tri thi phai co dau xap xi: "1.5 hours" tran doc nhu con so DO duoc,
        # trong khi no la hai can khac nhau (82 va 95 phut) cung tron ve 1.5.
        return f"~{fmt(h_lo)} hour" + ("" if h_lo == 1.0 else "s")
    return f"{fmt(h_lo)}&ndash;{fmt(h_hi)} hours"


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
    """The hero cua HAF theo MAU GOC cua trang (Save / From / 24-7), khong phai the
    so sanh hai hang nhu bon site kia. Chu site chot 05/10/2026: giu gan ban goc.

    1. Tieu de the ("Why Choose HAN Fast Track?") la phan TINH nam NGOAI vung zone.
       Sua no phai sua trong trang, `monthly_publish.py` co cong chan rieng. Xem
       SKILL.md muc 3b.

    2. Hang SAVE chi in MOT con so -- muc tiet kiem -- de khach khong phai tru nham.
       Nhung mot con so tiet kiem dung tran trui thi khach khong biet no tru tu dau,
       nen dong phu PHAI noi ca HAI dau: hang thuong bao nhieu, Fast Track bao nhieu.
       Chu site chot 05/10/2026 (cau do CHU SITE viet, da dich tu tieng Viet):

         The standard immigration queue is estimated to reach {X} minutes.
         Fast Track gets you through in under {tran} minutes.

       Hai dong, ngat bang <br>, moi dong mot dau cua phep tru.
       Hai chu bat buoc giu trong moi lan viet lai sau nay:
       a. "estimated" -- cong bo bat buoc, bo di la trang noi mot con so DO duoc.
       b. "reach" -- chinh chu nay ganh ve "o luc cao diem" ("len toi" trong ban
          tieng Viet). Dong phu KHONG con cum "in the busiest hours" nua, nen neu
          ai do doi "reach" thanh "is"/"takes" thi the hero se tuyen bo 90-110 la
          hang chuan CA NGAY -- trong khi khung vang chi 35-36 phut va doan dan
          ngay duoi van ghi "landing during the busiest hours". Doi chu nay la
          trang tu mau thuan voi chinh no.
       KHONG in thang o day: dong "Updated {ngay}" nam ngay duoi the da noi ky hon.
       Hai cum so noi bang &nbsp; de khong bao gio bi ngat doi khoi dong cua no.

    3. KHONG in doan `basis` trong the. No la MENH DE MO DAU cua doan dan ben duoi
       (xem render_section) va cua FAQ. Dung mot minh trong the thi no doc nhu loi
       dan khong co ngu canh -- chua noi so nao da giai thich cach tinh so.
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
    # Dai cong bo = dinh bang + so lon thu nhi cach no >= 10 phut (headline_range,
    # chot 06/10/2026). THAY cho h["busy"] (90-110): o HAN cum busy gom BA khung sat
    # nhau, can duoi 90 la san cua khung Busy NHE NHAT trong cum -- tu ha thap dinh
    # cua chinh minh. Hero / doan dan / FAQ dung CHUNG ham nay.
    busy = {"range": headline_range(d)}
    return f'''

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div class="haf-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Save</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{saved(busy, h["fast_track"])}</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; line-height:1.45; color:#5A5A72; margin-top:3px;">Peak immigration queue: {rng(busy["range"])}&nbsp;min<br>With Fast Track: under&nbsp;{ft_floor_cap(h["fast_track"])[1]}&nbsp;min<br><span style="font-size:0.72rem;">Estimate &middot; Updated {fmt_short(updated)}</span></span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div class="haf-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[haf_price service="fast_track"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div class="haf-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">24/7</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">Support</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">WhatsApp &amp; Email</span>
        </div>

      </div>
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
    # Hai thu khac nhau, DUNG gop lam mot (gop la KeyError: 'window' -- CAF da dinh):
    #   headline = dai cong bo (dinh + so thu nhi), chi dung cho CON SO.
    #   busy     = cum busy that cua thang, con giu "window" -> the vang can no de
    #              in khung gio va goi cities().
    headline = {"range": headline_range(d)}
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
      <p class="haf-wt-lead">In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Noi Bai International Airport (HAN) could spend <strong>{rng(headline["range"])} minutes</strong> completing immigration procedures. With Fast Track, this time is under {ftcap(ft)} minutes at any hour.</p>
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
    busy = {"range": headline_range(d)}  # FAQ bam theo hero -- cung mot con so
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
