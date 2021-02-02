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
            { 'data': 'name' },
            { 'data': 'author.username' },
            { 'data': 'education_center' },
            { 'data': 'requisite' },
            { 'data': 'published' }
        ],
        'columnDefs': [
            {
                'targets':0,
                'title': 'Nom de la prova'
            },
            {
                'targets':1,
                'title': 'Autor',
                'render': function(value){
                    if(value){
                        return value;
                    }else{
                        return 'Anònim';
                    }
                }
            },
            {
                'targets':2,
                'title': 'Centre'
            },
            {
                'targets':3,
                'title': 'Requisits',
                'render': function(value){
                    if(value){
                        return value.name;
                    }else{
                        return '';
                    }
                }
            },
            {
            'targets':4,
            'title': 'Prova publicada?',
            'render': function(value){
                    if(value == true){
                        return '<p><i class="fas fa-check"></i></p>';
                    }else{
                        return '<p><i class="fas fa-times"></i></p>';
                    }
                }
            },
            {
                'targets': 5,
                'sortable': false,
                'render': function(value){
                    return '<button title="Editar" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            },
            {
                'targets': 6,
                'sortable': false,
                'render': function(value){
                    return '<button title="Eliminar prova" class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
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
            toastr.success('Prova eliminada!');
            table.ajax.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error('Error eliminant prova');
        }
        });
    };

    var confirmDialog = function(message,id){
    $('<div></div>').appendTo('body')
        .html('<div><h6>'+message+'</h6></div>')
        .dialog({
            modal: true, title: 'Eliminant prova...', zIndex: 10000, autoOpen: true,
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
            toastr.warning('Ho sentim, no es permet la edició de proves ja publicades.')
        }else{
            window.location.href = _quiz_update_url + id + '/';
        }
    });

    $('#quiz_list tbody').on('click', 'td button.delete_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        confirmDialog("Segur que vols esborrar la prova?",id);
    });

});