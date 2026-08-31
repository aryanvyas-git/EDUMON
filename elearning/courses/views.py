from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def course_list(request):
    """Placeholder — replaced with full course browsing in Phase 2."""
    return render(request, 'courses/course_list.html', {'courses': []})


@login_required
def course_create(request):
    """Placeholder — replaced with full course creation in Phase 2."""
    return render(request, 'courses/course_create.html')
