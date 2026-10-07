"""Lich chuyen QUOC TE DEN DAD, mot ngay THU TU tieu bieu thang 11/2026 (mua dong W2026).

Dung lai tu: aeroroutes (thong bao NW26), flight.info (lich co CUA SO HIEU LUC theo mua),
flightsfrom (ngay trong tuan + loai tau bay), flightconnections (tuyen theo mua),
trip.com / airportia (gio tung chuyen), mainlymiles, danangfantasticity, Emirates.com.
Da loc theo NGAY TRONG TUAN = thu Tu. Da loai codeshare va ma GDS ao
(A1xxxx A.P.G., W2xxxx Flexflight, H1xxxx Hahn Air, W1xxxx World Ticket).

(gio ha canh, so hieu, san bay di, loai tau bay, ghe)
Ghe lay theo cau hinh pho bien cua chinh hang tren tuyen do.

NHAN TUNG DONG -- muc do chac chan cho MUA DONG W2026:
  [W-OK]  xac nhan cho mua dong: co nguon noi ro hieu luc tu 25/10/2026 tro di.
  [W-RT]  TUYEN xac nhan con bay mua dong, nhung GIO / SO HIEU lay tu lich he S2026.
  [CARRY] khong co xac nhan mua dong nao -- bung nguyen tu S2026.
Nhan la nhan cua CA DONG: dong nao co mot thanh phan phai bung thi nhan tut xuong
muc yeu nhat cua dong do, ghi chu noi ro thanh phan nao da xac nhan.
"""

SCHEDULE_SEASON = "W2026"   # mua IATA cua danh sach chuyen DUOI DAY.
# Dung lai danh sach cho mua khac thi PHAI sua dong nay cung luc. run_month.py co
# cong chan doi chieu no voi thang dang dung va DUNG HAN neu lech (them 07/10/2026).
# Doi S2026 -> W2026 ngay 07/10/2026 cung luc voi viec dung lai danh sach duoi day.

