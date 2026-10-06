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
rng   = lambda p: f"{p[0]}&ndash;{p[1]}"
# Fast Track BA BAC o SAF: Lighter ~10 · Moderate ~15 · Busy tran 20.
# FT_WORD/ftxt (bang tra cuu cho HERO, tra ve "Under 20") DA BO 06/10/2026: tu khi dong
# phu hang SAVE doi sang dang "With Fast Track: under&nbsp;{tran}&nbsp;min", tran duoc
# lay thang bang ft_floor_cap(h["fast_track"])[1], khong qua bang tra cuu nua. De lai
# chung thi chung thanh ma chet mang mot comment noi sai -- va nguoi sua sau se noi hero
# qua ftxt roi lam song lai chuoi "Under 20" da bo. Doan dan va FAQ dung ft_of().
# O BANG dung "15-20" thay cho "Under 20". Ly do thuan hien thi: cot Fast Track hep,
# tren dien thoai "Under 20 min" xuong hai dong, nhin nhu loi. "15-20" ngan hon ma
# KHONG noi khac di -- bac Moderate la 15, bac Busy tran 20, nen dai 15-20 chinh la
# cai bang dang mo ta. Hero rong nen van giu "Under 20 min" (chu cam ket manh hon).
FT_CELL = {10: "~10", 15: "~15", 20: "15&ndash;20"}
ftcell = lambda v: FT_CELL.get(v, f"~{v}")
ft_of = lambda tier, c: c.get(tier, c["busy"]) if isinstance(c, dict) else c
# Cau o the vang phai khop voi con so that cua khung de tho nhat. O PQC khung do la
# 37-46 phut nen "ban co the khong can chung toi" la dung. O DAD khung de tho nhat
# van la 43-65 phut -- noi cau do thanh ra sai, va ban re chinh dich vu cua minh.
# Chu site CAM chuoi "you may not need us, and we will say so." tu 04/10/2026, o MOI
# site (luat 3, house-rules). Tu 06/10/2026 SAF cung dung CAU CO DINH nhu bon site kia.
# Ban cu o day la mot bieu thuc dieu kien: duoi 35 phut thi in cau bi cam. Thang
# 10/2026 nhanh do khong chay (khung vang cua SGN la 51-58 phut) nen no ngoi im --
# nhung mot thang nao do SGN vang hon la trang tu in ra chuoi bi cam, va khong cong
# nao bat duoc vi khong cong nao kiem chuoi do. Gio cau la hang so + co cong chan.
calm_line = lambda q: "the line is shorter, though rarely short."


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
      PQC  moi so 94 69 59 56 48 46 44 42 38 37           -> dinh 94,  lon nhat <=84  la 69  -> 69-94
      DAD  moi so 79 77 68 66 62 60 52 50 49 45 44 40     -> dinh 79,  lon nhat <=69  la 68  -> 68-79
      CXR  moi so 83 77 71 70 64 54 50 44 43 30 28        -> dinh 83,  lon nhat <=73  la 71  -> 71-83
      SGN  moi so 113 97 93 78 77 70 58 56 55 52 51       -> dinh 113, lon nhat <=103 la 97  -> 97-113

    SGN la ngay co dai RONG nhat trong nam site: dinh 113 cach so thu nhi 16 phut.
    Khong phai may man -- SGN la san bay DONG nhat (59 chuyen trong cum busy), nen
    khung 16:00-20:00 doi dau han cac khung khac. Dung coi do la ly do bo cong chan.

    BA BAN TRUOC DA BO, DUNG QUAY LAI:
      1. nguyen dai cua khung ban nhat -- can duoi la SAN cua chinh khung do, chi noi
         "khach may man nhat trong khung te nhat", khong noi gi ve ca ngay.
      2. ghep hai TRAN cao nhat ca ngay -- o DAD hai khung ban nhat co tran gan bang
         nhau (77 va 79) nen dai co lai con 2 phut, doc nhu so DO chinh xac.
      3. tran bac Moderate -> tran bac Busy -- o CXR cac khung Moderate nhe that
         (tran 50) nen can duoi tut qua sau, tiet kiem roi xuong duoi 1 gio.
    Ban thu tu bo han khai niem "bac" va "tran": chi lay hai con so lon nhat trong
    bang con cach nhau du xa. On dinh voi moi hinh dang ngay.

    O SAF cach nay con THAY luon cum h["busy"] (78-113) o ba cho in con so. Cum busy
    cua SGN gom hai khung chenh nhau nhieu (93-113 va 78-97) nen can duoi 78 la san
    cua khung NHE HON trong cum -- cong bo 78-113 la tu ha thap dinh cua chinh minh.
    h["busy"] VAN duoc dung cho the vang (window + cities), xem render_section.

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
    Ly do: the hero chi cong bo MOT con so Fast Track -- "under {tran} min" o dong 2.
    Neu can tren tru SAN thi khach lay giay but tinh lai theo dong phu se ra con so
    khac cai in to phia tren, khong kiem chung duoc. O SAF chenh lech nay LON NHAT
    trong nam site: Fast Track ba bac (san 10, tran 20) nen tru san o can tren se
    cong them 10 phut vao muc tiet kiem -- dung 1/3 cua mot bac nua tieng.

    SAF IN THEO GIO, BAC NUA TIENG (chu site chot 06/10/2026, theo sau PAF, DAF, CAF):
    1 - 1.5 - 2 - 2.5 - 3 ... Lam tron ve bac GAN NHAT, khong phai lam tron len.
    SGN thang 10/2026: 97-113 tru tran 20 -> 77-93 phut -> ca hai tron ve 1.5
    -> nhanh "~1.5 hours" ben duoi.

    TRAN FAST TRACK O SAF LA 20, KHONG PHAI 15. ft_floor_cap() tu doc ra tu cau hinh
    ba bac {"quick":10,"moderate":15,"busy":20}. Dung gan cung 15 theo bon site kia --
    tru 15 se lam the hero hua tiet kiem nhieu hon 5 phut so voi cam ket dong 2.

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
        # Can duoi tut xuong duoi 1 gio. Ep no thanh "1 hour" la noi qua, nen KHONG ep.
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
        # Mot gia tri thi phai co dau xap xi: "1.5 hours" tran doc nhu con so DO duoc,
        # trong khi no la hai can khac nhau (77 va 93 phut) cung tron ve 1.5.
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

       BAN DO DA BO 06/10/2026. CAU CHU CHOT, GIONG NHAU O CA BON SITE DA CHUYEN
       (PQC, DAD, CXR, SGN):

           Peak immigration queue: {dai} min
           With Fast Track: under {tran} min
           Estimate - Updated {ngay rut gon}

       Ba dong, ngat bang <br>; dong 3 nho hon (0.72rem).

       Bon chu bat buoc, mat chu nao cung la trang noi sai:
       a. "immigration" -- san bay co nhieu hang cho (check-in, soi chieu, nhap canh,
          hanh ly, taxi) va ngay duoi the la hai o Arrival/Departure, nen khach mua
          Departure rat de hieu con so nay thanh hang check-in. Dem tren hero TRUOC
          khi them chu nay: PQC 0 lan, DAD 1 lan, CXR 3 lan -- rieng PQC khong co cho
          nao cho khach biet day la hang gi.
       b. "Peak" -- con so la luc CAO DIEM, khong phai ca ngay. Bo di la trang tuyen
          bo dai do dung o moi khung gio.
       c. "under {tran}" -- MOT nguong duy nhat (luat 10). O SAF tran la 20, khong
          phai 15; lay tu ft_floor_cap(), dung gan cung. Dung doi thanh "15-20 min"
          -- dang do CHI dung trong cot Fast Track cua BANG (xem FT_CELL).
       d. "Estimate" o dong 3 -- cong bo uoc tinh, danh cho khach luot. Dau "~" tung
          dung thay no (06/10/2026) nhung da bo: thua khi dong 3 da noi, va tren man
          hep moi ky tu deu dang gia.

       KHONG dau cham cuoi dong 1 va dong 2. Don vi "min", khong phai "minutes".
       Ngay dung fmt_short (5 Oct 2026), khong phai fmt_date.

       DO DAI LA RANG BUOC CUNG: moi dong phai vua MOT DONG o ca 1440px (cot 262px)
       lan 390px (cot 240px). Ban cu la mot cau day du
       ("The standard immigration queue is estimated to reach X minutes.") --
       no vo thanh 4 dong, va cum &nbsp; lam dong 2 de lai mot khoang trong lon
       ben phai, trong nhu loi hien thi. Da do bang Playwright: chi dang nhan:gia-tri
       moi vua mot dong. "within 15 minutes" va "in 10-15 minutes" DEU KHONG cuu
       duoc (van 2 dong o 240px) -- dung de xuat lai.

       RIENG SAF dong 1 la dong DAI NHAT trong bon site: dai 97-113 la ba chu so
       o ca hai can (cac site kia hai chu so). Do lai nguong ngat sau moi lan doi
       cau o day, dung suy tu PQC/DAD/CXR sang.

    3. KHONG in thang trong the: dong "Updated {ngay}" trong dong phu da noi ky hon.
    4. KHONG in doan `basis`: no la menh de mo dau cua doan dan ben duoi (render_section).
    5. Hai cum so noi bang &nbsp; de khong bao gio bi ngat khoi dong cua no.
    6. Dong "Updated {ngay} - Hour by hour" DA CHUYEN vao dong phu hang SAVE, khong
       con la mot the <p> duoi day the. Chu site chot 06/10/2026: ngay do dong dau
       thoi diem cua UOC TINH, ma uoc tinh nam o hang SAVE. De duoi day the, no doc
       nhu footer cua ca the -- ham y gia va gio ho tro cung "cap nhat 5/10", khong
       phai y do. Link "Hour by hour" DA BO 06/10/2026 theo quyet dinh cua chu site:
       bang Wait Times nam ngay section ke duoi hero nen link chi tiet kiem mot cu
       cuon, va chu site se dua muc nay vao NAV khi can. Dung tu them lai.
    7. BA HANG deu phai co class="sgn-hero-row" -- CSS tinh trong page-in.txt bam
       vao class nay de thu cot nhan tren man hep (xem muc 1d cua skill me).
    """
    h = d["headline"]
    # Dai cong bo = dinh bang + so lon thu nhi cach no >= 10 phut (headline_range,
    # chot 06/10/2026). THAY cho h["busy"] (ca cum bac cao nhat): cum busy cua SGN
    # gom hai khung chenh nhieu (93-113 va 78-97) nen can duoi 78 la san cua khung
    # NHE HON trong cum -- cong bo 78-113 la tu ha thap dinh cua chinh minh.
    # Hero / doan dan / FAQ dung CHUNG ham nay -- lech nhau la trang tu mau thuan.
    busy = {"range": headline_range(d)}
    return f'''

      <div style="display: flex; flex-direction: column; gap: 0;">

        <div class="sgn-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">Save</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#1a7a42; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">{saved(busy, h["fast_track"])}</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; line-height:1.45; color:#5A5A72; margin-top:3px;">Peak immigration queue: {rng(busy["range"])}&nbsp;min<br>With Fast Track: under&nbsp;{ft_floor_cap(h["fast_track"])[1]}&nbsp;min<br><span style="font-size:0.72rem;">Estimate &middot; Updated {fmt_short(updated)}</span></span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div class="sgn-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
          <span style="grid-row:1; grid-column:1; font-family:'DM Sans',sans-serif; font-size:0.65rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#5A5A72; align-self:end;">From</span>
          <span style="grid-row:1; grid-column:2; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:700; color:#0B1F3A; line-height:1; font-variant-numeric:lining-nums; font-feature-settings:'lnum' 1;">[saf_price service="fast_track_arrival"]</span>
          <span style="grid-row:2; grid-column:2; font-family:'DM Sans',sans-serif; font-size:0.75rem; color:#5A5A72; margin-top:2px;">Per person &middot; Confirmed in 10 minutes</span>
        </div>

        <div style="height:1px; background:#E8E4DE;"></div>

        <div class="sgn-hero-row" style="display: grid; grid-template-columns: 50px 1fr; column-gap: 12px; padding: 11px 0;">
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
    # CA BA cho tren trang (hero · doan dan · FAQ) deu lay CUNG MOT con so va deu goi
    # la "the busiest hours", khong ke ten khung. h["peak"] (mot khung te nhat) van nam
    # trong JSON nhung KHONG cho ra trang nua: ba cho noi ba con so khac nhau cho cung
    # mot cau hoi thi doc len thanh mau thuan.
    # Hai thu khac nhau, DUNG gop lam mot (gop la KeyError: 'window' nhu CAF da bi):
    #   headline = dai cong bo (dinh + so thu nhi), chi dung cho CON SO.
    #   busy     = cum busy that cua thang, con giu "window" -> the vang can no de
    #              in khung gio va goi cities().
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
      <p class="sgn-wt-lead">In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Tan Son Nhat International Airport (SGN) could spend <strong>{rng(headline["range"])} minutes</strong> completing immigration procedures. With Fast Track, this time is under {ft_of("busy", ft)} minutes at any hour.</p>
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

    <p class="sgn-wt-method"><strong>How we estimate:</strong> a minute-by-minute queue model over the {h["intl_arrivals_per_day"]} international arrivals on a representative {d["month_label"].split()[0]} day, counting deplaning and the walk to the hall, and checked against the daily immigration volume the airport publishes.</p>

    <div class="sgn-wt-cta">
      <button type="button" class="sgn-pick-btn sgn-wt-btn" aria-expanded="false" aria-haspopup="true">Book Fast Track<svg class="sgn-pick-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg></button>
    </div>
'''


def render_faq(d, updated, faq_id="sgn-faq-a12"):
    """Khoi de bi AI trich nguyen van nhat -> phai TU DUNG MOT MINH.

    Dung chung menh de `d["basis"]` voi doan dan. KHAC doan dan dung mot cho: FAQ GIU
    con so khung vang, vi no la cau tra loi day du; doan dan la tieu diem nen chi neu
    con so te nhat.
    """

    h = d["headline"]; quiet, ft = h["quiet"], h["fast_track"]
    busy = {"range": headline_range(d)}  # FAQ bam theo hero va doan dan -- cung mot con so
    return f'''
        <div class="sgn-faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <button class="sgn-faq-btn" type="button" onclick="sgnFaqToggle(this)" aria-expanded="false" aria-controls="{faq_id}">
            <h3 class="sgn-faq-q" itemprop="name">How long is the immigration queue at Tan Son Nhat Airport in {d["month_label"]}?</h3>
            <span class="sgn-faq-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="sgn-faq-body" id="{faq_id}" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <div itemprop="text">
            <p>In {d["month_label"]}, {d["basis"]}, passengers landing during the busiest hours at Tan Son Nhat Airport could spend <strong style="color:#0B1F3A; font-weight:600;">{rng(busy["range"])} minutes</strong> completing immigration procedures, and {rng(quiet["range"])} minutes at quieter hours.</p>
            <p style="margin-top:10px !important;">With Fast Track, this time is under {ft_of("busy", ft)} minutes at any hour. <a href="#wait-times" style="color:#C9A84C; font-weight:600; text-decoration:none;">See the estimate for your landing time</a> (updated {fmt_date(updated)}).</p>
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
