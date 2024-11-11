from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
import time
from firebase_admin import firestore
from django.views.decorators.csrf import csrf_exempt
import json


db = firestore.client()
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


@csrf_exempt  # Disable CSRF for simplicity; consider proper CSRF handling in production
@api_view(['POST'])
def add_flight_details(request):
    if request.method == "POST":
        # Parse JSON data from the request body
        data = json.loads(request.body)
        ussid = data.get("ussid")
        flight_number = data.get("flight_number")
        flight_date = data.get("flight_date")
        if not ussid:
            return JsonResponse({"error": "ussid is required"}, status=400)

        user_flight_details = {
            "flight_number" : flight_number,
            "flight_date" : flight_date
        }
        # Save the data in the 'users' collection with document ID as `ussid`
        try:
            db.collection("users").document(ussid).set(user_flight_details)
            return JsonResponse({"message": f"Flight details pushed successfully for user"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    

@api_view(['GET'])
def autocomplete_flight_number(request,flight_number):
    FLIGHT_NUMBER_URL =f"https://aerodatabox.p.sulu.sh/flights/search/term?q={flight_number}&limit=5"
    try:
        # Make the API request
        response = requests.get(FLIGHT_NUMBER_URL, headers=headers)
        response.raise_for_status()
        response = response.json()
        flight_numbers = [item["number"] for item in response.get("items", [])]
        if flight_numbers is None:
            return None
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch numbers"}, status=404)
    return JsonResponse(flight_numbers, safe=False)




