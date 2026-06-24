from django.contrib import admin
from .models import Course, Lesson, LessonProgress, LessonQuestion

class LessonQuestionInline(admin.TabularInline):
    model = LessonQuestion
    extra = 1
    fields = ['question', 'expected_answer', 'order']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'created_at']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    prepopulated_fields = {'slug': ('title',)}
    fields = ['course', 'title', 'slug', 'content', 'starter_code', 'order']
    inlines = [LessonQuestionInline]

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at']