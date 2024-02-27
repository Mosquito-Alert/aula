import app_config

from django.contrib.auth.models import User, Group
from main.models import QuizRun, Campaign, EducationCenter, Quiz
from main.views import do_copy
from django.db import transaction
from datetime import date
import csv
from django.contrib.gis.geos import GEOSGeometry
from slugify import slugify

ORIGIN_CAMPAIGNS = ['FECYT 22/23 PRIMARIA','FECYT 22/23 ESO','FECYT 22/23 BATX','BCN 22/23','Netherlands 2023']
DESTINATION_CAMPAIGNS = ['FECYT 23/24 PRIMARIA','FECYT 23/24 ESO','FECYT 23/24 BATX','BCN 23/24 ESO','Netherlands 2024']
USERS_FILE = app_config.proj_path + '/util_scripts/campaigns_2024.csv'

def get_center_hashtag(center_slug, center_name, campaign_name):
    print(center_name)
    if center_name == 'IES Cervantes':
        center_slug = '#ice24'
    if center_name == 'IES ALFONSO VI':
        center_slug = '#ievi24'
    if center_name == 'Colegio Asunción Cuestablanca':
        center_slug = '#coac24'
    if center_name == 'CIFP A Carballeira':
        center_slug = '#ciac24'
    if center_name == 'IES AZUER':
        center_slug = '#iaz24'
    if center_name == 'INS Alzina':
        center_slug = '#ial24'
    if center_name == 'CEIP Virgen de Argeme de Coria en Cáceres':
        center_slug = '#cvac24'
    if center_name == 'CPR PLURILINGÜE CASA  DE LA VIRGEN':
        center_slug = '#cpcv24'
    if center_name == 'Colegio San José de Cluny de Vigo':
        center_slug = '#csjc24'
    if center_name == 'Eskibel' or center_name == 'IES Carpetania':
        if campaign_name == 'FECYT 23/24 BATX':
            return center_slug + 'b'
        elif campaign_name == 'FECYT 23/24 PRIMARIA':
            return center_slug + 'p'
        elif campaign_name == 'FECYT 23/24 ESO':
            return center_slug + 'e'
        elif campaign_name == 'BCN 23/24 ESO':
            return center_slug + 'bc'
        else:
            return center_slug + 'nl'
    else:
        return center_slug
def add_csv_data():
    with open(USERS_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            campaign_name = row[8]
            center_name = row[1]
            campaign = Campaign.objects.get(name=campaign_name)
            center = None
            try:
                center = EducationCenter.objects.get(name=center_name, campaign=campaign)
                center_slug = center.center_slug()
                center.hashtag = get_center_hashtag(center_slug, center_name, campaign_name)
                center.save()
            except EducationCenter.DoesNotExist:
                location = GEOSGeometry('POINT (0 0)', srid=4326)
                center = EducationCenter(name=center_name,campaign=campaign,location=location)
                center_slug = center.center_slug()
                center.hashtag = get_center_hashtag(center_slug, center_name, campaign_name)
                center.save()

            teacher_name = row[5]
            password = row[6]
            teacher_user = User.objects.create_user(username=teacher_name, password=password)
            teacher_user.save()
            teacher_user.profile.is_teacher = True
            teacher_user.profile.teacher_belongs_to = center
            teacher_user.profile.campaign = campaign
            teacher_user.profile.teacher_password = password
            teacher_user.save()




def create_campaigns():
    today = date.today()
    for cmp_name in DESTINATION_CAMPAIGNS:
        c = Campaign(name=cmp_name)
        c.start_date = today
        c.save()

def delete_other_campaigns():
    #delete everything that is not a destination campaign
    qs = Campaign.objects.exclude(name__in=DESTINATION_CAMPAIGNS)
    qs.delete()
    #delete also quizzes without campaign
    qs = Quiz.objects.filter(campaign__isnull=True)
    qs.delete()

def delete_orphan_centers():
    qs = EducationCenter.objects.filter(campaign__isnull=True)
    qs.delete()

def transfer_tests():
    campaigns = {
        'from':ORIGIN_CAMPAIGNS,
        'to':DESTINATION_CAMPAIGNS
    }
    for idx, campaign_name in enumerate(campaigns['from']):
        from_campaign = Campaign.objects.get(name=campaign_name)
        to_campaign = Campaign.objects.get(name=campaigns['to'][idx])
        for quiz in from_campaign.quizzes.all():
            do_copy(quiz.id,to_campaign.id)

def rename_new_tests():
    qs = Quiz.objects.all()
    for quiz in qs:
        quiz.name = quiz.name.replace('_COPY','')
        quiz.save()

def delete_users():
    master = User.objects.get(username='aula_master')
    User.objects.exclude(username='aula_master').delete()
    QuizRun.objects.filter(taken_by=master).delete()

def requisites_c1():
    # 'FECYT 23/24 PRIMARIA'
    q = Quiz.objects.get(campaign__name='FECYT 23/24 PRIMARIA', name='Encuesta inicial - Profesorado')
    q1 = Quiz.objects.get(campaign__name='FECYT 23/24 PRIMARIA', name='Encuesta final - Profesorado')
    q1.requisite = q
    q1.save()

def requisites_c2():
    # 'FECYT 23/24 ESO',
    q = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Encuesta inicial - Alumnado')
    q1 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Introducción')
    q1.requisite = q
    q1.save()
    q2 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Orientación - Entrenamiento entomológico')
    q2.requisite = q1
    q2.save()
    q3 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Orientación - Herramientas tecnológicas')
    q3.requisite = q2
    q3.save()
    q4 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Aprendizaje práctico - Laboratorio')
    q4.requisite = q3
    q4.save()
    q5 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Aprendizaje práctico - Preparación del safari')
    q5.requisite = q3
    q5.save()
    q6 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Aprendizaje práctico - Safari')
    q6.requisite = q3
    q6.save()
    q7 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO',
                          name='Acción - Cómo hacer una buena campaña de comunicación')
    q7.requisite = q5
    q7.save()
    q8 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Productos comunicativos')
    q8.requisite = q7
    q8.save()
    q9 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Encuesta inicial - Profesorado')
    q10 = Quiz.objects.get(campaign__name='FECYT 23/24 ESO', name='Encuesta final - Profesorado')
    q10.requisite = q9
    q10.save()

