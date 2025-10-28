# WebTestool v2.0 - Hızlı Başlangıç Rehberi

## 🎯 5 Dakikada Başlayın!

### Adım 1: Bağımlılıkları Yükleyin (2 dakika)

```bash
# Tüm bağımlılıkları yükle
pip install -r requirements.txt

# Veya hızlı kurulum
pip install playwright httpx beautifulsoup4 sqlalchemy pyyaml loguru rich aiofiles pytest
```

### Adım 2: İlk Taramanızı Yapın (1 dakika)

#### En Kolay Yol - Interactive Mode

```bash
python main_enhanced.py --interactive
```

Bu komut sizi adım adım yönlendirecek:
1. ✅ Hedef URL girin
2. ✅ Tarama profili seçin (Quick önerilir)
3. ✅ Authentication gerekirse yapılandırın
4. ✅ Taramayı başlatın!

#### Hızlı Tarama

```bash
python main_enhanced.py --url https://example.com --profile quick --pdf
```

**Sonuç:** 1-3 dakikada HTML + PDF rapor

---

## 📊 Kullanım Senaryoları

### 1. E-Commerce Güvenlik Taraması

```bash
python main_enhanced.py \
  --url https://shop.example.com \
  --config config/templates/ecommerce.yaml \
  --pdf --excel --save-db
```

**Ne Yapar:**
- Payment security kontrolleri
- SQL injection testleri
- Session güvenliği
- PCI DSS compliance

**Süre:** 5-15 dakika

### 2. API Testing

```bash
python main_enhanced.py \
  --url https://api.example.com/v1 \
  --config config/templates/api.yaml \
  --pdf
```

**Ne Yapar:**
- JWT token testleri
- Authentication/Authorization
- Rate limiting kontrolü
- GraphQL security

**Süre:** 3-8 dakika

### 3. WCAG Accessibility Audit

```bash
python main_enhanced.py \
  --url https://example.com \
  --config config/templates/compliance.yaml \
  --pdf --excel
```

**Ne Yapar:**
- WCAG 2.1 Level AA testleri
- Keyboard navigation
- Screen reader uyumluluğu
- Color contrast kontrolü

**Süre:** 15-30 dakika

### 4. WordPress Güvenlik

```bash
python main_enhanced.py \
  --url https://wordpress-site.com \
  --config config/templates/wordpress.yaml \
  --pdf
```

**Ne Yapar:**
- Plugin vulnerability scan
- Theme security
- User enumeration
- XML-RPC güvenliği

**Süre:** 10-20 dakika

---

## 🎨 Tüm Özellikler

### Interactive Mode (Önerilen)

```bash
python main_enhanced.py --interactive
```

**Avantajları:**
- ✅ Soru-cevap formatı
- ✅ Otomatik config oluşturma
- ✅ Profil seçimi
- ✅ Authentication wizard
- ✅ Hata yapma riski yok

### Manuel Tarama

```bash
# Temel
python main_enhanced.py --url https://example.com

# Profil seçerek
python main_enhanced.py --url https://example.com --profile security

# PDF rapor ile
python main_enhanced.py --url https://example.com --pdf

# Excel rapor ile
python main_enhanced.py --url https://example.com --excel

# Her ikisi + veritabanı
python main_enhanced.py --url https://example.com --pdf --excel --save-db

# Private IP taraması
python main_enhanced.py --url http://192.168.1.1 --allow-private-ips

# Cache olmadan
python main_enhanced.py --url https://example.com --no-cache

# Verbose output
python main_enhanced.py --url https://example.com --verbose
```

### Specific Modules

```bash
# Sadece security
python main_enhanced.py --url https://example.com --profile security

# Sadece performance
python main_enhanced.py --url https://example.com --profile performance

# Custom modules
python main_enhanced.py --url https://example.com --tests security,seo
```

---

## 📁 Configuration Templates

### Kullanılabilir Şablonlar

| Şablon | Kullanım | Süre |
|--------|----------|------|
| `quick.yaml` | Hızlı tarama | 1-3 dk |
| `ecommerce.yaml` | E-ticaret | 5-15 dk |
| `api.yaml` | API testing | 3-8 dk |
| `compliance.yaml` | WCAG compliance | 15-30 dk |
| `wordpress.yaml` | WordPress | 10-20 dk |
| `full.yaml` | Tam tarama | 15-45 dk |

### Template Kullanımı

