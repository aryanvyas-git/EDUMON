from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course, Enrolment

from .forms import RegistrationForm, StatusUpdateForm
from .models import CustomUser, StatusUpdate


def landing(request):
    """Public marketing home page for signed-out visitors."""
    if request.user.is_authenticated:
        return redirect('accounts:home')
    return render(request, 'accounts/landing.html')


def register(request):
    """Handle new account creation for both students and teachers (R1a)."""
    if request.user.is_authenticated:
        return redirect('accounts:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:home')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


class EmailAwareLoginView(LoginView):
    """Standard Django auth login view (R1b) rendered with our template."""

    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    """Standard Django auth logout view (R1b)."""

    next_page = 'accounts:login'


@login_required
def home(request):
    """The logged-in user's own home page: profile, courses, status feed (R1i)."""
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            status.save()
            return redirect('accounts:home')
    else:
        form = StatusUpdateForm()

    context = _build_profile_context(request.user, form)
    return render(request, 'accounts/home.html', context)


@login_required
def user_detail(request, username):
    """View another user's public home page (profile + status feed)."""
    profile_user = get_object_or_404(CustomUser, username=username)
    if profile_user == request.user:
        return redirect('accounts:home')
    context = _build_profile_context(profile_user, form=None)
    context['is_own_profile'] = False
    return render(request, 'accounts/home.html', context)


@login_required
def search(request):
    """Teachers search students and teachers by name/username (R1c)."""
    if not request.user.is_teacher():
        raise PermissionDenied('Only teachers can search users.')

    query = request.GET.get('q', '').strip()
    results = CustomUser.objects.none()
    if query:
        results = CustomUser.objects.filter(
            Q(username__icontains=query)
            | Q(real_name__icontains=query)
            | Q(email__icontains=query)
        ).order_by('username')
    return render(request, 'accounts/search.html', {'results': results, 'query': query})


def _build_profile_context(profile_user, form):
    statuses = StatusUpdate.objects.filter(user=profile_user)
    if profile_user.is_teacher():
        courses = Course.objects.filter(teacher=profile_user)
        course_stat_label = 'Courses taught'
    else:
        courses = Course.objects.filter(
            id__in=Enrolment.objects.filter(student=profile_user, is_blocked=False).values('course_id')
        )
        course_stat_label = 'Courses enrolled'
    return {
        'profile_user': profile_user,
        'statuses': statuses,
        'courses': courses,
        'course_stat_label': course_stat_label,
        'form': form,
        'is_own_profile': form is not None,
    }
