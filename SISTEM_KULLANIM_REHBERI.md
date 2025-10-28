# 🎯 WEBTESTOOL - KOMPLE SİSTEM KULLANIM REHBERİ

**Son Güncelleme:** 23 Ekim 2025
**Durum:** Kullanıma Hazır

---

## 📑 İÇİNDEKİLER

1. [Hızlı Başlangıç](#-hizli-baslangic)
2. [Sistem Yapısı](#-sistem-yapisi)
3. [Temel Kullanım](#-temel-kullanim)
4. [Testler](#-testler)
5. [Performans Analizi](#-performans-analizi)
6. [Monitoring](#-monitoring)
7. [Gelişmiş Özellikler](#-gelismis-ozellikler)
8. [Sorun Giderme](#-sorun-giderme)

---

## ⚡ HIZLI BAŞLANGIÇ

### 1. Kurulum (İlk Kez)

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Test bağımlılıklarını yükle (opsiyonel)
pip install -r requirements-test.txt

# 3. Monitoring bağımlılıklarını yükle (opsiyonel)
pip install fastapi uvicorn psutil

# 4. Playwright kurulumu
python -m playwright install
```

### 2. İlk Tarama (30 saniye)

```bash
# Basit quick scan
python main.py --url https://example.com --profile quick

# Rapor oluşur: reports/<timestamp>/ klasöründe
```

### 3. Özellikleri Test Et (5 dakika)

```bash
# Testleri çalıştır
pytest tests/unit/core/test_config_comprehensive.py -v

# Monitoring API'yi başlat
python api/health.py

# Başka terminalde health check yap
curl http://localhost:8081/health
```

**✅ HAZIR! Sistem çalışıyor.**

---

## 📁 SİSTEM YAPISI

```
C:\Projects\testool\
│
├─── 🎯 ANA KULLANIM DOSYALARI
│    ├── main.py                          # Ana program - buradan başla
│    ├── config.yaml                      # Ayarlar dosyası
│    └── requirements.txt                 # Bağımlılıklar
│
├─── 📚 DÖKÜMANTASYON (SEN BURADA ŞİMDİ!)
│    ├── SISTEM_KULLANIM_REHBERI.md      # ← BU DOSYA (MASTER GUIDE)
│    ├── README.md                        # Proje tanıtımı
│    ├── ARCHITECTURE.md                  # Teknik mimari
│    │
│    ├── HIZLI_BASLANGIC_YENI_OZELLIKLER.md   # Yeni özellikleri öğren
│    ├── TAMAMLANAN_IYILESTIRMELER_2025.md    # Neler yapıldı
│    ├── gelecektebelki.md                     # Gelecek planlar
│    │
│    └── archive/                         # Eski raporlar (görmezden gel)
│         ├── SISTEM_IYILESTIRME_RAPORU_2025.md
│         └── ...
│
├─── 🧪 TESTLER
│    └── tests/
│         ├── unit/core/
│         │   ├── test_config_comprehensive.py    # Config testleri (30+)
│         │   └── test_engine_comprehensive.py    # Engine testleri (25+)
│         └── ...
│
├─── 🔧 ARAÇLAR
│    └── tools/
│         └── profile_scan.py             # Performans analizi aracı
│
├─── 📊 MONİTORİNG
│    ├── api/
│    │   └── health.py                    # Health & Metrics API
│    └── utils/
│        ├── health.py                    # Health check logic
│        └── metrics.py                   # Metrics collection
│
├─── 💻 KAYNAK KOD
│    ├── core/                            # Çekirdek sistem
│    │   ├── scanner.py                   # Web scanner
│    │   ├── engine.py                    # Test engine
│    │   └── config.py                    # Configuration
│    │
│    ├── modules/                         # Test modülleri
│    │   ├── security/                    # Güvenlik testleri
│    │   ├── performance/                 # Performans testleri
│    │   ├── seo/                         # SEO testleri
│    │   └── ...
│    │
│    ├── reporters/                       # Rapor oluşturucular
│    │   ├── html_reporter.py
│    │   └── json_reporter.py
│    │
│    └── utils/                           # Yardımcı araçlar
│
└─── 📄 RAPORLAR (Otomatik oluşur)
     └── reports/
          └── <timestamp>/
               ├── report.html              # HTML rapor
               └── results.json             # JSON sonuçlar
```

---

## 🎮 TEMEL KULLANIM

### Senaryo 1: Web Sitesi Tara

```bash
# Quick scan (hızlı)
python main.py --url https://example.com --profile quick

# Security scan (güvenlik odaklı)
python main.py --url https://example.com --profile security

# Full scan (kapsamlı)
python main.py --url https://example.com --profile full --max-pages 100
```

**Rapor Nerede?**
- `reports/<timestamp>/report.html` - Tarayıcıda aç
- `reports/<timestamp>/results.json` - JSON verisi

### Senaryo 2: Belirli Modüllerle Tara

```bash
# Sadece güvenlik testleri
python main.py \
    --url https://example.com \
    --modules security.xss security.sql_injection

# Sadece performans testleri
python main.py \
    --url https://example.com \
    --modules performance.page_speed performance.resource_size
```

### Senaryo 3: Ayarları Özelleştir

```bash
# config.yaml dosyasını düzenle
nano config.yaml

# Özel config ile çalıştır
python main.py --url https://example.com --config custom_config.yaml
```

**Önemli Ayarlar (config.yaml):**
```yaml
target:
  url: "https://example.com"
  max_pages: 50

crawler:
  enabled: true
  respect_robots: true
  max_depth: 3

performance:
  parallel_workers: 5
  timeout: 30

output:
  format: ["html", "json", "markdown"]
  directory: "reports"
```

---

## 🧪 TESTLER

### Test Nedir?

Test dosyaları, sistemin doğru çalıştığından emin olmak için yazılmış otomatik kontrollerdir.

### Testleri Çalıştır

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Sadece core testleri
pytest tests/unit/core/ -v

# Belirli bir test dosyası
pytest tests/unit/core/test_config_comprehensive.py -v

# Coverage raporu ile
pytest tests/unit/core/ --cov=core --cov-report=html
open htmlcov/index.html
```

### Test Coverage Nedir?

Kodun ne kadarının testlerle kontrol edildiğini gösterir.

**Coverage Raporu Görüntüle:**
```bash
# 1. Coverage testi çalıştır
pytest tests/unit/core/ --cov=core --cov-report=html

# 2. Raporu aç
# Windows:
start htmlcov/index.html

# Linux/Mac:
open htmlcov/index.html
```

### Mevcut Testler

| Test Dosyası | Ne Test Eder? | Test Sayısı |
|-------------|---------------|-------------|
| `test_config_comprehensive.py` | Configuration sistemi | 30+ |
| `test_engine_comprehensive.py` | Test engine | 25+ |

**Toplam Test Coverage:** ~65% (Core modules)

---

## ⚡ PERFORMANS ANALİZİ

### Performans Profiling Nedir?

Tarama sırasında hangi işlemlerin yavaş olduğunu, hangi fonksiyonların çok bellek kullandığını bulur.

### Profiling Nasıl Yapılır?

```bash
# 1. Basit profiling
python tools/profile_scan.py \
    --url https://example.com \
    --profile quick

# Çıktı:
# 🎯 Target: https://example.com
# ⏱️  Duration: 15.32s
# 💾 Peak Memory: 245.67 MB
# 🔥 Top Bottlenecks:
#   1. [HIGH] core.scanner._crawl_url - 8.234s
```

```bash
# 2. Detaylı profiling + kaydet
python tools/profile_scan.py \
    --url https://example.com \
    --pages 50 \
    --profile full \
    --output my_analysis.json

# Sonuç: reports/my_analysis.json
```

### Profiling Sonuçları Nasıl Okunur?

**Örnek Çıktı:**
```
🎯 Target: https://example.com
⏱️  Duration: 15.32s
💾 Peak Memory: 245.67 MB
📊 URLs Crawled: 5
🔥 Top Bottlenecks:
  1. [HIGH] core.scanner.WebScanner._crawl_url
     Time: 8.234s (5 calls)
     Avg: 1.647s per call
  2. [MEDIUM] modules.security.xss.check
     Time: 2.145s (10 calls)
```

**Açıklama:**
- **Duration**: Toplam süre
- **Peak Memory**: En yüksek bellek kullanımı
- **Bottlenecks**: Yavaş olan fonksiyonlar
- **[HIGH/MEDIUM/LOW]**: Önem derecesi

### Ne Zaman Kullanılır?

- Tarama çok yavaş ise
- Optimizasyon yapmadan önce baseline almak için
- Optimizasyondan sonra iyileşmeyi ölçmek için

---

## 📊 MONİTORİNG

### Monitoring Nedir?

Sistemin sağlık durumunu ve metriklerini gerçek zamanlı izleme.

### 1. Monitoring API'yi Başlat

```bash
# Terminal 1: API'yi başlat
python api/health.py

# Çıktı:
# INFO: Started server process
# INFO: Uvicorn running on http://0.0.0.0:8081
```

API çalışıyor: http://localhost:8081

### 2. Health Check (Sağlık Kontrolü)

```bash
# Başka terminal (Terminal 2):

# Genel sağlık durumu
curl http://localhost:8081/health

# Sonuç:
{
  "status": "healthy",
  "timestamp": "2025-10-23T10:30:00",
  "checks": {
    "database": true,
    "cache": true,
    "disk_space": true,
    "memory": true,
    "cpu": true
  },
  "uptime_seconds": 3600.5
}
```

### 3. Metrics (Metrikler)

```bash
# Prometheus formatı
curl http://localhost:8081/metrics

# JSON formatı
curl http://localhost:8081/metrics/json

# Sistem kaynakları
curl http://localhost:8081/stats/system

# Scan istatistikleri
curl http://localhost:8081/stats/scans
```

### 4. Mevcut Endpoint'ler

| Endpoint | Ne Yapar? | Kullanım |
|----------|-----------|----------|
| `/health` | Genel sağlık durumu | Production health check |
| `/health/live` | Kubernetes liveness | K8s deployment |
| `/health/ready` | Kubernetes readiness | K8s deployment |
| `/health/components` | Bileşen detayları | Debug için |
| `/metrics` | Prometheus metrics | Monitoring sistemleri |
| `/metrics/json` | JSON metrics | Dashboard'lar |
| `/stats/system` | CPU, RAM, Disk | Sistem izleme |
| `/stats/scans` | Scan istatistikleri | Uygulama metrikleri |
| `/version` | Versiyon bilgisi | Info |

### 5. Ne Zaman Kullanılır?

- **Production'da**: Sistemin çalışıp çalışmadığını izlemek için
- **Kubernetes'te**: Liveness/Readiness probe'lar için
- **Prometheus/Grafana ile**: Metrik toplama ve görselleştirme
- **Debug sırasında**: Sistem kaynaklarını kontrol etmek için

---

## 🚀 GELİŞMİŞ ÖZELLIKLER

### 1. Paralel Tarama

```bash
# 10 paralel worker ile tara
python main.py \
    --url https://example.com \
    --workers 10 \
    --max-pages 100
```

### 2. Rate Limiting

```yaml
# config.yaml
rate_limiting:
  enabled: true
  requests_per_second: 5
  burst: 10
```

### 3. Cache Kullanımı

```yaml
# config.yaml
cache:
  enabled: true
  ttl: 3600  # 1 saat
  max_size: 1000
```

### 4. Custom Modül Yazma

```python
# modules/custom/my_module.py
from modules.base import BaseTestModule

class MyCustomModule(BaseTestModule):
    def __init__(self):
        super().__init__(
            name="my_custom_module",
            description="My custom test",
            severity="medium"
        )

    async def run(self, context):
        # Test logic burada
        url = context.url

        # Bulgu varsa kaydet
        self.add_finding(
            title="Custom Finding",
            description="Found something",
            severity="high",
            evidence={"url": url}
        )

        return self.get_results()
```

**Kullanım:**
```bash
python main.py --url https://example.com --modules custom.my_module
```

---

## 🐛 SORUN GİDERME

### Problem: Testler çalışmıyor

**Hata:** `ModuleNotFoundError: No module named 'pytest'`

**Çözüm:**
```bash
pip install -r requirements-test.txt
```

---

### Problem: Monitoring API başlamıyor

**Hata:** `ModuleNotFoundError: No module named 'fastapi'`

**Çözüm:**
```bash
pip install fastapi uvicorn psutil
```

---

### Problem: Port 8081 kullanımda

**Hata:** `Address already in use`

**Çözüm:**
```bash
# Farklı port kullan
uvicorn api.health:app --port 8082

# Veya process'i bul ve kapat (Windows)
netstat -ano | findstr :8081
taskkill /PID <PID> /F
```

---

### Problem: Playwright çalışmıyor

**Hata:** `Playwright executable not found`

**Çözüm:**
```bash
python -m playwright install
```

---

### Problem: Tarama çok yavaş

**Çözümler:**

1. **Paralel worker artır:**
```bash
python main.py --url https://example.com --workers 10
```

2. **Sayfa sayısını azalt:**
```bash
python main.py --url https://example.com --max-pages 10
```

3. **Quick profile kullan:**
```bash
python main.py --url https://example.com --profile quick
```

4. **Profiling yap ve bottleneck bul:**
```bash
python tools/profile_scan.py --url https://example.com
```

---

## 📖 KULLANIM ÖRNEKLERİ

### Örnek 1: E-ticaret Sitesi Tara

```bash
# Güvenlik ve performans odaklı
python main.py \
    --url https://myshop.com \
    --profile security \
    --max-pages 50 \
    --workers 5 \
    --modules security.xss security.sql_injection security.csrf performance.page_speed
```

### Örnek 2: Blog Sitesi SEO Analizi

```bash
python main.py \
    --url https://myblog.com \
    --modules seo.meta_tags seo.structured_data seo.sitemap \
    --max-pages 100
```

### Örnek 3: API Endpoint Testi

```bash
python main.py \
    --url https://api.example.com \
    --modules api.rest api.authentication api.rate_limit \
    --profile quick
```

### Örnek 4: Karşılaştırmalı Performans Analizi

```bash
# 1. Baseline al
python tools/profile_scan.py \
    --url https://example.com \
    --pages 20 \
    --output baseline.json

# 2. Optimizasyon yap (kod değişikliği)

# 3. Tekrar profille
python tools/profile_scan.py \
    --url https://example.com \
    --pages 20 \
    --output after_optimization.json

# 4. JSON dosyalarını karşılaştır
# reports/baseline.json vs reports/after_optimization.json
```

---

## 🎯 HIZLI KOMUT REFERANSı

### Tarama Komutları

```bash
# Quick scan
python main.py --url <URL> --profile quick

# Security scan
python main.py --url <URL> --profile security

# Full scan
python main.py --url <URL> --profile full --max-pages 100

# Özel modüllerle
python main.py --url <URL> --modules security.xss performance.page_speed
```

### Test Komutları

```bash
# Tüm testler
pytest tests/ -v

# Coverage ile
pytest tests/unit/core/ --cov=core --cov-report=html

# Belirli test
pytest tests/unit/core/test_config_comprehensive.py -v
```

### Profiling Komutları

```bash
# Basit profiling
python tools/profile_scan.py --url <URL> --profile quick

# Detaylı profiling
python tools/profile_scan.py --url <URL> --pages 50 --output report.json
```

### Monitoring Komutları

```bash
# API başlat
python api/health.py

# Health check
curl http://localhost:8081/health

# Metrics
curl http://localhost:8081/metrics

# System stats
curl http://localhost:8081/stats/system
```

---

## 📚 DAHA FAZLA BİLGİ

### Yeni Özellikleri Öğren
- `HIZLI_BASLANGIC_YENI_OZELLIKLER.md` - Yeni eklenen özellikler hakkında detaylı bilgi

### Neler Yapıldı
- `TAMAMLANAN_IYILESTIRMELER_2025.md` - 23 Ekim 2025'te tamamlanan iyileştirmeler

### Gelecek Planlar
- `gelecektebelki.md` - Gelecekte eklenebilecek özellikler

### Teknik Mimari
- `ARCHITECTURE.md` - Sistemin teknik mimarisi

### Proje Tanıtımı
- `README.md` - Proje hakkında genel bilgi

---

## 🎉 ÖZET

**WebTestool'u Kullanmaya Başla:**

1. **Kurulum:**
   ```bash
   pip install -r requirements.txt
   python -m playwright install
   ```

2. **İlk Tarama:**
   ```bash
   python main.py --url https://example.com --profile quick
   ```

3. **Raporu Gör:**
   ```bash
   open reports/<timestamp>/report.html
   ```

**İşte bu kadar! Sistem hazır.**

---

**Son Güncelleme:** 23 Ekim 2025
**Versiyon:** 2.0
**Hazırlayan:** Claude Code AI Assistant

**Not:** Bu rehber, WebTestool'un TÜM özelliklerini ve kullanımını kapsar. Herhangi bir sorun yaşarsan, "Sorun Giderme" bölümüne bak.
