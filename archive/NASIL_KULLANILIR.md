# 🚀 WebTestool - Basit Kullanım Kılavuzu

## ⚡ Hızlı Başlangıç (3 Dakika)

### 1️⃣ Kurulum (İlk Kez)

**Windows:**
```bash
# Projeyi indirdiğiniz klasöre gidin
cd C:\Projects\testool

# Kurulum scriptini çalıştırın (tek tık!)
quick_setup.bat
```

**Linux/Mac:**
```bash
# Projeyi indirdiğiniz klasöre gidin
cd /path/to/testool

# Kurulum scriptini çalıştırın
chmod +x install.sh
./install.sh
```

### 2️⃣ İlk Taramanızı Yapın

**Windows:**
```bash
# Hızlı test (2-3 dakika sürer)
tarama_yap.bat
```

Manuel olarak çalıştırmak için:
```bash
python main.py --url https://example.com --profile quick
```

### 3️⃣ Sonuçları İnceleyin

Tarama bittiğinde:
1. `reports/scan_TARIH_SAAT/` klasörüne bakın
2. `report.html` dosyasını tarayıcıda açın
3. Bulguları inceleyin!

---

## 📋 Basit Kullanım Örnekleri

### Örnek 1: Hızlı Güvenlik Taraması
```bash
python main.py --url https://siteniz.com --profile quick
```
- ⏱️ **Süre:** 1-3 dakika
- 🔍 **Kapsamı:** 10 sayfa tarar
- ✅ **Kullanım:** İlk test için ideal

### Örnek 2: Tam Güvenlik Taraması
```bash
python main.py --url https://siteniz.com --profile security
```
- ⏱️ **Süre:** 5-15 dakika
- 🔍 **Kapsamı:** Tüm sitede güvenlik testleri
- ✅ **Kullanım:** Detaylı güvenlik analizi

### Örnek 3: Sadece Performans Testi
```bash
python main.py --url https://siteniz.com --profile performance
```
- ⏱️ **Süre:** 3-8 dakika
- 🔍 **Kapsamı:** Hız ve yük testleri
- ✅ **Kullanım:** Site yavaşlığı analizi

### Örnek 4: Tam Kapsamlı Tarama
```bash
python main.py --url https://siteniz.com
```
- ⏱️ **Süre:** 15-45 dakika
- 🔍 **Kapsamı:** Her şey (güvenlik, performans, SEO, erişilebilirlik)
- ✅ **Kullanım:** Komple site analizi

---

## 🎯 Test Profilleri

| Profil | Ne Yapar? | Ne Zaman Kullanılır? | Süre |
|--------|-----------|----------------------|------|
| **quick** | Hızlı test (10 sayfa) | İlk deneme, hızlı kontrol | 1-3 dk |
| **security** | Güvenlik açıkları | Güvenlik denetimi | 5-15 dk |
| **performance** | Hız ve yük testi | Performans analizi | 3-8 dk |
| **full** (varsayılan) | Her şey | Tam analiz | 15-45 dk |

---

## 🔐 Şifre/Giriş Gerektiren Siteler

Eğer siteniz giriş gerektiriyorsa:

### 1. Yapılandırma dosyası oluşturun

`benim_ayarlarim.yaml` adında dosya oluşturun:

```yaml
target:
  url: "https://siteniz.com"
  auth:
    type: "basic"
    username: "test_kullanici"
    password: "test_sifre"
```

### 2. Bu dosya ile tarayın

```bash
python main.py --url https://siteniz.com --config benim_ayarlarim.yaml
```

---

## 📊 Sonuçları Anlama

### Rapor Dosyaları

Tarama bittiğinde `reports/scan_TARIH_SAAT/` klasöründe:

- **report.html** 📄 → Tarayıcıda açın (en detaylı)
- **report.json** 💾 → Programlar için (makine okunabilir)
- **summary.txt** 📝 → Hızlı özet (metin dosyası)

### Bulgu Seviyeleri

Raporlarda bulgular önem sırasına göre sıralanır:

