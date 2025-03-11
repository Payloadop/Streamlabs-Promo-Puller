import tls_client
from console import Console
import threading, urllib, json, base64, random
import re
import hashlib
import os
import time
import sys

console = Console()
os.system('cls')

def read_proxies():
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            console.error("No proxies found in proxies.txt")
            sys.exit(1)
        return proxies
    except FileNotFoundError:
        console.error("proxies.txt not found.")
        sys.exit(1)

def remove_account(acc):
    try:
        with open("accs.txt", "r") as f:
            data = f.read().strip().splitlines()

        if str(acc) in data:
            data.remove(str(acc))

            with open("accs.txt", "w") as f:
                f.writelines("\n".join(data) + "\n")

            console.info(f"Removed account {acc} from accs.txt")
    except FileNotFoundError:
        console.error("accs.txt not found. Skipping removal.")

def puller(client, acc, retries=3):
    proxies = read_proxies()
    proxy = f"http://{random.choice(proxies)}"
    client.proxies = {"http": proxy, "https": proxy}

    response = client.get("https://streamlabs.com/discord/nitro?s=")

    if "https://discord.com/billing/partner-promotions/1310745123109339258" in response.text:
        promo = response.headers.get("Location", "Promo URL Not Found")
        with open("3month_promos.txt", "a") as f:
            f.write(f"{promo}\n")
        console.success(f"Successfully pulled promo code: {promo[:160]}...")
        remove_account(acc)

    elif "https://discord.com/billing/partner-promotions/1310745070936391821" in response.text:
        promo = response.headers.get("Location", "Promo URL Not Found")
        with open("1month_promos.txt", "a") as f:
            f.write(f"{promo}\n")
        console.success(f"Successfully pulled promo code: {promo[:160]}...")
        remove_account(acc)

    elif "https://streamlabs.com/dashboard?error=Not-allowed-to-claim-Nitro-trial" in response.text:
        with open("notallowed.txt", "a") as f:
            f.write(f"{acc}\n")
        console.info(f"Failed To Pull Promo: Not Allowed To Claim Nitro Trial")
        remove_account(acc)

    elif "You-have-already-claimed-your-Nitro-trial" in response.text:
        console.error("Already Claimed")
        remove_account(acc)

    else:
        console.warning("Failed to pull promo code. Retrying...")
        if retries > 0:
            time.sleep(3)
            return puller(client, acc, retries - 1)
        else:
            console.error("Max retries reached. Exiting.")
            remove_account(acc)

def get_xsrf_token_from_cookies(client):
    url = "https://streamlabs.com/slid/login"
    s = client.get(url)
    xsrf_token = client.cookies.get('XSRF-TOKEN')
    if xsrf_token:
        return xsrf_token.replace('%3D', '=')
    else:
        raise ValueError("XSRF token not found in cookies")

def login(acc):
    mail, passw = acc.split(":")
    client = tls_client.Session(client_identifier="chrome_133", random_tls_extension_order=True)
    proxies = read_proxies()
    proxy = f"http://{random.choice(proxies)}"
    client.proxies = {"http": proxy, "https": proxy}

    try:
        tokenn = get_xsrf_token_from_cookies(client)
    except ValueError:
        console.error("XSRF token not found. Skipping account.")
        remove_account(acc)
        return

    payload = {"email": mail, "password": passw}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://streamlabs.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-xsrf-token': tokenn,
    }

    s = client.post("https://api-id.streamlabs.com/v1/auth/login", headers=headers, json=payload)

    if s.status_code == 200:
        hidden_mail = re.sub(r'@.*', '@*****.***', mail)
        console.success(f"Successfully Logged In -> {hidden_mail}")
        finalize_registration(client, headers, acc)
    else:
        console.error(f"Failed to login -> {s.text}")
        remove_account(acc)

def finalize_registration(client, headers, acc):
    resp = client.post("https://api-id.streamlabs.com/v1/identity/clients/419049641753968640/oauth2", 
                       headers=headers, 
                       json={"origin": "https://streamlabs.com", "intent": "connect", "state": ""})
    
    if resp.status_code == 200:
        location = follow_redirects(client, resp.json().get("redirect_url"))
        csrf_token = client.get("https://streamlabs.com/dashboard").text.split('name="csrf-token" content="')[1].split('"')[0]
        console.info(f"CSRF -> {csrf_token}")
        puller(client, acc)

def follow_redirects(client, url):
    while url:
        resp = client.get(url, headers={"referer": url})
        url = resp.headers.get("Location")
        if "data=" in resp.url:
            try:
                decoded_data = json.loads(base64.b64decode(urllib.parse.unquote(resp.url.split("?data=")[1].split("&")[0])).decode("utf-8"))
                return decoded_data["redirect"]
            except (IndexError, KeyError, json.JSONDecodeError):
                console.error("Failed to decode redirect URL.")
                return None
    return url

from concurrent.futures import ThreadPoolExecutor

if __name__ == "__main__":
    try:
        thr = int(console.input("Enter number of threads: "))
        accounts = open("accs.txt").read().strip().splitlines()
        with ThreadPoolExecutor(max_workers=thr) as executor:
            executor.map(login, accounts)
    except ValueError:
        console.error("Invalid thread count. Please enter a valid number.")
    except FileNotFoundError:
        console.error("accs.txt not found. Add accounts before running the script.")
