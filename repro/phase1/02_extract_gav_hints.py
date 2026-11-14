#!/usr/bin/env python3
"""Giai doan 1 - Buoc 3a (offline): suy ra ten class day du (FQCN) tu duong dan file VF
va goi y phien ban bi anh huong tu mo ta CVE.  Chua goi mang.

Chay: python 02_extract_gav_hints.py --data repro/phase1/data
"""
import argparse, csv, json, pathlib, re

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
a = ap.parse_args()
d = pathlib.Path(a.data)
rows = list(csv.DictReader(open(d / "ground_truth_vf.csv", encoding="utf-8")))
desc = json.load(open(d / "cve_description.json", encoding="utf-8"))

ROOTS = {"org", "com", "net", "io", "javax", "edu", "de", "ch", "fr", "nl", "uk", "jp",
         "ru", "cn", "se", "it", "es", "be", "at", "dk", "fi", "no", "pl", "cz", "hu", "me"}

def fqcn(path: str):
    """Tra ve (fqcn, do_tin_cay).  'high' neu co moc src/main/java hoac java/;
    'medium' neu doan tu goi goc (org/com/...); 'none' neu khong doan duoc."""
    p = path.replace("\\", "/")
    parts = p.split("/")
    for i in range(len(parts) - 1, -1, -1):          # moc 'java' gan nhat tu phai
        if parts[i] == "java" and i + 1 < len(parts) - 0:
            rest = parts[i + 1:]
            if len(rest) >= 2:
                return ".".join(rest).removesuffix(".java"), "high"
    for i, seg in enumerate(parts[:-1]):
        if seg in ROOTS:
            return ".".join(parts[i:]).removesuffix(".java"), "medium"
    return "", "none"

VER = r"\d+(?:\.\d+)+(?:[.\-]?(?:[A-Za-z]+\d*))?"
PAT_BEFORE = re.compile(r"(?:before|prior to|earlier than|through|up to(?: and including)?|"
                        r"<=?|and earlier)\s+(" + VER + ")", re.I)
PAT_ALL = re.compile(VER)

def versions(text: str):
    before = []
    for m in PAT_BEFORE.finditer(text):
        v = m.group(1).rstrip(".")
        if v not in before:
            before.append(v)
    allv = []
    for m in PAT_ALL.finditer(text):
        v = m.group(0).rstrip(".")
        if v not in allv:
            allv.append(v)
    return before, allv

out_rows = []
for r in rows:
    f, conf = fqcn(r["file"])
    text = desc.get(r["cve"], "")
    before, allv = versions(text)
    out_rows.append(dict(cve=r["cve"], fqcn=f, fqcn_conf=conf, method=r["method"],
                         version_bound="|".join(before), versions_all="|".join(allv),
                         n_versions=len(allv), file=r["file"]))

with open(d / "gav_hints.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys())); w.writeheader(); w.writerows(out_rows)

n = len(out_rows)
conf = {k: sum(1 for r in out_rows if r["fqcn_conf"] == k) for k in ("high", "medium", "none")}
nv = sum(1 for r in out_rows if r["versions_all"])
nb = sum(1 for r in out_rows if r["version_bound"])
print(f"VF: {n}")
print(f"FQCN do tin cay cao / trung binh / khong: {conf['high']} / {conf['medium']} / {conf['none']}")
print(f"Co it nhat 1 phien ban trong mo ta       : {nv}/{n}")
print(f"Co moc 'before/prior to/through ...'     : {nb}/{n}")
print("Can xem tay (fqcn none hoac khong co phien ban):")
for r in out_rows:
    if r["fqcn_conf"] == "none" or not r["versions_all"]:
        print("  ", r["cve"], "|", r["fqcn"] or "(khong doan duoc)", "|", r["file"][:70])
print(f"\nDa ghi {d/'gav_hints.csv'}")
