var colors = [
  ['#264653ff','#26b9ac00'],
  ['#2a9d8fff','#2a627000'],
  ['#e9c46aff','#e93b9500'],
  ['#f4a261ff','#f45d9e00'],
  ['#e76f51ff','#e790ae00']
];

$(document).ready( function () {

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
                    toastr.success(gettext('Grup desactivat!'));
                }else{
                    toastr.success(gettext('Grup activat!'));
                }
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error modificant grup'));
            }
        });
    };

    var confirmDialog = function(message,id, to_state){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: gettext('Inactivant grup...'), zIndex: 10000, autoOpen: true,
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
            ,{ 'data': 'group_tutor' }
            ,{ 'data': 'group_picture' }
            ,{ 'data': 'is_active' }
            ,{ 'data': 'group_n_students' }
            ,{ 'data': 'group_hashtag' }
        ],
        'columnDefs': [
            {
                'targets': 9,
                'data': 'is_active',
                'sortable': false,
                'render': function(value){
                    if(admin_edit){
                        return '<button title="' + gettext('Desactivar usuari') + '" class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
                    }else{
                        return '';
                    }
                }
            },
            {
                'targets': 10,
                'data': 'is_active',
                'sortable': false,
                'render': function(value){
                    if(admin_edit){
                        return '<button title="' + gettext('Editar') + '" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                    }else{
                        return '';
                    }
                }
            },
            {
                'targets':0,
                'title': gettext('Nom usuari del grup')
            },
            {
                'targets':1,
                'title': gettext('Password')
            },
            {
                'targets':2,
                'title': gettext('Nom públic')
            },
            {
                'targets':3,
                'title': gettext('Centre')
            },
            {
                'targets':4,
                'title': gettext('Tutor')
            },
            {
                'targets':5,
                'title': gettext('Imatge del grup'),
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
                'title': gettext('Grup actiu?'),
                'render': function(value){
                    if(value == true){
                        return '<p><i class="fas fa-check"></i></p>';
                    }else{
                        return '<p><i class="fas fa-times"></i></p>';
                    }
                }
            },
            {
                'targets':7,
                'title': gettext('N. alumnes')
            },
            {
                'targets':8,
                'title': gettext('Hashtag')
            }
        ]
    } );

    $('#group_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        var active = row.data().is_active;
        if(active){
            confirmDialog(gettext("El grup està actiu i es marcarà com a inactiu. Segur que vols continuar?"),id,false);
        }else{
            confirmDialog(gettext("El grup està inactiu i es marcarà com a actiu. Segur que vols continuar?"),id,true);
        }
    });

    $('#group_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        window.location.href = _group_update_url + id + '/';
    });


    $('#getPDFlist').on('click', function(){
        var params = table.ajax.params();
        window.location.href = _group_list_pdf + '?' + jQuery.param(params);

    });


});
