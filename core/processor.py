import os
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup

KEYWORDS = ["password", "admin", "config", "db_password", "api_key", "secret", "login"]


async def process_target(context, subdomain, scan_dir, target_domain):
    url = f"http://{subdomain}"
    page = await context.new_page()

    await page.set_extra_http_headers({"Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"})

    safe_name = subdomain.replace("://", "_").replace("/", "_")
    ss_path = os.path.abspath(os.path.join(scan_dir, "screenshots", f"{safe_name}.png"))

    status = "Success"
    status_code = "N/A"
    found_words = []

    print(f"[*] İşleniyor: {url}")

    try:
        response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        if response:
            status_code = response.status
    except TimeoutError:
        status = "Timeout (Kısmen Yüklendi)"
    except Exception as e:
        # HATA GİZLEMEYİ KALDIRDIK! Artık Playwright'ın gerçek hatasını göreceğiz.
        hata_mesaji = str(e).split('\n')[0]  # Hatanın sadece ilk satırını al
        status = f"Bağlantı Koptu: {hata_mesaji}"
        print(f"[!] {subdomain} için bağlantı koptu: {hata_mesaji}")
        await page.close()
        return {"subdomain": subdomain, "status": status, "found_keywords": []}

    try:
        await page.wait_for_timeout(2000)
        await page.screenshot(path=ss_path, full_page=False)

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        text_content = soup.get_text().lower()

        found_words = [word for word in KEYWORDS if word in text_content]

        if subdomain == target_domain:
            html_path = os.path.join(scan_dir, f"{target_domain}_kaynak_kodu.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"    [+] Ana domain HTML kodu kaydedildi!")

    except Exception as e:
        status = f"İşlem Hatası: SS veya Kayıt yapılamadı."

    finally:
        await page.close()

    return {
        "subdomain": subdomain,
        "status": status,
        "status_code": status_code,
        "found_keywords": found_words
    }


async def run_scanner(subdomain_list, scan_dir, target_domain):
    abs_scan_dir = os.path.abspath(scan_dir)
    screenshots_dir = os.path.join(abs_scan_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        semaphore = asyncio.Semaphore(3)

        async def sem_process(sub):
            async with semaphore:
                return await process_target(context, sub, abs_scan_dir, target_domain)

        tasks = [sem_process(sub) for sub in subdomain_list]
        results = await asyncio.gather(*tasks)

        await browser.close()

    notes_path = os.path.join(abs_scan_dir, f"{target_domain}_analiz_raporu.txt")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(f"HEDEF ANALİZ RAPORU: {target_domain}\n")
        f.write("=" * 40 + "\n\n")

        for res in results:
            f.write(f"Hedef: {res['subdomain']}\n")
            f.write(f"Durum: {res['status']}\n")
            if res.get('status_code') and res['status_code'] != "N/A":
                f.write(f"HTTP Kodu: {res['status_code']}\n")

            keywords = res.get('found_keywords', [])
            if keywords:
                f.write(f"Kritik Kelimeler: {', '.join(keywords)}\n")
            f.write("-" * 30 + "\n")

    return results