from django.contrib import admin
from django.urls import path, include
from riders import views  # Assuming your views are in the same directory

urlpatterns = [
    # Azure AD / ADFS auth endpoints under /ADA/
    path('ADA/oauth2/', include('django_auth_adfs.urls')),
    path('ADA/', include([
           path('admin/', admin.site.urls),

           path('', views.home, name='home'),
           path('riders/search/', views.search_riders, name='search_riders'),
           path('riders/<int:pk>/', views.rider_detail, name='rider_detail'),
           path('riders/new/', views.rider_create, name='rider_create'),
           path('riders/<int:pk>/save/', views.rider_save, name='rider_save'),
           path('riders/<int:pk>/inactive/', views.rider_inactive, name='rider_inactive'),
           path('reports/finance-transmittal/', views.finance_transmittal, name='finance_transmittal'),
           path('riders/<int:pk>/tickets/new/', views.ticket_create, name='ticket_create'),
       ])),
   ]

