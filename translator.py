import json
import os
import re
import urllib.request
import urllib.error
import html
from dotenv import load_dotenv

load_dotenv()

SKIP_PATTERNS = [
    r"^https?://",        # URL
    r"^/\w+",             # Telegram command
    r"^@\w+$",            # mention only
    r"^[0-9\s\+\-\(\)]+$",  # số điện thoại / số thuần
]


def _should_skip(text: str) -> bool:
    if len(text.strip()) < 3:
        return True
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, text.strip()):
            return True
    return False


def _detect_language(text: str, api_key: str) -> str:
    url = f"https://translation.googleapis.com/language/translate/v2/detect?key={api_key}"
    data = json.dumps({"q": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["data"]["detections"][0][0]["language"]


def _translate_text(text: str, target_lang: str, api_key: str) -> str:
    url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
    lines = text.split("\n")
    to_translate = []
    indices = []
    
    for i, line in enumerate(lines):
        if not _should_skip(line):
            to_translate.append(line)
            indices.append(i)
            
    if not to_translate:
        return text

    data = json.dumps({"q": to_translate, "target": target_lang, "format": "text"}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        translations = result["data"]["translations"]
        translated_texts = [html.unescape(t["translatedText"]) for t in translations]
        
    result_lines = list(lines)
    for idx, translated_val in zip(indices, translated_texts):
        result_lines[idx] = translated_val
        
    return "\n".join(result_lines)


def translate_message(text: str) -> dict | None:
    """
    Detect ngôn ngữ và dịch bằng Google Translate API.
    Trả về dict kết quả hoặc None nếu không cần dịch.
    """
    if _should_skip(text):
        return None

    api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    if not api_key:
        print("[Translator] Missing GOOGLE_TRANSLATE_API_KEY in .env")
        return None

    try:
        detected_lang = _detect_language(text, api_key)
        
        target_langs = []
        # Fallback handling in case Google uses different language codes
        lang_code = detected_lang.lower()
        if lang_code.startswith("ko"):
            target_langs = ["vi"]
        elif lang_code.startswith("en"):
            target_langs = ["vi"]
        elif lang_code.startswith("vi"):
            target_langs = ["ko", "en"]
        else:
            return None
            
        translations = {}
        for lang in target_langs:
            translated = _translate_text(text, lang, api_key)
            translations[lang] = translated
            
        return {
            "detected_lang": "ko" if lang_code.startswith("ko") else ("en" if lang_code.startswith("en") else "vi"),
            "translations": translations,
        }

    except urllib.error.HTTPError as e:
        print(f"[Translator] API HTTP error: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
        return None
    except Exception as e:
        print(f"[Translator] Unexpected error: {e}")
        return None
