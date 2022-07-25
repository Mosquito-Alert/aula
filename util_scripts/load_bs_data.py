import app_config

from main.models import BreedingSites, Campaign
import csv

WORKING_DIR = app_config.proj_path + '/util_scripts/'

hashtags = {
    '1': [
        '#cjdl21',
        '#ifa21',
        '#ic21',
        '#eb21',
        '#vdr21',
        '#ildv21',
        '#is21',
        '#ijaz21',
        '#igadh21',
        '#ieo21',
        '#iepp21',
        '#ia21',
        '#iac21',
        '#cb21',
        '#cemdls21',
        '#cmada21',
        '#st21',
        '#spa21',
        '#mr21',
        '#gdlr21',
        '#e21',
        '#cmm21',
        '#cli21',
        '#cdnsdlm21',
        '#ip21',
        '#icre22',
        '#im21'
    ],
    '2': [
        '#cepaa22',
        '#ct22',
        '#itp22',
        '#cnsdlm22',
        '#cgdlr22',
        '#cjdl22',
        '#cmm22',
        '#cii22',
        '#ei22',
        '#e22',
        '#ia22',
        '#icr22',
        '#ic22',
        '#ieo22',
        '#ijaz22',
        '#ildv22',
        '#is22',
        '#st22',
        '#vdr22',
        '#icn22',
        '#idds22',
        '#idc22',
        '#iln22',
        '#igm22',
        '#iedg22',
        '#isjdc22',
        '#ialm22',
        '#ccdm22',
        '#ice22',
        '#im22',
        '#cmada22',
        '#ijc22'
    ],
    '3': [
        '#ctt22',
        '#ijda22',
        '#idp22',
        '#ila22',
        '#ime22',
        '#inm22',
        '#iv22',
        '#iea22'
    ],
    '30': [
        '#St21',
        '#UC21',
        '#KKCA21',
        '#PL21'
    ]
}


def row_formatter(row):
    b = BreedingSites(
        version_uuid= row[1],
        observation_date= row[2],
        lon= row[3],
        lat= row[4],
        private_webmap_layer= row[23],
        photo_url= 'http://webserver.mosquitoalert.com' + row[15],
        note= row[22],
        center_hashtag=row[54]
    )
    return b


def load_campaign(id, pre_delete=False):
    if pre_delete:
        campaign_hashtags = hashtags[str(id)]
        BreedingSites.objects.filter(center_hashtag__in=campaign_hashtags).delete()
    breeding_sites = []
    campaign = Campaign.objects.get(pk=id)
    with open(f"{WORKING_DIR}c{id}_data.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(csv_reader)
        for row in csv_reader:
            breeding_site = row_formatter(row)
            breeding_site.campaign = campaign
            breeding_sites.append(breeding_site)
    BreedingSites.objects.bulk_create(breeding_sites)


def main():
    load_campaign(1, pre_delete=True)
    load_campaign(2, pre_delete=True)
    load_campaign(3, pre_delete=True)
    load_campaign(30, pre_delete=True)


if __name__ == '__main__':
    main()
