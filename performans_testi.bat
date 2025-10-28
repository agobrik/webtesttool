@echo off
chcp 65001 >nul
color 0E
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║             WebTestool - Performans ve Yük Testi                   ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Kullanıcıdan URL al
set /p URL="Test edilecek sitenin URL'sini girin: "

if "%URL%"=="" (
    echo [HATA] URL girilmedi!
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo   ⚡ Performans Testi Başlatılıyor
echo   ─────────────────────────────────────────────────────────────────
echo   🌐 Hedef: %URL%
echo.
echo   Yapılacak Testler:
echo   ✓ Sayfa yükleme hızı
echo   ✓ Response time (yanıt süresi)
echo   ✓ Yük testi (çoklu kullanıcı simülasyonu)
echo   ✓ Kaynak optimizasyonu (CSS, JS, resim)
echo   ✓ Önbellekleme kontrolü
echo   ✓ Sıkıştırma ayarları
echo.
echo   Tahmini Süre: 3-8 dakika
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

pause

echo Performans testi başlatılıyor...
echo.

python main.py --url "%URL%" --profile performance --verbose

echo.
echo ════════════════════════════════════════════════════════════════════
echo Performans testi tamamlandı!
echo ════════════════════════════════════════════════════════════════════
echo.

echo Rapor klasörünü açmak ister misiniz? (E/H)
set /p OPEN="Seçim: "

if /i "%OPEN%"=="E" (
    explorer reports
)

echo.
pause
