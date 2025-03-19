$(document).ready( function () {

var delete_teacher = function(id, to_state){
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
                toastr.success(gettext('Professor desactivat!'));
            }else{
                toastr.success(gettext('Professor activat!'));
            }
            table.ajax.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error(gettext('Error modificant professor'));
        }
    });
};

var confirmDialog = function(message,id, to_state){
    $('<div></div>').appendTo('body')
        .html('<div><h6>'+message+'</h6></div>')
        .dialog({
            modal: true, title: gettext('Inactivant professor...'), zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    delete_teacher(id,to_state);
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

var table = $('#teacher_list').DataTable( {
    'ajax': {
        'url': _teacher_list_url,
        'dataType': 'json'
    },
    'serverSide': true,
    'createdRow': function( row, data, dataIndex){
        if( data.active == false ){
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
        ,{ 'data': 'center' }
        ,{ 'data': 'password' }
        ,{ 'data': 'is_active' }
    ],
    'columnDefs': [
        {
            'targets': 4,
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
            'targets': 5,
            'data': 'is_active',
            'sortable': false,
            'render': function(value){
                if(admin_edit){
                    return '<button title="' + gettext('Editar') + '" class="edit_button btn btn-info"><i class="fa-solid fa-pencil" aria-hidden="true"></i></button>';
                }else{
                    return '';
                }
            }
        },
        {
            'targets': 6,
            'data': null,
            'sortable': false,
            'render': function(value){
                if(admin_edit){
                    return '<button title="' + gettext('Canviar password') + '" class="chgpsswd_button btn btn-danger"><i class="fa fa-asterisk"></i></button>';
                }else{
                    return '';
                }
            }
        },
        {
            'targets':0,
            'title': gettext('Nom usuari')
        },
        {
            'targets':1,
            'title': gettext('Centre')
        },
        {
            'targets':2,
            'title': gettext('Password')
        },
        {
            'targets':3,
            'title': gettext('Usuari actiu?'),
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

$('#teacher_list tbody').on('click', 'td button.delete_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id;
    var active = row.data().is_active;
    if(active){
        confirmDialog(gettext("El professor està actiu i es marcarà com a inactiu. Això vol dir que no es podrà loginar. Segur que vols continuar?"),id,false);
    }else{
        confirmDialog(gettext("El professor està inactiu i es marcarà com a actiu. Això vol dir que no es podrà loginar. Segur que vols continuar?"),id,true);
    }
});

$('#teacher_list tbody').on('click', 'td button.edit_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id
    window.location.href = _teacher_update_url + id + '/';
});

$('#teacher_list tbody').on('click', 'td button.chgpsswd_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id;
    url = '/user/password/change/' + id;
    window.location.href = url;
});

});