```bash
# Template ile tarama
python main_enhanced.py \
  --url https://example.com \
  --config config/templates/TEMPLATE_ADI.yaml

# Örnek: E-commerce
python main_enhanced.py \
  --url https://shop.com \
  --config config/templates/ecommerce.yaml \
  --pdf
```

### Custom Template Oluşturma

```bash
# Şablonu kopyala
copy config\templates\quick.yaml config\my-custom.yaml

# Düzenle
notepad config\my-custom.yaml

# Kullan
python main_enhanced.py --url https://example.com --config config\my-custom.yaml
```

---

## 🔐 Güvenli Kimlik Bilgileri

### Kimlik Bilgisi Kaydetme

```bash
# CLI ile
python -m utils.secrets_manager

# Interactive mode ile (otomatik)
python main_enhanced.py --interactive
```

### Config Dosyasında Kullanım

```yaml
target:
  auth:
    type: basic
    username: admin
    password: {{ SECRET:myapp:admin }}
```

### Programatik Kullanım

```python
from utils.secrets_manager import get_secrets_manager

manager = get_secrets_manager()

# Kaydet
manager.store_credential("myapp", "admin", "password123")

# Al
password = manager.get_credential("myapp", "admin")
```

---

## 📊 Raporlar

### Rapor Formatları

1. **HTML** (varsayılan) - Web browser'da görüntüle
2. **PDF** - Paylaşım için ideal
3. **Excel** - Veri analizi için

### Rapor Oluşturma

```bash
# Sadece HTML
python main_enhanced.py --url https://example.com

# HTML + PDF
python main_enhanced.py --url https://example.com --pdf

# HTML + Excel
python main_enhanced.py --url https://example.com --excel

# Hepsi
python main_enhanced.py --url https://example.com --pdf --excel
```

### Raporları Açma

```bash
# En son raporu aç
rapor_ac.bat

# Veya manuel
start reports\report_TIMESTAMP.html
start reports\report_TIMESTAMP.pdf
start reports\report_TIMESTAMP.xlsx
```

---

## 🗄️ Veritabanı

### Sonuçları Kaydetme

```bash
python main_enhanced.py --url https://example.com --save-db
```

### Veritabanı Sorgulama

```python
from database.optimized_db_manager import get_db_manager

db = get_db_manager()

# Son taramaları al
scans = db.get_all_scans(limit=10)

# İstatistikler
stats = db.get_statistics()
print(f"Total scans: {stats['total_scans']}")
print(f"Critical findings: {stats['critical_findings']}")

# Scan detayları
scan = db.get_scan_result(scan_id=1)
findings = db.get_findings_by_scan(scan_id=1)

# Eski taramaları sil
deleted = db.delete_old_scans(days=30)
```

---

## 🎨 Kod Kalitesi

### İlk Kurulum

```bash
# Linting araçlarını kur
setup_linting.bat
```

### Kullanım

```bash
# Tüm kontrolleri çalıştır
run_linting.bat

# Sadece format
black .

# Sadece lint
flake8 .

# Sadece type check
mypy .

# Hızlı lint + auto-fix
ruff check . --fix
```

### Pre-commit Hooks

```bash
# Kur (bir kere)
pre-commit install

# Artık her commit'te otomatik çalışır
git commit -m "my changes"
```

---

## 🐛 Sorun Giderme

### Bağımlılık Hatası

```bash
# Tüm bağımlılıkları yeniden yükle
pip install -r requirements.txt --force-reinstall

# Veya tek tek
pip install playwright --upgrade
pip install httpx --upgrade
```

### ModuleNotFoundError

```bash
# Python path kontrolü
python -c "import sys; print('\n'.join(sys.path))"

# Projeyi path'e ekle
set PYTHONPATH=C:\Projects\testool
```

### URL Validation Error

```bash
# Private IP için
python main_enhanced.py --url http://192.168.1.1 --allow-private-ips

# HTTPS zorunlu değil
python main_enhanced.py --url http://example.com
```

### Keyring Error

```bash
# Fallback mode kullanır (otomatik)
# Credentials ~/.webtestool/credentials.enc dosyasına kaydedilir
```

### Slow Scans

```bash
# Cache etkinleştir (varsayılan zaten açık)
python main_enhanced.py --url https://example.com --cache

# Daha az sayfa tara
python main_enhanced.py --url https://example.com --profile quick
```

---

## 📚 İleri Seviye

