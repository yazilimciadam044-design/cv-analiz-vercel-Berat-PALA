import os
import sys
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Projenin kök dizinini Python yoluna ekleyelim ki veritabanı, AI ve parser modüllerini bulabilsin.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, save_analysis, get_all_analyses, delete_analysis, get_statistics, get_analysis_by_id
from ai_models import analyze_cv
from cv_parser import extract_text_from_pdf, extract_text_from_url, get_source_info
from export_utils import generate_pdf, generate_docx, generate_csv

# Veritabanını ilklendirelim
init_db()

app = FastAPI(title="AI CV Analyzer API")

# CORS İzinleri (Yerel testler ve Vercel CDN istekleri için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def redirect_root():
    # Vercel'in ana dizini API'ye yönlendirmesi ihtimaline karşı frontend'e yönlendir.
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/index.html")

@app.get("/api")
async def api_root():
    return {"status": "success", "message": "API basariyla calisiyor!"}

@app.get("/api/fetch-url")
async def api_fetch_url(url: str):
    try:
        text = extract_text_from_url(url)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/analyze")
async def api_analyze(
    isim: str = Form(...),
    meslek_alani: str = Form(...),
    ai_provider: str = Form(...),
    gemini_model: str = Form(...),
    groq_model: str = Form(...),
    cv_text: Optional[str] = Form(None),
    cv_url: Optional[str] = Form(None),
    cv_file: Optional[UploadFile] = File(None)
):
    text_content = ""
    source_tag = ""
    
    if cv_file:
        try:
            file_bytes = await cv_file.read()
            text_content = extract_text_from_pdf(file_bytes)
            source_tag = get_source_info("pdf", filename=cv_file.filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF okunamadı: {str(e)}")
            
    elif cv_url and cv_url.strip():
        try:
            text_content = extract_text_from_url(cv_url)
            source_tag = get_source_info("url", url=cv_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"URL okunamadı: {str(e)}")
            
    elif cv_text and cv_text.strip():
        text_content = cv_text
        source_tag = get_source_info("text")
        
    else:
        raise HTTPException(status_code=400, detail="Lütfen CV içeriği için metin girin, PDF yükleyin veya bir Link ekleyin.")
        
    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="CV içeriği çok kısa. En az 50 karakter olmalıdır.")
        
    try:
        # Analizi çalıştır
        analiz = analyze_cv(
            cv_metni=text_content,
            meslek_alani=meslek_alani,
            ai_provider=ai_provider,
            gemini_model=gemini_model,
            groq_model=groq_model
        )
        
        # Veritabanına kaydet
        row_id = save_analysis(
            isim=isim,
            meslek_alani=meslek_alani,
            cv_metni=text_content,
            analiz_sonucu=analiz,
            puan=analiz.get("puan", 0),
            ai_model=f"{ai_provider} ({gemini_model if ai_provider == 'Gemini' else groq_model}) | {source_tag}"
        )
        
        # Eklenen kaydı getirip dönelim
        saved_record = get_analysis_by_id(row_id)
        return saved_record
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz sırasında hata oluştu: {str(e)}")

@app.get("/api/history")
async def api_history(q: Optional[str] = None):
    try:
        rows = get_all_analyses(search_query=q or "")
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/delete/{id}")
async def api_delete(id: int):
    try:
        success = delete_analysis(id)
        if not success:
            raise HTTPException(status_code=404, detail="Kayıt bulunamadı.")
        return {"success": True, "message": "Analiz silindi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def api_statistics():
    try:
        stats = get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/pdf/{id}")
async def api_download_pdf(id: int):
    record = get_analysis_by_id(id)
    if not record:
        raise HTTPException(status_code=404, detail="Analiz kaydı bulunamadı.")
    try:
        pdf_bytes = generate_pdf(record["isim"], record["meslek_alani"], record["analiz_sonucu"])
        # Türkçe dosya adı için ascii dönüşüm
        safe_name = "".join(c for c in record["isim"] if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")
        filename = f"cv_rapor_{safe_name}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF oluşturulamadı: {str(e)}")

@app.get("/api/download/docx/{id}")
async def api_download_docx(id: int):
    record = get_analysis_by_id(id)
    if not record:
        raise HTTPException(status_code=404, detail="Analiz kaydı bulunamadı.")
    try:
        docx_bytes = generate_docx(record["isim"], record["meslek_alani"], record["analiz_sonucu"])
        safe_name = "".join(c for c in record["isim"] if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")
        filename = f"cv_rapor_{safe_name}.docx"
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word belgesi oluşturulamadı: {str(e)}")

@app.get("/api/download/csv")
async def api_download_csv():
    try:
        rows = get_all_analyses()
        csv_bytes = generate_csv(rows)
        filename = "cv_analiz_gecmis.csv"
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV oluşturulamadı: {str(e)}")
