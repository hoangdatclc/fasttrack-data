"""Lich chuyen quoc te DEN cua PQC -- mot ngay thuong tieu bieu.

TACH RA FILE RIENG 07/10/2026, de giong bon site kia (dad_flights / cxr_flights /
han_flights / sgn_flights). Vi sao phai tach:

    Truoc day FLIGHTS nam TRONG paf_queue_model.py. Ban nghien cuu lich mua moi vi the
    la mot ban COPY CA MODEL, va "cap nhat lich" = ghi de ca model -> am tham lui MOI
    ban sua model ke tu ngay dung ban nghien cuu do. Da dinh that: ban nghien cuu
    W2026 (06/10/2026) khi ghi de len model lam `assumptions` quay ve in hang so module,
    tuc hong dung cai moc doi chieu ma luat 16 dua vao.

    Nay doi lich chi sua FILE NAY. Model khong bi dung toi.

DOI LICH SANG MUA KHAC thi PHAI sua SCHEDULE_SEASON cung luc -- run_month.py co cong
chan doi chieu no voi thang dang dung va DUNG HAN neu lech.
"""

SCHEDULE_SEASON = "S2026"   # mua IATA cua danh sach chuyen DUOI DAY.
# Dung lai danh sach cho mua khac thi PHAI sua dong nay cung luc. run_month.py co
# cong chan doi chieu no voi thang dang dung va DUNG HAN neu lech (them 07/10/2026).


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
