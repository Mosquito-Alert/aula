from django.test import TestCase
from main.models import Campaign, EducationCenter, get_current_active_campaign
from django.contrib.auth.models import User

# Create your tests here.


def create_models():
    c = Campaign(name="Campaign",active=True)
    c.save()
    e = EducationCenter(name="Center", campaign=c, hashtag="center")
    e.save()

    t = User.objects.create(pk=1)
    t.username = 'teacher'
    t.save()
    t.profile.is_teacher = True
    t.profile.teacher_belongs_to = e
    t.profile.campaign = c
    t.save()

    g = User.objects.create(pk=2)
    g.username = 'group'
    g.save()
    g.profile.is_group = True
    g.profile.group_teacher = t
    g.profile.campaign = c
    g.profile.n_students_in_group = 3
    g.save()


class DuplicateInProgressTest(TestCase):
    def test_models(self):
        create_models()
        c = Campaign.objects.first()
        e = EducationCenter.objects.first()
        current_active = get_current_active_campaign()

        self.assertTrue(Campaign.objects.all().count() == 1, "There should be 1 campaign" )
        self.assertTrue(EducationCenter.objects.all().count() == 1, "There should be 1 education center")
        self.assertTrue(e.campaign.id == c.id, "Education center campaign should be currently active" )
        self.assertTrue(current_active == c.id, "Currently active campaign should be only campaign")

