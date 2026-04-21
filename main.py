import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def gather_recon_data(target_url):
    print(f"[*] Hedef taranıyor: {target_url}\n")

    # Hedef siteye gerçek bir tarayıcı gibi görünmek için User-Agent ekliyoruz (Anti-Bot önlemi)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Siteye GET isteği atıyoruz
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()  # Hata varsa (404, 500 vb.) programı durdurmadan yakalamak için
    except Exception as e:
        print(f"[!] Hedefe ulaşılamadı: {e}")
        return

    # Gelen HTML'i BeautifulSoup ile parçalıyoruz
    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Bütün HTTP/HTTPS Linklerini Çekme
    print("--- BULUNAN BAĞLANTILAR ---")
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        # Eğer link "/hakkimizda" gibi yarım bir linkse, tam URL'ye çeviriyoruz
        full_url = urljoin(target_url, href)
        if full_url.startswith("http"):
            print(full_url)

    print("\n--- BULUNAN GÖRSELLER (JPEG/PNG) ---")
    # 2. Bütün Görsel (img) etiketlerini çekme
    images = soup.find_all("img", src=True)
    for img in images:
        img_src = img["src"]
        full_img_url = urljoin(target_url, img_src)

        # Sadece .jpg, .jpeg ve .png uzantılı olanları filtrele
        if full_img_url.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(full_img_url)


if __name__ == "__main__":
    # Buraya test etmek istediğin bir sitenin adresini yazabilirsin (Örn: "https://scrapethissite.com")
    hedef_site = "https://example.com"
    gather_recon_data(hedef_site)