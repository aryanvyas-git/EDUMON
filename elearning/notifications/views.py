from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def notification_list(request):
    """Placeholder — replaced with full notification list in Phase 3."""
    return render(request, 'notifications/notification_list.html', {'notifications': []})
