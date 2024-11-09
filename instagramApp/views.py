import requests
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import HttpResponse

# Base URL for the Sulu Instagram API
INSTAGRAM_API_URL = "https://instagram-scraper-2022.p.sulu.sh/ig/"


@api_view(['GET'])
def validate_instagram(request, username):
    # Step 1: Retrieve user ID
    user_id_url = f"{INSTAGRAM_API_URL}user_id/?user={username}"
    api_key = settings.SULU_API_KEY

    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    
    try:
        # Request to get the user ID
        response = requests.get(user_id_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get('id')
            if not user_id:
                return HttpResponse(status=404)  # User ID not found
            
            # Step 2: Retrieve following list using the user ID
            following_url = f"{INSTAGRAM_API_URL}followings/?id_user={user_id}"
            following_response = requests.get(following_url, headers=headers)
            
            if following_response.status_code == 200:
                following_data = following_response.json()
                following_list = following_data.get('users', [])
                
                # If following list is empty, return 404
                if not following_list:
                    return HttpResponse(status=404)
                
                # If following list is non-empty, return 200
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=404)
        
        else:
            return HttpResponse(status=404)
    
    except requests.exceptions.RequestException:
        return HttpResponse(status=500)