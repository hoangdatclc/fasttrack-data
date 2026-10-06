"""Mo phong hang cho nhap canh SGN (Tan Son Nhat) theo tung phut. Uoc tinh, khong phai do dac.

Dung chung khung voi DAD/CXR. NAM cho khac, deu co ly do rut tu chinh du lieu cua SGN:

  1. QUY MO KHAC HAN. SGN la cua ngo quoc te lon nhat Viet Nam: 145 chuyen quoc te
     den/ngay, 31.857 ghe -- gap 5,5 lan CXR. Moi hang so ben duoi phai suy lai tu dau,
     khong duoc be tu site khac sang.

  2. PROC_SEC = 110 GIAY, GAP HON MOT RUOI BA SITE KIA (70). Day la con so gay tranh cai
     nhat trong file, nen phan chung minh dat ngay duoi, muc (A).

  3. FOREIGN = 0,70 -- THAP NHAT trong bon site. SGN la diem ve cua kieu bao va la
     diem noi chuyen noi dia lon nhat; ty le khach mang ho chieu Viet cao hon han
     CXR (0,88) hay DAD (0,85).

  4. DINH LA BUOI CHIEU-TOI, khong phai dem nhu CXR. Cum 16:00-20:00 co 30 chuyen /
     4.080 khach ngoai. Day la dac diem nhan dang cua SGN; dung "sua" cho giong site khac.

  5. KHONG CO GIO VANG THAT SU. 22 chuyen ha trong khung 00:00-06:00. quiet_hours()
     tra ve rong hoac gan rong -- dung, va phai de nguyen.

======================================================================
(A) PROC_SEC = 110 -- SUY TU SAN LUONG CONG BO CUA CHINH T2
======================================================================
Bao Thanh Nien (02/2026) dan so cua don vi van hanh: khu xuat nhap canh nha ga quoc te
T2 giai quyet "khoang 50.000 luot khach/ngay, ca biet co ngay cao diem toi hon 61.000".
T2 co 44 quay nhap canh + 48 quay xuat canh = 92 quay lap dat.

    50.000 luot / (92 quay x 20 gio mo) = 27,2 luot/gio/quay = 132 giay/luot

132 giay la dau CHAM NHAT cua dai: no gia dinh ca 92 quay deu mo 20 tieng. Mo it quay
hon thi moi quay phai chay nhanh hon, tuc so giay/luot THAP hon 132. Chon 110 -- nam
trong dai, lech an toan ve phia nhanh hon.

SUA 06/10/2026: ba cho trong muc nay ghi "120" trong khi hang so thuc la 110 -- comment
viet tu thoi PROC_SEC con 120, doi gia tri ma quen doi chu. Khong doi mot byte dau ra;
nhung day dung la kieu loi da can mot lan roi (ma chet kem comment noi sai), nen chua.

Vi sao SGN cham hon CXR/DAD (70 giay): SGN nhan ty le khach e-visa va visa-on-arrival
lan dau cao nhat nuoc, co mat gan nhu moi quoc tich, va la noi duy nhat trong bon site
co luong khach noi chuyen quoc te->noi dia lon (phai kiem them chang tiep). CXR nguoc
lai gan nhu thuan charter Nga/Han lap lai, ho so giong nhau, quet rat nhanh.

======================================================================
(C) SURGE = 4 (ha tu 6) -- HIEU CHUAN LAI 06/10/2026 THEO THUC TE VAN HANH
======================================================================
Chu site bao: cao diem o T2 thuc te cho LAU HON HAN mo hinh -- thuong hon 2 tieng,
co luc 2,5 tieng. Mo hinh khi do cong bo dinh 113 phut (1,88 gio).

VI SAO LA SURGE CHU KHONG PHAI PROC_SEC -- da quet ca hai, co so do:

  | don bay          | dinh cong bo | hinh dang bang                          |
  |------------------|--------------|------------------------------------------|
  | SURGE 6 (cu)     | 113 (1,88h)  | du ba bac, khung dem 52-55 quick         |
  | SURGE 5          | 123 (2,05h)  | du ba bac, khung dem 52-55 quick         |
  | SURGE 4 (chon)   | 133 (2,22h)  | du ba bac, khung dem 52-71 moderate      |
  | SURGE 3          | 155 (2,58h)  | du ba bac, khung dem 52-95 busy          |
  | PROC_SEC 110->120| 152 (2,53h)  | VO: mat bac Moderate, khung dem thanh    |
  |                  |              | busy 55-90 -- ca NGAY deu tac            |

PROC_SEC lam cham DEU ca ngay. Chu site bao van de o CAO DIEM, khong phai ca ngay --
khung vang 06:00-10:00 khong ai keu. Nang PROC_SEC se day luon khung dem thanh "busy",
tra ve mot bang chi con hai bac: sai voi cai duoc mo ta.

SURGE thi can DUNG CHO: no chi tac dong khi hang da dai, tuc chi o cao diem.

VI SAO HA SURGE LA CO CAN CU, KHONG PHAI "chinh cho vua so":
muc (B)(3) dat SURGE = 6 bang cach tinh "can bao nhieu quay de GIAI TOA kip dinh
chieu-toi". Tuc no gia dinh cong an cua khau MO DU so quay can thiet. Quan sat cua chu
site noi chinh xac dieu nguoc lai: hang KHONG duoc giai toa kip, no dai toi 2+ gio.
Vay gia dinh "mo du" la cai sai, va SURGE la cho dung de sua. Day cung la gia thuyet
thu hai chu site tu neu ("so quay it hon so voi uoc tinh").

VI SAO CHON 4 CHU KHONG PHAI 3: so trang cong bo la phan vi 0,75 cua luoi -- truong hop
xau, khong phai xau nhat. SURGE 4 cho cong bo 133 phut (= "hon 2 tieng", dung mo ta
thuong gap) va duoi luoi cham ~150 (= "co luc 2,5 tieng", dung mo ta ca biet).
SURGE 3 cong bo thang 155 = 2,58h -- lay truong hop CA BIET lam so thuong gap, noi qua.

CONG CHAN VAT LY DA KIEM: voi SURGE 4, hang VAN giai toa het trong ngay (ton cuoi ngay
= 0 khach). Neu khong, mo hinh se mau thuan voi viec T2 tren thuc te van thong
~50.000 luot/ngay -- luc do con so dinh "dep" cung la con so sai.

======================================================================
(B) BASE_DAY = 28 -- SUY TU CHINH DU LIEU CUA SGN, bon rang buoc doc lap
======================================================================
(0) TRAN VAT LY -- so quay LAP DAT, nguon cong khai:
    T2 Tan Son Nhat: 44 QUAY NHAP CANH, 48 quay xuat canh, 120 quay check-in,
    115.834 m2, 26 cua ra, cong suat THIET KE 13 trieu khach/nam (sau mo rong 2018).
    Thuc te T2 dang xu ly ~50.000 luot xuat+nhap canh/ngay = ~18 trieu/nam = 140%
    cong suat thiet ke. DAY la ly do goc cua hang cho 60-120 phut, khong phai thieu quay.
    44 la so quay CO. BASE_DAY la so MO cung luc.

(1) TY LE MO so voi so lap dat, doi chieu cheo voi DAD:
    DAD mo 11+3 = 14 tren 22 quay lap dat o dinh = 64%.
    SGN: 28 tren 44 = 64%. Trung khop -- khong phai trung hop, ca hai deu la T2
    do cung mot luc luong cong an cua khau bo tri theo ca.

(2) SAN LUONG CA NGAY cua chinh T2 phai giai toa duoc:
    18.955 khach ngoai den/ngay / (3600/120 = 30 luot/gio/quay) = 632 gio-quay/ngay.
    Chia deu 24 gio (SGN chay 24/24, 22 chuyen ha trong khung 00:00-06:00)
    = 26,3 quay mo lien tuc. Cong bien cho gio thap diem -> 28.

(3) DINH CHIEU-TOI phai giai toa duoc (khong dai them vo han):
    cua so 240 phut (16:00-20:00): 4.080 khach -> can >= 34 quay-gio -> 8,5 quay/gio
    cong ton hang tu khung truoc -> SURGE 6 quay la de bu phan nay, khong phai de du.

(4) DOI CHIEU CHEO voi luu luong cong bo:
    Mo hinh ra 27.078 khach den/ngay (ca Viet lan ngoai). Thanh Nien ghi T2 xu ly
    ~50.000 luot/ngay ca hai chieu vao dip cuoi nam = ~25.000 luot den.
    Lech 8% -- trong nguong chap nhan. Lich thang 10/2026 la lich dong day du nen
    nhinh hon la hop ly.

HE SO SU DUNG 94%. Cao hon han ba site kia (DAD 71%). Day KHONG phai loi mo hinh:
SGN that su chay sat tran, va do chinh la ly do trang cong bo 60-120 phut cao diem
trong khi CXR chi 40-120. Hau qua ky thuat: mo hinh rat nhay voi tham so, nen
GRID de rong (+-2 quay, +-15 giay) va dau duoi khoang lay phan vi 0,50.

AUTOGATE KHONG GIUP KHACH NUOC NGOAI. SGN co 10 cong autogate (5 den, 5 di) tu 2024,
nhung chieu NHAP CANH "nguoi nuoc ngoai hien chua su dung duoc" (Cong an TP.HCM).
Ca nuoc chi ~2.500 luot/ngay dung autogate ca hai chieu -- 5% luu luong T2.
=> TOAN BO khach quoc te den deu qua quay nguoi; dung bot FOREIGN de "tru autogate".
"""
import json
from collections import deque
from sgn_flights import FLIGHTS

