from main.models import Campaign


def campaign(request):
    c = Campaign.objects.get(active=True)
    return { 'campaign': c }
