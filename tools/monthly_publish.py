"""Mot lenh cho ca thang: kiem trang -> dung XML -> day len repo -> in URL edit."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from datetime import date
from urllib.parse import urlparse, parse_qs

# Van tay cau truc theo site. Site moi phai them mot muc o day.
PROFILE = {
    "PAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'Wait Times', 'What Is Fast Track?', 'Services',
                   'Booking', 'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp Float',
                   'Mobile Book Now', 'Booking Picker'],
        "zones": ['wait-hero', 'wait-section', 'wait-faq'],

        # The hero: BA HANG LA BA LY DO -- Save / From / 24-7 (chot 05/10/2026, ca 5 site).
        #   - tieu de la phan TINH, nam NGOAI vung wait-hero, khong mang ten thang
        #   - dong phu hang SAVE phai noi CA HAI dau cua phep tru, moi dau mot dong;
        #     hai chu "estimated" va "reach" khong duoc mat (xem skill tung site)
        "hero_title": 'Why Choose PQC Fast Track?',
        "musts": [
                  'Peak immigration queue: ',
                  'Estimate &middot; Updated ',
                  'With Fast Track: under&nbsp;','add-to-cart=311', 'add-to-cart=313',
                  '[paf_price service="fast_track_arrival"]',
                  '[paf_price service="fast_track_departure"]',
                  'id="wait-times"', 'id="paf-pick-tpl"', '#wait-times .paf-wt-num',
                  '#wait-times .paf-wt-ft', '#wait-times .paf-wt-btn', '.paf-pick-btn',
                  '#paf-pick-panel'],
        "counts": {r'<img ': 15, r'schema\.org/Question': 12,
                   r'class="paf-review-card"': 22, r'class="paf-pick-btn': 3},
    },
    "DAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'Wait Times', 'What Is Fast Track?', 'Services',
                   'Booking', 'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp Float',
                   'Mobile Book Now', 'Booking Picker'],
        "zones": ['wait-hero', 'wait-section', 'wait-faq'],

        # The hero: BA HANG LA BA LY DO -- Save / From / 24-7 (chot 05/10/2026, ca 5 site).
        #   - tieu de la phan TINH, nam NGOAI vung wait-hero, khong mang ten thang
        #   - dong phu hang SAVE phai noi CA HAI dau cua phep tru, moi dau mot dong;
        #     hai chu "estimated" va "reach" khong duoc mat (xem skill tung site)
        "hero_title": 'Why Choose DAD Fast Track?',
        "musts": [
                  'Peak immigration queue: ',
                  'With Fast Track: under&nbsp;','add-to-cart=311', 'add-to-cart=313',
                  '[daf_price service="fast_track_arrival"]',
                  '[daf_price service="fast_track_departure"]',
                  'id="wait-times"', 'id="daf-pick-tpl"', '#wait-times .daf-wt-num',
                  '#wait-times .daf-wt-ft', '#wait-times .daf-wt-btn', '.daf-pick-btn',
                  '#daf-pick-panel'],
        "counts": {r'<img ': 16, r'schema\.org/Question': 11,
                   r'class="daf-review-card"': 16, r'class="daf-pick-btn': 3},
    },
    "CAF": {
        "labels": ['Nav Bar', 'Hero Banner', 'Wait Times', 'What Is Fast Track?', 'Services',
                   'Booking', 'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp Float',
                   'Mobile Book Now', 'Booking Picker'],
        "zones": ['wait-hero', 'wait-section', 'wait-faq'],

        # The hero: BA HANG LA BA LY DO -- Save / From / 24-7 (chot 05/10/2026, ca 5 site).
        #   - tieu de la phan TINH, nam NGOAI vung wait-hero, khong mang ten thang
        #   - dong phu hang SAVE phai noi CA HAI dau cua phep tru, moi dau mot dong;
        #     hai chu "estimated" va "reach" khong duoc mat (xem skill tung site)
        "hero_title": 'Why Choose CXR Fast Track?',
        "musts": [
                  'Peak immigration queue: ',
                  'Estimate &middot; Updated ',
                  'With Fast Track: under&nbsp;','add-to-cart=311', 'add-to-cart=313',
                  '[caf_price service="fast_track_arrival"]',
                  '[caf_price service="fast_track_departure"]',
                  'id="wait-times"', 'id="caf-pick-tpl"', '#wait-times .caf-wt-num',
                  '#wait-times .caf-wt-ft', '#wait-times .caf-wt-btn', '.caf-pick-btn',
                  '#caf-pick-panel', 'id="caf-marquee"'],
        # CAF co 13 Question (12 cua site + 1 trong vung wait-faq), DAF co 11.
        # Bang review CAF KHONG dung class .caf-review-card nhu PAF/DAF: the la div tran,
        # va ban sao duoc JS nhan ra khi chay (clone + aria-hidden), khong nhan doi san
        # trong markup. Nen dem bang chuoi 5 sao - moi the dung mot lan.
        "counts": {r'<img ': 16, r'schema\.org/Question': 13,
                   r'\u2605\u2605\u2605\u2605\u2605': 11, r'class="caf-pick-btn': 3},
    },
    "SAF": {
        # BA cho SAF khac ba site kia -- doi mot trong ba la trang hong:
        #   1. ten element: "Whatsapp & Mess" / "Book Now Button" (khong phai
        #      "Whatsapp Float" / "Mobile Book Now").
        #   2. tien to: CSS dung sgn-, shortcode dung saf_. Lam sed 's/caf-/saf-/'
        #      se sinh ra saf-pick-btn -> khong khop CSS -> picker chet im.
        #   3. SAF co BA dich vu: them connection. Hai site kia chi hai.
        "labels": ['Nav Bar', 'Hero Banner', 'Wait Times', 'What Is Fast Track?', 'Services',
                   'Booking', 'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp & Mess',
                   'Book Now Button', 'Booking Picker'],
        "zones": ['wait-hero', 'wait-section', 'wait-faq'],

        # The hero: BA HANG LA BA LY DO -- Save / From / 24-7 (chot 05/10/2026, ca 5 site).
        #   - tieu de la phan TINH, nam NGOAI vung wait-hero, khong mang ten thang
        #   - dong phu hang SAVE phai noi CA HAI dau cua phep tru, moi dau mot dong;
        #     hai chu "estimated" va "reach" khong duoc mat (xem skill tung site)
        "hero_title": 'Why Choose SGN Fast Track?',
        "musts": [
                  'The standard immigration queue is estimated to reach&nbsp;',
                  'Fast Track gets you through in under&nbsp;','add-to-cart=311', 'add-to-cart=313',
                  '[saf_price service="fast_track_arrival"]',
                  '[saf_price service="fast_track_departure"]',
                  '[saf_price service="connection"]',
                  'id="wait-times"', 'id="sgn-pick-tpl"', '#wait-times .sgn-wt-num',
                  '#wait-times .sgn-wt-ft', '#wait-times .sgn-wt-btn', '.sgn-pick-btn',
                  '#sgn-pick-panel', 'id="sgn-carousel-track"',
                  # Fast Track o SAF co BA bac: Lighter ~10 · Moderate ~15 · Busy.
                  # SAF cong bo tran 20 phut, khac quy uoc 15 cua bon site kia.
                  # Hero: "in under&nbsp;20&nbsp;minutes." -- bang: "15&ndash;20 min"
                  # (cot bang hep, tren dien thoai mot cau day se xuong hai dong).
                  # Mat mot trong hai nghia la renderer da bi be ve quy uoc 15.
                  # Thang nao cung co khung Busy nen ca hai chuoi luon phai co mat;
                  # mat chung = hieu chuan da troi. Bat bien day du nam o saf/run_qc.py.
                  'in under&nbsp;20&nbsp;minutes.', '15&ndash;20 min', '~10 min'],
        "counts": {r'<img ': 15, r'schema\.org/Question': 12,
                   r'class="sgn-review-card"': 16, r'class="sgn-pick-btn': 3},
    },
    "HAF": {
        # BON cho HAF khac bon site kia -- doi mot trong bon la trang hong:
        #   1. ten element giong SAF: "Whatsapp & Mess" / "Book Now Button".
        #   2. tien to DON: CSS va shortcode deu dung `haf`. Khac SAF (sgn- + saf_).
        #      Port tu SAF phai doi saf_price TRUOC roi moi doi sgn-.
        #   3. TEN DICH VU khac moi site kia: fast_track / vip_departure / connection,
        #      khong phai fast_track_arrival / fast_track_departure.
        #   4. CHI MOT nut picker o hero (bon site kia hai) -> tong 2, khong phai 3.
        "labels": ['Nav Bar', 'Hero Banner', 'Wait Times', 'What Is Fast Track?', 'Services',
                   'Booking', 'Reviews', 'FAQs', 'Footer', 'Smooth Scroll', 'Whatsapp & Mess',
                   'Book Now Button', 'Booking Picker'],
        "zones": ['wait-hero', 'wait-section', 'wait-faq'],

        # The hero HAF giu MAU GOC cua trang: Save / From / 24-7, khong phai bang
        # so sanh nhu bon site kia (chot 05/10/2026).
        #   - tieu de la phan TINH, nam NGOAI vung wait-hero, khong mang ten thang
        #   - dong phu hang SAVE phai noi CA HAI dau cua phep tru, moi dau mot dong
        "hero_title": 'Why Choose HAN Fast Track?',
        "musts": [
                  'The standard immigration queue is estimated to reach&nbsp;',
                  'Fast Track gets you through in under&nbsp;',
                  'Why Choose HAN Fast Track?','add-to-cart=311', 'add-to-cart=313',
                  '[haf_price service="fast_track"]',
                  '[haf_price service="vip_departure"]',
                  '[haf_price service="connection"]',
                  'id="wait-times"', 'id="haf-pick-tpl"', '#wait-times .haf-wt-num',
                  '#wait-times .haf-wt-ft', '#wait-times .haf-wt-btn', '.haf-pick-btn',
                  '#haf-pick-panel', 'id="haf-carousel-track"', 'class="haf-marquee-track"',
                  # LUAT 7: nut vang hero la <button>, media query phai phu ca button.
                  # Mat dong nay = nut lech trai tren dien thoai, khong ai bao.
                  '.haf-cta-row button'],
        # Bang review HAF: 32 the = 16 goc + 16 ban sao aria-hidden. So LE hoac hai nua
        # khac nhau se lam bang giat moi vong (animation chay translateX(-50%)).
        "counts": {r'<img ': 17, r'schema\.org/Question': 12,
                   r'class="haf-review-card': 32, r'class="haf-pick-btn': 3},
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True)
    ap.add_argument("--month", required=True)
    ap.add_argument("--edit-url", required=True)
    ap.add_argument("--site", default="PAF")
    ap.add_argument("--repo", default="")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--no-push", action="store_true")
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

    # Tieu de the hero la phan TINH. Neu no lot VAO TRONG vung wait-hero thi thang sau
    # update_zones.py se xoa mat ma khong ai bao -- dung loai loi am da dinh nhieu lan.
    ht = prof.get("hero_title")
    if ht:
        zm = re.search(r"<!--dat:zone:wait-hero-->(.*?)<!--/dat:zone:wait-hero-->",
                       content, re.S)
        if not zm:
            sys.exit("khong tim thay vung wait-hero")
        if content.count(ht) != 1:
            sys.exit(f"tieu de the hero {ht!r} xuat hien {content.count(ht)} lan, can 1")
        if ht in zm.group(1):
            sys.exit(f"tieu de the hero {ht!r} lot VAO TRONG vung wait-hero -- "
                     "thang sau update_zones.py se xoa mat no")
        print(f"  tieu de hero tinh: OK ({ht})")

    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    xml = build_xml(content, page_id, a.month, sha)
    slug = a.site.lower()
    meta = {"site": a.site, "month": a.month, "page_id": page_id, "host": host,
            "edit_url": a.edit_url, "content_sha256": sha,
            "content_bytes": len(content.encode("utf-8")), "generated": date.today().isoformat()}

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
