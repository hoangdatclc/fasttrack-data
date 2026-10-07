# -*- coding: utf-8 -*-
"""Lich chuyen QUOC TE den SGN (Tan Son Nhat) - NGAY DAI DIEN, mua DONG W2026 (11/2026).

NGUON GOC: ban S2026 (ngay dai dien 14/10/2026, 145 chuyen / 31.857 ghe) da doi chieu
tung phut voi ban hien truong airportia/avionio 03/10/2026. Ban nay DAP cac thay doi
mua dong W2026 (hieu luc 25/10/2026) len tren ban do, tung thay doi mot nguon dat ten.

NGAY DAI DIEN: mot ngay THU TRONG TUAN (Tue-Thu) thang 11/2026. Giu dung luat cu:
chi lay chuyen chay >= 4 NGAY/TUAN. Ra 147 chuyen / 32.108 ghe -- lech +1,4% chuyen va
+0,8% ghe so voi moc 145/31.857, trong nguong +-20% o cuoi sgn_queue_model.py.

NHAN TUNG DONG (bulk theo khoi, dem that o duoi):
  [W-OK]  = lich dong DA CONG BO dich danh cho chuyen nay (moi, mo lai, doi gio, doi may
            bay, hoac tan suat duoc neu ten trong mot thong bao NW26/Nov-2026 co ngay).
  [W-RT]  = SUY RA cho mua dong tu mot thong bao co lien quan nhung KHONG neu ten dong nay.
  [CARRY] = khong tra duoc nguon W2026 -> bo nguyen tu ban S2026 da kiem hien truong.

  [W-OK]   24 dong
  [W-RT]    3 dong  (TR502/TR552/TR516 -- xem muc 6)
  [CARRY]  120 dong

----------------------------------------------------------------------
THAY DOI SO VOI S2026 -- tung muc mot nguon
----------------------------------------------------------------------
1. THEM 9G635 PVG0415-0740SGN, A321neo 236 ghe, HANG NGAY tu 25/10/2026.  [W-OK]
   TUYEN MOI HOAN TOAN cua Sun PhuQuoc Airways (SGN-Shanghai Pu Dong).
   Nguon: aeroroutes.com/eng/260914-9gnw26cn (14/09/2026), trich nguyen van
   "9G635 PVG0415 - 0740SGN 32Q D".

2. THEM SQ188 SIN2150-2300SGN, 737-8 MAX 154 ghe, HANG NGAY tu 25/10/2026. [W-OK]
   Singapore Airlines len chuyen thu TU moi ngay tren SIN-SGN.
   Nguon 1: aviationa2z.com 18/09/2026. Nguon 2: mainlymiles.com 16/09/2026
   (ca hai doc lap deu ghi SQ188 21:50-23:00, 737-8 MAX 154 ghe, 25/10/2026-27/03/2027).

3. THEM VJ1884 CNX1630-1845SGN, A321 214 ghe, 4 CHUYEN/TUAN tu 25/10/2026. [W-OK]
   VietJet MO LAI SGN-Chiang Mai (lan cuoi chay den 02/2024).
   Nguon: aeroroutes.com/eng/260810-vjnw26as, trich "VJ1884 CNX1630 - 1845SGN 321 x246".
   x246 = tru Thu 3/5/7 -> chay Mon/Wed/Fri/Sun = 4 ngay/tuan, DU nguong >= 4.

4. BO MOT VONG VJ SGN-SIN (3 chuyen/ngay -> 2 chuyen/ngay, 25/10-07/12/2026). [W-RT]
   Nguon: aeroroutes.com/eng/261002-vjnov26int (02/10/2026), trich "Ho Chi Minh City -
   Singapore: Reduce from 3 to 2 daily (except selected dates)".
   THONG BAO KHONG NEU TEN vong nao bi cat. Da bo VJ812 (20:45) -- vong muon nhat trong
   ba. Day la SUY LUAN, khong phai so cong bo: muc GIAM la co nguon, DANH TINH vong bi
   cat thi khong. Neu sau nay biet that la VJ882 hay VJ814, doi mot dong la xong
   (ca ba cung 214 ghe, lech chi la GIO ha canh).

5. DOI GIO / DOI MAY BAY -- bay dong, moi dong mot nguon co ngay 25/10/2026:  [W-OK]
   SQ178  10:55 -> 11:00, 337 -> 154 ghe (737-8 MAX thay 787-10)
   SQ184  14:45 -> 15:00, 337 -> 253 ghe (A350-900 LH 42J/24W/187Y)
   SQ186  18:30 -> 18:40, giu 337 ghe (787-10)
     Nguon gio: aeroroutes.com/eng/260611-sqnw26sgn ("SQ178 SIN0950 - 1100SGN 7M8 D",
     "SQ184 SIN1350 - 1500SGN 359 D", "SQ186 SIN1730 - 1840SGN 787 D").
     SO GHE KIEM DUOC BANG PHEP CONG, khong phai doan: aviationa2z ghi tuan SGN tut
     6.489 -> 6.286 ghe va khoang business 798 -> 686. Giai ra:
        truoc  (337 + X + 337) x 7 = 6.489  -> X = 253   va  (36 + B + 36) x 7 = 798 -> B = 42
        sau    154 + 253 + 337 + 154 = 898,  898 x 7 = 6.286   KHOP CHINH XAC
               business 10 + 42 + 36 + 10 = 98,  98 x 7 = 686   KHOP CHINH XAC
     42J + 24W + 187Y = 253 dung dung cau hinh A350-900 long-haul cua SQ. Hai dang thuc
     khop khong du cho mot con so doan. (mainlymiles ghi SQ184 la "78J/237Y = 315" --
     SQ KHONG co cau hinh A350 nao nhu vay va 315 lam vo ca hai phep cong tren, nen
     da BO con so do, giu 253.)
   CA903  PEK, 167 -> 176 ghe (737-8 MAX thay 737-800, 8J/168Y).
     Nguon: aeroroutes.com/eng/260804-canw26vn -- "Beijing Capital - Ho Chi Minh City
     to be operated by 737 MAX 8 from 25OCT26, replacing -800".
   VJ82   MEL, 06:10 -> 05:55 (5 chuyen/tuan thay vi 7 nhu filed ban dau).
     Nguon: aeroroutes.com/eng/260915-vjnw26mel -- "VJ082 MEL0130 - 0555SGN 330 x47",
     "From 25OCT26 to 27MAR27 the airline will maintain 5 weekly flights".
   JX711  TPE, 242 -> 306 ghe (A350-900 thay A330-900neo; 4F/26J/36W/240Y = 306)
   JX713  TPE, 242 -> 297 ghe (A330-900neo thay A321neo; 28J/269Y = 297)
     Nguon lich: aeroroutes.com/eng/260604-jxnw26sea (hieu luc 25/10/2026).
     Nguon cau hinh: onemileatatime (A350-900 = 306), seatcompare (A330-900neo = 297).

6. SCOOT: da doc THONG BAO NW26 cua Scoot (aeroroutes.com/eng/260919-trnw26, 19/09/2026)
   -- no liet ke Clark, Hat Yai, Kota Kinabalu, Phuket, Phu Quoc, Tiruchirappalli va
   KHONG he co SGN. Nen TR502/TR552/TR516 giu nguyen gio va ghe. Nhan [W-RT] chu KHONG
   phai [W-OK]: "khong co trong thong bao" la suy ra, khong phai lich cong bo.

7. VIETNAM AIRLINES chau A: aeroroutes.com/eng/260710-vnnw26as (NW26 Asia increases)
   chi tang HAN-KIX va HAN-TPE, KHONG co dong nao tu SGN. Cac tuyen VN tu SGN [CARRY].
   VN620 HKT la ngoai le [W-OK]: co thong bao tang tan suat NW26 rieng cho Phuket va
   flightsfrom.com/HKT-SGN hom nay cho dung 5 chuyen/tuan, dep 18:45 -> ve 20:50,
   A321 184 ghe -- KHOP TUNG PHUT voi dong dang co.

8. CAC TUYEN VJ BI GIAM nhung VAN >= 4 chuyen/tuan nen O LAI ngay dai dien   [W-OK]
   (tat ca deu duoc NEU TEN trong aeroroutes.com/eng/261002-vjnov26int):
     BKK 4->3 chuyen/ngay · PUS 7->5/tuan · DPS 14->11/tuan · HKG 7->4/tuan
     KHH 7->4/tuan · HKT 7->5/tuan (4 tu 06/11/2026) · RMQ 7->4/tuan
     AMD 7->6->5/tuan
   VJ808 HKT kiem cheo doc lap: flightsfrom.com/HKT-SGN cho dep 11:55 Mon/Wed/Fri/Sun
   (dung 4 chuyen/tuan), bay 2h05 -> ve 14:00. KHOP TUNG PHUT voi dong dang co.

----------------------------------------------------------------------
DA XET VA CO CHU Y KHONG DUA VAO
----------------------------------------------------------------------
- VJ1871 CRK0640-0810SGN (Clark) MOI tu 10/11/2026, va VJ SGN-Cebu MOI tu 10/11/2026:
  CA HAI chi 3 CHUYEN/TUAN -> DUOI nguong >= 4 ngay/tuan cua ngay dai dien, nen KHONG
  co trong danh sach. Nguon: aeroroutes.com/eng/260810-vjnw26as ("VJ1871 CRK0640 -
  0810SGN 321 246" = Tue/Thu/Sat, 3 weekly).
  LUU Y: skill cua du an ghi "CNX va CEB bat dau 25-26/10" -- SAI voi Cebu. Cebu bat
  dau 10/11/2026, khong phai 26/10. Da dung ngay THAT.
- MU KMG-SGN tang 7 -> 11 chuyen/tuan tu 25/10/2026 (aeroroutes.com/eng/260918-munw26kmg).
  11/tuan = mot vong hang ngay + MOT VONG THU HAI 4 chuyen/tuan, tuc DU nguong. Nhung
  KHONG tra duoc so hieu lan gio cua vong thu hai: flightsfrom.com/KMG-SGN hom nay chi
  liet ke MU9633. Khong bia -> danh sach nay THIEU khoang 1 chuyen / 158 ghe o khung
  chieu-toi. Day la huong THAP, khong phai cao.
- Air Premia SGN: aeroroutes.com/eng/260828-ypdec26sgn DOI ngay mo lai sang THANG 12/2026
  (ban 10/08 ghi thang 11). Nen THANG 11 KHONG co -> khong them.
- Arkia: aeroroutes.com/eng/260825-iznw26sgn -- da HUY ke hoach bay SGN trong NW26.
- Turkish TK: aeroroutes.com/eng/260702-tk1q27as tang 10 -> 11 chuyen/tuan va doi gio
  (TK162 ve 16:30) nhung hieu luc 07/02/2027, SAU thang 11. TK162 giu 15:50 [CARRY].
- LONG THANH (VVLT): mo thuong mai 01/12/2026, KHONG phai thang 11. Pha 1 chi nhan
  long-haul moi + tuyen moi; toan bo duong bay quoc te dang co cua SGN o LAI SGN het
  thang 11. Hai nguon doc lap: travelmole.com/news/vietnam-traffic-transfer-long-thanh-airport
  va vietone.travel/long-thanh-airport-travel-agents. => THANG 11/2026 LA THANG CUOI
  CUNG SGN con nguyen 100% hang quoc te den. Khong tru dong nao.

(gio_ha_canh, so_hieu, san_bay_di, so_ghe)
"""

