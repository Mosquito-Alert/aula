from django.test import TestCase
from slugify import slugify
from main.models import Campaign, get_current_active_campaign, EducationCenter, User, Profile, Quiz, Question, Answer, \
    QuizRun, QuizRunAnswers
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase


class CampaignTest(TestCase):
    "Tests campaign model"
    def setUp(self) -> None:
        c1 = Campaign(name='campaign1')
        c1.save()
        c2 = Campaign(name='campaign2')
        c2.save()
        c3 = Campaign(name='campaign2')
        c3.save()

    def tearDown(self) -> None:
        Campaign.objects.all().delete()

    def test_basic(self):
        n_campaigns = Campaign.objects.all().count()
        self.assertTrue(n_campaigns==3, msg="There should be 3 campaigns, {0} found".format(n_campaigns))

    def test_active_campaign(self):
        current_active = get_current_active_campaign()
        self.assertTrue( current_active is None, msg="There should not be a currently active campaign" )
        current_active_campaign_name = 'campaign1'
        c1 = Campaign.objects.get(name=current_active_campaign_name)
        c1.active = True
        c1.save()
        current_active_id = get_current_active_campaign()
        current_active = Campaign.objects.get(pk=current_active_id)
        self.assertTrue( current_active.name == 'campaign1', msg="Current active campaign name should be {0}, is {1}".format( current_active_campaign_name, current_active.name ) )


class ProfileTests(TestCase):
    def setUp(self) -> None:
        c1 = Campaign(name='campaign1')
        c1.active = True
        c1.save()

        e1 = EducationCenter(
            name="educationcenter1",
            campaign=c1
        )
        e1.hashtag = e1.center_slug()
        e1.save()

        teacher = User(username='teacher1')
        teacher.set_password('123456')
        teacher.save()
        teacher.profile.teacher_password = '123456'
        teacher.profile.is_teacher = True
        teacher.profile.teacher_belongs_to = e1
        teacher.save()

        group1 = User(username='group1')
        group1.set_password('123456')
        group1.save()
        group1.profile.is_group = True
        group1.profile.group_password = '1234'
        group1.profile.group_public_name = 'Group 1'
        group1.profile.group_class = 'Class 1'
        group1.profile.group_class_slug = slugify('Class 1')
        group1.profile.group_teacher = teacher
        group1.profile.campaign = c1
        group1.profile.n_students_in_group = 3
        group1.save()

        group2 = User(username='group2')
        group2.set_password('123456')
        group2.save()
        group2.profile.is_group = True
        group2.profile.group_password = '1234'
        group2.profile.group_public_name = 'Group 2'
        group2.profile.group_class = 'Class 1'
        group2.profile.group_class_slug = slugify('Class 1')
        group2.profile.group_teacher = teacher
        group2.profile.campaign = c1
        group2.profile.n_students_in_group = 3
        group2.save()

    def tearDown(self) -> None:
        teacher = User.objects.get(username='teacher1')
        teacher.delete()
        center = EducationCenter.objects.get(name="educationcenter1")
        center.delete()
        c1 = Campaign.objects.get(name='campaign1')
        c1.delete()
        group1 = User.objects.get(username='group1')
        group1.delete()
        group2 = User.objects.get(username='group2')
        group2.delete()

    def test_center(self):
        center = EducationCenter.objects.get(name="educationcenter1")
        group1 = User.objects.get(username='group1')
        teacher = User.objects.get(username='teacher1')
        self.assertTrue( teacher.profile.center == center.name, msg="Teacher center should be {0}, is {1}".format( center.name, teacher.profile.center ) )
        self.assertTrue( group1.profile.center == center.name, msg="Group center should be {0}, is {1}".format(center.name, group1.profile.center))

    def test_group_lists(self):
        group1 = User.objects.get(username='group1')
        group1.profile.groups_list
        self.assertTrue(True, msg="Blank test")

    def test_tutored_groups(self):
        group1 = User.objects.get(username='group1')
        teacher = User.objects.get(username='teacher1')
        self.assertTrue( group1.profile.tutored_groups == 0, "A group should never have tutoried groups, has {0}".format( group1.profile.tutored_groups ) )
        self.assertTrue(teacher.profile.tutored_groups == 2, "Teacher should tutor 2 groups, has {0}".format(teacher.profile.tutored_groups))

    def test_available_tests(self):
        group1 = User.objects.get(username='group1')
        teacher = User.objects.get(username='teacher1')
        self.assertTrue( teacher.profile.available_tests is None, "Teacher should never have available tests" )
        self.assertTrue(group1.profile.available_tests.count() == 0, "There should not be available tests for the group")

    def test_user_campaign(self):
        group1 = User.objects.get(username='group1')
        group2 = User.objects.get(username='group2')
        teacher = User.objects.get(username='teacher1')
        c1 = Campaign.objects.get(name='campaign1')
        self.assertTrue(c1.active == True, "Campaign 1 should be active")
        self.assertTrue( group1.profile.get_user_campaign == c1, "Group 1 campaign should be {0}, is {1}".format( c1, group1.profile.get_user_campaign ) )
        self.assertTrue(group2.profile.get_user_campaign == c1, "Group 2 campaign should be {0}, is {1}".format(c1, group2.profile.get_user_campaign))
        self.assertTrue(teacher.profile.get_user_campaign == c1, "Teacher campaign should be {0}, is {1}".format(c1, teacher.profile.get_user_campaign))


