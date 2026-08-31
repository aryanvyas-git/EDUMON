from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def room_list(request):
    """Placeholder — replaced with full chat room list in Phase 5."""
    return render(request, 'chat/room_list.html', {'rooms': []})
