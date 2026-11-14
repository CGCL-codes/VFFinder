#!/usr/bin/env python3
"""Giai doan 1 - Buoc 1+2: parse CVE_API (ground truth VF) va CVE_description,
doi chieu so luong, xuat bang CSV + bao cao.

Chay:  python 01_parse_ground_truth.py --root $VFF_ROOT --out ../data_phase1
"""
import argparse, csv, json, pathlib, re, collections

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True, help="thu muc VFFinder/VFFinder (chua resource/)")
ap.add_argument("--out", default="data_phase1")
a = ap.parse_args()
res = pathlib.Path(a.root) / "resource"
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)

CVE_RE = re.compile(r"^(CVE-\d{4}-\d+):(.*)$")

# ---------- 1. CVE_API:  CVE:duong/dan/File.java:method(params)@visibility ----------
api_rows, api_bad = [], []
for ln, line in enumerate((res / "CVE_API").read_text(encoding="utf-8").splitlines(), 1):
    if not line.strip():
        continue
    m = CVE_RE.match(line)
    if not m:
        api_bad.append((ln, line)); continue
    cve, rest = m.groups()
    # rest = <file>:<method>(<params>)@<vis>   (file khong chua ':' )
    try:
        file_path, sig = rest.split(":", 1)
        # co dong co hau to @public/@private..., co dong khong
        if "@" in sig:
            sig, _, vis = sig.rpartition("@")
        else:
            vis = ""
        name, _, params = sig.partition("(")
        params = params.rstrip(")")
    except ValueError:
        api_bad.append((ln, line)); continue
    cls = file_path.split("/")[-1].removesuffix(".java")
    api_rows.append(dict(cve=cve, file=file_path, cls=cls, method=name.strip(),
                         params=params.strip(), visibility=vis.strip(),
                         pkg="/".join(file_path.split("/")[:-1])))

# ---------- 2. CVE_description: moi CVE bat dau mot dong, mo ta co the xuong dong ----------
desc = {}
cur = None
for line in (res / "CVE_description").read_text(encoding="utf-8").splitlines():
    m = CVE_RE.match(line)
    if m:
        cur = m.group(1); desc[cur] = m.group(2).strip()
    elif cur and line.strip():
        desc[cur] += " " + line.strip()

# ---------- 3. Doi chieu ----------
gt = collections.defaultdict(list)
for r in api_rows:
    gt[r["cve"]].append(r)
S_api, S_desc = set(gt), set(desc)
both = sorted(S_api & S_desc)

with open(out / "ground_truth_vf.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(api_rows[0].keys())); w.writeheader(); w.writerows(api_rows)
with open(out / "cve_table.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["cve", "n_vf", "has_desc", "desc_words", "cls_in_desc", "vf_classes", "vf_methods"])
    for c in sorted(S_api | S_desc):
        vfs = gt.get(c, [])
        d = desc.get(c, "")
        cls_hit = any(v["cls"].lower() in d.lower() for v in vfs) if d else False
        w.writerow([c, len(vfs), c in S_desc, len(d.split()), cls_hit,
                    "|".join(v["cls"] for v in vfs), "|".join(v["method"] for v in vfs)])
json.dump(desc, open(out / "cve_description.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 4. Bao cao ----------
lens = [len(d.split()) for d in desc.values()]
cls_hits = sum(1 for c in both if any(v["cls"].lower() in desc[c].lower() for v in gt[c]))
meth_hits = sum(1 for c in both if any(v["method"].lower() in desc[c].lower() for v in gt[c]))
report = [
    "=== BAO CAO DOI CHIEU DU LIEU ===",
    f"Dong hop le trong CVE_API         : {len(api_rows)}  (dong loi: {len(api_bad)})",
    f"So CVE khac nhau trong CVE_API     : {len(S_api)}",
    f"CVE co >1 ham VF                   : { {c: len(v) for c, v in gt.items() if len(v) > 1} }",
    f"So CVE trong CVE_description       : {len(S_desc)}",
    f"CVE co CA mo ta LAN ground truth   : {len(both)}",
    f"Chi co ground truth (thieu mo ta)  : {sorted(S_api - S_desc)}",
    f"Chi co mo ta (thieu ground truth)  : {sorted(S_desc - S_api)}",
    f"So 'du an' (goi/thu vien) khac nhau: {len({r['pkg'].split('/')[0] for r in api_rows})} (top-level package, uoc luong)",
    f"Do dai mo ta (so tu): min={min(lens)} median={sorted(lens)[len(lens)//2]} max={max(lens)}",
    f"Dong VF khong ghi visibility (@...)  : {sum(1 for r in api_rows if not r['visibility'])}/{len(api_rows)}",
    f"Dong VF khong co ten ham           : {sum(1 for r in api_rows if not r['method'])}",
    f"Mo ta nhac TEN CLASS cua VF        : {cls_hits}/{len(both)} CVE ({100*cls_hits/len(both):.1f}%)",
    f"Mo ta nhac TEN HAM cua VF          : {meth_hits}/{len(both)} CVE ({100*meth_hits/len(both):.1f}%)",
    "",
    "So voi paper: 77 CVE / 77 VF / 75 du an / 30 CWE.",
]
for ln, l in api_bad:
    report.append(f"  [loi dong {ln}] {l}")
(out / "report.txt").write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))
print(f"\nDa ghi: {out}/ground_truth_vf.csv, cve_table.csv, cve_description.json, report.txt")
