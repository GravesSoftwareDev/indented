from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Course(models.Model):
    title = models. CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title       = models.CharField(max_length=200)
    slug        = models.SlugField()
    content     = models.TextField()
    starter_code = models.TextField(blank=True, default='')
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'slug']

    def __str__(self):
        return f"{self.course.title} — {self.title}"
    
class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user','lesson']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} Completed: {self.completed}"
    
class LessonQuestion(models.Model):
    QUESTION_TYPES = [
        ('output', 'Paste Output'),
        ('short_answer', 'Short Answer'),
        ('true_false', 'True / False'),
        ('multiple_choice', 'Multiple Choice'),
        ('ordering', 'Put in Order'),
    ]

    lesson          = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_type   = models.CharField(max_length=20, choices=QUESTION_TYPES, default='output')
    question        = models.TextField()
    choices         = models.TextField(blank=True, default='', help_text='One item per line. For multiple choice: options (expected_answer = correct one). For ordering: items in correct order (expected_answer unused).')
    expected_answer = models.TextField()
    order           = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} — Q{self.order}"

    def get_choices(self):
        return [c.strip() for c in self.choices.splitlines() if c.strip()]


class QuestionResponse(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_responses')
    question     = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, related_name='responses')
    answer       = models.TextField(blank=True, default='')
    correct      = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username} — {self.question} — {'✓' if self.correct else '✗'}"


class Assignment(models.Model):
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title           = models.CharField(max_length=200)
    slug            = models.SlugField()
    description     = models.TextField(blank=True, default='')
    instructions    = models.TextField()
    buggy_code      = models.TextField()
    expected_output = models.TextField()
    test_inputs     = models.TextField(blank=True, default='', help_text='One input value per line, in the order they will be fed to input() calls when the code runs.')
    order           = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'slug']

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    def get_test_inputs(self):
        return [line.strip() for line in self.test_inputs.splitlines() if line.strip()]


class AssignmentSubmission(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    assignment   = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    code         = models.TextField()
    passed       = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} — {self.assignment.title} — {'✓' if self.passed else '✗'}"


class FeedbackReport(models.Model):
    CATEGORY_CHOICES = [
        ('bug', 'Bug Report'),
        ('feedback', 'General Feedback'),
        ('suggestion', 'Suggestion'),
    ]
    user         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_reports')
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='feedback')
    message      = models.TextField()
    page         = models.CharField(max_length=500, blank=True, default='', help_text='Page or URL where the issue occurred')
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved     = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.get_category_display()} — {self.user or 'anonymous'} — {self.submitted_at:%Y-%m-%d}"


class Announcement(models.Model):
    title      = models.CharField(max_length=200)
    body       = models.TextField(help_text='Supports the same markdown formatting as lesson content.')
    starts_at  = models.DateTimeField(help_text='Announcement starts showing to students at this time.')
    ends_at    = models.DateTimeField(help_text='Announcement stops showing after this time.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_live(self, at=None):
        at = at or timezone.now()
        return self.starts_at <= at <= self.ends_at


class AnnouncementDismissal(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_dismissals')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='dismissals')
    dismissed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'announcement']

    def __str__(self):
        return f"{self.user.username} — {self.announcement.title}"


class CourseSurveyResponse(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_responses')
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='survey_responses')
    rating          = models.PositiveSmallIntegerField(help_text='Overall course rating 1–5')
    content_clarity = models.PositiveSmallIntegerField(help_text='How well you understood the content 1–5')
    liked_most      = models.TextField(blank=True, default='')
    improve         = models.TextField(blank=True, default='')
    would_recommend = models.BooleanField(null=True, blank=True)
    submitted_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} — {self.course.title} — {self.rating}/5"