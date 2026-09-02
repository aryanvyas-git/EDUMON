def unread_notifications(request):
    """Expose the unread notification count to every template (nav badge)."""
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notification_count': count}
