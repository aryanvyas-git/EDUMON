from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseForm, CourseMaterialForm, FeedbackForm
from .models import Course, Enrolment, Feedback


def _require_teacher(user):
    if not user.is_teacher():
        raise PermissionDenied('Only teachers can perform this action.')


@login_required
def course_list(request):
    """Browse all courses available to enrol on (R1e)."""
    courses = Course.objects.select_related('teacher').all()
    enrolled_course_ids = set()
    if request.user.is_student():
        enrolled_course_ids = set(
            Enrolment.objects.filter(student=request.user).values_list('course_id', flat=True)
        )
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids,
    })


@login_required
def course_create(request):
    """Teachers create a new course (R1d)."""
    _require_teacher(request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Course created.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = CourseForm()
    return render(request, 'courses/course_create.html', {'form': form})


@login_required
def course_detail(request, pk):
    """Course overview: materials, feedback, enrolment/blocking actions."""
    course = get_object_or_404(Course.objects.select_related('teacher'), pk=pk)
    is_teacher_of_course = course.teacher_id == request.user.id
    enrolment = None
    if request.user.is_student():
        enrolment = Enrolment.objects.filter(course=course, student=request.user).first()

    can_view_materials = is_teacher_of_course or (enrolment and not enrolment.is_blocked)
    materials = course.materials.all() if can_view_materials else []
    feedback_list = course.feedback.select_related('student').all()

    feedback_form = None
    already_left_feedback = Feedback.objects.filter(course=course, student=request.user).exists()
    if enrolment and not enrolment.is_blocked and not already_left_feedback:
        feedback_form = FeedbackForm()

    material_form = CourseMaterialForm() if is_teacher_of_course else None

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_teacher_of_course': is_teacher_of_course,
        'enrolment': enrolment,
        'materials': materials,
        'feedback_list': feedback_list,
        'feedback_form': feedback_form,
        'material_form': material_form,
    })


@login_required
def enrol(request, pk):
    """Student self-enrolment on a course (R1e)."""
    if request.method != 'POST':
        raise PermissionDenied
    if not request.user.is_student():
        raise PermissionDenied('Only students can enrol.')
    course = get_object_or_404(Course, pk=pk)
    Enrolment.objects.get_or_create(student=request.user, course=course)
    messages.success(request, f'Enrolled on {course.title}.')
    return redirect('courses:course_detail', pk=pk)


@login_required
def add_feedback(request, pk):
    """Enrolled, non-blocked students leave feedback on a course (R1f)."""
    if request.method != 'POST':
        raise PermissionDenied
    course = get_object_or_404(Course, pk=pk)
    enrolment = get_object_or_404(Enrolment, course=course, student=request.user)
    if enrolment.is_blocked:
        raise PermissionDenied('Blocked students cannot leave feedback.')

    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.course = course
        feedback.student = request.user
        feedback.save()
        messages.success(request, 'Feedback submitted.')
    return redirect('courses:course_detail', pk=pk)


@login_required
def upload_material(request, pk):
    """Teachers upload course materials (R1j)."""
    course = get_object_or_404(Course, pk=pk)
    if course.teacher_id != request.user.id:
        raise PermissionDenied('Only the course teacher can upload materials.')

    if request.method != 'POST':
        raise PermissionDenied
    form = CourseMaterialForm(request.POST, request.FILES)
    if form.is_valid():
        material = form.save(commit=False)
        material.course = course
        material.save()
        messages.success(request, 'Material uploaded.')
    return redirect('courses:course_detail', pk=pk)


@login_required
def manage_students(request, pk):
    """Teacher view of enrolled students, with block/unblock controls (R1h)."""
    course = get_object_or_404(Course, pk=pk)
    if course.teacher_id != request.user.id:
        raise PermissionDenied('Only the course teacher can manage students.')
    enrolments = course.enrolments.select_related('student').all()
    return render(request, 'courses/manage_students.html', {
        'course': course,
        'enrolments': enrolments,
    })


@login_required
def toggle_block_student(request, pk, enrolment_id):
    """Toggle whether a student is blocked from a course (R1h)."""
    if request.method != 'POST':
        raise PermissionDenied
    course = get_object_or_404(Course, pk=pk)
    if course.teacher_id != request.user.id:
        raise PermissionDenied('Only the course teacher can block students.')
    enrolment = get_object_or_404(Enrolment, pk=enrolment_id, course=course)
    enrolment.is_blocked = not enrolment.is_blocked
    enrolment.save(update_fields=['is_blocked'])
    return redirect('courses:manage_students', pk=pk)
