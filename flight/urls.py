from django.urls import path
from . import views

urlpatterns = [
    path('fetch_flight_details/<str:search_param>/', views.fetch_flight_details, name='fetch_flight_details'),
]
