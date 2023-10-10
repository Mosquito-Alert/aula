from django.test import TestCase
from main.models import Campaign, EducationCenter, get_current_active_campaign, Quiz, Question, Answer, QuizRun
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase

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

    q = Quiz(name='poll', published=True, type=2, campaign=c, seq=0)
    q.save()

    q1 = Question(quiz=q, text='What is your favourite color?', question_order=1)
    q1.save()
    q1_a1 = Answer(question=q1, label='1', text='Red')
    q1_a2 = Answer(question=q1, label='2', text='Orange')
    q1_a3 = Answer(question=q1, label='3', text='Blue')
    q1_a1.save()
    q1_a2.save()
    q1_a3.save()

    q2 = Question(quiz=q, text='What is your favourite animal?', question_order=2)
    q2.save()
    q2_a1 = Answer(question=q2, label='1', text='Llama')
    q2_a2 = Answer(question=q2, label='2', text='Sheep')
    q2_a3 = Answer(question=q2, label='3', text='Cat')
    q2_a1.save()
    q2_a2.save()
    q2_a3.save()

    q3 = Question(quiz=q, text='What is your favourite ice cream?', question_order=3)
    q3.save()
    q3_a1 = Answer(question=q2, label='1', text='Vanilla')
    q3_a2 = Answer(question=q2, label='2', text='Chocolate')
    q3_a3 = Answer(question=q2, label='3', text='Strawberry')
    q3_a1.save()
    q3_a2.save()
    q3_a3.save()


class DuplicateInProgressTest(APITestCase):
    def test_models(self):
        create_models()
        c = Campaign.objects.first()
        e = EducationCenter.objects.first()
        current_active = get_current_active_campaign()

        self.assertTrue(Campaign.objects.all().count() == 1, "There should be 1 campaign" )
        self.assertTrue(EducationCenter.objects.all().count() == 1, "There should be 1 education center")
        self.assertTrue(e.campaign.id == c.id, "Education center campaign should be currently active" )
        self.assertTrue(current_active == c.id, "Currently active campaign should be only campaign")

    def test_quizrun_start(self):
        create_models()

        group = User.objects.get(username='group')
        quiz = Quiz.objects.get(name='poll')

        self.client.force_authenticate(user=group)

        data = {
            'quiz_id': quiz.id,
            'taken_by': group.id,
            'run_number': 1
        }
        response = self.client.post('/api/startrun/', data=data)
        self.assertTrue(response.status_code == 200, "Quizrun should be created")

        data = {
            'quiz_id': quiz.id,
            'taken_by': group.id,
            'run_number': 1
        }
        response = self.client.post('/api/startrun/', data=data)
        self.assertTrue(response.status_code == 400,
                        "Should not be allowed to create a second run with the same number")

        non_finished_quizrun_exists = QuizRun.objects.filter(quiz=quiz.id, taken_by=group).filter(date_finished__isnull=True).exists()
        self.assertTrue( non_finished_quizrun_exists, "There should be an existing unfinished quizrun" )
        data = {
            'quiz_id': quiz.id,
            'taken_by': group.id,
            'run_number': 2
        }
        response = self.client.post('/api/startrun/', data=data)
        self.assertTrue(response.status_code == 400,
                        "Quizrun should not be created because there is already a non finished quizrun")
