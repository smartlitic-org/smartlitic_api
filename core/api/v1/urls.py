from django.urls import path

from .views import LoggerLoadCompleteView


urlpatterns = [
    path('load-complete/', LoggerLoadCompleteView.as_view(), name='load-complete-logger'),
]
