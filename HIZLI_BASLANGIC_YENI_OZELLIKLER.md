# ⚡ HIZLI BAŞLANGIÇ - YENİ ÖZELLİKLER

**Oluşturulma:** 23 Ekim 2025
**Durum:** Kullanıma Hazır

---

## 🚀 5 DAKİKADA YENİ ÖZELLİKLERİ KULLAN

### 1️⃣ Test Coverage - İlk Testleri Çalıştır (2 dakika)

```bash
# Test bağımlılıklarını yükle
pip install pytest pytest-asyncio pytest-cov

# Yeni testleri çalıştır
pytest tests/unit/core/test_config_comprehensive.py -v

# Sonuç:
# ✅ 30+ test case
# ✅ Config manager fully tested
# ⚡ ~5 saniyede tamamlanır
```

**Coverage raporu:**
```bash
# HTML coverage raporu oluştur
pytest tests/unit/core/ --cov=core --cov-report=html

# Raporu aç
# Windows:
start htmlcov/index.html

# Linux/Mac:
open htmlcov/index.html
```

---

### 2️⃣ Performance Profiling - İlk Profiling (2 dakika)

```bash
# Basit bir profiling yap
python tools/profile_scan.py \
    --url https://example.com \
    --pages 5 \
    --profile quick

# Çıktı:
# 🎯 Target: https://example.com
# ⏱️  Duration: 15.32s
# 💾 Peak Memory: 245.67 MB
# 📊 URLs Crawled: 5
# 🔥 Top Bottlenecks:
#   1. [HIGH] core.scanner.WebScanner._crawl_url
#      Time: 8.234s (5 calls)
```

**Sonuçları kaydet:**
```bash
python tools/profile_scan.py \
    --url https://example.com \
    --output my_profile.json

# JSON dosyası oluşturulur: reports/my_profile.json
```

---

### 3️⃣ Monitoring API - Health Checks (1 dakika)

```bash
# Monitoring API'yi başlat (terminal 1)
pip install fastapi uvicorn psutil
python api/health.py

# API çalışıyor: http://localhost:8081
```

**Health check yap (terminal 2):**
```bash
# Genel health check
curl http://localhost:8081/health

# Sonuç:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-23T...",
#   "checks": {
#     "database": true,
#     "cache": true,
#     "disk_space": true,
#     "memory": true,
#     "cpu": true
#   }
# }
```

**Metrikleri al:**
```bash
# Prometheus format
curl http://localhost:8081/metrics

# JSON format
curl http://localhost:8081/metrics/json | jq
```

---

## 📚 DETAYLI KULLANIM

### Test Suite Kullanımı

#### Tüm Testleri Çalıştır
```bash
# Tüm core testleri
pytest tests/unit/core/ -v

# Sadece başarısız olanları göster
pytest tests/unit/core/ -v --tb=short

# Verbose output
pytest tests/unit/core/ -vv

# Parallel execution (hızlı)
pip install pytest-xdist
pytest tests/unit/core/ -n auto
```

#### Belirli Testler
```bash
# Sadece config testleri
pytest tests/unit/core/test_config_comprehensive.py -v

# Sadece engine testleri
pytest tests/unit/core/test_engine_comprehensive.py -v

# Sadece bir test class
pytest tests/unit/core/test_config_comprehensive.py::TestConfigGetSet -v

# Sadece bir test method
pytest tests/unit/core/test_config_comprehensive.py::TestConfigGetSet::test_set_simple_value -v
```

#### Coverage Raporları
```bash
# Terminal'de coverage
pytest tests/unit/core/ --cov=core --cov-report=term-missing

# HTML raporu
pytest tests/unit/core/ --cov=core --cov-report=html
open htmlcov/index.html

# XML raporu (CI/CD için)
pytest tests/unit/core/ --cov=core --cov-report=xml

# Tüm formatlar
pytest tests/unit/core/ \
    --cov=core \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml
```

#### Test Filtering
```bash
# Sadece hızlı testler (slow işaretli olanları atla)
pytest tests/unit/core/ -m "not slow"

# Sadece yavaş testler
pytest tests/unit/core/ -m slow

# İsme göre filtrele
pytest tests/unit/core/ -k "config" -v
pytest tests/unit/core/ -k "validation" -v
```

---

### Performance Profiling Kullanımı

#### Temel Profiling
```bash
# Quick scan profile
python tools/profile_scan.py \
    --url https://example.com \
    --profile quick

# Security scan profile
python tools/profile_scan.py \
    --url https://example.com \
    --profile security

# Full scan profile
python tools/profile_scan.py \
    --url https://example.com \
    --profile full \
    --pages 100
```

