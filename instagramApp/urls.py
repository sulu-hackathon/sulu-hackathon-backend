from django.urls import path
from . import views

urlpatterns = [
    path('validate_instagram/<str:username>/', views.validate_instagram),
    path('find_matches/', views.find_matches)
]
