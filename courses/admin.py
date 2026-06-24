from django.contrib import admin
from .models import Course, Lesson, LessonProgress, LessonQuestion, Assignment, AssignmentSubmission

class LessonQuestionInline(admin.TabularInline):
    model = LessonQuestion
    extra = 1
    fields = ['question_type', 'question', 'choices', 'expected_answer', 'order']

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

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    prepopulated_fields = {'slug': ('title',)}
    fields = ['course', 'title', 'slug', 'description', 'instructions', 'buggy_code', 'expected_output', 'order']

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment', 'passed', 'submitted_at']
    readonly_fields = ['user', 'assignment', 'code', 'passed', 'submitted_at']