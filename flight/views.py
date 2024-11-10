from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
import time
# Create your views here.

# Fetch the API key from settings or a file
headers = {
    "Authorization": f"Bearer {settings.SULU_API_KEY}"
}
@api_view(['GET'])
def fetch_flight_details(request, search_param):
    FLIGHT_URL =f"https://aerodatabox.p.sulu.sh/flights/Number/{search_param}/dates"
    try:
        # Make the API request
        response = requests.get(FLIGHT_URL, headers=headers)
        response.raise_for_status() 

        # Parse and return the JSON data
        data = response.json()
        today = datetime.now().date()
        # Sort and filter dates after today, then select the first 10
        filtered_dates = sorted(
            [date_str for date_str in data if datetime.strptime(date_str, "%Y-%m-%d").date() >= today]
        )[:10]
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch dates, flight does not exist or dates are not near enough"}, status=404)

    flight_details =[]
    for date in filtered_dates:
        FLIGHT_DETAILS_URL= f"https://aerodatabox.p.sulu.sh/flights/Number/{search_param}/{date}?withAircraftImage=false&withLocation=false"
        try:
            response = requests.get(FLIGHT_DETAILS_URL, headers=headers)
            response = response.json()

            flight_number_detail = [{
                "date": date,
                "departure_airport": response[0]["departure"]["airport"]["shortName"],
                "arrival_airport": response[0]["arrival"]["airport"]["shortName"],
                "departure_local_time": response[0]["departure"]["scheduledTime"]["utc"],
                "arrival__local_time": response[0]["arrival"]["scheduledTime"]["utc"],
                "airline_name": response[0]["airline"]["name"]
            }]
            flight_details = flight_details + flight_number_detail
        except requests.exceptions.RequestException as e:
            flight_number_detail = [{
                "date": date,
                "error": "Coudn't fetch details of this flight for this date"
            }]
            flight_details = flight_details + flight_number_detail
        time.sleep(1) #To avoid being rate limited

    return JsonResponse(flight_details, safe=False)


