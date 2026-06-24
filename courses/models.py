from django.db import models
from django.contrib.auth.models import User

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