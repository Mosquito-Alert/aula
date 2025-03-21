from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
import os
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from slugify import slugify
from django.db.models import Q, Func, F, Value
from django.db.models.constraints import UniqueConstraint
import datetime


class Campaign(models.Model):
    name = models.CharField(max_length=500)
    active = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    html_header_groups = models.TextField(blank=True, null=True)
    html_header_teachers = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    @property
    def centers(self):
        return EducationCenter.objects.filter(campaign=self)


def get_current_active_campaign():
    try:
        return Campaign.objects.get(active=True).id
    except Campaign.DoesNotExist:
        return None


class EducationCenter(models.Model):
    name = models.CharField(max_length=500)
    location = models.PointField(srid=4326, null=True)
    hashtag = models.CharField(max_length=20, null=True, blank=True, unique=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    campaign = models.ForeignKey(Campaign, default=get_current_active_campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name="education_centers")

    def __str__(self):
        return "{0} - {1}".format(self.name, self.campaign.name)

    def center_slug(self, year=True):
        now = datetime.datetime.now()
        if year:
            year = str(now.year - 2000)
        else:
            year = ''
        try:
            slug = slugify(self.name)
            bits = slug.split("-")
            initials = [ b[0] for b in bits ]
            return "#" + "".join(initials) + year
        except:
            return "#acme" + year

    def center_groups(self, slug = None):
        if slug:
            return User.objects.filter(profile__center_string=self.name).filter(profile__campaign=self.campaign).filter(profile__is_group=True).filter(profile__group_class_slug=slug).order_by('profile__group_public_name')
        else:
            return User.objects.filter(profile__center_string=self.name).filter(profile__campaign=self.campaign).filter(profile__is_group=True).order_by('profile__group_public_name')


    @property
    def center_teachers(self):
        return User.objects.filter(profile__teacher_belongs_to=self).filter(profile__campaign=self.campaign).filter(profile__is_teacher=True).order_by('username')

    @property
    def center_pupil_tests(self):
        return Quiz.objects.filter(author__isnull=True).filter(campaign=self.campaign).filter(published=True).exclude(type=4).exclude(type=6).order_by('seq')

    def n_groups_center(self):
        return self.center_groups().count()

    def n_students_center(self):
        total = 0
        groups = self.center_groups();
        for g in groups:
            total += g.profile.n_students_in_group
        return total





QUIZ_TYPES = (
    (0, _('Test')),
    (1, _('Material')),
    (2, _('Enquesta')),
    (3, _('Pujar fitxer')),
    (4, _('Enquesta professorat')),
    (5, _('Resposta oberta')),
    (6, _('Resposta oberta professorat')),
)


class Quiz(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    html_header = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)
    type = models.IntegerField(choices=QUIZ_TYPES)
    # To take this quiz, you need to previously complete 'requisite'
    requisite = models.ForeignKey('main.Quiz', null=True, blank=True, on_delete=models.SET_NULL, related_name='allows')
    campaign = models.ForeignKey(Campaign, default=get_current_active_campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name="quizzes")
    seq = models.IntegerField('Sequence in which the quizzes are meant to be taken', blank=True, null=True)
    # When this quiz is completed, send notification
    notify_on_completion = models.BooleanField(default=False)

    def clone(self):
        q = Quiz(
            author=self.author,
            name=self.name,
            html_header=self.html_header,
            published=self.published,
            type=self.type,
            seq=self.seq
        )
        return q

    def __str__(self):
        return "{0} - {1}".format(self.name, self.type_text)

    @property
    def comment_at_the_end(self):
        return self.type == 4

    @property
    def color_bootstrap(self):
        values = {
            0: 'primary',
            1: 'secondary',
            2: 'success',
            3: 'warning',
            5: 'info'
        }
        return values.get(self.type, 5)

    @property
    def type_text(self):
        switcher = {
            0: QUIZ_TYPES[0][1],
            1: QUIZ_TYPES[1][1],
            2: QUIZ_TYPES[2][1],
            3: QUIZ_TYPES[3][1],
            4: QUIZ_TYPES[4][1],
            5: QUIZ_TYPES[5][1],
            6: QUIZ_TYPES[6][1],
        }
        return switcher.get(self.type,_('Tipus invàlid'))

    @property
    def sorted_questions_set(self):
        return self.questions.all().order_by('question_order')

    @property
    def n_questions(self):
        return self.questions.all().count()


    @property
    def is_test(self):
        return self.type == 0

    @property
    def is_open(self):
        return self.type == 5 or self.type == 6

    @property
    def is_open_teacher(self):
        return self.type == 6

    @property
    def is_material(self):
        return self.type == 1

    @property
    def is_poll(self):
        return self.type == 2 or self.type == 4

    @property
    def is_upload(self):
        return self.type == 3

    @property
    def get_next_question_number(self):
        number = 1
        question_numbers = [ q.question_order for q in self.questions.all() ]
        try:
            number = max(question_numbers) + 1
        except:
            pass
        return number

    @property
    def get_material_link(self):
        if self.type == 1:
            if Question.objects.filter(quiz=self).exists():
                return Question.objects.filter(quiz=self).first().doc_link
        return None

    @property
    def taken_by_n_people(self):
        return QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).values('taken_by__id').distinct().count()

    def is_completed_by(self,group_id):
        return QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).filter(taken_by=group_id).exists()

    (0, _('Test')),
    (1, _('Material')),
    (2, _('Enquesta')),
    (3, _('Pujar fitxer')),
    (4, _('Enquesta professorat')),
    (5, _('Resposta oberta')),
    (6, _('Resposta oberta professorat')),

    def n_completed_by_group(self, group):
        # these can be repeated
        if self.type == 0 or self.type == 2:
            return QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).filter(taken_by__in=group).values('taken_by').distinct().count()
        else:
            return QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).filter(taken_by__in=group).count()

    # @property
    # def taken_by_n_people_per_teacher(self):
    #     author = User.objects.get(id=self.author.id)
    #     grupos_profe = User.objects.filter(profile__group_teacher=author)
    #     for r in grupos_profe:
    #         t = QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).values('taken_by__id').distinct().count()
    #         QuizRun.objects.filter(taken_by__id=r.id).filter(quiz=quiz_id).filter(
    #             date_finished__isnull=False).order_by('-questions_right', '-date_finished').first()
    #     return QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).values('taken_by__id').distinct().count()
    def best_run(self, user_id):
        best_run = QuizRun.objects.filter(taken_by__id=user_id).filter(quiz=self).order_by('-questions_right').first()
        return best_run

    @property
    def best_runs(self):
        best_runs = []
        taken_by = QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).values('taken_by__id').distinct()
        for user in taken_by:
            best_run = QuizRun.objects.filter(taken_by__id=user['taken_by__id']).filter(quiz=self).order_by('-questions_right', '-date_finished').first()
            best_runs.append(best_run)
        #sorting by center name and group/user name
        best_runs.sort(key=lambda x: ( x.taken_by.profile.center, x.taken_by.profile.group_public_name if x.taken_by.profile.group_public_name is not None else x.taken_by.username) )
        return best_runs

    @property
    def taken_by(self):
        taken_by = QuizRun.objects.filter(quiz=self).filter(date_finished__isnull=False).values('taken_by__id').distinct()
        for user in taken_by:
            return QuizRun.objects.filter(taken_by__id=user['taken_by__id']).filter(quiz=self).filter(date_finished__isnull=False).distinct()

    @property
    def centers_available(self):
        return EducationCenter.objects.filter(campaign=self.campaign).order_by('name')



