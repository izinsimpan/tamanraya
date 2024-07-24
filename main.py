import requests
import time
import os
from colorama import init, Fore
import itertools

# Inisialisasi colorama
init(autoreset=True)

# Fungsi untuk membaca wallet dari file
def read_wallets(filename):
    with open(filename, 'r') as file:
        return [line.strip().lower() for line in file]  # Convert to lowercase

# Fungsi untuk mengirimkan POST request
def send_post_request(url, headers):
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return None

# Fungsi untuk mengirimkan GET request
def send_get_request(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred: {e}")
        return None

# Fungsi untuk membaca data dari API
def get_data(wallet_address, session):
    post_url = "https://api.taman.fun/users"
    post_headers = {"Wallet": wallet_address}

    post_data = send_post_request(post_url, post_headers)
    if post_data and not post_data.get('success'):
        print(f"POST request failed for wallet {wallet_address}: {post_data.get('message')}")
        return None, None, None

    mining_url = "https://api.taman.fun/mining"
    get_headers = {"Wallet": wallet_address}

    mining_data = send_get_request(mining_url, get_headers)
    if mining_data and mining_data.get('success'):
        return (mining_data['data']['pointPerHour'], mining_data['data']['point'], 
                mining_data['data']['pointCanClaimed'])
    elif mining_data:
        print(f"GET request failed for wallet {wallet_address}: {mining_data.get('message')}")
    return None, None, None

# Fungsi untuk klaim poin
def claim_points(wallet_address, session):
    claim_url = "https://api.taman.fun/mining"
    headers = {"Wallet": wallet_address}

    claim_data = send_post_request(claim_url, headers)
    if claim_data and claim_data.get('success'):
        return claim_data['data']['pointClaimed']
    return None

# Fungsi untuk membersihkan layar
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Daftar warna yang akan digunakan
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
color_cycle = itertools.cycle(colors)

# Membaca wallet dari file
wallets = read_wallets('akun.txt')

while True:
    clear_screen()
    session = requests.Session()

    for idx, wallet_address in enumerate(wallets, 1):
        point_per_hour, point, point_can_claimed = get_data(wallet_address, session)

        if point_per_hour is not None and point is not None and point_can_claimed is not None:
            color = next(color_cycle)
            print(color + f"Akun {idx}: Point Claim: {point_can_claimed:.4f} | Point Per Hour: {point_per_hour} | Point: {point:.4f}")
            Fore.RESET  # Reset warna setelah mencetak

            if point_can_claimed >= 1.4:  # Sesuaikan dengan batas klaim yang sesuai
                claimed_points = claim_points(wallet_address, session)
                if claimed_points:
                    print(color + f"Akun {idx}: Klaim berhasil, jumlah poin yang diklaim: {claimed_points:.4f}")
                    Fore.RESET  # Reset warna setelah mencetak
        else:
            color = next(color_cycle)
            print(color + f"Akun {idx}: Gagal mendapatkan data")
            Fore.RESET  # Reset warna setelah mencetak

    time.sleep(360)