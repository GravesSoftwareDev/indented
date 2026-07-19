from django.urls import path
from . import views

urlpatterns = [
    path('', views.sandbox_view, name='sandbox'),
    path('programs/', views.program_list, name='program_list'),
    path('favorites/', views.program_favorites, name='program_favorites'),
    path('explore/', views.program_gallery, name='program_gallery'),
    path('programs/save/', views.program_save, name='program_save'),
    path('programs/<int:pk>/', views.sandbox_view, name='sandbox_edit'),
    path('programs/<int:pk>/toggle-public/', views.program_toggle_public, name='program_toggle_public'),
    path('programs/<int:pk>/delete/', views.program_delete, name='program_delete'),
    path('programs/<int:pk>/favorite/', views.program_favorite_toggle, name='program_favorite_toggle'),
    path('s/<slug:slug>/', views.program_share_view, name='program_share'),
    path('s/<slug:slug>/fork/', views.program_fork, name='program_fork'),
]