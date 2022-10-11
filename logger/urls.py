from django.urls import path, include


urlpatterns = [
    path('v1/', include('logger.api.v1.urls')),
]
