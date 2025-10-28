# 🎯 WebTestool - Başlamak İçin İlk Adımlar

**Hoş Geldiniz!** Bu dosya, WebTestool'u hızlıca kullanmaya başlamanız için hazırlandı.

---

## 🚀 Hemen Başla (3 Adım)

### 1️⃣ Kurulum (İlk Kez - Sadece 1 Defa)

Projenin bulunduğu klasörde aşağıdaki dosyayı çalıştırın:

```
quick_setup.bat    ← Buna çift tıklayın!
```

Bu script:
- ✅ Python bağımlılıklarını yükler
- ✅ Playwright tarayıcıları kurar
- ✅ Gerekli klasörleri oluşturur
- ✅ Kurulumu doğrular

**Süre:** 3-5 dakika

---

### 2️⃣ İlk Taramanızı Yapın

Kurulum bittikten sonra aşağıdaki dosyayı çalıştırın:

```
tarama_yap.bat    ← Buna çift tıklayın!
```

Size şunlar sorulacak:
- 🌐 Hangi siteyi test etmek istiyorsunuz? (URL)
- 🎯 Hangi profili seçmek istiyorsunuz? (Hızlı/Güvenlik/Performans/Tam)

Script size rehberlik edecek!

---

### 3️⃣ Sonuçları İnceleyin

Tarama bittiğinde aşağıdaki dosyayı çalıştırın:

```
rapor_ac.bat    ← Buna çift tıklayın!
```

Bu script:
- 📊 En son raporu tarayıcıda açar
- 📁 Rapor klasörünü gösterir
- 📄 Tüm rapor dosyalarını listeler

---

## 📁 Hazır Scriptler

Artık kullanıma hazır 5 adet kolay script hazırlandı:

| Script | Ne Yapar? | Ne Zaman Kullanılır? |
|--------|-----------|----------------------|
| **quick_setup.bat** | Kurulum yapar | İlk kez (1 defa) |
| **tarama_yap.bat** | Genel tarama menüsü | Her tarama için |
| **guvenlik_taramasi.bat** | Güvenlik testleri | Güvenlik kontrolü |
| **performans_testi.bat** | Hız ve yük testleri | Performans analizi |
| **rapor_ac.bat** | En son raporu açar | Rapor görüntüleme |

---

## 📚 Dokümantasyon Dosyaları

Sistemi anlamak ve kullanmak için hazırlanmış dosyalar:

### 🇹🇷 Türkçe Dokümantasyon (YENİ!)

1. **BASLAMAK_ICIN.md** (BU DOSYA)
   - İlk adımlar
   - En basit kullanım
   - **🔰 BURADAN BAŞLAYIN!**

2. **NASIL_KULLANILIR.md** (YENİ!)
   - Basit kullanım kılavuzu
   - Adım adım örnekler
   - Sorun giderme
   - **👉 İLK OKUMA İÇİN İDEAL**

3. **SISTEM_ANALIZ_RAPORU.md**
   - Sistem nedir, ne yapar?
   - Nasıl çalışır?
   - Detaylı mimari
   - **📖 SİSTEMİ ANLAMAK İÇİN**

4. **IYILESTIRME_OZETI.md** (YENİ!)
   - Öncelikli iyileştirmeler
   - Kısa vadeli öneriler
   - ROI analizi
   - **💡 GELİŞTİRME İÇİN**

5. **GELISTIRME_ONERILERI_RAPORU.md**
   - Detaylı teknik öneriler
   - Kod örnekleri (2010 satır)
   - Mimari tasarımlar
   - **🔧 DETAYLI TEKNİK BİLGİ**

### 🇬🇧 İngilizce Dokümantasyon

- **README.md** - Genel bakış
- **QUICKSTART.md** - Hızlı başlangıç
- **USAGE_GUIDE.md** - Detaylı kullanım
- **ARCHITECTURE.md** - Mimari detayları
- **ADVANCED_FEATURES.md** - İleri özellikler

---

## ⚡ Hızlı Kullanım Örnekleri

### Örnek 1: Hızlı Test (1-3 dakika)
```batch
python main.py --url https://siteniz.com --profile quick
```

### Örnek 2: Güvenlik Taraması (5-15 dakika)
```batch
python main.py --url https://siteniz.com --profile security
```

### Örnek 3: Performans Testi (3-8 dakika)
```batch
python main.py --url https://siteniz.com --profile performance
```

### Örnek 4: Tam Tarama (15-45 dakika)
```batch
python main.py --url https://siteniz.com
```

**💡 İpucu:** İlk testinizi `--profile quick` ile yapın!

---

## 🎨 WebTestool Ne Yapar?

### 🔒 Güvenlik Testleri (30+ test)
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF
- SSL/TLS
- Güvenlik başlıkları
- Ve daha fazlası...

### ⚡ Performans Testleri
- Sayfa yükleme hızı
- Yük testi (çoklu kullanıcı)
- Kaynak optimizasyonu
- Önbellekleme kontrolü

### 📈 SEO Testleri (40+ kontrol)
- Meta etiketler
- Başlıklar yapısı
- Resim optimizasyonu
- Mobil uyumluluk
- Sitemap kontrolü

### ♿ Erişilebilirlik Testleri
- WCAG 2.1 uyumluluk
- Engelli kullanıcı desteği
- Klavye navigasyonu
- Renk kontrastı

---

## 📊 Rapor Dosyaları

Her tarama sonrası `reports/scan_TARIH_SAAT/` klasöründe:

- **report.html** 📄 → Görsel, detaylı (tarayıcıda açın!)
- **report.json** 💾 → Makine okunabilir
- **summary.txt** 📝 → Hızlı metin özeti

**En İyisi:** `report.html` dosyasını tarayıcıda açın!

---

