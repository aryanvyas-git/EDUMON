from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomUser

from .models import ChatRoom


def _room_slug_for(user_a, user_b):
    """Deterministic room name for a 1:1 chat between two usernames."""
    names = sorted([user_a.username, user_b.username])
    return f'dm-{names[0]}-{names[1]}'


@login_required
def room_list(request):
    """List chat rooms the user participates in, and let them start a new one (R1g)."""
    rooms = request.user.chat_rooms.all()
    other_users = CustomUser.objects.exclude(pk=request.user.pk)
    return render(request, 'chat/room_list.html', {'rooms': rooms, 'other_users': other_users})


@login_required
def start_chat(request):
    """Start (or resume) a direct chat with another user."""
    if request.method != 'POST':
        raise PermissionDenied
    other = get_object_or_404(CustomUser, pk=request.POST.get('user_id'))
    room_name = _room_slug_for(request.user, other)
    room, _ = ChatRoom.objects.get_or_create(name=room_name)
    room.participants.add(request.user, other)
    return redirect('chat:room_detail', room_name=room_name)


@login_required
def room_detail(request, room_name):
    """Chat room page: message history + live WebSocket connection (R1g)."""
    room, created = ChatRoom.objects.get_or_create(name=room_name)
    if not created and not room.participants.filter(pk=request.user.pk).exists():
        raise PermissionDenied('You are not a participant of this chat room.')
    room.participants.add(request.user)
    messages_qs = room.messages.select_related('sender').all()
    return render(request, 'chat/room_detail.html', {'room': room, 'chat_messages': messages_qs})
