from main.models import get_current_active_campaign


def campaign(request):
    c = get_current_active_campaign()
    return { 'campaign': c }
