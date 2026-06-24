from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Course, Lesson, LessonProgress, LessonQuestion, Assignment, AssignmentSubmission

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
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
    assignments_locked = completed_count < total

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
    })

@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    questions = lesson.questions.all()

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'questions': questions,
    })

@login_required
def mark_complete(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

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
        return JsonResponse({
            'correct': correct,
            'expected': ' → '.join(correct_order) if not correct else None,
        })

    expected = question.expected_answer.strip()
    correct = user_answer.lower() == expected.lower()

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


@login_required
def assignment_detail(request, course_slug, assignment_slug):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, slug=assignment_slug, course=course)

    if not _all_lessons_complete(request.user, course):
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
    })


@login_required
def submit_assignment(request, course_slug, assignment_slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, slug=assignment_slug, course=course)

    if not _all_lessons_complete(request.user, course):
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