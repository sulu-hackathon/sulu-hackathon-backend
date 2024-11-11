import requests
import os
import json
from firebase_admin import firestore
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DATA_FILE = os.path.join(BASE_DIR, 'pages_ids.txt')
PEOPLE_DATA_FILE = os.path.join(BASE_DIR, 'people_ids.txt')

api_key = settings.SULU_API_KEY
headers = {
    'Authorization': f'Bearer {api_key}',
}
# Instagram API URL
INSTAGRAM_API_URL = "https://instagram-scraper-2022.p.sulu.sh/ig/"

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



# Process followings for a given user
def process_followings(username):
    print("process_followings")
    user_id = fetch_user_id(username)
    if not user_id:
        print("Could not retrieve user ID for the provided username.")
        return None, None

    followings = fetch_followings(user_id)
    print(f"Total followings retrieved: {len(followings)}")
    pages_data = load_data(PAGES_DATA_FILE)
    people_data = load_data(PEOPLE_DATA_FILE)
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

def calculate_score(hashmap1, hashmap2):
    score = sum((hashmap1[key] & hashmap2[key]) for key in hashmap1)
    return score




db = firestore.client()
def matchmake(ussid):
    try:
        # Get the document with the specified ussid
        user_doc = db.collection("users").document(ussid).get()
        
        if user_doc.exists:
            # Convert document to dictionary
            user_data = user_doc.to_dict()

            # Convert pages_hash and people_hash back to dictionaries if stored as strings
            if 'pages_hash' in user_data:
                user_data['pages_hash'] = json.loads(user_data['pages_hash'])
            if 'people_hash' in user_data:
                user_data['people_hash'] = json.loads(user_data['people_hash'])
        else:
            print("User not found")
            return None

    except Exception as e:
        print("Error:", e)
        return None
    
    # print(user_data['pages_hash'])
    # Fetch current user's flight_date and flight_number
    current_flight_date = user_data.get('flight_date')
    current_flight_number = user_data.get('flight_number')
    current_people_hash = user_data.get('people_hash')
    current_pages_hash = user_data.get('pages_hash')
    # Query for other users with the same flight_date and flight_number
    matching_users = db.collection("users").where("flight_date", "==", current_flight_date)\
                                            .where("flight_number", "==", current_flight_number)\
                                            .stream()

    # Store ussids of matching users, excluding the current user
    matching_ussids = [user.id for user in matching_users if user.id != ussid]
    score_list = []
    for match_ussid in matching_ussids:
        match_doc = db.collection("users").document(match_ussid).get()
        if match_doc.exists:
            match_data = match_doc.to_dict()
            # Parse pages_hash and people_hash as dictionaries if stored as JSON strings
            pages_hash = json.loads(match_data['pages_hash']) if 'pages_hash' in match_data else {}
            people_hash = json.loads(match_data['people_hash']) if 'people_hash' in match_data else {}
            people_score = calculate_score(pages_hash,current_pages_hash)
            pages_score = calculate_score(people_hash , current_people_hash)
            total_score = people_score + pages_score
            # score_list.append({"ussid": match_ussid, "total_score": total_score})
            # Collect additional fields and add to score list
            score_list.append({
                "ussid": match_ussid,
                "instaid": match_data.get("instaid"),
                "name": match_data.get("name"),
                "picture": match_data.get("picture"),
                "age": match_data.get("age"),
                "nationality": match_data.get("nationality"),
                "gender": match_data.get("gender"),
                "bio": match_data.get("bio"),
                "total_score": total_score
            })
    sorted_score_list = sorted(score_list, key=lambda x: x["total_score"], reverse=True)      
    for entry in sorted_score_list:
        print(f"User ID: {entry['ussid']}, Total Score: {entry['total_score']}, Name: {entry['name']}")
    return sorted_score_list