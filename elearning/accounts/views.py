from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course, Enrolment

from .forms import RegistrationForm, StatusUpdateForm
from .models import CustomUser, StatusUpdate


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
    """Placeholder — replaced with full student/teacher search in Phase 3 (R1c)."""
    return render(request, 'accounts/search.html', {'results': []})


def _build_profile_context(profile_user, form):
    statuses = StatusUpdate.objects.filter(user=profile_user)
    if profile_user.is_teacher():
        courses = Course.objects.filter(teacher=profile_user)
    else:
        courses = Course.objects.filter(
            id__in=Enrolment.objects.filter(student=profile_user, is_blocked=False).values('course_id')
        )
    return {
        'profile_user': profile_user,
        'statuses': statuses,
        'courses': courses,
        'form': form,
        'is_own_profile': form is not None,
    }
