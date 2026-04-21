import asyncio
import random
import socket

# En çok kullanılan ve en kritik 15 port (WAF'ı yormamak için listeyi kısa tutuyoruz)
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]

async def check_port(sem, host, port):
    async with sem:
        # IDS/IPS ATLATMA TAKTİĞİ 1: Jitter (Rastgele bekleme süresi)
        await asyncio.sleep(random.uniform(0.1, 0.4))
        try:
            # Sadece 2 saniye cevap bekliyoruz.
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=2.0
            )
            writer.close()
            await writer.wait_closed()
            return port, "Açık"
        except Exception:
            return port, "Kapalı"

async def run_portscanner(active_urls):
    print(f"\n[*] 4. AŞAMA: {len(active_urls)} aktif hedefte kritik portlar taranıyor (Gizlilik Modu Aktif)...")
    results = {}

    # IDS/IPS ATLATMA TAKTİĞİ 2: Aynı anda sadece 15 port denenir.
    sem = asyncio.Semaphore(15)

    for target in active_urls:
        # Hedef 'http://vulnweb.com' şeklinde geliyor, bize sadece domain kısmı lazım
        host = target.replace("http://", "").replace("https://", "").split('/')[0]
        print(f" -> Portlar test ediliyor: {host}")

        # IDS/IPS ATLATMA TAKTİĞİ 3: Port listesini karıştır (Sıralı tarama yapma)
        ports_to_scan = COMMON_PORTS.copy()
        random.shuffle(ports_to_scan)

        tasks = [check_port(sem, host, port) for port in ports_to_scan]
        port_results = await asyncio.gather(*tasks)

        # Sadece açık olan portları filtrele ve raporda güzel dursun diye tekrar küçükten büyüğe sırala
        open_ports = sorted([p for p, status in port_results if status == "Açık"])
        if open_ports:
            results[target] = open_ports

    return results