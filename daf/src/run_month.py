"""Chay mo hinh cho mot thang tu file inputs. Deterministic: cung input -> cung output."""
import json, sys
import dad_queue_model as M


# =====================================================================
# CONG CHAN MUA LICH BAY + NHAN THANG -- them 07/10/2026, siet cung ngay
# sau mot vong ra soat doc lap.
#
# VI SAO CAN: danh sach chuyen trong repo la cua MOT mua IATA. Chay mot
# thang thuoc mua khac ma quen dung lai danh sach thi KHONG cong nao bat
# duoc -- trang in ra con so hop ly, nhan ghi dung thang, chi co so la cua
# mua truoc. Da do thu: gia lap run 01/11/2026 tren ban chua va, SAF in
# 95-133 min y het thang 10 duoi nhan "November 2026". Loi am dung nghia.
#
# PHAN MUA: thang 1-3 -> mua dong nam truoc (W{y-1}); thang 4-10 -> mua he
# nam nay (S{y}); thang 11-12 -> mua dong nam nay (W{y}). Nen 01/2027 va
# 03/2027 deu la W2026, KHONG phai W2027.
#
# VI SAO PHAN MUA CHI LA PHEP CHIA THANG, khong phai so sanh ngay: du an
# lay NGAY 15 lam ngay dai dien cho ca thang (lich thang 10/2026 dung ngay
# dai dien 14/10, mua S2026). Moc doi mua IATA -- CN cuoi thang 3 va CN
# cuoi thang 10 -- luon roi vao khoang 25-31, tuc LUON SAU ngay 15. Nen
# viec so ngay 15 voi moc khong bao gio doi duoc ket qua.
#   BAN DAU HAM NAY CO SO NGAY THAT, va comment khoe la "tinh duoc, khong
#   can bang tra". Ra soat doc lap chi ra: thay moc bang hang so 16, 25, 31
#   hay 99 deu cho DUNG 0/84 ket qua khac -- tuc phep so ngay la MA CHET
#   kem mot comment noi sai cong trang cua no. Da bo.
# Phep tinh moc VAN CON, nhung gio lam dung mot viec co that: CANH chinh
# gia dinh "ngay 15" o duoi. Gia dinh vo thi dung, khong im lang.
# =====================================================================
MONTHS_EN = ("January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December")


def iata_season(month):
    """'YYYY-MM' -> ma mua IATA cua thang do, dang 'S2026' / 'W2026'."""
    import datetime, re
    g = re.fullmatch(r"(\d{4})-(\d{2})", month or "")
    if not g:
        raise SystemExit(
            f"THANG KHONG DUNG DANG: {month!r}. Can dung 'YYYY-MM' (vd '2026-11'), "
            f"KHONG kem ngay.\n"
            f"  Ban cu cat bot phan thua roi chay tiep, nen '2026-10-25' -- dung ngay "
            f"doi mua -- bi coi la thang 10 ma khong bao gi.")
    y, m = int(g.group(1)), int(g.group(2))
    if not 1 <= m <= 12:
        raise SystemExit(f"THANG KHONG CO THAT: {month!r}. Ban cu nhan ca '2026-13'.")

    def last_sun(yy, mm):
        """Chu nhat cuoi cung cua thang (thang 3 va 10 deu 31 ngay).

        Dung so hoc ngay THUAN. KHONG dung calendar.monthcalendar: ham do doc
        calendar.setfirstweekday(), la trang thai TOAN CUC cua tien trinh -- ai
        goi setfirstweekday(SUNDAY) o bat ky dau cung lam no tra ve thu BAY cuoi
        thang (31 thay vi 25 cho 10/2026) ma khong bao gi.
        """
        return 31 - (datetime.date(yy, mm, 31).isoweekday() % 7)

    s3, s10 = last_sun(y, 3), last_sun(y, 10)
    if s3 <= 15 or s10 <= 15:
        raise SystemExit(
            f"GIA DINH 'NGAY DAI DIEN 15' DA VO: nam {y} co moc doi mua {s3}/03 va "
            f"{s10}/10, roi vao hoac truoc ngay 15.\n"
            f"  Phep chia thang ben duoi dua tren viec moc LUON sau ngay 15. Gia dinh "
            f"do khong con dung -- xem lai ham nay truoc khi chay tiep.")
    if m <= 3:
        return f"W{y - 1}"
    if m <= 10:
        return f"S{y}"
    return f"W{y}"


