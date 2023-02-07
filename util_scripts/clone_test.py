import app_config

from main.models import Profile, EducationCenter, Campaign, Quiz, Question, Answer
import csv
import string
import random
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
from django.contrib.gis.geos import GEOSGeometry
import csv


def clone_quiz(test_pk, campaign_to_move_to_id):
    quiz = Quiz.objects.get(pk=test_pk)
    target_campaign = Campaign.objects.get(pk=campaign_to_move_to_id)

    cloned_quiz = quiz.clone()
    cloned_quiz.campaign = target_campaign
    cloned_quiz.save()

    print("Cloned quiz {0} with id {1} new id {2}".format( quiz.name, quiz.id, cloned_quiz.id ))
    for question in quiz.questions.all().order_by('question_order'):
        clone_question( cloned_quiz, question )


def clone_question(cloned_quiz, question):
    cloned_question = question.clone()
    cloned_question.quiz = cloned_quiz
    cloned_question.save()
    print("\tCloned question '{0}' with id {1} new id {2}".format( question.text, question.id, cloned_question.id ))
    for answer in question.answers.all().order_by('label'):
        clone_answer( cloned_question, answer )


def clone_answer(cloned_question, answer):
    cloned_answer = answer.clone()
    cloned_answer.question = cloned_question
    cloned_answer.save()
    print("\t\tCloned Answer '{0}' with id {1} new id {2}".format(answer.text, answer.id, cloned_answer.id))


def main():
    clone_quiz(290, 5)


if __name__ == '__main__':
    main()
