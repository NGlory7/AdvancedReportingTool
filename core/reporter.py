import os
from datetime import datetime



def generate_reports(results, fuzz_results, port_results, scan_dir, target_domain):
    print("[*] HTML ve TXT Raporları oluşturuluyor...")

    html_path = os.path.join(scan_dir, "index.html")
    txt_path = os.path.join(scan_dir, f"{target_domain}_tam_rapor.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"HEDEF ANALİZ RAPORU: {target_domain}\n")
        f.write(f"Tarama Tarihi: {timestamp}\n")
        f.write("=" * 40 + "\n\n")

        for res in results:
            sub = res['subdomain']
            f.write(f"Hedef: {sub}\n")
            f.write(f"Durum: {res['status']}\n")
            if res.get('status_code') and res['status_code'] != "N/A":
                f.write(f"HTTP Kodu: {res['status_code']}\n")

            keywords = res.get('found_keywords', [])
            if keywords:
                f.write(f"Kritik Kelimeler: {', '.join(keywords)}\n")

            target_url = f"http://{sub}"

            # Port Sonuçları
            if target_url in port_results:
                f.write(f"Açık Portlar: {', '.join(map(str, port_results[target_url]))}\n")

            # Fuzz Sonuçları
            if target_url in fuzz_results:
                f.write("Gizli Dizinler:\n")
                for fz in fuzz_results[target_url]:
                    f.write(f"  -> {fz['path']} (HTTP {fz['status']})\n")

            f.write("-" * 30 + "\n")


    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>OSINT Dashboard: {target_domain}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #1e1e2e; color: #cdd6f4; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #89b4fa; border-bottom: 2px solid #313244; padding-bottom: 10px; }}
            .summary {{ text-align: center; margin-bottom: 30px; font-size: 1.1em; color: #a6adc8; }}
            .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
            .card {{ background-color: #181825; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid #313244; }}
            .card-header {{ padding: 15px; background-color: #313244; font-weight: bold; color: #f5c2e7; }}
            .card-img {{ width: 100%; height: 200px; object-fit: cover; border-bottom: 1px solid #313244; }}
            .card-body {{ padding: 15px; }}
            .status-success {{ color: #a6e3a1; font-weight: bold; }}
            .status-error {{ color: #f38ba8; }}
            .status-timeout {{ color: #f9e2af; }}
            .keywords {{ margin-top: 10px; padding: 10px; background-color: #45475a; border-radius: 4px; color: #f38ba8; font-weight: bold; font-size: 0.9em; }}
            .fuzz-box {{ margin-top: 10px; padding: 10px; background-color: #2b2a3d; border-radius: 4px; border-left: 4px solid #cba6f7; }}
            .fuzz-item {{ color: #cba6f7; font-size: 0.9em; font-family: monospace; }}
            .port-box {{ margin-top: 10px; padding: 10px; background-color: #1e2030; border-radius: 4px; border-left: 4px solid #8caaee; font-weight: bold; color: #8caaee; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>Hedef Analiz Raporu: {target_domain}</h1>
        <div class="summary">
            <p>Tarama Tarihi: {timestamp} | Toplam Taranan Hedef: {len(results)}</p>
        </div>
        <div class="grid-container">
    """

    for res in results:
        sub = res['subdomain']
        status = res['status']
        status_code = res.get('status_code', 'N/A')
        keywords = res.get('found_keywords', [])

        if "Success" in status:
            status_class = "status-success"
        elif "Timeout" in status:
            status_class = "status-timeout"
        else:
            status_class = "status-error"

        safe_name = sub.replace("://", "_").replace("/", "_")
        ss_rel_path = f"screenshots/{safe_name}.png"
        ss_abs_path = os.path.join(scan_dir, "screenshots", f"{safe_name}.png")

        if os.path.exists(ss_abs_path):
            img_tag = f'<a href="{ss_rel_path}" target="_blank"><img src="{ss_rel_path}" class="card-img" alt="Screenshot"></a>'
        else:
            img_tag = f'<div style="height:200px; display:flex; align-items:center; justify-content:center; background:#11111b;">Görsel Yok</div>'

        kw_tag = ""
        if keywords:
            kw_tag = f'<div class="keywords">🚨 KRİTİK BULGULAR:<br>{", ".join(keywords).upper()}</div>'

        target_url = f"http://{sub}"

        port_tag = ""
        if target_url in port_results:
            ports_str = ", ".join(map(str, port_results[target_url]))
            port_tag = f'<div class="port-box">🔌 Açık Portlar: {ports_str}</div>'

        fuzz_tag = ""
        if target_url in fuzz_results:
            fuzz_tag += '<div class="fuzz-box"><strong>📁 Bulunan Dizinler:</strong><br>'
            for fz in fuzz_results[target_url]:
                fuzz_tag += f'<span class="fuzz-item">{fz["path"]} (HTTP {fz["status"]})</span><br>'
            fuzz_tag += '</div>'

        card = f"""
            <div class="card">
                <div class="card-header">{sub}</div>
                {img_tag}
                <div class="card-body">
                    <p>Durum: <span class="{status_class}">{status}</span></p>
                    <p>HTTP Kodu: {status_code}</p>
                    {port_tag}
                    {kw_tag}
                    {fuzz_tag}
                </div>
            </div>
        """
        html_content += card

    html_content += "</div></body></html>"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_path, txt_path