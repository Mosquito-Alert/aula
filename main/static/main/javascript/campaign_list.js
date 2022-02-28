$(document).ready( function () {

    var table = $('#campaign_list').DataTable( {
        'ajax': {
            'url': _campaign_list_url,
            'dataType': 'json'
        },
        'serverSide': true,
        'processing': true,
        'language': table_language,
        'pageLength': 25,
        'pagingType': 'full_numbers',
        'bLengthChange': false,
        'responsive': true,
        'order': [[ 0, "desc" ]],
        stateSave: true,
        'dom': '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) );
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) );
        },
        'columns': [
            { 'data': 'name' }
            ,{ 'data': 'start_date' }
            ,{ 'data': 'end_date' }
            ,{ 'data': 'active' }
        ],
        'columnDefs': [
            {
                'title': gettext('Campanya activa'),
                'targets': 3,
                'data': 'active',
                'sortable': false,
                "render": function(value){
                    var retVal = "";
                    if(value){
                        retVal += '<input type="checkbox" class="active_chk" checked/>';
                    }else{
                        retVal += '<input type="checkbox" class="active_chk"/>';
                    }
                    return retVal;
                },
            },
            {
                'targets': 4,
                'sortable': false,
                'render': function(value){
                    return '<button title="' + gettext('Editar') + '" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            },
            {
                'targets':0,
                'title': gettext('Nom de la campanya')
            },
            {
                'targets':1,
                'title': gettext('Data inici'),
            },
            {
                'targets':2,
                'title': gettext('Data fi')
            }
        ]
    } );

    $('#campaign_list tbody').on('click', 'td input.active_chk', function (e) {
        var checked = $(this).is(":checked");
        e.preventDefault();
        if(checked){
            if(confirm(gettext('La campanya que has clicat s\'establirà com a activa. Segur que vols continuar?'))){
                var tr = $(this).closest('tr');
                var row = table.row( tr );
                var id = row.data().id
                toggle_active(id);
            }
        }
    });

    $('#campaign_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        window.location.href = _campaign_update_url + id + '/';
    });

    var toggle_active = function(campaign_id){
        $.ajax({
            url: _toggle_active,
            data: 'id=' + encodeURI(campaign_id),
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                table.ajax.reload(null,false);
            },
            error: function(jqXHR, textStatus, errorThrown){
                table.ajax.reload(null,false);
            }
        });
    }

});
