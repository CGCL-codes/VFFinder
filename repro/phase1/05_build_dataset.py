#!/usr/bin/env python3
"""Giai doan 1 - Buoc 6: gop ground truth + mo ta + ket qua Maven thanh BANG DU LIEU CUOI
(moi dong = 1 ham VF), kiem tra file jar ton tai tren dia.

Chay: python 05_build_dataset.py --data repro/phase1/data
Ghi : dataset_final.csv , dataset_summary.txt
"""
import argparse, csv, json, pathlib, collections

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--jars", default=None)
a = ap.parse_args()
d = pathlib.Path(a.data)
jars = pathlib.Path(a.jars) if a.jars else d.parent / "jars"

gt = list(csv.DictReader(open(d / "ground_truth_vf.csv", encoding="utf-8")))
hints = list(csv.DictReader(open(d / "gav_hints.csv", encoding="utf-8")))
res = list(csv.DictReader(open(d / "gav_resolved.csv", encoding="utf-8")))
desc = json.load(open(d / "cve_description.json", encoding="utf-8"))
excl = {}
ep = d / "excluded.csv"
if ep.exists():
    excl = {r["cve"]: r["reason"] for r in csv.DictReader(open(ep, encoding="utf-8"))}

assert len(gt) == len(hints) == len(res), f"so dong lech: gt={len(gt)} hints={len(hints)} resolved={len(res)}"
INFERRED_FQCN = {"CVE-2018-12972"}      # FQCN suy tu cau truc du an, khong co trong du lieu goc
rows, problems = [], []
for g, h, r in zip(gt, hints, res):
    assert g["cve"] == h["cve"] == r["cve"] and g["method"] == h["method"] == r["method"], f"lech thu tu: {g['cve']}"
    c = g["cve"]
    jar = sp = ""
    jar_exists = src_exists = False
    if r["status"] == "ok":
        stem = f'{r["group"]}__{r["artifact"]}-{r["chosen_version"]}'
        jp, sj = jars / f"{stem}.jar", jars / f"{stem}-sources.jar"
        jar_exists, src_exists = jp.exists(), sj.exists()
        jar, sp = str(jp), str(sj)
        if not jar_exists:
            problems.append(f"{c}: thieu {jp.name}")
        if str(r["src_ok"]) == "True" and not src_exists:
            problems.append(f"{c}: thieu {sj.name}")
    has_desc = bool(desc.get(c, "").strip())
    in_exp = (r["status"] == "ok") and has_desc and (c not in excl) and jar_exists
    flags = []
    if c in INFERRED_FQCN: flags.append("fqcn_suy_dien")
    if not has_desc: flags.append("thieu_mo_ta")
    if c in excl: flags.append("bi_loai")
    if r["reason"] == "thu cong": flags.append("phien_ban_thu_cong")
    rows.append(dict(cve=c, in_experiment=in_exp, flags="|".join(flags), fqcn=r["fqcn"] or h["fqcn"],
                     method=g["method"], params=g["params"], vf_file=g["file"],
                     group=r["group"], artifact=r["artifact"], version=r["chosen_version"],
                     version_reason=r["reason"], status=r["status"] + (":excluded" if c in excl else ""),
                     jar_path=jar, sources_path=sp if src_exists else "", description=" ".join(desc.get(c, "").split())))

with open(d / "dataset_final.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

use = [r for r in rows if r["in_experiment"] == True]
cves = {r["cve"] for r in use}
libs = {(r["group"], r["artifact"]) for r in use}
lines = [
    "=== TOM TAT BANG DU LIEU CUOI ===",
    f"Dong VF tong (ground truth repo)       : {len(rows)}  thuoc {len({r['cve'] for r in rows})} CVE",
    f"Dong VF dung duoc cho thuc nghiem      : {len(use)}  thuoc {len(cves)} CVE",
    f"So thu vien (group:artifact) khac nhau : {len(libs)}",
    f"CVE bi loai (excluded.csv)             : {sorted(excl)}",
    f"CVE thieu mo ta (khong chay duoc VFFinder): {sorted({r['cve'] for r in rows if 'thieu_mo_ta' in r['flags']})}",
    f"VF co co 'fqcn_suy_dien'               : {[r['cve'] for r in rows if 'fqcn_suy_dien' in r['flags']]}",
    f"VF co phien ban dien thu cong          : {sum(1 for r in use if 'phien_ban_thu_cong' in r['flags'])}",
    "Ly do chon phien ban: " + str(dict(collections.Counter((r['version_reason'] or '').split(' ')[0] + ' ' + ((r['version_reason'] or '').split(' ')[1] if len((r['version_reason'] or '').split(' ')) > 1 else '') for r in use))),
    "So voi paper: 77 CVE / 77 VF / 75 du an / 30 CWE.",
]
if problems:
    lines += ["", "CANH BAO file thieu tren dia:"] + ["  " + p for p in problems]
(d / "dataset_summary.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print(f"\nDa ghi {d/'dataset_final.csv'}")
