import json
from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User

from courses.models import (
    Course, Lesson, LessonProgress, LessonQuestion,
    Assignment, AssignmentSubmission, FeedbackReport, CourseSurveyResponse,
    Announcement,
)
from .forms import CourseForm, LessonForm, LessonQuestionForm, AssignmentForm, StudentCreateForm, StudentEditForm, AnnouncementForm


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_staff:
            return redirect('course_list')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Dashboard ────────────────────────────────────────────────────────────────

@staff_required
def dashboard(request):
    stats = {
        'courses':            Course.objects.count(),
        'lessons':            Lesson.objects.count(),
        'assignments':        Assignment.objects.count(),
        'students':           User.objects.filter(is_staff=False, is_superuser=False).count(),
        'lesson_completions': LessonProgress.objects.filter(completed=True).count(),
        'assignments_passed': AssignmentSubmission.objects.filter(passed=True).count(),
        'unresolved_feedback': FeedbackReport.objects.filter(resolved=False).count(),
        'survey_responses':   CourseSurveyResponse.objects.count(),
    }
    recent_feedback = FeedbackReport.objects.filter(resolved=False).order_by('-submitted_at')[:5]
    return render(request, 'panel/dashboard.html', {
        'stats': stats,
        'recent_feedback': recent_feedback,
        'panel_section': 'dashboard',
    })


# ─── Courses ──────────────────────────────────────────────────────────────────

@staff_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'panel/course_list.html', {
        'courses': courses,
        'panel_section': 'courses',
    })


@staff_required
def course_create(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        course = form.save(commit=False)
        if not course.slug:
            course.slug = slugify(course.title)
        course.save()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/course_form.html', {
        'form': form,
        'title': 'New Course',
        'submit_label': 'Create Course',
        'cancel_url': reverse('panel:course_list'),
        'panel_section': 'courses',
    })


@staff_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.prefetch_related('questions').all()
    assignments = course.assignments.all()
    return render(request, 'panel/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'assignments': assignments,
        'panel_section': 'courses',
    })


@staff_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    form = CourseForm(request.POST or None, instance=course)
    if form.is_valid():
        form.save()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/course_form.html', {
        'form': form,
        'course': course,
        'title': f'Edit: {course.title}',
        'submit_label': 'Save Changes',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


