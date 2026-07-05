"""
AI Modülleri — Gemini ve Groq API entegrasyonları
"""

import json
import re
import os
from dotenv import load_dotenv
# Streamlit'i opsiyonel hale getirelim
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

# ─── Prompt Şablonu ──────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """
Sen bir üst düzey kariyer danışmanısın ve CV değerlendirme uzmanısın.
Aşağıdaki CV metnini '{meslek_alani}' alanı için titizlikle değerlendir.

YALNIZCA aşağıdaki alanları içeren GEÇERLİ bir JSON döndür (başka hiçbir metin ekleme):
{{
    "puan": <0 ile 100 arasında tam sayı>,
    "guclu_yonler": ["<güçlü yön 1>", "<güçlü yön 2>", ...],
    "eksikler": ["<eksik 1>", "<eksik 2>", ...],
    "onerilen_meslekler": ["<meslek 1>", "<meslek 2>", ...],
    "oneriler": ["<öneri 1>", "<öneri 2>", ...]
}}

Değerlendirme kriterleri:
- Teknik beceriler ve {meslek_alani} alanıyla uyumu
- İş deneyimi derinliği ve süresi
- Eğitim ve sertifikalar
- Proje ve başarılar
- İletişim ve sunum kalitesi

CV Metni:
---
{cv_metni}
---

SADECE JSON döndür. Açıklama, yorum veya markdown bloğu ekleme.
"""


def _clean_json_response(text: str) -> str:
    """Model yanıtından JSON bloğunu temizler."""
    # ```json ... ``` bloğunu çıkar
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    # Süslü parantez arasındaki ilk JSON'u bul
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0).strip()
    return text.strip()


def _validate_result(data: dict) -> dict:
    """Dönen JSON'un beklenen alanları içerdiğini doğrular."""
    required = ["puan", "guclu_yonler", "eksikler", "onerilen_meslekler", "oneriler"]
    for field in required:
        if field not in data:
            data[field] = [] if field != "puan" else 0
    # puan int olmalı
    try:
        data["puan"] = max(0, min(100, int(data["puan"])))
    except (ValueError, TypeError):
        data["puan"] = 0
    return data


# ─── Gemini ──────────────────────────────────────────────────────────────────

def analyze_with_gemini(cv_metni: str, meslek_alani: str, model_name: str = "gemini-3.5-flash") -> dict:
    """Gemini API kullanarak CV analizi yapar."""
    try:
        from google import genai
    except ImportError:
        raise ImportError("google-genai paketi yüklü değil. 'pip install google-genai' komutunu çalıştırın.")

    # API anahtarını önce ortam değişkenlerinden (Vercel/.env) alalım
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    # Eğer ortam değişkenlerinde yoksa ve Streamlit çalışıyorsa secrets'a bakalım
    if not api_key and st is not None:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Geçerli bir GEMINI_API_KEY bulunamadı. Lütfen .env dosyanızı veya ortam değişkenlerinizi kontrol edin.")

    client = genai.Client(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(
        meslek_alani=meslek_alani,
        cv_metni=cv_metni[:8000]  # Token limitini aşmamak için
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
        )
    )

    raw_text = response.text
    clean_text = _clean_json_response(raw_text)
    data = json.loads(clean_text)
    return _validate_result(data)


# ─── Groq ─────────────────────────────────────────────────────────────────────

def analyze_with_groq(cv_metni: str, meslek_alani: str, model_name: str = "openai/gpt-oss-120b") -> dict:
    """Groq API kullanarak CV analizi yapar."""
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("groq paketi yüklü değil. 'pip install groq' komutunu çalıştırın.")

    # API anahtarını önce ortam değişkenlerinden (Vercel/.env) alalım
    api_key = os.getenv("GROQ_API_KEY", "")
    
    # Eğer ortam değişkenlerinde yoksa ve Streamlit çalışıyorsa secrets'a bakalım
    if not api_key and st is not None:
        try:
            api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass

    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Geçerli bir GROQ_API_KEY bulunamadı. Lütfen .env dosyanızı veya ortam değişkenlerinizi kontrol edin.")

    client = Groq(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(
        meslek_alani=meslek_alani,
        cv_metni=cv_metni[:8000]
    )

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "Sen bir profesyonel CV analiz yapay zekâsısın. Her zaman geçerli JSON formatında yanıt ver."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    raw_text = completion.choices[0].message.content
    clean_text = _clean_json_response(raw_text)
    data = json.loads(clean_text)
    return _validate_result(data)


# ─── Ana analiz fonksiyonu ────────────────────────────────────────────────────

def analyze_cv(cv_metni: str, meslek_alani: str, ai_provider: str = "Gemini",
               gemini_model: str = "gemini-3.5-flash",
               groq_model: str = "openai/gpt-oss-120b") -> dict:
    """
    Seçilen AI sağlayıcısına göre CV analizi yapar.
    Dönen dict: puan, guclu_yonler, eksikler, onerilen_meslekler, oneriler
    """
    if not cv_metni or len(cv_metni.strip()) < 50:
        raise ValueError("CV metni çok kısa. Lütfen en az 50 karakter içeren bir CV girin.")

    if ai_provider == "Gemini":
        return analyze_with_gemini(cv_metni, meslek_alani, gemini_model)
    elif ai_provider == "Groq":
        return analyze_with_groq(cv_metni, meslek_alani, groq_model)
    else:
        raise ValueError(f"Bilinmeyen AI sağlayıcısı: {ai_provider}")
