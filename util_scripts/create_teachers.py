import os, sys
import csv
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aula.settings")
proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proj_path)
os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from main.models import Profile, EducationCenter
import csv
import string
import random
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry
import csv


USERS_FILE = proj_path + '/util_scripts/profes_restants.csv'
OUT_FILE = proj_path + '/util_scripts/teachers_out.csv'

def clean_teacher_name(original_name):
    return original_name.split('@')[0].lower()


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
    with open(USERS_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            center_name = row[0]
            teacher_name = clean_teacher_name(row[3])
            center = None
            try:
                center = EducationCenter.objects.get(name=center_name)
                print("Center does exist")
            except EducationCenter.DoesNotExist:
                location = GEOSGeometry('POINT (0 0)', srid=4326)
                center = EducationCenter(name=center_name, location=location)
                center.save()
                print("Center does not exist")

            password = generate_password()
            #teacher_user = User(username=teacher_name, password=password)
            teacher_user = User.objects.create_user(username=teacher_name, password=password)
            teacher_user.save()
            teacher_user.profile.is_teacher = True
            teacher_user.profile.teacher_belongs_to = center
            teacher_user.save()

            new_rows.append(row + [ teacher_name, password ])
            print(generate_password())

    with open(OUT_FILE, mode='w') as teacher_file:
        teacher_writer = csv.writer(teacher_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        teacher_writer.writerow(['Marca de temps','Nombre del centro','Curso','Nombre y apellidos del docente','Correo electrónico del docente','Teléfono de contacto del docente','username','password'])
        for row in new_rows:
            teacher_writer.writerow(row)


create_users()
#remove_users()
