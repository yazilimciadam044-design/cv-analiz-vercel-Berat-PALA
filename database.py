"""
Veritabanı Modülü — SQLite bağlantısı ve CRUD işlemleri
"""

import sqlite3
import json
from datetime import datetime
import os
import shutil
from pathlib import Path

# Vercel sunucusuz (serverless) ortamında sadece /tmp dizinine yazılabilir.
if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
    DB_PATH = Path("/tmp/cv_analiz.db")
    # Eğer /tmp altında DB yoksa ve proje kök dizininde hazır bir veritabanı varsa kopyala
    template_db = Path("cv_analiz.db")
    if template_db.exists() and not DB_PATH.exists():
        try:
            shutil.copy(template_db, DB_PATH)
        except Exception:
            pass
else:
    DB_PATH = Path("cv_analiz.db")


def init_db():
    """Veritabanı ve tabloyu oluşturur (yoksa)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analizler (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            isim        TEXT NOT NULL,
            tarih       TEXT NOT NULL,
            meslek_alani TEXT NOT NULL,
            cv_metni    TEXT NOT NULL,
            analiz_sonucu TEXT NOT NULL,
            puan        INTEGER NOT NULL,
            ai_model    TEXT DEFAULT 'Gemini'
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(isim: str, meslek_alani: str, cv_metni: str,
                  analiz_sonucu: dict, puan: int, ai_model: str = "Gemini") -> int:
    """Analiz sonucunu veritabanına kaydeder. Eklenen satırın id'sini döner."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tarih = datetime.now().isoformat(sep=" ", timespec="seconds")
    cursor.execute("""
        INSERT INTO analizler (isim, tarih, meslek_alani, cv_metni, analiz_sonucu, puan, ai_model)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (isim, tarih, meslek_alani, cv_metni, json.dumps(analiz_sonucu, ensure_ascii=False), puan, ai_model))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_analyses(search_query: str = "") -> list[dict]:
    """Tüm analizleri döner. Arama sorgusu varsa filtreler."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if search_query:
        cursor.execute("""
            SELECT * FROM analizler
            WHERE isim LIKE ? OR meslek_alani LIKE ? OR cv_metni LIKE ?
            ORDER BY id DESC
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("SELECT * FROM analizler ORDER BY id DESC")

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # JSON alanını Python nesnesine dönüştür
    for row in rows:
        try:
            row["analiz_sonucu"] = json.loads(row["analiz_sonucu"])
        except (json.JSONDecodeError, TypeError):
            row["analiz_sonucu"] = {}
    return rows


def delete_analysis(analysis_id: int) -> bool:
    """Belirtilen id'li analizi siler."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analizler WHERE id = ?", (analysis_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_statistics() -> dict:
    """Genel istatistikleri döner."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*)          AS toplam,
            AVG(puan)         AS ort_puan,
            MAX(puan)         AS max_puan,
            MIN(puan)         AS min_puan
        FROM analizler
    """)
    row = cursor.fetchone()
    cursor.execute("""
        SELECT meslek_alani, COUNT(*) AS sayi
        FROM analizler
        GROUP BY meslek_alani
        ORDER BY sayi DESC
    """)
    alan_dagilimi = {r[0]: r[1] for r in cursor.fetchall()}
    cursor.execute("""
        SELECT ai_model, COUNT(*) AS sayi
        FROM analizler
        GROUP BY ai_model
    """)
    model_dagilimi = {r[0]: r[1] for r in cursor.fetchall()}
    conn.close()
    return {
        "toplam": row[0] or 0,
        "ort_puan": round(row[1] or 0, 1),
        "max_puan": row[2] or 0,
        "min_puan": row[3] or 0,
        "alan_dagilimi": alan_dagilimi,
        "model_dagilimi": model_dagilimi,
    }


def get_analysis_by_id(analysis_id: int) -> dict | None:
    """Belirtilen id'li analiz kaydını döner."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analizler WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        row_dict = dict(row)
        try:
            row_dict["analiz_sonucu"] = json.loads(row_dict["analiz_sonucu"])
        except (json.JSONDecodeError, TypeError):
            row_dict["analiz_sonucu"] = {}
        return row_dict
    return None
