import app_config

from main.models import Quiz, QuizRun, Campaign, QuizRunAnswers
from slugify import slugify
import os
from urllib.request import urlopen

OUT_DIR = '/tmp/camps'
BASE_URL = 'https://humboldt2.ceab.csic.es/media/'


def download_and_save_as( url, save_as ):
    with urlopen(url) as file:
        content = file.read()

    # Save to file
    with open(save_as, 'wb') as download:
        download.write(content)

def do_work(campaign_filter=None, quiz_filter=None, center_filter=None):
    if campaign_filter is not None:
        campaigns = Campaign.objects.filter(id=campaign_filter).all().order_by('name')
    else:
        campaigns = Campaign.objects.all().order_by('name')
    for campaign in campaigns:
        if quiz_filter is not None:
            quizzes = Quiz.objects.filter(type=3).filter(campaign=campaign).filter(published=True).filter(id=quiz_filter)
        else:
            quizzes = Quiz.objects.filter(type=3).filter(campaign=campaign).filter(published=True)
        quizruns = QuizRun.objects.filter(quiz__in=quizzes).filter(date_finished__isnull=False)
        materials = QuizRunAnswers.objects.filter( quizrun__in=quizruns )
        for m in materials:
            if m.quizrun.taken_by.profile.is_group:
                quiz = m.quizrun.quiz
                quiz_slug = slugify(quiz.name)
                campaign_slug = slugify(campaign.name)
                center = m.quizrun.taken_by.profile.group_teacher.profile.teacher_belongs_to
                center_slug = slugify( center.name )
                group = m.quizrun.taken_by.profile.group_public_name
                group_slug = slugify( group )
                filename = "{0}/{1}/{2}/{3}/{4}.zip".format( OUT_DIR, campaign_slug, center_slug, group_slug, quiz_slug )
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                url = BASE_URL +  str(m.uploaded_material)
                print("Downloading {0} to file {1}".format(url, filename))
                download_and_save_as( url, filename )
                # with open(filename, "w") as f:
                #     f.write("FOOBAR")


def main():
    do_work()

if __name__ == '__main__':
    main()
