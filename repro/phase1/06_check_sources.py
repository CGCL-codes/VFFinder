#!/usr/bin/env python3
"""Giai doan 1 - Buoc 7: kiem tra sources.jar co CHUA ma nguon cua class VF va TEN HAM VF khong.
(Class co trong .jar chua chac co .java trong -sources.jar - vd goi OSGi dong goi lai thu vien khac.)

Chay: python 06_check_sources.py --data repro/phase1/data
Ghi : source_check.csv , va in tom tat + danh sach loi
"""
import argparse, csv, pathlib, re, zipfile, collections

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
a = ap.parse_args()
d = pathlib.Path(a.data)
rows = [r for r in csv.DictReader(open(d / "dataset_final.csv", encoding="utf-8")) if r["in_experiment"] == "True"]

zcache = {}
def open_zip(path):
    if path not in zcache:
        z = zipfile.ZipFile(path)
        zcache[path] = (z, {n: n for n in z.namelist()})
    return zcache[path]

out = []
for r in rows:
    res = dict(cve=r["cve"], fqcn=r["fqcn"], method=r["method"], artifact=f'{r["group"]}:{r["artifact"]}:{r["version"]}',
               source_found="", method_found="", java_entry="", note="")
    sp = r["sources_path"]
    if not sp or not pathlib.Path(sp).exists():
        res.update(source_found="khong_co_sources_jar"); out.append(res); continue
    try:
        z, names = open_zip(sp)
    except Exception as e:
        res.update(source_found="loi_mo_zip", note=str(e)[:60]); out.append(res); continue
    exact = r["fqcn"].replace(".", "/") + ".java"
    entry = exact if exact in names else None
    how = "chinh_xac"
    if entry is None:                                   # thu tim theo ten file o thu muc khac
        simple = r["fqcn"].split(".")[-1] + ".java"
        cands = [n for n in names if n.endswith("/" + simple) or n == simple]
        if len(cands) == 1:
            entry, how = cands[0], "khac_duong_dan"
        elif len(cands) > 1:
            entry, how = cands[0], f"mo_ho({len(cands)})"
    if entry is None:
        res.update(source_found="khong_co_java"); out.append(res); continue
    text = z.read(entry).decode("utf-8", "ignore")
    m = r["method"]
    if not m or m.startswith("<"):
        mf = "NA"
    else:
        mf = str(re.search(r"\b" + re.escape(m) + r"\s*\(", text) is not None)
    res.update(source_found=how, method_found=mf, java_entry=entry)
    out.append(res)

with open(d / "source_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

n = len(out)
sf = collections.Counter(o["source_found"].split("(")[0] for o in out)
mf = collections.Counter(o["method_found"] for o in out if o["method_found"])
good = [o for o in out if o["source_found"] in ("chinh_xac", "khac_duong_dan") and o["method_found"] in ("True", "NA")]
print(f"Hang VF kiem tra: {n}")
print(f"Tim thay file .java : {dict(sf)}")
print(f"Ten ham xuat hien   : {dict(mf)}")
print(f"=> DAT CA HAI (co .java va co ham): {len(good)}/{n}")
bad = [o for o in out if o not in good]
if bad:
    print("\nCAN XEM LAI:")
    for o in bad:
        print(f"  {o['cve']:16} {o['artifact']:60} {o['source_found']:20} method_found={o['method_found'] or '-'}  ({o['method']})")
print(f"\nDa ghi {d/'source_check.csv'}")
