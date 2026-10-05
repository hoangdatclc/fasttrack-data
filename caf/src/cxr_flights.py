# -*- coding: utf-8 -*-
"""Lich chuyen QUOC TE den CXR (Cam Ranh) - NGAY DAI DIEN, 10/2026.

====================================================================
VI SAO CXR KHONG DUNG "MOT NGAY THU TU CU THE" NHU DAD VA PQC
====================================================================
O DAD/PQC, ban lich mot ngay thuong lay tu nguon GDS la DU. O CXR thi KHONG:

  1. MANG CHARTER NGA KHONG NAM TRONG GDS. Noi lai tu 03-05/2025 sau 3 nam dut.
     Azur Air bay charter tu 11 thanh pho Nga; Nordwind tu 10/2025 chay 18-22
     chuyen/thang, ~6.800 khach/thang (=~340 khach/chuyen, than rong). Cuc Hang
     khong: "hon 30 chuyen/tuan tu cac thanh pho lon cua Nga den Khanh Hoa".
     flightconnections chi thay Azur o 3 tuyen x 2 chuyen/thang.
  2. NGAY TRONG TUAN KHONG ON DINH. Cac nguon mau thuan nhau ngay tren cung mot
     chuyen (WZ3201: airportia ghi Hai/Nam/Bay nhung ban san bay thay no thu Sau;
     RF557: flightsfrom ghi Tu/Bay nhung ban san bay thay no thu Sau). Charter doi
     ngay theo tung tuan. Chot cung mot thu la OVERFIT vao nhieu mang du lieu le.

=> Dung NGAY DAI DIEN: moi tuyen gop vao theo DUNG TY LE tan suat thang cua no,
   roi roi rac hoa thanh chuyen rieng le sao cho (a) so chuyen ~ tong ty le, va
   (b) tong ghe ~ tong ghe ky vong. Gio ha canh deu la gio THAT da quan sat hoac
   suy tu gio khoi hanh that + mui gio, KHONG co gio nao bia ra.

====================================================================
COT MOC DOI CHIEU (cong 2) - DAY LA RANG BUOC CHINH
====================================================================
  2024 (chinh thuc, Bao Khanh Hoa): 6,8 trieu luot khach, QUOC TE 4,2 trieu,
        noi dia 2,6 trieu, 40.044 chuyen bay.
  2025: khach quoc te ~4,69 trieu (+7%).
  4,2 trieu luot quoc te /2 /365 = 5.753 KHACH DEN/NGAY (binh quan nam 2024).
  Bang tan suat GDS cho 24,9 chuyen/ngay -> 231 khach/chuyen: BAT KHA THI voi doi
  bay A320/A321/B737 (174-214 ghe). So dung phai la ~28 chuyen/ngay voi ty le lap
  day cao (charter tour chay rat day) va vai chuyen than rong.

GIO = gio ha canh THEO LICH, gio dia phuong CXR (UTC+7). KHONG dung gio ha canh thuc te.
Da doi chieu khop tung phut voi ban san bay: CZ6049 15:10, SU294 09:30, SU830 04:00,
KC193 07:30, BX787 20:20, TW33 22:30, RF557 22:30, TW37 22:50, 3U3939 17:50.

DA LOAI: chuyen noi dia; codeshare OZ95xx/KE5055/DL78xx/VN34xx/VN35xx/CI87xx/AF92xx/
3U7091; bong GDS A1xxxx (A.P.G.) W2xxxx (Flexflight) H1xxxx (Hahn Air) W1xxxx
(World Ticket); WE205 "Thai Smile" ICN-CXR (Thai Smile da sap vao Thai Airways 2024,
khong khai thac duong nay -> codeshare ao).

(gio_ha_canh, so_hieu, san_bay_di, loai_tau_bay, so_ghe)
"""

