from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
import os
from datetime import datetime


class EducationCenter(models.Model):
    name = models.CharField(max_length=500)
    location = models.PointField(srid=4326, null=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def sorted_questions_set(self):
        return self.questions.all().order_by('question_order')

    @property
    def get_next_question_number(self):
        number = 1
        question_numbers = [ q.question_order for q in self.questions.all() ]
        try:
            number = max(question_numbers) + 1
        except:
            pass
        return number


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

    @property
    def next_run(self):
        return self.run_number + 1

    @property
    def last_run(self):
        last_run = QuizRun.objects.filter(taken_by=self.taken_by).filter(quiz=self.quiz).order_by('-run_number').first()
        if last_run:
            return last_run.run_number
        return 0

    def is_done(self):
        for a in self.answers.all():
            if not a.answered:
                return False
        return True

    @property
    def n_runs(self):
        return QuizRun.objects.filter(taken_by=self.taken_by).filter(quiz=self.quiz).values('id').count()

    def evaluate(self):
        answers = self.answers.all()
        questions_number = answers.count()
        questions_right = 0
        questions_right_list = []
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



class QuizRunAnswers(models.Model):
    quizrun = models.ForeignKey(QuizRun, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('main.Question', on_delete=models.CASCADE, related_name='run_question')
    chosen_answer = models.ForeignKey('main.Answer', on_delete=models.CASCADE, related_name='run_answer', null=True, blank=True)
    #chosen answer might not always have a value, so we need a field to indicate that the answer has been answered
    answered = models.BooleanField(default=False)



class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)
    question_order = models.IntegerField('Question order inside the quiz')
    doc_link = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.text

    @property
    def sorted_answers_set(self):
        return self.answers.all().order_by('label')


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    label = models.CharField('Label', max_length=10)
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


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
    word = models.CharField('A word', max_length=50, unique=True, db_index=True)
    TYPE_CHOICES = (('animal', 'animal'), ('color', 'color'), ('adjective', 'adjective'),)
    type = models.CharField(max_length=9, choices=TYPE_CHOICES, db_index=True)


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
    group_teacher = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="group_teacher")
    groups_string = models.CharField(max_length=1000, null=True, blank=True)
    center_string = models.CharField(max_length=1000, null=True, blank=True)

    @property
    def groups_list(self):
        groups = []
        for g in self.alum_in_group.all():
            groups.append(g.profile.group_public_name)
        return ','.join(groups)


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
def save_user_profile(sender, instance, **kwargs):
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
        if instance.profile.group_teacher and instance.profile.group_teacher.profile.teacher_belongs_to:
            center_string = instance.profile.group_teacher.profile.teacher_belongs_to.name
        instance.profile.center_string = center_string
    instance.profile.save()