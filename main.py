import asyncio
import os
from datetime import datetime
from core.enumerator import get_subdomains
from core.processor import run_scanner


async def main():
    print("=" * 40)
    print("   PROFESYONEL OSINT TARAYICI v2.1   ")
    print("=" * 40)

    target_domain = input("\n[?] Hedef domain (örn: erciyes.edu.tr): ").strip()
    if not target_domain:
        return

    # --- KLASÖRLEME SİSTEMİ ---
    base_output_dir = os.path.abspath("outputs")
    os.makedirs(base_output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    scan_folder_name = f"{target_domain}_{timestamp}"
    scan_dir = os.path.join(base_output_dir, scan_folder_name)

    # 1. Aşama: Keşif
    subdomains = get_subdomains(target_domain)

    if not subdomains:
        print("[-] Hedef bulunamadı veya bağlantı kurulamadı.")
        return

    # 2. Aşama: Derin Analiz
    print(f"\n[*] 2. AŞAMA: {len(subdomains)} adet hedef analiz ediliyor...")
    print(f"[*] Kayıt Klasörü: {scan_dir}\n")

    results = await run_scanner(subdomains, scan_dir, target_domain)

    print("\n" + "=" * 40)
    print(f" TARAMA TAMAMLANDI - Dosyalar '{scan_dir}' içine kaydedildi. ")
    print("=" * 40)

    # Sadece kritik bulguları terminale bas (Kalabalık yapmasın)
    for res in results:
        if res['status'] == "Success" and res.get('found_keywords'):
            print(f"[!] KRİTİK BULGU - {res['subdomain']}: {', '.join(res['found_keywords'])}")


if __name__ == "__main__":

    asyncio.run(main())