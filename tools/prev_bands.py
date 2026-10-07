#!/usr/bin/env python3
"""PHEP THU DON DIEU (luat nha 12) -- chay TRUOC KHI GIAO, moi thang, moi site.

    Thang dong khach hon KHONG THE cho thoi gian cho thap hon.

Cach dung:

    # chuan: moc doi chieu lay tu latest.json (co pax va so quay), so voi JSON vua dung
    python3 tools/prev_bands.py --prev haf/home/latest.json --new haf-wait-2026-11.json

    # thang chuyen tiep: latest.json con chua co khoa "baseline" -> doc do chu tren trang
    python3 tools/prev_bands.py --xml haf/home/latest.xml --new haf-wait-2026-11.json

    # chi doc bang thang truoc ra
    python3 tools/prev_bands.py --prev saf/home/latest.json

Moc doi chieu lay TU BAN DA PHAT HANH, khong tu bang so cung trong skill hay trong
prompt -- so cung se cu di mot thang la het dung.

=== DOC KY: XET CAI GI, VA VI SAO KHONG XET TRAN ===

Dai cong bo la KHOANG TIN CAY (tu phan vi 25/75 cua luoi kich ban), khong phai
min/max trai nghiem. Nen ba dau moc khong noi cung mot chuyen:

  * CAN DUOI  -- "kich ban thuan loi cung mat bao lau". Bam truc tiep theo luu luong.
                 Dong hon ma can duoi TUT XUONG = van nham can. VI PHAM.
  * TRUNG DIEM-- uoc luong trung tam. Dong hon ma trung diem TUT XUONG. VI PHAM.
  * CAN TREN  -- duoi kich ban xau nhat cua luoi. THEM QUAY lam cut duoi nay di, va do
                 la tac dung DUNG cua `surge`: chan khong cho hang vo tran. Nen tran
                 giam MA DA THEM QUAY la hop le -- nhung PHAI noi ro trong ban giao.
                 Tran giam ma KHONG them quay thi khong giai thich duoc. VI PHAM.

Ca thuc 11/2026 o HAN, chinh la ly do cong nay phai phan biet ba dau moc: `surge` 5 -> 8
lam moi can duoi di LEN (90->95, 97->108, ...) trong khi tran cua ba khung di XUONG
(77->75, 107->103, 110->100), vi may quay tang them cat duoi xau cua luoi. Dai hep lai
quanh mot tam CAO HON. Neu chi so tran thi cong nay bao dong gia ba lan mot thang --
va mot cong hay bao dong gia la mot cong se bi ngo.

Nguoc lai, ca HAF truoc do -- nang `BASE_DAY` 28 -> 33 -- lam khung VANG 06:00-10:00
nhanh len 51-53 -> 49-52: can duoi tut, trung diem tut. Do moi la loi, va cong nay bat.

=== LUU LUONG: `pax` CHU KHONG PHAI SO CHUYEN ===

Cau hoi "thang nay co dong hon khong" phai tra bang SO KHACH, khong phai so chuyen.
Cung 13 chuyen ma doi doi tau bay la lech ca tram khach. Ca thuc 11/2026 o DAD, khung
10:00-13:00: 13 chuyen ca hai thang, nhung 1.907 -> 1.824 khach. San di 1 phut (50->49)
la DUNG, vi khung do NHE hon. Neu chi so so chuyen thi cong nay goi do la vi pham.

Nen `pax` lay tu khoa "baseline" trong {site}/home/latest.json, do monthly_publish.py
ghi vao (tham so --wait-json). Trang HTML khong in pax. Khi thieu pax, cong KHONG ket
luan vi pham ma bao CHUA KET LUAN DUOC va thoat ma 2 -- phai tu doi chieu danh sach
chuyen cua khung do.

MA THOAT: 0 qua · 1 vi pham · 2 chua ket luan duoc (thieu pax).
Ma 1 hay 2 DEU KHONG PHAI GIAY PHEP DE DUNG LAI (luat 11): ma 1 noi rang DA VAN NHAM
CAN. Sua can roi chay lai. Thu het cach van vi pham thi VAN GIAO, kem canh bao noi
thang ngay trong phan ban giao.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET

DASH = re.compile(r"&ndash;|&mdash;|–|—")
ROW = re.compile(r'wt-band"\s+role="rowheader"><strong>(.*?)</strong>'
                 r'<span class="[a-z]{3}-wt-flights">(.*?)</span>', re.S)
NUM = re.compile(r'wt-num"[^>]*>(.*?)</span>', re.S)


def norm(b):
    return DASH.sub("-", b).strip()


def from_xml(path):
    html = ET.fromstring(open(path, encoding="utf-8").read()).find("item").findtext("post_content")
    rows, nums = ROW.findall(html), NUM.findall(html)
    if not rows or len(rows) != len(nums):
        sys.exit(f"TRANG KHONG DOC DUOC: {len(rows)} hang / {len(nums)} o so. Markup bang da "
                 f"doi -> sua regex trong tools/prev_bands.py, dung bo qua buoc nay.")
    out = []
    for (band, meta), num in zip(rows, nums):
        g = re.search(r"(\d+)", meta)
        v = re.findall(r"\d+", norm(num))
        out.append({"band": norm(band), "flights": int(g.group(1)) if g else None, "pax": None,
                    "standard": [int(v[0]), int(v[-1])] if v else None})
    return {"month": "(doc tu trang)", "bands": out, "levers": {}}


def from_prev_json(path):
    d = json.load(open(path, encoding="utf-8"))
    b = d.get("baseline")
    if not b:
        sys.exit(f"{path} chua co khoa \"baseline\" -- la ban publish truoc khi co tinh nang nay.\n"
                 f"  Thang nay dung --xml {path.replace('.json', '.xml')} thay the (doc do chu tren\n"
                 f"  trang, thieu pax va so quay nen phan xu tran se than trong hon).\n"
                 f"  Va nho truyen --wait-json cho monthly_publish.py de thang sau co moc that.")
    b["bands"] = [{**r, "band": norm(r["band"])} for r in b["bands"]]
    return b


def from_new(path):
    d = json.load(open(path, encoding="utf-8"))
    asm = d.get("assumptions", {})
    return ({"month": d.get("month_label", d.get("month", "?")),
             "bands": [{"band": norm(b["band"]), "flights": b.get("flights"), "pax": b.get("pax"),
                        "standard": b.get("standard")} for b in d.get("bands", [])],
             "levers": {"month_uplift": asm.get("month_uplift"),
                        "surge": asm.get("surge_counters", asm.get("surge")),
                        "counters_day": asm.get("counters_day")}})


def fmt(st):
    return "-" if not st else f"{st[0]}-{st[1]} min"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prev", help="{site}/home/latest.json cua thang truoc (uu tien)")
    p.add_argument("--xml", help="{site}/home/latest.xml -- dung khi latest.json chua co baseline")
    p.add_argument("--new", help="{site}-wait-YYYY-MM.json cua thang nay")
    a = p.parse_args()
    if not (a.prev or a.xml):
        sys.exit("can --prev (latest.json) hoac --xml (latest.xml) cua THANG TRUOC")
    old = from_prev_json(a.prev) if a.prev else from_xml(a.xml)

    if not a.new:
        print(f"MOC DOI CHIEU -- {old['month']}   don bay {old.get('levers') or '(khong ro)'}")
        for r in old["bands"]:
            pax = "" if r.get("pax") is None else f" · {r['pax']} khach"
            print(f"  {r['band']:<13} {fmt(r['standard']):>12}   {r['flights']} chuyen{pax}")
        return 0

    new = from_new(a.new)
    o_s, n_s = (old.get("levers") or {}).get("surge"), (new.get("levers") or {}).get("surge")
    added = None if o_s is None or n_s is None else n_s > o_s
    byband = {r["band"]: r for r in old["bands"]}

    print(f"PHEP THU DON DIEU -- {old['month']}  ->  {new['month']}")
    print(f"  don bay: surge {o_s} -> {n_s}   uplift {(old.get('levers') or {}).get('month_uplift')}"
          f" -> {(new.get('levers') or {}).get('month_uplift')}"
          f"   | them quay: {{True:'CO',False:'KHONG',None:'khong ro'}}[{added!r}]"
          .replace("{True:'CO',False:'KHONG',None:'khong ro'}[True]", "CO")
          .replace("{True:'CO',False:'KHONG',None:'khong ro'}[False]", "KHONG")
          .replace("{True:'CO',False:'KHONG',None:'khong ro'}[None]", "khong ro"))
    print(f"\n  {'khung':<13}{'thang truoc':>12}{'thang nay':>12}  {'luu luong':>13}  ket qua")
    bad, soft, unsure = [], [], []
    for r in new["bands"]:
        o = byband.get(r["band"])
        if o is None:
            print(f"  {r['band']:<13}{'(khong co)':>12}{fmt(r['standard']):>12}  {'':>13}  "
                  f"KHUNG MOI -- doi chieu tay")
            continue
        if not r["standard"] or not o["standard"]:
            print(f"  {r['band']:<13}{fmt(o['standard']):>12}{fmt(r['standard']):>12}  {'':>13}  "
                  f"o trong -- doi chieu tay")
            continue
        if o.get("pax") is not None and r.get("pax") is not None:
            load = f"{o['pax']}->{r['pax']} kh"
            busier = r["pax"] >= o["pax"]
        else:
            load = f"{o['flights']}->{r['flights']} ch"
            busier = (r["flights"] or 0) >= (o["flights"] or 0)
        olo, ohi = o["standard"]
        nlo, nhi = r["standard"]
        omid, nmid = (olo + ohi) / 2, (nlo + nhi) / 2
        has_pax = o.get("pax") is not None and r.get("pax") is not None
        if busier and (nlo < olo or nmid < omid) and not has_pax:
            why = (f"can duoi {olo}->{nlo}" if nlo < olo else f"trung diem {omid:g}->{nmid:g}")
            unsure.append((r["band"], why))
            v = f"?? CHUA KET LUAN: {why}, nhung so bang SO CHUYEN (thieu pax)"
        elif busier and nlo < olo:
            bad.append((r["band"], f"can duoi {olo} -> {nlo}"))
            v = f"*** VI PHAM: can duoi tut ({olo}->{nlo}) ***"
        elif busier and nmid < omid:
            bad.append((r["band"], f"trung diem {omid:g} -> {nmid:g}"))
            v = f"*** VI PHAM: trung diem tut ({omid:g}->{nmid:g}) ***"
        elif busier and nhi < ohi and added is False:
            bad.append((r["band"], f"tran {ohi} -> {nhi} ma khong them quay"))
            v = f"*** VI PHAM: tran tut ({ohi}->{nhi}) ma KHONG them quay ***"
        elif busier and nhi < ohi:
            soft.append((r["band"], ohi, nhi))
            v = f"tran {ohi}->{nhi}: cat duoi xau vi them quay -- PHAI noi trong ban giao"
        elif not busier and (nlo < olo or nmid < omid):
            v = "thap hon, nhung VANG hon -- hop le, ghi ly do"
        else:
            v = "ok"
        print(f"  {r['band']:<13}{fmt(o['standard']):>12}{fmt(r['standard']):>12}  {load:>13}  {v}")

    if soft and not bad:
        print("\nPHAI VIET VAO BAN GIAO -- tran giam o: "
              + ", ".join(f"{b} ({x}->{y} min)" for b, x, y in soft))
        print(f"  Cau giai thich: da nang surge {o_s} -> {n_s}, may quay them cat duoi xau cua")
        print("  luoi kich ban, nen dai hep lai quanh mot tam CAO HON -- can duoi va trung diem")
        print("  deu di len. Dung de chu site tu phat hien tran giam roi hoi.")
    if unsure:
        print(f"\nDON DIEU: CHUA KET LUAN DUOC o {len(unsure)} khung -- moc thang truoc khong co "
              f"`pax`\n(doc do chu tren trang). So bang so chuyen la proxy yeu: cung so chuyen ma\ndoi doi "
              f"tau bay la lech ca tram khach.")
        for b, why in unsure:
            print(f"  - {b}: {why}")
        print("""
