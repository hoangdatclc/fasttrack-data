"""Thay RUỘT các vùng dat:zone. Dừng nếu có gì ngoài vùng bị đổi."""
import json, re, sys
from datetime import date
import render_blocks as R

ZONES = ("wait-hero", "wait-section", "wait-faq")


def zone_re(name):
    return re.compile(r"(<!--dat:zone:%s-->)(.*?)(<!--/dat:zone:%s-->)"
                      % (re.escape(name), re.escape(name)), re.S)


def strip_zones(s):
    for z in ZONES:
        s = zone_re(z).sub(lambda m: m.group(1) + m.group(3), s)
    return s


def main(src, data_path, updated, dst):
    page = open(src, encoding="utf-8").read()
    d = json.load(open(data_path, encoding="utf-8"))
    up = date.fromisoformat(updated)
    # giữ nguyên id của FAQ đang có trong trang, tránh đụng id FAQ viết tay
    cur = zone_re("wait-faq").search(page)
    ids = re.findall(r"daf-faq-a\d+", cur.group(2)) if cur else []
    faq_id = ids[0] if ids else "daf-faq-a12"
    new = {"wait-hero": R.render_hero(d, up), "wait-section": R.render_section(d, up),
           "wait-faq": R.render_faq(d, up, faq_id=faq_id)}
    out = page
    for z in ZONES:
        if len(zone_re(z).findall(out)) != 1:
            sys.exit(f"vùng {z}: không tìm thấy đúng 1 lần")
        out = zone_re(z).sub(lambda m, z=z: m.group(1) + new[z] + m.group(3), out)
    if strip_zones(out) != strip_zones(page):
        sys.exit("có nội dung NGOÀI vùng bị đổi — dừng")
    open(dst, "w", encoding="utf-8").write(out)
    print("xong:", ", ".join(ZONES))


if __name__ == "__main__":
    main(*sys.argv[1:5])
