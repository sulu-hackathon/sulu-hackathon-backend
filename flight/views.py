from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from datetime import datetime, timedelta

# Create your views here.

# Fetch the API key from settings or a file
headers = {
    "Authorization": f"Bearer {settings.SULU_API_KEY}"
}
@api_view(['GET'])
def fetch_possible_dates(request, search_param):
    FLIGHT_URL =f"https://aerodatabox.p.sulu.sh/flights/Number/{search_param}/dates"
    try:
        # Make the API request
        response = requests.get(FLIGHT_URL, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Parse and return the JSON data
        data = response.json()

        # Filter to include only the next 10 dates from today
        today = datetime.now().date()
        ten_days_from_today = today + timedelta(days=10)
        
        filtered_dates = [
            date_str for date_str in data
            if today <= datetime.strptime(date_str, "%Y-%m-%d").date() <= ten_days_from_today
        ][:10]  # Limit to the first 10 days

        return JsonResponse(filtered_dates, safe=False)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch dates, flight does not exist or dates are not near enough"}, status=404)

