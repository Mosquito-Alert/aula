import app_config

from main.models import Profile, EducationCenter, Campaign
import csv
import string
import random
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
from django.contrib.gis.geos import GEOSGeometry
import csv


USERS_FILE = app_config.proj_path + '/util_scripts/docents_2022.csv'
#USERS_FILE = app_config.proj_path + '/util_scripts/test_profe.csv'
OUT_FILE = app_config.proj_path + '/util_scripts/teachers_out.csv'


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


def create_users(campaign):
    new_rows = []
    with open(USERS_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            center_name = row[0]
            original_teacher_name = clean_teacher_name(row[3])
            center = None
            try:
                center = EducationCenter.objects.get(name=center_name, campaign=campaign)
                print("Center does exist")
            except EducationCenter.DoesNotExist:
                location = GEOSGeometry('POINT (0 0)', srid=4326)
                center = EducationCenter(name=center_name, location=location, campaign=campaign)
                center.save()
                print("Center does not exist")

            password = generate_password()
            try:
                teacher_name = original_teacher_name
                teacher_user = User.objects.create_user(username=teacher_name, password=password)
            except IntegrityError:
                alternate_name = give_alternate_teacher_name(teacher_name)
                teacher_name = alternate_name
                teacher_user = User.objects.create_user(username=alternate_name, password=password)

            teacher_user.save()
            teacher_user.profile.is_teacher = True
            teacher_user.profile.teacher_belongs_to = center
            teacher_user.profile.campaign = campaign
            teacher_user.save()

            new_rows.append(row + [ teacher_name, password ])
            print(generate_password())

    with open(OUT_FILE, mode='w') as teacher_file:
        teacher_writer = csv.writer(teacher_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        teacher_writer.writerow(['Nombre del centro','Curso','Nombre y apellidos del docente','Correo electrónico del docente','Teléfono de contacto del docente','username','password'])
        for row in new_rows:
            teacher_writer.writerow(row)


def delete_users(campaign):
    User.objects.filter(profile__campaign=campaign).delete()


if __name__ == '__main__':
    campaign = Campaign.objects.get(pk=2)
    create_users( campaign )
    #delete_users( campaign )
