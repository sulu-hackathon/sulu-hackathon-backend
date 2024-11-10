import requests
import os

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY_PATH = os.path.join(BASE_DIR, 'sulu_api_key.txt')
INPUT_FILE_PATH = os.path.join(BASE_DIR, 'top_pages.txt')
OUTPUT_FILE_PATH = os.path.join(BASE_DIR, 'pages_ids.txt')

# Base URL for the Instagram API
INSTAGRAM_API_URL = "https://instagram-scraper-2022.p.sulu.sh/ig/"

# Load the API key
try:
    with open(API_KEY_PATH, 'r') as f:
        api_key = f.read().strip()
except FileNotFoundError:
    print("API key file not found. Please ensure 'sulu_api_key.txt' exists in the script directory.")
    exit(1)

headers = {
    'Authorization': f'Bearer {api_key}',
}

# Function to fetch user ID by username
def fetch_user_id(username):
    user_id_url = f"{INSTAGRAM_API_URL}user_id/?user={username}"
    
    try:
        response = requests.get(user_id_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('id')
        else:
            print(f"Failed to retrieve user ID for '{username}': Status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error for '{username}': {e}")
        return None

# Read usernames from input file
try:
    with open(INPUT_FILE_PATH, 'r') as f:
        usernames = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Usernames file not found. Please ensure 'usernames.txt' exists in the script directory.")
    exit(1)

# Fetch user IDs and save to output file
with open(OUTPUT_FILE_PATH, 'w') as output_file:
    for username in usernames:
        user_id = fetch_user_id(username)
        if user_id:
            output_file.write(f"{username}: {user_id}\n")
            print(f"Username '{username}' has user ID '{user_id}'")

print("User ID fetching complete. Results saved to 'user_ids.txt'.")
