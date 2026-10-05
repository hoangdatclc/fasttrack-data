"""Dong goi 3 vung dat:zone thanh MOT file JSON nho de site tu keo ve.

Chay trong thu muc run-YYYY-MM (noi co render_blocks.py va {site}-wait-YYYY-MM.json).

    python3 build_zones_json.py zones.json 2026-10:paf-wait-2026-10.json:2026-10-01 [...]

Moi doi so sau file dich la mot thang:  THANG:duong_dan_wait_json:ngay_cap_nhat
Nhieu thang trong mot lan goi -> mot file JSON phuc vu ca mua IATA.
"""
import json, re, sys
from datetime import date

sys.path.insert(0, ".")
import render_blocks as R

SCHEMA = "paf-zones/1.0"
KEYS = ("hero", "section", "faq")
# Shortcode duoc phep nam trong vung. PHP BAT BUOC chay do_shortcode() tren dau ra,
# neu khong chung se hien ra chu tho tren trang.
ALLOWED_SHORTCODES = {"paf_price"}


def build_month(wait_path, updated, faq_id="paf-faq-a12"):
    d = json.load(open(wait_path, encoding="utf-8"))
    up = date.fromisoformat(updated)
    out = {"updated": updated,
           "month_label": d.get("month_label", ""),
           "hero": R.render_hero(d, up),
           "section": R.render_section(d, up),
           "faq": R.render_faq(d, up, faq_id=faq_id)}
    for k in KEYS:
        v = out[k]
        if not v or not v.strip():
            sys.exit(f"vung {k} cua {wait_path} rong")
        # shortcode long nhau: chi cho phep danh sach da biet
        found = set(re.findall(r"\[([a-z_][a-z0-9_]*)[\s\]]", v))
        bad = found - ALLOWED_SHORTCODES
        if bad:
            sys.exit(f"vung {k} chua shortcode la: {sorted(bad)} -> kiem tra lai renderer")
        if "]]>" in v:
            sys.exit(f"vung {k} chua ]]> -> vo CDATA neu sau nay dung XML")
    return out


def main(dst, *specs):
    if not specs:
        sys.exit("thieu doi so THANG:wait.json:ngay")
    months = {}
    for s in specs:
        m, path, upd = s.split(":")
        if not re.fullmatch(r"\d{4}-\d{2}", m):
            sys.exit(f"thang sai dinh dang: {m}")
        months[m] = build_month(path, upd)
    payload = {"schema": SCHEMA, "site": "PAF", "airport": "PQC",
               "generated": date.today().isoformat(), "months": months}
    txt = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    open(dst, "w", encoding="utf-8").write(txt)
    # tu kiem: doc lai, du khoa, du thang
    back = json.loads(open(dst, encoding="utf-8").read())
    assert back["schema"] == SCHEMA
    for m, v in back["months"].items():
        assert all(v.get(k) for k in KEYS), f"{m} thieu vung"
    print(f"{dst}: {len(months)} thang ({', '.join(sorted(months))}) · {len(txt):,} bytes")
    for m in sorted(months):
        v = months[m]
        print(f"   {m}  hero {len(v['hero']):>6,}  section {len(v['section']):>6,}  faq {len(v['faq']):>6,}")


if __name__ == "__main__":
    main(*sys.argv[1:])
