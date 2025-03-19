import sys

import app_config

from main.models import Profile, EducationCenter, Campaign
import csv
import string
import random
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
from django.contrib.gis.geos import GEOSGeometry
import csv
import datetime
from django.db import transaction


#USERS_FILE = app_config.proj_path + '/util_scripts/docents_2022.csv'
USERS_FILE = app_config.proj_path + '/util_scripts/docents_2025_4.csv'
#USERS_FILE = app_config.proj_path + '/util_scripts/test_profe.csv'
OUT_FILE = app_config.proj_path + '/util_scripts/docents_2025_4_out.csv'

ALIAS_HASHES = {
    'Colegio Eskibel': {
        'FECYT 24/25 ESO':'#cee25',
        'FECYT 24/25 PRIMARIA':'#cep25',
        'FECYT 24/25 BATX':'#ceb25'
    },
    'INS Valldemossa': {
        'BCN 24/25 ESO':'#ive25'
    },
    'CPR Casa de la Virgen': {
        'FECYT 24/25 ESO':'#cve25',
        'FECYT 24/25 BATX':'#cvb25'
    },
    'Santa Magdalena Sofia': {
        'FECYT 24/25 PRIMARIA': '#smsp25',
        'FECYT 24/25 ESO': '#smse25',
        'FECYT 24/25 BATX': '#smsb25'
    },
    'IES ALONSO DE ERCILLA': {
        'FECYT 24/25 ESO':'#iade25',
        'FECYT 24/25 BATX':'#iadeb25'
    },
    'IES CERVANTES':{
        'FECYT 24/25 BATX': '#icb25'
    },
    'IES La Serranía':{
        'FECYT 24/25 ESO': '#ilse25',
        'FECYT 24/25 BATX': '#ilsb25'
    },
    'IES Ruiz Gijón':{
        'FECYT 24/25 ESO': '#irge25',
        'FECYT 24/25 BATX': '#irgb25'
    },
    'IES Azuer':{
        'FECYT 24/25 BATX': '#iazb25'
    }
}

def clean_teacher_name(original_name):
    return original_name.split('@')[0].lower()


def give_alternate_teacher_name(original_name):
    n_existing = User.objects.filter(username__startswith=original_name).count()
    return original_name + str(n_existing)


def generate_password( size=8, chars= string.ascii_uppercase + string.ascii_lowercase + string.digits ):
    return ''.join(random.choice(chars) for _ in range(size))


def remove_users():
    with open(USERS_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            teacher_name = clean_teacher_name(row[3])
            try:
                u = User.objects.get(username=teacher_name)
                u.delete()
                print("user {0} removed".format(teacher_name,))
            except User.DoesNotExist:
                print("user does not exist")


def create_users():
    new_rows = []
    current_year = datetime.date.today().year
    last_year = current_year - 1
    last_year_str = str(last_year)
    with open(USERS_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            campaign_name = row[4]
            try:
                campaign = Campaign.objects.get(name=campaign_name)
            except Campaign.DoesNotExist:
                print("Campaign with name {0} does not exist".format( campaign_name ))
            center_name = row[0]
            original_teacher_name = clean_teacher_name(row[1])
            center = None
            try:
                center = EducationCenter.objects.get(name=center_name, campaign=campaign)
                print("Center does exist")
            except EducationCenter.DoesNotExist:
                print("Center does not exist")
                location = GEOSGeometry('POINT (0 0)', srid=4326)
                center = EducationCenter(name=center_name, location=location, campaign=campaign)
                try:
                    center.hashtag = ALIAS_HASHES[center_name][campaign_name]
                except KeyError:
                    center.hashtag = center.center_slug()
                try:
                    center.save()
                except IntegrityError as ie:
                    print(ie)
                    print("Failed save for center {}".format(center_name))
                    sys.exit(1)

            password = generate_password()
            if User.objects.filter(username=original_teacher_name).exists():
                try:
                    old_user = User.objects.get(username=original_teacher_name)
                    old_user.username = old_user.username + '_' + last_year_str
                    old_user.save()
                except IntegrityError:
                    print("Can't rename user. Username {0} already exists, skipping...".format( old_user.username + '_' + last_year_str ))

            # try:
            #     teacher_name = original_teacher_name
            #     teacher_user = User.objects.create_user(username=teacher_name, password=password)
            # except IntegrityError:
            #     alternate_name = give_alternate_teacher_name(teacher_name)
            #     teacher_name = alternate_name
            #     teacher_user = User.objects.create_user(username=alternate_name, password=password)
            try:
                teacher_name = original_teacher_name
                teacher_user = User.objects.create_user(username=teacher_name, password=password)
                teacher_user.save()
                teacher_user.profile.is_teacher = True
                teacher_user.profile.teacher_belongs_to = center
                teacher_user.profile.campaign = campaign
                teacher_user.profile.teacher_password = password
                teacher_user.save()
                new_rows.append(row + [teacher_name, password])
                print(generate_password())
            except IntegrityError:
                print("Can't create user. Username {0} already exists, skipping...".format( teacher_name ))


    with open(OUT_FILE, mode='w') as teacher_file:
        teacher_writer = csv.writer(teacher_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # teacher_writer.writerow(['Nombre del centro','Curso','Nombre y apellidos del docente','Correo electrónico del docente','Teléfono de contacto del docente','username','password'])
        for row in new_rows:
            teacher_writer.writerow(row)


def delete_users(campaign):
    User.objects.filter(profile__campaign=campaign).delete()


if __name__ == '__main__':
    with transaction.atomic():
        # campaign = Campaign.objects.get(pk=5)
        create_users()
        #delete_users( campaign )
