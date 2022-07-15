var bar;
var selected_marker;
var default_bounds;

$(document).ready(function() {

    var base = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
    });

    var baseLayers = {
		"Open street map": base
	};

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

    var school_icon = L.icon({
        iconUrl: _school_icon_url,
        iconAnchor:     [27, 80],
        iconSize:     [55, 80]
    })

    var selected_school_icon = L.icon({
        iconUrl: _selected_school_icon_url,
        iconAnchor:     [27, 80],
        iconSize:     [55, 80]
    })

    var layer_data = [];

    var myMarker = L.Marker.extend( { options:{ id: 'default_id' } });

    if(default_bounds==null){
        default_bounds = L.latLngBounds();
    }
    for(var i = 0; i < _center_data.length; i++){
        var ec = _center_data[i];
        var m = new myMarker([ec.pos_x, ec.pos_y],{icon:school_icon, id: ec.id});
        default_bounds.extend( [ec.pos_x, ec.pos_y] );
        m.on('click', function(e){
            var ec_id = e.target.options.id;
            if(bar){
                bar.close();
                selected_marker.setIcon(school_icon);
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
                if(selected_marker){
                    selected_marker.setIcon(school_icon);
                    map.fitBounds(default_bounds);
                }
            });
            if(selected_marker){
                selected_marker.setIcon(school_icon);
            }
            var layer = e.target;
            e.target.setIcon(selected_school_icon);
            selected_marker = e.target;
            get_center_info(ec_id, bar);
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

});
