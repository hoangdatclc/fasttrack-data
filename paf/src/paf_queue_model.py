"""Mô phỏng hàng chờ nhập cảnh theo từng phút. Ước tính, không phải đo đạc."""
import json
from collections import deque

# (giờ hạ cánh, số hiệu, sân bay đi) — THAY bằng lịch của tháng cần tính
FLIGHTS = [
    ("07:35", "VJ979", "ICN"), ("09:00", "9G (W16098)", "ICN"), ("09:30", "AK543", "KUL"),
    ("09:40", "UO598", "HKG"), ("11:10", "VJ969", "PUS"),
    ("13:20", "AK660", "DMK"), ("13:35", "AK545", "KUL"), ("13:45", "VJ984", "SIN"),
    ("14:30", "9G (W16114)", "BKK"), ("15:05", "9G720", "SIN"), ("15:30", "AK547", "KUL"),
    ("15:35", "9G451", "ICN"), ("15:55", "VZ982", "BKK"),
    ("16:50", "VJ845", "TPE"), ("17:00", "AK662", "DMK"), ("17:40", "TR524", "SIN"),
    ("17:55", "9G750", "KUL"), ("18:05", "UO596", "HKG"), ("18:25", "VJ985", "HKG"),
    ("18:35", "9G501", "HKG"), ("20:25", "9G511", "TPE"), ("21:00", "LJ91", "ICN"),
    ("21:25", "7C2315", "ICN"), ("22:25", "ZE981", "PUS"), ("22:50", "KE485", "ICN"),
]

# Ghế theo TỪNG HÃNG. Dùng một con số phẳng 180 là sai: 9G và VJ — 12/25 chuyến ở PQC
# — đều bay A321. [V] = đã xác minh bằng nguồn; [~] = ước tính thận trọng, nên tra lại khi có dịp.
SEATS_BY = {
    "9G": 217,   # [V] 3xA320neo 174 + 2xA321 220 + 6xA321neo 236-240 -> binh quan doi bay
    "VJ": 230,   # [V] A321-200ext/neo = 230; VJ quoc te gan nhu luon A321
    "AK": 180,   # [~] AirAsia A320
    "FD": 180,   # [~] Thai AirAsia A320
    "VZ": 180,   # [~] Thai Vietjet A320
    "UO": 190,   # [~] HK Express A320neo/A321neo pha tron
    "TR": 186,   # [~] Scoot A320neo
    "7C": 189,   # [~] Jeju B737-800
    "LJ": 189,   # [~] Jin Air B737-800
    "ZE": 189,   # [~] Eastar B737-800
    "KE": 160,   # [~] Korean Air B737-8 tuyen nghi duong
    "SU": 220, "KC": 180, "HY": 220, "C6": 180, "HH": 180,   # [~] charter Nga/Trung A
}
SEATS_DEFAULT = 190          # hang la: lay binh quan than trong, va BAO trong bao cao

LOAD, FOREIGN = 0.85, 0.85
# FOREIGN = ty le khach phai qua QUAY TAY (khach Viet di autogate). 0.85 la tham so
# HIEU CHUAN, khong phai so do -- xem muc "Hieu chuan" trong skill.
MONTH_UPLIFT = 1.05                      # hệ số mùa của tháng cần tính (xem bảng dưới)
WALK = (8, 20)                           # phút từ lúc đỗ chèn tới lúc vào hàng
PROC_SEC = 70                            # giây xử lý mỗi khách (quét QR PAI + đóng dấu + kiểm vé đi tiếp)
BASE_DAY, BASE_NIGHT, SURGE, SURGE_AT = 7, 5, 2, 200   # so quay mo (DA HIEU CHUAN); +2 khi hang >= 200
FT = 10                                  # cam kết Fast Track: ~10 phút, mọi khung
TAXI = 5                                 # cham banh -> do chen. Con so tren trang do tu CHAM BANH,
                                         # con gio trong lich bay la gio vao bai. Phan di bo da nam
                                         # trong WALK roi, KHONG cong them lan nua.
GRID_COUNTERS, GRID_PROC = (6, 7, 8), (60, 70, 80)
GRID_FOREIGN = (0.80, 0.85, 0.90)        # 27 kich ban: 3 quay x 3 ty le ngoai x 3 toc do
TIER_MOD, TIER_BUSY = 50, 70             # phân bậc theo con số HIỂN THỊ:
                                         # <50 "Usually quick" · 50-69 "Moderate" · >=70 "Busy"

OBSERVED_PEAK = (45, 60)                 # phut xep hang o cao diem, theo bao cao thuc dia.
                                         # Dung lam CONG HIEU CHUAN -- xem build_month_json.


