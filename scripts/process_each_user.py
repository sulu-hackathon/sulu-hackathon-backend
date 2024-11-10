import requests
import os

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY_PATH = os.path.join(BASE_DIR, 'sulu_api_key.txt')
PAGES_DATA_FILE = os.path.join(BASE_DIR, 'pages_ids.txt')

# Instagram API URL
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

# Load pages_data dictionary from file
def load_pages_data(file_path):
    pages_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    username, user_id = line.strip().split(': ')
                    pages_data[username.strip()] = int(user_id.strip())
    except FileNotFoundError:
        print("Pages data file not found. Please ensure 'pages_ids.txt' exists in the script directory.")
        exit(1)
    return pages_data

# Function to fetch user ID for a given username
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

# Function to fetch all followings for a given user ID with pagination
def fetch_followings(user_id):
    followings_url = f"{INSTAGRAM_API_URL}followings/?id_user={user_id}"
    all_followings = []  # List to store all followings
    next_max_id = None   # Pagination cursor, if provided by the API

    try:
        while True:
            # Update URL with pagination parameter if available
            if next_max_id:
                url = f"{followings_url}&next_max_id={next_max_id}"
            else:
                url = followings_url

            response = requests.get(url, headers=headers)
            print(response)
            
            if response.status_code == 200:
                data = response.json()
                followings = [user['pk'] for user in data.get('users', [])]  # List of current batch of followings
                all_followings.extend(followings)  # Append to the master list

                # Check if there's a next page
                next_max_id = data.get('next_max_id')
                if not next_max_id:
                    # No more pages left to fetch
                    break
            else:
                print(f"Failed to retrieve followings for user ID '{user_id}': Status code {response.status_code}")
                break
    except requests.exceptions.RequestException as e:
        print(f"Request error for user ID '{user_id}': {e}")

    return all_followings

# Initialize following_pages dictionary with values set to 0
def initialize_following_pages(pages_data):
    return {user_id: 0 for user_id in pages_data.values()}

# Main function to process followings and count '1's in following_pages
def process_followings(username, pages_data):
    # Step 1: Get the user ID of the given username
    user_id = fetch_user_id(username)
    if not user_id:
        print("Could not retrieve user ID for the provided username.")
        return

    # Step 2: Get the list of followings for the retrieved user ID
    followings = fetch_followings(user_id)
    print(f"Total followings retrieved: {len(followings)}")

    # Step 3: Initialize following_pages dictionary with 0
    following_pages = initialize_following_pages(pages_data)

    # Step 4: Update following_pages where IDs match followings
    for following_id in followings:
        if following_id in following_pages:
            following_pages[following_id] = 1

    # Step 5: Count and print the number of 1s in following_pages
    count_ones = sum(1 for value in following_pages.values() if value == 1)
    print("following_pages:", following_pages)
    print("Number of 1s in following_pages:", count_ones)

# Load pages_data and process followings for a given username
pages_data = load_pages_data(PAGES_DATA_FILE)
process_followings("ferrari", pages_data)