#### İleri Seviye
```bash
# Çok sayıda sayfa ile test et
python tools/profile_scan.py \
    --url https://example.com \
    --pages 50 \
    --profile quick \
    --output performance_test_50pages.json

# Sonuçları karşılaştır
# 1. Baseline oluştur
python tools/profile_scan.py \
    --url https://example.com \
    --pages 10 \
    --output baseline.json

# 2. Optimizasyondan sonra tekrar profille
python tools/profile_scan.py \
    --url https://example.com \
    --pages 10 \
    --output after_optimization.json

# 3. Karşılaştır (manuel olarak JSON'ları karşılaştır)
```

#### Profiling Sonuçlarını Okuma

**JSON Çıktısı:**
```json
{
  "target_url": "https://example.com",
  "duration": {
    "total_seconds": 15.32,
    "formatted": "15.32s"
  },
  "memory": {
    "current_mb": 180.45,
    "peak_mb": 245.67
  },
  "scan_stats": {
    "urls_crawled": 5,
    "modules_executed": 1,
    "total_findings": 3
  },
  "bottlenecks": [
    {
      "function": "core/scanner.py:68:_crawl_url",
      "cumulative_time": 8.234,
      "calls": 5,
      "time_per_call": 1.647,
      "severity": "HIGH"
    }
  ]
}
```

---

### Monitoring API Kullanımı

#### Health Endpoints

**1. Comprehensive Health Check:**
```bash
curl http://localhost:8081/health | jq

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-23T10:30:00",
#   "checks": { ... },
#   "failed_checks": [],
#   "uptime_seconds": 3600.5
# }
```

**2. Liveness Probe (Kubernetes):**
```bash
curl http://localhost:8081/health/live

# Response: {"status": "alive", "timestamp": "..."}
# Status Code: 200 (always, if app is running)
```

**3. Readiness Probe (Kubernetes):**
```bash
curl http://localhost:8081/health/ready

# Response: {"status": "ready", "timestamp": "..."}
# Status Code: 200 (ready) or 503 (not ready)
```

**4. Component Health:**
```bash
curl http://localhost:8081/health/components | jq

# Response:
# {
#   "timestamp": "...",
#   "components": {
#     "database": true,
#     "cache": true,
#     "disk_space": true,
#     "memory": true,
#     "cpu": true
#   },
#   "overall_status": "healthy"
# }
```

#### Metrics Endpoints

**1. Prometheus Metrics:**
```bash
curl http://localhost:8081/metrics

# Response: (Prometheus text format)
# # HELP webtestool_scans_total Total number of scans
# # TYPE webtestool_scans_total counter
# webtestool_scans_total 42
# ...
```

**2. JSON Metrics:**
```bash
curl http://localhost:8081/metrics/json | jq

# Response:
# {
#   "timestamp": "...",
#   "metrics": {
#     "scans": {
#       "total": 42,
#       "success": 38,
#       "failure": 4,
#       "active": 2
#     },
#     "findings": {
#       "by_severity": {
#         "critical": 5,
#         "high": 12
#       }
#     }
#   }
# }
```

#### System Stats

**1. System Resources:**
```bash
curl http://localhost:8081/stats/system | jq

# CPU, Memory, Disk stats
```

**2. Scan Statistics:**
```bash
curl http://localhost:8081/stats/scans | jq

# Historical scan stats from database
```

**3. Version Info:**
```bash
curl http://localhost:8081/version | jq

# Response:
# {
#   "name": "WebTestool",
#   "version": "2.0.0",
#   "python_version": "3.11.0",
#   "build_date": "2025-10-23"
# }
```

---

## 🔧 KOD İÇİNDE KULLANIM

### Metrics Tracking

```python
# main.py
from utils.metrics import get_metrics

def main():
    metrics = get_metrics()

    # Scan başladığında
    metrics.record_scan_start()

    try:
        # Scan yap
        start_time = time.time()
        result = await engine.run()
        duration = time.time() - start_time

        # Başarılı scan
        metrics.record_scan_end(duration, success=True)

        # Findings kaydet
        for finding in result.get_all_findings():
            metrics.record_finding(finding.severity.value)

        # Module execution kaydet
        for module_result in result.module_results:
            metrics.record_module_execution(
                module_result.name,
                module_result.duration
            )

    except Exception as e:
        # Hata kaydet
        metrics.record_error(type(e).__name__)
        metrics.record_scan_end(duration, success=False)

    # Özet göster
    metrics.print_summary()
```

