import app_config

from main.models import Profile, EducationCenter, Campaign, Awards
from main.views import get_center_bs_sites_count, get_center_bs_sites, get_center_awards, get_participation_years, get_number_of_points_center
import csv
import string
import random
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
from django.contrib.gis.geos import GEOSGeometry
import csv
import datetime
from django.db import transaction

OUT_FILE_CENTERS = app_config.proj_path + '/util_scripts/static_center_map_data_2025.csv'
OUT_FILE_AWARDS = app_config.proj_path + '/util_scripts/static_award_map_data_2025.csv'

def dump_center_data():
    with open(OUT_FILE_CENTERS, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['education_center', 'lat', 'lon', 'year', 'participation_years', 'hashtag','n_pupils','n_groups','n_bs_total','n_storm_drain_water','n_storm_drain_dry','n_other_bs', 'has_awards'])
        for year in [2025]:
            campaigns_year = Campaign.objects.filter(end_date__year=year)
            centers = EducationCenter.objects.filter(campaign__in=campaigns_year).exclude(location__isnull=True)
            count_data = get_center_bs_sites_count()
            bs = get_center_bs_sites(campaigns_year)
            awards = get_center_awards()
            for c in centers:
                has_awards = awards.get(c.hashtag,False)
                participation_years = get_participation_years(c)
                n_points_data = get_number_of_points_center(c)
                n_groups = c.n_groups_center()
                if n_groups > 0 and c.hashtag is not None and c.hashtag != '':
                    writer.writerow([ c.name, c.location.y, c.location.x, year, participation_years, c.hashtag, c.n_students_center(), n_groups, n_points_data['total'], n_points_data['sd_water'], n_points_data['sd_dry'],n_points_data['sd_other'], has_awards ])
                    #print("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}".format( c.name, c.location.y, c.location.x, year, participation_years, c.hashtag, c.n_students_center(), n_groups, n_points_data['total'], n_points_data['sd_water'], n_points_data['sd_dry'],n_points_data['sd_other'], has_awards ))

def dump_award_data():
    with open(OUT_FILE_AWARDS, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['age_bracket', 'format', 'award', 'center_hashtag', 'center_name', 'group_hashtag', 'group_name'])
        awards = Awards.objects.all()
        for a in awards:
            writer.writerow([a.age_bracket, a.format, a.award, a.center.hashtag, a.center.name, a.group.profile.group_hashtag, a.group.profile.group_public_name])

if __name__ == '__main__':
    dump_center_data()
    dump_award_data()
