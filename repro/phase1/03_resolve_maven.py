#!/usr/bin/env python3
"""Giai doan 1 - Buoc 3b (v3): FQCN -> (groupId, artifactId) -> phien ban de bi tan cong -> jar.

Nguon (group, artifact):
  1) gav_manual.csv  (cot: fqcn,group,artifact,version ; NHIEU dong cho 1 fqcn = cac ung vien)
  2) --use-search : neu MOI ung vien thu cong deu khong ton tai tren Maven (hoac khong co dong nao),
     tra search.maven.org; CHI chap nhan khi class hiem (numFound <= 200).
Moi ung vien duoc XAC MINH bang cach mo jar xem co file .class cua FQCN hay khong (can --download).

Chay:  python 03_resolve_maven.py --data repro/phase1/data --download --use-search
"""
import argparse, csv, json, pathlib, re, time, urllib.parse, urllib.request, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

SEARCH = "https://search.maven.org/solrsearch/select"
REPO = "https://repo.maven.apache.org/maven2"
UA = {"User-Agent": "vffinder-repro/0.1 (student project)"}
# Ban CHUA on dinh: qualifier dung rieng (sau . - _ hoac dau chuoi), vd 7.0.0.M2, 1.0-beta1, 2.0.0-SNAPSHOT.
# (Khong khop 'RELEASE', 'Final', 'java7'... - ban cu khop nham vi chuoi 'ea' nam trong 'RELEASE'.)
UNSTABLE = re.compile(r"(?:^|[.\-_])(?:alpha|beta|rc|cr|m\d+|milestone|snapshot|ea|dev|preview|b\d+)(?=[.\-_\d]|$)", re.I)
MAX_VERSIONS_PER_ARTIFACT = 3


def http_get(url, binary=False, retries=3, timeout=30):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as e:
            last = e
            if getattr(e, "code", None) == 404:
                return None
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"GET that bai {url}: {last}")


# ---------------- phien ban ----------------
def nums_of(v):
    m = re.match(r"\d+(?:\.\d+)*", v)
    return [int(x) for x in m.group(0).split(".")] if m else [0]

def is_stable(v):
    return not UNSTABLE.search(v)

def vkey(v):
    return (nums_of(v), 0 if not is_stable(v) else 1, v)

def major(v):
    return nums_of(v)[0]

def norm(v):
    n = nums_of(v)
    while len(n) > 1 and n[-1] == 0:
        n.pop()
    return tuple(n)

def find_match(av, v):
    """Tim phien ban on dinh trong 'av' tuong duong v (1.0.1 ~ 1.0.1.RELEASE ; 2.4 ~ 2.4.0)."""
    c = [x for x in av if is_stable(x) and norm(x) == norm(v)]
    if not c:
        return None
    return v if v in c else min(c, key=lambda x: (len(x), x))

VER = r"\d+(?:\.\d+)+(?:[.\-]?[A-Za-z]+\d*)?"
VP = r"v?(" + VER + ")"          # cho phep tien to 'v' (v2.10.0)
_FIXED = [
    r"(?:before|prior to|earlier than)\s+(?:versions?\s+)?" + VP,
    r"<(?!=)\s*" + VP,
    r"(?:fixed|patched|resolved|addressed|corrected)\s+in\s+(?:[A-Za-z][\w.\-]*\s+){0,4}?" + VP,
    r"(?:upgrade|update)\s+to\s+(?:versions?\s+)?" + VP,
]
_LAST = [
    r"(?:through|up to(?: and including)?|<=)\s*(?:versions?\s+)?" + VP,
    r"(?:" + VER + r")\s*(?:to|-|\u2013)\s*" + VP,                 # khoang X to Y, X-Y  -> lay Y
    VP + r"\s+(?:and|or)\s+(?:earlier|prior|older|below)",
]

def parse_all(text):
    def grab(pats):
        out = []
        for p in pats:
            out += [m.group(1).rstrip(".") for m in re.finditer(p, text, re.I)]
        return list(dict.fromkeys(out))
    fixed, last = grab(_FIXED), grab(_LAST)
    # Moi phien ban xuat hien SAU cac tu 'fixed/patched/resolved/addressed/upgrade/update' deu la moc DA SUA
    # (vd 'fixed in kubernetes-client-4.13.2 kubernetes-client-5.0.2'), khong duoc coi la ban bi anh huong.
    kw = re.search(r"\b(?:fixed|patched|resolved|addressed|corrected|upgrade|update)\b", text, re.I)
    head, tail = (text[:kw.start()], text[kw.end():]) if kw else (text, "")
    for m in re.finditer(VER, tail):
        v = m.group(0).rstrip(".")
        if v not in fixed:
            fixed.append(v)
    mentioned = list(dict.fromkeys(m.group(0).rstrip(".") for m in re.finditer(VER, head)))
    return fixed, last, mentioned

