from django.urls import path

from .views import ComponentsListView


urlpatterns = [
    path('components/<int:project_id>/', ComponentsListView.as_view(), name='components-list'),
]
