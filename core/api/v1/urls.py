from django.urls import path

from .views import LoggerClickView


urlpatterns = [
    path('click/', LoggerClickView.as_view(), name='click-logger'),
]
