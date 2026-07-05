"""
CV Parser Modülü — PDF ve URL'den CV metni çıkarma
"""

import re
import io
import requests
from urllib.parse import urlparse

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ─── Yardımcı ─────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Metni temizler: fazla boşluklar, tekrarlayan satırlar."""
    lines = text.split("\n")
    cleaned = []
    prev = None
    for line in lines:
        line = line.strip()
        if line == prev and len(line) < 30:
            continue
        if line or (cleaned and cleaned[-1] != ""):
            cleaned.append(line)
        prev = line
    result = "\n".join(cleaned)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


# ─── PDF Ayrıştırma ───────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    PDF dosyasından metin çıkarır.
    pdfplumber kullanır (tablo ve kolon destekli).
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber paketi yüklü değil. 'pip install pdfplumber' çalıştırın.")

    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        if len(pdf.pages) == 0:
            raise ValueError("PDF dosyası boş veya okunamıyor.")

        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if page_text:
                text_parts.append(page_text.strip())

            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    clean_row = [cell.strip() if cell else "" for cell in row]
                    row_text = " | ".join(filter(None, clean_row))
                    if row_text.strip():
                        text_parts.append(row_text)

    full_text = "\n\n".join(text_parts).strip()

    if not full_text:
        raise ValueError(
            "PDF'den metin çıkarılamadı. Bu PDF taranmış bir görüntü (scanned) olabilir. "
            "Lütfen metni manuel olarak kopyalayıp yapıştırın."
        )

    return _clean_text(full_text)


# ─── URL Parserleri ───────────────────────────────────────────────────────────

def _parse_linkedin(soup, url: str) -> str:
    """LinkedIn profil sayfasından metin çıkarır."""
    texts = []

    name_tag = soup.find("h1") or soup.find(class_=re.compile(r"top-card.*name|profile.*name", re.I))
    if name_tag:
        texts.append(f"Ad Soyad: {name_tag.get_text(strip=True)}")

    headline = soup.find(class_=re.compile(r"headline|title", re.I))
    if headline:
        texts.append(f"Başlık: {headline.get_text(strip=True)}")

    about = soup.find(class_=re.compile(r"about|summary|description", re.I))
    if about:
        texts.append(f"Hakkında:\n{about.get_text(separator=chr(10), strip=True)}")

    exp_section = soup.find(id=re.compile(r"experience", re.I)) or soup.find(
        class_=re.compile(r"experience", re.I)
    )
    if exp_section:
        texts.append(f"Deneyim:\n{exp_section.get_text(separator=chr(10), strip=True)}")

    if not texts:
        return _parse_generic(soup, url)

    result = "\n\n".join(texts)
    if len(result.strip()) < 100:
        raise ValueError(
            "LinkedIn sayfasından yeterli içerik çekilemedi. "
            "LinkedIn oturum gerektirdiği için profil bilgilerini "
            "manuel olarak kopyalayıp 'Metin Yapıştır' sekmesini kullanın."
        )
    return _clean_text(result)


def _parse_github(soup, url: str) -> str:
    """GitHub profil veya README sayfasından metin çıkarır."""
    texts = []

    name = soup.find(class_=re.compile(r"p-name|vcard-fullname", re.I))
    if name:
        texts.append(f"Ad Soyad: {name.get_text(strip=True)}")

    bio = soup.find(class_=re.compile(r"p-note|user-profile-bio", re.I))
    if bio:
        texts.append(f"Biyografi: {bio.get_text(strip=True)}")

    repo_list = soup.find_all(class_=re.compile(r"repo", re.I), limit=10)
    if repo_list:
        repo_names = [r.get_text(strip=True) for r in repo_list if r.get_text(strip=True)]
        texts.append("Projeler/Repolar:\n" + "\n".join(repo_names[:10]))

    readme = soup.find(class_=re.compile(r"markdown-body|readme", re.I))
    if readme:
        texts.append("README:\n" + readme.get_text(separator="\n", strip=True))

    if not texts:
        return _parse_generic(soup, url)

    return _clean_text("\n\n".join(texts))


def _parse_generic(soup, url: str) -> str:
    """Genel web sayfasından anlamlı metni çıkarır."""
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "iframe", "noscript", "aside", "form", "button",
                     "meta", "link", "svg", "img"]):
        tag.decompose()

    main_content = (
        soup.find("article") or
        soup.find("main") or
        soup.find(class_=re.compile(r"resume|cv|content|profile|portfolio", re.I)) or
        soup.find("body")
    )

    if main_content:
        lines = []
        for el in main_content.find_all(["h1", "h2", "h3", "h4", "p", "li", "span", "div"]):
            txt = el.get_text(separator=" ", strip=True)
            if txt and len(txt) > 15:
                lines.append(txt)
        text = "\n".join(dict.fromkeys(lines))
    else:
        text = soup.get_text(separator="\n", strip=True)

    text = _clean_text(text)

    if len(text.strip()) < 100:
        raise ValueError(
            f"'{url}' adresinden yeterli metin içeriği çekilemedi. "
            "Sayfanın CV/profil içeriği olmayabilir veya JavaScript gerektiriyor olabilir."
        )

    return text


# ─── Ana URL Fonksiyonu ───────────────────────────────────────────────────────

def extract_text_from_url(url: str) -> str:
    """
    Verilen URL'den CV ile ilgili metin içeriği çıkarır.
    LinkedIn, GitHub ve genel web sayfalarını destekler.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("beautifulsoup4 paketi yüklü değil.")

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Bağlantı hatası: '{url}' adresine ulaşılamıyor.")
    except requests.exceptions.Timeout:
        raise ValueError("İstek zaman aşımına uğradı (15 saniye). Lütfen tekrar deneyin.")
    except requests.exceptions.HTTPError as e:
        status = getattr(resp, "status_code", 0)
        if status == 999:
            raise ValueError(
                "LinkedIn bu isteği engelledi (999 hatası). "
                "LinkedIn profil bilgilerini manuel olarak kopyalayıp 'Metin Yapıştır' sekmesini kullanın."
            )
        elif status == 403:
            raise ValueError(
                "Erişim engellendi (403). Site bot erişimine izin vermiyor. "
                "İçeriği manuel olarak kopyalayın."
            )
        raise ValueError(f"HTTP Hatası: {e}")
    except Exception as e:
        raise ValueError(f"URL bağlantı hatası: {e}")

    content_type = resp.headers.get("Content-Type", "")
    if "application/pdf" in content_type:
        return extract_text_from_pdf(resp.content)

    soup = BeautifulSoup(resp.text, "html.parser")

    if "linkedin.com" in domain:
        return _parse_linkedin(soup, url)
    elif "github.com" in domain:
        return _parse_github(soup, url)
    else:
        return _parse_generic(soup, url)


def get_source_info(source_type: str, url: str = "", filename: str = "") -> str:
    """Analiz için kaynak bilgi etiketi üretir."""
    if source_type == "pdf":
        return f"📄 PDF: {filename}"
    elif source_type == "url":
        parsed = urlparse(url)
        return f"🔗 URL: {parsed.netloc}"
    return "📝 Manuel Metin"
