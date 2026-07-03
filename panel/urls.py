from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('courses/<slug:slug>/delete/', views.course_delete, name='course_delete'),

    # Lessons (nested under courses)
    path('courses/<slug:course_slug>/lessons/new/', views.lesson_create, name='lesson_create'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/edit/', views.lesson_edit, name='lesson_edit'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/delete/', views.lesson_delete, name='lesson_delete'),

    # Questions (nested under lessons)
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/questions/', views.question_list, name='question_list'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/questions/new/', views.question_create, name='question_create'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    # Assignments (nested under courses)
    path('courses/<slug:course_slug>/assignments/new/', views.assignment_create, name='assignment_create'),
    path('courses/<slug:course_slug>/assignments/<slug:assignment_slug>/edit/', views.assignment_edit, name='assignment_edit'),
    path('courses/<slug:course_slug>/assignments/<slug:assignment_slug>/delete/', views.assignment_delete, name='assignment_delete'),

    # Feedback
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:pk>/toggle/', views.feedback_toggle, name='feedback_toggle'),

    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/new/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    # Students
    path('students/', views.students, name='students'),
    path('students/new/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    # Surveys
    path('surveys/', views.surveys, name='surveys'),
]