# class AssignedQuiz(models.Model):
#     assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
#     assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homework')
#     assigned_on = models.DateTimeField(auto_now_add=True)
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='assignations')

class QuizRun(models.Model):
    taken_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    #computed_score = models.IntegerField(help_text='Score automatically calculated when the quiz is finished', default=0)
    #assigned_score = models.IntegerField(help_text='Score given by tutor. Can be different and supersedes the former.', default=0)
    date = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(blank=True, null=True)
    run_number = models.IntegerField(default=1)
    questions_number = models.IntegerField(help_text='Number of questions when the quiz was finished', default=0)
    questions_right = models.IntegerField(help_text='Number of correctly answered questions in the run', default=0)
    finishing_comments = models.TextField(blank=True, null=True)

    @property
    def next_run(self):
        return self.run_number + 1

    @property
    def last_run(self):
        last_run = QuizRun.objects.filter(taken_by=self.taken_by).filter(quiz=self.quiz).order_by('-run_number').first()
        if last_run:
            return last_run.run_number
        return 0

    def all_questions_answered(self):
        for a in self.answers.all():
            if not a.answered:
                return False
        return True

    @property
    def is_done(self):
        if not self.all_questions_answered():
            return False
        return True


    @property
    def n_runs(self):
        return QuizRun.objects.filter(taken_by=self.taken_by).filter(quiz=self.quiz).values('id').count()

    @property
    def uploaded_file(self):
        if self.quiz.is_upload:
            answer = self.answers.first()
            if answer is not None:
                return answer.uploaded_material
        return None

    @property
    def uploaded_file_id(self):
        if self.quiz.is_upload:
            answer = self.answers.first()
            if answer is not None:
                return answer.id
        return None

    @property
    def authorized_public(self):
        if self.quiz.is_upload:
            answer = self.answers.first()
            if answer is not None:
                return answer.authorize_material_public_use
        return False

    def __str__(self):
        return "{0} ({1}) - {2} - Intent {3}".format(self.quiz.name, self.quiz.type_text, self.taken_by.username, str(self.run_number))

    def evaluate(self):
        answers = self.answers.all()
        questions_number = answers.count()
        questions_right = 0
        questions_right_list = []
        if self.quiz.is_test:
            for answer in answers:
                question = answer.question
                if question.doc_link is not None:
                    questions_right += 1
                    questions_right_list.append(question.question_order)
                else:
                    correct_answer = question.answers.get(is_correct=True)
                    if answer.chosen_answer.id == correct_answer.id:
                        questions_right += 1
                        questions_right_list.append(question.question_order)
            return { 'questions_number': questions_number, 'questions_right': questions_right, 'questions_right_list': questions_right_list }
        else:
            return {'questions_number': questions_number, 'questions_right': questions_number, 'questions_right_list': questions_right_list}


