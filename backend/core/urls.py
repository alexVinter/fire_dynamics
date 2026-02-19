from django.urls import path

from . import views

urlpatterns = [
    path("models/", views.ModelsSearchView.as_view(), name="api-models"),
    path("zones/", views.ZonesListView.as_view(), name="api-zones"),
    path("calculate/", views.CalculateView.as_view(), name="api-calculate"),
    path("calculations/save/", views.SaveCalculationView.as_view(), name="api-calculations-save"),
]
