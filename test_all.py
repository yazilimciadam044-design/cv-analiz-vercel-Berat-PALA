"""
Test Script — Tüm modülleri test eder
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

results = []

def test_ok(name):
    results.append(f"  ✅ {name}")

def test_fail(name, err):
    results.append(f"  ❌ {name}: {err}")

# ═══════════════════════════════════════════════
# 1. DATABASE TEST
# ═══════════════════════════════════════════════
print("\n🗃️  DATABASE TESTİ")
print("=" * 50)
try:
    from database import init_db, save_analysis, get_all_analyses, delete_analysis, get_statistics
    init_db()
    test_ok("init_db()")

    # Kayıt ekle
    row_id = save_analysis(
        isim="Test Kullanıcı",
        meslek_alani="Yazılım",
        cv_metni="Bu bir test CV metnidir. Python, SQL, Machine Learning bilgisi mevcut.",
        analiz_sonucu={
            "puan": 72,
            "guclu_yonler": ["Python", "SQL"],
            "eksikler": ["Docker", "AWS"],
            "onerilen_meslekler": ["Backend Developer", "Data Engineer"],
            "oneriler": ["Docker öğren", "AWS sertifikası al"]
        },
        puan=72,
        ai_model="Gemini",
    )
    test_ok(f"save_analysis() -> id={row_id}")

    # Tüm analizleri getir
    rows = get_all_analyses()
    assert len(rows) >= 1
    test_ok(f"get_all_analyses() -> {len(rows)} kayıt")

    # Arama
    search_results = get_all_analyses(search_query="Test Kullanıcı")
    assert len(search_results) >= 1
    test_ok(f"get_all_analyses(search) -> {len(search_results)} kayıt")

    # İstatistikler
    stats = get_statistics()
    assert stats["toplam"] >= 1
    test_ok(f"get_statistics() -> toplam={stats['toplam']}, ort_puan={stats['ort_puan']}")

    # Sil
    deleted = delete_analysis(row_id)
    assert deleted
    test_ok(f"delete_analysis({row_id}) -> silindi")

except Exception as e:
    test_fail("Database", str(e))

for r in results:
    print(r)
results.clear()

# ═══════════════════════════════════════════════
# 2. AI MODELS TEST (import + prompt oluşturma)
# ═══════════════════════════════════════════════
print("\n🤖 AI MODELS TESTİ")
print("=" * 50)
try:
    from ai_models import PROMPT_TEMPLATE, _clean_json_response, _validate_result
    test_ok("ai_models import")

    # Prompt şablonu test
    prompt = PROMPT_TEMPLATE.format(meslek_alani="Yazılım", cv_metni="Test CV")
    assert "Yazılım" in prompt
    assert "Test CV" in prompt
    test_ok("PROMPT_TEMPLATE.format()")

    # JSON temizleme
    raw = '```json\n{"puan": 80, "guclu_yonler": ["A"]}\n```'
    cleaned = _clean_json_response(raw)
    assert '"puan": 80' in cleaned
    test_ok("_clean_json_response(markdown)")

    raw2 = 'Burası yorum. {"puan":65} Biraz daha yorum.'
    cleaned2 = _clean_json_response(raw2)
    assert '"puan"' in cleaned2
    test_ok("_clean_json_response(inline)")

    # Doğrulama
    data = {"puan": 150, "guclu_yonler": ["X"]}
    validated = _validate_result(data)
    assert validated["puan"] == 100  # max 100
    assert "eksikler" in validated
    assert "onerilen_meslekler" in validated
    assert "oneriler" in validated
    test_ok("_validate_result()")

except Exception as e:
    test_fail("AI Models", str(e))

for r in results:
    print(r)
results.clear()

# ═══════════════════════════════════════════════
# 3. CV PARSER TEST
# ═══════════════════════════════════════════════
print("\n📄 CV PARSER TESTİ")
print("=" * 50)
try:
    from cv_parser import extract_text_from_pdf, extract_text_from_url, _clean_text, get_source_info
    test_ok("cv_parser import")

    # _clean_text testi
    messy = "Satır 1\n\n\n\n\nSatır 2\n\n\n\n\n\nSatır 3"
    clean = _clean_text(messy)
    assert "\n\n\n" not in clean
    test_ok("_clean_text()")

    # get_source_info
    pdf_info = get_source_info("pdf", filename="cv.pdf")
    assert "cv.pdf" in pdf_info
    url_info = get_source_info("url", url="https://github.com/user")
    assert "github.com" in url_info
    text_info = get_source_info("text")
    assert "Manuel" in text_info
    test_ok("get_source_info()")

    # PDF test - gerçek PDF oluştur
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, "Ad Soyad: Test Kisi", ln=True)
        pdf.cell(0, 10, "Deneyim: 5 yil yazilim gelistirme", ln=True)
        pdf.cell(0, 10, "Beceriler: Python, Java, SQL, Docker", ln=True)
        pdf.cell(0, 10, "Egitim: Bilgisayar Muhendisligi", ln=True)
        pdf.cell(0, 10, "Projeler: E-ticaret, CRM, API gelistirme", ln=True)
        pdf_bytes = bytes(pdf.output())

        extracted = extract_text_from_pdf(pdf_bytes)
        assert "Test Kisi" in extracted
        assert "Python" in extracted
        test_ok(f"extract_text_from_pdf() -> {len(extracted)} karakter")
    except ImportError:
        test_fail("PDF test", "fpdf2 yüklü değil")

except Exception as e:
    test_fail("CV Parser", str(e))

for r in results:
    print(r)
results.clear()

# ═══════════════════════════════════════════════
# 4. EXPORT UTILS TEST
# ═══════════════════════════════════════════════
print("\n📥 EXPORT UTILS TESTİ")
print("=" * 50)
try:
    from export_utils import generate_pdf, generate_docx, generate_csv

    sample_analiz = {
        "puan": 75,
        "guclu_yonler": ["Python", "SQL"],
        "eksikler": ["Docker"],
        "onerilen_meslekler": ["Backend Dev"],
        "oneriler": ["Docker ogren"]
    }

    # PDF
    pdf_data = generate_pdf("Test User", "Yazılım", sample_analiz)
    assert len(pdf_data) > 100
    assert pdf_data[:5] == b"%PDF-"
    test_ok(f"generate_pdf() -> {len(pdf_data)} bytes")

    # Word
    docx_data = generate_docx("Test User", "Yazılım", sample_analiz)
    assert len(docx_data) > 100
    test_ok(f"generate_docx() -> {len(docx_data)} bytes")

    # CSV
    sample_rows = [{
        "id": 1, "isim": "Test", "tarih": "2026-01-01",
        "meslek_alani": "Yazılım", "ai_model": "Gemini",
        "puan": 75, "analiz_sonucu": sample_analiz,
    }]
    csv_data = generate_csv(sample_rows)
    assert len(csv_data) > 50
    assert b"Test" in csv_data
    test_ok(f"generate_csv() -> {len(csv_data)} bytes")

except Exception as e:
    test_fail("Export Utils", str(e))

for r in results:
    print(r)
results.clear()

# ═══════════════════════════════════════════════
# 5. STREAMLIT APP SYNTAX CHECK
# ═══════════════════════════════════════════════
print("\n🖥️  APP.PY SYNTAX TESTİ")
print("=" * 50)
try:
    import ast
    with open("app.py", encoding="utf-8") as f:
        ast.parse(f.read())
    test_ok("app.py syntax valid")
except SyntaxError as e:
    test_fail("app.py syntax", str(e))

for r in results:
    print(r)
results.clear()

# ═══════════════════════════════════════════════
# 6. STREAMLIT HEALTH CHECK
# ═══════════════════════════════════════════════
print("\n🌐 STREAMLIT SERVER TESTİ")
print("=" * 50)
try:
    import requests
    resp = requests.get("http://localhost:8501/_stcore/health", timeout=5)
    if resp.text.strip() == "ok":
        test_ok("Streamlit health OK")
    else:
        test_fail("Streamlit health", resp.text)

    resp2 = requests.get("http://localhost:8501", timeout=5)
    if resp2.status_code == 200:
        test_ok(f"Main page loaded ({len(resp2.text)} chars)")
    else:
        test_fail("Main page", f"status={resp2.status_code}")
except Exception as e:
    test_fail("Server", str(e))

for r in results:
    print(r)
results.clear()

# ═══════════════════════════════════════════════
# SONUÇ
# ═══════════════════════════════════════════════
print("\n" + "=" * 50)
print("🏁 TÜM TESTLER TAMAMLANDI")
print("=" * 50)
