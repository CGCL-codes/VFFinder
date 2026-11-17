#!/usr/bin/env python3
"""Hoi dap tung dong de dien cot verdict/note cua spotcheck.csv (luu ngay sau moi cau tra loi).
Chay: python 04b_fill_verdicts.py --data repro/phase1/data
Tra loi: Y (ban chon DE BI TAN CONG) | N (khong) | ? (khong xac dinh) | s (bo qua) | q (thoat)
"""
import argparse, csv, pathlib, re, textwrap

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--redo", action="store_true", help="hoi lai ca nhung dong da co verdict")
a = ap.parse_args()
p = pathlib.Path(a.data) / "spotcheck.csv"
with open(p, newline="", encoding="utf-8") as f:
    rd = csv.DictReader(f); cols = rd.fieldnames; rows = list(rd)

def save():
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

todo = [i for i, r in enumerate(rows) if a.redo or not r["verdict"].strip()]
print(f"{len(todo)}/{len(rows)} dong can danh gia.\n")
for k, i in enumerate(todo, 1):
    r = rows[i]
    print("=" * 78)
    print(f"[{k}/{len(todo)}] {r['cve']}   thu vien: {r['artifact']}")
    print(f"   PHIEN BAN DA CHON: {r['chosen_version']}      ({r['reason']})")
    print(f"   cac ung vien khac: {r['other_versions']}")
    print("   mo ta: " + textwrap.shorten(re.sub(r"\s+", " ", r["description"]), 300))
    print(f"   doi chieu: {r['osv_url']}")
    print(f"              {r['nvd_url']}")
    while True:
        v = input("   verdict [Y/N/?/s/q]: ").strip()
        if v.lower() in ("y", "n", "?", "s", "q"):
            break
        print("   (chi nhan Y, N, ?, s, q)")
    if v.lower() == "q":
        break
    if v.lower() == "s":
        continue
    r["verdict"] = v.upper()
    r["note"] = input("   ghi chu (Enter de bo qua): ").strip()
    save()
save()
done = sum(1 for r in rows if r["verdict"].strip())
print(f"\nDa luu {p}. Da danh gia {done}/{len(rows)}.")
if done == len(rows):
    print("Xong. Chay:  python 04_spotcheck.py summary --data " + str(p.parent))