SCHEDULE_SEASON = "W2026"   # mua IATA cua danh sach chuyen DUOI DAY.
# Dung lai danh sach cho mua khac thi PHAI sua dong nay cung luc. run_month.py co
# cong chan doi chieu no voi thang dang dung va DUNG HAN neu lech (them 07/10/2026).

FLIGHTS = [
    ("00:05", "5J751", "MNL", 236),
    ("00:20", "NH833", "NRT", 257),
    ("00:25", "VJ861", "ICN", 214),
    ("00:30", "HO1327", "PVG", 164),
    ("00:35", "CX721", "HKG", 286),
    ("00:55", "CZ8473", "SZX", 182),
    ("00:58", "CZ8317", "WUH", 174),
    ("01:00", "MU869", "HGH", 158),
    ("01:05", "CA903", "PEK", 176),
    ("01:40", "CZ6089", "CAN", 182),
    ("01:50", "MU281", "PVG", 177),
    ("02:15", "ZH117", "SZX", 171),
    ("03:20", "9G401", "ICN", 236),
    ("04:30", "VJ3909", "CAN", 214),
    ("04:40", "MU2839", "NKG", 158),
    ("04:55", "VJ859", "MNL", 214),
    ("04:57", "VJ84", "BNE", 373),
    ("05:00", "VU8601", "SZX", 216),
    ("05:15", "VJ3949", "PKX", 180),
    ("05:15", "VN10", "CDG", 304),
    ("05:25", "VN99", "SFO", 304),
    ("05:50", "VJ3901", "PVG", 214),
    ("05:55", "VJ82", "MEL", 373),
    ("06:00", "VJ1802", "BLR", 214),
    ("06:00", "VN649", "MNL", 184),
    ("06:20", "JL79", "HND", 211),
    ("06:25", "VN30", "FRA", 308),
    ("06:30", "VJ1806", "AMD", 214),
    ("06:50", "VJ821", "HND", 214),
    ("07:10", "VJ884", "BOM", 214),
    ("07:30", "VN670", "CMB", 184),
    ("07:40", "9G635", "PVG", 236),
    ("08:05", "AK1490", "JHB", 180),
    ("08:05", "K6812", "KTI", 72),
    ("08:10", "AK520", "KUL", 183),
    ("08:15", "TR502", "SIN", 236),
    ("08:50", "PR591", "MNL", 190),
    ("09:10", "FD656", "DMK", 208),
    ("09:20", "TG550", "BKK", 156),
    ("09:40", "VN581", "KHH", 184),
    ("09:50", "CI781", "TPE", 325),
    ("10:05", "MH750", "KUL", 174),
    ("10:15", "BR395", "TPE", 321),
    ("10:15", "CX767", "HKG", 348),
    ("10:15", "JX711", "TPE", 306),
    ("10:20", "VN571", "TPE", 184),
    ("10:30", "AE1857", "RMQ", 174),
    ("10:40", "OZ731", "ICN", 290),
    ("10:50", "CZ8159", "CAN", 182),
    ("11:00", "SQ178", "SIN", 154),
    ("11:15", "K6808", "SAI", 72),
    ("11:30", "K6838", "KOS", 72),
    ("11:30", "MF893", "XMN", 172),
    ("11:50", "VJ869", "PUS", 214),
    ("11:55", "BR391", "TPE", 321),
    ("12:10", "AK528", "KUL", 183),
    ("12:15", "KE471", "ICN", 278),
    ("12:20", "CZ6077", "PVG", 189),
    ("12:40", "VN517", "PKX", 184),
    ("12:50", "VN343", "NGO", 184),
    ("13:02", "AK1502", "PEN", 180),
    ("13:05", "VN600", "BKK", 184),
    ("13:15", "VJ802", "BKK", 180),
    ("13:25", "VJ823", "NRT", 214),
    ("13:30", "CZ8465", "SZX", 182),
    ("13:30", "VJ829", "KIX", 214),
    ("13:40", "VN423", "PUS", 308),
    ("13:45", "VN409", "ICN", 312),
    ("14:00", "QR970", "DOH", 358),
    ("14:00", "VJ808", "HKT", 214),
    ("14:00", "VN307", "NRT", 312),
    ("14:00", "VN321", "KIX", 304),
    ("14:25", "VN650", "SIN", 184),
    ("14:40", "CZ373", "CAN", 182),
    ("14:40", "TR552", "SIN", 236),
    ("14:40", "VJ826", "KUL", 214),
    ("14:50", "VJ863", "ICN", 214),
    ("14:50", "VJ885", "KHH", 214),
    ("15:00", "SQ184", "SIN", 253),
    ("15:10", "VN583", "KHH", 184),
    ("15:15", "VN921", "KTI", 184),
    ("15:20", "FD654", "DMK", 208),
    ("15:35", "K6816", "KTI", 72),
    ("15:35", "MH758", "KUL", 174),
    ("15:35", "VJ1814", "KUL", 214),
    ("15:45", "AK522", "KUL", 183),
    ("15:50", "TK162", "IST", 330),
    ("16:10", "VJ92", "PER", 214),
    ("16:10", "VN604", "BKK", 184),
    ("16:10", "VU130", "BKK", 216),
    ("16:15", "VJ86", "SYD", 373),
    ("16:15", "VN772", "SYD", 304),
    ("16:15", "VN780", "MEL", 304),
    ("16:20", "CI783", "TPE", 325),
    ("16:40", "K6824", "SAI", 72),
    ("16:40", "VJ882", "SIN", 214),
    ("16:42", "VJ854", "CGK", 214),
    ("16:50", "VJ848", "DPS", 214),
    ("16:55", "JX713", "TPE", 297),
    ("17:02", "VN630", "CGK", 184),
    ("17:15", "TR516", "SIN", 236),
    ("17:15", "VN503", "CAN", 184),
    ("17:25", "VJ894", "DPS", 214),
    ("17:30", "CX769", "HKG", 334),
    ("17:30", "VJ800", "BKK", 197),
    ("18:00", "VJ853", "RMQ", 214),
    ("18:05", "9C7347", "CAN", 180),
    ("18:07", "MU9633", "KMG", 158),
    ("18:25", "MH766", "KUL", 174),
    ("18:40", "SQ186", "SIN", 337),
    ("18:45", "QR971", "KTI", 358),
    ("18:45", "VJ1884", "CNX", 214),
    ("18:45", "VN525", "PVG", 308),
    ("18:50", "VN640", "DPS", 184),
    ("19:10", "VJ814", "SIN", 214),
    ("19:20", "TG556", "BKK", 156),
    ("19:40", "VN654", "SIN", 184),
    ("19:55", "AI2388", "DEL", 165),
    ("20:05", "EK392", "DXB", 307),
    ("20:30", "VN678", "KUL", 184),
    ("20:40", "VN595", "HKG", 184),
    ("20:45", "AK524", "KUL", 183),
    ("20:50", "VN620", "HKT", 184),
    ("20:50", "VN812", "SAI", 184),
    ("21:05", "FD658", "DMK", 208),
    ("21:05", "VN403", "ICN", 184),
    ("21:10", "JQ61", "SYD", 333),
    ("21:10", "VJ1832", "VTE", 214),
    ("21:15", "VN606", "BKK", 184),
    ("21:20", "CA407", "CKG", 167),
    ("21:20", "K6828", "SAI", 72),
    ("21:35", "VJ843", "TPE", 214),
    ("21:45", "VJ877", "HKG", 214),
    ("22:00", "KE475", "ICN", 278),
    ("22:00", "MF841", "XMN", 172),
    ("22:10", "BR381", "TPE", 321),
    ("22:10", "K6818", "KTI", 72),
    ("22:15", "CZ367", "CAN", 182),
    ("22:15", "JL759", "NRT", 211),
    ("22:15", "VN656", "SIN", 184),
    ("22:25", "3U3903", "TFU", 194),
    ("22:25", "UA152", "HKG", 240),
    ("22:35", "NH891", "HND", 320),
    ("22:40", "OZ735", "ICN", 290),
    ("22:45", "VN608", "BKK", 184),
    ("22:55", "KE479", "ICN", 278),
    ("23:00", "SQ188", "SIN", 154),
]
