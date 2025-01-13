$(document).ready( function () {
    var mark_as_read = function(id, read){
        $.ajax({
            url: '/internalnotification/update-partial/' + id + '/',
            data: {"read":read},
            method: 'PUT',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                console.log(data);
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error marcant notificació!'));
            }
        });
    };

    var table = $('#notifications_list').DataTable( {
        'ajax': {
            'url': _notification_list_url,
            'dataType': 'json',
            'data': function(d){
                const selectedValue = $('input[name="radiollegit"]:checked').val();
                d.filtrejson = JSON.stringify({ 'field':'read', 'value': selectedValue });
            }
        },
        'serverSide': true,
        'createdRow': function( row, data, dataIndex){
            if( data.read == true ){
                $(row).addClass('row-disabled');
            }
        },
        'processing': true,
        'language': table_language,
        'pageLength': 25,
        'pagingType': 'full_numbers',
        'bLengthChange': false,
        'responsive': true,
        'order': [[ 3, "desc" ]],
        stateSave: true,
        'dom': '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) );
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) );
        },
        'columns': [
            //{ 'data': 'id' }
            { 'data': 'center' }
            ,{ 'data': 'notification_text' }
            ,{ 'data': 'read' }
            ,{ 'data': 'created' }
        ],
        'columnDefs': [
//            {
//                'targets': 4,
//                'sortable': false,
//                'data': 'read',
//                'render': function(value){
//                    if(value){
//                        return '<button title="' + gettext('Marcar com no llegit') + '" class="read_button btn btn-danger"></button>';
//                    }else{
//                        return '<button title="' + gettext('Marcar com llegit') + '" class="read_button btn btn-danger"></button>';
//                    }
//                }
//            },
            {
                'targets':0,
                'title': gettext('Centre')
            },
            {
                'targets':1,
                'title': gettext('Notificacio')
            },
            {
                "targets": 2,
                "title": gettext("Llegida"),
                "render": function(value){
                    var retVal = "";
                    if(value){
                        retVal += '<input type="checkbox" class="visible_chk" checked/>';
                    }else{
                        retVal += '<input type="checkbox" class="visible_chk"/>';
                    }
                    return retVal;
                },
                "sortable": false
            },
            {
                'targets':3,
                'title': gettext('Data')
            }
        ]
    } );

    $('input[name="radiollegit"]').on('change', function () {
        table.ajax.reload();
    });


    $('#notifications_list tbody').on('click', 'td input.visible_chk', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        console.log(id);
        var read = row.data().read;
        mark_as_read(id, !read);
    });
});