FLIGHTS = [
    # ================= CUM DEM HAN QUOC - dac diem lon nhat cua CXR =================
    # 11 chuyen Han ha canh trong 4 tieng 20:20-00:35. Khong san bay nao trong mang
    # nay co cum dac nhu vay. Day la cho bang thoi gian cho phai noi that ro.
    ("00:10", "TW41", "PUS", "B737-800", 189),   # T'way B737-800
    ("00:35", "7C2303", "ICN", "B737-800", 189),   # Jeju Air B737-800, hang ngay
    ("20:20", "BX787", "ICN", "A321", 195),   # Air Busan A321, hang ngay
    ("22:30", "TW33", "ICN", "B737-800", 189),   # T'way B737-800, hang ngay
    ("22:30", "RF557", "CJJ", "A320", 180),   # Aero K A320
    ("22:50", "TW37", "TAE", "B737-800", 189),   # T'way B737-800
    ("22:55", "RS527", "ICN", "A321", 195),   # Air Seoul A321, hang ngay
    ("22:55", "LJ115", "PUS", "B737-800", 188),   # Jin Air B737-800
    ("23:05", "KE467", "ICN", "A330-300", 276),   # Korean Air A330-300, hang ngay (xem GHI CHU GHE)
    ("23:45", "LJ87", "ICN", "B737-800", 189),   # Jin Air B737-800
    ("23:55", "ZE561", "ICN", "B737-8", 189),   # Eastar Jet B737-8, hang ngay
    # ================= HAN QUOC BAN NGAY (tau bay Viet quay dau) =================
    ("09:55", "VJ835", "ICN", "A321", 214),   # VietJet A321, hang ngay
    ("10:00", "VN441", "ICN", "A321", 184),   # Vietnam Airlines A321, hang ngay
    ("10:55", "VN435", "PUS", "A321", 184),   # Vietnam Airlines A321, hang ngay
    ("13:35", "VJ919", "PUS", "A321", 214),   # VietJet A321
    # ================= TRUNG QUOC =================
    ("10:00", "CZ8475", "CAN", "B737-800", 174),   # China Southern B737-800
    ("15:10", "CZ6049", "CAN", "B737-800", 174),   # China Southern B737-800
    ("17:50", "3U3939", "TFU", "A32X", 165),   # Sichuan Airlines A32X
    # ================= DONG NAM A - lap day khung giua trua =================
    ("10:00", "FD646", "DMK", "A320", 180),   # Thai AirAsia A320
    ("11:30", "TR548", "SIN", "E190-E2", 112),   # Scoot Embraer 190-E2
    ("12:30", "AK204", "KUL", "A320neo", 186),   # AirAsia A320neo
    ("13:30", "VZ968", "BKK", "B737", 191),   # Thai Vietjet B737, hang ngay
    # ================= NGA / SNG - cum sang, nhieu THAN RONG =================
    ("04:00", "SU830", "OVB", "A330-300", 307),   # Aeroflot A330-300
    ("07:30", "KC193", "ALA", "A321neo", 169),   # Air Astana A321neo
    ("09:30", "SU294", "SVO", "A350-900", 316),   # Aeroflot A350-900, hang ngay
    ("11:20", "ZF2555", "MRV", "B767-300", 336),   # Azur Air B767-300 - dai dien mang charter Azur
    ("12:00", "N4CHTR", "SVO", "B777-200", 340),   # Nordwind - dai dien 18-22 chuyen/thang, 340 khach/chuyen
                                       # Gio 12:00 lay tu chuyen dau tien ha canh 12h ngay 29/9
    ("12:50", "SU840", "IKT", "A320neo", 156),   # Aeroflot A320neo
]

# ---------------------------------------------------------------- GHI CHU GHE
# KE467: nguon liet ke Korean Air chay CA B737-800 (138 ghe, 2 khoang) LAN A330-300
#   (276) tren duong nay, khong noi chuyen nao. Chon 276 vi KE467 la chuyen HANG NGAY
#   dai 5 tieng vao cao diem dong Han Quoc, va Jin Air da phu phan LCC nen KE thuong
#   dat than rong. Sai thi sai ve phia AN TOAN. => VIEC CON MO.
# N4CHTR: KHONG phai so hieu that. La MOT SUAT charter Nordwind dai dien, dat ten ro
#   rang de khong ai nham voi chuyen co that. 340 ghe = 6.800 khach/thang chia 20 chuyen,
#   theo so Cuc Hang khong cong bo 30/09/2025.
# ZF2555: so hieu THAT, da quan sat tren ban san bay. 336 ghe = cau hinh B767-300 cua
#   Azur Air. Dung lam dai dien cho ca mang charter Azur (11 thanh pho Nga).
