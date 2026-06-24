from django.urls import path
from . import views

urlpatterns = [
    path('', views.sandbox_view, name='sandbox')
]