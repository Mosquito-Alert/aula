import app_config

from django.contrib.auth.models import User, Group
from main.models import QuizRun, Campaign, EducationCenter, Quiz
from main.views import do_copy
from django.db import transaction
from datetime import date
import csv
from django.contrib.gis.geos import GEOSGeometry
from slugify import slugify
import datetime

ORIGIN_CAMPAIGNS = ['FECYT 24/25 ESO','FECYT 24/25 PRIMARIA','FECYT 24/25 BATX','BCN 24/25 BATX','BCN 24/25 ESO']
DESTINATION_CAMPAIGNS = ['FECYT 25/26 ESO','FECYT 25/26 PRIMARIA','FECYT 25/26 BATX','BCN 25/26 BATX','BCN 25/26 ESO']
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
    today = datetime.datetime(2026, 1, 1)
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
    # FECYT 25/26 ESO
    # requisits
    q = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Introducción') #304
    q1 = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Encuesta inicial - Profesorado') #308
    q2 = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Encuesta inicial - Alumnado') #309
    q3 = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Aprendizaje práctico - Preparación del safari') #315
    q4 = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Orientación - Herramientas tecnológicas') #314
    q5 = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Autoevaluación - Encuesta final (Alumnado)')  # 313

    #Requereixen 304
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Aprendizaje práctico - Laboratorio')
    qr.requisite = q
    qr.save()
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Orientación - Entrenamiento entomológico')
    qr.requisite = q
    qr.save()
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Orientación - Herramientas tecnológicas')
    qr.requisite = q
    qr.save()

    # Requereixen 308
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Encuesta final - Profesorado')
    qr.requisite = q1
    qr.save()

    # Requereixen 309
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Introducción')
    qr.requisite = q2
    qr.save()

    # Requereixen 315
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Aprendizaje práctico - Safari')
    qr.requisite = q3
    qr.save()

    # Requereixen 314
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Acción - Cómo hacer una buena campaña de comunicación')
    qr.requisite = q4
    qr.save()
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Aprendizaje práctico - Preparación del safari')
    qr.requisite = q4
    qr.save()

    # Requereixen 313
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 ESO', name='Productos comunicativos')
    qr.requisite = q5
    qr.save()

def requisites_c2():
    # FECYT 25/26 PRIMARIA
    # requisits
    q1 = Quiz.objects.get(campaign__name='FECYT 25/26 PRIMARIA', name='Encuesta Inicial Alumnado') #372
    q2 = Quiz.objects.get(campaign__name='FECYT 25/26 PRIMARIA', name='Encuesta Final Alumnos') #374
    q3 = Quiz.objects.get(campaign__name='FECYT 25/26 PRIMARIA', name='Encuesta inicial - Profesorado') #302

    # requereixen 372
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 PRIMARIA', name='Encuesta Final Alumnos')
    qr.requisite = q1
    qr.save()
    # requereixen 374
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 PRIMARIA', name='Producto Final')
    qr.requisite = q2
    qr.save()
    # requereixen 302
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 PRIMARIA', name='Encuesta final - Profesorado')
    qr.requisite = q3
    qr.save()


def requisites_c3():
    # FECYT 25/26 BATX
    # Requisits
    q1 = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Introducción') #318
    q2 = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Encuesta inicial - Profesorado')  # 319
    q3 = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Orientación - Herramientas tecnológicas')  # 326
    q4 = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Introducción')  # 327
    q5 = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Autoevaluación - Encuesta final - Alumnado') #329
    q6 = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Acción - Pregunta investigable (contenidos)')  # 330

    #requereixen 318
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Orientación - Herramientas tecnológicas')
    qr.requisite = q1
    qr.save()
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Orientación - Entrenamiento entomológico')
    qr.requisite = q1
    qr.save()

    # requereixen 319
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Encuesta final - Profesorado')
    qr.requisite = q2
    qr.save()

    # requereixen 326
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Acción - Pregunta investigable (contenidos)')
    qr.requisite = q3
    qr.save()
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Aprendizaje práctico - Recolección de datos con la App')
    qr.requisite = q3
    qr.save()

    # requereixen 327
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Introducción')
    qr.requisite = q4
    qr.save()

    # requereixen 329
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Autoevaluación - Encuesta final - Alumnado')
    qr.requisite = q5
    qr.save()
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Poster científico')
    qr.requisite = q5
    qr.save()

    # requereixen 330
    qr = Quiz.objects.get(campaign__name='FECYT 25/26 BATX', name='Acción - Diseñando la pregunta investigable')
    qr.requisite = q6
    qr.save()


