#!/usr/bin/env python3
"""Va candidate_versions trong 03_resolve_maven.py: uu tien ung vien CUNG NHANH major.minor voi moc.
Chay: python patch_tiers.py repro/phase1/03_resolve_maven.py
"""
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
NEW = '''def candidate_versions(available, fixed, last, mentioned=()):
    """Tier 0: cung nhanh major.minor voi moc, hoac moc la ban minor moi (x.y.0), hoac khop chinh xac ban cuoi bi anh huong.
       Tier 1: moc la ban VA (x.y.z, z>0) nhung KHONG co ban nao cung nhanh minor (du phong; vd 'before 2.5.1' khong nen nhay sang 2.3.37)."""
    av = sorted(set(available), key=vkey)
    mm = lambda v: tuple(nums_of(v)[:2])
    out = []                                   # (tier, moc, version, ly_do)
    for b in fixed:
        prev = [v for v in av if is_stable(v) and vkey(v) < vkey(b) and major(v) == major(b)]
        if prev:
            same = [v for v in prev if mm(v) == mm(b)]
            nb = nums_of(b)
            minor_release = len(nb) < 3 or nb[2] == 0      # moc x.y.0 / x.y: ban phat hanh minor moi -> ban truoc co the o minor cu
            if same:
                out.append((0, b, same[-1], f"truoc moc sua {b}"))
            elif minor_release:
                out.append((0, b, prev[-1], f"truoc moc sua {b}"))
            else:                                          # moc x.y.z (z>0) la ban VA trong nhanh x.y: ban truoc phai cung nhanh
                out.append((1, b, prev[-1], f"truoc moc sua {b} (khac nhanh minor)"))
    for b in last:
        mt = find_match(av, b)
        if mt:
            out.append((0, b, mt, f"moc cuoi bi anh huong {b}"))
        else:
            prev = [v for v in av if is_stable(v) and vkey(v) < vkey(b) and major(v) == major(b)]
            if prev:
                out.append((1, b, prev[-1], f"gan moc cuoi {b}"))
    out.sort(key=lambda x: vkey(x[1]), reverse=True)      # moc cao truoc
    out.sort(key=lambda x: x[0])                          # roi tier 0 truoc tier 1 (sap on dinh)
    res0 = [(v, why) for _, _, v, why in out]
    if not fixed and not last:                            # du phong: mo ta chi nhac cac ban cu the
        for b in sorted(mentioned, key=vkey, reverse=True):
            mt = find_match(av, b)
            if mt:
                res0.append((mt, f"phien ban duoc nhac trong mo ta ({b})"))
    seen, res = set(), []
    for v, why in res0:
        if v not in seen:
            seen.add(v); res.append((v, why))
    return res


'''
pat = re.compile(r"def candidate_versions\(.*?(?=# ---------------- Maven ----------------)", re.S)
if len(pat.findall(s)) != 1:
    sys.exit("KHONG tim thay dung 1 ham candidate_versions (file khac ban toi viet?)")
open(p, "w", encoding="utf-8").write(pat.sub(lambda m: NEW, s, count=1))
print("Da va candidate_versions trong", p)
