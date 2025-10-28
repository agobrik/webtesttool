@echo off
chcp 65001 >nul
color 0B
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                  WebTestool - Hızlı Tarama                         ║
echo ║                  Test Sitesi: example.com                          ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Kullanıcıdan URL al
set /p URL="Taramak istediğiniz sitenin URL'sini girin (örn: https://example.com): "

if "%URL%"=="" (
    echo [HATA] URL girilmedi!
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    Tarama Profili Seçin                            ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo   1. Hızlı Test        (1-3 dakika, 10 sayfa, tüm testler)
echo   2. Güvenlik Taraması (5-15 dakika, sadece güvenlik testleri)
echo   3. Performans Testi  (3-8 dakika, hız ve yük testleri)
echo   4. Tam Tarama        (15-45 dakika, her şey)
echo.

set /p CHOICE="Seçiminiz (1-4): "

set PROFILE=quick
set PROFILE_NAME=Hızlı Test

if "%CHOICE%"=="2" (
    set PROFILE=security
    set PROFILE_NAME=Güvenlik Taraması
)
if "%CHOICE%"=="3" (
    set PROFILE=performance
    set PROFILE_NAME=Performans Testi
)
if "%CHOICE%"=="4" (
    set PROFILE=full
    set PROFILE_NAME=Tam Tarama
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo   📋 Tarama Özeti
echo   ─────────────────────────────────────────────────────────────────
echo   🌐 Hedef URL: %URL%
echo   🎯 Profil: %PROFILE_NAME%
echo   📁 Rapor Klasörü: reports\scan_TARIH_SAAT\
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

set /p CONFIRM="Taramayı başlatmak için ENTER'a basın (İptal için Ctrl+C)..."

echo.
echo [1/2] Python ve bağımlılıkları kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo Lütfen önce "quick_setup.bat" çalıştırın.
    pause
    exit /b 1
)

echo [2/2] Tarama başlatılıyor...
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

REM Taramayı başlat
python main.py --url "%URL%" --profile %PROFILE% --verbose

echo.
echo ════════════════════════════════════════════════════════════════════
echo.

if errorlevel 1 (
    echo ❌ Tarama tamamlandı ancak bulgular var!
    echo.
    echo 💡 Raporları incelemek için:
    echo    1. "reports" klasörünü açın
    echo    2. En son "scan_" klasörüne girin
    echo    3. "report.html" dosyasını tarayıcıda açın
    echo.
) else (
    echo ✅ Tarama başarıyla tamamlandı!
    echo.
    echo 💡 Raporları incelemek için:
    echo    1. "reports" klasörünü açın
    echo    2. En son "scan_" klasörüne girin
    echo    3. "report.html" dosyasını tarayıcıda açın
    echo.
)

echo Son tarama klasörünü açmak ister misiniz? (E/H)
set /p OPEN="Seçim: "

if /i "%OPEN%"=="E" (
    explorer reports
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo Teşekkürler! WebTestool kullandığınız için 🚀
echo ════════════════════════════════════════════════════════════════════
echo.

pause
