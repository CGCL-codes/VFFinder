#!/usr/bin/env python3
"""Smoke test Giai doan 0. Chay: python check_env.py"""
import os, shutil, subprocess, sys, importlib

ok = True
def row(name, good, detail=""):
    global ok
    ok &= bool(good)
    print(f"[{'OK ' if good else 'FAIL'}] {name} {detail}")

row("Python 3.10", sys.version_info[:2] == (3, 10), sys.version.split()[0])
for m in ["google.genai", "nltk", "spacy", "stanfordcorenlp", "networkx",
          "scipy", "sklearn", "pandas", "tqdm", "numpy"]:
    try:
        importlib.import_module(m); row(f"import {m}", True)
    except Exception as e:
        row(f"import {m}", False, str(e))

try:
    import spacy; spacy.load("en_core_web_sm"); row("spacy en_core_web_sm", True)
except Exception as e:
    row("spacy en_core_web_sm", False, str(e))
try:
    from nltk.corpus import wordnet, stopwords
    wordnet.synsets("token"); stopwords.words("english"); row("nltk data", True)
except Exception as e:
    row("nltk data", False, str(e))

jv = shutil.which("java")
if jv:
    out = subprocess.run(["java", "-version"], capture_output=True, text=True).stderr.splitlines()[0]
    row("java", True, out)
else:
    row("java", False)
row("mvn", shutil.which("mvn") is not None)
row("VFF_ROOT", os.path.isdir(os.environ.get("VFF_ROOT", "")), os.environ.get("VFF_ROOT", ""))
cn = os.environ.get("CORENLP_DIR", "")
row("CORENLP_DIR", os.path.isdir(cn), cn)

# CoreNLP parse thu
try:
    from stanfordcorenlp import StanfordCoreNLP
    nlp = StanfordCoreNLP(cn, memory="2g")
    tree = nlp.parse("The service does not properly validate SAML tokens.")
    nlp.close(); row("CoreNLP parse", "(S" in tree)
except Exception as e:
    row("CoreNLP parse", False, str(e)[:120])

# Gemini + prompt that cua repo
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ask_GPT import query_chat_gpt
    tmpl = open(os.path.join(os.environ["VFF_ROOT"], "..", "Prompt", "RCAV_extract_prompt"), encoding="utf-8").read()
    desc = ("The SecurityTokenService (STS) in Apache CXF before 2.6.12 and 2.7.x before 2.7.9 "
            "does not properly validate SAML tokens when caching is enabled, which allows remote "
            "attackers to gain access via an invalid SAML token.")
    ans = query_chat_gpt(tmpl.format("(khong vi du)", desc))
    print("Gemini tra loi:", ans[:300])
    row("Gemini API", len(ans) > 0)
except Exception as e:
    row("Gemini API", False, str(e)[:160])

print("\nTONG KET:", "SAN SANG" if ok else "CON LOI - xem cac dong FAIL")