class QuizTest(TestCase):
    def setUp(self) -> None:
        c1 = Campaign(name='campaign1')
        c1.active = True
        c1.save()

        q1 = Quiz( name = 'quiz_test_1', published = True, type = 0, campaign = c1, seq = 1)
        q1.save()

        q1_1 = Question( quiz=q1, text='Test question 1', question_order = 1)
        q1_1.save()

        q1_2 = Question(quiz=q1, text='Test question 2', question_order=2)
        q1_2.save()

        q2 = Quiz( name='quiz_teacher_poll_2', published=True, type=4, campaign=c1, seq= 2)
        q2.save()

        q2_1 = Question(quiz=q2, text='Teacher poll question 1', question_order=1)
        q2_1.save()

        q2_2 = Question(quiz=q2, text='Teacher poll question 2', question_order=2)
        q2_2.save()

    def tearDown(self) -> None:
        q1 = Quiz.objects.get(name='quiz_test_1')
        q1.delete()
        c1 = Campaign.objects.get(name='campaign1')
        c1.delete()

    def test_clone(self):
        q1 = Quiz.objects.get(name='quiz_test_1')
        q2 = q1.clone()
        self.assertTrue(q1.author == q2.author, "Author should be cloned")
        self.assertTrue(q1.name == q2.name, "Name should be cloned")
        self.assertTrue(q1.html_header == q2.html_header, "Html header should be cloned")
        self.assertTrue(q1.published == q2.published, "Published should be cloned")
        self.assertTrue(q1.type == q2.type, "Type should be cloned")
        self.assertTrue(q1.seq == q2.seq, "Seq should be cloned")

    def test_comment_at_the_end(self):
        q1 = Quiz.objects.get(name='quiz_test_1')
        self.assertFalse( q1.comment_at_the_end, "Quiz is test, should NOT HAVE comment at end"  )
        q2 = Quiz.objects.get(name='quiz_teacher_poll_2')
        self.assertTrue( q2.comment_at_the_end, "Quiz is teacher poll, should HAVE comment at end")

    def test_type_text(self):
        q1 = Quiz.objects.get(name='quiz_test_1')
        self.assertTrue( q1.type_text == 'Test', "Quiz is test, type text should be {0}, is {1}".format( 'Test', q1.type_text)  )
        q2 = Quiz.objects.get(name='quiz_teacher_poll_2')
        self.assertTrue(q2.type_text == 'Enquesta professorat', "Quiz is test, type text should be {0}, is {1}".format('Enquesta professorat', q2.type_text))

    def test_sorted_questions_set(self):
        q1 = Quiz.objects.get(name='quiz_test_1')
        sorted_questions = q1.sorted_questions_set
        self.assertTrue( len(sorted_questions) == 2, "Quiz {0} should have {1} questions, has {2}".format( q1.name, 2, len(sorted_questions) ) )
        self.assertTrue( sorted_questions[0].question_order == 1 and sorted_questions[1].question_order == 2, "Questions should be consecutive" )
        q2 = Quiz.objects.get(name='quiz_teacher_poll_2')
        sorted_questions = q2.sorted_questions_set
        self.assertTrue(len(sorted_questions) == 2, "Quiz {0} should have {1} questions, has {2}".format(q2.name, 2, len(sorted_questions)))
        self.assertTrue(sorted_questions[0].question_order == 1 and sorted_questions[1].question_order == 2, "Questions should be consecutive")


