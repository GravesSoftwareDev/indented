import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .models import Course, Lesson, LessonProgress, LessonQuestion, QuestionResponse, Assignment, AssignmentSubmission, FeedbackReport, CourseSurveyResponse, Announcement, AnnouncementDismissal

@login_required
def course_list(request):
    courses = Course.objects.all()
    unlocked_ids = {
        course.id
        for course in courses
        if request.user.is_staff or _is_course_unlocked(request.user, course)
    }
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'unlocked_ids': unlocked_ids,
    })

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if not request.user.is_staff and not _is_course_unlocked(request.user, course):
        return redirect('course_list')

    lessons = course.lessons.all()

    completed_ids = set(
        LessonProgress.objects.filter(
            user=request.user,
            lesson__in=lessons,
            completed=True
        ).values_list('lesson_id', flat=True)
    )

    total = lessons.count()
    completed_count = len(completed_ids)
    progress_pct = int((completed_count / total) * 100) if total > 0 else 0

    assignments = course.assignments.all()
    passed_assignment_ids = set(
        AssignmentSubmission.objects.filter(
            user=request.user,
            assignment__in=assignments,
            passed=True,
        ).values_list('assignment_id', flat=True)
    )
    assignments_locked = not request.user.is_staff and (completed_count < total)

    assignment_count = assignments.count()
    all_assignments_passed = len(passed_assignment_ids) >= assignment_count
    course_fully_complete = (
        total > 0 and completed_count >= total and
        (assignment_count == 0 or all_assignments_passed)
    )
    survey_submitted = (
        CourseSurveyResponse.objects.filter(user=request.user, course=course).exists()
        if course_fully_complete else False
    )

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'completed_ids': completed_ids,
        'completed_count': completed_count,
        'total': total,
        'progress_pct': progress_pct,
        'assignments': assignments,
        'passed_assignment_ids': passed_assignment_ids,
        'assignments_locked': assignments_locked,
        'course_fully_complete': course_fully_complete,
        'survey_submitted': survey_submitted,
    })

@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if not request.user.is_staff and not _is_course_unlocked(request.user, course):
        return redirect('course_list')

    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    questions = list(lesson.questions.all())

    saved_responses = {
        r.question_id: r
        for r in QuestionResponse.objects.filter(user=request.user, question__in=questions)
    }

    initial_results = {}
    for question in questions:
        resp = saved_responses.get(question.id)
        question.saved_response = resp

        choices = question.get_choices()
        if question.question_type == 'ordering' and resp and resp.answer:
            saved_order = [line.strip() for line in resp.answer.split('\n') if line.strip()]
            if sorted(saved_order) == sorted(choices):
                choices = saved_order
        question.display_choices = choices

        if resp:
            if question.question_type == 'ordering':
                expected = None if resp.correct else ' → '.join(question.get_choices())
            else:
                expected = None if resp.correct else question.expected_answer.strip()
            initial_results[question.id] = {'correct': resp.correct, 'expected': expected}

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    next_lesson = course.lessons.filter(order__gt=lesson.order).order_by('order').first()

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'questions': questions,
        'next_lesson': next_lesson,
        'initial_results_json': json.dumps(initial_results),
    })

