copy (select * from (select *,'#bc23' from map_aux_reports where note ilike '%#bc23%' UNION select *,'#c23' from map_aux_reports where note ilike '%#c23%' UNION select *,'#cl23' from map_aux_reports where note ilike '%#cl23%' UNION select *,'#doc23' from map_aux_reports where note ilike '%#doc23%' UNION select *,'#el23' from map_aux_reports where note ilike '%#el23%' UNION select *,'#ghc23' from map_aux_reports where note ilike '%#ghc23%' UNION select *,'#h23' from map_aux_reports where note ilike '%#h23%' UNION select *,'#hd23' from map_aux_reports where note ilike '%#hd23%' UNION select *,'#ja23' from map_aux_reports where note ilike '%#ja23%' UNION select *,'#jfc23' from map_aux_reports where note ilike '%#jfc23%' UNION select *,'#ll23' from map_aux_reports where note ilike '%#ll23%' UNION select *,'#m23' from map_aux_reports where note ilike '%#m23%' UNION select *,'#mcbp23' from map_aux_reports where note ilike '%#mcbp23%' UNION select *,'#mch23' from map_aux_reports where note ilike '%#mch23%' UNION select *,'#mml23' from map_aux_reports where note ilike '%#mml23%' UNION select *,'#s23' from map_aux_reports where note ilike '%#s23%' UNION select *,'#sdc23' from map_aux_reports where note ilike '%#sdc23%' UNION select *,'#tc23' from map_aux_reports where note ilike '%#tc23%') as foo where foo.private_webmap_layer in ('breeding_site_other', 'storm_drain_dry', 'storm_drain_water')) to '/tmp/c5_data.csv' CSV HEADER;