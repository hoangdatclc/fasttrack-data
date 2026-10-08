#!/usr/bin/env python3
"""Doc / thay / nghiem thu cac VUNG TEXT THEO THANG tren trang chu.

Vung = phan nam GIUA  <!--m:id-->  va  <!--/m:id-->.  Chi phan giua duoc thay.
Moi byte ngoai vung phai giu nguyen tuyet doi -- do la ca hop dong.

    python3 tools/text_zones.py --list  page.txt
    python3 tools/text_zones.py --apply page.txt zones-YYYY-MM.json out.txt
    python3 tools/text_zones.py --check page-cu.txt page-moi.txt [--freeze a,b]

VI SAO LAM BANG COMMENT HTML: no khong render ra trang, khong doi cau truc, khong
them khoi moi -- dung rang buoc chu site da dat. Va no cho phep mot cong chan tuyet
doi: xoa het marker o ca hai ban roi so, khac mot byte ngoai vung la HONG.

=== VUNG DONG BANG ===
Mot so vung bi DONG BANG co chu dich (vd o chua con so hang cho). `--apply` tu choi
ghi vao chung tru khi truyen --allow-frozen. Danh sach dong bang nam trong chinh file
zones JSON, khoa "_frozen". Dung bo cong nay de "cho tien".
"""
import argparse
import html
import json
import re
import sys

MARK = re.compile(r'<!--m:([a-z0-9-]+)-->')
KEYWORDS_DEFAULT = ("fast track", "immigration", "queue", "visa-free", "charter",
                    "airport", "terminal", "priority lane")


def zones(page):
    """-> {id: ruot} theo dung thu tu xuat hien."""
    out = {}
    for zid in MARK.findall(page):
        m = re.search(r'<!--m:%s-->(.*?)<!--/m:%s-->' % (zid, zid), page, re.S)
        if not m:
            sys.exit(f"VUNG HONG: <!--m:{zid}--> khong co the dong tuong ung.")
        if f'<!--m:{zid}-->' in m.group(1):
            sys.exit(f"VUNG LONG NHAU: {zid}.")
        out[zid] = m.group(1)
    return out


def blank(page):
    """Xoa RUOT moi vung, giu marker -- dung de so phan ngoai vung."""
    for zid in MARK.findall(page):
        page = re.sub(r'(<!--m:%s-->).*?(<!--/m:%s-->)' % (zid, zid), r'\1\2', page, flags=re.S)
    return page


def plain(t):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', t, flags=re.S)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', t)).lower()


def cmd_list(path):
    page = open(path, encoding="utf-8").read()
    z = zones(page)
    print(f"{len(z)} vung trong {path}\n")
    for zid, inner in z.items():
        txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', inner))).strip()
        print(f"--- m:{zid}  ({len(inner)} ky tu ruot, {len(txt.split())} chu)")
        print(f"    {txt}\n")


def cmd_apply(src, zjson, dst, allow_frozen):
    page = open(src, encoding="utf-8").read()
    data = json.load(open(zjson, encoding="utf-8"))
    frozen = set(data.pop("_frozen", []))
    # Moi khoa bat dau bang "_" la SIEU DU LIEU (nguon, ly do dong bang, ghi chu
    # thang...), khong phai vung. An toan: id vung chi gom [a-z0-9-] nen khong
    # bao gio bat dau bang "_" -> cong "vung khong co tren trang" van bat duoc
    # loi go sai ten vung thuc.
    for k in [k for k in data if k.startswith("_")]:
        data.pop(k)
    have = zones(page)
    unknown = [k for k in data if k not in have]
    if unknown:
        sys.exit(f"VUNG KHONG CO TREN TRANG: {unknown}\n  Trang nay co: {list(have)}")
    hit = [k for k in data if k in frozen]
    if hit and not allow_frozen:
        sys.exit(f"VUNG DANG DONG BANG: {hit}\n\n"
                 f"  Nhung vung nay bi dong bang co chu dich (xem \"_frozen\" trong {zjson}).\n"
                 f"  Muon doi that thi phai duoc chu site chot TRUOC, roi chay lai voi\n"
                 f"  --allow-frozen. Dung go --allow-frozen vao chi de cho qua.")
    out = page
    for zid, new in data.items():
        out = re.sub(r'(<!--m:%s-->).*?(<!--/m:%s-->)' % (zid, zid),
                     lambda m, v=new: m.group(1) + v + m.group(2), out, flags=re.S)
    if blank(out) != blank(page):
        sys.exit("CO NOI DUNG NGOAI VUNG BI DOI -- dung, khong xuat file.")
    open(dst, "w", encoding="utf-8").write(out)
    print(f"xong: {len(data)} vung -> {dst}")
    for zid, new in data.items():
        a = len(have[zid])
        print(f"  m:{zid:<16} {a:>5} -> {len(new):>5} ky tu  ({(len(new)-a)/a*100:+.0f}%)")


