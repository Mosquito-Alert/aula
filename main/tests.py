from django.test import TestCase
from slugify import slugify
from main.models import Campaign, get_current_active_campaign, EducationCenter, User, Profile, Quiz, Question
from django.contrib.auth.models import User


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