LOAD, FOREIGN = 0.85, 0.70
MONTH_UPLIFT = 1.00   # thang 10 = moc. Xem BANG HE SO MUA cuoi file -- SGN rat phang.
WALK = (10, 28)        # T2 115.834 m2, 19 cua ra -- nha ga lon nhat trong bon site
PROC_SEC = 110         # xem muc (A) dau file
BASE_DAY, BASE_NIGHT, SURGE = 28, 22, 4   # SURGE ha 6 -> 4 ngay 06/10/2026, xem (C)
SURGE_PAX = 1800       # khach vua ha trong 45 phut gan nhat -> mo them lan. ~8 chuyen SGN.
SURGE_AT = 300         # chot chan: hang da dai the nay thi mo them du lich bay khong bao truoc
# Fast Track bam theo BAC, ba muc -- khac ca PAF/DAF/CAF (hai muc) lan ban SAF dau tien
# (mot muc phang 20). Khoa theo ten bac, khong theo "base/peak", de them bac khong vo.
#   Lighter  -> ~10 phut   Moderate -> ~15 phut   Busy -> Under 20
# "Under 20" la cam ket TRAN cua trang: khung te nhat van khong qua 20.
FT = {"quick": 10, "moderate": 15, "busy": 20}
TAXI = 5
# LUOI CHI QUET HAI CHIEU O SAF (ba site kia quet ba). Ly do do bang so, khong phai cho tien:
# o SGN lan khach ngoai va lan khach Viet dung CHUNG 44 quay den cua T2. Khach ngoai dong
# hon du tinh thi cong an cua khau DICH QUAY sang lan ngoai -- cau va cung di cung nhau.
# Do thuc te tren mo hinh (03/10/2026):
#     co dich quay theo ty le:  fo .65/.70/.75 -> dinh 85 / 88 / 91 phut  (+-3%)
#     giu cung 28 quay:         fo .65/.70/.75 -> dinh 75 / 88 / 110 phut (+-23%)
# Quet doc lap tuc la dung cot thu hai: no che ra nhung kich ban khach tang ma quay khong
# tang, va o he so su dung 86% thi nhung kich ban do cho hang dai VO HAN -- dieu T2 ro rang
# khong gap (van thong ~50.000 luot/ngay). CXR/DAD chay o 55-71% nen khong dinh chuyen nay,
# va van giu luoi ba chieu.
GRID_FOREIGN = (0.70,)
# Khoang cong bo = phan vi [BAND_Q] cua 27 kich ban luoi. Dau duoi 0,50 (uoc tinh trung
# tam) chu khong phai 0,25 (kich ban lac quan) -- xem ghi chu cung ten trong model CXR.
BAND_Q = (0.50, 0.75)
# Nguong cao hon ba site kia (CAF 50/70) vi CA PHAN BO cua SGN dich len: khung vang nhat
# van 52-58 phut. Dat nguong thap thi moi khung deu "Busy", bang mat het tac dung phan loai.
TIER_MOD, TIER_BUSY = 65, 90