class QuizCorrection(models.Model):
    corrector = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='corrected_quizzes')
    corrected_quizrun = models.ForeignKey(QuizRun, on_delete=models.CASCADE, related_name='corrections')
    date = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    correction_value = models.FloatField(blank=True, null=True)



class QuizRunAnswers(models.Model):
    quizrun = models.ForeignKey(QuizRun, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('main.Question', on_delete=models.CASCADE, related_name='run_question')
    chosen_answer = models.ForeignKey('main.Answer', on_delete=models.CASCADE, related_name='run_answer', null=True, blank=True)
    #chosen answer might not always have a value, so we need a field to indicate that the answer has been answered
    answered = models.BooleanField(default=False)
    uploaded_material = models.FileField(upload_to='media/uploaded/', null=True, blank=True)
    open_answer = models.TextField(blank=True, null=True)
    authorize_material_public_use = models.BooleanField(default=False)


    @property
    def quizrun_info(self):
        return QuizRun.objects.filter(id=self.quizrun_id)


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    #text = models.CharField('Question', max_length=500)
    text = models.TextField('Question')
    question_order = models.IntegerField('Question order inside the quiz', default=1)
    doc_link = models.URLField(max_length=1000, blank=True, null=True)
    question_picture = models.ImageField(upload_to='media/question_pics/', null=True)

    def clone(self):
        q = Question(
            quiz=self.quiz,
            text=self.text,
            question_order=self.question_order,
            doc_link=self.doc_link,
            question_picture=self.question_picture
        )
        return q

    def __str__(self):
        return "{0} - {1}".format(self.text, str(self.quiz))

    @property
    def sorted_answers_set(self):
        return self.answers.all().order_by('label')

    @property
    def sorted_answers_set_2(self):
        return self.answers.objects.filter()

    @property
    def total_number_of_answers_of_question(self):
        n_total = QuizRunAnswers.objects.filter(question=self).filter(answered=True).count()
        return n_total

    def total_number_of_answers_of_question_per_group(self, group_id):
        n_total = QuizRunAnswers.objects.filter(question=self).filter(answered=True).filter(quizrun__taken_by=group_id).count()
        return n_total

    def total_number_of_answers_of_question_per_center(self, center_id):
        center = EducationCenter.objects.get(pk=center_id)
        groups_in_center = User.objects.filter(profile__center_string=center.name).filter(profile__is_group=True)
        n_total = QuizRunAnswers.objects.filter(question=self).filter(answered=True).filter(quizrun__taken_by__in=groups_in_center).count()
        return n_total

    def total_number_of_answers_of_question_per_slug(self, teacher_id, slug):
        teacher = User.objects.get(pk=teacher_id)
        groups_in_slug = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=teacher).filter(profile__group_class_slug=slug)
        n_total = QuizRunAnswers.objects.filter(question=self).filter(answered=True).filter(quizrun__taken_by__in=groups_in_slug).count()
        return n_total

    def total_number_of_answers_of_question_per_center_teachers(self, center_id):
        center = EducationCenter.objects.get(pk=center_id)
        teachers_in_center = User.objects.filter(profile__is_teacher=True).filter(profile__teacher_belongs_to=center)
        n_total = QuizRunAnswers.objects.filter(question=self).filter(answered=True).filter(quizrun__taken_by__in=teachers_in_center).count()
        return n_total


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    label = models.CharField('Label', max_length=10)
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def clone(self):
        a = Answer(
            question=self.question,
            label=self.label,
            text=self.text,
            is_correct=self.is_correct
        )
        return a

    def __str__(self):
        return self.text

    @property
    def how_many_times_answered(self):
        n_this = QuizRunAnswers.objects.filter(chosen_answer=self).filter(answered=True).count()
        return n_this

    def how_many_times_answered_by_group(self,group_id):
        n_this = QuizRunAnswers.objects.filter(chosen_answer=self).filter(quizrun__taken_by=group_id).filter(answered=True).count()
        return n_this

    def how_many_times_answered_by_center(self,center_id):
        center = EducationCenter.objects.get(pk=center_id)
        groups_in_center = User.objects.filter(profile__center_string=center.name).filter(profile__is_group=True)
        n_this = QuizRunAnswers.objects.filter(chosen_answer=self).filter(quizrun__taken_by__in=groups_in_center).filter(answered=True).count()
        return n_this

    def how_many_times_answered_by_slug(self, teacher_id, slug):
        teacher = User.objects.get(pk=teacher_id)
        groups_in_slug = User.objects.filter(profile__is_group=True).filter(profile__group_teacher=teacher).filter(profile__group_class_slug=slug)
        n_this = QuizRunAnswers.objects.filter(chosen_answer=self).filter(quizrun__taken_by__in=groups_in_slug).filter(answered=True).count()
        return n_this

    def how_many_times_answered_by_center_teachers(self,center_id):
        center = EducationCenter.objects.get(pk=center_id)
        teachers_in_center = User.objects.filter(profile__is_teacher=True).filter(profile__teacher_belongs_to=center)
        n_this = QuizRunAnswers.objects.filter(chosen_answer=self).filter(quizrun__taken_by__in=teachers_in_center).filter(answered=True).count()
        return n_this

    def answered_by_perc_group(self,group_id):
        n_total = self.question.total_number_of_answers_of_question_per_group(group_id)
        n_this = self.how_many_times_answered_by_group(group_id)
        if n_total == 0:
            return "0"
        else:
            return str(round((n_this/n_total)*100, 0))

    def answered_by_perc_center_teachers(self,center_id):
        n_total = self.question.total_number_of_answers_of_question_per_center_teachers(center_id)
        n_this = self.how_many_times_answered_by_center_teachers(center_id)
        if n_total == 0:
            return "0"
        else:
            return str(round((n_this / n_total) * 100, 0))

    def answered_by_perc_class(self,teacher_id,slug):
        n_total = self.question.total_number_of_answers_of_question_per_slug(teacher_id, slug)
        n_this = self.how_many_times_answered_by_slug(teacher_id, slug)
        if n_total == 0:
            return "0"
        else:
            return str(round((n_this / n_total) * 100, 0))

    def answered_by_perc_center(self, center_id):
        n_total = self.question.total_number_of_answers_of_question_per_center(center_id)
        n_this = self.how_many_times_answered_by_center(center_id)
        if n_total == 0:
            return "0"
        else:
            return str(round((n_this / n_total) * 100, 0))

    @property
    def answered_by_perc(self):
        #number of total answers of question
        n_total = self.question.total_number_of_answers_of_question
        #number of THIS answer
        n_this = self.how_many_times_answered
        if n_total == 0:
            return "0"
        else:
            return str(round((n_this/n_total)*100, 0))


