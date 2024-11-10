from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view

# Create your views here.

# Fetch the API key from settings or a file
headers = {
    "Authorization": f"Bearer {settings.SULU_API_KEY}"
}
@api_view(['GET'])
def fetch_possible_dates(request, search_by, search_param):
    FLIGHT_URL =f"https://aerodatabox.p.sulu.sh/flights/{search_by}/{search_param}/dates"
    try:
        # Make the API request
        response = requests.get(FLIGHT_URL, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Parse and return the JSON data
        data = response.json()
        return JsonResponse(data, safe=False)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch dates", "details": str(e)}, status=500)