def requisites_c3():
    # 'FECYT 23/24 BATX',
    q1 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Encuesta inicial - Alumnado')
    q2 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Introducción')
    q2.requisite = q1
    q2.save()

    q3 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Orientación - Entrenamiento entomológico')
    q3.requisite = q2
    q3.save()

    q4 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Orientación - Herramientas tecnológicas')
    q4.requisite = q3
    q3.save()

    q5 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX',
                          name='Aprendizaje práctico - Recolección de datos con la App')
    q5.requisite = q4
    q5.save()

    q6 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX',
                          name='Aprendizaje práctico - Recolección de datos con la App')
    q6.requisite = q4
    q6.save()

    q7 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Acción - Pregunta investigable (contenidos)')
    q7.requisite = q4
    q7.save()

    q8 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Acción - Diseñando la pregunta investigable')
    q8.requisite = q7
    q8.save()

    q9 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Poster científico')
    q9.requisite = q8
    q9.save()

    q10 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Encuesta inicial - Profesorado')
    q11 = Quiz.objects.get(campaign__name='FECYT 23/24 BATX', name='Encuesta final - Profesorado')
    q11.requisite = q10
    q11.save()

def requisites_c4():
    # 'BCN 23/24 ESO',
    q1 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Enquesta inicial alumnes')
    q2 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Introducció')
    q2.requisite = q1
    q2.save()

    q3 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Orientació - Entrenament entomològic')
    q3.requisite = q2
    q3.save()

    q4 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Orientació - Entrenament tecnològic')
    q4.requisite = q3
    q4.save()

    q5 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Aprenentatge pràctic - Laboratori')
    q5.requisite = q4
    q5.save()

    q6 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Aprenentatge pràctic - Preparació del safari')
    q6.requisite = q5
    q6.save()

    q7 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Aprenentatge pràctic - Safari')
    q7.requisite = q6
    q7.save()

    q8 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Com fer una bona campanya de comunicació')
    q8.requisite = q7
    q8.save()

    q9 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Producte comunicatiu')
    q9.requisite = q8
    q9.save()

    q10 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Enquesta inicial - Professorat')
    q11 = Quiz.objects.get(campaign__name='BCN 23/24 ESO', name='Enquesta final - Professorat')
    q11.requisite = q10
    q11.save()

def requisites_c5():
    # 'Netherlands 2024'
    q1 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Initial survey - Students')
    q2 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Introduction')
    q2.requisite = q1
    q2.save()

    q3 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Orientation - Enthomological training')
    q3.requisite = q1
    q3.save()

    q4 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Orientation - Technological tools')
    q4.requisite = q3
    q4.save()

    q5 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Action - Data collection')
    q5.requisite = q4
    q5.save()

    q6 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Action - Reseach question (theoretical contents)')
    q6.requisite = q5
    q6.save()

    q7 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Action - Designing the research question')
    q7.requisite = q6
    q7.save()

    q8 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Scientific poster')
    q8.requisite = q7
    q8.save()

    q9 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Self-assessment')
    q9.requisite = q8
    q9.save()

    q10 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Final survey - Students')
    q10.requisite = q9
    q10.save()

    q11 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Initial survey - Teachers')
    q12 = Quiz.objects.get(campaign__name='Netherlands 2024', name='Final survey - Teachers')
    q12.requisite = q11
    q12.save()

def set_requisites():
    requisites_c1()
    requisites_c2()
    requisites_c3()
    requisites_c4()
    requisites_c5()

def set_current_active_campaign():
    c = Campaign.objects.get(name='FECYT 23/24 ESO')
    c.active = True
    c.save()

def main():
    with transaction.atomic():
        delete_users()
        create_campaigns()
        transfer_tests()
        delete_other_campaigns()
        delete_orphan_centers()
        add_csv_data()
        rename_new_tests()
        set_requisites()
        set_current_active_campaign()


if __name__ == '__main__':
    main()