# class QuizSolution(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answered_questions')
#     alum_answered = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='responses', null=True, blank=True)
#     answered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alum_answers' )
#     completed = models.BooleanField(default=False)
#
#
# class GroupAnswer(models.Model):
#     group = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_answers')
#     answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')


class Word(models.Model):
    word = models.CharField('A word', max_length=50, db_index=True)
    TYPE_CHOICES = (('animal', 'animal'), ('color', 'color'), ('adjective', 'adjective'),)
    type = models.CharField(max_length=9, choices=TYPE_CHOICES, db_index=True)
    language = models.CharField(max_length=2, default='en', db_index=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_teacher = models.BooleanField(default=False)
    is_group = models.BooleanField(default=False)
    is_alum = models.BooleanField(default=False)
    alum_teacher = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="teacher")
    # groups the alum is in
    alum_in_group = models.ManyToManyField(User, related_name="alum_groups")
    teacher_belongs_to = models.ForeignKey(EducationCenter, null=True, on_delete=models.SET_NULL)
    group_password = models.CharField('Password grup', max_length=4, null=True)
    group_public_name = models.CharField(max_length=255, null=True)
    group_picture = models.ImageField(upload_to='media/group_pics/', null=True)
    group_picture_thumbnail = ImageSpecField(source='group_picture', processors=[ResizeToFill(150, 150)], options={'quality': 80})
    group_picture_thumbnail_small = ImageSpecField(source='group_picture', processors=[ResizeToFill(50, 50)],options={'quality': 80})
    group_teacher = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="group_teacher")
    # class label, for filters
    group_class = models.CharField(max_length=500, null=True)
    group_class_slug = models.CharField(max_length=500, null=True)
    groups_string = models.CharField(max_length=1000, null=True, blank=True)
    center_string = models.CharField(max_length=1000, null=True, blank=True)
    n_students_in_group = models.IntegerField(default=3)
    group_hashtag = models.CharField(max_length=20, null=True, blank=True, unique=True)
    campaign = models.ForeignKey(Campaign, default=get_current_active_campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name="profiles")
    teacher_password = models.CharField(max_length=128, null=True)
    consent_form_visited = models.BooleanField(default=False)
    auth_tutor = models.BooleanField(default=False)
    
    def __str__(self):
        if self.is_group:
            user_type = 'group'
        elif self.is_teacher:
            user_type = 'teacher'
        else:
            user_type = 'other'
        return "{0} - {1}".format(self.user.username, user_type)

    @property
    def center(self):
        if self.is_teacher:
            return self.teacher_belongs_to.name
        if self.is_group:
            return self.group_teacher.profile.teacher_belongs_to.name
        return ''

    # @property
    # def full_auth_granted(self):
    #     this_auth_group = None
    #     consents_group = ConsentPupil.objects.filter(profile=self)
    #     if consents_group.count() == 0 or not consents_group.exists():
    #         this_auth_group = False
    #     else:
    #         if consents_group.count() != self.n_students_in_group:
    #             this_auth_group = False
    #         else:
    #             for ind_consent in consents_group:
    #                 if this_auth_group is None:
    #                     this_auth_group = ind_consent.consent
    #                 else:
    #                     this_auth_group = this_auth_group and ind_consent.consent
    #     return self.auth_tutor and this_auth_group

    @property
    def full_auth_granted(self):
        """
        Check if all students in the group have given consent.
        Returns True if all students have consented, False otherwise.
        """
        # Get all ConsentPupil objects for this profile
        consent_pupils = self.group_consent.all()

        # If there are no consent pupils, return False
        if not consent_pupils.exists() or consent_pupils.count() != self.n_students_in_group:
            return False

        # Check if all consent values are True
        return all(pupil.consent for pupil in consent_pupils)

    @property
    def groups_list(self):
        groups = []
        for g in self.alum_in_group.all():
            groups.append(g.profile.group_public_name)
        return ','.join(groups)

    @property
    def tutored_groups(self):
        if self.is_teacher:
            return User.objects.filter(profile__is_group=True).filter(profile__group_teacher=self.user).count()
        else:
            return 0

    @property
    def available_tests(self):
        if self.is_teacher:
            return None
        elif self.is_group:
            group_campaign = self.campaign
            return Quiz.objects.filter(Q(author=self.group_teacher) | Q(author__isnull=True)).filter(campaign=group_campaign).filter(published=True).exclude(type=4).exclude(type=6).order_by('name')

    @property
    def available_tests_ordered(self):
        if self.is_teacher:
            return None
        elif self.is_group:
            group_campaign = self.campaign
            return Quiz.objects.filter(Q(author=self.group_teacher) | Q(author__isnull=True)).filter(
                campaign=group_campaign).filter(published=True).exclude(type=4).exclude(type=6).order_by('seq')

    # for normal users, the campaign is assigned and never changed. The admin can change the current campaign at a given time
    @property
    def get_user_campaign(self):
        if self.user.is_superuser:
            try:
                campaign = Campaign.objects.get(active=True)
                return campaign
            except Campaign.DoesNotExist:
                return None
        else:
            return self.campaign



