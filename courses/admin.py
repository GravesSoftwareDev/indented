from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title',  'order','created_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    prepopulated_fields = {'slug': ('title',)}
    fields = ['course', 'title', 'slug', 'content', 'starter_code', 'order']