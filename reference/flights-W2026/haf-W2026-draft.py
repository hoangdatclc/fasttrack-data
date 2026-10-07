# -*- coding: utf-8 -*-
"""Lich chuyen QUOC TE DEN HAN, mot ngay THU TU tieu bieu thang 11/2026 (mau: thu Tu 18/11/2026, mua lich dong W2026).

VI SAO NGAY 18/11: mua IATA doi 25/10/2026, nen moi dong trong file nay la lich DONG.
Chon thu Tu giua thang vi no la ngay DUY NHAT nam sau TAT CA cac moc mo tuyen dau
thang (VN968 Ahmedabad 03/11, VJ Cebu 10/11, VJ Taichung ha xuong 5 chuyen/tuan 06/11)
va TRUOC hai moc cuoi thang (Asiana ICN-HAN ha tu 2 xuong 1 chuyen/ngay 22/11-17/12;
Cebu Pacific CRK-HAN mo lai 20/11). 18/30 ngay cua thang khop cau hinh nay.

NGUON (da fetch that, 10/2026):
  aeroroutes.com/eng/260904-6enw26han   IndiGo them Mumbai-HAN NW26 (6E1637, hang ngay, 25/10)
  aeroroutes.com/eng/260804-canw26vn    Air China them chuyen 2 PEK-HAN (CA883 00:05-03:00, 25/10)
  aeroroutes.com/eng/260902-keoznw26int KE ICN-HAN doi sang 1 A330-300 + 1 B777-300ER; OZ 2->1/ngay 22/11-17/12
  aeroroutes.com/eng/260710-vnnw26as    VN tang KIX va TPE 7 -> 11 chuyen/tuan (VN335/339, VN577/579)
  aeroroutes.com/eng/261001-vnnov26amd  VN968 AMD-HAN hoan sang 03/11/2026, 4 chuyen/tuan
  aeroroutes.com/eng/261002-vjnov26int  VJ ha tan suat thang 11-12 (6 tuyen tu HAN)
  aeroroutes.com/eng/260824-vjnw26tnn + nomadlawyer.org/vietjet-direct-hanoi-tainan-flights-2026
                                        VJ HAN-TNN 4 chuyen/tuan (2-4-6-CN) tu 25/10
  aeroroutes.com/eng/260928-eknw26han   EK chuyen 2 (EK388) chi tu 01/12/2026; EK394 doi A350 tu 01/01/2027
  aeroroutes.com/eng/260817-eynw26sea   EY AUH-HAN 10 -> 14 chuyen/tuan CHI tu 16/12/2026
  aeroroutes.com/eng/251125-tknw26ea    TK IST-HAN NW26 10 chuyen/tuan A350-900
  aeroroutes.com/eng/260803-vjnw26ceb   VJ HAN-CEB 3 chuyen/tuan tu 10/11 -> DUOI nguong 4 ngay/tuan, LOAI
  aeroroutes.com/eng/260914-9gnw26cn    9G them tuyen Trung Quoc nhung KHONG qua HAN
  aeroroutes.com/eng/260816-lynw26han   El Al dong ban ve HAN tu cuoi 10/2026 (khong co trong danh sach cu)
  flightsfrom.com/HAN, /HYD-HAN, /HAN-TNN; flightconnections.com/flights-from-han-to-tnn
  en.wikipedia.org/wiki/Noi_Bai_International_Airport
  vietnamnews.vn (VN82/83 AMS-HAN 3 chuyen/tuan), prg.aero (VJ PRG-ALA-HAN 2 chuyen/tuan),
  businesstraveller.com (5J CRK-HAN mo lai 20/11, 3 chuyen/tuan)

GIU NGUYEN LUAT LOC CUA BAN S2026: bo codeshare, bo noi dia, bo bong GDS
(A1xxxx/W2xxxx/H1xxxx/W1xxxx), bo chuyen < 4 ngay/tuan. Vi luat cuoi nay ma BA tuyen
dong moi KHONG vao danh sach: VJ HAN-CEB (3/tuan), 5J CRK-HAN (3/tuan tu 20/11),
VJ PRG-ALA-HAN (2/tuan), VN984 HYD-HAN (3/tuan), VN82 AMS-HAN (3/tuan).

NHAN DO CHAC CHAN -- tung dong, dong CARRY khong ghi nhan:
  [W-OK]  22 dong co nhan, trong do 15 dong la W-OK: co cong bo NW26 dich danh
          (them tuyen, doi tau bay, doi gio, hoac ha tan suat ma van >= 4 ngay/tuan).
  [W-RT]  7 dong: tuyen/tan suat/tau bay duoc xac nhan cho mua dong, nhung GIO HA CANH
          lay tu lich he vi cong bo khong kem gio.
  [CARRY] 104 dong con lai: KHONG co cong bo rieng cho mua dong. Day la phan YEU NHAT
          cua danh sach -- bang den tra hom nay (07/10/2026) van la lich HE, nen cac
          dong nay la lich he duoc mang sang. Phan lon la tuyen chay ca nam (Trung Quoc,
          Dong Nam A, Nhat, Dai Loan) nen rui ro chu yeu la lech gio +-15 phut,
          khong phai tuyen bien mat.

Cong 2 (san luong): 26.838 ghe x LOAD 0,85 = 22.812 khach den/ngay vs moc ~22.250
-> 102,5% (nguong 85-110%). So chuyen 126 vs moc ~120 -> +5,0%.
Phan bo khung: 00-06 = 14/2.705 · 06-10 = 15/3.465 · 10-13 = 22/4.859 ·
13-16 = 27/5.751 · 16-20 = 25/5.045 · 20-24 = 23/5.013.
"""
# (gio ha canh, so hieu, san bay di, loai tau bay, so ghe)
_RAW = [
    ("00:15", "VN616", "BKK", "A321", 184),
    ("00:20", "HO1329", "PVG", "A320", 180),
    ("00:45", "PR595", "MNL", "A321", 199),
    ("01:05", "5J746", "MNL", "A321neo", 236),
    ("01:10", "ZH107", "SZX", "A320", 158),
    ("01:20", "MU5075", "PVG", "B737-800", 162),
    ("01:30", "CA707", "HGH", "A320", 158),
    ("02:45", "9G411", "ICN", "A321neo", 203),
    ("03:00", "CA883", "PEK", "A321", 177),       # [W-OK] MOI 25/10/2026 - Air China them chuyen thu hai PEK-HAN
    ("03:05", "VJ7527", "CAN", "A321", 230),
    ("03:35", "VN968", "AMD", "A321", 184),       # [W-OK] MOI 03/11/2026 - Ahmedabad, 4 chuyen/tuan (hoan tu 25/10)
    ("03:55", "VJ7713", "PKX", "A320", 180),
    ("04:50", "VJ7239", "PVG", "A320", 180),
    ("05:25", "VN980", "DEL", "B787-9", 274),
    ("06:05", "VN36", "FRA", "B787-9", 274),
    ("06:40", "VN18", "CDG", "A350-900", 305),
    ("07:15", "QR982", "DOH", "B787-9", 311),
    ("07:20", "AI2390", "DEL", "A320neo", 180),
    ("07:20", "EY432", "AUH", "B787-9", 299),     # [W-RT] NW26 10 chuyen/tuan; tang len 14 chi tu 16/12/2026
    ("07:35", "VN646", "MNL", "A321", 184),
    ("07:40", "5J744", "MNL", "A321neo", 236),
    ("08:25", "AK516", "KUL", "A320", 180),
    ("08:30", "FD642", "DMK", "A320", 180),
    ("08:50", "UO540", "HKG", "A321neo", 236),
    ("08:55", "VJ963", "ICN", "A321", 230),       # [W-OK] VJ ha ICN 14 -> 11 chuyen/tuan 25/10-06/12; 4/7 ngay van co 2 chuyen -> giu ca hai
    ("09:35", "TG560", "BKK", "A320", 168),
    ("09:40", "ZH101", "SZX", "A320", 158),
    ("09:50", "VN579", "TPE", "A321", 184),       # [W-OK] DOI 09:30 -> 09:50 (lich NW26)
    ("09:55", "CX741", "HKG", "B777-300ER", 340),
    ("10:00", "6E1637", "BOM", "A321neo", 232),   # [W-OK] MOI 25/10/2026 - IndiGo Mumbai, hang ngay
    ("10:05", "CZ3049", "CAN", "A320neo", 180),
    ("10:10", "JX715", "TPE", "A330-900", 297),
    ("10:20", "VN587", "KHH", "A321", 184),
    ("10:30", "CI791", "TPE", "A330-300", 307),
    ("10:35", "KE441", "ICN", "A330-300", 276),   # [W-RT] DOI A321neo -> A330-300 tu 25/10/2026 (gio giu cua mua he)
    ("10:40", "VJ981", "PUS", "A321", 230),
    ("10:50", "6E1633", "DEL", "A321neo", 232),
    ("11:00", "CA703", "PVG", "A321", 177),
    ("11:05", "BR397", "TPE", "B777-300ER", 333),
    ("11:30", "SQ192", "SIN", "A350-900", 253),
    ("11:50", "FD640", "DMK", "A320", 180),
    ("11:55", "CA741", "PEK", "A321neo", 185),    # [W-OK] lich NW26 xac nhan PEK 09:00 - HAN 11:55 hang ngay, giu nguyen
    ("12:00", "QP625", "BOM", "B737MAX8", 189),
    ("12:15", "MH752", "KUL", "B737MAX8", 160),
    ("12:15", "OZ729", "ICN", "A330-300", 290),   # [W-RT] NW26 van 2 chuyen/ngay; 22/11-17/12 ha con 1 (ngay dai dien 18/11 chua giam)
    ("12:20", "VJ939", "KIX", "A321", 230),       # [W-OK] VJ ha KIX 11 -> 9 -> 7 chuyen/tuan nhung CHI den 16/11; 18/11 da ve 11
    ("12:20", "VN349", "NGO", "A321", 184),
    ("12:30", "OD571", "KUL", "B737MAX8", 162),
    ("12:30", "VN357", "FUK", "A321", 184),
    ("12:50", "VJ921", "NGO", "A321", 230),
    ("12:50", "ZH121", "CAN", "B737-800", 164),
    ("13:05", "VJ933", "NRT", "A321", 230),
    ("13:10", "VN311", "NRT", "B787-9", 274),
    ("13:15", "EK394", "DXB", "B777-300ER", 354),  # [W-RT] NW26 van B777-300ER; A350-900 chi tu 01/01/2027. Chuyen thu hai EK388 tu 01/12/2026 -> KHONG tinh cho thang 11
    ("13:15", "VN429", "PUS", "B787-9", 274),
    ("13:35", "VJ961", "ICN", "A321", 230),       # [W-OK] VJ ha ICN 14 -> 11 chuyen/tuan 25/10-06/12
    ("13:35", "VN335", "KIX", "A350-900", 305),   # [W-OK] DOI 13:00 -> 13:35, B787-9 -> A350-900 (lich NW26)
    ("13:40", "CZ8083", "SZX", "A320neo", 180),
    ("13:55", "QR976", "DOH", "B787-9", 311),
    ("13:55", "VN610", "BKK", "A321", 184),
    ("14:00", "MU6011", "PVG", "A321", 177),
    ("14:00", "VJ1943", "TNN", "A321", 230),      # [W-OK] MOI 25/10/2026 - Tainan, 4 chuyen/tuan (2-4-6-CN), so hieu SUY RA tu VJ1942
    ("14:05", "ZH103", "SZX", "A320", 158),
    ("14:15", "9G531", "HKG", "A321neo", 203),
    ("14:20", "AK512", "KUL", "A320", 180),
    ("14:40", "MF859", "XMN", "B737-800", 170),
    ("14:45", "CZ8315", "CAN", "A320neo", 180),
    ("14:45", "MU9605", "KMG", "A320", 158),
    ("14:50", "FD870", "CNX", "A320", 180),
    ("14:55", "SQ196", "SIN", "B737MAX8", 154),
    ("15:20", "MF8697", "FOC", "B737-800", 170),
    ("15:25", "VN577", "TPE", "A321", 184),       # [W-OK] MOI - VN tang TPE 7 -> 11 chuyen/tuan tu 25/10/2026
    ("15:30", "QV311", "VTE", "A320", 158),
    ("15:35", "VN593", "HKG", "A321", 184),
    ("15:35", "VN660", "SIN", "A321", 184),
    ("15:40", "TK164", "IST", "A350-900", 329),   # [W-RT] NW26 10 chuyen/tuan A350-900 (NW25: 7 A350 + 3 B787-9)
    ("15:45", "CZ8469", "SZX", "A320neo", 180),
    ("15:50", "VJ902", "BKK", "A321", 230),
    ("16:05", "VU136", "BKK", "A321", 220),
    ("16:50", "BR385", "TPE", "B777-300ER", 333),
    ("16:50", "CA755", "PVG", "A321", 177),
    ("16:50", "CI793", "TPE", "A330-300", 307),
    ("16:55", "MF8713", "NKG", "B737-800", 170),
    ("17:25", "PN6423", "CKG", "A320", 186),
    ("17:25", "ZH105", "SZX", "A320", 158),
    ("17:30", "VN507", "CAN", "A321", 184),
    ("17:40", "SQ194", "SIN", "B737MAX8", 154),
    ("17:45", "MU6013", "PVG", "A321", 177),
    ("17:55", "MF8011", "PKX", "B737-800", 170),
    ("17:55", "VN614", "BKK", "A321", 184),
    ("18:10", "CX743", "HKG", "B777-300ER", 340),
    ("18:15", "VJ928", "CGK", "A321", 230),
    ("18:25", "VN533", "PVG", "A350-900", 305),
    ("18:30", "QV313", "LPQ", "ATR72", 70),
    ("18:35", "K6850", "KTI", "A320", 174),
    ("18:40", "CZ8177", "CAN", "A320neo", 180),
    ("18:40", "VN513", "PEK", "A321", 184),
    ("18:45", "6E1631", "CCU", "A321neo", 232),
    ("19:15", "VN339", "KIX", "A321", 184),       # [W-OK] MOI - VN tang KIX 7 -> 11 chuyen/tuan tu 26/10/2026
    ("19:40", "TG564", "BKK", "A320", 168),
    ("19:50", "VJ949", "RMQ", "A321", 230),       # [W-OK] VJ ha RMQ 11 -> 7 -> 5 chuyen/tuan (5 tu 06/11) 25/10-09/12
    ("19:50", "VN836", "SAI", "A321", 184),
    ("19:55", "8M450", "RGN", "A319", 144),
    ("20:05", "CZ8359", "CSX", "A320neo", 180),
    ("20:05", "VJ935", "NRT", "A321", 230),
    ("20:05", "VN385", "HND", "B787-9", 274),
    ("20:20", "FD644", "DMK", "A320", 180),
    ("20:30", "AK518", "KUL", "A320", 180),
    ("20:35", "VJ947", "KHH", "A321", 230),       # [W-OK] VJ ha KHH 10 -> 5 chuyen/tuan 27/10-09/12
    ("20:35", "VN415", "ICN", "A350-900", 305),
    ("20:40", "VN930", "LPQ", "A321", 184),
    ("20:55", "VJ943", "TPE", "A321", 230),
    ("21:05", "VN618", "BKK", "A321", 184),
    ("21:20", "VN786", "SYD", "A350-900", 305),
    ("21:35", "KE447", "ICN", "B777-300ER", 291),  # [W-RT] DOI A321neo -> B777-300ER tu 25/10/2026 (gio giu cua mua he)
    ("21:35", "VJ998", "DPS", "A321", 230),       # [W-OK] VJ ha DPS 7 -> 4 chuyen/tuan 02/11-07/12 -- van >= 4 nen giu
    ("21:35", "VN920", "VTE", "A321", 184),
    ("21:45", "NX950", "MFM", "A321", 174),
    ("21:50", "JL751", "NRT", "B767-300", 199),
    ("22:00", "OZ733", "ICN", "A330-300", 290),   # [W-RT] NW26 van 2 chuyen/ngay; 22/11-17/12 ha con 1
    ("22:10", "VN922", "KTI", "A321", 184),
    ("22:15", "NH897", "NRT", "B787-9", 246),
    ("22:20", "3U3905", "TFU", "A320", 180),
    ("22:20", "VN680", "KUL", "A321", 184),
    ("23:00", "CZ371", "CAN", "A320neo", 180),
    ("23:45", "7C2201", "ICN", "B737-800", 189),]

# Mo hinh chi can (gio, so hieu, san bay di, so ghe). Giu loai tau bay rieng de tra nguoc.
SCHEDULE_SEASON = "W2026"   # mua IATA cua danh sach chuyen O TREN (doi 07/10/2026 cung luc
# voi viec dung lai danh sach cho mua dong). run_month.py co cong chan doi chieu no voi
# thang dang dung va DUNG HAN neu lech.

FLIGHTS = [(t, f, o, seats) for t, f, o, _ac, seats in _RAW]
AIRCRAFT = {f: ac for _t, f, _o, ac, _s in _RAW}