def seats_of(flight_no):
    for code, n in SEATS_BY.items():
        if flight_no.startswith(code):
            return n
    return SEATS_DEFAULT


BANDS = [("00:00-06:00", 0, 6), ("06:00-10:00", 6, 10), ("10:00-13:00", 10, 13),
         ("13:00-16:00", 13, 16), ("16:00-20:00", 16, 20), ("20:00-24:00", 20, 24)]


def minute(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def simulate(proc_sec=None, base_day=None, surge=None, uplift=None, foreign=None):
    # Giai tri mac dinh phai lay LUC GOI, khong phai luc dinh nghia ham. Viet
    # uplift=MONTH_UPLIFT trong chu ky ham se dong bang gia tri tai thoi diem import,
    # nen doi M.MONTH_UPLIFT tu ben ngoai se bi lo di khong bao loi.
    proc_sec = PROC_SEC if proc_sec is None else proc_sec
    base_day = BASE_DAY if base_day is None else base_day
    surge = SURGE if surge is None else surge
    uplift = MONTH_UPLIFT if uplift is None else uplift
    foreign = FOREIGN if foreign is None else foreign
    horizon = 30 * 60
    arrivals = [[] for _ in range(horizon)]
    for i, (t, fl, _) in enumerate(FLIGHTS):
        pax = seats_of(fl) * LOAD * foreign * uplift
        a, b = WALK
        for m in range(a, b):                      # khách rải đều ra trong khoảng đi bộ
            arrivals[minute(t) + m].append((i, pax / (b - a)))
    queue = deque()
    wait_sum = [0.0] * len(FLIGHTS)
    pax_sum = [0.0] * len(FLIGHTS)
    worst = [0.0] * len(FLIGHTS)
    for t in range(horizon):
        for f, n in arrivals[t]:
            queue.append([f, t, n])
        qlen = sum(c[2] for c in queue)
        hour = (t // 60) % 24
        counters = base_day if 6 <= hour < 24 else max(2, base_day - 2)
        if qlen >= SURGE_AT:
            counters += surge
        cap = counters * 60.0 / proc_sec
        while cap > 1e-9 and queue:
            f, joined, n = queue[0]
            take = min(n, cap)
            w = t - joined
            wait_sum[f] += take * w
            pax_sum[f] += take
            # Do từ GIỜ TRONG LỊCH BAY, không phải từ lúc vào hàng. Khách cuối cùng
            # vào hàng ở phút thứ 19 sau khi hạ cánh, nên đo từ lúc vào hàng rồi cộng
            # một BUFFER 15 phẳng là thiếu đúng 4 phút, và đếm hai lần phần đi bộ.
            worst[f] = max(worst[f], t - minute(FLIGHTS[f][0]))
            cap -= take
            if take >= n - 1e-9:
                queue.popleft()
            else:
                queue[0][2] -= take
    rows = []
    for name, h0, h1 in BANDS:
        idx = [i for i, (t, _, _) in enumerate(FLIGHTS) if h0 * 60 <= minute(t) < h1 * 60]
        p = sum(pax_sum[i] for i in idx)
        avg = sum(wait_sum[i] for i in idx) / p if p else None
        rows.append({"band": name, "flights": len(idx),
                     "avg_wait": None if avg is None else round(avg, 1),
                     "worst_wait": None if not idx else round(max(worst[i] for i in idx)),
                     "pax": round(p)})
    tot_p = sum(pax_sum)
    return rows, sum(wait_sum) / tot_p, tot_p


def build_month_json(month, month_label, month_notes, empty_band_note, context, basis, cities, guide):
    """month='2026-10', month_label='October 2026'."""
    import itertools
    central_rows, _, central_pax = simulate()
    grid = [simulate(proc_sec=p, base_day=c, foreign=fo)
            for p, c, fo in itertools.product(GRID_PROC, GRID_COUNTERS, GRID_FOREIGN)]

    def q(vals, lo=0.25, hi=0.75):                 # tứ phân vị -> khoảng, không lấy min/max
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
        return {"window": "|".join(f"{a}-{z}" for a, z in runs),
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
        "schema": "paf-wait/3.0", "site": "PAF", "airport": "PQC", "month": month,
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
                        "seats": {f: seats_of(f) for _, f, _ in FLIGHTS},
                        "counters_day": BASE_DAY, "counters_night": BASE_NIGHT,
                        "surge_counters": SURGE, "surge_queue": SURGE_AT, "taxi_min": TAXI,
                        "seats_by_carrier": True, "calibrated_to": list(OBSERVED_PEAK),
                        "grid_counters": list(GRID_COUNTERS), "grid_processing_sec": list(GRID_PROC)},
        "sample_flights": [{"time": t, "flight": f, "from": o} for t, f, o in FLIGHTS],
    }
