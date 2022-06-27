var bar;

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

    var layer_data = [];
    for(var i = 0; i < _center_data.length; i++){
        var ec = _center_data[i];
        //var m = L.marker([ec.pos_x, ec.pos_y]).bindPopup(ec.name);
        var m = L.marker([ec.pos_x, ec.pos_y]);
        m.on('click', function(e){
            if(bar){
                bar.close();
            }
            map.setView(e.latlng, 10);
            bar = L.control.sidebar({ container: 'sidebar', position: 'right', }).addTo(map);

            var newDiv = document.createElement("div");
            newDiv.className = "leaflet-sidebar-pane";
            var header = document.createElement("h1");
            header.className = "leaflet-sidebar-header";
            newDiv.appendChild(header);
            header.innerHTML = '<span class="leaflet-sidebar-close"><i class="fa fa-times"></i></span>';
            var bulmaDiv = document.createElement("div");
            bulmaDiv.innerHTML =
                '<br>' +
                '<article class="panel is-link">' +
                  '<p class="panel-heading">' +
                    'Link' +
                  '</p>' +
                  '<p class="panel-tabs">' +
                    '<a class="is-active">All</a>' +
                    '<a>Public</a>' +
                    '<a>Private</a>' +
                    '<a>Sources</a>' +
                    '<a>Forks</a>' +
                  '</p>' +
                  '<div class="panel-block">' +
                    '<p class="control has-icons-left">' +
                      '<input class="input is-link" type="text" placeholder="Search">' +
                      '<span class="icon is-left">' +
                        '<i class="fas fa-search" aria-hidden="true"></i>' +
                      '</span>' +
                    '</p>' +
                  '</div>' +
                  '<a class="panel-block is-active">' +
                    '<span class="panel-icon">' +
                      '<i class="fas fa-book" aria-hidden="true"></i>' +
                    '</span>' +
                    'bulma' +
                  '</a>' +
                  '<a class="panel-block">' +
                    '<span class="panel-icon">' +
                      '<i class="fas fa-book" aria-hidden="true"></i>' +
                    '</span>' +
                    'marksheet' +
                  '</a>' +
                  '<a class="panel-block">' +
                    '<span class="panel-icon">' +
                      '<i class="fas fa-book" aria-hidden="true"></i>' +
                    '</span>' +
                    'minireset.css' +
                  '</a>' +
                  '<a class="panel-block">' +
                    '<span class="panel-icon">' +
                      '<i class="fas fa-book" aria-hidden="true"></i>' +
                    '</span>' +
                    'jgthms.github.io' +
                  '</a>' +
                '</article>';
            newDiv.appendChild(bulmaDiv);

            var panelContent = {
                id: 'content',                     // UID, used to access the panel
                //tab: '<i class="fa fa-info"></i>',  // content can be passed as HTML string,
                tab: '',  // content can be passed as HTML string,
                //pane: "Click "+ counter,            // DOM elements can be passed, too
                pane: newDiv,            // DOM elements can be passed, too
                title: 'Info ',     // an optional pane header
                position: 'top'                     // optional vertical alignment, defaults to 'top'
            };
            bar.addPanel(panelContent);
            bar.open('content');
        });
        layer_data.push(m);
    }
    ec_markers = L.layerGroup(layer_data);
    map.addLayer(ec_markers);

});
