"""Render 3 vùng từ {site}-wait-YYYY-MM.json."""
import json, math, os, sys
from datetime import date

MONTHS = ["January","February","March","April","May","June","July",
          "August","September","October","November","December"]

fmt_date = lambda d: f"{d.day} {MONTHS[d.month - 1]} {d.year}"
# Ban rut gon, CHI dung trong the hero: cot o do hep nhat trang, moi ky tu dang
# gia. Doan dan va FAQ van dung fmt_date day du -- chung co ca chieu rong dong van.
fmt_short = lambda d: f"{d.day} {MONTHS[d.month - 1][:3]} {d.year}"
# window có thể gồm nhiều cụm rời, nối bằng '|'. Một cụm thì kết quả y hệt bản cũ.
dash  = lambda w: " and ".join("&ndash;".join(r.split("-")) for r in w.split("|"))
rng   = lambda p: f"{p[0]}&ndash;{p[1]}"
# Bac cao diem hien HAI kieu, co y (chot 05/10/2026, theo chuan SAF/DAF):
#   o BANG   -> "10-15 min": cot hep tren dien thoai.
#   HERO+van xuoi -> "Under 15": hero da co MOT dai so o dong Queue; them dai thu hai
#   ngay duoi lam yeu tuong phan "dai va bap benh" vs "ngan va chac". "Under 15" la
#   tran, dung o MOI khung, khop dong phu "every flight, every hour".
ftcell = lambda v: (f"{v[0]}&ndash;{v[1]}" if isinstance(v, (list, tuple)) else f"~{v}")
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
    """Muc tiet kiem in o hang SAVE. LUON LA MOT KHOANG, don vi GIO, bac nua tieng.

    CHU SITE CHOT 06/10/2026 -- bon dieu, ap cung:
      1. PHAI la mot KHOANG (hai gia tri), khong bao gio mot so.
      2. Bac nua tieng: 1 - 1.5 - 2 - 2.5 - 3 ... Toi thieu 1 gio.
      3. CAN CU la dai hang thuong NGUYEN, *KHONG* tru thoi gian Fast Track.
      4. Chon khoang dung nhat theo lam tron GAN NHAT ca hai can.

    VI SAO KHONG TRU FAST TRACK (ly do chu site, ghi lai de khong ai "sua lai cho
    dung"): dai hang thuong la UOC TINH tu mo hinh, con thuc te van hanh cho thay
    buffer thuong lon hon 15 phut rat nhieu. Tru dung 15 phut trong khi phan vuot
    buffer khong ai do duoc la tu ha thap muc tiet kiem that. Hang SAVE la cho gay
    an tuong voi khach; hai dong ngay duoi no van in ca hai con so nguyen de khach
    tu kiem.

    TINH CHAT GIU CHO CON SO NAY TRUNG THUC -- va CONG CHAN o duoi ep no dung:

        can duoi cua khoang == dung bang phep tru ma khach tu lam theo dong 1 va 2

    Thang 10/2026 ca nam site deu thoa: PQC 69-94 -> SAVE 1-1.5, khach tu tru
    (69-15=54) cung ra 1.0. HAN 97-110 -> SAVE 1.5-2, khach tu tru (97-15=82)
    cung ra 1.5. Nghia la CAN DUOI luon kiem chung duoc ngay tren trang; chi CAN
    TREN moi la phan dua vao buffer thuc te. Day la cau tra loi cho khach nao lay
    giay but ra tinh: ho se thay con so nho nhat trang hua dung bang con so ho tinh.

    Thang nao tinh chat do gay -> DUNG, khong giao trang. Luc do hang SAVE se hua
    o CAN DUOI nhieu hon cai trang tu noi, va do la noi qua, khong phai an tuong.

    LAM TRON: dung floor(m/30 + 0.5), KHONG dung round(). round() cua Python la
    banker's rounding -- round(2.5) ra 2 chu khong phai 3 -- nen 75 phut se tut
    xuong 1.0 thay vi len 1.5. Da suyt dinh.

    HAI CAN TRON VE CUNG MOT GIA TRI: noi rong XUONG (can duoi = can tren - 0.5),
    khong bao gio noi len. Noi len la dua can tren vuot qua ca so lon nhat trong
    bang -- bia ra mot con so khong co trong du lieu. Noi xuong chi lam loi hua
    khiem ton hon.
    """
    base, cap = ft_floor_cap(ft)
    lo_min, hi_min = busy["range"]                 # NGUYEN, khong tru Fast Track
    half = lambda m: math.floor(m / 30.0 + 0.5) / 2.0
    fmt  = lambda v: (f"{v:.0f}" if v == int(v) else f"{v:.1f}")

    lo, hi = half(lo_min), half(hi_min)

    # CONG CHAN 1 -- toi thieu 1 gio, va phai la KET QUA lam tron chu khong phai san
    # ep vao. Kiem CA HAI can: ban dau chi kiem `hi` nen dai 40-50 phut lot qua va in
    # ra "0.5-1 hours" -- vua duoi nguong chu site dat, vua la mot khoang nua tieng
    # doc nhu khong co gi de ban. Lam tron ve bac gan nhat chi ra >= 1.0 khi so that
    # >= 45 phut; thang nao tut duoi do ma van in "1 hour" la trang noi qua > 25%.
    if hi < 1.0:
        raise SystemExit(
            f"KHONG IN DUOC THEO GIO: dai hang thuong {lo_min}-{hi_min} phut, ca hai can "
            f"deu tron ve duoi 1 gio. Hang SAVE khong the vua la khoang vua >= 1 gio. "
            "Dung lai -- hoi chu site: chuyen the hero ve phut thang nay, hay xem lai mo hinh?")
    if lo < 1.0:
        raise SystemExit(
            f"CAN DUOI DUOI NGUONG: dai hang thuong {lo_min}-{hi_min} phut -> can duoi tron "
            f"ve {fmt(lo)} gio, duoi nguong 1 gio chu site dat. Ep len 1.0 la noi qua "
            f"({lo_min} phut that su khong phai 1 gio). Dung lai, hoi chu site.")

    # PHAI LA MOT KHOANG. Tron ve cung mot gia tri -> noi rong XUONG, khong bao gio len.
    if lo == hi:
        lo = hi - 0.5
        if lo < 1.0:
            raise SystemExit(
                f"KHONG DUNG DUOC KHOANG: ca hai can deu tron ve {fmt(hi)} gio, noi rong "
                f"xuong se ra {fmt(hi - 0.5)} gio -- duoi nguong 1 gio chu site dat. "
                "Dung lai, hoi chu site truoc khi giao.")

    # CONG CHAN 2 -- can duoi phai TRUNG voi phep tru khach tu lam (xem docstring).
    #
    # SUA THU TU 07/10/2026 -- truoc do cong nay chay TRUOC buoc noi rong o tren, tuc
    # no kiem mot gia tri KHONG BAO GIO LEN TRANG. CXR thang 11 lo ra: dai 75-87, ca
    # hai can tron ve 1.5, cong doi chieu 1.5 voi phep tru half(75-15)=1.0 roi DUNG --
    # trong khi sau khi noi rong can duoi la 1.0, BANG DUNG phep tru, va trang se in
    # "1-1.5 hours" hoan toan kiem chung duoc. Cong da chan mot trang dung.
    # Chuyen xuong day: kiem DUNG con so se in ra. Khong noi long mot ly nao -- noi
    # rong chi HA can duoi, nen phep kiem o vi tri moi chat bang hoac chat hon.
    # Da doi chieu: thang 10/2026 ca bon site deu khong cham nhanh noi rong, nen doi
    # thu tu KHONG doi mot con so nao cua thang 10.
    arith = half(lo_min - cap)
    if lo != arith:
        raise SystemExit(
            f"CAN DUOI KHONG KIEM CHUNG DUOC: hang SAVE in can duoi {fmt(lo)} gio, nhung "
            f"khach tu tru theo dong 1 va dong 2 ({lo_min} - {cap} = {lo_min - cap} phut) ra "
            f"{fmt(arith)} gio. Chenh nhau la trang hua nhieu hon chinh no noi. Dung lai.")

    return f"{fmt(lo)}&ndash;{fmt(hi)} hours"


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
       CAU CHU CHOT 06/10/2026, GIONG NHAU O CA BA SITE (PQC, DAD, CXR):
           Peak immigration queue: {dai} min
           With Fast Track: under {tran} min
           Estimate - Updated {ngay rut gon}

       Bon chu bat buoc, mat chu nao cung la trang noi sai:
       a. "immigration" -- san bay co nhieu hang cho (check-in, soi chieu, nhap canh,
          hanh ly, taxi) va ngay duoi the la hai o Arrival/Departure, nen khach mua
          Departure rat de hieu con so nay thanh hang check-in. Dem tren hero TRUOC
          khi them chu nay: PQC 0 lan, DAD 1 lan, CXR 3 lan -- rieng PQC khong co cho
          nao cho khach biet day la hang gi.
       b. "Peak" -- con so la luc CAO DIEM, khong phai ca ngay. Bo di la trang tuyen
          bo dai do dung o moi khung gio.
       c. "under {tran}" -- MOT nguong duy nhat (luat 10). Dung doi thanh "10-15 min".
       d. "Estimate" o dong 3 -- cong bo uoc tinh, danh cho khach luot. Dau "~" tung
          dung thay no (06/10/2026) nhung da bo: thua khi dong 3 da noi, va tren man
          hep moi ky tu deu dang gia.

       KHONG dau cham cuoi dong 1 va dong 2. Don vi "min", khong phai "minutes".
       Ngay dung fmt_short (5 Oct 2026), khong phai fmt_date.

       DO DAI LA RANG BUOC CUNG: moi dong phai vua MOT DONG o
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
    # CXR: cum busy TACH BACH khoi cac bac duoi (san 54 > tran Moderate 50) nen
    # cong bo CA CUM theo chuan SAF. Khac DAF -- o DAD cum busy co mot khung dao
    # dong manh keo san xuong duoi ca khung Moderate nen DAF phai dung h["peak"].
    # Dai cong bo = tran bac Moderate -> tran bac Busy (headline_range, chot 06/10/2026).
    # Hero / doan dan / FAQ dung CHUNG ham nay -- lech nhau la trang tu mau thuan.
    busy = {"range": headline_range(d)}
    return f'''

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div class="caf-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Save</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{saved(busy, h["fast_track"])}</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; line-height:1.45; color:#5A5A72; margin-top:3px;">Peak immigration queue: {rng(busy["range"])}&nbsp;min<br>With Fast Track: under&nbsp;{ft_floor_cap(h["fast_track"])[1]}&nbsp;min<br><span style="font-size:0.72rem;">Estimate &middot; Updated {fmt_short(updated)}</span></span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div class="caf-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[caf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div class="caf-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
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
    # doan dan dung CA CUM, giong hero. The vang van ghi khung gio (ngoai le).
    # Hai thu khac nhau, DUNG gop lam mot:
    #   headline = dai cong bo (tran Moderate -> tran Busy), chi dung cho CON SO.
    #   busy     = cum busy that cua thang, con giu "window" -> the vang can no de
    #              in khung gio va goi cities(). Gop lam mot se KeyError: 'window'.
    headline = {"range": headline_range(d)}
    busy = h["busy"]
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
      <p class="caf-wt-lead">In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Cam Ranh International Airport (CXR) could spend <strong>{rng(headline["range"])} minutes</strong> completing immigration procedures. With Fast Track, this time is under {ftcap(ft)} minutes at any hour.</p>
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

    <p class="caf-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a representative {d["month_label"].split()[0]} day, counting deplaning and the walk to the hall, and checked against the waits travellers report.</p>

    <div class="caf-wt-cta">
      <button type="button" class="caf-pick-btn caf-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="caf-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
    </div>
'''


def render_faq(d, updated, faq_id="caf-faq-a12"):
    """Khoi de bi AI trich nguyen van nhat -> phai TU DUNG MOT MINH.

    Dung chung menh de `d["basis"]` voi doan dan. KHAC doan dan dung mot cho: FAQ GIU
    con so khung vang, vi no la cau tra loi day du; doan dan la tieu diem nen chi neu
    con so te nhat.
    """

    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = {"range": headline_range(d)}  # FAQ bam theo hero
    return f'''
        <div class="caf-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="caf-faq-btn" type="button" onclick="cafFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="caf-faq-q" itemprop="name">How long is the immigration queue at Cam Ranh Airport in {d["month_label"]}?</h3>
            <span class="caf-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="caf-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Cam Ranh Airport could spend <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> completing immigration procedures, and {rng(quiet["range"])} minutes at quieter hours.</p>
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
    main(sys.argv[1] if len(sys.argv) > 1 else "caf-wait.json",
         date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today())