def parse_bounds(text):            # giu ten cu cho tuong thich
    f, l, _ = parse_all(text)
    return f, l

def candidate_versions(available, fixed, last, mentioned=()):
    av = sorted(set(available), key=vkey)
    out = []
    for b in sorted(fixed, key=vkey, reverse=True):
        prev = [v for v in av if is_stable(v) and vkey(v) < vkey(b) and major(v) == major(b)]
        if prev:
            out.append((prev[-1], f"truoc moc sua {b}"))
    for b in sorted(last, key=vkey, reverse=True):
        mt = find_match(av, b)
        if mt:
            out.append((mt, f"moc cuoi bi anh huong {b}"))
        else:
            prev = [v for v in av if is_stable(v) and vkey(v) < vkey(b) and major(v) == major(b)]
            if prev:
                out.append((prev[-1], f"gan moc cuoi {b}"))
    if not fixed and not last:                      # du phong: mo ta chi nhac cac ban cu the
        for b in sorted(mentioned, key=vkey, reverse=True):
            mt = find_match(av, b)
            if mt:
                out.append((mt, f"phien ban duoc nhac trong mo ta ({b})"))
    seen, res = set(), []
    for v, why in out:
        if v not in seen:
            seen.add(v); res.append((v, why))
    return res


# ---------------- Maven ----------------
def search_artifacts(fqcn, cache):
    if fqcn in cache:
        return cache[fqcn]
    q = urllib.parse.urlencode({"q": f'fc:"{fqcn}"', "rows": 200, "wt": "json"})
    raw = http_get(f"{SEARCH}?{q}", timeout=60, retries=4)
    resp = json.loads(raw)["response"] if raw else {"numFound": 0, "docs": []}
    agg = {}
    for d in resp["docs"]:
        k = (d["g"], d["a"]); agg[k] = agg.get(k, 0) + 1
    arts = sorted(([g, a, n] for (g, a), n in agg.items()), key=lambda x: x[2], reverse=True)
    cache[fqcn] = (resp["numFound"], arts)
    time.sleep(0.5)
    return cache[fqcn]

def list_versions(g, a, cache):
    k = f"{g}:{a}"
    if k in cache:
        return cache[k]
    xml = http_get(f"{REPO}/{g.replace('.', '/')}/{a}/maven-metadata.xml")
    vs = [e.text for e in ET.fromstring(xml).iter("version") if e.text] if xml else []
    cache[k] = vs
    time.sleep(0.15)
    return vs

def jar_urls(g, a, v):
    base = f"{REPO}/{g.replace('.', '/')}/{a}/{v}/{a}-{v}"
    return base + ".jar", base + "-sources.jar"

def class_in_jar(path, fqcn):
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
        return (fqcn.replace(".", "/") + ".class") in names
    except Exception:
        return False


