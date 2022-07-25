import app_config

from main.models import Awards, EducationCenter
from django.contrib.auth.models import User
import csv

WORKING_DIR = app_config.proj_path + '/util_scripts/'


def load_awards_data(overwrite=False):
    if overwrite:
        Awards.objects.all().delete()
    awards = []
    with open(f"{WORKING_DIR}premis.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(csv_reader)
        for row in csv_reader:
            if(row[4] != ''):
                user = User.objects.get(pk=row[4])
                center_string = user.profile.center_string
                campaign = user.profile.campaign
                ec = EducationCenter.objects.filter(name=center_string).filter(campaign=campaign).first()
                a = Awards(
                    age_bracket = row[0],
                    format = row[1],
                    award = row[2],
                    group = user,
                    center = ec
                )
                awards.append(a)
    Awards.objects.bulk_create(awards)


def main():
    load_awards_data(overwrite=True)


if __name__ == '__main__':
    main()
