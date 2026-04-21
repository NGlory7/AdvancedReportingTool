import asyncio
import aiohttp

# vulnweb ve gerçek dünyada en çok karşılaşılan dizinler
WORDLIST = [
    "admin", "login", "wp-admin", "robots.txt", "backup.zip",
    ".git/config", "api", "dashboard", "config.php", "test", "CVS/Entries", "login.php"
]


async def fuzz_target(session, base_url, path):
    # Eğer url'nin sonunda / varsa ve wordlist'in başında da / varsa çift // olmasın diye ayarlıyoruz
    url = f"{base_url.rstrip('/')}/{path}"
    try:
        async with session.get(url, timeout=10, allow_redirects=False) as response:
            if response.status in [200, 301, 302, 403]:
                return {"path": f"/{path}", "status": response.status}
    except Exception:
        pass
    return None


async def run_fuzzer(active_urls):
    print(f"\n[*] 3. AŞAMA: {len(active_urls)} aktif hedefte gizli dizinler taranıyor...")
    results = {}

    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit_per_host=10, limit=50)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        for target in active_urls:
            print(f" -> Dizinler test ediliyor: {target}")
            tasks = [fuzz_target(session, target, word) for word in WORDLIST]
            found = await asyncio.gather(*tasks)

            valid_finds = [f for f in found if f]
            if valid_finds:
                results[target] = valid_finds

    return results