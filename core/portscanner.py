import asyncio
import random
import socket

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]

async def check_port(sem, host, port):
    async with sem:

        await asyncio.sleep(random.uniform(0.1, 0.4))
        try:

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

    sem = asyncio.Semaphore(15)

    for target in active_urls:

        host = target.replace("http://", "").replace("https://", "").split('/')[0]
        print(f" -> Portlar test ediliyor: {host}")


        ports_to_scan = COMMON_PORTS.copy()
        random.shuffle(ports_to_scan)

        tasks = [check_port(sem, host, port) for port in ports_to_scan]
        port_results = await asyncio.gather(*tasks)


        open_ports = sorted([p for p, status in port_results if status == "Açık"])
        if open_ports:
            results[target] = open_ports

    return results