# 🔐 WebTestool Authentication Guide

Bu rehber, WebTestool'da authentication ve login yönetimini açıklar.

## 📖 İçindekiler

- [Neden Authentication Gerekli?](#neden-authentication-gerekli)
- [Desteklenen Authentication Yöntemleri](#desteklenen-authentication-yöntemleri)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Desktop App ile Login](#desktop-app-ile-login)
- [CLI ile Login](#cli-ile-login)
- [Session Yönetimi](#session-yönetimi)
- [Gelişmiş Kullanım](#gelişmiş-kullanım)
- [Sorun Giderme](#sorun-giderme)

---

## Neden Authentication Gerekli?

Birçok web sitesi içeriğine erişmek için giriş yapmayı gerektirir:

- 🔒 **Korumalı İçerik**: Admin panelleri, kullanıcı profilleri
- 🏢 **Kurumsal Uygulamalar**: Intranet siteleri, CRM sistemleri
- 🛒 **E-ticaret**: Alışveriş sepeti, sipariş geçmişi
- 📱 **Sosyal Medya**: Kullanıcı feed'leri, mesajlaşma
- 📊 **Dashboard'lar**: Analytics, raporlama araçları

**Authentication olmadan:**
- ❌ Tarama sadece public sayfalarda kalır
- ❌ Önemli sayfalar görülemez
- ❌ Form testleri yapılamaz
- ❌ Güvenlik testleri sınırlı olur

**Authentication ile:**
- ✅ Tüm sayfalara erişim
- ✅ Kapsamlı güvenlik testleri
- ✅ Gerçekçi kullanıcı deneyimi testi
- ✅ Daha detaylı raporlar

---

## Desteklenen Authentication Yöntemleri

### 1. 🤖 Automatic Login (Playwright)
Tarayıcı otomasyonu ile otomatik giriş yapma.

**Avantajlar:**
- Tamamen otomatik
- CSRF token desteği
- JavaScript yürütme
- Session cookie'leri otomatik kaydedilir

**Kullanım:**
```bash
# CLI
python -m cli.login_cli login auto --url https://example.com/login \
  --username user@example.com --password mypassword

# Desktop App
Settings > Authentication > Configure Login > Automatic Login
```

### 2. 🌐 Interactive Login
Tarayıcıyı açar, kullanıcı manuel giriş yapar.

**Ne Zaman Kullanılır:**
- CAPTCHA var
- 2FA/MFA gerekli
- OAuth providers (Google, Facebook, etc.)
- Karmaşık login flow'lar

**Kullanım:**
```bash
# CLI
python -m cli.login_cli login interactive --url https://example.com/login

# Desktop App
Settings > Authentication > Interactive Login
```

### 3. 🔑 API Token / Bearer Token
API tabanlı authentication.

**Kullanım:**
```python
# Config dosyasında
auth:
  type: bearer
  token: "your_api_token_here"
```

### 4. 🔐 HTTP Basic/Digest Auth
Klasik HTTP authentication.

**Kullanım:**
```python
# Config dosyasında
auth:
  type: basic
  username: "admin"
  password: "password"
```

### 5. 🍪 Cookie Import
Tarayıcıdan cookie'leri import etme.

**Kullanım:**
```bash
# Export cookies from browser (using extension)
# Import to WebTestool
python -m cli.login_cli login import-cookies cookies.json
```

---

## Hızlı Başlangıç

### Senaryo: E-ticaret Sitesi Taraması

```bash
# 1. Login yapılandır
python -m cli.login_cli login configure \
  --url https://shop.example.com/login \
  --username customer@email.com \
  --password MySecurePass123 \
  --auto

# 2. Session kaydedildi! Şimdi tarama yap
python main.py --url https://shop.example.com --use-session

# Session otomatik kullanılacak ve tüm sayfalara erişilecek!
```

---

## Desktop App ile Login

### Adım 1: Login Dialog'u Aç

1. Desktop app'i başlat
2. **Settings** sekmesine git
3. **Authentication** bölümünü bul
4. **Configure Login** butonuna tıkla

### Adım 2: Credentials Gir

**Temel Bilgiler:**
- **Login URL**: Giriş sayfasının URL'i
  ```
  https://example.com/login
  ```

- **Username/Email**: Kullanıcı adı veya email
  ```
  user@example.com
  ```

- **Password**: Şifreniz
  ```
  ********
  ```

### Adım 3: Login Yöntemini Seç

#### Option A: Automatic Login
- **"Automatic Login"** butonuna tıklayın
- Sistem otomatik giriş yapacak
- 5-10 saniye bekleyin
- ✅ "Login successful!" mesajını görün

#### Option B: Interactive Login
- **"Interactive Login"** butonuna tıklayın
- Tarayıcı açılacak
- Manuel olarak giriş yapın (CAPTCHA, 2FA vb. için)
- Giriş tamamlandığında ENTER'a basın
- ✅ Session kaydedildi!

### Adım 4: Scan Yap

- **New Scan** sekmesine git
- URL gir
- **"Use Saved Session"** seçeneğini işaretle
- **Start Scan** yap!

---

## CLI ile Login

### 1. Configuration

```bash
# Interactive konfigürasyon
python -m cli.login_cli login configure

# Non-interactive
python -m cli.login_cli login configure \
  --url https://example.com/login \
  --username user@example.com \
  --password mypassword
```

### 2. Automatic Login

```bash
# Saved configuration kullanarak
python -m cli.login_cli login auto

# Direct credentials ile
python -m cli.login_cli login auto \
  --url https://example.com/login \
  --username user@example.com \
  --password mypassword

# Visible browser ile (debugging için)
python -m cli.login_cli login auto --no-headless
```

### 3. Interactive Login

```bash
# CAPTCHA/2FA için
python -m cli.login_cli login interactive
```

### 4. Session Management

```bash
# Tüm session'ları listele
python -m cli.login_cli login list

# Session geçerliliğini kontrol et
python -m cli.login_cli login verify

# Session sil
python -m cli.login_cli login delete session_name

# Tüm session'ları sil
python -m cli.login_cli login delete --all

# Cookie'leri export et
python -m cli.login_cli login export-cookies my_cookies.json
```

---

## Session Yönetimi

### Session Nedir?

Login yaptıktan sonra, tarayıcı cookies ve authentication state'i kaydedilir. Bu session, gelecekteki taramalarda tekrar login yapmadan kullanılır.

### Session Dosyaları

```
data/
└── sessions/
    ├── https_example_com_login.json
    ├── https_shop_example_com_login.json
    └── https_admin_example_com_login.json
```

Her session içerir:
- 🍪 Cookies
- 🔑 Authentication tokens
- 📦 localStorage/sessionStorage data
- ⏰ Timestamp

### Session Lifecycle

1. **Create**: Login yapıldığında otomatik oluşturulur
2. **Store**: `data/sessions/` klasöründe saklanır
3. **Reuse**: Taramalarda otomatik kullanılır
4. **Expire**: 24 saat sonra uyarı verir (ama çalışmaya devam eder)
5. **Delete**: Manuel veya otomatik silinebilir

### Best Practices

✅ **DO:**
- Session'ları düzenli kontrol edin
- Expired session'ları silin
- Güvenli şifreler kullanın
- Session dosyalarını git'e commit etmeyin

❌ **DON'T:**
- Session'ları public yerlerde paylaşmayın
- Aynı session'ı production'da kullanmayın
- Session dosyalarını email ile göndermeyin

---

## Gelişmiş Kullanım

### Custom Selectors

Form element'leri standart değilse, custom CSS selectors kullanın:

```python
config = {
    'login_url': 'https://custom-site.com/signin',
    'username': 'user@example.com',
    'password': 'password',
    'username_selector': '#user-email-input',  # Custom selector
    'password_selector': 'input[data-test="password"]',
    'submit_selector': 'button.login-btn',
    'success_indicator': '.user-dashboard',  # Check this element after login
}
```

### Success Verification

Login başarısını doğrulamak için:

**URL-based:**
```python
'success_indicator': 'https://example.com/dashboard'
```

**Element-based:**
```python
'success_indicator': '.user-menu, #profile-dropdown'
```

### Multiple Accounts

Farklı siteler için farklı session'lar:

```bash
# Site 1
python -m cli.login_cli login configure \
  --url https://site1.com/login --username user1 --password pass1 --auto

# Site 2
python -m cli.login_cli login configure \
  --url https://site2.com/login --username user2 --password pass2 --auto

# Her site için ayrı session kaydedilir
```

### Programmatic Usage

Python kodunuzda kullanma:

```python
from core.login_automation import LoginAutomation
import asyncio

async def login_and_scan():
    # Login
    config = {
        'login_url': 'https://example.com/login',
        'username': 'user@example.com',
        'password': 'password123',
    }

    login_automation = LoginAutomation(config)
    success = await login_automation.perform_login(headless=True)

    if success:
        print("✅ Login successful!")

        # Get cookies for httpx/aiohttp
        cookies = login_automation.export_cookies_for_httpx()

        # Use cookies in your scan
        # ... your scan code ...

asyncio.run(login_and_scan())
```

---

## Sorun Giderme

### Problem: "Login failed"

**Nedenleri:**
1. Yanlış credentials
2. CAPTCHA var
3. 2FA/MFA gerekli
4. Wrong selectors
5. JavaScript heavy site

**Çözümler:**
```bash
# 1. Credentials'ı kontrol et
python -m cli.login_cli login configure --url ... --username ... --password ...

# 2. Interactive mode kullan (CAPTCHA/2FA için)
python -m cli.login_cli login interactive

# 3. Visible browser ile test et
python -m cli.login_cli login auto --no-headless

# 4. Custom selectors kullan (Desktop app > Show Advanced Options)
```

### Problem: "Session expired"

**Çözüm:**
```bash
# Session'ı sil ve tekrar login yap
python -m cli.login_cli login delete session_name
python -m cli.login_cli login auto
```

### Problem: "Element not found"

**Nedenleri:**
- Form element'leri standart değil
- JavaScript ile yükleniyor
- Shadow DOM kullanılıyor

**Çözümler:**
```python
# Desktop app'te "Show Advanced Options" ile custom selectors gir
username_selector: '#email-field'  # F12 ile inspect edip bulun
password_selector: '[data-qa="password-input"]'
submit_selector: 'button[aria-label="Sign in"]'
```

### Problem: "Cookies not persisting"

**Çözüm:**
```bash
# Session dosyasını kontrol et
ls -la data/sessions/

# Verify session
python -m cli.login_cli login verify

# Re-login
python -m cli.login_cli login auto
```

---

## 🔒 Security Best Practices

### 1. Credential Storage

❌ **Kötü:**
```python
# Kod içinde hardcode
password = "MyPassword123"
```

✅ **İyi:**
```python
# Environment variable
import os
password = os.getenv('SCAN_PASSWORD')
```

✅ **Daha İyi:**
```bash
# CLI'da prompt
python -m cli.login_cli login configure  # Interaktif prompt
```

### 2. Session Files

```bash
# .gitignore dosyasına ekleyin
data/sessions/
*.session
```

### 3. Test Accounts

- Production credentials kullanmayın
- Test account'ları kullanın
- Sınırlı yetkili hesaplar kullanın

---

## 📝 Examples

### Example 1: WordPress Site

```bash
python -m cli.login_cli login configure \
  --url https://mysite.com/wp-login.php \
  --username admin \
  --password MyWPPass123 \
  --auto

# Scan with authentication
python main.py --url https://mysite.com --use-session --profile full
```

### Example 2: SPA with OAuth

```bash
# Interactive login gerekli (Google/Facebook login için)
python -m cli.login_cli login interactive \
  --url https://app.example.com/login

# Browser açılır, manuel login yapın
# Session kaydedilir

# Scan
python main.py --url https://app.example.com --use-session
```

### Example 3: Admin Panel

```bash
# Desktop App kullanın
# 1. Settings > Authentication > Configure Login
# 2. URL: https://admin.example.com/login
# 3. Username: admin@company.com
# 4. Password: ********
# 5. Automatic Login
# 6. New Scan > Use Saved Session > Start
```

---

## 🎯 Tips & Tricks

1. **Always Test First**: İlk login'i interactive mode ile yapın
2. **Check Selectors**: F12 Developer Tools ile element'leri inspect edin
3. **Use Sessions**: Session'ları tekrar kullanın, her seferinde login yapmayın
4. **Verify Regularly**: Session'ları düzenli verify edin
5. **Clean Up**: Eski session'ları silin

---

## 📚 Kaynaklar

- [Playwright Authentication](https://playwright.dev/docs/auth)
- [Session Management Best Practices](https://owasp.org/www-community/Session_Management)
- [WebTestool Documentation](README.md)

---

## 💡 FAQ

**Q: Tüm siteler için aynı session kullanılır mı?**
A: Hayır, her site için ayrı session dosyası oluşturulur.

**Q: Session ne kadar geçerli?**
A: Sitenin session timeout politikasına bağlı. Genelde 24 saat.

**Q: CAPTCHA'lı sitelerde ne yapmalıyım?**
A: Interactive mode kullanın, manuel çözün.

**Q: 2FA/MFA destekleniyor mu?**
A: Evet, interactive mode ile. Browser açılır, 2FA kodunu girersiniz.

**Q: Session güvenli mi?**
A: Evet, local'de saklanır. Ama hassas dosyalardır, paylaşmayın.

---

**🎉 Authentication sistemi hazır! Artık korumalı siteleri tarayabilirsiniz!**
