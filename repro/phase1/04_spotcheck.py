#!/usr/bin/env python3
"""Giai doan 1 - Buoc 5: chon mau ngau nhien (co phan tang) cac CVE 'ok' de DOI CHIEU THU CONG
phien ban da chon voi NVD/OSV, roi tinh ty le dung.

B1  python 04_spotcheck.py sample  --data repro/phase1/data --n 10
      -> ghi spotcheck.csv (cot verdict de trong) va in danh sach de doi chieu
B2  Mo spotcheck.csv, dien cot verdict: Y (phien ban da chon DE BI TAN CONG), N (khong), ? (khong xac dinh)
B3  python 04_spotcheck.py summary --data repro/phase1/data
      -> ty le dung + khoang tin cay Wilson 95%
"""
import argparse, csv, json, math, pathlib, random, re, textwrap

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["sample", "summary"])
ap.add_argument("--data", required=True)
ap.add_argument("--n", type=int, default=10)
ap.add_argument("--seed", type=int, default=42)
a = ap.parse_args()
d = pathlib.Path(a.data)
out_path = d / "spotcheck.csv"


def stratum(reason):
    r = reason or ""
    if r.startswith("thu cong"):
        return "D_thu_cong"
    if r.startswith("truoc moc sua"):
        return "A_truoc_moc_sua"
    if r.startswith("moc cuoi") or r.startswith("gan moc cuoi"):
        return "B_moc_cuoi"
    if r.startswith("phien ban duoc nhac"):
        return "C_ban_duoc_nhac"
    return "E_khac"


if a.mode == "sample":
    rows = list(csv.DictReader(open(d / "gav_resolved.csv", encoding="utf-8")))
    desc = json.load(open(d / "cve_description.json", encoding="utf-8"))
    ok = [r for r in rows if r["status"] == "ok"]
    # moi CVE chi lay 1 dong (tranh trung lap CVE co 2 ham VF)
    seen, uniq = set(), []
    for r in ok:
        if r["cve"] not in seen:
            seen.add(r["cve"]); uniq.append(r)
    groups = {}
    for r in uniq:
        groups.setdefault(stratum(r["reason"]), []).append(r)
    rnd = random.Random(a.seed)
    # chia deu theo ty le, moi tang co it nhat 1 neu co
    total = len(uniq)
    quota = {k: max(1, round(a.n * len(v) / total)) for k, v in groups.items()}
    while sum(quota.values()) > a.n:
        k = max(quota, key=lambda x: quota[x]); quota[k] -= 1
    while sum(quota.values()) < a.n:
        k = max(groups, key=lambda x: len(groups[x]) - quota[x]); quota[k] += 1
    pick = []
    for k, v in sorted(groups.items()):
        pick += rnd.sample(v, min(quota[k], len(v)))
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cve", "stratum", "artifact", "chosen_version", "reason", "other_versions",
                    "nvd_url", "osv_url", "description", "verdict", "note"])
        for r in pick:
            c = r["cve"]
            w.writerow([c, stratum(r["reason"]), f'{r["group"]}:{r["artifact"]}', r["chosen_version"],
                        r["reason"], r["other_versions"],
                        f"https://nvd.nist.gov/vuln/detail/{c}", f"https://osv.dev/vulnerability/{c}",
                        re.sub(r"\s+", " ", desc.get(c, ""))[:400], "", ""])
    print(f"Quota theo tang: {quota}  (tong {len(pick)}/{total} CVE ok)\n")
    for i, r in enumerate(pick, 1):
        print(f"[{i}] {r['cve']}  {r['group']}:{r['artifact']}  phien ban chon = {r['chosen_version']}")
        print(f"    ly do: {r['reason']}   | cac ung vien khac: {r['other_versions']}")
        print("    mo ta: " + textwrap.shorten(re.sub(r"\s+", " ", desc.get(r['cve'], '')), 230))
        print(f"    https://osv.dev/vulnerability/{r['cve']}\n")
    print(f"Da ghi {out_path}. Dien cot 'verdict' (Y/N/?) roi chay: python 04_spotcheck.py summary --data {a.data}")

else:
    rows = list(csv.DictReader(open(out_path, encoding="utf-8")))
    v = [r["verdict"].strip().upper() for r in rows]
    y, nn, q, blank = v.count("Y"), v.count("N"), v.count("?"), sum(1 for x in v if x == "")
    judged = y + nn
    print(f"Y={y}  N={nn}  ?={q}  chua dien={blank}  (tong {len(rows)})")
    if blank:
        print("CANH BAO: con dong chua dien verdict.")
    if judged:
        p = y / judged; z = 1.96
        den = 1 + z * z / judged
        centre = (p + z * z / (2 * judged)) / den
        half = z * math.sqrt(p * (1 - p) / judged + z * z / (4 * judged * judged)) / den
        print(f"Ty le phien ban chon dung (loai ?): {y}/{judged} = {100*p:.1f}%   Wilson 95% CI: [{100*(centre-half):.1f}%, {100*(centre+half):.1f}%]")
        for st in sorted({r['stratum'] for r in rows}):
            sub = [r['verdict'].strip().upper() for r in rows if r['stratum'] == st]
            sy, sn = sub.count("Y"), sub.count("N")
            if sy + sn:
                print(f"   {st}: {sy}/{sy+sn}")
        for r in rows:
            if r["verdict"].strip().upper() == "N":
                print("   SAI:", r["cve"], r["artifact"], r["chosen_version"], "|", r["note"])
    print("(Voi mau nho, khoang tin cay rat rong - hay ghi ro trong bao cao.)")