def cmd_check(old_path, new_path, freeze):
    a = open(old_path, encoding="utf-8").read()
    b = open(new_path, encoding="utf-8").read()
    za, zb = zones(a), zones(b)
    err = []

    if blank(a) != blank(b):
        err.append("NGOAI VUNG BI DOI -- day la loi nghiem trong, khong duoc giao.")
    if set(za) != set(zb):
        err.append(f"DANH SACH VUNG DOI: them {set(zb)-set(za)}, mat {set(za)-set(zb)}")
    for zid in freeze:
        if zid in za and za.get(zid) != zb.get(zid):
            err.append(f"VUNG DONG BANG {zid} DA BI DOI")

    changed = [z for z in za if z in zb and za[z] != zb[z]]
    print(f"Doi {len(changed)}/{len(za)} vung: {', '.join(changed) if changed else '(khong vung nao)'}\n")
    print(f"  {'vung':<16}{'cu':>7}{'moi':>7}{'lech':>8}")
    for zid in changed:
        x, y = len(za[zid]), len(zb[zid])
        d = (y - x) / x * 100 if x else 0
        flag = "  <- lech >15%, chi chap nhan o vung bac A" if abs(d) > 15 else ""
        print(f"  {zid:<16}{x:>7}{y:>7}{d:>+7.0f}%{flag}")

    pa, pb = plain(a), plain(b)
    print(f"\n  {'tu khoa':<20}{'cu':>5}{'moi':>6}")
    for k in KEYWORDS_DEFAULT:
        ca, cb = pa.count(k), pb.count(k)
        mark = "" if ca == cb else f"   {cb-ca:+d}"
        if cb < ca:
            err.append(f"MAT TU KHOA: '{k}' {ca} -> {cb}")
        print(f"  {k:<20}{ca:>5}{cb:>6}{mark}")
    print(f"\n  {'tong so tu':<20}{len(pa.split()):>5}{len(pb.split()):>6}")

    if not changed:
        err.append("KHONG VUNG NAO DOI -- thang nay khong co gi de giao. "
                   "Khong co du kien moi thi DUNG cap nhat (xem luat 3 cua skill me).")
    print("\n" + ("NGHIEM THU: PASS" if not err else "NGHIEM THU: FAIL"))
    for e in dict.fromkeys(err):
        print("  -", e)
    return 1 if err else 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", metavar="PAGE")
    p.add_argument("--apply", nargs=3, metavar=("PAGE", "ZONES_JSON", "OUT"))
    p.add_argument("--check", nargs=2, metavar=("PAGE_CU", "PAGE_MOI"))
    p.add_argument("--freeze", default="")
    p.add_argument("--allow-frozen", action="store_true")
    a = p.parse_args()
    if a.list:
        cmd_list(a.list); return 0
    if a.apply:
        cmd_apply(*a.apply, a.allow_frozen); return 0
    if a.check:
        return cmd_check(*a.check, [x for x in a.freeze.split(",") if x])
    p.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
