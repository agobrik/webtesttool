"""
Kurulum Dogrulama Script'i
Tum bagimliliklarin dogru yuklendigini kontrol eder
"""

import sys

def check_import(module_name, package_name=None):
    """Modulu import etmeyi dene"""
    try:
        __import__(module_name)
        print(f"[OK] {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {package_name or module_name} - HATA: {e}")
        return False

print("=" * 60)
print("WEBTESTOOL - KURULUM DOGRULAMA")
print("=" * 60)

print("\nTEMEL BAGIMLILIKLAR:")
results = []
results.append(check_import("playwright", "Playwright"))
results.append(check_import("httpx", "HTTPX"))
results.append(check_import("aiohttp", "AioHTTP"))
results.append(check_import("bs4", "BeautifulSoup4"))
results.append(check_import("lxml", "LXML"))
results.append(check_import("sqlalchemy", "SQLAlchemy"))
results.append(check_import("yaml", "PyYAML"))
results.append(check_import("pydantic", "Pydantic"))
results.append(check_import("tqdm", "TQDM"))
results.append(check_import("loguru", "Loguru"))
results.append(check_import("rich", "Rich"))
results.append(check_import("click", "Click"))
results.append(check_import("jinja2", "Jinja2"))

print("\nTEST BAGIMLILIKLARI:")
results.append(check_import("pytest", "Pytest"))
results.append(check_import("pytest_asyncio", "Pytest-Asyncio"))
results.append(check_import("pytest_cov", "Pytest-Cov"))
results.append(check_import("pytest_xdist", "Pytest-XDist"))
results.append(check_import("pytest_mock", "Pytest-Mock"))
results.append(check_import("coverage", "Coverage"))

print("\nMONITORING BAGIMLILIKLARI:")
results.append(check_import("fastapi", "FastAPI"))
results.append(check_import("uvicorn", "Uvicorn"))
results.append(check_import("psutil", "PSUtil"))

print("\n" + "=" * 60)
success_count = sum(results)
total_count = len(results)

if success_count == total_count:
    print(f"BASARILI! TUM BAGIMLILIKLAR YUKLENDI! ({success_count}/{total_count})")
    print("=" * 60)
    print("\nSISTEM KULLANIMA HAZIR!")
    print("\nSonraki adim:")
    print("   python main.py --url https://example.com --profile quick")
    sys.exit(0)
else:
    print(f"UYARI! BAZI BAGIMLILIKLAR EKSIK: {success_count}/{total_count}")
    print("=" * 60)
    print("\nLutfen eksik paketleri yukleyin:")
    print("   pip install -r requirements.txt")
    print("   pip install -r requirements-test.txt")
    sys.exit(1)
