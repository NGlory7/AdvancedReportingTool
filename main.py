import asyncio
import os
import warnings
import sys
from datetime import datetime
from urllib.parse import urlparse
from core.enumerator import get_subdomains
from core.processor import run_scanner
from core.reporter import generate_reports
from core.fuzzer import run_fuzzer
from core.portscanner import run_portscanner


G = '\033[92m'  # Yeşil (Başarılı)
R = '\033[91m'  # Kırmızı (Hata/Kritik)
B = '\033[94m'  # Mavi (Bilgi)
Y = '\033[93m'  # Sarı (Uyarı)
W = '\033[0m'  # Beyaz (Sıfırlama)


def clean_domain(raw_input):
    """Kullanıcının girdiği karmaşık URL'yi saf domaine çevirir."""

    if not raw_input.startswith(('http://', 'https://')):
        raw_input = 'http://' + raw_input

    parsed = urlparse(raw_input)
    domain = parsed.netloc


    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


async def main():
    print(f"{B}{'=' * 50}{W}")
    print(f"{G}   PROFESYONEL OSINT & PENTEST TARAYICI v5.1   {W}")
    print(f"{B}{'=' * 50}{W}")

    raw_target = input(f"\n{Y}[?] Hedef domain (örn: vulnweb.com): {W}").strip()
    if not raw_target:
        print(f"{R}[!] Hedef boş bırakılamaz. Çıkış yapılıyor.{W}")
        return

    target_domain = clean_domain(raw_target)
    print(f"{B}[*] Temizlenen Hedef: {W}{target_domain}")

    base_output_dir = os.path.abspath("outputs")
    os.makedirs(base_output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    scan_folder_name = f"{target_domain}_{timestamp}"
    scan_dir = os.path.join(base_output_dir, scan_folder_name)

    print(f"\n{B}[*] 1. AŞAMA: Subdomain Keşfi...{W}")
    subdomains = get_subdomains(target_domain)
    if not subdomains:
        print(f"{R}[-] Hedef bulunamadı veya bağlantı kurulamadı.{W}")
        return

    print(f"\n{B}[*] 2. AŞAMA: {len(subdomains)} adet hedef analiz ediliyor (SS ve İçerik)...{W}")
    results = await run_scanner(subdomains, scan_dir, target_domain)

    active_urls = [f"http://{res['subdomain']}" for res in results if res.get('status_code', 'N/A') != "N/A"]

    fuzz_results = {}
    if active_urls:
        print(f"\n{B}[*] 3. AŞAMA: Aktif hedeflerde gizli dizin taraması...{W}")
        fuzz_results = await run_fuzzer(active_urls)

    port_results = {}
    if active_urls:
        print(f"\n{B}[*] 4. AŞAMA: Aktif hedeflerde port taraması (Ninja Mod)...{W}")
        port_results = await run_portscanner(active_urls)

    print(f"\n{B}[*] 5. AŞAMA: Raporlar Derleniyor...{W}")
    html_path, txt_path = generate_reports(results, fuzz_results, port_results, scan_dir, target_domain)

    print(f"\n{G}{'=' * 50}{W}")
    print(f"{G} [✓] TARAMA BAŞARIYLA TAMAMLANDI {W}")
    print(f"{Y} HTML Dashboard: {W}{html_path}")
    print(f"{Y} TXT Analiz Raporu: {W}{txt_path}")
    print(f"{G}{'=' * 50}{W}")


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':

            warnings.filterwarnings("ignore", category=DeprecationWarning)
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] İşlem kullanıcı tarafından iptal edildi (Ctrl+C).{W}")
        print(f"{Y}[*] Güvenli bir şekilde kapatılıyor...{W}")
        sys.exit(0)