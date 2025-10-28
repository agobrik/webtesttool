@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                  WebTestool - Rapor Görüntüle                      ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM En son rapor klasörünü bul
for /f "delims=" %%i in ('dir /b /ad /o-d reports\scan_* 2^>nul') do (
    set LATEST=%%i
    goto :found
)

echo [HATA] Henüz hiç tarama yapılmamış!
echo.
echo Önce bir tarama yapmalısınız:
echo   - tarama_yap.bat
echo   - guvenlik_taramasi.bat
echo   - performans_testi.bat
echo.
pause
exit /b 1

:found
echo Son tarama raporu: reports\%LATEST%
echo.

REM HTML raporunu aç
if exist "reports\%LATEST%\report.html" (
    echo HTML raporu tarayıcıda açılıyor...
    start "" "reports\%LATEST%\report.html"
    timeout /t 2 /nobreak >nul
) else (
    echo [HATA] HTML raporu bulunamadı!
)

REM Klasörü Explorer'da aç
echo Rapor klasörü açılıyor...
explorer "reports\%LATEST%"

echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo Rapor dosyaları:
echo   📄 report.html  - Detaylı görsel rapor (tarayıcıda)
echo   💾 report.json  - Makine okunabilir rapor
echo   📝 summary.txt  - Hızlı metin özeti
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

pause