@staff_required
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        course.delete()
        return redirect('panel:course_list')
    return render(request, 'panel/confirm_delete.html', {
        'object_name': course.title,
        'object_type': 'course',
        'warning': 'This will permanently delete all lessons, questions, and assignments inside this course.',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


# ─── Lessons ──────────────────────────────────────────────────────────────────

@staff_required
def lesson_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    form = LessonForm(request.POST or None)
    if form.is_valid():
        lesson = form.save(commit=False)
        lesson.course = course
        if not lesson.slug:
            lesson.slug = slugify(lesson.title)
        lesson.save()
        return redirect('panel:question_list', course_slug=course.slug, lesson_slug=lesson.slug)
    return render(request, 'panel/lesson_form.html', {
        'form': form,
        'course': course,
        'title': 'New Lesson',
        'submit_label': 'Create Lesson',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


@staff_required
def lesson_edit(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    form = LessonForm(request.POST or None, instance=lesson)
    if form.is_valid():
        form.save()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/lesson_form.html', {
        'form': form,
        'course': course,
        'lesson': lesson,
        'title': f'Edit Lesson: {lesson.title}',
        'submit_label': 'Save Changes',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


@staff_required
def lesson_delete(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    if request.method == 'POST':
        lesson.delete()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/confirm_delete.html', {
        'object_name': lesson.title,
        'object_type': 'lesson',
        'warning': 'This will also delete all check-your-understanding questions attached to this lesson.',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


# ─── Questions ────────────────────────────────────────────────────────────────

@staff_required
def question_list(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    questions = lesson.questions.all()
    return render(request, 'panel/question_list.html', {
        'course': course,
        'lesson': lesson,
        'questions': questions,
        'panel_section': 'courses',
    })


@staff_required
def question_create(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    form = LessonQuestionForm(request.POST or None)
    if form.is_valid():
        question = form.save(commit=False)
        question.lesson = lesson
        question.save()
        return redirect('panel:question_list', course_slug=course.slug, lesson_slug=lesson.slug)
    return render(request, 'panel/question_form.html', {
        'form': form,
        'course': course,
        'lesson': lesson,
        'title': 'New Question',
        'submit_label': 'Add Question',
        'cancel_url': reverse('panel:question_list', kwargs={'course_slug': course.slug, 'lesson_slug': lesson.slug}),
        'panel_section': 'courses',
    })


@staff_required
def question_edit(request, course_slug, lesson_slug, question_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    question = get_object_or_404(LessonQuestion, id=question_id, lesson=lesson)
    form = LessonQuestionForm(request.POST or None, instance=question)
    if form.is_valid():
        form.save()
        return redirect('panel:question_list', course_slug=course.slug, lesson_slug=lesson.slug)
    return render(request, 'panel/question_form.html', {
        'form': form,
        'course': course,
        'lesson': lesson,
        'question': question,
        'title': f'Edit Question {question.order}',
        'submit_label': 'Save Changes',
        'cancel_url': reverse('panel:question_list', kwargs={'course_slug': course.slug, 'lesson_slug': lesson.slug}),
        'panel_section': 'courses',
    })


@staff_required
def question_delete(request, course_slug, lesson_slug, question_id):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    question = get_object_or_404(LessonQuestion, id=question_id, lesson=lesson)
    if request.method == 'POST':
        question.delete()
        return redirect('panel:question_list', course_slug=course.slug, lesson_slug=lesson.slug)
    return render(request, 'panel/confirm_delete.html', {
        'object_name': f'Q{question.order}: {question.question[:80]}',
        'object_type': 'question',
        'warning': None,
        'cancel_url': reverse('panel:question_list', kwargs={'course_slug': course.slug, 'lesson_slug': lesson.slug}),
        'panel_section': 'courses',
    })


# ─── Assignments ──────────────────────────────────────────────────────────────

@staff_required
def assignment_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    form = AssignmentForm(request.POST or None)
    if form.is_valid():
        assignment = form.save(commit=False)
        assignment.course = course
        if not assignment.slug:
            assignment.slug = slugify(assignment.title)
        assignment.save()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/assignment_form.html', {
        'form': form,
        'course': course,
        'title': 'New Assignment',
        'submit_label': 'Create Assignment',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


@staff_required
def assignment_edit(request, course_slug, assignment_slug):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, slug=assignment_slug, course=course)
    form = AssignmentForm(request.POST or None, instance=assignment)
    if form.is_valid():
        form.save()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/assignment_form.html', {
        'form': form,
        'course': course,
        'assignment': assignment,
        'title': f'Edit: {assignment.title}',
        'submit_label': 'Save Changes',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


@staff_required
def assignment_delete(request, course_slug, assignment_slug):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, slug=assignment_slug, course=course)
    if request.method == 'POST':
        assignment.delete()
        return redirect('panel:course_detail', slug=course.slug)
    return render(request, 'panel/confirm_delete.html', {
        'object_name': assignment.title,
        'object_type': 'assignment',
        'warning': 'This will permanently delete all student submissions for this assignment.',
        'cancel_url': reverse('panel:course_detail', kwargs={'slug': course.slug}),
        'panel_section': 'courses',
    })


# ─── Feedback ─────────────────────────────────────────────────────────────────

@staff_required
def feedback_list(request):
    show = request.GET.get('show', 'unresolved')
    if show == 'all':
        reports = FeedbackReport.objects.all()
    elif show == 'resolved':
        reports = FeedbackReport.objects.filter(resolved=True)
    else:
        show = 'unresolved'
        reports = FeedbackReport.objects.filter(resolved=False)
    return render(request, 'panel/feedback_list.html', {
        'reports': reports,
        'show': show,
        'unresolved_count': FeedbackReport.objects.filter(resolved=False).count(),
        'panel_section': 'feedback',
    })


@staff_required
def feedback_toggle(request, pk):
    if request.method == 'POST':
        report = get_object_or_404(FeedbackReport, pk=pk)
        report.resolved = not report.resolved
        report.save()
        next_url = request.POST.get('next', reverse('panel:feedback_list'))
        return redirect(next_url)
    return redirect('panel:feedback_list')


# ─── Announcements ────────────────────────────────────────────────────────────

@staff_required
def announcement_list(request):
    now = timezone.now()
    announcements = Announcement.objects.all()
    return render(request, 'panel/announcement_list.html', {
        'announcements': announcements,
        'now': now,
        'panel_section': 'announcements',
    })


@staff_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('panel:announcement_list')
    return render(request, 'panel/announcement_form.html', {
        'form': form,
        'title': 'New Announcement',
        'submit_label': 'Create Announcement',
        'cancel_url': reverse('panel:announcement_list'),
        'panel_section': 'announcements',
    })


@staff_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=announcement)
    if form.is_valid():
        form.save()
        return redirect('panel:announcement_list')
    return render(request, 'panel/announcement_form.html', {
        'form': form,
        'announcement': announcement,
        'title': f'Edit: {announcement.title}',
        'submit_label': 'Save Changes',
        'cancel_url': reverse('panel:announcement_list'),
        'panel_section': 'announcements',
    })


@staff_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        return redirect('panel:announcement_list')
    return render(request, 'panel/confirm_delete.html', {
        'object_name': announcement.title,
        'object_type': 'announcement',
        'warning': None,
        'cancel_url': reverse('panel:announcement_list'),
        'panel_section': 'announcements',
    })


# ─── Students ─────────────────────────────────────────────────────────────────

@staff_required
def students(request):
    users = User.objects.filter(is_superuser=False).order_by('username')
    total_lessons = Lesson.objects.count()
    total_assignments = Assignment.objects.count()

    student_data = []
    for user in users:
        completed = LessonProgress.objects.filter(user=user, completed=True).count()
        passed = AssignmentSubmission.objects.filter(
            user=user, passed=True
        ).values('assignment').distinct().count()
        surveys = CourseSurveyResponse.objects.filter(user=user).count()
        student_data.append({
            'user': user,
            'completed': completed,
            'passed': passed,
            'surveys': surveys,
            'lesson_pct': int(completed / total_lessons * 100) if total_lessons else 0,
        })

    return render(request, 'panel/students.html', {
        'student_data': student_data,
        'total_lessons': total_lessons,
        'total_assignments': total_assignments,
        'panel_section': 'students',
    })


@staff_required
def student_detail(request, pk):
    student = get_object_or_404(User, pk=pk)
    courses = Course.objects.prefetch_related('lessons', 'assignments').all()

    course_data = []
    for course in courses:
        lessons = list(course.lessons.all())
        assignments = list(course.assignments.all())

        completed_ids = set(
            LessonProgress.objects.filter(user=student, lesson__in=lessons, completed=True)
            .values_list('lesson_id', flat=True)
        )
        passed_ids = set(
            AssignmentSubmission.objects.filter(user=student, assignment__in=assignments, passed=True)
            .values_list('assignment_id', flat=True)
        )

        try:
            survey = CourseSurveyResponse.objects.get(user=student, course=course)
        except CourseSurveyResponse.DoesNotExist:
            survey = None

        course_data.append({
            'course': course,
            'lessons': [(l, l.id in completed_ids) for l in lessons],
            'assignments': [(a, a.id in passed_ids) for a in assignments],
            'survey': survey,
        })

    return render(request, 'panel/student_detail.html', {
        'student': student,
        'course_data': course_data,
        'panel_section': 'students',
    })


@staff_required
def student_create(request):
    form = StudentCreateForm(request.POST or None)
    if form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data.get('email', ''),
            password=form.cleaned_data['password'],
        )
        user.is_staff = form.cleaned_data.get('is_staff', False)
        user.save()
        return redirect('panel:student_detail', pk=user.pk)
    return render(request, 'panel/student_form.html', {
        'form': form,
        'title': 'Add Student',
        'submit_label': 'Create Account',
        'cancel_url': reverse('panel:students'),
        'panel_section': 'students',
    })


@staff_required
def student_edit(request, pk):
    student = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StudentEditForm(request.POST, user=student)
        if form.is_valid():
            student.username = form.cleaned_data['username']
            student.email = form.cleaned_data.get('email', '')
            student.is_staff = form.cleaned_data.get('is_staff', False)
            if form.cleaned_data.get('password'):
                student.set_password(form.cleaned_data['password'])
            student.save()
            return redirect('panel:student_detail', pk=student.pk)
    else:
        form = StudentEditForm(initial={
            'username': student.username,
            'email': student.email,
            'is_staff': student.is_staff,
        }, user=student)
    return render(request, 'panel/student_form.html', {
        'form': form,
        'student': student,
        'title': f'Edit: {student.username}',
        'submit_label': 'Save Changes',
        'cancel_url': reverse('panel:student_detail', kwargs={'pk': student.pk}),
        'panel_section': 'students',
    })


@staff_required
def student_delete(request, pk):
    student = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('panel:students')
    return render(request, 'panel/confirm_delete.html', {
        'object_name': student.username,
        'object_type': 'user',
        'warning': 'This will permanently delete the account and all progress data for this user.',
        'cancel_url': reverse('panel:student_detail', kwargs={'pk': student.pk}),
        'panel_section': 'students',
    })


# ─── Surveys ──────────────────────────────────────────────────────────────────

@staff_required
def surveys(request):
    courses = Course.objects.all()
    course_slug = request.GET.get('course', '')

    qs = CourseSurveyResponse.objects.select_related('user', 'course')
    selected_course_title = 'All Courses'
    if course_slug:
        qs = qs.filter(course__slug=course_slug)
        try:
            selected_course_title = Course.objects.get(slug=course_slug).title
        except Course.DoesNotExist:
            course_slug = ''

    total = qs.count()

    rating_counts  = [qs.filter(rating=i).count() for i in range(1, 6)]
    clarity_counts = [qs.filter(content_clarity=i).count() for i in range(1, 6)]
    yes_count      = qs.filter(would_recommend=True).count()
    no_count       = qs.filter(would_recommend=False).count()
    skip_count     = qs.filter(would_recommend__isnull=True).count()

    avg_rating  = round(sum(i * rating_counts[i-1]  for i in range(1, 6)) / total, 1) if total else None
    avg_clarity = round(sum(i * clarity_counts[i-1] for i in range(1, 6)) / total, 1) if total else None

    liked_responses   = list(qs.exclude(liked_most='').values('liked_most',   'course__title', 'user__username'))
    improve_responses = list(qs.exclude(improve='').values('improve', 'course__title', 'user__username'))

    chart_data = json.dumps({
        'ratings':    rating_counts,
        'clarity':    clarity_counts,
        'recommend':  [yes_count, no_count, skip_count],
    })

    return render(request, 'panel/surveys.html', {
        'courses':              courses,
        'selected_course':      course_slug,
        'selected_course_title': selected_course_title,
        'chart_data':           chart_data,
        'total':                total,
        'avg_rating':           avg_rating,
        'avg_clarity':          avg_clarity,
        'recommend_yes':        yes_count,
        'recommend_no':         no_count,
        'liked_responses':      liked_responses,
        'improve_responses':    improve_responses,
        'panel_section':        'surveys',
    })
