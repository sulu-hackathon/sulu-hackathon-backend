from django.urls import path
from . import views

urlpatterns = [
    path('fetch_flight_details/<str:search_param>/', views.fetch_flight_details, name='fetch_flight_details'),
    path('add_flight_details/', views.add_flight_details, name='add_flight_details'),
    path('autocomplete_flight_number/<str:flight_number>/', views.autocomplete_flight_number, name='autocomplete_flight_number')
]
