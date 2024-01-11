from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from main.models import Quiz, Campaign, EducationCenter, Question, Answer, QuizRun, get_current_active_campaign
from rest_framework.test import APIClient, APITestCase
import datetime
from slugify import slugify

# Create your tests here.
class SingleInProgressQuiz(APITestCase):
    def setUp(self):
        # create campaign
        c = Campaign(
            name = 'Test campaign',
            active = True,
            start_date = datetime.datetime.strptime("2024-01-01", "%Y-%m-%d").date(),
            end_date = datetime.datetime.strptime("2024-12-31", "%Y-%m-%d").date()
        )
        c.save()

        # create campaign
        c2 = Campaign(
            name='Test campaign 2',
            active=False,
            start_date=datetime.datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
            end_date=datetime.datetime.strptime("2023-12-31", "%Y-%m-%d").date()
        )
        c2.save()

        # create Center
        edc = EducationCenter(
            name='Test center',
            hashtag = 'tc_2024',
            campaign = c
        )
        edc.save()

        # create teacher
        tu = User.objects.create_user(username='test_teacher', email='test_teacher@example.com', password='test_teacher')
        tu.save()
        tu.profile.teacher_password = 'test_teacher'
        tu.profile.is_teacher = True
        tu.profile.teacher_belongs_to = edc
        tu.save()

        # create group
        gu = User.objects.create_user(username='test_group', email='test_group@example.com', password='test')
        gu.save()
        gu.profile.is_group = True
        gu.profile.group_password = 'test'
        gu.profile.group_public_name = 'test_group_public_name'
        gu.profile.group_class = 'test_group_class'
        gu.profile.group_class_slug = slugify('test_group_class')
        gu.profile.group_teacher = tu
        gu.profile.campaign = c
        gu.profile.n_students_in_group = 3
        gu.save()

        # create simple test
        q = Quiz(name = 'test_quiz',published = True,type = 0,campaign = c,seq = 1)
        q.save()

        q1 = Question(quiz=q,text = "Question 1",question_order = 1)
        q1.save()

        q1a1 = Answer(question=q1,label = "a",text = "Answer 1 question 1",is_correct = True)
        q1a1.save()

        q1a2 = Answer(question=q1,label="b",text="Answer 2 question 1",is_correct=False)
        q1a2.save()

    def test_base(self):
        # test everything is created
        self.assertTrue(Campaign.objects.filter(name='Test campaign').exists(),"Campaign does not exist, it should...")
        self.assertTrue(EducationCenter.objects.filter(name='Test center').exists(), "Education center does not exist, it should...")
        self.assertTrue(User.objects.filter(username='test_teacher').exists(),"Teacher does not exist, it should...")
        self.assertTrue(User.objects.filter(username='test_group').exists(), "Group does not exist, it should...")
        self.assertTrue(Quiz.objects.filter(name='test_quiz').exists(), "Quiz does not exist, it should...")

    def test_two_in_progress_tests_no_api(self):
        quiz = Quiz.objects.get(name='test_quiz')
        user_taken = User.objects.get(username='test_group')
        qr1 = QuizRun(taken_by=user_taken, quiz=quiz, run_number=1)
        qr1.save()
        qr2 = QuizRun(taken_by=user_taken, quiz=quiz, run_number=2)
        try:
            qr2.save()
            self.fail("A second in progress quizrun has been created without error, this should not be allowed")
        except IntegrityError:
            pass

    def test_two_in_progress_tests_api(self):
        user_taken = User.objects.get(username='test_group')
        quiz = Quiz.objects.get(name='test_quiz')
        self.client.force_authenticate(user=user_taken)
        data_1 = {
            'quiz_id': quiz.id,
            'taken_by': user_taken.id,
            'run_number': 1
        }
        data_2 = {
            'quiz_id': quiz.id,
            'taken_by': user_taken.id,
            'run_number': 2
        }
        response = self.client.post('/api/startrun/', data=data_1)
        self.assertEqual(response.status_code, 200, "Response should be 200, is {0}".format(response.status_code))
        self.assertTrue( QuizRun.objects.filter(taken_by=user_taken).filter(quiz=quiz).filter(run_number=1).exists(), "API call should have created a quizrun, it has not" )
        response = self.client.post('/api/startrun/', data=data_2)
        self.assertEqual(response.status_code, 400, "Response should be 400, is {0}".format(response.status_code))

    def test_active_campaign(self):
        c = get_current_active_campaign()
        active = Campaign.objects.get(name='Test campaign')
        self.assertTrue( c == active.id, "Current active method returns campaign with id {0}, should be {1}".format( c, active.id ) )

        #create new education center without setting explicitly campaign
        edc2 = EducationCenter(
            name='Test center 2',
            hashtag='tc2_2024'
        )
        edc2.save()
        self.assertTrue(edc2.campaign is not None, "Campaign of newly created center should not be null, it is")
        self.assertTrue(edc2.campaign.id == c, "Campaign of newly created center should be the active campaign, it is not")

        quiz = Quiz(name='test_quiz_2', published=True, type=0, seq=1)
        quiz.save()
        self.assertTrue(quiz.campaign is not None, "Campaign of newly created quiz should not be null, it is")
        self.assertTrue(quiz.campaign.id == c,"Campaign of newly created quiz should be the active campaign, it is not")

        # don't set campaign for new group and check
        teacher = User.objects.get(username='test_teacher')
        gu = User.objects.create_user(username='test_group_2', email='test_group_2@example.com', password='test')
        gu.save()
        gu.profile.is_group = True
        gu.profile.group_password = 'test'
        gu.profile.group_public_name = 'test_group_2_public_name'
        gu.profile.group_class = 'test_group_class'
        gu.profile.group_class_slug = slugify('test_group_class')
        gu.profile.group_teacher = teacher
        gu.profile.n_students_in_group = 3
        gu.save()
        self.assertTrue(gu.profile.campaign is not None, "Campaign of newly created group should not be null, it is")
        self.assertTrue(gu.profile.campaign.id == c,"Campaign of newly created group should be the active campaign, it is not")
