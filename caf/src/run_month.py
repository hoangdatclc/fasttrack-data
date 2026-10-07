"""Chay mo hinh cho mot thang tu file inputs. Deterministic: cung input -> cung output."""
import json, sys
import cxr_queue_model as M


# =====================================================================
# CONG CHAN MUA LICH BAY -- them 07/10/2026.
#
# VI SAO CAN: danh sach chuyen trong repo la cua MOT mua IATA. Chay mot
# thang thuoc mua khac ma quen dung lai danh sach thi KHONG cong nao bat
# duoc -- patch_static PASS, run_qc PASS, monthly_publish PASS, trang in ra
# con so hop ly, nhan ghi dung thang, chi co so la cua mua truoc. Loi am
# dung nghia. Truoc 07/10/2026 viec nay chi duoc nhac bang CHU trong skill
# ("lich dong W2026 tu 25/10") -- chu thi doc roi quen, va loi nhac do con
# HET HAN sau thang 11/2026.
#
# MOC IATA: mua he bat dau CHU NHAT CUOI THANG 3, mua dong bat dau CHU NHAT
# CUOI THANG 10. Tinh duoc, khong can bang tra. Da doi chieu voi bang chep
# tay trong skill DAF (reference/model.md): he 29/03/2026 - dong 25/10/2026
# - he 28/03/2027 - dong 31/10/2027 - he 26/03/2028 - dong 29/10/2028: KHOP
# tung ngay.
#
# NGAY DAI DIEN = ngay 15 cua thang, theo dung thong le san co cua du an
# (lich thang 10/2026 dung ngay dai dien 14/10, mua S2026).
#
# HAM NAY DUOC CHEP Y HET SANG CA NAM run_month.py (paf/daf/caf/haf/saf).
# Co y, khong phai luoi: moi site chay tu mot thu muc rieng va khong co
# duong import chung nao dang tin (clean-room keo file ve phang). Sua mot
# ban thi PHAI sua ca nam. Kiem nam ban con giong nhau:
#   for f in */src/run_month.py; do sed -n '/^def iata_season/,/^    return want$/p' $f | md5sum; done
# Nam dong md5 phai y het nhau.
# =====================================================================
def iata_season(month):
    """'YYYY-MM' -> ma mua IATA cua thang do, dang 'S2026' / 'W2026'.

    Mua dong bat dau thang 10 nam Y mang ma W{Y} va keo DAI sang het thang 3
    nam Y+1 -- nen 01/2027 va 03/2027 deu la W2026, KHONG phai W2027.
    """
    import calendar
    y, m = (int(v) for v in month.split("-")[:2])

    def last_sun(yy, mm):
        return max(w[calendar.SUNDAY] for w in calendar.monthcalendar(yy, mm)
                   if w[calendar.SUNDAY])

    d = 15
    if (m, d) < (3, last_sun(y, 3)):      # truoc moc he -> van la mua dong nam truoc
        return f"W{y - 1}"
    if (m, d) < (10, last_sun(y, 10)):    # giua hai moc -> mua he nam nay
        return f"S{y}"
    return f"W{y}"                        # tu moc dong tro di -> mua dong nam nay


def check_season(month, declared):
    """Dung han neu mua cua danh sach chuyen khong khop thang dang dung."""
    want = iata_season(month)
    if declared != want:
        raise SystemExit(
            f"LICH BAY SAI MUA: danh sach chuyen dang khai SCHEDULE_SEASON={declared}, "
            f"nhung thang {month} thuoc mua {want}.\n"
            f"\n"
            f"  DAY LA VIEC DU KIEN moi lan doi mua IATA (2 lan/nam), KHONG phai hong.\n"
            f"  Viec phai lam: DUNG LAI danh sach chuyen quoc te den cho mua {want}\n"
            f"  (tra lich bay that, bo codeshare, bo noi dia, kiem cheo >=2 nguon),\n"
            f"  GHI DE danh sach cu, ROI moi sua SCHEDULE_SEASON thanh \"{want}\".\n"
            f"  Xong thi chay lai lenh nay va di tiep -- dung bo cuoc, dung bao\n"
            f"  \"khong chay duoc\" roi dung lai.\n"
            f"\n"
            f"  TUYET DOI KHONG chi sua moi SCHEDULE_SEASON cho qua cong. Lam vay la\n"
            f"  noi doi voi chinh cong nay: trang se in con so cua mua {declared} kem\n"
            f"  nhan thang {month}, va sau do KHONG CONG NAO khac bat duoc -- "
            f"patch_static,\n"
            f"  run_qc va monthly_publish deu se PASS. Do dung la loi am ma cong nay\n"
            f"  sinh ra de chan.")
    return want


def main(inp_path, out_path):
    i = json.load(open(inp_path, encoding="utf-8"))
    season = check_season(i["month"], M.SCHEDULE_SEASON)
    d = M.build_month_json(i["month"], i["month_label"], i["month_notes"],
                           i["empty_band_note"], i["context"], i["basis"],
                           i["cities"], i["guide"])
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
