from django import template
from main.models import QuizRunAnswers, Question

register = template.Library()

@register.simple_tag
def how_many_times_answered_by_group( group_id, answer_id ):
    n_this = QuizRunAnswers.objects.filter(chosen_answer__id=answer_id).filter(quizrun__taken_by__id=group_id).filter(answered=True).count()
    return n_this

@register.simple_tag
def total_number_of_answers_of_question_per_group( question_id, group_id ):
    n_total = QuizRunAnswers.objects.filter(question__id=question_id).filter(answered=True).filter(quizrun__taken_by=group_id).count()
    return n_total

@register.simple_tag
def answered_by_perc_group( question_id, group_id, answer_id):
    n_total = QuizRunAnswers.objects.filter(question__id=question_id).filter(answered=True).filter(quizrun__taken_by=group_id).count()
    n_this = QuizRunAnswers.objects.filter(chosen_answer__id=answer_id).filter(quizrun__taken_by__id=group_id).filter(answered=True).count()
    if n_total == 0:
        return "0"
    else:
        return str(round((n_this/n_total)*100, 0))
