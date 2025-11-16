"""
URL patterns for Stats compatibility layer.
Provides all 2 endpoints matching Flutter app expectations.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.StatsView.as_view(), name='stats'),
    path('chart', views.StatsChartView.as_view(), name='stats-chart'),
]

