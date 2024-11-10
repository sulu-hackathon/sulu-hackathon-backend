from django.urls import path
from . import views

urlpatterns = [
    path('fetch-dates/<str:search_param>/', views.fetch_possible_dates, name='fetch_possible_dates'),
]