## 🔍 Bulgu Seviyeleri

Raporlarda bulgular önem sırasına göre gösterilir:

| Seviye | Açıklama | Ne Yapmalı? |
|--------|----------|-------------|
| 🔴 **Critical** | Çok ciddi | HEMEN düzeltin! |
| 🟠 **High** | Önemli | En kısa sürede düzeltin |
| 🟡 **Medium** | Orta | Yakında düzeltin |
| 🟢 **Low** | Küçük | Fırsat buldukça |
| 🔵 **Info** | Bilgi | İnceleme için |

---

## ⚙️ Gelişmiş Özellikler

### Şifre/Giriş Gerektiren Siteler

`ayarlar.yaml` dosyası oluşturun:

```yaml
target:
  url: "https://siteniz.com"
  auth:
    type: "basic"
    username: "kullanici_adi"
    password: "sifre"
```

Kullanım:
```batch
python main.py --url https://siteniz.com --config ayarlar.yaml
```

### Özelleştirilmiş Testler

```batch
# Sadece güvenlik ve performans testleri
python main.py --url https://siteniz.com --tests security,performance

# Detaylı log göster
python main.py --url https://siteniz.com --verbose

# Özel klasöre rapor kaydet
python main.py --url https://siteniz.com --output ./raporlarim
```

---

## 🐛 Sorun Giderme

### Python bulunamadı?
- [python.org](https://python.org)'dan Python 3.11+ indirin
- Kurulumda "Add Python to PATH" seçeneğini işaretleyin

### Playwright tarayıcıları yok?
```batch
python -m playwright install
```

### Tarama çok yavaş?
```batch
# Hızlı profil kullanın
python main.py --url https://siteniz.com --profile quick
```

### Çok fazla hatalı bulgu?
- Agresif modu kapatın (config dosyasında)
- Bulguları manuel olarak doğrulayın

---

## ⚠️ ÖNEMLİ UYARILAR

### 🚫 Yasal Uyarı
**SADECE kendi sitenizi veya yetkiniz olan siteleri test edin!**

Başkasının sitesini izinsiz test etmek:
- ❌ Yasa dışıdır
- ❌ Ceza alabilirsiniz
- ❌ Hukuki sorun yaşarsınız

### ✅ İzin Alın
- Kendi siteniz → ✅ Sorun yok
- Müşteri sitesi → ✅ Yazılı izin alın
- Başkasının sitesi → ❌ TEST ETMEYİN!

---

## 💡 İpuçları

### ✅ YAPILMASI GEREKENLER
1. ✅ İlk testinizi `--profile quick` ile yapın
2. ✅ Raporları HTML formatında inceleyin
3. ✅ Bulguları doğrulayın (false positive olabilir)
4. ✅ Düzenli taramalar yapın
5. ✅ SADECE yetkiniz olan siteleri test edin

### ❌ YAPILMAMASI GEREKENLER
1. ❌ Yetkiniz olmayan siteleri test etmeyin
2. ❌ Tüm bulguları gerçek sanmayın
3. ❌ Üretim ortamında agresif testler yapmayın
4. ❌ Test sonuçlarını herkesle paylaşmayın

---

## 📱 Kullanım Senaryoları

### Senaryo 1: Yeni Site Kontrolü
```
1. quick_setup.bat       (ilk kez)
2. tarama_yap.bat        (hızlı profil seç)
3. rapor_ac.bat          (sonuçları incele)
4. Sorun varsa düzelt
5. tarama_yap.bat        (tam tarama yap)
```

### Senaryo 2: Güvenlik Denetimi
```
1. guvenlik_taramasi.bat (çalıştır)
2. rapor_ac.bat          (kritik bulguları incele)
3. Sorunları düzelt
4. Tekrar test et
```

### Senaryo 3: Performans Optimizasyonu
```
1. performans_testi.bat  (çalıştır)
2. rapor_ac.bat          (yavaş sayfaları bul)
3. Optimizasyon yap
4. Tekrar test et ve karşılaştır
```

---

## 📚 Daha Fazla Bilgi

### Sıradaki Okumalar
1. ✅ Bu dosya → **Başladınız!** 🎉
2. → `NASIL_KULLANILIR.md` → Detaylı kullanım
3. → `SISTEM_ANALIZ_RAPORU.md` → Sistem nasıl çalışır?
4. → `IYILESTIRME_OZETI.md` → Geliştirme fırsatları

### Komut Satırı Yardımı
```batch
python main.py --help
```

### Kurulum Doğrulama
```batch
python verify_installation.py
```

### Test Çalıştırma
```batch
python test_system.py
```

---

## 🎯 Özet: 3 Basit Adım

```
1️⃣  quick_setup.bat       → Kurulum (ilk kez)
           ↓
2️⃣  tarama_yap.bat        → Test yap (her zaman)
           ↓
3️⃣  rapor_ac.bat          → Sonuçları gör (her zaman)
```

**Hepsi bu kadar! 🎉**

---

## 🆘 Yardım

Sorun mu yaşıyorsunuz?

1. `NASIL_KULLANILIR.md` dosyasına bakın (Sorun Giderme bölümü)
2. `python verify_installation.py` çalıştırın
3. `python main.py --help` komutunu deneyin
4. GitHub Issues'da sorun bildirin

---

## 🎉 Başlamaya Hazırsınız!

Artık WebTestool'u kullanmaya hazırsınız.

**İlk adım:**
```
quick_setup.bat  ← ÇİFT TIKLAYIN!
```

**Daha sonra:**
```
tarama_yap.bat   ← İLK TESTİNİZİ YAPIN!
```

---

**İyi Testler! 🚀🔒**

*Hazırlayan: AI Sistem Analiz Asistanı*
*Tarih: 2025-10-23*
