# -*- coding: utf-8 -*-
"""Lich chuyen QUOC TE den CXR (Cam Ranh) - NGAY DAI DIEN, mua DONG W2026 (11/2026).

====================================================================
VI SAO CXR KHONG DUNG "MOT NGAY THU TU CU THE" NHU DAD VA PQC
====================================================================
O DAD/PQC, ban lich mot ngay thuong lay tu nguon GDS la DU. O CXR thi KHONG:

  1. MANG CHARTER NGA KHONG NAM TRONG GDS. Azur Air chay chuong trinh mua dong
     2026/27 tu BAY thanh pho Nga BAT DAU TU THANG 11 (Moskva 3 chuyen/12 ngay,
     Samara 2/12 ngay, Mineralnye Vody - Tyumen - Omsk - Perm - Chelyabinsk moi
     noi 1/12 ngay) = ~10 chuyen/12 ngay ~ 0,83 chuyen/ngay. Nordwind chay
     18-22 chuyen/thang (~340 khach/chuyen, than rong). Khong hang nao trong so
     do ban ve qua GDS theo lich co dinh.
  2. NGAY TRONG TUAN KHONG ON DINH. Charter doi ngay theo tung tuan; cac nguon
     mau thuan nhau ngay tren cung mot chuyen. Chot cung mot thu la OVERFIT.

=> Dung NGAY DAI DIEN: moi tuyen gop vao theo DUNG TY LE tan suat thang cua no,
   roi roi rac hoa thanh chuyen rieng le sao cho (a) so chuyen ~ tong ty le, va
   (b) tong ghe ~ tong ghe ky vong. Gio ha canh deu la gio THAT da cong bo hoac
   da quan sat, KHONG co gio nao bia ra.

====================================================================
COT MOC DOI CHIEU (cong 2) - DAY LA RANG BUOC CHINH
====================================================================
  2024 (chinh thuc, Bao Khanh Hoa): 6,8 trieu luot khach, QUOC TE 4,2 trieu,
        noi dia 2,6 trieu, 40.044 chuyen bay.
  2025: khach quoc te ~4,69 trieu (+7%).
  HAN QUOC (so chinh thuc Cam Ranh International Terminal, cong bo khi Parata Air
        khai truong): ICN 67 + PUS 29 + TAE 14 + CJJ 14 = 124 chuyen/tuan, cong
        Parata 4/tuan -> "19 chuyen Han moi ngay". 124/7 = 17,7 chuyen DEN/ngay.
        Danh sach duoi day co 17 chuyen Han -> lech 4%, trong nguong.
  TONG QUOC TE: bao chi dan so san bay cho ~38 chuyen quoc te DEN/ngay vao
        thang 1/2026 (dinh mua dong), va dip 01-04/01/2026 co 321 luot bay quoc
        te trong 4 ngay = 80 luot/ngay = ~40 chuyen den/ngay. Thang 10 (chuyen
        mua) la 28. Thang 11 nam GIUA: 32 la diem giua co can cu, khong phai
        ngoai suy.

GIO = gio ha canh THEO LICH, gio dia phuong CXR (UTC+7). KHONG dung gio ha canh thuc te.

DA LOAI: chuyen noi dia; codeshare OZ95xx/KE5055/DL78xx/VN34xx/VN35xx/CI87xx/
AF92xx/3U7091; bong GDS A1xxxx (A.P.G.) W2xxxx (Flexflight) H1xxxx (Hahn Air)
W1xxxx (World Ticket).
DA LOAI RIENG CHO THANG 11: VietJet Cam Ranh - Singapore. Tuyen nay CO THAT va la
  mot bo sung NW26, nhung aeroroutes chot ngay khai truong 11/12/2026 -> THANG 11
  CHUA BAY. Khong duoc dua vao danh sach thang 11.

====================================================================
SUA MOT LOI CUA BAN S2026 -- WE205 KHONG PHAI CODESHARE AO
====================================================================
Ban S2026 loai WE205 ICN-CXR voi ly do "Thai Smile da sap vao Thai Airways 2024
-> codeshare ao". SAI. WE205 la chuyen cua PARATA AIR, hang hang khong Han Quoc
thu 11 bay den Khanh Hoa; chinh trang chu san bay Cam Ranh cong bo chuyen khai
truong WE205 ha canh 21:50, A320, 4 chuyen/tuan (Tu-Nam-Bay-CN). aeroroutes
cung xac nhan Parata giu ICN-CXR 4 chuyen/tuan sang mua he NS26 -> tuyen chay
lien tuc qua mua dong. Da dua vao lai.

(gio_ha_canh, so_hieu, san_bay_di, loai_tau_bay, so_ghe)
"""

SCHEDULE_SEASON = "W2026"   # mua IATA cua danh sach chuyen DUOI DAY (bat dau 25/10/2026).
# Dung lai danh sach cho mua khac thi PHAI sua dong nay cung luc. run_month.py co
# cong chan doi chieu no voi thang dang dung va DUNG HAN neu lech (them 07/10/2026).

