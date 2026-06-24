from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('<slug:course_slug>/<slug:lesson_slug>/complete/', views.mark_complete, name='mark_complete'),
    path('question/<int:question_id>/check/', views.check_answer, name='check_answer'),
    path('<slug:course_slug>/assignments/<slug:assignment_slug>/', views.assignment_detail, name='assignment_detail'),
    path('<slug:course_slug>/assignments/<slug:assignment_slug>/submit/', views.submit_assignment, name='submit_assignment'),
]