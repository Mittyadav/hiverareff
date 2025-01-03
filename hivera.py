import requests
import time
from datetime import datetime, timezone
import json
from colorama import Fore, Style, init
import signal
import sys
import urllib.parse

init(autoreset=True)

contribute_url = "https://api.hivera.org/v2/engine/contribute"
powers_url = "https://api.hivera.org/users/powers"
auth_url = "https://api.hivera.org/auth"
metric_self_url = "https://api.hivera.org/metric/self"
referal_auth = "https://api.hivera.org/referral?referral_code=1405c09f8"

def exit_handler(sig, frame):
    print(f"\n{Fore.RED+Style.BRIGHT}Bot stopped!{Style.RESET_ALL}")
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

auth_data_file = "data.txt"
auth_data_list = []

def parse_auth_data(raw_auth_data):
    parsed_data = urllib.parse.parse_qs(raw_auth_data, strict_parsing=True)
    auth_data = {k: v[0] for k, v in parsed_data.items()}
    if 'user' in auth_data:
        try:
            user_json = urllib.parse.unquote(auth_data['user'])
            auth_data['user'] = json.loads(user_json)
        except json.JSONDecodeError:
            auth_data['user'] = {}
    return auth_data

def is_valid_auth_data(auth_data):
    required_fields = ['user', 'chat_instance', 'chat_type', 'auth_date', 'signature', 'hash']
    return all(field in auth_data for field in required_fields)

try:
    with open(auth_data_file, "r") as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if line:
                parsed_auth = parse_auth_data(line)
                if is_valid_auth_data(parsed_auth):
                    auth_data_list.append({'parsed': parsed_auth, 'raw': line})
                else:
                    print(f"{Fore.RED}Invalid auth_data structure at line {line_number}: {line}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Loaded {len(auth_data_list)} accounts.{Style.RESET_ALL}")
except FileNotFoundError:
    print(f"{Fore.RED}Error: The file {auth_data_file} was not found.{Style.RESET_ALL}")

proxies = []
use_proxy = False

if use_proxy:
    try:
        with open("proxy.txt", "r") as proxy_file:
            proxies = [line.strip() for line in proxy_file.readlines() if line.strip()]
        if proxies:
            print(f"{Fore.GREEN}Loaded {len(proxies)} proxies.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Proxy file is empty. Proceeding without proxies.{Style.RESET_ALL}")
            use_proxy = False
    except FileNotFoundError:
        print(f"{Fore.RED}Proxy file not found. Proceeding without proxies.{Style.RESET_ALL}")
        use_proxy = False

def get_activity(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            referal_auth,
            params=params,
            headers=headers,
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def get_metrics(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            metric_self_url,
            params=params,
            headers=headers,
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json().get("result", {})
            return data.get("rank", "N/A"), data.get("earned", "N/A")
        return "N/A", "N/A"
    except:
        return "N/A", "N/A"

def check_power(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            powers_url,
            params=params,
            headers=headers,
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=10
        )
        if response.status_code == 200:
            power_data = response.json().get("result", {})
            return True, power_data.get("POWER", 0), power_data.get("POWER_CAPACITY", 0)
        return False, 0, 0
    except:
        return False, 0, 0

def post_request(raw_auth_data, proxy=None):
    from_date = int(datetime.now(timezone.utc).timestamp() * 1000)
    payload = {
        "from_date": from_date,
        "quality_connection": 100,
        "times": 100
    }
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            contribute_url,
            params=params,
            json=payload,
            headers=headers,
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except:
        return False, "Error occurred"

def animated_loading(duration):
    frames = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        for frame in frames:
            print(f"\rWaiting for the next claim {frame} - {remaining_time} seconds", end="", flush=True)
            time.sleep(0.25)
    print("\rWaiting for the next claim to be completed.         ", flush=True)

def print_welcome_message():
    print(Fore.GREEN + r"""
  -================= ≫ ──── ≪•◦ ❈ ◦•≫ ──── ≪=================-
 │                                                          │
 │  ██████╗  █████╗ ██████╗ ██╗  ██╗                        │
 │  ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝                        │
 │  ██║  ██║███████║██████╔╝█████╔╝                         │
 │  ██║  ██║██╔══██║██╔══██╗██╔═██╗                         │
 │  ██████╔╝██║  ██║██║  ██║██║  ██╗                        │
 │  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                        │
 │                                                          │
 │                                                          │
 ╰─━━━━━━━━━━━━━━━━━━━━━━━━Termux-os━━━━━━━━━━━━━━━━━━━━━━━─╯

    """)
    print(Fore.YELLOW + "Join Telegram Channel: https://t.me/scripthub00")

def print_chamber(username, referral_status, rank, earned, power_status, miner_status):
    print(f"{Fore.MAGENTA}────────────────────────────────────────────────────────────────────{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Username: {Fore.CYAN}{username}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Referral Status: {Fore.GREEN if referral_status == 'Applied' else Fore.RED}{referral_status}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Rank: {Fore.CYAN}{rank}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Balance: {Fore.CYAN}{earned}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Power: {Fore.GREEN if power_status == 'Good' else Fore.RED}{power_status}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Miner Status: {Fore.YELLOW}{miner_status}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}────────────────────────────────────────────────────────────────────{Style.RESET_ALL}")

if __name__ == "__main__":
    print_welcome_message()
    if not auth_data_list:
        print(f"{Fore.RED}Auth data is empty.{Style.RESET_ALL}")
        sys.exit(1)

    proxy_index = 0
    while True:
 
        for auth_entry in auth_data_list:
            parsed_auth = auth_entry['parsed']
            raw_auth = auth_entry['raw']
            username = parsed_auth.get('user', {}).get('username', 'No Username')
            print(f"\n{Fore.CYAN}[ Username ] : {username}{Style.RESET_ALL}")
            
            proxy = None
            if use_proxy and proxies:
                proxy = proxies[proxy_index % len(proxies)]
                print(f"{Fore.YELLOW}[ Proxy ] : {proxy}{Style.RESET_ALL}")
            elif use_proxy:
                print(f"{Fore.YELLOW}[ Proxy ] : No proxies.{Style.RESET_ALL}")
            
            response_activity = get_activity(raw_auth, proxy)
            if response_activity:
                print(f"{Fore.GREEN}[ Referral ] : Applied{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[ Referral ] : Failed to Apply referral{Style.RESET_ALL}")
            # Fetch and print rank and earned before checking power
            rank, earned = get_metrics(raw_auth, proxy)
            print(f"{Fore.BLUE+Style.BRIGHT}[ Rank ] : {rank}{Style.RESET_ALL}")
            print(f"{Fore.GREEN+Style.BRIGHT}[ Balance ] : {earned}{Style.RESET_ALL}")
            power_ok, current_power, power_capacity = check_power(raw_auth, proxy)
            if power_ok:
                print(f"{Fore.GREEN}[ Power ] : {current_power}/{power_capacity}{Style.RESET_ALL}")
                if current_power >= 1000:
                    success, response = post_request(raw_auth, proxy)
                    if success:
                        hivera_balance = response.get('result', {}).get('profile', {}).get('HIVERA', 0)
                        print(f"{Fore.GREEN}[ Miner ] : Mining successful! Balance: {hivera_balance}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[ Miner ] : Request failed. Response: {response}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[ Miner ] : Skipping. Power is low{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[ Power ]: Power is low{Style.RESET_ALL}")
            
            time.sleep(5)

            if use_proxy and len(proxies) > 1:
                proxy_index += 1

        animated_loading(60)