def requisites_c4():
    # BCN 25/26 BATX
    # Requisits
    q1 = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Enquesta inicial - Professorat') #358
    q2 = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Enquesta inicial alumnes') #359
    q3 = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Introducció') #360
    q4 = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Orientació - Entrenament tecnològic') #362
    q5 = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Acció - Pregunta Investigable (continguts)') #364
    q6 = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Acció - Dissenyant la pregunta investigable') #365

    # requereixen 358
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Enquesta final - Professorat')
    qr.requisite = q1
    qr.save()

    # requereixen 359
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Introducció')
    qr.requisite = q2
    qr.save()

    # requereixen 360
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Orientació - Entrenament tecnològic')
    qr.requisite = q3
    qr.save()
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Orientació - Entrenament entomològic')
    qr.requisite = q3
    qr.save()

    # requereixen 362
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Acció - Pregunta Investigable (continguts)')
    qr.requisite = q4
    qr.save()
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Aprenentatge pràctic - Recol·lecció de dades amb l\'App')
    qr.requisite = q4
    qr.save()

    # requereixen 364
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Acció - Dissenyant la pregunta investigable')
    qr.requisite = q5
    qr.save()

    # requereixen 365
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Conclusió - Enquesta final/ Autoavaluació alumnat')
    qr.requisite = q6
    qr.save()
    qr = Quiz.objects.get(campaign__name='BCN 25/26 BATX', name='Conclusió - Pòster Científic')
    qr.requisite = q6
    qr.save()

def requisites_c5():
    # 'BCN 25/26 ESO'
    # requisits
    q1 = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Enquesta inicial - Professorat') #331
    q2 = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Enquesta inicial alumnes')  # 334
    q3 = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Introducció')  # 336
    q4 = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Orientació - Entrenament tecnològic')  # 337
    q5 = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Aprenentatge pràctic - Preparació del safari')  # 338

    # requereixen 331
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Enquesta final - Professorat')
    qr.requisite = q1
    qr.save()

    # requereixen 334
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Introducció')
    qr.requisite = q2
    qr.save()

    # requereixen 336
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Orientació - Entrenament tecnològic')
    qr.requisite = q3
    qr.save()
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Orientació - Entrenament entomològic')
    qr.requisite = q3
    qr.save()
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Aprenentatge pràctic - Laboratori')
    qr.requisite = q3
    qr.save()

    # requereixen 337
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Aprenentatge pràctic - Preparació del safari')
    qr.requisite = q4
    qr.save()
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Com fer una bona campanya de comunicació')
    qr.requisite = q4
    qr.save()

    # requereixen 338
    qr = Quiz.objects.get(campaign__name='BCN 25/26 ESO', name='Aprenentatge pràctic - Safari')
    qr.requisite = q5
    qr.save()


def set_requisites():
    requisites_c1()
    requisites_c2()
    requisites_c3()
    requisites_c4()
    requisites_c5()

def set_current_active_campaign():
    c = Campaign.objects.get(name='FECYT 25/26 ESO')
    c.active = True
    c.save()

def main():
    with transaction.atomic():
        delete_users()
        create_campaigns()
        transfer_tests()
        delete_other_campaigns()
        delete_orphan_centers()
        #add_csv_data()
        rename_new_tests()
        set_requisites()
        set_current_active_campaign()


if __name__ == '__main__':
    main()
