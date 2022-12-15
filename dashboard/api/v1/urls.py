from django.urls import path

from .views import ComponentsListView, DashboardGeneralView, DashboardComponentsView


urlpatterns = [
    path('components/<int:project_id>/', ComponentsListView.as_view(), name='components-list'),
    path('general-view/<int:project_id>/', DashboardGeneralView.as_view(), name='general-view'),
    path('components-view/<int:project_id>/', DashboardComponentsView.as_view(), name='components-view'),
]
