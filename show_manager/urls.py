# main_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Built-in Django admin (Great for database management if you aren't building a custom UI for everything yet)
    path('admin/', admin.site.urls),

    # Route all API requests to the api app's urls.py
    path('api/', include('api.urls')),

    # Route UI
    path('', include('ui.urls')),
]
