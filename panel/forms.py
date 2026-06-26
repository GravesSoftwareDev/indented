from django import forms
from courses.models import Course, Lesson, LessonQuestion, Assignment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'slug', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'slug', 'content', 'starter_code', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20}),
            'starter_code': forms.Textarea(attrs={'rows': 8}),
        }


class LessonQuestionForm(forms.ModelForm):
    class Meta:
        model = LessonQuestion
        fields = ['question_type', 'question', 'choices', 'expected_answer', 'order']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
            'choices': forms.Textarea(attrs={'rows': 5}),
            'expected_answer': forms.Textarea(attrs={'rows': 3}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'slug', 'description', 'instructions', 'buggy_code', 'expected_output', 'test_inputs', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'instructions': forms.Textarea(attrs={'rows': 8}),
            'buggy_code': forms.Textarea(attrs={'rows': 14}),
            'expected_output': forms.Textarea(attrs={'rows': 5}),
            'test_inputs': forms.Textarea(attrs={'rows': 3}),
        }