def try_artifact(g, art, fq, cve_desc, hint_version, jars, download, vcache):
    vs = list_versions(g, art, vcache)
    if not vs:
        return None, "khong_co_artifact"
    fixed, last, mentioned = parse_all(cve_desc)
    cands = candidate_versions(vs, fixed, last, mentioned)
    if hint_version:
        cands = [(hint_version, "thu cong")] + [c for c in cands if c[0] != hint_version]
    if not cands:
        return None, "khong_chon_duoc_phien_ban"
    tried = 0
    for v, why in cands:
        if tried >= MAX_VERSIONS_PER_ARTIFACT:
            break
        ju, su = jar_urls(g, art, v)
        jp = jars / f"{g}__{art}-{v}.jar"
        if download:
            if not jp.exists():
                data = http_get(ju, binary=True)
                if data is None:
                    continue
                jars.mkdir(parents=True, exist_ok=True); jp.write_bytes(data)
            tried += 1
            if not class_in_jar(jp, fq):
                continue
            sok = False
            sp = jars / f"{g}__{art}-{v}-sources.jar"
            if sp.exists():
                sok = True
            else:
                sd = http_get(su, binary=True)
                if sd is not None:
                    sp.write_bytes(sd); sok = True
            return dict(version=v, reason=why, jar_ok=True, src_ok=sok, class_in_jar=True,
                        others="|".join(x[0] for x in cands)), "ok"
        else:
            return dict(version=v, reason=why, jar_ok="chua_kiem_tra", src_ok="chua_kiem_tra",
                        class_in_jar="chua_kiem_tra", others="|".join(x[0] for x in cands)), "ok_chua_xac_minh"
    return None, "class_khong_co_trong_jar"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--download", action="store_true", help="tai jar va XAC MINH class (khuyen dung)")
    ap.add_argument("--use-search", action="store_true", help="tra search.maven.org khi ung vien thu cong khong ton tai")
    ap.add_argument("--jars", default=None)
    ap.add_argument("--only", default=None, help="chi chay cac CVE nay (phan cach bang dau phay)")
    a = ap.parse_args()
    d = pathlib.Path(a.data)
    jars = pathlib.Path(a.jars) if a.jars else d.parent / "jars"
    desc = json.load(open(d / "cve_description.json", encoding="utf-8"))
    rows = list(csv.DictReader(open(d / "gav_hints.csv", encoding="utf-8")))
    if a.only:
        keep = set(a.only.split(","))
        rows = [r for r in rows if r["cve"] in keep]

    manual = {}
    mp = d / "gav_manual.csv"
    if mp.exists():
        for r in csv.DictReader(open(mp, encoding="utf-8")):
            manual.setdefault(r["fqcn"], []).append(r)

    cache_path = d / "maven_cache.json"
    cache = json.load(open(cache_path)) if cache_path.exists() else {"search": {}, "versions": {}}

    out = []
    for i, r in enumerate(rows, 1):
        cve, fq = r["cve"], r["fqcn"]
        rec = dict(cve=cve, fqcn=fq, method=r["method"], group="", artifact="", chosen_version="",
                   reason="", other_versions="", jar_ok="", src_ok="", class_in_jar="", status="", tried="")
        print(f"[{i}/{len(rows)}] {cve} {fq}", flush=True)
        if not fq:
            rec["status"] = "khong_co_FQCN"; out.append(rec); continue

        def run(cands):
            tried, final = [], None
            for g, art, hv in cands:
                try:
                    res, why = try_artifact(g, art, fq, desc.get(cve, ""), hv, jars, a.download, cache["versions"])
                except Exception as e:
                    res, why = None, f"loi:{str(e)[:50]}"
                tried.append(f"{g}:{art}={why}")
                if res:
                    final = (g, art, res, why); break
            return tried, final

        cands = [(m["group"], m["artifact"], m.get("version", "")) for m in manual.get(fq, [])]
        tried, final = run(cands) if cands else ([], None)
        all_missing = (not cands) or all(t.endswith("=khong_co_artifact") for t in tried)
        note_search = ""
        if not final and all_missing and a.use_search:
            try:
                nf, arts = search_artifacts(fq, cache["search"])
                if nf <= 200 and arts:
                    t2, final = run([(g, art, "") for g, art, _ in arts[:3] if (g, art) not in {(c[0], c[1]) for c in cands}])
                    tried += ["[search] " + x for x in t2]
                else:
                    note_search = f"search_mo_ho(numFound={nf})"
            except Exception as e:
                note_search = f"search_loi:{str(e)[:50]}"
        rec["tried"] = " ; ".join(tried)
        if final:
            g, art, res, why = final
            rec.update(group=g, artifact=art, chosen_version=res["version"], reason=res["reason"],
                       other_versions=res["others"], jar_ok=res["jar_ok"], src_ok=res["src_ok"],
                       class_in_jar=res["class_in_jar"], status=why)
        else:
            rec["status"] = note_search or ("can_dien_gav_manual" if not cands else "khong_xac_minh_duoc")
        out.append(rec)
        json.dump(cache, open(cache_path, "w"))

    with open(d / "gav_resolved.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    ok = [r for r in out if r["status"] == "ok"]
    print("\n=== TONG KET ===")
    print(f"VF: {len(out)} | xac minh OK (class co trong jar): {len(ok)} | co sources.jar: {sum(1 for r in ok if r['src_ok'] is True)}")
    print("Trang thai:", dict(Counter(r["status"].split(':')[0].split('(')[0] for r in out)))
    print(f"Da ghi {d/'gav_resolved.csv'}")

if __name__ == "__main__":
    main()
