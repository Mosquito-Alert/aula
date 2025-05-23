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
        'order': [[ 1, "desc" ]],
        stateSave: true,
        'dom': '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) );
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) );
        },
        'columns': [
            { 'data': 'name' },
            { 'data': 'seq' },
            { 'data': 'author.username' },
            { 'data': 'education_center' },
            { 'data': 'requisite' },
            { 'data': 'published' },
            { 'data': 'type_text' },
            { 'data': 'quiz_browse_url' },
        ],
        'columnDefs': [
            {
                'targets':0,
                'title': gettext('Nom de la prova')
            },
            {
                'targets':1,
                'title': gettext('Ordre')
            },
            {
                'targets':2,
                'title': gettext('Autor'),
                'render': function(value){
                    if(value){
                        return value;
                    }else{
                        return gettext('Anònim');
                    }
                }
            },
            {
                'targets':3,
                'title': gettext('Centre')
            },
            {
                'targets':4,
                'title': gettext('Requisits'),
                'render': function(value){
                    if(value){
                        return value.name;
                    }else{
                        return '';
                    }
                }
            },
            {
            'targets':5,
            'title': gettext('Prova publicada?'),
            'render': function(value){
                    if(value == true){
                        return '<p><i class="fas fa-check"></i></p>';
                    }else{
                        return '<p><i class="fas fa-times"></i></p>';
                    }
                }
            },
            {
            'targets':6,
            'title': gettext('Tipus prova')
            },
            {
            'targets':7,
            'sortable': false,
            'title': gettext('Enllaç a la prova'),
            'render': function(value){
                    return '<a target="_blank" href="' + protocol + host + value + '">link</a>';
                }
            },
            {
                'targets': 8,
                'sortable': false,
                'render': function(value){
                    if(admin_edit){
                        return '<button title="' + gettext('Editar') + '" class="edit_button btn btn-info"><i class="fa-solid fa-pencil" aria-hidden="true"></i></button>';
                    }else{
                        return '<button title="' + gettext('View') + '" class="detail_button btn btn-info"><i class="far fa-eye" aria-hidden="true"></i></button>';
                    }
                }
            },
            {
                'targets': 9,
                'sortable': false,
                'render': function(value){
                    if(admin_edit){
                        return '<button title="' + gettext('Eliminar prova') + '" class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
                    }else{
                        return '';
                    }
                }
            },
        ]
    } );

    var delete_quiz = function(id){
    $.ajax({
        url: _quiz_delete_url + id,
        method: 'DELETE',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        success: function( data, textStatus, jqXHR ) {
            toastr.success(gettext('Prova eliminada!'));
            table.ajax.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error(gettext('Error eliminant prova'));
        }
        });
    };

    var confirmDialog = function(message,id){
    $('<div></div>').appendTo('body')
        .html('<div><h6>'+message+'</h6></div>')
        .dialog({
            modal: true, title: gettext('Eliminant prova...'), zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    delete_quiz(id);
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

    $('#quiz_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        var published = row.data().published;
        if(!user_is_admin && published){
            toastr.options = {"positionClass": "toast-top-full-width","preventDuplicates": true};
            toastr.warning(gettext('Ho sentim, no es permet la edició de proves ja publicades.'));
        }else{
            window.location.href = _quiz_update_url + id + '/';
        }
    });

    $('#quiz_list tbody').on('click', 'td button.detail_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        var published = row.data().published;
        window.open(_quiz_browse_url + id, '_blank').focus();
    });

    $('#quiz_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        confirmDialog(gettext("Segur que vols esborrar la prova?"),id);
    });

});
