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

    def __str__(self):
        return self.name


class TakenQuiz(models.Model):
    taken_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class GroupAnswer(models.Model):
    group = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')


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
    alum_in_group = models.ManyToManyField(User, related_name="alum_groups")
    teacher_belongs_to = models.ForeignKey(EducationCenter, null=True, on_delete=models.SET_NULL)
    group_password = models.CharField('Password grup', max_length=4, null=True)
    group_public_name = models.CharField(max_length=255, null=True)
    group_picture = models.ImageField(upload_to='media/group_pics/', null=True)
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
    if instance.profile.is_alum:
        group_string = get_string_from_groups(instance.profile)
        center_string = None
        if instance.profile.alum_teacher and instance.profile.alum_teacher.profile.teacher_belongs_to:
            center_string = instance.profile.alum_teacher.profile.teacher_belongs_to.name
        instance.profile.center_string = center_string
        instance.profile.groups_string = group_string
    instance.profile.save()