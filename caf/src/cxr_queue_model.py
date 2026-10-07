"""Mo phong hang cho nhap canh CXR (Cam Ranh) theo tung phut. Uoc tinh, khong phai do dac.

Dung chung khung voi DAD. BON cho khac, deu co ly do thuc te:

  1. LICH LA "NGAY DAI DIEN", KHONG PHAI MOT THU CU THE. CXR nang charter Nga, ma
     charter khong nam trong GDS va doi ngay theo tung tuan. Chot cung mot thu la
     overfit. Xem dau file cxr_flights.py.

  2. CUM DEM HAN QUOC LA DINH CAO NHAT TRONG NGAY, khong phai khung sang nhu PQC/DAD.
     11 chuyen Han ha canh trong 4 tieng 20:20-00:35. Hau qua: quiet_hours() tra ve
     RONG -- CXR khong co gio nao that su vang. Dieu nay DUNG va la dac diem nhan dang
     cua san bay nay; dung "sua" bang cach ep BASE_NIGHT vao.

  3. FOREIGN = 0,88 (cao hon DAD 0,85). Thi truong CXR gan nhu thuan khach quoc te
     vao (Nga, Han, Trung); phan khach Viet di autogate nho hon o DAD.

  4. MUA VU NGUOC VOI PHU QUOC. Khach chinh la Nga va Han tranh dong -> cao diem
     thang 12-2, day thang 9-11 (mua mua Nha Trang). Bang he so o cuoi file nay
     la cua RIENG CXR; KHONG duoc be tu PAF sang.
"""
import json
from collections import deque
from cxr_flights import FLIGHTS, SCHEDULE_SEASON

LOAD, FOREIGN = 0.87, 0.88
MONTH_UPLIFT = 1.00   # thang 10 = moc. Xem BANG HE SO MUA cuoi file -- CXR nguoc PQC.
WALK = (9, 24)        # T2 Cam Ranh 50.500 m2, 10 cua ra -> quang di bo tuong duong T2 DAD
PROC_SEC = 70
BASE_DAY, BASE_NIGHT, SURGE = 10, 8, 3
SURGE_PAX = 500       # khach vua ha trong 45 phut gan nhat -> mo them lan. ~2,5 chuyen CXR.
SURGE_AT = 300        # chot chan: hang da dai the nay thi mo them du lich bay khong bao truoc
FT = {"base": 10, "peak": [10, 15]}   # Fast Track: ~10 phut khung thuong, 10-15 khung cao diem
TAXI = 5
GRID_FOREIGN = (0.80, 0.85, 0.90)
# Khoang cong bo = phan vi [BAND_Q] cua 27 kich ban luoi.
# Dau tren giu 0.75. Dau duoi chuyen 0.25 -> 0.50: 0.25 la kich ban LAC QUAN (it quay
# nhat / xu ly nhanh nhat it khi xay ra), lam khung 10-13 ra "37-77" -- dau duoi dung
# bang khung VANG nhat trong ngay nen doc len thay vo ly. 0.50 la uoc tinh TRUNG TAM.
BAND_Q = (0.50, 0.75)
TIER_MOD, TIER_BUSY = 50, 70
# ----------------------------------------------------------------------
# BASE_DAY = 10 -- SUY TU CHINH DU LIEU CUA CXR, ba rang buoc doc lap
# ----------------------------------------------------------------------
# (0) TRAN VAT LY -- so quay LAP DAT, nguon cong khai:
#     T2 Cam Ranh co 28 QUAY NHAP CANH va 22 quay xuat canh, 70 quay check-in,
#     cong suat thiet ke 6,5 trieu khach/nam (VietnamNet).
#     28 la so quay CO, khong phai so quay MO cung luc. BASE_DAY la so MO.
#
# (1) SAN LUONG CA NAM cua chinh CXR:
#     4,2 trieu luot quoc te 2024 -> 2,1 trieu luot den -> x FOREIGN = 1,85 trieu
#     khach phai qua quay nguoi. Chia cho 51,4 khach/gio/quay (PROC_SEC=70)
#     = 35.933 gio-quay/nam. Mo 18h/ngay:
#         he so su dung 45% -> 12,2 quay      55% -> 9,9 quay
#
# (2) DINH DEM cua chinh CXR phai giai toa duoc (khong dai them vo han):
#         cua so 180 phut: 1.582 khach -> can >= 10,3 quay
#         cua so 240 phut: 1.892 khach -> can >=  9,2 quay
#
# (3) DOI CHIEU CHEO voi DAD (chi la kiem tra, KHONG phai can cu chinh):
#     dinh 90 phut DAD 1.327 khach (BASE_DAY 11, da hieu chuan 45-120 phut)
#     dinh 90 phut CXR 1.221 -> 11 x 0,920 = 10,1
#
# BON con duong doc lap deu roi vao 9-12. Chon 10 = dau THAN TRONG cua dai
# (it quay hon -> cho lau hon -> khong hua hen qua tay voi khach).
#
# AUTOGATE KHONG GIUP KHACH NUOC NGOAI. CXR co autogate tu 08/2023 nhung khi NHAP
# CANH chi cong dan Viet co ho chieu gan chip duoc dung. Nguoi nuoc ngoai chi dung
# duoc khi XUAT CANH va phai co the thuong tru/tam tru. => TOAN BO khach quoc te
# den deu qua quay nguoi, dung bot FOREIGN de "tru autogate" lan nua.
#
# GRID_COUNTERS de +-2 (DAF de +-1): o DAD con so 11 neo bang quan sat that,
# o CXR moi la so suy. Khong chac bang thi khoang cong bo phai rong hon.

