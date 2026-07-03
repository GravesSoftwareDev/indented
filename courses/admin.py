from django.contrib import admin
from .models import Course, Lesson, LessonProgress, LessonQuestion, QuestionResponse, Assignment, AssignmentSubmission, FeedbackReport, CourseSurveyResponse

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

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'correct', 'submitted_at']
    list_filter = ['correct']
    readonly_fields = ['user', 'question', 'answer', 'correct', 'submitted_at']
    ordering = ['-submitted_at']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    prepopulated_fields = {'slug': ('title',)}
    fields = ['course', 'title', 'slug', 'description', 'instructions', 'buggy_code', 'expected_output', 'test_inputs', 'order']

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment', 'passed', 'submitted_at']
    readonly_fields = ['user', 'assignment', 'code', 'passed', 'submitted_at']

@admin.register(FeedbackReport)
class FeedbackReportAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'page', 'submitted_at', 'resolved']
    list_filter = ['category', 'resolved']
    list_editable = ['resolved']
    readonly_fields = ['user', 'category', 'message', 'page', 'submitted_at']
    ordering = ['-submitted_at']

@admin.register(CourseSurveyResponse)
class CourseSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'content_clarity', 'would_recommend', 'submitted_at']
    list_filter = ['course', 'rating', 'would_recommend']
    readonly_fields = ['user', 'course', 'rating', 'content_clarity', 'liked_most', 'improve', 'would_recommend', 'submitted_at']
    ordering = ['-submitted_at']