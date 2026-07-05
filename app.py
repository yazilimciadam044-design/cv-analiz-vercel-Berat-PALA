"""
AI Destekli CV Analiz ve Kariyer Danışmanı
Geliştirici: Necmeddin Tekik
"""

import json
import time
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from database import init_db, save_analysis, get_all_analyses, delete_analysis, get_statistics
from ai_models import analyze_cv
from export_utils import generate_pdf, generate_docx, generate_csv
from cv_parser import extract_text_from_pdf, extract_text_from_url, get_source_info

# ─── Sayfa Yapılandırması ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI CV Analiz Sistemi",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "AI Destekli CV Analiz ve Kariyer Danışmanı | Necmeddin Tekik",
    },
)

# ─── Logo (Sidebar'da gösterilecek) ──────────────────────────────────────────

# ─── CSS ──────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Dark theme override ── */
.stApp {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 40%, #065f46 100%);
    color: #f8fafc;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1300px !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #059669 100%);
    border: 1px solid rgba(52, 211, 153, 0.3);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(52,211,153,0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a7f3d0, #6ee7b7, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #d1fae5;
    margin: 0;
    font-weight: 400;
}

.hero-badge {
    display: inline-block;
    background: rgba(16,185,129,0.2);
    border: 1px solid rgba(16,185,129,0.5);
    color: #6ee7b7;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    text-transform: uppercase;
}

/* ── Cards ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(139,92,246,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* ── Score Ring ── */
.score-container {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(2,44,34,0.8), rgba(6,78,59,0.8));
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 20px;
    margin: 1rem 0;
}

.score-number {
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    margin: 0;
}

.score-label {
    font-size: 1rem;
    color: #94a3b8;
    margin-top: 0.5rem;
}

/* ── List Items ── */
.check-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.6rem 0.8rem;
    margin: 0.35rem 0;
    border-radius: 10px;
    background: rgba(16, 185, 129, 0.07);
    border: 1px solid rgba(16, 185, 129, 0.15);
    font-size: 0.92rem;
    color: #d1fae5;
    line-height: 1.4;
    transition: background 0.2s;
}

.check-item:hover { background: rgba(16, 185, 129, 0.12); }

.cross-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.6rem 0.8rem;
    margin: 0.35rem 0;
    border-radius: 10px;
    background: rgba(239, 68, 68, 0.07);
    border: 1px solid rgba(239, 68, 68, 0.15);
    font-size: 0.92rem;
    color: #fecaca;
    line-height: 1.4;
    transition: background 0.2s;
}

.cross-item:hover { background: rgba(239, 68, 68, 0.12); }

.tip-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.6rem 0.8rem;
    margin: 0.35rem 0;
    border-radius: 10px;
    background: rgba(251, 191, 36, 0.07);
    border: 1px solid rgba(251, 191, 36, 0.15);
    font-size: 0.92rem;
    color: #fef3c7;
    line-height: 1.4;
    transition: background 0.2s;
}

.tip-item:hover { background: rgba(251, 191, 36, 0.12); }

/* ── Badges ── */
.badge-container { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0; }

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(52,211,153,0.2));
    border: 1px solid rgba(16,185,129,0.4);
    color: #a7f3d0;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 1.2rem 0 0.6rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #022c22 0%, #064e3b 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] p {
    color: #a7f3d0 !important;
}

/* ── Inputs (Input & Textarea Fix) ── */
.stTextInput input, 
.stTextArea textarea, 
.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(6, 78, 59, 0.4) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(52, 211, 153, 0.3) !important;
    border-radius: 8px !important;
}

.stTextInput input:focus, 
.stTextArea textarea:focus, 
.stSelectbox div[data-baseweb="select"]:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 1px #10b981 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s ease !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.35) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Text area & inputs ── */
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.3s ease !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 0.3rem;
    border: 1px solid rgba(255,255,255,0.06);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8 !important;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
}

/* ── Progress ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #4f46e5) !important;
    border-radius: 10px !important;
}

/* ── Divider ── */
hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.5rem 0;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7c3aed !important; }

/* ── History card ── */
.history-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin: 0.7rem 0;
    transition: all 0.25s ease;
}

.history-card:hover {
    border-color: rgba(139,92,246,0.3);
    background: rgba(139,92,246,0.05);
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

.animate-in {
    animation: fadeInUp 0.5s ease forwards;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.6); }
