@echo off
chcp 65001 >nul
color 0C
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║               WebTestool - Güvenlik Taraması                       ║
echo ║              OWASP Top 10 + 20 Ek Güvenlik Testi                   ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Kullanıcıdan URL al
set /p URL="Taramak istediğiniz sitenin URL'sini girin: "

if "%URL%"=="" (
    echo [HATA] URL girilmedi!
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo   🔒 Güvenlik Taraması Başlatılıyor
echo   ─────────────────────────────────────────────────────────────────
echo   🌐 Hedef: %URL%
echo.
echo   Yapılacak Testler:
echo   ✓ SQL Injection (4 çeşit)
echo   ✓ Cross-Site Scripting (XSS)
echo   ✓ CSRF
echo   ✓ XXE
echo   ✓ SSRF
echo   ✓ Command Injection
echo   ✓ Path Traversal
echo   ✓ Security Headers
echo   ✓ SSL/TLS
echo   ✓ CORS
echo   ✓ Cookie Security
echo   ✓ ve daha fazlası...
echo.
echo   Tahmini Süre: 5-15 dakika
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

pause

echo Güvenlik taraması başlatılıyor...
echo.

python main.py --url "%URL%" --profile security --verbose

echo.
echo ════════════════════════════════════════════════════════════════════
echo.

if errorlevel 1 (
    echo ⚠️  GÜVENLİK SORUNLARI TESPİT EDİLDİ!
    echo.
    echo    Kritik ve yüksek seviye bulgular var.
    echo    Lütfen raporları acilen inceleyin!
    echo.
) else (
    echo ✅ Tarama tamamlandı!
    echo.
    echo    Detaylı rapor için HTML dosyasını açın.
    echo.
)

echo Rapor klasörünü açmak ister misiniz? (E/H)
set /p OPEN="Seçim: "

if /i "%OPEN%"=="E" (
    explorer reports
)

echo.
pause
