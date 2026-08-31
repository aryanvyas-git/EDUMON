from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
    """List the logged-in user's notifications, newest first (R1k, R1l)."""
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    """Mark a single notification as read."""
    if request.method != 'POST':
        raise PermissionDenied
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect('notifications:list')
