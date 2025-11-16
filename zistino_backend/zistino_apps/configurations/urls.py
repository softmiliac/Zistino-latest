from django.urls import path
from . import views

urlpatterns = [
    path('client/search', views.ConfigurationSearchView.as_view(), name='config-client-search'),
]