</style>
""", unsafe_allow_html=True)


# ─── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def get_score_color(puan: int) -> str:
    if puan >= 75:
        return "#10b981"   # yeşil
    elif puan >= 50:
        return "#f59e0b"   # sarı
    else:
        return "#ef4444"   # kırmızı


def get_score_emoji(puan: int) -> str:
    if puan >= 85: return "🏆"
    if puan >= 70: return "⭐"
    if puan >= 50: return "👍"
    return "⚠️"


def render_score_gauge(puan: int):
    color = get_score_color(puan)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=puan,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "CV Puanı", "font": {"size": 16, "color": "#94a3b8", "family": "Inter"}},
        number={"font": {"size": 52, "color": color, "family": "Inter"}, "suffix": "/100"},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#374151",
                "tickfont": {"color": "#6b7280", "size": 10},
            },
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50],  "color": "rgba(239,68,68,0.1)"},
                {"range": [50, 75], "color": "rgba(245,158,11,0.1)"},
                {"range": [75, 100], "color": "rgba(16,185,129,0.1)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": puan,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
        height=260,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_analysis_results(analiz: dict, isim: str, meslek_alani: str, ai_model_label: str):
    puan = analiz.get("puan", 0)
    color = get_score_color(puan)
    emoji = get_score_emoji(puan)

    st.markdown('<div class="animate-in">', unsafe_allow_html=True)

    # ── Puan Göstergesi
    st.markdown("---")
    col_gauge, col_info = st.columns([1, 1.4], gap="large")

    with col_gauge:
        render_score_gauge(puan)

    with col_info:
        st.markdown(f"""
        <div class="glass-card" style="height:100%; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size:0.75rem; font-weight:600; letter-spacing:0.1em; color:#7c3aed; text-transform:uppercase; margin-bottom:0.5rem;">📋 Analiz Özeti</div>
            <div style="font-size:0.95rem; color:#94a3b8; margin-bottom:0.3rem;">👤 <b style="color:#e2e8f0">{isim}</b></div>
            <div style="font-size:0.95rem; color:#94a3b8; margin-bottom:0.3rem;">🏷️ Alan: <b style="color:#e2e8f0">{meslek_alani}</b></div>
            <div style="font-size:0.95rem; color:#94a3b8; margin-bottom:0.3rem;">🤖 Model: <b style="color:#e2e8f0">{ai_model_label}</b></div>
            <div style="font-size:0.95rem; color:#94a3b8; margin-bottom:1rem;">📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
            <div style="font-size:2rem; font-weight:800; color:{color};">{emoji} {puan}/100</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">
                {'Mükemmel CV!' if puan >= 85 else 'Çok İyi!' if puan >= 70 else 'Geliştirebilirsin' if puan >= 50 else 'Önemli eksikler var'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Detay Bölümleri
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="section-header">✅ Güçlü Yönler</div>', unsafe_allow_html=True)
        guclu = analiz.get("guclu_yonler", [])
        if guclu:
            for item in guclu:
                st.markdown(f'<div class="check-item"><span>✅</span><span>{item}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="check-item"><span>ℹ️</span><span>Güçlü yön bulunamadı.</span></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">❌ Eksikler</div>', unsafe_allow_html=True)
        eksikler = analiz.get("eksikler", [])
        if eksikler:
            for item in eksikler:
                st.markdown(f'<div class="cross-item"><span>❌</span><span>{item}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cross-item"><span>ℹ️</span><span>Eksik bulunamadı.</span></div>', unsafe_allow_html=True)

    # ── Önerilen Meslekler
    st.markdown('<div class="section-header">🎯 Önerilen Meslekler</div>', unsafe_allow_html=True)
    meslekler = analiz.get("onerilen_meslekler", [])
    badge_html = '<div class="badge-container">'
    for m in meslekler:
        badge_html += f'<span class="badge">🚀 {m}</span>'
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)

    # ── Kariyer Önerileri
    st.markdown('<div class="section-header">💡 Kariyer Önerileri</div>', unsafe_allow_html=True)
    for item in analiz.get("oneriler", []):
        st.markdown(f'<div class="tip-item"><span>💡</span><span>{item}</span></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Logoyu göster
        import os
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:1.5rem 0 1rem 0;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">🎯</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
        <div style="text-align:center; padding:0 0 1rem 0;">
            <div style="font-size:1.2rem; font-weight:700; color:#e2e8f0;">AI CV Analiz</div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:0.2rem;">Kariyer Danışmanı</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### ⚙️ Ayarlar")

        ai_provider = st.selectbox(
            "🤖 AI Modeli",
            options=["Gemini", "Groq"],
            key="sidebar_ai_provider",
            help="Analiz için kullanmak istediğiniz yapay zekâ modelini seçin.",
        )

        gemini_model = st.selectbox(
            "Gemini Versiyonu",
            options=["gemini-3.5-flash", "gemini-3.1-pro", "gemini-3.1-flash-lite"],
            index=0,
            key="sidebar_gemini_model",
            disabled=(ai_provider != "Gemini"),
        )

        groq_model = st.selectbox(
            "Groq Modeli",
            options=[
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "llama-3.3-70b-versatile",
                "qwen/qwen3.6-27b",
            ],
            index=0,
            key="sidebar_groq_model",
            disabled=(ai_provider != "Groq"),
        )

        st.markdown("---")

        # İstatistikler
        stats = get_statistics()
        st.markdown("### 📊 İstatistikler")
        st.metric("Toplam Analiz", stats["toplam"])
        if stats["toplam"] > 0:
            st.metric("Ortalama Puan", f"{stats['ort_puan']}/100")
            st.metric("En Yüksek Puan", f"{stats['max_puan']}/100")

        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.75rem; color:#475569; text-align:center; line-height:1.6;">
            <b>AI CV Analiz Sistemi</b><br>
            Necmeddin Tekik<br>
            Final Projesi 2026
        </div>
        """, unsafe_allow_html=True)

    return ai_provider, gemini_model, groq_model


# ─── TAB 1: Analiz ───────────────────────────────────────────────────────────

def _render_download_buttons(analiz: dict, isim: str, meslek_alani: str, key_suffix: str = ""):
    """PDF / Word / CSV indirme düğmelerini render eder."""
    st.markdown("---")
    st.markdown('<div class="section-header">📥 Raporu İndir</div>', unsafe_allow_html=True)
    col_p, col_d, col_c = st.columns(3, gap="medium")
    with col_p:
        try:
            pdf_bytes = generate_pdf(isim, meslek_alani, analiz)
            st.download_button(
                "📄 PDF İndir", data=pdf_bytes,
                file_name=f"cv_rapor_{isim.replace(' ', '_')}.pdf",
                mime="application/pdf", use_container_width=True,
                key=f"dl_pdf{key_suffix}",
            )
        except Exception as e:
            st.warning(f"PDF oluşturulamadı: {e}")
    with col_d:
        try:
            docx_bytes = generate_docx(isim, meslek_alani, analiz)
            st.download_button(
                "📝 Word İndir", data=docx_bytes,
                file_name=f"cv_rapor_{isim.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True, key=f"dl_word{key_suffix}",
            )
        except Exception as e:
            st.warning(f"Word oluşturulamadı: {e}")
    with col_c:
        try:
            csv_bytes = generate_csv(get_all_analyses())
            st.download_button(
                "📊 CSV İndir", data=csv_bytes,
                file_name="cv_analiz_gecmis.csv", mime="text/csv",
                use_container_width=True, key=f"dl_csv{key_suffix}",
            )
        except Exception as e:
            st.warning(f"CSV oluşturulamadı: {e}")


def _run_analysis(cv_text: str, isim: str, meslek_alani: str,
                  ai_provider: str, gemini_model: str, groq_model: str,
                  kaynak_etiketi: str = "", key_suffix: str = ""):
    """Ortak analiz + kaydet + göster akışı."""
    if not isim.strip():
        st.error("⚠️ Lütfen adınızı ve soyadınızı girin.")
        return
    if not cv_text or len(cv_text.strip()) < 50:
        st.error("⚠️ CV metni çok kısa. Lütfen en az 50 karakter içeren bir CV girin.")
        return

    ai_model_label = f"{ai_provider} ({gemini_model if ai_provider == 'Gemini' else groq_model})"
    if kaynak_etiketi:
        ai_model_label += f" | {kaynak_etiketi}"

    with st.spinner(f"🤖 {ai_provider} CV'nizi analiz ediyor... Lütfen bekleyin."):
        try:
            start_time = time.time()
            analiz = analyze_cv(
                cv_metni=cv_text, meslek_alani=meslek_alani,
                ai_provider=ai_provider, gemini_model=gemini_model, groq_model=groq_model,
            )
            elapsed = time.time() - start_time
            row_id = save_analysis(
                isim=isim, meslek_alani=meslek_alani, cv_metni=cv_text,
                analiz_sonucu=analiz, puan=analiz.get("puan", 0), ai_model=ai_provider,
            )
            st.success(f"✅ Analiz tamamlandı! ({elapsed:.1f} sn) — Kayıt ID: #{row_id}")
            render_analysis_results(analiz, isim, meslek_alani, ai_model_label)
            _render_download_buttons(analiz, isim, meslek_alani, key_suffix=key_suffix)
        except ValueError as e:
            st.error(f"⚠️ Girdi Hatası: {e}")
        except json.JSONDecodeError:
            st.error("❌ AI yanıtı ayrıştırılamadı. Lütfen tekrar deneyin.")
        except Exception as e:
            st.error(f"❌ Analiz başarısız: {e}")
            with st.expander("🔍 Hata Detayı"):
                st.exception(e)


def tab_analiz(ai_provider: str, gemini_model: str, groq_model: str):
    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">✨ Yapay Zekâ Destekli</div>
        <h1 class="hero-title">AI CV Analiz Sistemi</h1>
        <p class="hero-subtitle">Metin yapıştırın, PDF yükleyin veya link ekleyin — CV'nizi anında analiz edin.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Ortak alanlar (isim + meslek) ──────────────────────────────────────────
    col_isim, col_meslek = st.columns([1, 1], gap="medium")
    with col_isim:
        isim = st.text_input(
            "👤 Adınız Soyadınız",
            placeholder="Örn: Ahmet Yılmaz",
            key="input_isim",
        )
    with col_meslek:
        meslek_alani = st.selectbox(
            "🏷️ Hedef Meslek Alanı",
            options=["Yazılım", "Data Science", "Eğitim", "Finans", "Pazarlama", "Tasarım"],
            key="select_meslek",
        )

    st.markdown("")

    # ── Girdi yöntemi seçimi ───────────────────────────────────────────────────
    input_tabs = st.tabs(["📝 Metin Yapıştır", "📄 PDF Yükle", "🔗 Link Ekle"])

    # ════════════════════════════════════════════
    # SEKME 1 — Metin Yapıştır
    # ════════════════════════════════════════════
    with input_tabs[0]:
        col_form, col_tip = st.columns([2, 1], gap="large")
        with col_form:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            cv_text_raw = st.text_area(
                "📄 CV Metninizi Buraya Yapıştırın",
                height=280,
                placeholder="CV'nizi kopyalayıp buraya yapıştırın...\n\nÖrnek:\nAd Soyad: ...\nDeneyim: ...\nEğitim: ...\nBeceriler: ...",
                key="input_cv_text",
            )
            char_count = len(cv_text_raw) if cv_text_raw else 0
            if char_count > 0:
                clr = "#10b981" if char_count >= 200 else "#f59e0b"
                st.markdown(
                    f'<div style="font-size:0.78rem;color:{clr};text-align:right;margin-top:-0.5rem;">📝 {char_count:,} karakter</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns([2, 1])
            with col_b1:
                btn_text = st.button(f"🚀 CV'yi Analiz Et ({ai_provider})",
                                     use_container_width=True, key="btn_analyze_text")
            with col_b2:
                if st.button("🗑️ Temizle", use_container_width=True, key="btn_clear_text"):
                    st.session_state["input_cv_text"] = ""
                    st.rerun()

        with col_tip:
            st.markdown("""
            <div class="glass-card" style="height:100%;">
                <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">💬 Nasıl Kullanılır?</div>
                <div style="font-size:0.87rem;color:#94a3b8;line-height:1.9;">
                    <div><span style="color:#7c3aed;font-weight:600;">1.</span> Adınızı ve soyadınızı girin.</div>
                    <div><span style="color:#7c3aed;font-weight:600;">2.</span> Hedef meslek alanını seçin.</div>
                    <div><span style="color:#7c3aed;font-weight:600;">3.</span> CV metnini yapıştırın.</div>
                    <div><span style="color:#7c3aed;font-weight:600;">4.</span> Analiz Et butonuna basın.</div>
                </div>
                <div style="margin-top:1rem;padding:0.8rem;background:rgba(139,92,246,0.1);border-radius:10px;border:1px solid rgba(139,92,246,0.2);">
                    <div style="font-size:0.8rem;font-weight:600;color:#a78bfa;margin-bottom:0.3rem;">💡 İpucu</div>
                    <div style="font-size:0.8rem;color:#94a3b8;">En az 200 karakter CV metni daha isabetli sonuç üretir.</div>
                </div>
                <div style="margin-top:0.8rem;padding:0.8rem;background:rgba(16,185,129,0.07);border-radius:10px;border:1px solid rgba(16,185,129,0.15);">
                    <div style="font-size:0.8rem;font-weight:600;color:#34d399;margin-bottom:0.3rem;">🔐 Gizlilik</div>
                    <div style="font-size:0.8rem;color:#94a3b8;">Veriler yalnızca yerel veritabanınızda saklanır.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if btn_text:
            _run_analysis(cv_text_raw, isim, meslek_alani,
                          ai_provider, gemini_model, groq_model,
                          kaynak_etiketi="📝 Metin", key_suffix="_txt")

    # ════════════════════════════════════════════
    # SEKME 2 — PDF Yükle
    # ════════════════════════════════════════════
    with input_tabs[1]:
        col_pdf, col_tip2 = st.columns([2, 1], gap="large")
        with col_pdf:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:0.8rem;">
                CV'nizi <b style="color:#e2e8f0;">PDF formatında</b> yükleyin. Sistem metni otomatik olarak çıkaracak.
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "📎 PDF Dosyası Seçin",
                type=["pdf"],
                key="uploader_pdf",
                help="Maksimum 10 MB, yalnızca .pdf uzantılı dosyalar",
            )

            pdf_preview_text = ""
            if uploaded_file is not None:
                file_size_kb = len(uploaded_file.getvalue()) / 1024
                st.markdown(
                    f'<div style="font-size:0.8rem;color:#10b981;margin:0.5rem 0;">'
                    f'✅ Yüklendi: <b>{uploaded_file.name}</b> ({file_size_kb:.1f} KB)</div>',
                    unsafe_allow_html=True,
                )
                # PDF önizleme
                with st.spinner("PDF okunuyor..."):
                    try:
                        pdf_preview_text = extract_text_from_pdf(uploaded_file.getvalue())
                        preview_chars = len(pdf_preview_text)
                        clr2 = "#10b981" if preview_chars >= 200 else "#f59e0b"
                        st.markdown(
                            f'<div style="font-size:0.8rem;color:{clr2};">📝 {preview_chars:,} karakter çıkarıldı</div>',
                            unsafe_allow_html=True,
                        )
                        with st.expander("📖 Çıkarılan Metni Önizle", expanded=False):
                            st.text_area(
                                "PDF İçeriği",
                                value=pdf_preview_text[:3000] + ("..." if len(pdf_preview_text) > 3000 else ""),
                                height=180,
                                disabled=True,
                                key="pdf_preview_area",
                            )
                    except Exception as ex:
                        st.error(f"❌ PDF okunamadı: {ex}")

            st.markdown("</div>", unsafe_allow_html=True)

            btn_pdf = st.button(
                f"🚀 PDF CV'yi Analiz Et ({ai_provider})",
                use_container_width=True,
                key="btn_analyze_pdf",
                disabled=(uploaded_file is None or not pdf_preview_text),
            )

        with col_tip2:
            st.markdown("""
            <div class="glass-card" style="height:100%;">
                <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">📄 PDF Desteği</div>
                <div style="font-size:0.87rem;color:#94a3b8;line-height:1.9;">
                    <div>✅ Normal (dijital) PDF'ler</div>
                    <div>✅ Çok sayfalı belgeler</div>
                    <div>✅ Tablo içeren CV'ler</div>
                    <div>❌ Taranmış (görüntü) PDF'ler</div>
                    <div>❌ Şifreli PDF dosyaları</div>
                </div>
                <div style="margin-top:1rem;padding:0.8rem;background:rgba(251,191,36,0.08);border-radius:10px;border:1px solid rgba(251,191,36,0.2);">
                    <div style="font-size:0.8rem;font-weight:600;color:#fbbf24;margin-bottom:0.3rem;">⚠️ Dikkat</div>
                    <div style="font-size:0.8rem;color:#94a3b8;">Taranmış PDF'lerde metin tanıma (OCR) desteklenmez. Bu durumda metni manuel yapıştırın.</div>
                </div>
                <div style="margin-top:0.8rem;padding:0.8rem;background:rgba(16,185,129,0.07);border-radius:10px;border:1px solid rgba(16,185,129,0.15);">
                    <div style="font-size:0.8rem;font-weight:600;color:#34d399;margin-bottom:0.3rem;">💡 İpucu</div>
                    <div style="font-size:0.8rem;color:#94a3b8;">Word'den PDF'e dönüştürülmüş dosyalar en iyi sonucu verir.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if btn_pdf and uploaded_file and pdf_preview_text:
            _run_analysis(pdf_preview_text, isim, meslek_alani,
                          ai_provider, gemini_model, groq_model,
                          kaynak_etiketi=get_source_info("pdf", filename=uploaded_file.name),
                          key_suffix="_pdf")

    # ════════════════════════════════════════════
    # SEKME 3 — Link Ekle
    # ════════════════════════════════════════════
    with input_tabs[2]:
        col_url, col_tip3 = st.columns([2, 1], gap="large")
        with col_url:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:0.8rem;">
                CV'nizin bulunduğu web sayfasının URL'sini girin. GitHub profili, kişisel site veya PDF linki desteklenir.
            </div>
            """, unsafe_allow_html=True)

            cv_url = st.text_input(
                "🔗 CV URL'si",
                placeholder="https://github.com/kullanici-adi  veya  https://example.com/cv.pdf",
                key="input_cv_url",
            )

            url_text_preview = ""
            fetch_btn = st.button("🌐 İçeriği Getir", key="btn_fetch_url",
                                   disabled=not bool(cv_url and cv_url.strip()))

            if fetch_btn and cv_url:
                with st.spinner(f"🌐 '{cv_url}' adresi okunuyor..."):
                    try:
                        url_text_preview = extract_text_from_url(cv_url)
                        st.session_state["fetched_url_text"] = url_text_preview
                        st.session_state["fetched_url"] = cv_url
                        chars_fetched = len(url_text_preview)
                        clr3 = "#10b981" if chars_fetched >= 200 else "#f59e0b"
                        st.markdown(
                            f'<div style="font-size:0.8rem;color:{clr3};">📝 {chars_fetched:,} karakter çekildi</div>',
                            unsafe_allow_html=True,
                        )
                        with st.expander("📖 Çekilen Metni Önizle", expanded=False):
                            st.text_area(
                                "URL İçeriği",
                                value=url_text_preview[:3000] + ("..." if len(url_text_preview) > 3000 else ""),
                                height=180,
                                disabled=True,
                                key="url_preview_area",
                            )
                    except ValueError as ve:
                        st.error(f"⚠️ {ve}")
                        st.session_state.pop("fetched_url_text", None)
                    except Exception as ex:
                        st.error(f"❌ URL okunamadı: {ex}")
                        st.session_state.pop("fetched_url_text", None)

            # Session'dan önceki getirilen metni yükle
            if not url_text_preview and "fetched_url_text" in st.session_state:
                if st.session_state.get("fetched_url", "") == cv_url:
                    url_text_preview = st.session_state["fetched_url_text"]
                    st.markdown(
                        '<div style="font-size:0.8rem;color:#10b981;">✅ İçerik hazır — Analiz edebilirsiniz.</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("</div>", unsafe_allow_html=True)

            btn_url = st.button(
                f"🚀 URL CV'yi Analiz Et ({ai_provider})",
                use_container_width=True,
                key="btn_analyze_url",
                disabled=not bool(url_text_preview),
            )

        with col_tip3:
            st.markdown("""
            <div class="glass-card" style="height:100%;">
                <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:1rem;">🔗 Link Desteği</div>
                <div style="font-size:0.87rem;color:#94a3b8;line-height:1.9;">
                    <div>✅ GitHub profil sayfaları</div>
                    <div>✅ Kişisel CV/portföy siteleri</div>
                    <div>✅ Doğrudan PDF linkleri</div>
                    <div>✅ Genel web sayfaları</div>
                    <div>⚠️ LinkedIn (kısıtlı erişim)</div>
                </div>
                <div style="margin-top:1rem;padding:0.8rem;background:rgba(251,191,36,0.08);border-radius:10px;border:1px solid rgba(251,191,36,0.2);">
                    <div style="font-size:0.8rem;font-weight:600;color:#fbbf24;margin-bottom:0.3rem;">⚠️ LinkedIn Notu</div>
                    <div style="font-size:0.8rem;color:#94a3b8;">LinkedIn oturum gerektirdiğinden profil metni tam çekilemeyebilir. Metin sekmesini kullanmanız önerilir.</div>
                </div>
                <div style="margin-top:0.8rem;padding:0.8rem;background:rgba(16,185,129,0.07);border-radius:10px;border:1px solid rgba(16,185,129,0.15);">
                    <div style="font-size:0.8rem;font-weight:600;color:#34d399;margin-bottom:0.3rem;">💡 Önce Getir</div>
                    <div style="font-size:0.8rem;color:#94a3b8;">"İçeriği Getir" butonu ile önce metni çekip önizleyebilirsiniz.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if btn_url and url_text_preview:
            _run_analysis(url_text_preview, isim, meslek_alani,
                          ai_provider, gemini_model, groq_model,
                          kaynak_etiketi=get_source_info("url", url=cv_url or st.session_state.get("fetched_url", "")),
                          key_suffix="_url")


# ─── TAB 2: Geçmiş ────────────────────────────────────────────────────────────

def tab_gecmis():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="font-size:1.6rem; font-weight:700; color:#e2e8f0; margin:0;">📋 Analiz Geçmişi</h2>
        <p style="color:#64748b; font-size:0.9rem; margin:0.3rem 0 0 0;">Daha önce yapılan tüm CV analizleri</p>
    </div>
    """, unsafe_allow_html=True)

    # Arama
    col_s, col_refresh = st.columns([4, 1])
    with col_s:
        search_q = st.text_input(
            "🔍 Arama",
            placeholder="İsim, meslek alanı veya CV içeriğine göre arayın...",
            key="search_history",
            label_visibility="collapsed",
        )
    with col_refresh:
        if st.button("🔄 Yenile", use_container_width=True):
            st.rerun()

    rows = get_all_analyses(search_query=search_q)

    if not rows:
        st.markdown("""
        <div style="text-align:center; padding:4rem; color:#475569;">
            <div style="font-size:4rem;">📭</div>
            <div style="font-size:1.1rem; margin-top:1rem;">Henüz analiz geçmişi bulunmuyor.</div>
            <div style="font-size:0.85rem; margin-top:0.5rem;">Analiz sekmesinden CV'nizi analiz edin!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f'<div style="font-size:0.85rem; color:#64748b; margin-bottom:1rem;">🔎 {len(rows)} kayıt bulundu</div>', unsafe_allow_html=True)

    # CSV İndir
    try:
        csv_bytes = generate_csv(rows)
        st.download_button(
            "📊 Tüm Geçmişi CSV Olarak İndir",
            data=csv_bytes,
            file_name="cv_analiz_gecmis.csv",
            mime="text/csv",
            key="dl_history_csv",
        )
    except Exception:
        pass

    st.markdown("---")

    for row in rows:
        analiz = row.get("analiz_sonucu", {})
        puan = row.get("puan", 0)
        color = get_score_color(puan)
        emoji = get_score_emoji(puan)

        with st.expander(
            f"{emoji} {row['isim']} — {row['meslek_alani']} | Puan: {puan}/100 | {row['tarih']} | {row.get('ai_model','?')}",
            expanded=False,
        ):
            col_l, col_r = st.columns([1, 2])

            with col_l:
                st.markdown(f"""
                <div style="text-align:center; padding:1rem;">
                    <div style="font-size:3.5rem; font-weight:800; color:{color};">{puan}</div>
                    <div style="font-size:0.85rem; color:#94a3b8;">/ 100</div>
                    <div style="margin-top:0.5rem;">
                        <div style="background:rgba(255,255,255,0.05); border-radius:8px; height:8px; overflow:hidden;">
                            <div style="width:{puan}%; height:100%; background:{color}; border-radius:8px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**🤖 Model:** {row.get('ai_model','—')}")
                st.markdown(f"**📅 Tarih:** {row['tarih']}")
                st.markdown(f"**🏷️ Alan:** {row['meslek_alani']}")

            with col_r:
                inner1, inner2 = st.columns(2)
                with inner1:
                    st.markdown("**✅ Güçlü Yönler**")
                    for g in analiz.get("guclu_yonler", []):
                        st.markdown(f'<div class="check-item" style="margin:0.2rem 0;"><span>✅</span><span>{g}</span></div>', unsafe_allow_html=True)
                with inner2:
                    st.markdown("**❌ Eksikler**")
                    for e in analiz.get("eksikler", []):
                        st.markdown(f'<div class="cross-item" style="margin:0.2rem 0;"><span>❌</span><span>{e}</span></div>', unsafe_allow_html=True)

                st.markdown("**🎯 Önerilen Meslekler**")
                badges = "".join([f'<span class="badge">{m}</span>' for m in analiz.get("onerilen_meslekler", [])])
                st.markdown(f'<div class="badge-container">{badges}</div>', unsafe_allow_html=True)

                st.markdown("**💡 Öneriler**")
                for tip in analiz.get("oneriler", []):
                    st.markdown(f'<div class="tip-item" style="margin:0.2rem 0;"><span>💡</span><span>{tip}</span></div>', unsafe_allow_html=True)

                # Dışa aktarma
                col_dp, col_dw = st.columns(2)
                with col_dp:
                    try:
                        pdf_b = generate_pdf(row["isim"], row["meslek_alani"], analiz)
                        st.download_button("📄 PDF", pdf_b,
                                           file_name=f"cv_{row['id']}.pdf",
                                           mime="application/pdf",
                                           key=f"pdf_{row['id']}")
                    except Exception:
                        pass
                with col_dw:
                    try:
                        docx_b = generate_docx(row["isim"], row["meslek_alani"], analiz)
                        st.download_button("📝 Word", docx_b,
                                           file_name=f"cv_{row['id']}.docx",
                                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                           key=f"word_{row['id']}")
                    except Exception:
                        pass

            # Sil
            if st.button(f"🗑️ Bu Analizi Sil", key=f"del_{row['id']}"):
                if delete_analysis(row["id"]):
                    st.success("Analiz silindi.")
                    time.sleep(0.5)
                    st.rerun()


# ─── TAB 3: İstatistikler ─────────────────────────────────────────────────────

def tab_istatistikler():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="font-size:1.6rem; font-weight:700; color:#e2e8f0; margin:0;">📊 İstatistikler ve Analizler</h2>
        <p style="color:#64748b; font-size:0.9rem; margin:0.3rem 0 0 0;">Genel kullanım metrikleri ve trend grafikleri</p>
    </div>
    """, unsafe_allow_html=True)

    stats = get_statistics()

    if stats["toplam"] == 0:
        st.info("📭 Henüz istatistik yok. Analiz sekmesinden CV analizi yapın.")
        return

    # Metrikler
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Toplam Analiz", stats["toplam"])
    col2.metric("📈 Ortalama Puan", f"{stats['ort_puan']}/100")
    col3.metric("🏆 En Yüksek", f"{stats['max_puan']}/100")
    col4.metric("⚠️ En Düşük", f"{stats['min_puan']}/100")

    st.markdown("---")

    rows = get_all_analyses()
    if not rows:
        return

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # Meslek alanı dağılımı
        if stats["alan_dagilimi"]:
            fig_alan = px.pie(
                names=list(stats["alan_dagilimi"].keys()),
                values=list(stats["alan_dagilimi"].values()),
                title="Meslek Alanı Dağılımı",
                color_discrete_sequence=px.colors.sequential.Plasma,
                hole=0.45,
            )
            fig_alan.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#e2e8f0", "family": "Inter"},
                title_font={"size": 15, "color": "#94a3b8"},
                showlegend=True,
                legend=dict(font=dict(color="#94a3b8")),
                margin=dict(l=10, r=10, t=50, b=10),
                height=300,
            )
            st.plotly_chart(fig_alan, use_container_width=True, config={"displayModeBar": False})

    with col_g2:
        # AI Model dağılımı
        if stats["model_dagilimi"]:
            fig_model = px.bar(
                x=list(stats["model_dagilimi"].keys()),
                y=list(stats["model_dagilimi"].values()),
                title="AI Model Kullanımı",
                color=list(stats["model_dagilimi"].values()),
                color_continuous_scale="Plasma",
                labels={"x": "Model", "y": "Kullanım Sayısı"},
            )
            fig_model.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#e2e8f0", "family": "Inter"},
                title_font={"size": 15, "color": "#94a3b8"},
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=50, b=10),
                height=300,
                xaxis=dict(color="#94a3b8"),
                yaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
            )
            st.plotly_chart(fig_model, use_container_width=True, config={"displayModeBar": False})

    # Puan dağılımı
    puanlar = [r["puan"] for r in rows]
    isimler = [f"{r['isim']} ({r['meslek_alani']})" for r in rows]
    tarihler = [r["tarih"] for r in rows]

    fig_hist = px.histogram(
        x=puanlar,
        nbins=10,
        title="Puan Dağılımı",
        labels={"x": "Puan", "y": "Frekans"},
        color_discrete_sequence=["#7c3aed"],
    )
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0", "family": "Inter"},
        title_font={"size": 15, "color": "#94a3b8"},
        margin=dict(l=10, r=10, t=50, b=10),
        height=280,
        xaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    # Puan trendi
    if len(rows) >= 2:
        df_trend = pd.DataFrame({
            "Sıra": list(range(1, len(rows) + 1)),
            "Puan": puanlar[::-1],
            "Bilgi": [f"{r['isim']} — {r['tarih']}" for r in rows[::-1]],
        })
        fig_trend = px.line(
            df_trend, x="Sıra", y="Puan",
            title="Puan Trendi (Zamana Göre)",
            markers=True,
            hover_data=["Bilgi"],
            color_discrete_sequence=["#a78bfa"],
        )
        fig_trend.add_hline(y=stats["ort_puan"], line_dash="dash",
                             line_color="#f59e0b",
                             annotation_text=f"Ortalama: {stats['ort_puan']}",
                             annotation_font_color="#f59e0b")
        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e2e8f0", "family": "Inter"},
            title_font={"size": 15, "color": "#94a3b8"},
            margin=dict(l=10, r=10, t=50, b=10),
            height=280,
            xaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.05)", range=[0, 105]),
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})


# ─── Ana Uygulama ─────────────────────────────────────────────────────────────

def main():
    init_db()

    ai_provider, gemini_model, groq_model = render_sidebar()

    tab1, tab2, tab3 = st.tabs([
        "🚀 CV Analiz",
        "📋 Geçmiş Analizler",
        "📊 İstatistikler",
    ])

    with tab1:
        tab_analiz(ai_provider, gemini_model, groq_model)

    with tab2:
        tab_gecmis()

    with tab3:
        tab_istatistikler()


if __name__ == "__main__":
    main()