class EducationCenterTest(TestCase):
    def setUp(self) -> None:
        c1 = Campaign(name='campaign1')
        c1.active = True
        c1.save()
        e1 = EducationCenter(
            name = "educationcenter1",
            campaign = c1
        )
        e1.hashtag = e1.center_slug()
        e1.save()

    def tearDown(self) -> None:
        e1 = EducationCenter.objects.get(name='educationcenter1')
        c1 = Campaign.objects.get(name='campaign1')
        e1.delete()
        c1.delete()

    def test_hashtag(self):
        e1 = EducationCenter.objects.get(name='educationcenter1')
        self.assertTrue(e1.hashtag is not None, msg="Center hashtag should not be none")

    def test_str_method(self):
        e1 = EducationCenter.objects.get(name='educationcenter1')
        self.assertTrue( e1.name == str(e1), msg="Center string representation should be {0}, is {1}".format( e1.name, str(e1) ) )


class PollTests(APITestCase):
    def setUp(self) -> None:
        c1 = Campaign(name='campaign1')
        c1.active = True
        c1.save()

        e1 = EducationCenter(
            name = "educationcenter1",
            campaign = c1
        )
        e1.hashtag = e1.center_slug()
        e1.save()

        q2 = Quiz( name='quiz_poll_2', published=True, type=2, campaign=c1, seq= 2)
        q2.save()

        q2_1 = Question(quiz=q2, text='Poll question 1', question_order=1)
        q2_1.save()

        a2_1_1 = Answer( question=q2_1, label='A', text='A' )
        a2_1_1.save()
        a2_1_2 = Answer(question=q2_1, label='B', text='B')
        a2_1_2.save()
        a2_1_3 = Answer(question=q2_1, label='C', text='C')
        a2_1_3.save()
        a2_1_4 = Answer(question=q2_1, label='D', text='D')
        a2_1_4.save()

        q2_2 = Question(quiz=q2, text='Poll question 2', question_order=2)
        q2_2.save()

        a2_2_1 = Answer(question=q2_2, label='E', text='E')
        a2_2_1.save()
        a2_2_2 = Answer(question=q2_2, label='F', text='F')
        a2_2_2.save()
        a2_2_3 = Answer(question=q2_2, label='G', text='G')
        a2_2_3.save()
        a2_2_4 = Answer(question=q2_2, label='H', text='H')
        a2_2_4.save()

        teacher = User(username='teacher1')
        teacher.set_password('123456')
        teacher.save()
        teacher.profile.teacher_password = '123456'
        teacher.profile.is_teacher = True
        teacher.profile.teacher_belongs_to = e1
        teacher.save()

        group1 = User(username='group1')
        group1.set_password('123456')
        group1.save()
        group1.profile.is_group = True
        group1.profile.group_password = '1234'
        group1.profile.group_public_name = 'Group 1'
        group1.profile.group_class = 'Class 1'
        group1.profile.group_class_slug = slugify('Class 1')
        group1.profile.group_teacher = teacher
        group1.profile.campaign = c1
        group1.profile.n_students_in_group = 3
        group1.save()

        group2 = User(username='group2')
        group2.set_password('123456')
        group2.save()
        group2.profile.is_group = True
        group2.profile.group_password = '1234'
        group2.profile.group_public_name = 'Group 2'
        group2.profile.group_class = 'Class 1'
        group2.profile.group_class_slug = slugify('Class 1')
        group2.profile.group_teacher = teacher
        group2.profile.campaign = c1
        group2.profile.n_students_in_group = 3
        group2.save()

    def tearDown(self) -> None:
        group1 = User.objects.get(username='group1')
        group2 = User.objects.get(username='group2')
        teacher = User.objects.get(username='teacher1')

        group1.delete()
        group2.delete()
        teacher.delete()

        c1 = Campaign.objects.get(name='campaign1')
        e1 = EducationCenter.objects.get(name = "educationcenter1")
        e1.delete()
        c1.delete()

        q2 = Quiz.objects.get(name='quiz_poll_2')
        q2.delete()

    def test_poll_results(self):
        e1 = EducationCenter.objects.get(name="educationcenter1")
        group1 = User.objects.get(username='group1')
        self.client.force_authenticate(user=group1)
        q2 = Quiz.objects.get(name='quiz_poll_2')
        data = {
            'quiz_id': q2.id,
            'taken_by': group1.id,
            'run_number': 1
        }
        response = self.client.post('/api/startrun/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue( QuizRun.objects.filter(taken_by=group1).exists(), "Quizrun should have been created for quiz {0}, group {1}".format(q2, group1))

        group2 = User.objects.get(username='group2')
        self.client.force_authenticate(user=group1)
        data = {
            'quiz_id': q2.id,
            'taken_by': group2.id,
            'run_number': 1
        }
        response = self.client.post('/api/startrun/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(QuizRun.objects.filter(taken_by=group1).exists(), "Quizrun should have been created for quiz {0}, group {1}".format(q2, group2))

        group1_quizrun = QuizRun.objects.get(taken_by=group1)
        group1_quizrunanswers = QuizRunAnswers.objects.filter(quizrun=group1_quizrun).order_by('question__question_order')
        for quizrunanswer in group1_quizrunanswers:
            question = quizrunanswer.question
            answer = question.sorted_answers_set[0]
            data = {
                'id': quizrunanswer.id,
                'answer_id': answer.id
            }
            response = self.client.post('/api/writeanswer/', data=data)
            self.assertEqual(response.status_code, 200)

        group2_quizrun = QuizRun.objects.get(taken_by=group2)
        group2_quizrunanswers = QuizRunAnswers.objects.filter(quizrun=group2_quizrun).order_by('question__question_order')
        for quizrunanswer in group2_quizrunanswers:
            question = quizrunanswer.question
            answer = question.sorted_answers_set[0]
            data = {
                'id': quizrunanswer.id,
                'answer_id': answer.id
            }
            response = self.client.post('/api/writeanswer/', data=data)
            self.assertEqual(response.status_code, 200)

        a = Answer.objects.get(label='A', text='A')
        self.assertTrue(a.how_many_times_answered == 2, "Answer A should have been answered 2 times, has been {0} times".format(a.how_many_times_answered))
        self.assertTrue(a.how_many_times_answered_by_group(group1) == 1, "Answer A should have been answered 1 time by group 1, has been {0} times".format(a.how_many_times_answered_by_group(group1)))
        self.assertTrue(a.how_many_times_answered_by_group(group2) == 1, "Answer A should have been answered 1 time by group 2, has been {0} times".format(a.how_many_times_answered_by_group(group2)))
        self.assertTrue(a.how_many_times_answered_by_center(e1.id) == 2, "Answer A should have been answered 2 times by center 1, has been {0} times".format(a.how_many_times_answered_by_center(e1.id)))
        e = Answer.objects.get(label='E', text='E')
        self.assertTrue(e.how_many_times_answered == 2, "Answer E should have been answered 2 times, has been {0} times".format(e.how_many_times_answered))
        self.assertTrue(e.how_many_times_answered_by_group(group1) == 1, "Answer E should have been answered 1 time by group 1, has been {0} times".format(e.how_many_times_answered_by_group(group1)))
        self.assertTrue(e.how_many_times_answered_by_group(group2) == 1, "Answer E should have been answered 1 time by group 2, has been {0} times".format(e.how_many_times_answered_by_group(group2)))
        self.assertTrue(e.how_many_times_answered_by_center(e1.id) == 2, "Answer E should have been answered 2 times by center 1, has been {0} times".format(e.how_many_times_answered_by_center(e1.id)))

