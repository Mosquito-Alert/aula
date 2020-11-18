$(document).ready( function () {

var delete_center = function(id, toggle_flip){
    $.ajax({
        url: '/center/update-partial/' + id + '/',
        data: {"active":toggle_flip},
        method: 'PUT',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        success: function( data, textStatus, jqXHR ) {
            if(toggle_flip == true){
                toastr.success('Centre activat!');
            }else{
                toastr.success('Centre inactivat!');
            }
            table.ajax.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error('Error modificant centre');
        }
    });
};

var confirmDialog = function(message,id, to_state){
    $('<div></div>').appendTo('body')
        .html('<div><h6>'+message+'</h6></div>')
        .dialog({
            modal: true, title: 'Inactivant centre...', zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    delete_center(id, to_state);
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

var table = $('#center_list').DataTable( {
    'ajax': {
        'url': _center_list_url,
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
        { 'data': 'name' }
        ,{ 'data': 'pos_x' }
        ,{ 'data': 'pos_y' }
        ,{ 'data': 'created_date' }
        ,{ 'data': 'modified_date' }
        ,{ 'data': 'active' }
    ],
    'columnDefs': [
        {
            'targets': 6,
            'data': 'active',
            'sortable': false,
            'render': function(value){
                return '<button class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
            }
        },
        {
            'targets': 7,
            'data': 'active',
            'sortable': false,
            'render': function(value){
                if(value==true){
                    return '<button class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }else{
                    return '<button class="edit_button btn btn-info disabled"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            }
        },
        {
            'targets':0,
            'title': 'Nom'
        },
        {
            'targets':1,
            'title': 'X',
            'sortable': false
        },
        {
            'targets':2,
            'title': 'Y',
            'sortable': false
        },
        {
            'targets':3,
            'title': 'Data creació',
            'sortable': true,
            "render": function(value){
                var date = new Date(value);
                var month = date.getMonth() + 1;
                return date.getDate() + "/" + month + "/" + date.getFullYear() + " - " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
            }
        },
        {
            'targets':4,
            'title': 'Data modificació',
            'sortable': true,
            "render": function(value){
                var date = new Date(value);
                var month = date.getMonth() + 1;
                return date.getDate() + "/" + month + "/" + date.getFullYear() + " - " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
            }
        },
        {
            'targets':5,
            'title': 'Centre actiu?',
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

$('#center_list tbody').on('click', 'td button.delete_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id;
    var active = row.data().active;
    if(active){
        confirmDialog("El centre està actiu i es marcarà com a inactiu. Segur que vols continuar?",id,false);
    }else{
        confirmDialog("El centre està inactiu i es marcarà com a actiu. Segur que vols continuar?",id,true);
    }
});

$('#center_list tbody').on('click', 'td button.edit_button', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    var id = row.data().id
    window.location.href = _center_update_url + id + '/';
});

});