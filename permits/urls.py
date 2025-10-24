from django.urls import path
from . import views

app_name = 'permits'

urlpatterns = [
    path('', views.home, name='home'),
    path('history/', views.history, name='history'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('address_picker/', views.address_picker, name='address_picker'),
]
