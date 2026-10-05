"""Chay mo hinh cho mot thang tu file inputs. Deterministic: cung input -> cung output."""
import json, sys
import paf_queue_model as M


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
    print(f"  hero  {h['peak']['range'][0]}-{h['peak']['range'][1]} phut  {h['peak']['window']}")
    for b in d["bands"]:
        s = b["standard"]
        print(f"  {b['band']}  {b.get('tier','-'):>8}  "
              f"{(str(s[0])+'-'+str(s[1])) if s else '-':>8}  {b['flights']} ch")


if __name__ == "__main__":
    main(*sys.argv[1:3])