OBSERVED_PEAK = (85, 120)
# CAP NHAT 06/10/2026 -- xem muc (C) dau file. Day la THOI GIAN XEP HANG THUAN,
# KHONG phai so trang cong bo. Quy doi:  cong bo = hang cho + WALK[1] 28 + TAXI 5.
#   chu site quan sat (so cong bo): thuong > 120 phut, co luc 150 phut
#   -> hang cho thuan:               thuong >  87 phut, co luc 117 phut
#   -> OBSERVED_PEAK = (85, 120)
# DUNG LAN LON HAI THUOC DO NAY. Ban truoc ghi (60, 120) va chu thich "trang dang cong bo
# 60-120 at peak" -- tron so CONG BO vao mot hang danh cho hang cho THUAN, nen dai that
# rong gap doi y dinh va cong hieu chuan gan nhu khong bao gio keu.
# Neu sau nay chu site do lai va ra dai khac, sua OBSERVED_PEAK truoc roi chinh
# SURGE / PROC_SEC / BASE_DAY cho khop -- va chi chinh MOT don bay moi lan.
#
# !!! DIEM NHAY CAM NHAT CUA MO HINH NAY !!!
# O he so su dung 86%, 10 giay PROC_SEC doi dinh toi 28 phut (110s -> 88 phut, 120s -> 116).
# Ba site kia chay o 55-71% nen nhich vai giay khong an thua. O SAF thi an thua.
# => Doi PROC_SEC hay BASE_DAY o day PHAI chay lai ca bang va doc lai hinh dang cac khung,
#    khong duoc chi nhin moi con so dinh.
#
# HINH DANG, khong chi con so dinh: hieu chuan dung la khi bang co CA ba bac. Ban 28@120s
# truoc do cho dinh 88 phut (dat) nhung MOI khung deu >= 55 phut, tuc "ca ngay deu tac" --
# chọi voi chinh cau "60-120 at peak" cua trang. 28@110s giu dinh trong dai VA tra lai
# ba bac: 52-58 (vang) / 70-77 (vua) / 93-113 (dinh).

