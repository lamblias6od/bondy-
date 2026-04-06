from .models import Notification, Message

# Makes unread counts available in every template automatically.
# Registered in settings.py under TEMPLATES > context_processors,
# so there's no need to pass these values manually in each view.
def unread_notifications(request):
    if request.user.is_authenticated:
        # Count unread notifications and messages separately
        # so the navbar can display independent badges for each.
        notif_count = Notification.objects.filter(user=request.user, is_read=False).count()
        msg_count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return {
            'unread_count': notif_count,
            'unread_messages': msg_count
        }
    # Return zeros for unauthenticated users to avoid template errors.
    return {'unread_count': 0, 'unread_messages': 0}