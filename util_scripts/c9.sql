copy (select * from (select *,'#idp23' from map_aux_reports where note ilike '%#idp23%' UNION select *,'#iel23' from map_aux_reports where note ilike '%#iel23%' UNION select *,'#ijda23' from map_aux_reports where note ilike '%#ijda23%' UNION select *,'#ila23' from map_aux_reports where note ilike '%#ila23%' UNION select *,'#ime23' from map_aux_reports where note ilike '%#ime23%' UNION select *,'#inm23' from map_aux_reports where note ilike '%#inm23%' UNION select *,'#itp23' from map_aux_reports where note ilike '%#itp23%') as foo where foo.private_webmap_layer in ('breeding_site_other', 'storm_drain_dry', 'storm_drain_water')) to '/tmp/c9_data.csv' CSV HEADER;