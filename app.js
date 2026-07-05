document.addEventListener("DOMContentLoaded", () => {
    
    // ─── DOM Elemanları ───
    const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
    const tabPanes = document.querySelectorAll(".main-content .tab-pane");
    
    const aiProvider = document.getElementById("ai-provider");
    const geminiGroup = document.getElementById("gemini-group");
    const groqGroup = document.getElementById("groq-group");
    const geminiModel = document.getElementById("gemini-model");
    const groqModel = document.getElementById("groq-model");
    
    const inputTabBtns = document.querySelectorAll(".input-tab-btn");
    const inputPanes = document.querySelectorAll(".input-pane");
    const cvTextInput = document.getElementById("cv-text-input");
    const charCounter = document.getElementById("char-counter");
    
    const pdfDropzone = document.getElementById("pdf-dropzone");
    const cvFileInput = document.getElementById("cv-file-input");
    const pdfFileInfo = document.getElementById("pdf-file-info");
    const selectedFileName = document.getElementById("selected-file-name");
    const selectedFileSize = document.getElementById("selected-file-size");
    const clearFileBtn = document.getElementById("clear-file-btn");
    
    const cvUrlInput = document.getElementById("cv-url-input");
    const userNameInput = document.getElementById("user-name");
    const jobAreaSelect = document.getElementById("job-area");
    
    const analyzeBtn = document.getElementById("analyze-btn");
    const clearBtn = document.getElementById("clear-btn");
    const formError = document.getElementById("form-error");
    const loadingSpinner = document.getElementById("loading-spinner");
    const analysisResultContainer = document.getElementById("analysis-result-container");
    
    // Sonuç DOM Elemanları
    const scoreGauge = document.getElementById("score-gauge");
    const scoreText = document.getElementById("score-text");
    const resultName = document.getElementById("result-name");
    const resultArea = document.getElementById("result-area");
    const resultModel = document.getElementById("result-model");
    const resultDate = document.getElementById("result-date");
    const resultEval = document.getElementById("result-eval");
    const listGuclu = document.getElementById("list-guclu");
    const listEksik = document.getElementById("list-eksik");
    const containerMeslekler = document.getElementById("container-meslekler");
    const listOneriler = document.getElementById("list-oneriler");
    const downloadPdfBtn = document.getElementById("download-pdf-btn");
    const downloadWordBtn = document.getElementById("download-word-btn");
    
    // Geçmiş DOM Elemanları
    const historySearchInput = document.getElementById("history-search");
    const refreshHistoryBtn = document.getElementById("refresh-history-btn");
    const historyAccordion = document.getElementById("history-accordion");
    const historyCount = document.getElementById("history-count");
    
    // İstatistikler DOM Elemanları
    const statTotal = document.getElementById("stat-total");
    const statAvg = document.getElementById("stat-avg");
    const statMax = document.getElementById("stat-max");
    const statMin = document.getElementById("stat-min");
    const miniTotal = document.getElementById("mini-total");
    const miniAvg = document.getElementById("mini-avg");
    
    // ─── Global State ───
    let currentTab = "tab-analiz";
    let currentInputMode = "text"; // text, pdf, url
    let uploadedFile = null;
    let chartObjects = {}; // Chart nesnelerini tutmak için (tekrar çizimlerde çakışmayı önlemek için)

    // API Base URL
    const API_BASE = ""; // Vercel üzerinde bağıl yollar çalışır. (/api/...)

    // ─── 1. TAB YÖNETİMİ ───
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetTab = item.getAttribute("data-tab");
            
            navItems.forEach(nav => nav.classList.remove("active"));
            item.classList.add("active");
            
            tabPanes.forEach(pane => {
                pane.classList.remove("active");
                if (pane.id === targetTab) {
                    pane.classList.add("active");
                }
            });
            
            currentTab = targetTab;
            
            // Sekmeye göre yükleme yapalım
            if (currentTab === "tab-gecmis") {
                loadHistory();
            } else if (currentTab === "tab-istatistikler") {
                loadStatistics();
            }
        });
    });
    
    // Giriş Modu Alt Sekmeleri
    inputTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const mode = btn.getAttribute("data-input-mode");
            
            inputTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            inputPanes.forEach(pane => {
                pane.classList.remove("active");
                if (pane.id === `input-mode-${mode}`) {
                    pane.classList.add("active");
                }
            });
            
            currentInputMode = mode;
            hideError();
        });
    });
    
    // ─── 2. AYARLAR YÖNETİMİ ───
    aiProvider.addEventListener("change", () => {
        if (aiProvider.value === "Gemini") {
            geminiGroup.classList.remove("hidden");
            groqGroup.classList.add("hidden");
        } else {
            geminiGroup.classList.add("hidden");
            groqGroup.classList.remove("hidden");
        }
    });
    
    // ─── 3. METİN GİRİŞ KARAKTER SAYACI ───
    cvTextInput.addEventListener("input", () => {
        const count = cvTextInput.value.length;
        charCounter.textContent = `📝 ${count.toLocaleString("tr-TR")} karakter`;
        if (count > 0) {
            charCounter.style.color = count >= 200 ? "#10b981" : "#f59e0b";
        } else {
            charCounter.style.color = "#94a3b8";
        }
    });
    
    // ─── 4. PDF SÜRÜKLE BIRAK YÖNETİMİ ───
    // Tıklama ile dosya seçimi
    pdfDropzone.addEventListener("click", (e) => {
        // Eğer temizleme butonuna tıklanmadıysa
        if (!e.target.classList.contains("clear-file-btn") && !e.target.closest("#clear-file-btn")) {
            cvFileInput.click();
        }
    });
    
    cvFileInput.addEventListener("change", () => {
        if (cvFileInput.files.length > 0) {
            handleFileSelection(cvFileInput.files[0]);
        }
    });
    
    // Sürükle bırak olayları
    ["dragenter", "dragover"].forEach(eventName => {
        pdfDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            pdfDropzone.classList.add("dragover");
        }, false);
    });
    
    ["dragleave", "drop"].forEach(eventName => {
        pdfDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            pdfDropzone.classList.remove("dragover");
        }, false);
    });
    
    pdfDropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
    
    function handleFileSelection(file) {
        if (file.type !== "application/pdf") {
            showError("⚠️ Sadece PDF dosyaları desteklenmektedir.");
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showError("⚠️ Dosya boyutu 10 MB limitini aşamaz.");
            return;
        }
        
        uploadedFile = file;
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
        
        // UI güncelle
        pdfDropzone.querySelector(".dropzone-content").classList.add("hidden");
        pdfFileInfo.classList.remove("hidden");
        hideError();
    }
    
    // Dosya temizleme
    clearFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        resetFileSelection();
    });
    
    function resetFileSelection() {
        uploadedFile = null;
        cvFileInput.value = "";
        pdfDropzone.querySelector(".dropzone-content").classList.remove("hidden");
        pdfFileInfo.classList.add("hidden");
    }
    
    // ─── 5. HATA VE BİLDİRİM YÖNETİMİ ───
    function showError(msg) {
        formError.textContent = msg;
        formError.classList.remove("hidden");
        formError.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    
    function hideError() {
        formError.textContent = "";
        formError.classList.add("hidden");
    }
    
    // ─── 6. TEMİZLE BUTONU ───
    clearBtn.addEventListener("click", () => {
        userNameInput.value = "";
        cvTextInput.value = "";
        charCounter.textContent = "📝 0 karakter";
        charCounter.style.color = "#94a3b8";
        cvUrlInput.value = "";
        resetFileSelection();
        hideError();
        analysisResultContainer.classList.add("hidden");
    });
    
    // ─── 7. CV ANALİZ ETME (API ÇAĞRISI) ───
    analyzeBtn.addEventListener("click", async () => {
        hideError();
        
        const isim = userNameInput.value.trim();
        const meslekAlani = jobAreaSelect.value;
        const provider = aiProvider.value;
        const model = provider === "Gemini" ? geminiModel.value : groqModel.value;
        
        // Validasyonlar
        if (!isim) {
            showError("⚠️ Lütfen adınızı ve soyadınızı girin.");
            return;
        }
        
        const formData = new FormData();
        formData.append("isim", isim);
        formData.append("meslek_alani", meslekAlani);
        formData.append("ai_provider", provider);
        formData.append("gemini_model", geminiModel.value);
        formData.append("groq_model", groqModel.value);
        
        if (currentInputMode === "text") {
            const rawText = cvTextInput.value.trim();
            if (!rawText || rawText.length < 50) {
                showError("⚠️ CV metni çok kısa. Lütfen en az 50 karakter içeren bir CV metni girin.");
                return;
            }
            formData.append("cv_text", rawText);
            
        } else if (currentInputMode === "pdf") {
            if (!uploadedFile) {
                showError("⚠️ Lütfen analiz edilmesini istediğiniz bir PDF dosyasını seçin.");
                return;
            }
            formData.append("cv_file", uploadedFile);
            
        } else if (currentInputMode === "url") {
            const urlVal = cvUrlInput.value.trim();
            if (!urlVal) {
                showError("⚠️ Lütfen geçerli bir CV veya profil linki girin.");
                return;
            }
            formData.append("cv_url", urlVal);
        }
        
        // Spinner'ı göster
        loadingSpinner.classList.remove("hidden");
        analysisResultContainer.classList.add("hidden");
        analyzeBtn.disabled = true;
        
        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || "Analiz sırasında bir hata oluştu.");
            }
            
            // Başarılı Sonuç
            renderAnalysisResult(result);
            updateMiniStats(); // Mini widget'ı güncelle
            
        } catch (err) {
            showError(`❌ Hata: ${err.message}`);
        } finally {
            loadingSpinner.classList.add("hidden");
            analyzeBtn.disabled = false;
        }
    });
    
    // ─── 8. ANALİZ SONUCUNU EKRANA ÇİZME ───
    function renderAnalysisResult(record) {
        const analiz = record.analiz_sonucu;
        const puan = record.puan;
        
        resultName.textContent = record.isim;
        resultArea.textContent = record.meslek_alani;
        resultModel.textContent = record.ai_model || "Gemini";
        
        // Tarih formatlama
        try {
            const dateObj = new Date(record.tarih);
            resultDate.textContent = dateObj.toLocaleString("tr-TR");
        } catch(e) {
            resultDate.textContent = record.tarih;
        }
        
        // Puan Tag'i ve Emoji
        let emoji = "⚠️";
        let evalText = "Önemli eksikler var";
        let gaugeColor = "#ef4444";
        
        if (puan >= 85) {
            emoji = "🏆";
            evalText = "Mükemmel CV!";
            gaugeColor = "#10b981";
        } else if (puan >= 70) {
            emoji = "⭐";
            evalText = "Çok İyi!";
            gaugeColor = "#10b981";
        } else if (puan >= 50) {
            emoji = "👍";
            evalText = "Geliştirilebilir";
            gaugeColor = "#f59e0b";
        }
        
        resultEval.textContent = `${emoji} ${evalText}`;
        resultEval.style.color = gaugeColor;
        resultEval.style.background = `${gaugeColor}15`;
        
        // Gauge dairesini çizme (283 = Çevre uzunluğu)
        scoreText.textContent = puan;
        scoreText.style.fill = gaugeColor;
        scoreGauge.style.stroke = gaugeColor;
        const offset = 283 - (283 * puan) / 100;
        scoreGauge.style.strokeDashoffset = offset;
        
        // Güçlü Yönleri Listele
        listGuclu.innerHTML = "";
        const guclu = analiz.guclu_yonler || [];
        if (guclu.length > 0) {
            guclu.forEach(item => {
                const div = document.createElement("div");
                div.className = "check-item";
                div.innerHTML = `<span>✅</span><span>${escapeHtml(item)}</span>`;
                listGuclu.appendChild(div);
            });
        } else {
            listGuclu.innerHTML = '<div class="check-item"><span>ℹ️</span><span>Güçlü yön bulunamadı.</span></div>';
        }
        
        // Eksikleri Listele
        listEksik.innerHTML = "";
        const eksik = analiz.eksikler || [];
        if (eksik.length > 0) {
            eksik.forEach(item => {
                const div = document.createElement("div");
                div.className = "cross-item";
                div.innerHTML = `<span>❌</span><span>${escapeHtml(item)}</span>`;
                listEksik.appendChild(div);
            });
        } else {
            listEksik.innerHTML = '<div class="cross-item"><span>ℹ️</span><span>Eksik bulunamadı.</span></div>';
        }
        
        // Önerilen Meslekler
        containerMeslekler.innerHTML = "";
        const meslekler = analiz.onerilen_meslekler || [];
        meslekler.forEach(m => {
            const span = document.createElement("span");
            span.className = "profession-badge";
            span.innerHTML = `🚀 ${escapeHtml(m)}`;
            containerMeslekler.appendChild(span);
        });
        
        // Öneriler
        listOneriler.innerHTML = "";
        const oneriler = analiz.oneriler || [];
        oneriler.forEach(o => {
            const div = document.createElement("div");
            div.className = "tip-item";
            div.innerHTML = `<span>💡</span><span>${escapeHtml(o)}</span>`;
            listOneriler.appendChild(div);
        });
        
        // İndirme Bağlantılarını Güncelle
        downloadPdfBtn.href = `/api/download/pdf/${record.id}`;
        downloadWordBtn.href = `/api/download/docx/${record.id}`;
        
        // Sonuç panelini aç ve kaydır
        analysisResultContainer.classList.remove("hidden");
        analysisResultContainer.scrollIntoView({ behavior: "smooth" });
    }
    
    // ─── 9. GEÇMİŞ ANALİZLER YÜKLEME ───
    async function loadHistory() {
        historyAccordion.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';
        
        const q = historySearchInput.value.trim();
        let url = "/api/history";
        if (q) {
            url += `?q=${encodeURIComponent(q)}`;
        }
        
        try {
            const res = await fetch(url);
            const data = await res.json();
            
            if (!res.ok) throw new Error("Geçmiş getirilemedi.");
            
            historyCount.textContent = `🔎 ${data.length} kayıt bulundu`;
            
            if (data.length === 0) {
                historyAccordion.innerHTML = `
                    <div class="no-records">
                        <div class="no-records-icon">📭</div>
                        <h3>Kayıt Bulunamadı</h3>
                        <p>Arama kriterinize uygun veya henüz yapılmış bir analiz bulunmuyor.</p>
                    </div>
                `;
                return;
            }
            
            historyAccordion.innerHTML = "";
            
            data.forEach(record => {
                const analiz = record.analiz_sonucu || {};
                const puan = record.puan;
                
                let emoji = "⚠️";
                let color = "#ef4444";
                if (puan >= 85) {
                    emoji = "🏆";
                    color = "#10b981";
                } else if (puan >= 70) {
                    emoji = "⭐";
                    color = "#10b981";
                } else if (puan >= 50) {
                    emoji = "👍";
                    color = "#f59e0b";
                }
                
                let formattedDate = record.tarih;
                try {
                    formattedDate = new Date(record.tarih).toLocaleString("tr-TR");
                } catch(e){}
                
                const item = document.createElement("div");
                item.className = "history-item";
                
                // Başlık Satırı (Kapatılabilir/Açılabilir)
                const header = document.createElement("div");
                header.className = "history-item-header";
                header.innerHTML = `
                    <div class="h-left">
                        <div class="h-score-badge" style="color: ${color}; border-color: ${color}40; background: ${color}10;">${puan}</div>
                        <div class="h-info">
                            <h4>${escapeHtml(record.isim)}</h4>
                            <span>🏷️ ${escapeHtml(record.meslek_alani)}</span>
                        </div>
                    </div>
                    <div class="h-meta-right">
                        <span class="h-date">${formattedDate}</span>
                        <span class="h-arrow">▼</span>
                    </div>
                `;
                
                // Detay Gövdesi
                const body = document.createElement("div");
                body.className = "history-item-body";
                
                const bodyContent = document.createElement("div");
                bodyContent.className = "h-body-content";
                
                // Güçlü yönler
                let gucluHtml = "";
                (analiz.guclu_yonler || []).forEach(g => {
                    gucluHtml += `<div class="check-item" style="margin: 0.2rem 0;"><span>✅</span><span>${escapeHtml(g)}</span></div>`;
                });
                if (!gucluHtml) gucluHtml = "<p class='text-dark'>Kayıt yok</p>";
                
                // Eksikler
                let eksikHtml = "";
                (analiz.eksikler || []).forEach(e => {
                    eksikHtml += `<div class="cross-item" style="margin: 0.2rem 0;"><span>❌</span><span>${escapeHtml(e)}</span></div>`;
                });
                if (!eksikHtml) eksikHtml = "<p class='text-dark'>Kayıt yok</p>";
                
                // Meslek badgeleri
                let badgeler = "";
                (analiz.onerilen_meslekler || []).forEach(m => {
                    badgeler += `<span class="profession-badge" style="margin: 0.2rem 0.2rem 0 0;">🚀 ${escapeHtml(m)}</span>`;
                });
                
                // Öneriler
                let onerilerHtml = "";
                (analiz.oneriler || []).forEach(o => {
                    onerilerHtml += `<div class="tip-item" style="margin: 0.2rem 0;"><span>💡</span><span>${escapeHtml(o)}</span></div>`;
                });
                
                bodyContent.innerHTML = `
                    <div class="h-body-meta">
                        <div>🤖 <b>Model:</b> ${escapeHtml(record.ai_model || "Gemini")}</div>
                        <div>📅 <b>Tarih:</b> ${formattedDate}</div>
                    </div>
                    
                    <div class="details-grid" style="margin-top: 0.5rem;">
                        <div>
                            <strong style="color: var(--text-light); font-size: 0.88rem; display: block; margin-bottom: 0.4rem;">✅ Güçlü Yönler</strong>
                            ${gucluHtml}
                        </div>
                        <div>
                            <strong style="color: var(--text-light); font-size: 0.88rem; display: block; margin-bottom: 0.4rem;">❌ Eksikler</strong>
                            ${eksikHtml}
                        </div>
                    </div>
                    
                    <div style="margin-top: 0.5rem;">
                        <strong style="color: var(--text-light); font-size: 0.88rem; display: block; margin-bottom: 0.4rem;">🎯 Önerilen Meslekler</strong>
                        <div class="badge-container">${badgeler}</div>
                    </div>
                    
                    <div style="margin-top: 0.5rem;">
                        <strong style="color: var(--text-light); font-size: 0.88rem; display: block; margin-bottom: 0.4rem;">💡 Öneriler</strong>
                        <div class="detail-list">${onerilerHtml}</div>
                    </div>
                    
                    <div class="download-section" style="margin-top: 0.5rem; display: flex; gap: 1rem; align-items: center; justify-content: space-between;">
                        <div class="download-buttons" style="flex-grow: 1;">
                            <a href="/api/download/pdf/${record.id}" class="btn-download pdf-btn" style="padding: 0.5rem 1rem; font-size: 0.85rem;" target="_blank">📄 PDF</a>
                            <a href="/api/download/docx/${record.id}" class="btn-download word-btn" style="padding: 0.5rem 1rem; font-size: 0.85rem;" target="_blank">📝 Word</a>
                        </div>
                        <button class="btn-delete-record" data-id="${record.id}">🗑️ Bu Analizi Sil</button>
                    </div>
                `;
                
                body.appendChild(bodyContent);
                item.appendChild(header);
                item.appendChild(body);
                historyAccordion.appendChild(item);
                
                // Akordeon Aç/Kapat
                header.addEventListener("click", () => {
                    const isOpen = item.classList.contains("open");
                    // Diğerlerini kapat
                    document.querySelectorAll(".history-item").forEach(i => i.classList.remove("open"));
                    if (!isOpen) {
                        item.classList.add("open");
                    }
                });
            });
            
            // Silme butonlarını bağlayalım
            document.querySelectorAll(".btn-delete-record").forEach(btn => {
                btn.addEventListener("click", async (e) => {
                    e.stopPropagation();
                    const id = btn.getAttribute("data-id");
                    if (confirm("Bu analizi geçmişten kalıcı olarak silmek istediğinize emin misiniz?")) {
                        try {
                            const res = await fetch(`/api/delete/${id}`, { method: "DELETE" });
                            if (res.ok) {
                                loadHistory();
                                updateMiniStats();
                            } else {
                                alert("Silme başarısız.");
                            }
                        } catch(err) {
                            alert("Hata oluştu.");
                        }
                    }
                });
            });
            
        } catch(err) {
            historyAccordion.innerHTML = `<div class="error-banner">Geçmiş yüklenirken hata oluştu: ${err.message}</div>`;
        }
    }
    
    // Arama ve yenileme tetikleyicileri
    historySearchInput.addEventListener("input", debounce(() => loadHistory(), 300));
    refreshHistoryBtn.addEventListener("click", () => loadHistory());
    
    // ─── 10. İSTATİSTİKLERİ YÜKLEME VE CHART.JS GRAFİKLERİ ───
    async function loadStatistics() {
        try {
            // İstatistik verisini API'den çek
            const resStats = await fetch("/api/statistics");
            const stats = await resStats.json();
            
            if (!resStats.ok) throw new Error("İstatistikler yüklenemedi.");
            
            // Metrik Kartları
            statTotal.textContent = stats.toplam;
            statAvg.textContent = `${stats.ort_puan}/100`;
            statMax.textContent = `${stats.max_puan}/100`;
            statMin.textContent = `${stats.min_puan}/100`;
            
            if (stats.toplam === 0) {
                return; // Çizilecek grafik yok
            }
            
            // Geçmiş verilerini de çekelim (trend ve histogram için gerekli)
            const resHistory = await fetch("/api/history");
            const historyData = await resHistory.json();
            
            // ── Grafik 1: Meslek Alanı Dağılımı (Doughnut) ──
            drawDoughnutChart(stats.alan_dagilimi);
            
            // ── Grafik 2: AI Model Kullanımı (Bar) ──
            drawBarChart(stats.model_dagilimi);
            
            // ── Grafik 3: Puan Dağılımı Frekansı (Bar/Histogram) ──
            drawHistogramChart(historyData);
            
            // ── Grafik 4: Puan Trendi (Line) ──
            drawTrendChart(historyData, stats.ort_puan);
            
        } catch (err) {
            console.error("İstatistik yükleme hatası:", err);
        }
    }
    
    function drawDoughnutChart(data) {
        const ctx = document.getElementById("chart-alan").getContext("2d");
        destroyChart("chart-alan");
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        chartObjects["chart-alan"] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#10b981', '#7c3aed', '#f59e0b', '#3b82f6', '#ec4899', '#f43f5e'
                    ],
                    borderWidth: 1,
                    borderColor: 'rgba(255,255,255,0.05)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Inter' } }
                    }
                }
            }
        });
    }
    
    function drawBarChart(data) {
        const ctx = document.getElementById("chart-model").getContext("2d");
        destroyChart("chart-model");
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        chartObjects["chart-model"] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Analiz Sayısı',
                    data: values,
                    backgroundColor: 'rgba(124, 58, 237, 0.7)',
                    borderColor: '#7c3aed',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { 
                        ticks: { color: '#94a3b8', stepSize: 1 }, 
                        grid: { color: 'rgba(255,255,255,0.05)' } 
                    }
                }
            }
        });
    }
    
    function drawHistogramChart(history) {
        const ctx = document.getElementById("chart-puan-dist").getContext("2d");
        destroyChart("chart-puan-dist");
        
        // Puan grupları (0-10, 11-20, ..., 91-100)
        const bins = Array(10).fill(0);
        const labels = ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"];
        
        history.forEach(r => {
            const p = r.puan;
            const index = Math.min(9, Math.floor(p / 10));
            bins[index]++;
        });
        
        chartObjects["chart-puan-dist"] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'CV Adedi',
                    data: bins,
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { 
                        ticks: { color: '#94a3b8', stepSize: 1 }, 
                        grid: { color: 'rgba(255,255,255,0.05)' } 
                    }
                }
            }
        });
    }
    
    function drawTrendChart(history, avgScore) {
        const ctx = document.getElementById("chart-puan-trend").getContext("2d");
        destroyChart("chart-puan-trend");
        
        // Eskiden yeniye sırala
        const sorted = [...history].reverse();
        const labels = sorted.map((_, i) => `${i + 1}. Analiz`);
        const scores = sorted.map(r => r.puan);
        
        chartObjects["chart-puan-trend"] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Puan',
                        data: scores,
                        borderColor: '#a78bfa',
                        backgroundColor: 'rgba(167, 139, 250, 0.1)',
                        borderWidth: 2,
                        tension: 0.2,
                        fill: true,
                        pointBackgroundColor: '#7c3aed',
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { 
                        min: 0,
                        max: 105,
                        ticks: { color: '#94a3b8' }, 
                        grid: { color: 'rgba(255,255,255,0.05)' } 
                    }
                }
            }
        });
    }
    
    function destroyChart(canvasId) {
        if (chartObjects[canvasId]) {
            chartObjects[canvasId].destroy();
            delete chartObjects[canvasId];
        }
    }
    
    // ─── 11. YARDIMCI FONKSİYONLAR (Mini İstatistikler, Debounce, EscapeHtml) ───
    async function updateMiniStats() {
        try {
            const res = await fetch("/api/statistics");
            if (res.ok) {
                const stats = await res.json();
                miniTotal.textContent = stats.toplam;
                miniAvg.textContent = `${stats.ort_puan}/100`;
            }
        } catch(e){}
    }
    
    // Uygulama yüklenirken mini istatistikleri çek
    updateMiniStats();
    
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    function escapeHtml(text) {
        if (!text) return "";
        return text
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
