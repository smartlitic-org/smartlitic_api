from django.urls import path, include


urlpatterns = [
    path('v1/', include('dashboard.api.v1.urls')),
]
