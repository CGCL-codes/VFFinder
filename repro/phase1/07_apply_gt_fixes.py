#!/usr/bin/env python3
"""Giai doan 1 - Buoc 8: ap dung cac SUA LOI ground truth (co ghi ly do) len 3 file CSV.
Doc  ground_truth_fixes.csv  (cot: cve,method_old,method_new,reason). Chay lai nhieu lan van an toan (idempotent).
LUU Y: ground_truth_vf.csv se bi 01_parse_ground_truth.py ghi de -> chay lai file nay sau khi chay lai 01.

Chay: python 07_apply_gt_fixes.py --data repro/phase1/data
"""
import argparse, csv, pathlib

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
a = ap.parse_args()
d = pathlib.Path(a.data)
fixes = list(csv.DictReader(open(d / "ground_truth_fixes.csv", encoding="utf-8")))
FILES = ["ground_truth_vf.csv", "gav_hints.csv", "gav_resolved.csv"]

for fn in FILES:
    p = d / fn
    if not p.exists():
        print(f"[bo qua] {fn} (khong ton tai)"); continue
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; rows = list(rd)
    changed = already = 0
    for fx in fixes:
        for r in rows:
            if r["cve"] != fx["cve"]:
                continue
            if r["method"] == fx["method_old"]:
                r["method"] = fx["method_new"]; changed += 1
            elif r["method"] == fx["method_new"]:
                already += 1
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"{fn:22} da sua: {changed}   da co san: {already}")
print("\nLy do da ghi nhan:")
for fx in fixes:
    print(f"  {fx['cve']}: {fx['method_old']} -> {fx['method_new']}  | {fx['reason']}")