def get_string_from_groups(profile):
    groups = []
    for g in profile.alum_in_group.all():
        groups.append(g.profile.group_public_name)
    return ','.join(groups)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    # print(created)
    # if instance.profile.is_alum:
    #     group_string = get_string_from_groups(instance.profile)
    #     center_string = None
    #     if instance.profile.alum_teacher and instance.profile.alum_teacher.profile.teacher_belongs_to:
    #         center_string = instance.profile.alum_teacher.profile.teacher_belongs_to.name
    #     instance.profile.center_string = center_string
    #     instance.profile.groups_string = group_string
    # instance.profile.save()
    if instance.profile.is_group:
        center_string = None
        education_center = None
        if instance.profile.group_teacher and instance.profile.group_teacher.profile.teacher_belongs_to:
            education_center = instance.profile.group_teacher.profile.teacher_belongs_to
            center_string = education_center.name
        instance.profile.center_string = center_string
        if education_center is not None and instance.profile.group_hashtag is None:
            groups = education_center.center_groups()
            if groups.count() == 0:
                instance.profile.group_hashtag = education_center.hashtag + "_1"
            else:
                higher_index = -1
                no_one_has_hashtag = True
                for group in groups:
                    group_hashtag = group.profile.group_hashtag
                    if group_hashtag is not None:
                        no_one_has_hashtag = False
                        if "_" in group_hashtag:
                            s = group_hashtag.split("_")
                            try:
                                value = int(s[1])
                                if value > higher_index:
                                    higher_index = value
                            except ValueError:
                                pass
                if no_one_has_hashtag:
                    instance.profile.group_hashtag = education_center.hashtag + "_1"
                elif higher_index != -1:
                    instance.profile.group_hashtag = education_center.hashtag + "_" + str(higher_index + 1)
    instance.profile.save()


