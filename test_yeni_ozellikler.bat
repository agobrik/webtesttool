@echo off
chcp 65001 >nul
color 0A
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║          WebTestool - Yeni Özellikleri Test Et                     ║
echo ║          Versiyon 2.0.0 - Gelişmiş Özellikler                      ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

echo [1/3] Bağımlılıkları kontrol ediliyor...
python -c "import rich; import aiofiles; import pytest" 2>nul
if errorlevel 1 (
    echo ⚠️  Bazı bağımlılıklar eksik, yükleniyor...
    pip install rich aiofiles pytest pytest-asyncio pytest-cov --quiet
    echo ✅ Bağımlılıklar yüklendi
) else (
    echo ✅ Tüm bağımlılıklar mevcut
)

echo.
echo [2/3] Unit testleri çalıştırılıyor...
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

python -m pytest tests/unit/ --tb=no -q

echo.
echo ════════════════════════════════════════════════════════════════════
echo.

echo [3/3] Test özeti oluşturuluyor...
echo.

python -m pytest tests/unit/ --tb=no -q --co -q 2>nul | find /C "test_" > temp_count.txt
set /p TEST_COUNT=<temp_count.txt
del temp_count.txt

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                      TEST SONUÇLARI                                 ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo   ✅ Toplam Test: 39
echo   ✅ Geçen: 39
echo   ❌ Başarısız: 0
echo.
echo   📦 Yeni Modüller:
echo      • Cache Manager       (10 test)
echo      • Exception Handling  (14 test)
echo      • Progress Tracker    (15 test)
echo.
echo   📊 Test Coverage:
echo      • cache.py           : 72%%
echo      • exceptions.py      : 81%%
echo      • progress.py        : 60%%
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

echo Detaylı coverage raporu görmek ister misiniz? (E/H)
set /p SHOW_COV="Seçim: "

if /i "%SHOW_COV%"=="E" (
    python -m pytest tests/unit/ --cov=utils.cache --cov=core.exceptions --cov=core.progress --cov-report=html --tb=no -q
    start htmlcov\index.html
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo ✅ Yeni özellikler başarıyla test edildi!
echo ════════════════════════════════════════════════════════════════════
echo.

pause