FLIGHTS = [
    # --- rang sang ---
    ("00:25", "TW13",   "ICN", "B737-800",   189),   # [CARRY]
    ("01:10", "BX7315", "PUS", "A321",       220),   # [W-RT] aeroroutes BX NW26 (21/07/2026) khong co
                                                     # thay doi nao cho DAD -> tuyen giu nguyen mua dong.
    # --- sang ---
    ("07:30", "5J5758", "MNL", "A321",       230),   # [CARRY] flightsfrom tuan 42 ghi T3/T5/T7 -- LECH
                                                     # voi thu Tu. Giu theo S2026, xem §LECH NGUON.
    ("07:35", "Z2822",  "MNL", "A320",       180),   # [CARRY] flightsfrom: T2/T4/T6 -> co thu Tu.
    ("08:45", "Z2826",  "MNL", "A320",       180),   # [CARRY] flightsfrom: T3/T5/T7 -- LECH voi thu Tu.
    ("09:00", "CI787",  "TPE", "A321neo",    188),   # [CARRY]
    ("09:20", "UO552",  "HKG", "A321",       230),   # [CARRY]
    ("09:30", "FD634",  "DMK", "A320",       180),   # [CARRY]
    ("09:40", "VJ879",  "ICN", "A321",       230),   # [W-RT] aeroroutes 02/10/2026: DAD-ICN GIAM 7 -> 4
                                                     # chuyen/tuan tu 25/10 den 05/12/2026. Khong nguon nao
                                                     # noi 4 ngay nao -> thu Tu la PHONG DOAN. Xem §LECH NGUON.
    ("09:55", "TR510",  "SIN", "A321neo",    236),   # [CARRY]
    ("09:55", "VZ964",  "BKK", "A321",       230),   # [CARRY]
    ("10:10", "VJ989",  "PUS", "A321",       230),   # [CARRY]
    ("10:45", "TW7",    "ICN", "B737MAX8",   189),   # [CARRY]
    ("10:50", "AK642",  "KUL", "A320",       180),   # [CARRY]
    ("11:05", "SQ172",  "SIN", "B737MAX8",   154),   # [W-RT] SIA NW26: 3 chuyen/ngay, toan B737-8 MAX;
                                                     # hai chuyen cu giu nguyen gio (mainlymiles 16/09/2026).
    ("11:05", "UO566",  "HKG", "A321",       230),   # [CARRY]
    ("11:30", "FD636",  "DMK", "A320",       180),   # [CARRY]
    ("11:40", "BR383",  "TPE", "A321",       194),   # [W-OK] flight.info: cua so 25/10/2026-27/03/2027 la
                                                     # A321 194 ghe, den 11:40. He S2026 la A330-300 309 ghe,
                                                     # den 11:35. HA TAI 115 ghe -- doi lon nhat trong khung sang.
    ("11:50", "AK648",  "KUL", "A320",       180),   # [CARRY]
    ("12:05", "OD502",  "KUL", "B737MAX8",   162),   # [CARRY]
    ("12:10", "7C2211", "ICN", "B737-800",   189),   # [CARRY]
    ("12:25", "VN337",  "KIX", "A321",       203),   # [CARRY] VNA 2 khoang
    ("12:30", "VZ960",  "BKK", "A321",       230),   # [CARRY]
    ("12:40", "VN319",  "NRT", "A321",       203),   # [CARRY]
    # --- chieu ---
    ("13:10", "VJ970",  "SIN", "A321",       230),   # [W-OK] aeroroutes 02/10/2026: DAD-SIN giam 14 -> 7
                                                     # chuyen/tuan tu 25/10 (10 tu 18/11, 12 tu 04/12). 7/tuan
                                                     # = MOI NGAY mot chuyen -> dung mot dong nhu S2026.
    ("13:40", "MH748",  "KUL", "B737MAX8",   162),   # [CARRY]
    ("13:50", "VN431",  "ICN", "A321",       203),   # [CARRY]
    ("13:50", "KE2093", "PUS", "B737-900",   159),   # [CARRY]
    ("13:55", "VN698",  "BKK", "A321",       203),   # [W-OK] CHUYEN MOI. aeroroutes 04/09/2026: VNA them
                                                     # chuyen BKK-DAD thu hai moi ngay tu 25/10/2026,
                                                     # VN698 BKK1215-1355DAD A321.
    ("14:20", "KE457",  "ICN", "A330-300",   276),   # [W-RT] TAU BAY xac nhan mua dong: aeroroutes 03/09/2026
                                                     # "eff 25OCT26 1 of 2 daily KE457/458 A330-300 replaces
                                                     # 787-9". GIO 14:20 bung tu S2026 -- khong tra duoc gio
                                                     # mua dong. Ban S2026 ghi A321neo 182 ghe, khong khop
                                                     # voi 787-9 ma aeroroutes noi la tau bay he -> mot trong
                                                     # hai nguon sai ve mua he; ca hai deu dan ve A330-300
                                                     # cho mua dong.
    ("15:20", "HX548",  "HKG", "A320",       174),   # [CARRY]
    ("15:20", "PR585",  "MNL", "A321",       199),   # [CARRY] flightsfrom tuan 42: T4/T6 di 13:50 -> co thu Tu.
    ("15:30", "KR739",  "PNH", "ATR72",       70),   # [CARRY] NGHI VAN: trip.com ghi KR739 PNH-DAD di 09:55
                                                     # den 12:10 (khong phai 15:30) va chuyen 05/10 bi HUY;
                                                     # flightsfrom ghi Cambodia Airways tren tuyen nay
                                                     # "begins 2026-10-26". Giu theo S2026, 70 ghe nen anh
                                                     # huong nho. Xem §LECH NGUON.
    ("15:35", "AK640",  "KUL", "A320",       180),   # [CARRY]
    ("15:55", "SQ174",  "SIN", "B737MAX8",   154),   # [W-RT] xem SQ172.
    ("17:25", "UO558",  "HKG", "A321",       230),   # [CARRY]
    ("17:30", "VZ962",  "BKK", "A321",       230),   # [CARRY]
    ("17:40", "FD638",  "DMK", "A320",       180),   # [CARRY]
    ("17:55", "QZ480",  "DPS", "A320",       180),   # [CARRY] CHUYEN MOI trong file nay, nhung la tuyen MO
                                                     # TU 20/03/2026 -- ban S2026 BO SOT. Indonesia AirAsia
                                                     # Bali-DAD, 4 chuyen/tuan T2/T4/T6/CN, A320 180 ghe,
                                                     # di 14:15 den 17:55 (danangfantasticity + thebalisun).
                                                     # Khong co xac nhan nao cho mua dong.
    ("18:10", "IT585",  "KHH", "A320",       180),   # [W-RT] flightconnections: KHH-DAD la tuyen theo mua
                                                     # "October-March" -> dung la chuyen cua mua dong.
    ("18:45", "SQ176",  "SIN", "B737MAX8",   154),   # [W-OK] CHUYEN MOI. SIA tang DAD tu 14 len 21
                                                     # chuyen/tuan (2.156 -> 3.234 ghe/tuan) trong cua so
                                                     # 25/10/2026-27/03/2027; chuyen them la SQ176 SIN17:00 -
                                                     # DAD18:45, B737-8 MAX (mainlymiles 16 va 20/09/2026).
    # --- toi: cum Han Quoc + cum toi mo rong ---
    ("20:00", "K6840",  "SAI", "A320",       180),   # [W-OK] flight.info: cua so 25/10/2026-27/03/2027 la
                                                     # SAI18:50 - DAD20:00, A320 180 ghe, moi ngay. He S2026
                                                     # la SAI14:05 - DAD16:00 ATR72 72 ghe. aeroroutes
                                                     # 08/09/2026 doc lap: "Siem Reap - Da Nang eff 25OCT26
                                                     # A320 replaces ATR72, 1 daily". DOI GIO 4 TIENG +
                                                     # THEM 110 GHE, vao dung dau cum cao diem toi.
    ("20:05", "VN626",  "BKK", "A321",       203),   # [W-OK] aeroroutes 04/09/2026: VN626 BKK1825-2005DAD
                                                     # A321, MOI NGAY tu 25/10/2026. He S2026: den 19:45,
                                                     # 6 chuyen/tuan.
    ("20:30", "NX978",  "MFM", "A321neo",    198),   # [W-RT] flightconnections: MFM-DAD theo mua
                                                     # "October-March" -> chuyen cua mua dong.
    ("20:43", "WE201",  "ICN", "A330-200",   294),   # [W-RT] CHUYEN MOI trong file nay. Ban S2026 LOAI SAI
                                                     # dong nay: ma WE gio la cua PARATA AIR (Han Quoc),
                                                     # khong phai Thai Smile. Parata mo ICN-DAD 24/11/2025,
                                                     # 7 chuyen/tuan, A330 294 ghe (Da Nang Airport /
                                                     # routesonline + Air Cargo Week); trip.com: di 18:30
                                                     # den 20:43, A330-200 294 ghe, co bay thu Tu va thu Nam;
                                                     # FlightAware xac nhan PTA201 ICN-DAD. GHE LON NHAT
                                                     # trong cum Han Quoc. Khong co xac nhan rieng cho mua dong.
    ("21:30", "5J5756", "MNL", "A321",       230),   # [CARRY] flightsfrom tuan 42: moi ngay.
    ("21:40", "KE459",  "ICN", "A330-300",   278),   # [W-OK] flight.info: cua so 25/10-16/12/2026 la
                                                     # ICN18:40 - DAD21:40, A330-300 278 ghe. He S2026:
                                                     # ICN18:20 - DAD21:05. DAY 35 PHUT VAO GIUA CUM TOI.
    ("21:42", "OZ755",  "ICN", "A321neo",    188),   # [CARRY] Asiana chi hop nhat vao Korean Air ngay
                                                     # 17/12/2026 -> thang 11 van bay (Business Traveller).
                                                     # directflights ghi Asiana "ends October 2026" --
                                                     # LECH, xem §LECH NGUON. trip.com ghi A330-300; giu
                                                     # A321neo theo S2026 + flightsfrom.
    ("21:50", "EK370",  "BKK", "B777-300ER", 354),   # [W-OK] aeroroutes 01/10/2026 (bai ve cua so
                                                     # 25/10-30/11/2026) ghi Emirates "also operates ...
                                                     # 4 weekly Dubai - Bangkok Suvarnabhumi - Da Nang with
                                                     # 777-300ER" -> tuyen + tau bay dung trong thang 11.
                                                     # Ngay bay T2/T4/T6/CN theo flight.info -> co thu Tu
                                                     # (airportia ghi T2/T6/CN, xem §LECH NGUON).
    ("22:05", "NX986",  "MFM", "A320",       174),   # [W-RT] xem NX978.
    ("23:15", "LJ81",   "ICN", "B737-800",   189),   # [CARRY] aeroroutes CO bai "Jin Air NW26 International
                                                     # Flight Number Changes" (30/06/2026) nhung bi 429 sau
                                                     # bon lan goi -> KHONG doc duoc so hieu moi. Giu LJ81.
    ("23:33", "ZE593",  "ICN", "B737-800",   189),   # [CARRY]
    ("23:40", "RS511",  "ICN", "A321",       205),   # [CARRY] aeroroutes CO bai "Air Seoul NW26 Flight Number
                                                     # Changes" (14/08/2026), bi 429 sau nam lan goi.
                                                     # directflights (tuan 02-08/11/2026) ghi so hieu la RS95
                                                     # di 20:55 -- MOT nguon, va chinh nguon do con goi Parata
                                                     # Air la "Thai Smile", nen khong du de doi. Giu RS511.
    ("23:50", "BX773",  "PUS", "A321",       220),   # [W-RT] xem BX7315.
    ("23:55", "LJ111",  "PUS", "B737-800",   189),   # [CARRY]
    ("23:55", "RF531",  "CJJ", "A320",       180),   # [W-RT] flightconnections: CJJ-DAD theo mua
                                                     # "October-March"; flightsfrom: RF531 bay T4/T5/T7/CN
                                                     # -> co thu Tu.
    ("23:55", "TW29",   "TAE", "B737-800",   189),   # [W-RT] flightconnections: TAE-DAD theo mua
                                                     # "October-March"; flightsfrom: TW29 bay T4-CN
                                                     # -> co thu Tu.
]

