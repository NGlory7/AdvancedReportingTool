import requests


def get_subdomains(domain):
    """
    Hedef domain için birden fazla kaynaktan (crt.sh ve HackerTarget) subdomain toplar.
    """
    print(f"[*] {domain} için subdomainler aranıyor...")
    subdomains = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # --- 1. KAYNAK: crt.sh ---
    print(" -> crt.sh veritabanı sorgulanıyor (Bu işlem biraz sürebilir)...")
    try:
        url = "https://crt.sh/"
        params = {"q": domain, "output": "json"}
        # crt.sh yavaş olduğu için timeout süresini 30 saniyeye çıkardık
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 200 and response.text.strip():
            data = response.json()
            for entry in data:
                names = entry['name_value'].split('\n')
                for name in names:
                    name = name.strip()
                    if not name.startswith('*') and name.endswith(domain):
                        subdomains.add(name)
            print(f"    [+] crt.sh taraması bitti.")
    except Exception as e:
        print("    [-] crt.sh çok yavaş veya yanıt vermiyor, atlanıyor.")

    # --- 2. KAYNAK: HackerTarget ---
    print(" -> HackerTarget veritabanı sorgulanıyor...")
    try:
        ht_url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        # HackerTarget genelde çok hızlıdır, 15 saniye yeterli
        ht_response = requests.get(ht_url, headers=headers, timeout=15)

        if ht_response.status_code == 200:
            lines = ht_response.text.split('\n')
            for line in lines:
                if ',' in line:
                    # Gelen veri "subdomain.com,192.168.1.1" formatında, virgülden öncesini alıyoruz
                    sub = line.split(',')[0].strip()
                    if sub.endswith(domain):
                        subdomains.add(sub)
            print(f"    [+] HackerTarget taraması bitti.")
    except Exception as e:
        print("    [-] HackerTarget yanıt vermiyor, atlanıyor.")

    # --- SONUÇLARI DÖNDÜR ---
    print(f"\n[+] Toplam {len(subdomains)} adet benzersiz subdomain bulundu.\n")
    return list(subdomains)


if __name__ == "__main__":
    hedef = ""
    bulunanlar = get_subdomains(hedef)
    for sub in bulunanlar:
        print(sub)