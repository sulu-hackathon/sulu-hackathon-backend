import requests
import os

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY_PATH = os.path.join(BASE_DIR, 'sulu_api_key.txt')
PAGES_DATA_FILE = os.path.join(BASE_DIR, 'pages_ids.txt')
PEOPLE_DATA_FILE = os.path.join(BASE_DIR, 'people_ids.txt')

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

# Load data from file and create a dictionary
def load_data(file_path):
    data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    username, user_id = line.strip().split(': ')
                    data[username.strip()] = int(user_id.strip())
    except FileNotFoundError:
        print(f"Data file '{file_path}' not found.")
        exit(1)
    return data

# Function to fetch user ID for a given username
def fetch_user_id(username):
    print("fetch user id")
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

# Initialize dictionary with values set to 0
def initialize_data_hash(data):
    return {user_id: 0 for user_id in data.values()}

# Process followings for a given user
def process_followings(username, pages_data, people_data):
    print("process_followings")
    user_id = fetch_user_id(username)
    if not user_id:
        print("Could not retrieve user ID for the provided username.")
        return None, None

    followings = fetch_followings(user_id)
    print(f"Total followings retrieved: {len(followings)}")

    # Initialize data hash for pages and people
    pages_hash = initialize_data_hash(pages_data)
    people_hash = initialize_data_hash(people_data)

    # Update both hashes based on followings
    for following_id in followings:
        if following_id in pages_hash:
            pages_hash[following_id] = 1
        if following_id in people_hash:
            people_hash[following_id] = 1

    # Count the number of 1s in each hash
    pages_count = sum(1 for value in pages_hash.values() if value == 1)
    people_count = sum(1 for value in people_hash.values() if value == 1)

    print("Pages following count:", pages_count)
    print("People following count:", people_count)
    return pages_hash, people_hash

# New function to calculate score based on bitwise AND
def calculate_score(hashmap1, hashmap2):
    score = sum((hashmap1[key] & hashmap2[key]) for key in hashmap1)
    return score

# Load data for pages and people
pages_data = load_data(PAGES_DATA_FILE)
people_data = load_data(PEOPLE_DATA_FILE)

# Process followings for two accounts and display results
pages_hash_ferrari, people_hash_ferrari = process_followings("scuderiaferrari", pages_data, people_data)
pages_hash_mercedes, people_hash_mercedes = process_followings("mercedesamgf1", pages_data, people_data)

# Calculate scores
pages_score = calculate_score(pages_hash_ferrari, pages_hash_mercedes)
people_score = calculate_score(people_hash_ferrari, people_hash_mercedes)

print("Pages Score (Ferrari & Mercedes):", pages_score)
print("People Score (Ferrari & Mercedes):", people_score)