OBSERVED_PEAK = (40, 120)   # !!! CHUA DUOC XAC MINH -- KHAC HAN DAD VA PQC !!!
# O DAD va PQC, dai nay la do CHU SITE phan anh tu thuc te. O CXR CHUA CO phan anh nao.
# 40-120 la dai TAM suy tu DAD (45-120). Cong hieu chuan o day chi la CHOT CHAN THO.
# => PHAI HOI CHU SITE: cao diem khach cho bao lau, khung nao te nhat, mo may quay.

GRID_COUNTERS, GRID_PROC = (8, 10, 12), (60, 70, 80)

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


RUNWAY_GAP = 3        # phut toi thieu giua hai luot ha canh tren duong bang CXR


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
    for (t, _fl, _o, _ac, seats) in FLIGHTS:
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
        for k, (t, _fl, _o, _ac, seats) in enumerate(FLIGHTS):
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


def build_month_json(month, month_label, month_notes, empty_band_note, context, basis, cities,
                     guide, uplift=None, surge=None):
    """month='2026-10', month_label='October 2026'.

    `uplift` va `surge` LA DON BAY THEO THANG, nhan tu inputs-YYYY-MM.json (khoa
    `month_uplift` / `surge`). None -> dung hang so module.

    VI SAO PHAI NHAN TU INPUTS -- sua 07/10/2026:
    Truoc day ca hai la HANG SO MODULE. Doi chung cho thang moi la thang cu KHONG
    DUNG LAI DUOC nua: dung inputs thang 10 voi model da chinh cho thang 11 ra mot
    con so thu ba, khong phai thang nao ca. Da dinh that o HAF ngay 07/10/2026 khi
    SURGE 5 -> 8 lam thang 10 (da phat hanh 97-110) vo luon cong tran phong cho.
    Skill van canh bao "MONTH_UPLIFT la hang so module, quen sua la im lang dung he
    so thang truoc" -- day la cach chua goc cho ca canh bao do.
    Hang so module gio chi con la MAC DINH cho ban chay tay; moi thang co so cua no
    nam trong inputs cua chinh thang do.
    """
    import itertools
    central_rows, _, central_pax = simulate(uplift=uplift, surge=surge)
    grid = [simulate(proc_sec=p, base_day=c, foreign=fo, uplift=uplift, surge=surge)
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
        "schema": "caf-wait/1.0", "site": "CAF", "airport": "CXR", "month": month,
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
                        "month_uplift": MONTH_UPLIFT if uplift is None else uplift,
                        # ^ GIA TRI DA DUNG THAT, khong phai hang so module.
                        #   Tu khi don bay ve inputs (luat nha 14), hai khoa nay la
                        #   thu DUY NHAT ghi lai thang do chay voi don bay nao -- va
                        #   monthly_publish.py cop chung vao latest.json lam MOC DOI
                        #   CHIEU cho phep thu don dieu thang sau. Ghi hang so module
                        #   vao day la noi doi: 07/10/2026 HAF da in surge=8/uplift=1,05
                        #   cho ban thang 10 that ra chay surge=5/uplift=1,00, va moc
                        #   sai do se lam thang 11 ket luan nguoc ("khong them quay"). "walk_min": WALK, "processing_sec": PROC_SEC,
                        "seats": {f[1]: f[4] for f in FLIGHTS},
                        "counters_day": BASE_DAY, "counters_night": BASE_NIGHT,
                        "surge_counters": SURGE if surge is None else surge, "surge_queue": SURGE_AT, "taxi_min": TAXI,
                        "seats_per_flight": True, "calibrated_to": list(OBSERVED_PEAK),
                        "grid_counters": list(GRID_COUNTERS), "grid_processing_sec": list(GRID_PROC),
                        "grid_foreign_share": list(GRID_FOREIGN), "band_quantiles": list(BAND_Q)},
        "sample_flights": [{"time": f[0], "flight": f[1], "from": f[2], "aircraft": f[3]} for f in FLIGHTS],
    }


# ======================================================================
# BANG HE SO MUA CUA RIENG CXR  -- KHONG DUNG BANG CUA PAF
# ======================================================================
# PQC ban khach Tay tranh dong + khach Viet nghi le. CXR ban khach NGA va HAN
# tranh dong, cong khach Trung. Hai duong cong khac han nhau:
#
#   Thang | He so | Vi sao
#   ------|-------|---------------------------------------------------------
#    1    | 1,25  | Dinh Nga + Han. Tet duong lich keo dai o Nga den 08/01.
#    2    | 1,25  | Van dinh. Tet am lich them khach Trung.
#    3    | 1,15  | Cuoi mua Nga, bat dau rut.
#    4    | 1,00  | Chuyen mua. Charter Nga giam manh.
#    5    | 0,95  | Thap. Bu mot phan boi khach Han va noi dia dip 30/4-1/5.
#    6-8  | 0,90  | THAP NHAT ve khach quoc te (he Bac ban cau khong ai tranh dong).
#                   Khach noi dia cao nhung ho KHONG qua quay nhap canh.
#    9    | 0,90  | Mua mua Nha Trang bat dau.
#   10    | 1,00  | MOC. Mua mua, nhung charter Nga bat dau vao (Nordwind tu 10/2025).
#   11    | 1,10  | Charter Nga vao day; mua mua chua het nhung khach dong len.
#   12    | 1,25  | Giang sinh + Tet duong. Cao diem nam.
#
# CANH BAO QUAN TRONG -- khac PAF:
# He so nay chi bu TY LE LAP DAY GHE. O CXR, cao diem dong con THEM CHUYEN (charter
# Nga Nordwind/Azur bay day tu thang 11 den thang 3). Nhan he so vao lich thang 10
# KHONG the hien duoc so chuyen tang them.
# => Tu thang 11 den thang 3, PHAI DUNG LAI DANH SACH CHUYEN, khong duoc chi doi he so.