# NHAN NGUON tung dong, dung mot trong ba muc:
#   [W-OK]  co bang chung TRUC TIEP cho mua dong W2026 (thong bao hang / san bay).
#   [W-RT]  TUYEN duoc xac nhan ton tai trong mua dong, nhung so hieu / gio lay tu
#           ban quan sat mua he -> co the doi so hieu khi vao mua.
#   [CARRY] chuyen cua ban S2026 mang sang, KHONG tim duoc xac nhan rieng cho mua
#           dong. Giu lai vi tuyen la tuyen quanh nam va mua dong la CAO DIEM cua
#           chinh thi truong do; nhung day la phan KHONG KIEM CHUNG duoc.

FLIGHTS = [
    # ================= CUM DEM HAN QUOC - dac diem lon nhat cua CXR =================
    # 12 chuyen Han ha canh trong 4 tieng 30 phut 20:20-00:35. Khong san bay nao
    # trong mang nay co cum dac nhu vay.
    ("00:10", "TW41", "PUS", "B737-800", 189),   # [W-RT] T'way PUS-CXR 4 ch/tuan; aeroroutes xac nhan tuyen chi tam dung 03/06-12/07/2026
    ("00:35", "7C2303", "ICN", "B737-800", 189),   # [CARRY] Jeju Air B737-800, hang ngay
    ("20:20", "BX787", "ICN", "A321", 195),   # [CARRY] Air Busan A321, hang ngay
    ("21:50", "WE205", "ICN", "A320", 180),   # [W-OK] Parata Air 4 ch/tuan - gio 21:50 do san bay Cam Ranh cong bo
    ("22:30", "TW33", "ICN", "B737-800", 189),   # [W-OK] T'way giu 1 chuyen/ngay ICN-CXR (aeroroutes)
    ("22:30", "RF557", "CJJ", "A320", 180),   # [W-RT] Aero K CJJ-CXR hang ngay (bao VN 11/2025)
    ("22:50", "TW37", "TAE", "B737-800", 189),   # [W-RT] T'way TAE-CXR 4 ch/tuan
    ("22:55", "RS527", "ICN", "A321", 195),   # [CARRY] Air Seoul A321 - aeroroutes co muc "Air Seoul NW26 Flight Number Changes", KHONG doc duoc (429)
    ("22:55", "LJ115", "PUS", "B737-800", 188),   # [CARRY] Jin Air B737-800 - xem ghi chu SO HIEU NW26
    ("23:05", "KE467", "ICN", "A330-300", 276),   # [W-OK] Korean Air 1 ch/ngay, A330-300, hieu luc 25/10/2026-28/02/2027 (aeroroutes 03/09/2026)
    ("23:45", "LJ87", "ICN", "B737-800", 189),   # [CARRY] Jin Air B737-800 - xem ghi chu SO HIEU NW26
    ("23:55", "ZE561", "ICN", "B737-8", 189),   # [CARRY] Eastar Jet B737-8, hang ngay
    # ================= HAN QUOC BAN NGAY (tau bay Viet quay dau) =================
    ("09:55", "VJ835", "ICN", "A321", 214),   # [CARRY] VietJet A321, hang ngay (KHONG nam trong dot giam ICN thang 11 cua VJ)
    ("10:00", "VN441", "ICN", "A321", 184),   # [CARRY] Vietnam Airlines A321, hang ngay
    ("10:55", "VN435", "PUS", "A321", 184),   # [CARRY] Vietnam Airlines A321, hang ngay (mo 06/2025)
    ("11:00", "VJ871", "TAE", "A321", 214),   # [W-RT] VietJet TAE-CXR: so hieu + gio 07:50 TAE -> 11:00 CXR tu aeroroutes, tuyen MO TRONG MUA DONG NW24
    ("13:35", "VJ919", "PUS", "A321", 214),   # [W-OK] VietJet PUS-CXR GIAM 7 -> 4 ch/tuan tu 03/11 den 04/12/2026 (aeroroutes 02/10/2026)
    # ================= TRUNG QUOC =================
    ("10:00", "CZ8475", "CAN", "B737-800", 174),   # [CARRY] China Southern B737-800
    ("15:10", "CZ6049", "CAN", "B737-800", 174),   # [CARRY] China Southern B737-800
    ("17:50", "3U3939", "TFU", "A32X", 165),   # [CARRY] Sichuan Airlines A32X
    # ================= DONG NAM A - lap day khung giua trua =================
    ("10:00", "FD646", "DMK", "A320", 180),   # [CARRY] Thai AirAsia A320
    ("11:30", "TR548", "SIN", "E190-E2", 112),   # [CARRY] Scoot E190-E2 (mo 21/11/2025, 2->5 ch/tuan cao diem)
    ("12:30", "AK204", "KUL", "A320neo", 186),   # [CARRY] AirAsia A320neo
    ("13:30", "VZ968", "BKK", "B737", 191),   # [CARRY] Thai Vietjet B737, hang ngay
    # ================= NGA / SNG - CAO DIEM MUA DONG, nhieu THAN RONG =================
    ("04:00", "SU830", "OVB", "A330-300", 307),   # [W-RT] Aeroflot Novosibirsk 2 ch/tuan - gio 04:00 la vong thu Sau trong lich aeroroutes
    ("07:30", "KC193", "ALA", "A321neo", 169),   # [CARRY] Air Astana A321neo - xem ghi chu AIR ASTANA
    ("09:30", "SU294", "SVO", "A350-900", 316),   # [CARRY] Aeroflot Moskva, hang ngay
    ("11:20", "ZF2555", "MRV", "B767-300", 336),   # [W-RT] Azur Air - dai dien chuong trinh charter mua dong 7 thanh pho
    ("12:00", "N4CHTR", "SVO", "B777-200", 340),   # [W-RT] Nordwind - dai dien 18-22 chuyen/thang. Xem GHI CHU GHE
    ("12:50", "SU840", "IKT", "A320neo", 156),   # [W-RT] Aeroflot Irkutsk 3-4 ch/tuan
    ("14:50", "VJ5074", "SVO", "A330-300", 370),   # [W-OK] VietJet Moskva-Cam Ranh, mo 23/09/2026, ha canh 14:50, than rong ~370 ghe, 3 ch/tuan (5 tu 01/2027)
    ("16:15", "SU832", "VVO", "A330-300", 307),   # [W-RT] Aeroflot Vladivostok 2 ch/tuan - gio 16:15 la vong thu Tu trong lich aeroroutes
]