PHAI LAM RO, dung bo qua va cung dung goi la vi pham:
  1. Mo danh sach chuyen cua dung khung do o ca hai thang. Khung NHE hon (it khach hon)
     ma di xuong 1-2 phut la DUNG -- ghi ly do vao ban giao roi di tiep.
  2. Khung NANG hon ma di xuong thi la vi pham that -> xu theo phan duoi.
  3. De thang sau khong phai lam tay nua: truyen --wait-json cho monthly_publish.py,
     no ghi `baseline` (co pax va so quay) vao {site}/home/latest.json.""")
        if not bad:
            return 2
    if not bad:
        print("\nDON DIEU: QUA.")
        return 0
    print(f"\nDON DIEU: VI PHAM {len(bad)} khung")
    for b, why in bad:
        print(f"  - {b}: {why}")
    print("""
DAY KHONG PHAI DIEM DUNG (luat 11). No noi: DA VAN NHAM CAN.
  - Mot thang dong hon thi nang `surge`, KHONG nang `BASE_DAY` (luat 13). `BASE_DAY`
    chay suot ca ngay nen lam nhanh ca khung khong he dong -- do chinh la dau hieu lo
    ra o day, va no lo ro nhat o KHUNG VANG.
  - Dat `surge` o SO NHO NHAT dat rang buoc vat ly. Lam tron ve phia ban duoc nhieu
    Fast Track hon la dieu da bi cam.
  - Don bay theo thang nam trong inputs-YYYY-MM.json (`month_uplift`, `surge`), KHONG
    sua hang so module -- sua hang so la thang cu khong dung lai duoc (luat 14).
Sua can roi chay lai. Thu het cach van vi pham thi VAN GIAO, kem canh bao noi thang
NGAY TRONG phan ban giao -- giu lai khong giao gi moi la te nhat.""")
    return 1


if __name__ == "__main__":
    sys.exit(main())
