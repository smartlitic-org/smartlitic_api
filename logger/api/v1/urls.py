from django.urls import path

from .views import LoggerLoadCompleteView, LoggerRateView


urlpatterns = [
    path('load-complete/', LoggerLoadCompleteView.as_view(), name='load-complete-logger'),
    path('rate/', LoggerRateView.as_view(), name='rate-logger'),
]
