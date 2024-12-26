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
    print(f"\n{Fore.RED+Style.BRIGHT}Bot stopped !{Style.RESET_ALL}")
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
        except json.JSONDecodeError as e:
            auth_data['user'] = {}
        except Exception as e:
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
    print(f"{Fore.YELLOW}Loaded {len(auth_data_list)}  accounts.{Style.RESET_ALL}")
except FileNotFoundError:
    print(f"{Fore.RED}Error: The file {auth_data_file} was not found.{Style.RESET_ALL}")

proxies = []
use_proxy = False
min_power = 500

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

def get_username(raw_auth_data):
    try:
        response = requests.get(
            f"{auth_url}",
            params={"auth_data": raw_auth_data},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json().get("result", {})
            username = result.get("username", "Unknown")
            return username
        else:
            print(f"{Fore.RED}Error fetching username. Status Code: {response.status_code}{Style.RESET_ALL}")
          
            return "Unknown"
    except Exception as e:
   
        return "Unknown"
def get_activity(raw_auth_data, proxy=None):
    """
    Fetches the rank and earned metrics for the user.
    """
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.get(
                referal_auth,
                params=params,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.get(
                referal_auth,
                params=params,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            
            return True
        else:
           
            return False
    except Exception as e:
      
        return False
    
def get_metrics(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.get(
                metric_self_url,
                params=params,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.get(
                metric_self_url,
                params=params,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            data = response.json().get("result", {})
            rank = data.get("rank", "N/A")
            earned = data.get("earned", "N/A")
            return rank, earned
        else:
         
            return "N/A", "N/A"
    except Exception as e:
    
        return "N/A", "N/A"

def check_power(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.get(
                f"{powers_url}",
                params=params,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.get(
                f"{powers_url}",
                params=params,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            power_data = response.json().get("result", {})
            current_power = power_data.get("POWER", 0)
            power_capacity = power_data.get("POWER_CAPACITY", 0)
            hivera = power_data.get("HIVERA", 0)

       
            return True, current_power, power_capacity
            
        else:
            
            return False, 0, 0
    except Exception as e:
 
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

        if proxy:
            response = requests.post(
                f"{contribute_url}",
                params=params,
                json=payload,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.post(
                f"{contribute_url}",
                params=params,
                json=payload,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            return True, response.json()
        else:
           
            return False, response.text
    except Exception as e:
     
        return False, "Error occurred"

def print_header(title):
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * (len(title) + 2)}{Style.RESET_ALL}")

def animated_loading(duration):
    frames = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        for frame in frames:
            print(f"\rWaiting for the next claim time {frame} - Remaining {remaining_time} second         ", end="", flush=True)
            time.sleep(0.25)
    print("\rWaiting for the next claim to be completed.                            ", flush=True)
 

def print_welcome_message():
    print(Fore.WHITE + r"""
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
    print(Fore.GREEN + Style.BRIGHT + "Hivera Miner")
    print(Fore.YELLOW + Style.BRIGHT + "Join Telegram Channel: https://t.me/scripthub00")

if __name__ == "__main__":
    print_welcome_message()  # Banner must be printed first
    if not auth_data_list:
        print(f"{Fore.RED} Auth data is empty.{Style.RESET_ALL}")
        sys.exit(1)
    
 def display_chamber(username, referral_status, rank, balance, power_status, miner_status):
    """
    Display a stylish chamber for user details and mining status.
    """
    print("\n" + Fore.MAGENTA + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + f"               User Mining Chamber")
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 50)
    
    print(Fore.YELLOW + f"[ Username ] : {Fore.GREEN + username}")
    print(Fore.YELLOW + f"[ Referral ] : {Fore.GREEN + referral_status if referral_status == 'Applied' else Fore.RED + referral_status}")
    print(Fore.YELLOW + f"[ Rank ]     : {Fore.CYAN + rank}")
    print(Fore.YELLOW + f"[ Balance ]  : {Fore.CYAN + balance}")
    
    power_status_text = f"{current_power}/{power_capacity}" if power_status else "Power is low"
    power_status_color = Fore.GREEN if power_status else Fore.RED
    print(Fore.YELLOW + f"[ Power ]    : {power_status_color + power_status_text}")
    
    miner_status_color = Fore.GREEN if "Success" in miner_status else Fore.YELLOW if "Skipping" in miner_status else Fore.RED
    print(Fore.YELLOW + f"[ Miner ]    : {miner_status_color + miner_status}")
    
    print(Fore.MAGENTA + "=" * 50 + "\n")

# Main Loop with Stylish Chamber
if __name__ == "__main__":
    if not auth_data_list:
        print(f"{Fore.RED} Auth data is empty.{Style.RESET_ALL}")
        sys.exit(1)
    
    proxy_index = 0
    while True:
        for auth_entry in auth_data_list:
            parsed_auth = auth_entry['parsed']
            raw_auth = auth_entry['raw']
            username = parsed_auth.get('user', {}).get('username', 'No Username')
            
            # Determine Proxy
            proxy = None
            if use_proxy and proxies:
                proxy = proxies[proxy_index % len(proxies)]
            
            # Referral Status
            response_activity = get_activity(raw_auth, proxy)
            referral_status = "Applied" if response_activity else "Failed"
            
            # Metrics
            rank, earned = get_metrics(raw_auth, proxy)
            
            # Power Status
            power_ok, current_power, power_capacity = check_power(raw_auth, proxy)
            power_status = power_ok and current_power >= 1000
            
            # Miner Status
            if power_ok:
                if current_power >= 1000:
                    success, response = post_request(raw_auth, proxy)
                    miner_status = "Success" if success else f"Failed: {response}"
                else:
                    miner_status = "Skipping. Power is low"
            else:
                miner_status = "Power is low"
            
            # Display Chamber
            display_chamber(
                username=username,
                referral_status=referral_status,
                rank=rank,
                balance=earned,
                power_status=power_ok,
                miner_status=miner_status
            )
            
            time.sleep(5)
            
            if use_proxy and len(proxies) > 1:
                proxy_index += 1
        
        animated_loading(60)
