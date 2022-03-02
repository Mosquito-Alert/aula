import app_config

from main.models import Quiz, Answer, Question, Campaign


def copy_quiz(original, new_campaign, append_title):
    # original = Quiz.objects.get(pk=id_original)
    # new_campaign = Campaign.objects.get(pk=new_campaign_id)
    new_quiz = Quiz(
        author=original.author,
        name=original.name + append_title,
        html_header=original.html_header,
        published=original.published,
        type=original.type,
        requisite=original.requisite,
        campaign=new_campaign
    )
    new_quiz.save()
    original_questions = original.sorted_questions_set
    for original_question in original_questions:
        new_question = Question(
            quiz=new_quiz,
            text=original_question.text,
            question_order=original_question.question_order,
            doc_link=original_question.doc_link,
            question_picture=original_question.question_picture
        )
        new_question.save()
        for original_answer in original_question.sorted_answers_set:
            new_answer = Answer(
                question=new_question,
                label=original_answer.label,
                text=original_answer.text,
                is_correct=original_answer.is_correct
            )
            new_answer.save()
    return new_quiz

def main():
    originals = Quiz.objects.filter(campaign__id=1)
    new_campaign = Campaign.objects.get(pk=2)
    text_append = " - 2022"
    ids_table = {}
    for original in originals:
        new_quiz = copy_quiz(original, new_campaign, text_append)
        old_id = original.id
        new_id = new_quiz.id
        ids_table[old_id] = new_id
    news = Quiz.objects.filter(campaign=new_campaign)
    for new in news:
        if new.requisite is not None:
            new_requisite = Quiz.objects.get(pk=ids_table[new.requisite.id])
            new.requisite = new_requisite
            new.save()

# DELETE FROM main_answer where question_id in ( select id from main_question where quiz_id = x )
# DELETE FROM main_question where quiz_id = x
# DELETE FROM main_quiz where id = x

if __name__ == '__main__':
    main()

