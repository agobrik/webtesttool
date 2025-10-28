# ⚡ WEBTESTOOL - HIZLI REFERANS KARTI

**Tüm detaylar için:** `SISTEM_KULLANIM_REHBERI.md` dosyasına bak

---

## 🚀 EN ÇOK KULLANILAN KOMUTLAR

### 1. Web Sitesi Tara

```bash
# Hızlı tarama
python main.py --url https://example.com --profile quick

# Güvenlik taraması
python main.py --url https://example.com --profile security

# Tam tarama
python main.py --url https://example.com --profile full
```

**Rapor nerede?** → `reports/<timestamp>/report.html`

---

### 2. Testleri Çalıştır

```bash
# Tüm testler
pytest tests/ -v

# Coverage raporu
pytest tests/unit/core/ --cov=core --cov-report=html
start htmlcov/index.html
```

---

### 3. Performans Analizi

```bash
# Hızlı analiz
python tools/profile_scan.py --url https://example.com --profile quick

# Detaylı analiz (kaydet)
python tools/profile_scan.py --url https://example.com --output my_report.json
```

---

### 4. Monitoring

```bash
# API başlat (Terminal 1)
python api/health.py

# Health check (Terminal 2)
curl http://localhost:8081/health

# Metrics
curl http://localhost:8081/metrics
```

---

## 📁 ÖNEMLİ DOSYALAR

| Dosya | Ne İçin? |
|-------|----------|
| `main.py` | Ana program - tarama yap |
| `config.yaml` | Ayarlar |
| `SISTEM_KULLANIM_REHBERI.md` | **MASTER GUIDE - HER ŞEY BURADA** |
| `HIZLI_REFERANS.md` | Bu dosya - hızlı komutlar |

---

## 📊 PROJE YAPISI

```
testool/
├── main.py                           # ← Buradan başla
├── config.yaml                       # ← Ayarları buradan yap
│
├── SISTEM_KULLANIM_REHBERI.md       # ← MASTER GUIDE (detaylı)
├── HIZLI_REFERANS.md                 # ← Bu dosya (özet)
│
├── tests/                            # Testler
├── tools/profile_scan.py             # Performans analizi
├── api/health.py                     # Monitoring API
│
├── core/                             # Kaynak kod
├── modules/                          # Test modülleri
├── reporters/                        # Rapor oluşturucular
└── reports/                          # Raporlar (otomatik oluşur)
```

---

## 🐛 SIKÇA YAŞANAN SORUNLAR

### Problem: ModuleNotFoundError: pytest
```bash
pip install -r requirements-test.txt
```

### Problem: ModuleNotFoundError: fastapi
```bash
pip install fastapi uvicorn psutil
```

### Problem: Playwright çalışmıyor
```bash
python -m playwright install
```

### Problem: Port 8081 kullanımda
```bash
# Farklı port kullan
uvicorn api.health:app --port 8082
```

---

## ⚙️ AYARLAR (config.yaml)

```yaml
# En önemli ayarlar

target:
  url: "https://example.com"
  max_pages: 50

crawler:
  enabled: true
  max_depth: 3

performance:
  parallel_workers: 5
  timeout: 30

output:
  format: ["html", "json"]
  directory: "reports"
```

---

## 💡 İPUÇLARI

✅ **İlk kez kullanıyorsan:** `SISTEM_KULLANIM_REHBERI.md` dosyasını oku

✅ **Hızlı başlamak istiyorsan:** Bu dosyadaki komutları kullan

✅ **Sorun yaşıyorsan:** Önce "SIKÇA YAŞANAN SORUNLAR" bölümüne bak

✅ **Detaylı bilgi istiyorsan:** `SISTEM_KULLANIM_REHBERI.md` → Her şey orada

---

**Versiyon:** 2.0 | **Tarih:** 23 Ekim 2025
