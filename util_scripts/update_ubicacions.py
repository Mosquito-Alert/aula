import app_config

from main.models import EducationCenter
import csv
from csv import reader
import sys
from django.contrib.gis.geos import GEOSGeometry
WORKING_DIR = app_config.proj_path + '/util_scripts/'


def update_locations(filename):
    with open(f"{WORKING_DIR}{filename}",encoding='ISO-8859-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(csv_reader)
        for row in csv_reader:
            print("Updating geom for center {0}".format( row[1] ))
            wkt_point = "POINT ({0} {1})".format(row[2], row[3])
            point = GEOSGeometry(wkt_point)
            center = EducationCenter.objects.get(pk=(int(row[0])))
            center.location = point
            center.save()
            print("Center updated")


def main():
    args = sys.argv[1:]
    filename = args[0]
    update_locations(filename)


if __name__ == '__main__':
    main()
