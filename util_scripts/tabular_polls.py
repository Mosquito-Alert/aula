import app_config

import os, sys
from main.models import Quiz, QuizRun, QuizRunAnswers
import csv

def main(quiz_id):
    filename = '/tmp/tabular_results_{0}.csv'.format(quiz_id)
    q = Quiz.objects.get(pk=quiz_id)
    questions = q.sorted_questions_set
    questions_table = [0 for i in range( len(questions) )]
    for question in questions:
        questions_table[question.question_order - 1] = { 'text':question.text, 'id': question.id }
    quizruns = QuizRun.objects.filter(quiz=q).exclude(date_finished__isnull=True).order_by('taken_by_id','run_number')
    results = []
    headers = ['quiz_id','quiz_name','date_finished','attempt_n','group_id','center','class']
    for question_data in questions_table:
        headers.append( question_data['text'] )
    results.append(headers)
    for qr in quizruns:
        row = []
        row.append( q.id )
        row.append( q.name )
        row.append(qr.date_finished)
        row.append( qr.run_number )
        row.append( qr.taken_by_id )
        row.append( qr.taken_by.profile.center_string )
        row.append(qr.taken_by.profile.group_class )
        #then append answers
        for this_question in questions_table:
            chosen_answer = QuizRunAnswers.objects.get(quizrun=qr,question_id=this_question['id']).chosen_answer
            row.append( chosen_answer.text )
        results.append(row)

    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for r in results:
            writer.writerow(r)

if __name__ == '__main__':
    args = sys.argv[1:]
    n_args = len(args)
    if n_args != 1:
        print("Invalid n of arguments, passed {0}, required 1".format(n_args))
        sys.exit(2)
    else:
        quiz_id = int(args[0])
        main(quiz_id)