| Seviye | Renk | Anlamı | Öncelik |
|--------|------|--------|---------|
| 🔴 **Critical** | Kırmızı | Çok ciddi güvenlik açığı | Hemen düzelt! |
| 🟠 **High** | Turuncu | Önemli güvenlik sorunu | En kısa sürede düzelt |
| 🟡 **Medium** | Sarı | Orta seviye sorun | Yakında düzelt |
| 🟢 **Low** | Yeşil | Küçük sorun | Fırsat buldukça düzelt |
| 🔵 **Info** | Mavi | Bilgi amaçlı | İnceleme için |

---

## 🎨 Hangi Testler Yapılıyor?

### ✅ Güvenlik Testleri (30+ test)
- SQL Injection (Veritabanı saldırıları)
- XSS (JavaScript saldırıları)
- CSRF (Sahte istek saldırıları)
- Komut çalıştırma açıkları
- Dosya okuma açıkları
- Güvenlik başlıkları kontrolü
- SSL/HTTPS kontrolü
- Ve daha fazlası...

### ⚡ Performans Testleri
- Sayfa yükleme hızı
- Yük testi (çok kullanıcı simülasyonu)
- Kaynak optimizasyonu
- Önbellekleme kontrolü

### 📈 SEO Testleri
- Meta etiketler
- Başlıklar yapısı
- Resim alt metinleri
- Mobil uyumluluk
- Sitemap kontrolü

### ♿ Erişilebilirlik Testleri
- WCAG 2.1 uyumluluk
- Engelli kullanıcılar için uygunluk
- Form etiketleri
- Klavye navigasyonu

---

## ⚙️ Özelleştirme

### Basit Ayarlar

`basit_ayarlar.yaml` dosyası:

```yaml
target:
  url: "https://siteniz.com"

crawler:
  max_pages: 50        # Maksimum 50 sayfa tara
  max_depth: 3         # 3 seviye derinlik

modules:
  security:
    enabled: true      # Güvenlik testleri AÇIK
  performance:
    enabled: true      # Performans testleri AÇIK
  seo:
    enabled: false     # SEO testleri KAPALI
  accessibility:
    enabled: false     # Erişilebilirlik testleri KAPALI
```

Kullanım:
```bash
python main.py --url https://siteniz.com --config basit_ayarlar.yaml
```

---

## 🛠️ Sık Kullanılan Komutlar

```bash
# Hızlı test (önerilen başlangıç)
python main.py --url https://siteniz.com --profile quick

# Sadece güvenlik
python main.py --url https://siteniz.com --profile security

# Sadece performans
python main.py --url https://siteniz.com --profile performance

# Detaylı bilgi görüntüle
python main.py --url https://siteniz.com --verbose

# Özel klasöre rapor kaydet
python main.py --url https://siteniz.com --output ./raporlarim

# Belirli testleri çalıştır
python main.py --url https://siteniz.com --tests security,seo

# Özel ayarlarla çalıştır
python main.py --url https://siteniz.com --config ayarlarim.yaml
```

---

## 🐛 Sorun Giderme

