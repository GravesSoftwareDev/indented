from django.utils import timezone
from .models import Announcement


def active_announcement(request):
    if not request.user.is_authenticated:
        return {}

    now = timezone.now()
    announcement = (
        Announcement.objects
        .filter(starts_at__lte=now, ends_at__gte=now)
        .exclude(dismissals__user=request.user)
        .order_by('-created_at')
        .first()
    )
    return {'active_announcement': announcement}