### Programatik Kullanım

```python
from core import ConfigManager, TestEngine
from utils.sanitizers import sanitize_url
from utils.cache import get_cache
from reporting.pdf_reporter import generate_pdf_report

# URL doğrulama
url = sanitize_url("https://example.com")

# Config yükleme
config = ConfigManager("config/templates/quick.yaml")
config.set('target.url', url)

# Cache aktif et
cache = get_cache()

# Scan çalıştır
import asyncio
engine = TestEngine(config)
result = asyncio.run(engine.run())

# PDF rapor
pdf_path = generate_pdf_report({
    'target': url,
    'date': str(result.start_time),
    'summary': result.summary,
    'vulnerabilities': [...]
})
```

### Scheduled Scans (Windows Task Scheduler)

```bat
@echo off
cd C:\Projects\testool
python main_enhanced.py ^
  --url https://example.com ^
  --config config/templates/security.yaml ^
  --pdf --save-db
```

Görev Zamanlayıcı:
1. Task Scheduler açın
2. Create Basic Task
3. Daily / Weekly seçin
4. Action: Start a program
5. Program: `C:\Projects\testool\scan.bat`

### CI/CD Integration

```yaml
# GitHub Actions örnek
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * 0'  # Her Pazar 02:00

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run security scan
        run: |
          python main_enhanced.py \
            --url ${{ secrets.TARGET_URL }} \
            --profile security \
            --pdf --save-db

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: reports/*.pdf
```

---

## 💡 İpuçları

### En İyi Uygulamalar

1. ✅ **İlk tarama için Quick kullanın** - Hızlı geri bildirim
2. ✅ **Staging'de test edin** - Production'da agresif testler yapmayın
3. ✅ **Template kullanın** - Doğru konfigürasyon garantisi
4. ✅ **Cache açık tutun** - 3-5x daha hızlı
5. ✅ **Verbose mode kullanın** - Hata ayıklama için
6. ✅ **Sonuçları kaydedin** - Trend analizi için
7. ✅ **Interactive mode tercih edin** - Kolay ve hatasız

### Performans İpuçları

```bash
# Hızlı tarama
--profile quick

# Cache kullan
--cache (varsayılan açık)

# Daha az sayfa
--config ile max_pages ayarla

# Paralel modüller
# (otomatik)
```

### Güvenlik İpuçları

```bash
# Private IP'ler için dikkat
--allow-private-ips (sadece gerekirse)

# Credentials güvenli sakla
python main_enhanced.py --interactive

# Rate limiting
config'de rate_limit ayarları

# Respectful scanning
crawl_delay: 0.5  # saniye
```

---

## 🎓 Öğrenme Kaynakları

### Dokümantasyon
- `TAMAMLANAN_IYILESTIRMELER.md` - Tüm özellikler
- `YENI_OZELLIKLER_KULLANIM.md` - Detaylı örnekler
- `CODE_QUALITY.md` - Kod kalite rehberi
- `config/templates/README.md` - Template rehberi

### Örnekler
- `config/templates/*.yaml` - Configuration örnekleri
- `tests/unit/*.py` - Code örnekleri

### Batch Scripts
- `tarama_yap.bat` - Interactive menu
- `guvenlik_taramasi.bat` - Security scan
- `performans_testi.bat` - Performance test
- `rapor_ac.bat` - Report viewer
- `setup_linting.bat` - Linting setup
- `run_linting.bat` - Run quality checks
- `test_yeni_ozellikler.bat` - Run tests

---

## 🚀 Başarılı Tarama!

### İlk Tarama Checklist

- [ ] Bağımlılıkları yükledin (`pip install -r requirements.txt`)
- [ ] Interactive mode'u denedin (`python main_enhanced.py --interactive`)
- [ ] Bir template kullandın (`--config config/templates/quick.yaml`)
- [ ] PDF rapor oluşturdun (`--pdf`)
- [ ] Sonuçları veritabanına kaydett in (`--save-db`)
- [ ] Linting araçlarını kurdun (`setup_linting.bat`)

### Sonraki Adımlar

1. Farklı profilleri dene (quick, security, performance, full)
2. Kendi template'ini oluştur
3. Scheduled scans kur
4. CI/CD entegrasyonu yap
5. Custom modules geliştir

---

**WebTestool v2.0 ile güvenli taramalar! 🎉**

Sorular? → Dokümantasyona bakın veya issue açın!