# ---------------------------------------------------------------- GHI CHU GHE
# KE467: DA GIAI QUYET cho mua dong. Ban S2026 de ngo giua B737-800 (138 ghe) va
#   A330-300 (276). Thong bao NW26 cua Korean Air - Asiana (aeroroutes, 03/09/2026)
#   chot RO: Seoul Incheon - Cam Ranh/Nha Trang chay A330-300 (thay 787-9),
#   1 chuyen/ngay, hieu luc 25/10/2026 - 28/02/2027. Giu 276.
# WE205: so hieu THAT cua Parata Air. 180 ghe = cau hinh A320 mot khoang cua LCC
#   Han; chuyen khai truong cho 143 khach nhung do la TAI THUC, khong phai so ghe.
#   => day la phan SUY, sai thi sai ve phia an toan (180 < 189 cua B737-800).
# VJ5074: 370 ghe lay nguyen tu cong bo cua san bay ("than rong, suc chua khoang
#   370 khach"). Doi bay than rong cua VietJet la A330-300.
# N4CHTR: KHONG phai so hieu that. La MOT suat charter Nordwind dai dien, dat ten
#   ro rang de khong ai nham voi chuyen co that. 340 ghe = ~6.800 khach/thang chia
#   20 chuyen.
# ZF2555: so hieu THAT, da quan sat tren ban san bay. 336 ghe = cau hinh B767-300
#   cua Azur Air. Mua dong 2026/27 Azur chay ~10 chuyen/12 ngay (0,83/ngay) nen
#   MOT suat/ngay la ty le dung, khong phai phong len.
# SU832 / SU830: Aeroflot cong bo HAI vong moi tuyen voi hai gio khac nhau
#   (OVB: 23:20 thu Hai / 04:00 thu Sau; VVO: 16:15 thu Tu / 21:20 thu Bay).
#   Chon 04:00 va 16:15 de khong don them vao cum dem Han Quoc da qua day --
#   va vi hai gio do la gio co that trong chinh lich do.
#
# -------------------------------------------------- GHI CHU SO HIEU NW26 (CHUA DONG)
# Jin Air (LJ) va Air Seoul (RS) deu co thong bao "NW26 Flight Number Changes" tren
# aeroroutes. KHONG doc duoc hai trang do (HTTP 429 lap lai). Nghia la LJ115 / LJ87 /
# RS527 CO THE doi so hieu tu 25/10/2026. TUYEN va GIO khong doi theo cac thong bao
# nay (chung chi doi so hieu), nen mo hinh hang cho KHONG bi anh huong: mo hinh chi
# dung gio + so ghe. Nhung neu ai dung danh sach nay de in so hieu ra trang thi phai
# tra lai hai trang do truoc.
#
# -------------------------------------------------- GHI CHU AIR ASTANA (KC193)
# tisland.travel (nguon Nga, viet cho nua cuoi 2026) ghi Air Astana chay Almaty +
# Astana - Cam Ranh 4 chuyen/tuan bang A321neo LR. NHUNG flightsfrom.com cho thay
# Alma-Ata, Bishkek, Minsk va Astana deu "Ending at 25/10" -- tuc CHUA CO lich mua
# dong nap vao he thong. Hai nguon choi nhau. Giu KC193 vi: (a) Kazakhstan la thi
# truong tranh dong, mua dong la cao diem cua no, (b) Air Astana la hang bay theo
# lich chu khong phai charter. Day la mot chuyen KHONG KIEM CHUNG duoc cho W2026.