def check_season(month, declared, where):
    """Dung han neu mua cua danh sach chuyen khong khop thang dang dung.

    `where` = ten file dang giu SCHEDULE_SEASON cua site nay (moi site mot cho).
    """
    want = iata_season(month)
    if declared != want:
        raise SystemExit(
            f"LICH BAY SAI MUA: danh sach chuyen dang khai SCHEDULE_SEASON={declared}, "
            f"nhung thang {month} thuoc mua {want}.\n"
            f"\n"
            f"  DAY LA VIEC DU KIEN moi lan doi mua IATA (hai lan mot nam), KHONG hong.\n"
            f"  Trinh tu BAT BUOC, dung dao thu tu:\n"
            f"    1. Dung lai danh sach chuyen quoc te den cho mua {want}: tra lich bay\n"
            f"       that cua thang do, bo codeshare, bo chuyen noi dia, kiem cheo tu\n"
            f"       hai nguon tro len.\n"
            f"    2. Ghi de danh sach cu trong {where}.\n"
            f"    3. Sua SCHEDULE_SEASON trong chinh file do thanh \"{want}\".\n"
            f"    4. Chay lai lenh nay.\n"
            f"\n"
            f"  Bo buoc 1-2 va chi lam buoc 3 la NOI DOI voi cong nay: trang se in con\n"
            f"  so cua mua {declared} duoi nhan thang {month}. Khong lam vay.\n"
            f"  Khong tra duoc lich that thi DUNG LAI va bao nguoi. Do la ket qua DUNG,\n"
            f"  tot hon mot trang sai trong im lang.")
    return want


def check_month_label(month, label):
    """Nhan thang phai khop truong `month`.

    Cung ho loi voi cong mua: con so dung, NHAN sai, va khong cong nao khac bat
    duoc -- nhan nay in ra hero, doan dan va FAQ.
    """
    y, m = int(month[:4]), int(month[5:7])
    want = f"{MONTHS_EN[m - 1]} {y}"
    if (label or "").strip() != want:
        raise SystemExit(
            f"NHAN THANG KHONG KHOP: month={month!r} nhung month_label={label!r}.\n"
            f"  Phai la {want!r}. Lech la trang tu noi sai thang no dang mo ta.")
    return want

def main(inp_path, out_path):
    i = json.load(open(inp_path, encoding="utf-8"))
    season = check_season(i["month"], M.SCHEDULE_SEASON, "dad_flights.py")
    check_month_label(i["month"], i["month_label"])
    d = M.build_month_json(i["month"], i["month_label"], i["month_notes"],
                           i["empty_band_note"], i["context"], i["basis"],
                           i["cities"], i["guide"],
                           uplift=i.get("month_uplift"), surge=i.get("surge"))
    open(out_path, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    h = d["headline"]
    print(f"CONG MUA LICH BAY: PASS ({season})")
    print("CONG HIEU CHUAN: PASS")
    print(f"{out_path}: {i['month_label']} · {h['intl_arrivals_per_day']} chuyen · "
          f"{h['foreign_pax_per_day']:.0f} khach ngoai/ngay")
    print(f"  hero  {h['peak']['range'][0]}-{h['peak']['range'][1]} phut  {h['peak']['window']}")
    for b in d["bands"]:
        s = b["standard"]
        print(f"  {b['band']}  {b.get('tier','-'):>8}  "
              f"{(str(s[0])+'-'+str(s[1])) if s else '-':>8}  {b['flights']} ch")


if __name__ == "__main__":
    main(*sys.argv[1:3])
