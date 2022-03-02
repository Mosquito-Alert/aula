import app_config

from main.models import Campaign
from django.contrib.auth.models import User


def deactivate_campaign_users(campaign):
    deactivated_users = User.objects.filter(profile__campaign=campaign)
    for user in deactivated_users:
        user.is_active = False
        user.save()


def main():
    campaign = Campaign.objects.get(pk=1)
    deactivate_campaign_users(campaign)


if __name__ == '__main__':
    main()
