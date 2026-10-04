"""Cổng QC. Exit 1 nếu có lỗi."""
import re, sys
from collections import Counter
from html.parser import HTMLParser

VOID = {"area","base","br","col","embed","hr","img","input","link","meta","source","track","wbr",
        "path","polyline","circle","line","rect","polygon"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.err, self.ids, self.hrefs = [], [], [], []

    def handle_starttag(self, t, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if t == "a" and a.get("href"): self.hrefs.append(a["href"])
        if t not in VOID: self.stack.append(t)

    def handle_endtag(self, t):
        if t in VOID: return
        if self.stack and self.stack[-1] == t: self.stack.pop()
        else:
            self.err.append(f"</{t}> thừa (đang mở {self.stack[-3:]})")
            if t in self.stack:
                while self.stack and self.stack.pop() != t: pass


def main(path, labels, musts, counts, zones):
    s = open(path, encoding="utf-8").read()
    e = []
    blocks = re.findall(r'\[ux_html label="([^"]+)"\]\n(.*?)\n\[/ux_html\]', s, re.S)
    if [b[0] for b in blocks] != labels:
        e.append(f"thứ tự element sai: {[b[0] for b in blocks]}")
    ids, hrefs = [], []
    for label, html in blocks:
        # BOC COMMENT TRUOC, roi moi boc script/style. Nguoc lai la sai: mot chu "<style>"
        # nam trong comment (vi du ghi chu "100% inline, khong <style>") se bat cap voi
        # the </style> that o phia duoi va NUOT tron phan markup o giua -> QC mu ca mang.
        # Da dinh that o Hero Banner cua CAF: mat 8.663 byte khoi tam nhin cua QC.
        clean = re.sub(r"<!--.*?-->", "", html, flags=re.S)
        clean = re.sub(r"<(script|style)\b.*?</\1>", "", clean, flags=re.S)
        p = P(); p.feed(clean)
        if p.stack: e.append(f"[{label}] thẻ chưa đóng {p.stack}")
        e += [f"[{label}] {x}" for x in p.err]
        ids += p.ids; hrefs += p.hrefs
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup: e.append(f"id trùng: {dup}")
    for h in set(hrefs):
        if h.startswith("#") and len(h) > 1 and h[1:] not in ids:
            e.append(f"anchor không có đích: {h}")
    for z in zones:
        for mark in (f"<!--dat:zone:{z}-->", f"<!--/dat:zone:{z}-->"):
            if s.count(mark) != 1: e.append(f"{mark} xuất hiện {s.count(mark)} lần")
    for pat, want in counts.items():
        got = len(re.findall(pat, s))
        if got != want: e.append(f"đếm {pat!r}: {got}, cần {want}")
    for must in musts:
        if must not in s: e.append(f"thiếu: {must}")
    for cmt in re.finditer(r"<!--", s):          # comment vỡ sẽ rò chữ ra trang
        seg = s[cmt.end():]
        c = seg.find("-->")
        if c == -1 or "<!--" in seg[:c]: e.append("comment HTML bị vỡ")
    print(f"{len(blocks)} element · {len(ids)} id · {len(hrefs)} link")
    print("QC PASS" if not e else "QC FAIL")
    for x in dict.fromkeys(e): print(" -", x)
    return 0 if not e else 1
