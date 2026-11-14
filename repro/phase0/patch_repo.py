#!/usr/bin/env python3
"""Sua duong dan hard-code va ten thu muc sai trong repo VFFinder.
Dung:  python patch_repo.py --root $VFF_ROOT --corenlp $CORENLP_DIR [--dry-run]
"""
import argparse, pathlib

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True, help="thu muc VFFinder/VFFinder (chua resource/)")
ap.add_argument("--corenlp", required=True)
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
root = str(pathlib.Path(a.root).expanduser().resolve())
corenlp = str(pathlib.Path(a.corenlp).expanduser().resolve())

# THU TU QUAN TRONG: thay cac chuoi dai/cu the truoc
RULES = [
    ("ConceptExtractionRAG", "ConceptExtraction"),            # ten thu muc that
    ("//data/alan/stanford-corenlp-4.5.7", corenlp),
    ("//data/alan/VFlocation", root),
]
changed = 0
for p in pathlib.Path(root).rglob("*.py"):
    s = p.read_text(encoding="utf-8")
    t = s
    for old, new in RULES:
        t = t.replace(old, new)
    if t != s:
        changed += 1
        print(("[dry] " if a.dry_run else "[fix] ") + str(p.relative_to(root)))
        if not a.dry_run:
            p.write_text(t, encoding="utf-8")
print(f"{changed} file duoc sua")
