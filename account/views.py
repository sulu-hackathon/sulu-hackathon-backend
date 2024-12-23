from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from firebase_admin import firestore
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from instagramApp.matchmaker import process_followings

db = firestore.client()
@csrf_exempt  # Disable CSRF for simplicity; consider proper CSRF handling in production
@api_view(['POST'])
def create_user(request):
    if request.method == "POST":
        # Parse JSON data from the request body
        data = json.loads(request.body)
        ussid = data.get("ussid")
        instaid = data.get("instaid")
        name = data.get("name")
        bio = data.get("bio")
        picture = data.get("picture")
        age = data.get("age")
        nationality = data.get("nationality")
        gender = data.get("gender")

        if not ussid:
            return JsonResponse({"error": "ussid is required"}, status=400)

        pages_hash , people_hash = process_followings(instaid)
        # Prepare the data to store in Firestore
        user_data = {
            "instaid": instaid,
            "name": name,
            "picture": picture,  # Storing as base64
            "age": age,
            "nationality": nationality,
            "gender": gender,
            "bio": bio,
            "pages_hash":json.dumps(pages_hash),
            "people_hash": json.dumps(people_hash)
        }

        # Save the data in the 'users' collection with document ID as `ussid`
        try:
            db.collection("users").document(ussid).set(user_data)
            return JsonResponse({"message": "User created successfully"}, status=201)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)