### Sorun: Python bulunamadı
**Çözüm:**
- Windows: [python.org](https://python.org)'dan Python 3.11+ indirin
- Linux: `sudo apt install python3.11`
- Mac: `brew install python@3.11`

### Sorun: Playwright tarayıcıları kurulmamış
**Çözüm:**
```bash
python -m playwright install
```

### Sorun: Tarama çok yavaş
**Çözüm 1:** Hızlı profil kullanın
```bash
python main.py --url https://siteniz.com --profile quick
```

**Çözüm 2:** Sayfa limitini düşürün
```yaml
crawler:
  max_pages: 20
```

### Sorun: Çok fazla hatalı bulgu (false positive)
**Çözüm:** Agresif modu kapatın
```yaml
modules:
  security:
    aggressive_mode: false
```

---

## 💡 İpuçları

### ✅ YAPILMASI GEREKENLER
1. ✅ İlk testinizi `--profile quick` ile yapın
2. ✅ Raporları HTML formatında inceleyin
3. ✅ Sadece kendi sitenizi test edin
4. ✅ Bulguları inceleyip doğrulayın
5. ✅ Düzenli taramalar yapın

### ❌ YAPILMAMASI GEREKENLER
1. ❌ Yetkiniz olmayan siteleri test etmeyin (suçtur!)
2. ❌ Tüm bulguları gerçek sanmayın (false positive olabilir)
3. ❌ Üretim ortamında agresif testler yapmayın
4. ❌ İzinsiz başkasının sitesini taramayın

---

## 📱 Örnek Kullanım Senaryoları

### Senaryo 1: Yeni Bir Site Test Etme
```bash
# 1. İlk olarak hızlı test
python main.py --url https://yeni-site.com --profile quick

# 2. Sonuçları incele (reports/ klasöründe)

# 3. Her şey yolundaysa, tam tarama yap
python main.py --url https://yeni-site.com
```

### Senaryo 2: E-Ticaret Sitesi Güvenlik Kontrolü
```bash
# Güvenlik odaklı tarama
python main.py --url https://alisveris-sitem.com --profile security --verbose
```

### Senaryo 3: Blog Sitesi SEO Analizi
```bash
# SEO ve performans testleri
python main.py --url https://blog-sitem.com --tests seo,performance
```

### Senaryo 4: Kurumsal Site Tam Denetim
```bash
# Her şeyi içeren kapsamlı tarama
python main.py --url https://kurumsal-site.com --verbose
```

---

## 📞 Yardım Alma

### Komut Satırı Yardımı
```bash
python main.py --help
```

### Kurulum Kontrolü
```bash
python verify_installation.py
```

### Test Çalıştırma
```bash
python test_system.py
```

### Dokümantasyon
- Bu dosya: `NASIL_KULLANILIR.md` (Türkçe, basit)
- Detaylı kılavuz: `USAGE_GUIDE.md` (İngilizce, teknik)
- Hızlı başlangıç: `QUICKSTART.md` (İngilizce)
- Sistem analizi: `SISTEM_ANALIZ_RAPORU.md` (Türkçe, detaylı)

---

## ⚠️ ÖNEMLİ UYARILAR

### Yasal Uyarı
**SADECE** sahip olduğunuz veya test etme yetkiniz olan siteleri tarayın. Yetkiniz olmayan siteleri test etmek **yasa dışıdır** ve ciddi sonuçları olabilir.

### İzin Alın
Test etmeden önce:
- ✅ Kendi sitenizse → Sorun yok
- ✅ Müşteri sitesiyse → Yazılı izin alın
- ✅ Test ortamıysa → Yetkililere bildirin
- ❌ Başkasının sitesiyse → TEST ETMEYİN!

---

## 🎉 Başlamaya Hazırsınız!

### En Basit Kullanım:

```bash
# 1. Kurulum
quick_setup.bat

# 2. Test
python main.py --url https://siteniz.com --profile quick

# 3. Sonuçları görüntüle
# reports/scan_TARIH_SAAT/report.html dosyasını açın
```

### İletişim ve Destek

- 📖 Detaylı dokümantasyon: `README.md`
- 🔧 Teknik detaylar: `ARCHITECTURE.md`
- 🚀 İleri seviye: `ADVANCED_FEATURES.md`
- 🇹🇷 Sistem analizi: `SISTEM_ANALIZ_RAPORU.md`

---

## 🎯 Sık Sorulan Sorular

**S: Tarama ne kadar sürer?**
C: Profil ve site boyutuna göre değişir:
- Quick: 1-3 dakika
- Security: 5-15 dakika
- Full: 15-45 dakika

**S: Ücretsiz mi?**
C: Evet, MIT lisanslı açık kaynak.

**S: Hangi siteleri test edebilirim?**
C: Sadece kendi sitenizi veya yetkiniz olan siteleri.

**S: Bulguların hepsi gerçek mi?**
C: Hayır, bazıları false positive olabilir. İnceleme gerekir.

**S: Kaç tane test var?**
C: 100+ test (güvenlik, performans, SEO, erişilebilirlik).

---

**🚀 İyi Testler! 🔒**

*Son güncelleme: 2025-10-23*
