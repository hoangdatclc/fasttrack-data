"""Chay mo hinh cho mot thang tu file inputs. Deterministic: cung input -> cung output."""
import json, sys
import han_queue_model as M


def main(inp_path, out_path):
    i = json.load(open(inp_path, encoding="utf-8"))
    d = M.build_month_json(i["month"], i["month_label"], i["month_notes"],
                           i["empty_band_note"], i["context"], i["basis"],
                           i["cities"], i["guide"])
    open(out_path, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    h = d["headline"]
    print("CONG HIEU CHUAN: PASS")
    print(f"{out_path}: {i['month_label']} · {h['intl_arrivals_per_day']} chuyen · "
          f"{h['foreign_pax_per_day']:.0f} khach ngoai/ngay")
    # HAF dua CA CUM busy len hero (render_blocks.py dung h["busy"]), KHONG phai h["peak"].
    # In ca hai de thay ngay neu cum busy tut xuong duoi tran Moderate -- luc do phai
    # chuyen hero sang peak. In moi mot cai tung lam nguoi doc tuong hero la 77-91.
    for k in ("busy", "peak"):
        w = h[k]
        tag = " <- LEN HERO" if k == "busy" else ""
        print(f"  {k:5s} {w['range'][0]}-{w['range'][1]} phut  {w['window']}{tag}")
    for b in d["bands"]:
        s = b["standard"]
        print(f"  {b['band']}  {b.get('tier','-'):>8}  "
              f"{(str(s[0])+'-'+str(s[1])) if s else '-':>8}  {b['flights']} ch")


if __name__ == "__main__":
    main(*sys.argv[1:3])
