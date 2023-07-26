import app_config
import sys
import csv
from csv import reader

WORKING_DIR = app_config.proj_path + '/util_scripts/'

'''
reads a csv file with two columns, campaign id and hashtag. This file is generated using the query

copy (
select
 me.campaign_id,
 me.hashtag
from
main_campaign mc,
main_educationcenter me
where me.campaign_id in (5,6,7,8,9) and me.campaign_id = mc.id order by 1,2
) to '/tmp/campaigns.csv' CSV;

reads that file, and creates a sql file for each campaign which contains a query that dumps all the breeding site data for the campaign
'''

main_query_template = "copy (select * from ({0}) as foo where foo.private_webmap_layer in ('breeding_site_other', 'storm_drain_dry', 'storm_drain_water')) to '/tmp/c{1}_data.csv' CSV HEADER;"
subquery_template = "select *,'{0}' from map_aux_reports where note ilike '%{1}%'"

def main():
    args = sys.argv[1:]
    filename = args[0]
    data = {}
    with open(filename, 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            campaign_id = row[0]
            hashtag = row[1]
            try:
                data[campaign_id]
            except KeyError:
                data[campaign_id] = []
            data[campaign_id].append(hashtag)
    #print(data)
    for key in data:
        subqueries_campaign = []
        for value in data[key]:
            subqueries_campaign.append( subquery_template.format(value,value) )
        subqueries_list = ' UNION '.join(subqueries_campaign)
        w_filename = WORKING_DIR + 'c{0}.sql'.format(key)
        f = open(w_filename, 'w')
        f.write( main_query_template.format(subqueries_list, key) )



if __name__ == '__main__':
    main()