class ConsentPupil(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="group_consent")
    n = models.IntegerField()
    consent = models.BooleanField(default=False)


class BreedingSites(models.Model):
    version_uuid = models.CharField(max_length=36, blank=True, unique=True)
    observation_date = models.DateTimeField(null=True, blank=True)
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    private_webmap_layer = models.CharField(max_length=255, blank=True)
    photo_url = models.CharField(max_length=255, blank=True)
    note = models.TextField()
    center_hashtag = models.CharField(max_length=100, blank=True)
    campaign = models.ForeignKey(Campaign, null=True, blank=True, on_delete=models.SET_NULL, related_name="breeding_sites")


class Awards(models.Model):
    age_bracket = models.CharField(max_length=36, blank=True)
    format = models.CharField(max_length=100, blank=True)
    award = models.CharField(max_length=100, blank=True)
    group = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="group_awards")
    center = models.ForeignKey(EducationCenter, null=True, blank=True, on_delete=models.CASCADE, related_name="center_awards")


class CheckedQuizrun(models.Model):
    checked_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="checked_quizruns")
    quiz = models.ForeignKey(Quiz, null=True, blank=True, on_delete=models.CASCADE, related_name="checks")
    group = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="checkedbyadmin_quizruns")


class CenterMapData(models.Model):
    name = models.CharField(max_length=500)
    lat = models.FloatField()
    lon = models.FloatField()
    year = models.IntegerField()
    participation_years = models.CharField(max_length=100, null=True)
    hashtag = models.CharField(max_length=100)
    n_pupils = models.IntegerField(default=0)
    n_groups = models.IntegerField(default=0)
    n_bs_total = models.IntegerField(default=0)
    n_storm_drain_water = models.IntegerField(default=0)
    n_storm_drain_dry = models.IntegerField(default=0)
    no_other_bs = models.IntegerField(default=0)
    has_awards = models.BooleanField(default=False)


class MapAwardData(models.Model):
    age_bracket = models.CharField(max_length=500)
    format = models.CharField(max_length=500)
    award = models.CharField(max_length=500)
    center_hashtag = models.CharField(max_length=100)
    center_name = models.CharField(max_length=500)
    group_hashtag = models.CharField(max_length=100)
    group_name = models.CharField(max_length=500)


class InternalNotification(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="senders")
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="receivers")
    notification_text = models.CharField(max_length=1500)
    read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    class_label = models.CharField(max_length=150, null=True)

    def crea_query_de_filtre(json_filtre):
        field = json_filtre['field']
        value = json_filtre['value']
        if json_filtre['value'] == 'totes':
            return None
        elif json_filtre['value'] == 'llegides':
            value = True
        else:
            value = False
        filter_kwargs = {field:value}
        return Q(**filter_kwargs)