# =====================================================================
# KHONG DUA VAO -- va ly do. Nguyen tac giu nguyen: lam THIEU, khong lam THUA.
# =====================================================================
# KHONG co trong lich thu Tu (ghi lai de thang sau khong phai tra lai):
#   VN433 ICN (T2,3,5,6,7,CN) · MH746 KUL (T3,5,7) · CI789 TPE (T2,3,6,CN)
#   TR518 SIN (T3,7,CN) · JX703 TPE (T2,3,5,6,CN) · IT551 TPE (T2,3,5,6,7) · 8M454 RGN (T2,T6)
#   TW25 CJJ (T2,T6 -- flightsfrom tuan 42 xac nhan lai)
# THIEU gio ha canh mua dong, chua dua vao:
#   K6842 PNH -- aeroroutes 08/09/2026: PNH-DAD cung doi ATR72 -> A320 180 ghe tu 25/10/2026,
#     1 chuyen/ngay. flightsfrom (tuan 36) ghi thu Tu di 11:00, bay 2h00-2h15, nhung K6840
#     cung tuyen do DOI GIO 4 TIENG khi vao mua dong, nen gio he KHONG suy ra duoc gio dong.
#     Day la khoan THIEU lon nhat cua danh sach nay: 180 ghe quanh trua.
#   VN317 NRT (T2,5,7,CN)
# YP621 Air Premia ICN (di 17:45 den 20:40, 787-9, 4 chuyen/tuan x125 -> CO thu Tu):
#   tam dung 15/07-24/10/2026 theo thong bao cua chinh hang, tuc dung han dung hom truoc
#   ngay doi mua. KHONG nguon nao xac nhan bay lai tu 25/10; trip.com ngay 07/10/2026 van
#   ghi chuyen la "da bi huy". Khong dua vao. Neu hang mo lai, day la 1 chuyen 309 ghe
#   roi dung vao dau cum toi -- kiem lai dau thang 12.
# Z2824 MNL (den 15:20, A320 180, T2/T4/T6/CN, mo 20/03/2026): KHONG con trong lich tuan 42
#   cua flightsfrom -> coi nhu da dung. Luu y PR585 cung den 15:20 tu MNL; neu sau nay tim
#   lai duoc Z2824 thi phai kiem xem ban S2026 co ghi nham Z2824 thanh PR585 hay khong.
# Thai Airways BKK-DAD: aeroroutes 20/07/2026 -- khai thac lai THANG 12/2026, KHONG phai 11.
# VietJet DAD-KIX: aeroroutes 14/08/2026 -- mo THANG 12/2026, KHONG phai 11.
# Chuyen thue chuyen Nga/CIS (VietJet + Crystal Bay/Anex): chi chay 04-10/2026,
#   khong co mua dong (danangfantasticity).
# DAD KHONG co duong bay thang toi Trung Quoc dai luc -- flightconnections 07/10/2026 khong
#   liet ke diem nao o dai luc. He so thang GIU 1.00.
#
# =====================================================================
# §LECH NGUON -- cac cho hai nguon noi khac nhau, DE NGUYEN de doi
# =====================================================================
# 1. Ngay trong tuan cua 5J5758 va Z2826 (MNL): flightsfrom tuan 42 ghi T3/T5/T7, tuc
#    KHONG co thu Tu. Ban S2026 (dung airportia tung chuyen) co ca hai vao thu Tu.
#    Neu flightsfrom dung thi danh sach nay THUA 410 ghe trong khung 06:00-10:00.
# 2. VJ879 ICN: biet chac giam ve 4 chuyen/tuan trong thang 11, khong biet 4 ngay nao.
# 3. EK370: flight.info T2/T4/T6/CN (4/tuan, khop con so cua aeroroutes) va airportia
#    T2/T6/CN (3/tuan). Lay ban 4/tuan vi aeroroutes xac nhan "4 weekly".
# 4. OZ755: directflights ghi Asiana "ends October 2026"; Business Traveller ghi ngay hop
#    nhat la 17/12/2026. Lay 17/12 -> thang 11 con bay.
# 5. KR739: ba nguon, ba cau tra loi khac nhau (xem ghi chu tai dong).
# 6. So hieu mua dong cua Jin Air va Air Seoul: aeroroutes tra 429 lien tuc, khong doc duoc.
