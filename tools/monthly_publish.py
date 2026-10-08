"""Mot lenh cho ca thang: kiem trang -> dung XML -> day len repo -> in URL edit."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from datetime import date
from urllib.parse import urlparse, parse_qs

# Van tay cau truc theo site. Site moi phai them mot muc o day.
PROFILE = {
    # PAF -- DOI HAN 08/10/2026. Trang chu quay ve ban GOC 11 element (bo he tinh
    # thoi gian cho), cong element "Booking Picker" => 12 element. Khong con vung
    # dat:zone nao; cap nhat hang thang di qua cac vung <!--m:id--> (tools/text_zones.py).
    # Van tay cu cua he cu nam trong git history, commit f97f794 tro ve truoc.
    "PAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'What Is Fast Track?', 'Services', 'Booking',
                   'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp Float',
                   'Mobile Book Now', 'Booking Picker'],
        "zones": [],
        "musts": ['add-to-cart=311', 'add-to-cart=313',
                  '[paf_price service="fast_track_arrival"]',
                  '[paf_price service="fast_track_departure"]',
                  'id="paf-pick-tpl"', '.paf-pick-btn',
                  # media query phai nham CA <button>, khong chi <a> -- neu khong thi
                  # nut hero lech trai o <=600px. Loi am, desktop khong lo ra.
                  '.paf-cta-row button'],
        "counts": {r'<img ': 15, r'schema\.org/Question': 11,
                   r'class="paf-review-card"': 16, r'class="paf-pick-btn"': 2,
                   r'class="paf-pick-chev"': 2,
                   # 10 vung text theo thang -- mat mot cai la thang sau khong ghi duoc
                   r'<!--m:[a-z0-9-]+-->': 10, r'<!--/m:[a-z0-9-]+-->': 10},
    },
    # DAF -- DOI HAN 08/10/2026. Trang chu quay ve ban GOC 11 element (bo he tinh
    # thoi gian cho), cong element "Booking Picker" => 12 element. Khong con vung
    # dat:zone nao; cap nhat hang thang di qua cac vung <!--m:id--> (tools/text_zones.py).
    # Van tay cu cua he cu nam trong git history, commit f5fcb5d tro ve truoc.
    "DAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'What Is Fast Track?', 'Services', 'Booking',
                   'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp Float',
                   'Mobile Book Now', 'Booking Picker'],
        "zones": [],
        "musts": ['add-to-cart=311', 'add-to-cart=313',
                  '[daf_price service="fast_track_arrival"]',
                  '[daf_price service="fast_track_departure"]',
                  'id="daf-pick-tpl"', '.daf-pick-btn',
                  # media query phai nham CA <button>, khong chi <a> -- neu khong thi
                  # nut hero lech trai o <=600px. Loi am, desktop khong lo ra.
                  '.daf-cta-row button'],
        "counts": {r'<img ': 16, r'schema\.org/Question': 10,
                   r'class="daf-review-card"': 16, r'class="daf-pick-btn"': 2,
                   r'class="daf-pick-chev"': 2,
                   r'<!--m:[a-z0-9-]+-->': 10, r'<!--/m:[a-z0-9-]+-->': 10},
    },
    # CAF -- DOI HAN 08/10/2026. Trang chu quay ve ban GOC 11 element (bo he tinh
    # thoi gian cho), cong element "Booking Picker" => 12 element. Khong con vung
    # dat:zone nao; cap nhat hang thang di qua cac vung <!--m:id--> (tools/text_zones.py).
    #
    # CAF KHAC PAF/DAF hai cho, dung sua cho "giong":
    #   1. Khong co schema.org/FAQPage -- 12 the .caf-faq tran, khong microdata.
    #   2. Khong co media query nao, khong co .caf-cta-row. Trang tu ghi "100% inline,
    #      khong <style>, khong media query". Nen KHONG co must '.caf-cta-row button'
    #      nhu PAF/DAF -- phai kiem nut hero bang RENDER 390px thay vi bang chuoi.
    "CAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'What Is Fast Track?', 'Services', 'Booking',
                   'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp Float',
                   'Mobile Book Now', 'Booking Picker'],
        "zones": [],
        "musts": ['add-to-cart=311', 'add-to-cart=313',
                  '[caf_price service="fast_track_arrival"]',
                  '[caf_price service="fast_track_departure"]',
                  'id="caf-pick-tpl"', '.caf-pick-btn', 'id="caf-marquee"'],
        # Bang review CAF KHONG dung class .caf-review-card nhu PAF/DAF: the la div tran,
        # ban sao do JS clone khi chay. Nen dem bang chuoi 5 sao -- moi the dung mot lan.
        "counts": {r'<img ': 16, r'class="caf-faq"': 12,
                   r'\u2605\u2605\u2605\u2605\u2605': 11,
                   r'class="caf-pick-btn"': 2, r'class="caf-pick-chev"': 2,
                   r'<!--m:[a-z0-9-]+-->': 10, r'<!--/m:[a-z0-9-]+-->': 10},
    },
    # SAF -- DOI HAN 08/10/2026. Trang chu quay ve ban GOC 11 element (bo he tinh
    # thoi gian cho), cong element "Booking Picker" => 12 element. Khong con vung
    # dat:zone nao; cap nhat hang thang di qua cac vung <!--m:id--> (tools/text_zones.py).
    #
    # SAF KHAC BA SITE KIA hai cho, dung sua cho "giong":
    #   1. Picker dung tien to "sgn-", KHONG phai "saf-". Gia van la [saf_price ...].
    #      Review card cung la .sgn-review-card.
    #   2. Element 10 va 11 ten khac: "Whatsapp & Mess" va "Book Now Button"
    #      (PAF/DAF/CAF la "Whatsapp Float" / "Mobile Book Now").
    "SAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'What Is Fast Track?', 'Services', 'Booking',
                   'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp & Mess',
                   'Book Now Button', 'Booking Picker'],
        "zones": [],
        "musts": ['add-to-cart=311', 'add-to-cart=313',
                  '[saf_price service="fast_track_arrival"]',
                  '[saf_price service="fast_track_departure"]',
                  'id="sgn-pick-tpl"', '.sgn-pick-btn', '#sgn-pick-panel'],
        "counts": {r'<img ': 15, r'schema\.org/Question': 11,
                   r'class="sgn-review-card"': 16,
                   r'class="sgn-pick-btn"': 2, r'class="sgn-pick-chev"': 2,
                   r'<!--m:[a-z0-9-]+-->': 10, r'<!--/m:[a-z0-9-]+-->': 10},
    },
    # HAF -- DOI HAN 08/10/2026. Trang chu quay ve ban GOC 11 element (bo he tinh
    # thoi gian cho), cong element "Booking Picker" => 12 element. Khong con vung
    # dat:zone nao; cap nhat hang thang di qua cac vung <!--m:id--> (tools/text_zones.py).
    #
    # HAF KHAC BON SITE KIA ba cho, dung sua cho "giong":
    #   1. The so la hang "Save | 1 - 3 hours" -- THOI GIAN TIET KIEM, khong phai
    #      do dai hang cho. Vung ten la save-figure / save-note, KHONG phai
    #      queue-figure / queue-note.
    #   2. BA shortcode gia khac nhau: fast_track, connection, vip_departure
    #      (bon site kia chi co fast_track_arrival + fast_track_departure).
    #   3. Element 10 va 11 ten khac: "Whatsapp & Mess" va "Book Now Button"
    #      (giong SAF, khac PAF/DAF/CAF).
    "HAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'What Is Fast Track?', 'Services', 'Booking',
                   'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp & Mess',
                   'Book Now Button', 'Booking Picker'],
        "zones": [],
        "musts": ['add-to-cart=311', 'add-to-cart=313',
                  '[haf_price service="fast_track"]',
                  '[haf_price service="connection"]',
                  '[haf_price service="vip_departure"]',
                  'id="haf-pick-tpl"', '.haf-pick-btn', '#haf-pick-panel'],
        "counts": {r'<img ': 17, r'schema\.org/Question': 11,
                   r'class="haf-review-card"': 16,
                   r'class="haf-pick-btn"': 2, r'class="haf-pick-chev"': 2,
                   r'<!--m:[a-z0-9-]+-->': 12, r'<!--/m:[a-z0-9-]+-->': 12},
    },
}


def parse_edit_url(url):
    """-> (page_id, host). Chap nhan post.php?post=N&action=edit hoac chi so N."""
    if re.fullmatch(r"\d+", url.strip()):
        return int(url.strip()), None
    u = urlparse(url)
    pid = parse_qs(u.query).get("post", [None])[0]
    if not pid or not pid.isdigit():
        sys.exit(f"khong doc duoc ID tu --edit-url: {url}\n"
                 f"   can dang .../wp-admin/post.php?post=NNN&action=edit")
    if not u.netloc:
        sys.exit("--edit-url thieu ten mien")
    return int(pid), u.netloc


def cdata(tag, value):
    return f"  <{tag}><![CDATA[{value.replace(']]>', ']]]]><![CDATA[>')}]]></{tag}>"


def build_xml(content, page_id, month, sha):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<data>", " <item>",
             f"  <ID>{page_id}</ID>",
             "  <post_type>page</post_type>",
             cdata("wait_month", month),
             cdata("content_sha256", sha),
             cdata("post_content", content), " </item>", "</data>", ""]
    xml = "\n".join(lines)
    item = ET.fromstring(xml).find("item")        # tu kiem: parse lai, doi chieu tung byte
    assert item.findtext("post_content") == content, "noi dung sau parse KHAC ban goc"
    assert int(item.findtext("ID")) == page_id
    return xml


def push(repo, files, month, site):
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        return False, "khong co GH_TOKEN trong moi truong"
    tmp = tempfile.mkdtemp()
    url = f"https://x-access-token:{tok}@github.com/{repo}.git"
    try:
        r = subprocess.run(["git", "clone", "--depth", "1", url, tmp + "/r"],
                           capture_output=True, text=True, timeout=180)
        if r.returncode:
            return False, (r.stderr or r.stdout).strip().replace(tok, "***")[:400]
        for rel, src in files.items():
            dst = os.path.join(tmp, "r", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
        env = {**os.environ, "GIT_AUTHOR_NAME": "claude", "GIT_COMMITTER_NAME": "claude",
               "GIT_AUTHOR_EMAIL": "noreply@anthropic.com",
               "GIT_COMMITTER_EMAIL": "noreply@anthropic.com"}
        subprocess.run(["git", "-C", tmp + "/r", "add", "-A"], check=True, capture_output=True)
        st = subprocess.run(["git", "-C", tmp + "/r", "status", "--porcelain"],
                            capture_output=True, text=True)
        if not st.stdout.strip():
            return True, "khong co gi thay doi, bo qua commit"
        subprocess.run(["git", "-C", tmp + "/r", "commit", "-m", f"{site} homepage {month}"],
                       check=True, capture_output=True, env=env)
        r = subprocess.run(["git", "-C", tmp + "/r", "push"], capture_output=True, text=True,
                           timeout=180)
        if r.returncode:
            return False, (r.stderr or r.stdout).strip().replace(tok, "***")[:400]
        return True, "da push"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def baseline_from(wait_path):
    """Lay MOC DOI CHIEU cho phep thu don dieu thang sau (luat 12).

    Vi sao phai ghi vao latest.json: thang sau can biet thang nay DA CONG BO dai nao,
    luu luong bao nhieu, va MO MAY QUAY -- ca ba. Trang HTML chi in dai va so chuyen,
    khong in `pax` lan don bay, nen doc tu trang la doc thieu: mot tran giam di vi da
    them quay thi hop le, giam di ma KHONG them quay thi la vặn nhầm cần. Khong co so
    quay thi khong phan biet duoc hai truong hop.
    """
    d = json.load(open(wait_path, encoding="utf-8"))
    asm = d.get("assumptions", {})
    return {
        "month": d.get("month"),
        "bands": [{"band": b["band"], "flights": b.get("flights"), "pax": b.get("pax"),
                   "standard": b.get("standard")} for b in d.get("bands", [])],
        "levers": {"month_uplift": asm.get("month_uplift"),
                   "surge": asm.get("surge_counters", asm.get("surge")),
                   "counters_day": asm.get("counters_day")},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True)
    ap.add_argument("--month", required=True)
    ap.add_argument("--edit-url", required=True)
    ap.add_argument("--site", default="PAF")
    ap.add_argument("--repo", default="")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--wait-json", default="",
                    help="{site}-wait-YYYY-MM.json cua thang nay. Ghi MOC DOI CHIEU vao "
                         "latest.json de thang sau chay duoc phep thu don dieu (luat 12) "
                         "bang so chinh xac, khong phai bang cach do chu tren trang.")
    a = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}", a.month):
        sys.exit("--month phai dang YYYY-MM")
    prof = PROFILE.get(a.site) or sys.exit(f"chua co van tay cho site {a.site}")
    page_id, host = parse_edit_url(a.edit_url)
    content = open(a.page, encoding="utf-8").read()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import qc                                      # cong QC: khong PASS thi khong dung XML
    print("--- QC trang ---")
    if qc.main(a.page, prof["labels"], prof["musts"], prof["counts"], prof["zones"]):
        sys.exit("QC FAIL -> dung lai, khong dung XML")

    # TIEU DE THE HERO -- vi tri KHAC NHAU giua cac site, phai kiem theo tung site.
    #   PQC/DAD/CXR/HAN: tieu de la phan TINH, nam NGOAI vung. Lot VAO trong thi thang sau
    #                    update_zones.py xoa mat ma khong ai bao -- loi am da dinh nhieu lan.
    #   SGN:             toan bo ruot the (tieu de -> ba hang) nam TRONG vung. Chu site chot
    #                    06/10/2026 giu cau truc goc cua SAF, nen o day tieu de PHAI o TRONG.
    #                    Keo no ra ngoai la doi cau truc -- dung cai chu site tu choi.
    # PROFILE[site]["hero_title_in_zone"] quyet dinh chieu kiem. Mac dinh False (ngoai vung).
    ht = prof.get("hero_title")
    if ht:
        zm = re.search(r"<!--dat:zone:wait-hero-->(.*?)<!--/dat:zone:wait-hero-->",
                       content, re.S)
        if not zm:
            sys.exit("khong tim thay vung wait-hero")
        if content.count(ht) != 1:
            sys.exit(f"tieu de the hero {ht!r} xuat hien {content.count(ht)} lan, can 1")
        trong_vung = ht in zm.group(1)
        phai_trong = prof.get("hero_title_in_zone", False)
        if trong_vung and not phai_trong:
            sys.exit(f"tieu de the hero {ht!r} lot VAO TRONG vung wait-hero -- "
                     "thang sau update_zones.py se xoa mat no")
        if phai_trong and not trong_vung:
            sys.exit(f"tieu de the hero {ht!r} NAM NGOAI vung wait-hero -- o site nay no "
                     "phai o TRONG (render_hero sinh ra no). Xem ghi chu ngay tren.")
        print(f"  tieu de hero: OK ({ht}) -- {'trong vung' if trong_vung else 'ngoai vung'}")

    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    xml = build_xml(content, page_id, a.month, sha)
    slug = a.site.lower()
    meta = {"site": a.site, "month": a.month, "page_id": page_id, "host": host,
            "edit_url": a.edit_url, "content_sha256": sha,
            "content_bytes": len(content.encode("utf-8")), "generated": date.today().isoformat()}
    if a.wait_json:
        meta["baseline"] = baseline_from(a.wait_json)
        if meta["baseline"]["month"] != a.month:
            sys.exit(f"--wait-json la thang {meta['baseline']['month']!r} nhung --month "
                     f"la {a.month!r}. Sai file -> moc doi chieu thang sau se sai.")

    os.makedirs(a.outdir, exist_ok=True)
    paths = {f"{slug}/home/latest.xml": os.path.join(a.outdir, "latest.xml"),
             f"{slug}/home/latest.json": os.path.join(a.outdir, "latest.json")}
    open(paths[f"{slug}/home/latest.xml"], "w", encoding="utf-8").write(xml)
    open(paths[f"{slug}/home/latest.json"], "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

    print(f"\n--- XML ---\n  1 item · ID {page_id} · post_content "
          f"{meta['content_bytes']:,} bytes · sha256 {sha[:16]}…")

    if a.repo and not a.no_push:
        ok, msg = push(a.repo, paths, a.month, a.site)
        print(f"\n--- GitHub {a.repo} ---\n  {'OK' if ok else 'KHONG DAY DUOC'}: {msg}")
        if ok:
            print(f"  URL co dinh cho cron:\n"
                  f"  https://raw.githubusercontent.com/{a.repo}/main/{slug}/home/latest.xml")
    else:
        print(f"\n--- chua day len GitHub ---\n  file nam o {a.outdir}/, keo vao repo theo duong dan:")
        for rel in paths:
            print(f"    {rel}")

    print(f"\n--- VIEC CUA BAN ---\n  Mo: {a.edit_url}\n  Dan toan bo HTML vao, bam Update. Het.")


if __name__ == "__main__":
    main()
