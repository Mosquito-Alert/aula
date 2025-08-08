import app_config

from main.models import Quiz, EducationCenter
from slugify import slugify
import csv

WORKING_DIR = app_config.proj_path + '/util_scripts/'

def print_results_center(quiz_id, center_id):
    data = []
    quiz = Quiz.objects.get(pk=quiz_id)
    center = EducationCenter.objects.get(pk=center_id)
    campaign = quiz.campaign
    filename = WORKING_DIR + "{0}_{1}_{2}.csv".format(slugify(campaign.name), slugify(quiz.name), slugify(center.name))
    for question in quiz.sorted_questions_set:
        for answer in question.sorted_answers_set:
            data.append(
                [question.question_order, question.text, answer.label, answer.text, answer.how_many_times_answered_by_center(center_id),
                 answer.question.total_number_of_answers_of_question_per_center(center_id)])
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(
            ['ordre_pregunta', 'text_pregunta', 'etiqueta_resposta', 'text_resposta', 'n_respostes', 'n_total'])
        for d in data:
            writer.writerow(d)

def print_results(quiz_id):
    data = []
    quiz = Quiz.objects.get(pk=quiz_id)
    campaign = quiz.campaign
    filename = WORKING_DIR + "{0}_{1}.csv".format( slugify(campaign.name), slugify(quiz.name) )
    for question in quiz.sorted_questions_set:
        for answer in question.sorted_answers_set:
            data.append([ question.question_order, question.text, answer.label, answer.text, answer.how_many_times_answered, answer.question.total_number_of_answers_of_question ])
    with open(filename,'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['ordre_pregunta','text_pregunta','etiqueta_resposta','text_resposta','n_respostes','n_total'])
        for d in data:
            writer.writerow(d)


if __name__ == '__main__':
    # print_results(78)
    # print_results(89)
    # print_results(74)
    # print_results(100)
    # print_results(103)
    # print_results(115)
    # print_results(121)
    # print_results(133)
    # Ins Doctor Puigvert
    # print_results_center(121, 135)
    # print_results_center(133, 135)
    # Ins Maria Espinalt
    # print_results_center(121, 136)
    # print_results_center(133, 136)
    # Valldemossa
    # print_results_center(74, 134)
    # print_results_center(100, 134)

    #quiz_ids = [331,334,340,343]
    #center_ids = [497,498,520,525,526,532]

    quiz_ids = [358, 371, 359, 370]
    center_ids = [518, 519, 530]

    for quiz in quiz_ids:
        for center in center_ids:
            print_results_center(quiz, center)



