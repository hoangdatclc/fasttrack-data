"""Lich chuyen QUOC TE DEN DAD, mot ngay THU TU tieu bieu thang 10/2026.

Dung lai tu: airportia (bang arrivals + trang tung chuyen), airportinfo.live, flightsfrom.
Da loc theo NGAY TRONG TUAN = thu Tu. Da loai codeshare va ma GDS ao
(A1xxxx A.P.G., W2xxxx Flexflight, H1xxxx Hahn Air, W1xxxx World Ticket).

(gio ha canh, so hieu, san bay di, loai tau bay, ghe)
Ghe lay theo cau hinh pho bien cua chinh hang tren tuyen do; [?] = uoc tinh.
"""

SCHEDULE_SEASON = "S2026"   # mua IATA cua danh sach chuyen DUOI DAY.
# Dung lai danh sach cho mua khac thi PHAI sua dong nay cung luc. run_month.py co
# cong chan doi chieu no voi thang dang dung va DUNG HAN neu lech (them 07/10/2026).

FLIGHTS = [
    # --- rang sang ---
    ("00:25", "TW13",   "ICN", "B737-800",   189),
    ("01:10", "BX7315", "PUS", "A321",       220),
    # --- sang ---
    ("07:30", "5J5758", "MNL", "A321",       230),
    ("07:35", "Z2822",  "MNL", "A320",       180),
    ("08:45", "Z2826",  "MNL", "A320",       180),
    ("09:00", "CI787",  "TPE", "A321neo",    188),
    ("09:20", "UO552",  "HKG", "A321",       230),
    ("09:30", "FD634",  "DMK", "A320",       180),
    ("09:40", "VJ879",  "ICN", "A321",       230),
    ("09:55", "TR510",  "SIN", "A321neo",    236),
    ("09:55", "VZ964",  "BKK", "A321",       230),
    ("10:10", "VJ989",  "PUS", "A321",       230),
    ("10:45", "TW7",    "ICN", "B737MAX8",   189),
    ("10:50", "AK642",  "KUL", "A320",       180),
    ("11:05", "SQ172",  "SIN", "B737MAX8",   154),   # SIA 2 khoang, ghe it hon LCC
    ("11:05", "UO566",  "HKG", "A321",       230),
    ("11:30", "FD636",  "DMK", "A320",       180),
    ("11:35", "BR383",  "TPE", "A330-300",   309),
    ("11:50", "AK648",  "KUL", "A320",       180),
    ("12:05", "OD502",  "KUL", "B737MAX8",   162),
    ("12:10", "7C2211", "ICN", "B737-800",   189),
    ("12:25", "VN337",  "KIX", "A321",       203),   # VNA 2 khoang
    ("12:30", "VZ960",  "BKK", "A321",       230),
    ("12:40", "VN319",  "NRT", "A321",       203),
    # --- chieu ---
    ("13:10", "VJ970",  "SIN", "A321",       230),
    ("13:40", "MH748",  "KUL", "B737MAX8",   162),
    ("13:50", "VN431",  "ICN", "A321",       203),
    ("13:50", "KE2093", "PUS", "B737-900",   159),
    ("14:20", "KE457",  "ICN", "A321neo",    182),
    ("15:20", "HX548",  "HKG", "A320",       174),
    ("15:20", "PR585",  "MNL", "A321",       199),
    ("15:30", "KR739",  "PNH", "ATR72",       70),
    ("15:35", "AK640",  "KUL", "A320",       180),
    ("15:55", "SQ174",  "SIN", "B737MAX8",   154),
    ("16:00", "K6840",  "SAI", "ATR72",       70),
    ("17:25", "UO558",  "HKG", "A321",       230),
    ("17:30", "VZ962",  "BKK", "A321",       230),
    ("17:40", "FD638",  "DMK", "A320",       180),
    ("18:10", "IT585",  "KHH", "A320",       180),
    # --- toi: cum Han Quoc ---
    ("19:45", "VN626",  "BKK", "A321",       203),
    ("20:30", "NX978",  "MFM", "A321neo",    198),
    ("21:01", "KE459",  "ICN", "A330-300",   276),
    ("21:30", "5J5756", "MNL", "A321",       230),
    ("21:42", "OZ755",  "ICN", "A321neo",    188),
    ("21:50", "EK370",  "BKK", "B777-300ER", 354),
    ("22:05", "NX986",  "MFM", "A320",       174),
    ("23:40", "RS511",  "ICN", "A321",       205),   # [V] airportia 02/10/2026: di ICN 20:55, den DAD 23:40,
                                                        # 6 chuyen/tuan (T2,3,4,5,7,CN), A321 205 ghe toan pho thong.
                                                        # Hai lan doc truoc (00:04 / 00:25) la gio ha THUC TE mot dem
                                                        # bi tre, khong phai gio lich -- da xep nham sang khung 0-6.
    ("23:15", "LJ81",   "ICN", "B737-800",   189),
    ("23:33", "ZE593",  "ICN", "B737-800",   189),
    ("23:50", "BX773",  "PUS", "A321",       220),
    ("23:55", "LJ111",  "PUS", "B737-800",   189),
    ("23:55", "RF531",  "CJJ", "A320",       180),
    ("23:55", "TW29",   "TAE", "B737-800",   189),
]

# KHONG co trong lich thu Tu (ghi lai de thang sau khong phai tra lai):
#   VN433 ICN (T2,3,5,6,7,CN) · MH746 KUL (T3,5,7) · CI789 TPE (T2,3,6,CN)
#   TR518 SIN (T3,7,CN) · JX703 TPE (T2,3,5,6,CN) · IT551 TPE (T2,3,5,6,7) · 8M454 RGN (T2,T6)
# LOAI vi dang ngo: WE201 ICN -- hai nguon ghi hang "Thai Smile", hang nay da sap nhap
#   vao Thai Airways tu 2024 va tuyen ICN-DAD vo ly ve mang bay. Nhieu kha nang loi gan hang.
# RS511: gio lich DA XAC MINH 23:40 (truoc do dung nham 00:00 tu bang live).
# THIEU gio ha canh, chua dua vao (lam THIEU, khong lam THUA):
#   K6842 PNH · TW25 CJJ (T2,T6) · VN317 NRT (T2,5,7,CN)
# YP621 Air Premia ICN: tam dung 15/07-24/10/2026, dung la khong co dau thang 10.
# DAD KHONG co duong bay thang toi Trung Quoc dai luc -- da kiem ba nguon.
