"""Thay the VFFinder/LLMRequest/ask_GPT.py: goi Gemini thay vi OpenAI.
Giu NGUYEN ten ham query_chat_gpt(message)->str de cac cho goi cu khong phai sua.
Co cache tren dia: cung prompt + model thi khong goi API lai (tiet kiem tien, tai lap).
"""
import hashlib, json, os, pathlib, time
from google import genai
from google.genai import types

MODEL = os.environ.get("VFF_LLM_MODEL", "gemini-3.5-flash-lite")
CACHE_PATH = pathlib.Path(os.environ.get("VFF_LLM_CACHE", "llm_cache.jsonl"))
_client = None
_cache = None


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("Chua dat GEMINI_API_KEY")
        _client = genai.Client(api_key=key)
    return _client


def _load_cache():
    global _cache
    if _cache is None:
        _cache = {}
        if CACHE_PATH.exists():
            for line in CACHE_PATH.read_text(encoding="utf-8").splitlines():
                try:
                    d = json.loads(line)
                    _cache[d["k"]] = d["v"]
                except Exception:
                    pass
    return _cache


def _key(message):
    return hashlib.sha256((MODEL + "\x00" + message).encode("utf-8")).hexdigest()


def query_chat_gpt(message: str, max_retries: int = 5, base_delay: float = 2.0) -> str:
    cache = _load_cache()
    k = _key(message)
    if k in cache:
        return cache[k]
    cfg = types.GenerateContentConfig(
        temperature=0,
        system_instruction="You are a helpful assistant.",
    )
    last = None
    for i in range(max_retries):
        try:
            r = _get_client().models.generate_content(model=MODEL, contents=message, config=cfg)
            text = (r.text or "").strip()
            if not text:
                raise RuntimeError("Phan hoi rong")
            cache[k] = text
            with CACHE_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"k": k, "v": text}, ensure_ascii=False) + "\n")
            return text
        except Exception as e:           # 429, 5xx, mang...
            last = e
            time.sleep(base_delay * (2 ** i))
    raise RuntimeError(f"Gemini that bai sau {max_retries} lan: {last}")


def query_chat_gpt_api_key(message, api_key=None):   # tuong thich ham cu
    return query_chat_gpt(message)