GRID_COUNTERS, GRID_PROC = (26, 28, 30), (100, 110, 120)

def quiet_hours():
    """Gio NAO san bay thuc su rut bot lan -- suy TU LICH BAY, khong dat cung theo dong ho.

    Chu site xac nhan 02/10/2026: san bay KHONG cat quay khi biet chac khach con dong.
    Ban cu cat luc 00:00 dung vao luc ton hang cua cum 23:xx dang nang nhat, lam khung
    dem bi thoi len 89-105 phut -- sai han thuc te. Gio chi la VANG khi khong co chuyen
    nao ha trong 2 tieng TRUOC va 1 tieng TOI; con lai giu nguyen so lan ban ngay.
    """
    land = {minute(f[0]) // 60 for f in FLIGHTS}
    out = set()
    for h in range(24):
        near = {(h - 2) % 24, (h - 1) % 24, h, (h + 1) % 24}
        if not (land & near):
            out.add(h)
    return out


BANDS = [("00:00-06:00", 0, 6), ("06:00-10:00", 6, 10), ("10:00-13:00", 10, 13),
         ("13:00-16:00", 13, 16), ("16:00-20:00", 16, 20), ("20:00-24:00", 20, 24)]


def minute(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


RUNWAY_GAP = 2        # SGN co HAI duong bang song song (25L/25R) -> gian 2 phut la du.
                      # CXR/DAD mot duong bang nen de 3. Chi dung de ra bunch gio lam tron.


def sim_minutes(gap=RUNWAY_GAP):
    """Gio ha canh dung cho MO PHONG, tach khoi gio dung de xep khung.

    Nguon lich bay lam tron: ba chuyen LJ111 / RF531 / TW29 deu ghi 23:55. Ba may bay
    khong the cham dat cung mot phut tren mot duong bang. De nguyen thi mo hinh dung
    len mot buc tuong 778 ghe trong 5 phut, va chuyen RS511 luc 00:00 lanh tron hau qua
    -- khung dem bi thoi len thanh khung ban thu nhi, sai han thuc te chu site ghi nhan.

    Gian cac luot ha canh ra toi thieu `gap` phut. KHUNG GIO van xep theo GIO TRONG
    LICH (23:55 van thuoc 20:00-24:00), chi rieng mo phong dung gio da gian.
    """
    order = sorted(range(len(FLIGHTS)), key=lambda i: minute(FLIGHTS[i][0]))
    out = {}
    last = None
    for i in order:
        t = minute(FLIGHTS[i][0])
        if last is not None and t < last + gap:
            t = last + gap
        out[i] = t
        last = t
    return out


SIM_MINUTE = sim_minutes()
QUIET_HOURS = quiet_hours()


def landing_load(window=45):
    """Khach HA CANH trong `window` phut gan nhat, theo tung phut cua ngay.

    San bay BIET TRUOC cum nao sap toi va bo tri nguoi tu dau ca -- chu site xac nhan
    02/10/2026. Ban cu chi tang lan khi hang DA dai 300 nguoi, tuc phan ung sau khi
    tac: cum 23:15-23:55 don toi 474 nguoi roi moi mo them quay. Gio tang lan theo
    LICH BAY, con nguong hang dai giu lai lam chot chan.
    """
    DAY = 24 * 60
    load = [0.0] * DAY
    for (t, _fl, _o, seats) in FLIGHTS:
        pax = seats * LOAD * FOREIGN
        at = minute(t)
        for m in range(window):
            load[(at + m) % DAY] += pax
    return load


LANDING_LOAD = landing_load()


def simulate(proc_sec=None, base_day=None, surge=None, uplift=None, foreign=None):
    """Mo phong HAI ngay lien tiep giong het nhau, doc ket qua tu ngay THU HAI.

    Vi sao phai lam the: DAD co SAU chuyen ha canh 23:15-23:55. Khach cua ho van
    con dang xep hang khi sang ngay moi, roi ba chuyen 00:00 / 00:25 / 01:10 xep
    tiep vao do. Neu bat dau voi hang RONG luc 00:00 thi khung 00:00-06:00 bi tinh
    THIEU 58 phut (35 thay vi 93) -- da do. PQC khong dinh loi nay vi khung do
    khong co chuyen nao, nhung day la loi cua MO HINH, khong phai cua san bay.
    """
    proc_sec = PROC_SEC if proc_sec is None else proc_sec
    base_day = BASE_DAY if base_day is None else base_day
    surge = SURGE if surge is None else surge
    uplift = MONTH_UPLIFT if uplift is None else uplift
    foreign = FOREIGN if foreign is None else foreign
    DAY, DAYS = 24 * 60, 2
    horizon = DAYS * DAY + 6 * 60
    arrivals = [[] for _ in range(horizon)]
    sched = []                                   # (gio theo lich tuyet doi, chi so chuyen, ngay)
    for d in range(DAYS):
        for k, (t, _fl, _o, seats) in enumerate(FLIGHTS):
            st = d * DAY + SIM_MINUTE[k]          # gio da gian -> xep vao hang
            i = len(sched)
            sched.append((d * DAY + minute(t), k, d))   # do tu GIO TRONG LICH BAY
            pax = seats * LOAD * foreign * uplift
            a, b = WALK
            for m in range(a, b):
                arrivals[st + m].append((i, pax / (b - a)))
    queue = deque()
    wait_sum = [0.0] * len(FLIGHTS)
    pax_sum = [0.0] * len(FLIGHTS)
    worst = [0.0] * len(FLIGHTS)
    for t in range(horizon):
        for f, n in arrivals[t]:
            queue.append([f, t, n])
        qlen = sum(c[2] for c in queue)
        hour = (t // 60) % 24
        counters = max(3, base_day - 4) if hour in QUIET_HOURS else base_day
        # Tang lan theo LICH BAY (biet truoc), chot chan bang do dai hang (bat ngo).
        if LANDING_LOAD[t % (24 * 60)] * uplift >= SURGE_PAX or qlen >= SURGE_AT:
            counters += surge
        cap = counters * 60.0 / proc_sec
        while cap > 1e-9 and queue:
            f, joined, n = queue[0]
            take = min(n, cap)
            st, k, d = sched[f]
            if d == DAYS - 1:                    # chi ghi nhan ngay CUOI
                wait_sum[k] += take * (t - joined)
                pax_sum[k] += take
                worst[k] = max(worst[k], t - st)  # do tu GIO TRONG LICH BAY
            cap -= take
            if take >= n - 1e-9:
                queue.popleft()
            else:
                queue[0][2] -= take
    rows = []
    for name, h0, h1 in BANDS:
        idx = [i for i, f in enumerate(FLIGHTS) if h0 * 60 <= minute(f[0]) < h1 * 60]
        p = sum(pax_sum[i] for i in idx)
        avg = sum(wait_sum[i] for i in idx) / p if p else None
        rows.append({"band": name, "flights": len(idx),
                     "avg_wait": None if avg is None else round(avg, 1),
                     "worst_wait": None if not idx else round(max(worst[i] for i in idx)),
                     "pax": round(p)})
    return rows, sum(wait_sum) / sum(pax_sum), sum(pax_sum)


def peak_queue(**kw):
    """Dinh thoi gian XEP HANG (da tru di bo va lan bai) -- con so de doi chieu quan sat."""
    rows, _, _ = simulate(**kw)
    return max(r["worst_wait"] for r in rows if r["worst_wait"] is not None) - WALK[1]


def build_month_json(month, month_label, month_notes, empty_band_note, context, basis, cities, guide):
    """month='2026-10', month_label='October 2026'."""
    import itertools
    central_rows, _, central_pax = simulate()
    grid = [simulate(proc_sec=p, base_day=c, foreign=fo)
            for p, c, fo in itertools.product(GRID_PROC, GRID_COUNTERS, GRID_FOREIGN)]

    def q(vals, lo=BAND_Q[0], hi=BAND_Q[1]):      # phan vi -> khoang, khong lay min/max
        vals = sorted(v for v in vals if v is not None)
        if not vals:
            return None
        k = lambda f: vals[min(len(vals) - 1, max(0, round(f * (len(vals) - 1))))]
        return [k(lo), k(hi)]

    bands = []
    for i, r in enumerate(central_rows):
        if r["avg_wait"] is None:
            bands.append({**r, "standard": None, "tier": "none"})
            continue
        lo, hi = q([g[0][i]["worst_wait"] for g in grid])
        top = hi + TAXI
        # Phân bậc theo con số HIỂN THỊ, không theo worst_wait thô. Ngưỡng cũ đặt trên
        # số thô nên một khung hiện "38-50 min" vẫn bị gắn nhãn "Usually quick".
        tier = "busy" if top >= TIER_BUSY else ("moderate" if top >= TIER_MOD else "quick")
        bands.append({**r, "standard": [lo + TAXI, top], "tier": tier})

    # Tiêu đề chỉ lấy BẬC CAO NHẤT và BẬC THẤP NHẤT đang có trong tháng, không gộp
    # "moderate" vào cụm bận. Gộp vào sẽ cho ra kiểu "38-118 min, 06:00-24:00":
    # khoảng rộng gấp ba, trải gần cả ngày, người đọc không rút ra được gì.
    ORDER = ["quick", "moderate", "busy"]
    live = [b for b in bands if b["standard"]]
    hi_t = max((b["tier"] for b in live), key=ORDER.index)
    lo_t = min((b["tier"] for b in live), key=ORDER.index)
    worst = max(live, key=lambda b: b["standard"][1])   # MOT khung, de len hero
    for b in bands:
        b["busy"] = bool(b["standard"]) and b["tier"] == hi_t
        b["calm"] = bool(b["standard"]) and (b["tier"] == lo_t if lo_t != hi_t else True)

    def span(sel):
        """Gộp các khung được chọn thành CÁC CỤM LIỀN NHAU, nối bằng '|'.
        Lấy min(đầu)..max(cuối) như trước sẽ sai khi khung cao điểm và khung vắng
        xen kẽ nhau: hai mô tả sẽ chồng lên nhau và chọi nhau trong cùng một đoạn."""
        picked = [b for b in bands if b["standard"] and sel(b)]
        if not picked:
            return None
        runs = []
        for b in picked:                               # bands đã theo thứ tự thời gian
            a, z = b["band"].split("-")
            if runs and runs[-1][1] == a:              # nối tiếp cụm đang mở
                runs[-1][1] = z
            else:
                runs.append([a, z])
        # Noi vong qua nua dem. DAD co cum Han Quoc chay 20:00 den qua 01:10; neu khong
        # noi thi mot khoang lien tuc bi cat lam hai, doc ra thanh hai cum roi rac.
        if len(runs) > 1 and runs[0][0] == "00:00" and runs[-1][1] == "24:00":
            runs[-1][1] = runs[0][1]
            runs.pop(0)
        ORD = ["none", "quick", "moderate", "busy"]
        return {"window": "|".join(f"{a}-{z}" for a, z in runs),
                "tier": max((b["tier"] for b in picked), key=ORD.index),
                "range": [min(b["standard"][0] for b in picked),
                          max(b["standard"][1] for b in picked)],
                "flights": sum(b["flights"] for b in picked)}

    # CỔNG HIỆU CHUẨN — chạy trước khi trả kết quả.
    # Mô hình từng ra gấp 2-3 lần thời gian chờ thực tế mà khách phản ánh, vì số quầy
    # và tỷ lệ khách qua quầy tay đều là giả định. Không ai báo — trang cứ thế đăng số sai.
    peak_queue = max(b["standard"][1] - TAXI - WALK[1] for b in bands if b["standard"])
    lo_ok, hi_ok = OBSERVED_PEAK[0] * 0.7, OBSERVED_PEAK[1] * 1.6
    if not (lo_ok <= peak_queue <= hi_ok):
        raise SystemExit(
            f"CỔNG HIỆU CHUẨN KHÔNG QUA: đỉnh xếp hàng {peak_queue:.0f} phút, "
            f"ngoài dải chấp nhận được {lo_ok:.0f}-{hi_ok:.0f} "
            f"(quan sát thực tế {OBSERVED_PEAK[0]}-{OBSERVED_PEAK[1]}). "
            "Dừng lại: xem lại số quầy, tỷ lệ khách ngoại, hoặc lịch bay — đừng giao số.")

    return {
        "schema": "saf-wait/1.0", "site": "SAF", "airport": "SGN", "month": month,
        "month_label": month_label, "status": "estimate",
        "metric": "minutes from landing to clearing immigration, last passengers off a flight",
        "lane": "foreign passport holders, standard immigration queue",
        # peak = CHI MOT khung te nhat -> hero + doan dan + FAQ. Con so de khach quyet dinh.
        # busy = toan bo cum bac cao nhat -> the "When Fast Track matters most". Cua so de biet
        #        khi nao can dich vu. Thang cao diem co the co 3-4 khung Busy roi rac; gop het
        #        vao hero se ra kieu "44-136 min, 06:00-24:00", rong gap ba va vo nghia.
        "headline": {"peak": span(lambda b: b is worst),
                     "busy": span(lambda b: b["busy"]), "quiet": span(lambda b: b["calm"]),
                     "fast_track": FT, "intl_arrivals_per_day": len(FLIGHTS),
                     "foreign_pax_per_day": round(central_pax, -2)},
        "bands": bands,
        "notes": {"month_notes": month_notes, "empty_band_note": empty_band_note},
        "context": context, "basis": basis,
        "links": {"guide": guide}, "cities": cities,
        "assumptions": {"load": LOAD, "foreign_share": FOREIGN,
                        "month_uplift": MONTH_UPLIFT, "walk_min": WALK, "processing_sec": PROC_SEC,
                        "seats": {f[1]: f[3] for f in FLIGHTS},
                        "counters_day": BASE_DAY, "counters_night": BASE_NIGHT,
                        "surge_counters": SURGE, "surge_queue": SURGE_AT, "taxi_min": TAXI,
                        "seats_per_flight": True, "calibrated_to": list(OBSERVED_PEAK),
                        "grid_counters": list(GRID_COUNTERS), "grid_processing_sec": list(GRID_PROC),
                        "grid_foreign_share": list(GRID_FOREIGN), "band_quantiles": list(BAND_Q)},
        "sample_flights": [{"time": f[0], "flight": f[1], "from": f[2], "seats": f[3]} for f in FLIGHTS],
    }


# ======================================================================
# BANG HE SO MUA CUA RIENG SGN  -- KHONG DUNG BANG CUA PAF/CAF
# ======================================================================
# SGN khac han ba site kia: KHONG ban mot thi truong nghi duong nao ca. No la cua ngo
# da muc dich -- cong tac, kieu bao ve nuoc (VFR), noi chuyen, du lich. Hau qua:
# duong cong mua vu PHANG hon nhieu, bien do 0,95-1,20 thay vi 0,90-1,25 nhu CXR.
#
#   Thang | He so | Vi sao
#   ------|-------|---------------------------------------------------------
#    1    | 1,15  | Tet duong lich + kieu bao bat dau ve som.
#    2    | 1,20  | DINH NAM. Tet am lich (06/02/2027) -- song kieu bao lon nhat.
#                   Luu y: nhieu kieu bao mang ho chieu My/Uc -> VAO LAN NGUOI NUOC
#                   NGOAI, nen he so nay an truc tiep vao hang cho dang tinh.
#    3    | 1,05  | Hau Tet rut dan; khach cong tac quay lai.
#    4    | 1,00  | 30/4-1/5 chu yeu la khach NOI DIA -- khong qua quay nhap canh.
#    5    | 0,95  | Thap. Khong co le quoc te nao.
#    6    | 1,05  | Nghi he bat dau, kieu bao ve cung con.
#    7    | 1,15  | Cao diem he: VFR + du lich gia dinh chau A.
#    8    | 1,15  | Van cao diem he, den giua thang 8.
#    9    | 0,95  | Thap nhat nam. Het he, chua vao mua kho.
#   10    | 1,00  | MOC. Chuyen lich dong tu 25/10 -- xem canh bao ben duoi.
#   11    | 1,05  | Lich dong day du; khach cong tac cuoi nam.
#   12    | 1,20  | Giang sinh + Tet duong + kieu bao ve som. Ngang dinh thang 2.
#
# CANH BAO -- giong CAF, khac PAF:
# He so chi bu TY LE LAP DAY GHE, khong bu SO CHUYEN. SGN them chuyen that su vao
# lich dong (tu 25/10) va vao dot Tet (cac hang tang tan suat 2-4 chuyen/tuan).
# => Thang 12, 1, 2: PHAI DUNG LAI DANH SACH CHUYEN, khong duoc chi doi he so.
#
# MOC KIEM TRA: ngay dai dien thang 10/2026 = 145 chuyen quoc te den, 31.857 ghe.
# Thang moi ra lech qua +-20% so voi moc -> dung lai kiem nguon truoc khi chay tiep.
