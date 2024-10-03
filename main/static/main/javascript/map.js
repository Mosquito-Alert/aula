var bar;
var selected_marker;
var default_bounds;
var breeding_site_markers_layer;
var marker_cluster_layer;

$(document).ready(function() {

    var layer_to_label = {
        "storm_drain_dry": 'Imbornal seco',
        "storm_drain_water": 'Imbornal con agua',
        "breeding_site_other": 'Otro tipo de punto de cría'
    };

    var base = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
    });

    var baseLayers = {
		"Open street map": base
	};

	var adjust_ui = function(){
	    if( current_year == 0 ){
	        $('#year_list').val("");
	    }else{
	        $('#year_list').val(current_year);
	    }
	}

	var get_popup_text = function( this_bs ){
	    return '<div class="card">' +
          '<div class="card-image">' +
            '<figure class="image is-4by3">' +
              '<img width="600" style="background-color: #FFA07A; padding: 2px;" src="' + this_bs.photo_url + '" alt="Placeholder image">' +
            '</figure>' +
          '</div>' +
          '<div class="card-content">' +
            '<div class="content">' +
                '<p><b>Tipo:</b> ' + layer_to_label[this_bs.private_webmap_layer] + '</p>' +
                '<p><b>Fecha de observación:</b> ' + this_bs.observation_date + '</p>' +
                '<p><b>Observaciones del alumno:</b> ' + this_bs.note + '</p>' +
            '</div>' +
          '</div>' +
        '</div>';
	}

	var show_breeding_sites_for_hash = function(hashtag){
	    $.ajax({
            url: '/api/center_bs/' + hashtag + '/',
            method: "GET",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                var bounds = L.latLngBounds();
                var breeding_site_markers = [];
                marker_cluster_layer = L.markerClusterGroup();
                for(var i=0; i<data.length; i++){
                    var this_bs = data[i];
                    var marker;
                    if( this_bs.private_webmap_layer == 'storm_drain_dry' ){
                        marker = new myMarker([this_bs.lat, this_bs.lon],{icon:sd_dry_icon, id: this_bs.id, hashtag: this_bs.hashtag});
                    }else if( this_bs.private_webmap_layer == 'storm_drain_water' ){
                        marker = new myMarker([this_bs.lat, this_bs.lon],{icon:sd_water_icon, id: this_bs.id, hashtag: this_bs.hashtag});
                    }else{
                        marker = new myMarker([this_bs.lat, this_bs.lon],{icon:sd_other_icon, id: this_bs.id, hashtag: this_bs.hashtag});
                    }
                    marker.bindPopup(get_popup_text(this_bs));
                    breeding_site_markers.push(marker);
                    bounds.extend( [ this_bs.lat, this_bs.lon] );
                    marker_cluster_layer.addLayer(marker);
                }
                map.addLayer(marker_cluster_layer);
                map.fitBounds(bounds, {"animate":true,"pan": {"duration": 1}});
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(errorThrown);
            }
        });
	    /*
	    var breeding_sites_by_hash = _bs_data[hashtag];
	    var bounds = L.latLngBounds();
        var breeding_site_markers = [];
        marker_cluster_layer = L.markerClusterGroup();
        if(breeding_sites_by_hash){
            for(var i=0; i<breeding_sites_by_hash.length; i++){
                var this_bs = breeding_sites_by_hash[i];
                //var marker = new myMarker([ec.pos_x, ec.pos_y],{icon:full_school_icon, id: ec.id, hashtag: ec.hashtag});
                var marker;
                if( this_bs.private_webmap_layer == 'storm_drain_dry' ){
                    marker = new myMarker([this_bs.lat, this_bs.lon],{icon:sd_dry_icon, id: this_bs.id, hashtag: this_bs.hashtag});
                }else if( this_bs.private_webmap_layer == 'storm_drain_water' ){
                    marker = new myMarker([this_bs.lat, this_bs.lon],{icon:sd_water_icon, id: this_bs.id, hashtag: this_bs.hashtag});
                }else{
                    marker = new myMarker([this_bs.lat, this_bs.lon],{icon:sd_other_icon, id: this_bs.id, hashtag: this_bs.hashtag});
                }
                marker.bindPopup(get_popup_text(this_bs));
                //var marker = L.marker([ this_bs.lat, this_bs.lon] );
                breeding_site_markers.push(marker);
                bounds.extend( [ this_bs.lat, this_bs.lon] );
                marker_cluster_layer.addLayer(marker);
            }
            //breeding_site_markers_layer = L.layerGroup(breeding_site_markers);
            //map.addLayer(breeding_site_markers_layer);
            map.addLayer(marker_cluster_layer);
            map.fitBounds(bounds, {
                "animate":true,
                "pan": {
                    "duration": 1
                }
            });
        }*/
	}

	var get_center_info = function(center_id, sidebar){
        $.ajax({
            url: center_info_url + center_id + '/',
            method: "GET",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                var newDiv = document.createElement("div");
                newDiv.className = "leaflet-sidebar-pane";
                var header = document.createElement("h1");
                header.className = "leaflet-sidebar-header";
                newDiv.appendChild(header);
                header.innerHTML = '<span class="leaflet-sidebar-close"><i class="fa fa-times"></i></span>';
                var bulmaDiv = document.createElement("div");
                bulmaDiv.innerHTML = data.html;
                newDiv.appendChild(bulmaDiv);
                var panelContent = {
                    id: 'content',                     // UID, used to access the panel
                    tab: '',  // content can be passed as HTML string,
                    pane: newDiv,            // DOM elements can be passed, too
                    title: 'Info ',     // an optional pane header
                    position: 'top'                     // optional vertical alignment, defaults to 'top'
                };
                sidebar.addPanel(panelContent);
                sidebar.open('content');
            },
            error: function(jqXHR, textStatus, errorThrown){
                console.log(errorThrown);
            }
        });
    }

    var map = L.map('map', {
        center: [40.0000000, -4.0000000],
        zoom: 6,
        layers: [base]
    });

    var sd_water_icon = L.icon({
        iconUrl: _sd_water_icon_url,
        iconAnchor:     [17, 20],
        iconSize:     [25, 41]
    });

    var sd_dry_icon = L.icon({
        iconUrl: _sd_dry_icon_url,
        iconAnchor:     [17, 20],
        iconSize:     [25, 41]
    });

    var sd_other_icon = L.icon({
        iconUrl: _sd_other_icon_url,
        iconAnchor:     [17, 20],
        iconSize:     [25, 41]
    });

    var school_icon = L.icon({
        iconUrl: _school_icon_url,
        iconAnchor:     [27, 80],
        iconSize:     [55, 80]
    });

    var school_icon_laureate = L.icon({
        iconUrl: _laureate_school_icon_url,
        iconAnchor:     [35, 80],
        iconSize:     [70, 80]
    });

    var full_school_icon = L.icon({
        iconUrl: _full_school_icon_url,
        iconAnchor:     [27, 80],
        iconSize:     [55, 80]
    });

    var layer_data = [];
    var bs_data = [];

    var myMarker = L.Marker.extend( { options:{ id: 'default_id' } });

    if(default_bounds==null){
        default_bounds = L.latLngBounds();
    }
    for(var i = 0; i < _center_data.length; i++){
        var ec = _center_data[i];
        var m;
        if( ec.has_awards == true ){
            m = new myMarker([ec.lat, ec.lon],{icon:school_icon_laureate, id: ec.id, hashtag: ec.hashtag});
        }else{
            m = new myMarker([ec.lat, ec.lon],{icon:school_icon, id: ec.id, hashtag: ec.hashtag});
        }
        default_bounds.extend( [ec.lat, ec.lon] );
        m.on('click', function(e){
            if(bar){
                bar.close();
            }
            map.setView(e.latlng, 14, {
                    "animate":true,
                    "pan": {
                        "duration": 1
                    }
                }
            );
            bar = L.control.sidebar({ container: 'sidebar', position: 'right', }).addTo(map);
            bar.on('closing',function(e){
                if(marker_cluster_layer){
                    map.removeLayer(marker_cluster_layer);
                }
            });
            var layer = e.target;
            selected_marker = e.target;
            var ec_id = e.target.options.id;
            var hashtag = e.target.options.hashtag;
            get_center_info(ec_id, bar);
            show_breeding_sites_for_hash(hashtag.substring(1));
        });
        layer_data.push(m);
    }
    ec_markers = L.layerGroup(layer_data);
    map.addLayer(ec_markers);
    map.fitBounds(default_bounds, {
        "animate":true,
        "pan": {
            "duration": 1
        }
    });

    $('#year_list').change(function() {
        var selected_value =  $(this).val();
        if(selected_value==''){
            window.open(map_url,"_self")
        }else{
            window.open(map_url + selected_value + "/","_self")
        }
    });

    L.Control.Watermark = L.Control.extend({
        options:{
            url: '',
            img_width: '300px'
        },
        onAdd: function(map) {
            var img = L.DomUtil.create('img');
            //img.src = '/static/main/icons/mcin-fecyt-web.png';
            img.src = this.options.url;
            img.style.width = this.options.img_width;
            //console.log(this.url);
            return img;
        },
        onRemove: function(map) {
            // Nothing to do here
        }
    });

    L.control.watermark = function(opts) {
        return new L.Control.Watermark(opts);
    }

    L.control.watermark({ position: 'bottomleft', url: '/static/main/icons/one_health_pact.jpg', img_width: '100px' }).addTo(map)
    L.control.watermark({ position: 'bottomleft', url: '/static/main/icons/logo_ASPB.svg', img_width: '150px' }).addTo(map)
    L.control.watermark({ position: 'bottomleft', url: '/static/main/icons/mcin-fecyt-web.png', img_width: '420px' }).addTo(map)

    adjust_ui();
});
