from django import forms
from django.contrib.auth.models import User
from courses.models import Course, Lesson, LessonQuestion, Assignment, Announcement


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


class AnnouncementForm(forms.ModelForm):
    starts_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    ends_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Announcement
        fields = ['title', 'body', 'starts_at', 'ends_at']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
        }

    def clean(self):
        cleaned_data = super().clean()
        starts_at = cleaned_data.get('starts_at')
        ends_at = cleaned_data.get('ends_at')
        if starts_at and ends_at and ends_at <= starts_at:
            raise forms.ValidationError('End time must be after the start time.')
        return cleaned_data


class StudentCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    is_staff = forms.BooleanField(required=False, label='Staff access')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username


class StudentEditForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank to keep current password.',
    )
    is_staff = forms.BooleanField(required=False, label='Staff access')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self._user:
            qs = qs.exclude(pk=self._user.pk)
        if qs.exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username
