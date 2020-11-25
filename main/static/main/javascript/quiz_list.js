var colors = [
  ['#264653ff','#26b9ac00'],
  ['#2a9d8fff','#2a627000'],
  ['#e9c46aff','#e93b9500'],
  ['#f4a261ff','#f45d9e00'],
  ['#e76f51ff','#e790ae00']
];

$(document).ready( function () {

    var table = $('#quiz_list').DataTable( {
        'ajax': {
            'url': _quiz_list_url,
            'dataType': 'json'
        },
        'serverSide': true,
        'createdRow': function( row, data, dataIndex){
            if( data.is_active == false ){
                $(row).addClass('row-disabled');
            }
        },
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
        ],
        'columnDefs': [
            {
                'targets':0,
                'title': 'Nom de la prova'
            },
            {
                'targets': 1,
                'sortable': false,
                'render': function(value){
                    return '<button title="Editar" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            },
        ]
    } );

    $('#quiz_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        window.location.href = _quiz_update_url + id + '/';
    });

    $('#')

    /*
    var delete_group = function(id, to_state){
        $.ajax({
            url: '/user/update-partial/' + id + '/',
            data: {"is_active":to_state},
            method: 'PUT',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                if(data.is_active==false){
                    toastr.success('Grup desactivat!');
                }else{
                    toastr.success('Grup activat!');
                }
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error modificant grup');
            }
        });
    };

    var confirmDialog = function(message,id, to_state){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: 'Inactivant grup...', zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_group(id,to_state);
                        $(this).dialog("close");
                    },
                    No: function () {
                        $(this).dialog("close");
                    }
                },
                close: function (event, ui) {
                    $(this).remove();
                }
        });
    };

    var table = $('#group_list').DataTable( {
        'ajax': {
            'url': _group_list_url,
            'dataType': 'json'
        },
        'serverSide': true,
        'createdRow': function( row, data, dataIndex){
            if( data.is_active == false ){
                $(row).addClass('row-disabled');
            }
        },
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
            { 'data': 'username' }
            ,{ 'data': 'group_password' }
            ,{ 'data': 'group_public_name' }
            ,{ 'data': 'group_center' }
            ,{ 'data': 'group_alums' }
            ,{ 'data': 'group_picture' }
            ,{ 'data': 'is_active' }
        ],
        'columnDefs': [
            {
                'targets': 7,
                'data': 'is_active',
                'sortable': false,
                'render': function(value){
                    return '<button title="Desactivar usuari" class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
                }
            },
            {
                'targets': 8,
                'data': 'is_active',
                'sortable': false,
                'render': function(value){
                    return '<button title="Editar" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            },
            {
                'targets':0,
                'title': 'Nom usuari del grup'
            },
            {
                'targets':1,
                'title': 'Password'
            },
            {
                'targets':2,
                'title': 'Nom públic'
            },
            {
                'targets':3,
                'title': 'Centre'
            },
            {
                'targets':4,
                'title': 'Alumnes',
                'render': function(value){
                    if(value != null){
                        var alums = value.split(',');
                        var badges = [];
                        for(var i = 0; i < alums.length; i++){
                            var index = i % 5;
                            badges.push('<span style="color:white;background-color:' + colors[0][0] + ';" class="badge badge-pill">' + alums[i] + '</span>');
                        }
                        if(badges.length == 0){
                            return '';
                        }else{
                            return badges.join(' ');
                        }
                    }else{
                        return ''
                    }
                }
            },
            {
                'targets':5,
                'title': 'Imatge del grup',
                'render': function(value){
                    if(value != ''){
                        return '<img width="50px" src="' + value + '">';
                    }else{
                        return '<span width="50px"><i class="fas fa-ban"></i></span>'
                    }
                }
            },
            {
                'targets':6,
                'data': 'is_active',
                'title': 'Grup actiu?',
                'render': function(value){
                    if(value == true){
                        return '<p><i class="fas fa-check"></i></p>';
                    }else{
                        return '<p><i class="fas fa-times"></i></p>';
                    }
                }
            }
        ]
    } );

    $('#group_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        var active = row.data().is_active;
        if(active){
            confirmDialog("El grup està actiu i es marcarà com a inactiu. Segur que vols continuar?",id,false);
        }else{
            confirmDialog("El grup està inactiu i es marcarà com a actiu. Segur que vols continuar?",id,true);
        }
    });

    $('#group_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        window.location.href = _group_update_url + id + '/';
    });
    */
});