### Health Checks

```python
# Startup check
from utils.health import get_health_checker

async def startup():
    health = get_health_checker()

    # Wait until healthy
    is_healthy = await health.wait_for_healthy(timeout=30)

    if not is_healthy:
        logger.error("System not healthy after 30s")
        sys.exit(1)

    logger.info("System is healthy, starting application")

# Periodic check
async def periodic_health_check():
    health = get_health_checker()

    while True:
        result = await health.run_all_checks()

        if result['status'] != 'healthy':
            logger.warning(f"Health check failed: {result['failed_checks']}")

        await asyncio.sleep(60)  # Check every minute
```

---

## 🐛 SORUN GİDERME

### Testler Çalışmıyor

**Problem:** `ModuleNotFoundError: No module named 'pytest'`

**Çözüm:**
```bash
pip install -r requirements-test.txt
```

---

**Problem:** Tests fail with import errors

**Çözüm:**
```bash
# PYTHONPATH'i ayarla
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Veya
python -m pytest tests/unit/core/ -v
```

---

### Profiling Çalışmıyor

**Problem:** `ModuleNotFoundError: No module named 'core'`

**Çözüm:**
```bash
# Script doğru dizinden çalıştırılmalı
cd C:\Projects\testool
python tools/profile_scan.py --url https://example.com
```

---

**Problem:** Memory tracking errors

**Çözüm:**
```bash
# Python 3.8+ gerekli
python --version

# Upgrade if needed
```

---

### Monitoring API Sorunları

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Çözüm:**
```bash
pip install fastapi uvicorn psutil
```

---

**Problem:** Port 8081 already in use

**Çözüm:**
```bash
# Farklı port kullan
uvicorn api.health:app --port 8082

# Veya kullanımdaki process'i bul
# Windows:
netstat -ano | findstr :8081
taskkill /PID <PID> /F

# Linux:
lsof -i :8081
kill -9 <PID>
```

---

## 📊 SONUÇLARI DEĞERLENDİRME

### Test Coverage
```bash
# Coverage raporu oluşturduktan sonra
open htmlcov/index.html

# Şu bilgilere bak:
# - Overall coverage percentage
# - Lines missing coverage (kırmızı)
# - Partial coverage (sarı)
# - Full coverage (yeşil)
```

**Hedefler:**
- Core modules: 85%+
- Utils: 80%+
- Tests: 70%+

---

### Performance Profiling

**Baseline Oluştur:**
1. İlk profiling yap → baseline.json
2. Değişiklik yap (optimization)
3. Tekrar profille → after.json
4. Karşılaştır

**Değerlendirme Kriterleri:**
- Duration azaldı mı?
- Peak memory azaldı mı?
- Bottleneck'ler azaldı mı?
- Severity'ler düştü mü? (CRITICAL → HIGH)

---

### Monitoring Metrics

**Prometheus/Grafana ile görselleştirme:**
1. Prometheus'u ayarla
2. WebTestool metrics endpoint ekle
3. Grafana dashboard oluştur

**Takip edilecek metrikler:**
- Scan success rate
- Average scan duration
- Findings trend
- Error rate
- Cache hit rate

---

## ✅ CHECKLIST

Yeni özellikleri kullanmaya başlamak için:

- [ ] Test dependencies yükledim
- [ ] İlk testleri çalıştırdım
- [ ] Coverage raporunu oluşturdum
- [ ] Profile script çalıştırdım
- [ ] Monitoring API'yi başlattım
- [ ] Health check yaptım
- [ ] Metrics aldım
- [ ] Dokümantasyonu okudum

---

## 🎓 İLERİ SEVİYE

### CI/CD Integration

**GitHub Actions örneği:**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest tests/unit/core/ \
            --cov=core \
            --cov-report=xml \
            --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: v1
kind: Service
metadata:
  name: webtestool-monitoring
spec:
  ports:
    - port: 8081
      name: metrics
  selector:
    app: webtestool

---
apiVersion: v1
kind: Pod
metadata:
  name: webtestool
  labels:
    app: webtestool
spec:
  containers:
  - name: webtestool
    image: webtestool:latest
    ports:
    - containerPort: 8081
      name: metrics

    # Liveness probe
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8081
      initialDelaySeconds: 10
      periodSeconds: 30

    # Readiness probe
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8081
      initialDelaySeconds: 5
      periodSeconds: 10
```

---

**🎉 Hazırsın! Yeni özellikleri kullanmaya başlayabilirsin!**

*Sorular için: TAMAMLANAN_IYILESTIRMELER_2025.md dosyasına bak*
