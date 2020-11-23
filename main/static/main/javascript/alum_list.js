$(document).ready( function () {

//var colors = [
//  ['#00FFFF','#FF0000'],
//  ['#000080','#FFFF7F'],
//  ['#C0C0C0','#3F3F3F'],
//  ['#000000','#FFFFFF'],
//  ['#008000','#FF7FFF'],
//  ['#808000','#7F7FFF'],
//  ['#008080','#FF7F7F'],
//  ['#0000FF','#FFFF00'],
//  ['#00FF00','#FF00FF'],
//  ['#800080','#7FFF7F'],
//  ['#FFFFFF','#000000'],
//  ['#FF00FF','#00FF00'],
//  ['#800000','#7FFFFF'],
//  ['#FF0000','#00FFFF'],
//  ['#FFFF00','#0000FF'],
//  ['#808080','#7F7F7F']
//];

var colors = [
  ['#264653ff','#26b9ac00'],
  ['#2a9d8fff','#2a627000'],
  ['#e9c46aff','#e93b9500'],
  ['#f4a261ff','#f45d9e00'],
  ['#e76f51ff','#e790ae00']
];

var delete_alum = function(id, to_state){
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
                toastr.success('Alumne desactivat!');
            }else{
                toastr.success('Alumne activat!');
            }
            table.ajax.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error('Error modificant alumne');
        }
    });
};

var confirmDialog = function(message,id, to_state){
    $('<div></div>').appendTo('body')
        .html('<div><h6>'+message+'</h6></div>')
        .dialog({
            modal: true, title: 'Inactivant alumne...', zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    delete_alum(id,to_state);
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

var table = $('#alum_list').DataTable( {
    'ajax': {
        'url': _alum_list_url,
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
        ,{ 'data': 'teacher' }
        ,{ 'data': 'groups' }
        ,{ 'data': 'is_active' }
    ],
    'columnDefs': [
        {
            'targets': 4,
            'data': 'is_active',
            'sortable': false,
            'render': function(value){
                return '<button title="Desactivar usuari" class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
            }
        },
        {
            'targets': 5,
            'data': 'is_active',
            'sortable': false,
            'render': function(value){
                return '<button title="Editar" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
            }
        },
        {
            'targets': 6,
            'data': null,
            'sortable': false,
            'defaultContent': '<button title="Canviar password" class="chgpsswd_button btn btn-danger"><i class="fa fa-asterisk"></i></button>'
        },
        {
            'targets':0,
            'title': 'Nom usuari'
        },
        {
            'targets':1,
            'title': 'Professor'
        },
        {
            'targets':2,
            'title': 'Grups',
            'render': function(value){
                if(value != null){
                    var groups = value.split(',');
                    var badges = [];
                    for(var i = 0; i < groups.length; i++){
                        var index = i % 5;
                        badges.push('<span style="color:white;background-color:' + colors[0][0] + ';" class="badge badge-pill">' + groups[i] + '</span>');
                    }
                    if(badges.length == 0){
                        return '';
                    }else{
                        return badges.join(' ');
                    }
                }else{
                    return '';
                }
            }
        },
        {
            'targets':3,
            'title': 'Usuari actiu?',
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

$('#alum_list tbody').on('click', 'td button.delete_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id;
    var active = row.data().is_active;
    if(active){
        confirmDialog("El professor està actiu i es marcarà com a inactiu. Això vol dir que no es podrà loginar. Segur que vols continuar?",id,false);
    }else{
        confirmDialog("El professor està inactiu i es marcarà com a actiu. Això vol dir que no es podrà loginar. Segur que vols continuar?",id,true);
    }
});

$('#alum_list tbody').on('click', 'td button.edit_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id
    window.location.href = _alum_update_url + id + '/';
});

$('#alum_list tbody').on('click', 'td button.chgpsswd_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id;
    url = '/user/password/change/' + id;
    window.location.href = url;
});

});