@login_required
def mark_complete(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if not request.user.is_staff and not _is_course_unlocked(request.user, course):
        return redirect('course_list')

    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'completed_at': f'{progress.completed_at:%b} {progress.completed_at.day}, {progress.completed_at:%Y}',
        })

    return redirect('lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)

@login_required
def check_answer(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    question = get_object_or_404(LessonQuestion, id=question_id)
    user_answer = request.POST.get('answer', '').strip()

    if question.question_type == 'ordering':
        correct_order = question.get_choices()
        user_order = [item.strip() for item in user_answer.split('\n') if item.strip()]
        correct = [i.lower() for i in user_order] == [i.lower() for i in correct_order]
        QuestionResponse.objects.update_or_create(
            user=request.user, question=question,
            defaults={'answer': user_answer, 'correct': correct},
        )
        return JsonResponse({
            'correct': correct,
            'expected': ' → '.join(correct_order) if not correct else None,
        })

    expected = question.expected_answer.strip()
    correct = user_answer.lower() == expected.lower()

    QuestionResponse.objects.update_or_create(
        user=request.user, question=question,
        defaults={'answer': user_answer, 'correct': correct},
    )

    return JsonResponse({
        'correct': correct,
        'expected': expected if not correct else None,
    })


def _all_lessons_complete(user, course):
    total = course.lessons.count()
    if total == 0:
        return True
    completed = LessonProgress.objects.filter(
        user=user, lesson__course=course, completed=True
    ).count()
    return completed >= total


def _is_course_complete(user, course):
    total = course.lessons.count()
    if total == 0:
        return False
    completed = LessonProgress.objects.filter(
        user=user, lesson__course=course, completed=True
    ).count()
    if completed < total:
        return False
    assignment_count = course.assignments.count()
    if assignment_count == 0:
        return True
    passed = AssignmentSubmission.objects.filter(
        user=user, assignment__course=course, passed=True
    ).values('assignment').distinct().count()
    return passed >= assignment_count


def _is_course_unlocked(user, course):
    previous = Course.objects.filter(order__lt=course.order).order_by('-order').first()
    if previous is None:
        return True
    return _is_course_complete(user, previous)


@login_required
def assignment_detail(request, course_slug, assignment_slug):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, slug=assignment_slug, course=course)

    if not request.user.is_staff and not _is_course_unlocked(request.user, course):
        return redirect('course_list')

    if not request.user.is_staff and not _all_lessons_complete(request.user, course):
        return redirect('course_detail', slug=course_slug)

    passed = AssignmentSubmission.objects.filter(
        user=request.user,
        assignment=assignment,
        passed=True,
    ).exists()

    return render(request, 'courses/assignment_detail.html', {
        'course': course,
        'assignment': assignment,
        'passed': passed,
        'test_inputs_json': json.dumps(assignment.get_test_inputs()),
    })


@login_required
def submit_assignment(request, course_slug, assignment_slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, slug=assignment_slug, course=course)

    if not request.user.is_staff and not _is_course_unlocked(request.user, course):
        return JsonResponse({'error': 'Complete the previous course first'}, status=403)

    if not request.user.is_staff and not _all_lessons_complete(request.user, course):
        return JsonResponse({'error': 'Complete all lessons first'}, status=403)

    code = request.POST.get('code', '')
    output = request.POST.get('output', '').strip().replace('\r\n', '\n').replace('\r', '\n')
    expected = assignment.expected_output.strip().replace('\r\n', '\n').replace('\r', '\n')

    passed = output == expected

    AssignmentSubmission.objects.create(
        user=request.user,
        assignment=assignment,
        code=code,
        passed=passed,
    )

    return JsonResponse({
        'passed': passed,
        'expected': expected if not passed else None,
    })


@login_required
def feedback_report(request):
    if request.method == 'POST':
        category = request.POST.get('category', 'feedback')
        message_text = request.POST.get('message', '').strip()
        page = request.POST.get('page', '').strip()

        if message_text:
            FeedbackReport.objects.create(
                user=request.user,
                category=category,
                message=message_text,
                page=page,
            )
            messages.success(request, 'Thanks — your feedback has been submitted.')
            return redirect('feedback_report')

    return render(request, 'courses/feedback.html', {
        'submitted': 'submitted' in request.GET,
    })


@login_required
def course_survey(request, slug):
    course = get_object_or_404(Course, slug=slug)

    lessons = course.lessons.all()
    total = lessons.count()
    completed_count = LessonProgress.objects.filter(
        user=request.user, lesson__in=lessons, completed=True
    ).count()

    assignments = course.assignments.all()
    assignment_count = assignments.count()
    passed_count = AssignmentSubmission.objects.filter(
        user=request.user, assignment__in=assignments, passed=True
    ).values('assignment').distinct().count()

    course_complete = (
        total > 0 and completed_count >= total and
        (assignment_count == 0 or passed_count >= assignment_count)
    )

    if not request.user.is_staff and not course_complete:
        return redirect('course_detail', slug=slug)

    already_submitted = CourseSurveyResponse.objects.filter(
        user=request.user, course=course
    ).exists()

    if request.method == 'POST' and not already_submitted:
        try:
            rating = int(request.POST.get('rating', 0))
            content_clarity = int(request.POST.get('content_clarity', 0))
        except (ValueError, TypeError):
            rating = content_clarity = 0

        liked_most = request.POST.get('liked_most', '').strip()
        improve = request.POST.get('improve', '').strip()
        recommend_raw = request.POST.get('would_recommend', '')
        would_recommend = True if recommend_raw == 'yes' else (False if recommend_raw == 'no' else None)

        if 1 <= rating <= 5 and 1 <= content_clarity <= 5:
            CourseSurveyResponse.objects.create(
                user=request.user,
                course=course,
                rating=rating,
                content_clarity=content_clarity,
                liked_most=liked_most,
                improve=improve,
                would_recommend=would_recommend,
            )
            return redirect('course_survey_done', slug=slug)

    return render(request, 'courses/course_survey.html', {
        'course': course,
        'already_submitted': already_submitted,
    })


@login_required
def course_survey_done(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'courses/course_survey_done.html', {'course': course})


@login_required
def dismiss_announcement(request, announcement_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    announcement = get_object_or_404(Announcement, id=announcement_id)
    AnnouncementDismissal.objects.get_or_create(user=request.user, announcement=announcement)
    return JsonResponse({'success': True})