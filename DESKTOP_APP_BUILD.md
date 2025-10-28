# WebTestool Desktop App - Build Guide

Bu rehber, WebTestool Desktop uygulamasını standalone executable olarak derlemeyi anlatır.

## 📦 Gereksinimler

### Windows
- Python 3.10 veya üzeri
- PyInstaller
- (Opsiyonel) Inno Setup 6 - Windows installer için

### Linux/macOS
- Python 3.10 veya üzeri
- PyInstaller

## 🚀 Hızlı Başlangıç

### Windows'da Derleme

```bash
# 1. Geliştirme bağımlılıklarını kur
pip install -r requirements-dev.txt

# 2. Executable'ı derle
build_desktop.bat

# 3. (Opsiyonel) Windows installer oluştur
build_installer.bat
```

### Linux/macOS'ta Derleme

```bash
# 1. Geliştirme bağımlılıklarını kur
pip3 install -r requirements-dev.txt

# 2. Executable'ı derle
chmod +x build_desktop.sh
./build_desktop.sh
```

## 📂 Çıktı Dosyaları

### Executable (Tüm Platformlar)

Derleme sonrası:
```
dist/
└── WebTestool/
    ├── WebTestool.exe (Windows)
    ├── WebTestool (Linux/macOS)
    ├── config/
    ├── payloads/
    ├── reporters/
    │   └── templates/
    ├── data/ (boş klasör)
    ├── logs/ (boş klasör)
    ├── reports/ (boş klasör)
    ├── README.md
    └── LICENSE
```

### Windows Installer

Installer oluşturulduktan sonra:
```
installer_output/
└── WebTestool-2.0.0-Setup.exe
```

## 🔧 Manuel Derleme

### PyInstaller ile Derleme

```bash
# Önceki build'leri temizle
pyinstaller webtestool.spec --clean --noconfirm

# Gerekli klasörleri oluştur
mkdir dist/WebTestool/data
mkdir dist/WebTestool/logs
mkdir dist/WebTestool/reports
```

### Windows Installer Oluşturma

1. **Inno Setup'ı İndir ve Kur**
   - https://jrsoftware.org/isdl.php adresinden indirin
   - Varsayılan ayarlarla kurun

2. **Installer'ı Derle**
   ```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_windows.iss
   ```

## 🎯 Dağıtım

### Portable Sürüm (Zip)

```bash
# dist/WebTestool klasörünü zipleyın
# Kullanıcılar çıkarıp WebTestool.exe'yi çalıştırabilir
```

### Windows Installer

```bash
# installer_output/WebTestool-2.0.0-Setup.exe dosyasını dağıtın
# Kullanıcılar installer'ı çalıştırıp kurulum yapabilir
```

### macOS App Bundle

```bash
# build_desktop.sh çalıştırıldığında otomatik oluşturulur
# dist/WebTestool.app dosyası oluşur
# DMG oluşturmak için create-dmg kullanılabilir
```

## 📋 Dahil Edilen Dosyalar

PyInstaller spec dosyası (`webtestool.spec`) şu dosyaları paketler:

- **Config Files**: `config/` dizini
- **Payloads**: `payloads/` dizini
- **Templates**: `reporters/templates/` dizini
- **Dokümantasyon**: `README.md`, `LICENSE`

## 🐛 Sorun Giderme

### "Module not found" hatası

```bash
# Hidden imports'a ekleyin (webtestool.spec)
hiddenimports = [
    'eksik_modul_adi',
]
```

### "Permission denied" hatası (Linux/macOS)

```bash
chmod +x dist/WebTestool/WebTestool
```

### Playwright hatası

Executable çalıştırıldığında Playwright browser'ları kurmak gerekebilir:

```bash
playwright install chromium
```

### UPX hatası (Windows)

```bash
# UPX'i devre dışı bırakın
# webtestool.spec dosyasında:
upx=False
```

## 📊 Boyut Optimizasyonu

### Daha Küçük Executable

1. **Gereksiz modülleri exclude edin**:
   ```python
   # webtestool.spec
   excludes=['test', 'tests', 'pytest', ...],
   ```

2. **UPX compression kullanın**:
   ```python
   upx=True
   ```

3. **One-file mod yerine one-folder**:
   - Daha hızlı başlatma
   - Daha kolay debug

### Build Zamanını Azaltma

```bash
# --onedir kullanın (varsayılan)
# Incremental builds için build/ klasörünü sakklayın
```

## 🔐 Kod İmzalama (Opsiyonel)

### Windows

```bash
# Code signing certificate ile imzalayın
signtool sign /f certificate.pfx /p password WebTestool.exe
```

### macOS

```bash
# Apple Developer Certificate ile imzalayın
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application" WebTestool.app
```

## 📝 Build Süreci Detayları

### 1. Analysis Phase
- Tüm imports analiz edilir
- Dependencies bulunur
- Hidden imports eklenir

### 2. Collection Phase
- Binary dosyalar toplanır
- Data files kopyalanır
- Python kütüphaneleri paketlenir

### 3. Bundling Phase
- Executable oluşturulur
- Compression uygulanır
- Metadata eklenir

### 4. Verification
- Executable test edilir
- Dependencies kontrol edilir

## 🎨 Özelleştirme

### Icon Değiştirme

```python
# webtestool.spec
icon='assets/custom_icon.ico'  # Windows
icon='assets/custom_icon.icns' # macOS
```

### Uygulama Bilgileri (Windows)

```python
exe = EXE(
    ...
    version='version_info.txt',  # Version information file
)
```

### macOS Bundle Info

```python
app = BUNDLE(
    ...
    info_plist={
        'CFBundleName': 'WebTestool',
        'CFBundleDisplayName': 'WebTestool',
        'CFBundleIdentifier': 'com.webtestool.app',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
    },
)
```

## 📚 Kaynaklar

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [Flet Packaging Guide](https://flet.dev/docs/guides/python/packaging)

## 💡 İpuçları

1. **Test Edin**: Her platform için ayrı test edin
2. **Dependencies**: Minimal tutun
3. **Size**: Gereksiz dosyaları exclude edin
4. **Security**: Sensitive data'yı include etmeyin
5. **Updates**: Auto-update mekanizması ekleyin (gelecek)

## 🔄 CI/CD Entegrasyonu

GitHub Actions ile otomatik build:

```yaml
- name: Build Desktop App
  run: |
    pip install -r requirements-dev.txt
    pyinstaller webtestool.spec --clean --noconfirm

- name: Upload Artifact
  uses: actions/upload-artifact@v4
  with:
    name: WebTestool-${{ matrix.os }}
    path: dist/WebTestool
```

## 📞 Destek

Sorunlarla karşılaşırsanız:
- GitHub Issues: https://github.com/agobrik/webtesttool/issues
- Documentation: README.md
