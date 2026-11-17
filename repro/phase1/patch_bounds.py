#!/usr/bin/env python3
"""Va ham parse_bounds trong 03_resolve_maven.py: nhan them
  - 'before version X', 'fixed/patched/resolved in (version) X'   -> moc da sua
  - 'X to Y' (khoang phien ban)                                   -> ban cuoi bi anh huong = Y
Chay: python patch_bounds.py repro/phase1/03_resolve_maven.py
"""
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
NEW = '''def parse_bounds(text):
    VER = r"\\d+(?:\\.\\d+)+(?:[.\\-]?[A-Za-z]+\\d*)?"
    fixed = [m.group(1).rstrip(".") for m in re.finditer(
        r"(?:before|prior to|earlier than)\\s+(?:versions?\\s+)?(" + VER + ")", text, re.I)]
    fixed += [m.group(1).rstrip(".") for m in re.finditer(
        r"(?:fixed|patched|resolved|addressed|corrected)\\s+in\\s+(?:versions?\\s+|release\\s+)?(" + VER + ")", text, re.I)]
    last = [m.group(1).rstrip(".") for m in re.finditer(
        r"(?:through|up to(?: and including)?|<=)\\s+(?:versions?\\s+)?(" + VER + ")", text, re.I)]
    last += [m.group(1).rstrip(".") for m in re.finditer(
        r"(?:" + VER + r")\\s+to\\s+(" + VER + ")", text, re.I)]
    return list(dict.fromkeys(fixed)), list(dict.fromkeys(last))
'''
pat = re.compile(r"def parse_bounds\(text\):.*?return list\(dict\.fromkeys\(fixed\)\), list\(dict\.fromkeys\(last\)\)\n", re.S)
if not pat.search(s):
    sys.exit("KHONG tim thay ham parse_bounds de va (file khac ban toi viet?)")
s2 = pat.sub(lambda m: NEW, s, count=1)
open(p, "w", encoding="utf-8").write(s2)
print("Da va parse_bounds trong", p)
