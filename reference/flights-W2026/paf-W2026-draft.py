"""BAN NGHIEN CUU lich W2026 cua PQC -- KHONG phai ban chot. Dung 06-07/10/2026,
TRUOC moc doi lich 25/10, tu xep muc tin cay TRUNG BINH. Doi chieu lai bang chuyen
that roi moi dung.

DOI 07/10/2026: truoc day file nay la ban copy CA paf_queue_model.py, nen "cap nhat
lich" = ghi de ca model va am tham lui moi ban sua model. Nay no chi la file lich,
dat dung cho paf/src/paf_flights.py.
"""

SCHEDULE_SEASON = "W2026"   # mua IATA cua danh sach chuyen DUOI DAY.
# Dung lai danh sach cho mua khac thi PHAI sua dong nay cung luc. run_month.py co
# cong chan doi chieu no voi thang dang dung va DUNG HAN neu lech (them 07/10/2026).


FLIGHTS = [
    ("03:20", "9G615", "SZX"),
    ("09:00", "9G (W16098)", "ICN"),
    ("09:30", "AK543", "KUL"),
    ("09:40", "UO598", "HKG"),
    ("09:50", "HH2233", "TAS"),
    ("13:20", "FD660", "DMK"),
    ("13:35", "AK545", "KUL"),
    ("14:30", "9G (W16114)", "BKK"),
    ("14:55", "K6830", "PNH"),
    ("15:05", "9G (W16115)", "SIN"),
    ("15:20", "9G (W16095)", "ICN"),
    ("15:55", "VZ982", "BKK"),
    ("17:40", "TR524", "SIN"),
    ("17:55", "9G (W16118)", "KUL"),
    ("17:55", "JX705", "TPE"),
    ("18:05", "UO596", "HKG"),
    ("18:35", "9G (W16099)", "HKG"),
    ("20:00", "MU861", "XIY"),
    ("20:25", "9G (W16104)", "TPE"),
    ("21:00", "LJ91", "ICN"),
    ("21:25", "7C2315", "ICN"),
    ("22:10", "9G (W16101)", "HKG"),
    ("22:25", "ZE981", "PUS"),
    ("22:50", "KE485", "ICN"),
    ("23:20", "ZE581", "ICN"),
    ("23:35", "TW55", "ICN"),
    ("23:55", "TV9781", "TFU"),
    ("23:55", "DR5045", "KMG"),
]
