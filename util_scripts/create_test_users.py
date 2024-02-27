import app_config

from main.models import EducationCenter, Campaign
from django.db.utils import IntegrityError
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.models import User
import string
import random
import csv
import datetime
from django.db import transaction
from slugify import slugify

USERS_FILE = app_config.proj_path + '/util_scripts/profes_test_2024_workshop_4.csv'
OUT_FILE = app_config.proj_path + '/util_scripts/profes_test_2024_4 _out.csv'

def clean_teacher_name(original_name):
    return original_name.split('@')[0].lower()

def generate_password( size=8, chars= string.ascii_uppercase + string.ascii_lowercase + string.digits ):
    return ''.join(random.choice(chars) for _ in range(size))

def create_users():
    with transaction.atomic():
        new_rows = []
        current_year = datetime.date.today().year
        last_year = current_year - 1
        last_year_str = str(last_year)
        with open(USERS_FILE) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                campaign_name = row[4]
                campaign = None
                try:
                    campaign = Campaign.objects.get(name=campaign_name)
                except Campaign.DoesNotExist:
                    print("Campaign with name {0} does not exist".format( campaign_name ))
                center_name = row[0]
                original_teacher_name = clean_teacher_name(row[1])
                center = None
                try:
                    center = EducationCenter.objects.get(name=center_name, campaign=campaign)
                    print("Center {0} {1} does exist".format(center_name, campaign.name))
                except EducationCenter.DoesNotExist:
                    print("Creating center {0}".format(center_name))
                    location = GEOSGeometry('POINT (0 0)', srid=4326)
                    center = EducationCenter(name=center_name, location=location, campaign=campaign)
                    if center_name == 'Eskibel':
                        if campaign.id == 7:
                            center.hashtag = '#' + slugify(center_name) + "eso"
                        elif campaign.id == 8:
                            center.hashtag = '#' + slugify(center_name) + "pri"
                    elif center_name == 'IES Carpetania':
                        if campaign.id == 7:
                            center.hashtag = '#' + slugify(center_name) + "eso"
                        elif campaign.id == 6:
                            center.hashtag = '#' + slugify(center_name) + "bac"
                    elif center_name == 'CIFP A Carballeira':
                        if campaign.id == 7:
                            center.hashtag = '#eso' + center.center_slug()
                        elif campaign.id == 6:
                            center.hashtag = '#bac' + center.center_slug()
                    elif center_name == 'IES ALFONSO VI':
                        center.hashtag = '#bac' + center.center_slug()
                    elif center_name == 'Colegio Asunción Cuestablanca':
                        center.hashtag = '#bacc' + center.center_slug()
                    elif center_name == 'Eckartcollege':
                        center.hashtag = '#eckart24'
                    else:
                        center.hashtag = center.center_slug()
                    center.save()
                    print("{0} created".format(center_name))

                password = generate_password()
                if User.objects.filter(username=original_teacher_name).exists():
                    the_user = User.objects.get(username=original_teacher_name)
                    if the_user.profile.teacher_password is None or the_user.profile.teacher_password == '':
                        the_user.profile.teacher_password = password
                        the_user.profile.save()
                        the_user.set_password(password)
                        the_user.save()
                    new_rows.append(row + [original_teacher_name, the_user.profile.teacher_password])
                else:
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

if __name__ == '__main__':
    create_users()
