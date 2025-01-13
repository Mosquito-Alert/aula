from main.models import Campaign, InternalNotification


def campaign(request):
    c = Campaign.objects.get(active=True)
    return { 'campaign': c }

def unread_notifications(request):
    try:
        unread_notifications = InternalNotification.objects.filter(to_user=request.user).filter(read=False).count()
        return {'unread_notifications': unread_notifications}
    except:
        return {'unread_notifications': 0}
