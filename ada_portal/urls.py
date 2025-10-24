from django.contrib import admin
from django.urls import path, include
from permits import views as permit_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('permits/', include('permits.urls')),
]

