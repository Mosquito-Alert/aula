$(document).ready(function() {
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

    var editableLayers = new L.FeatureGroup();

	editableLayers.eachLayer(function(layer) {
        layer.on('click', function(){
            alert(this._leaflet_id);
        });
    });

    var draw_options = {
      position: 'topleft',
      draw: {
          polyline: false,
          polygon: false,
          circle: false,
          rectangle: false,
          marker: true,
          circlemarker: false
      },
      edit: {
          featureGroup: editableLayers,
          remove: true
      }
    };

    var drawControl = new L.Control.Draw(draw_options);
    map.addLayer(editableLayers);
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType,layer = e.layer;
        editableLayers.clearLayers();
        editableLayers.addLayer(layer);
        var string_json = JSON.stringify(editableLayers.toGeoJSON());
        $('#id_location').val(string_json);
        console.log(string_json);
    });

    map.on(L.Draw.Event.EDITED, function(e){
        var string_json = JSON.stringify(editableLayers.toGeoJSON());
        $('#id_location').val(string_json);
        console.log(string_json);
    });

    map.on(L.Draw.Event.DELETED, function(e){
        $('#id_location').val('');
        console.log("eliminado");
    });

    if(geom){
        var geometries_json = JSON.stringify(geom);
        $('#id_location').val(geometries_json);
        var geoJSONLayer = L.geoJson(geom);
        geoJSONLayer.eachLayer(
            function(l){
                editableLayers.addLayer(l);
            }
        );
    }

    $("#id_name").blur(function(evt){
        var hash = generate_hashtag();
        $('#id_hashtag').val(hash);
    });

    var generate_hashtag = function(){
        var nom = $('#id_name').val();
        if(nom.trim() != ''){
            var year = new Date().getFullYear() - 2000;
            var bits = nom.split(' ');
            var inicials = [];
            for(var i = 0; i < bits.length; i++){
                inicials.push(bits[i][0]);
            }
            return "#" + inicials.join("") + year;
        }
        return "";
    }

});
