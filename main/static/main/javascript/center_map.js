$(document).ready(function() {

    var default_bounds;

    var base = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
    });

    var baseLayers = {
		"Open street map": base
	};

	var map = L.map('map', {
        center: [40.0000000, -4.0000000],
        zoom: 6,
        layers: [base]
    });

    if(default_bounds==null){
        default_bounds = L.latLngBounds();
    }

    new L.Marker([57.666667, -2.64], {
    icon: new L.DivIcon({
        className: 'my-div-icon',
        html: '<span class="my-div-span">RAF Banff Airfield</span>'
        })
    });

    for(var i = 0; i < _center_data.length; i++){
        var ec = _center_data[i];
        default_bounds.extend( [ec.pos_x, ec.pos_y] );
        var marker = L.marker([ec.pos_x, ec.pos_y]).addTo(map);
        marker.bindPopup(
            '<p><h6>' + ec.name + '</h6></p>' +
            '<p>Hashtag: ' + ec.hashtag + '</p>' +
            '<p>' + gettext('N. grups')  + ': ' + ec.n_groups_in_center + '</p>' +
            '<p>' + gettext('N. alumnes')  + ': ' + ec.n_pupils_in_center + '</p>' +
            '<p><a href="/center/update/' + ec.id + '/" target="_blank">' + gettext('Editar') + '</a></p>'
        );
        /*var marker = new L.Marker([ec.pos_x, ec.pos_y], {icon: new L.DivIcon({className: 'my-div-icon',html: '<p><h5>' + ec.name + '</h5></p><p><a href="/center/update/' + ec.id + '/" target="_blank">' + gettext('Editar') + '</a></p>'})});
        marker.addTo(map);
        map.fitBounds(default_bounds, {
            "animate":true,
            "pan": {
            "duration": 1
            }
        });*/
    }
});
