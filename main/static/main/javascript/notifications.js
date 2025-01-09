$(document).ready( function () {
    var mark_as_read = function(id){
        $.ajax({
            url: '/internalnotification/update-partial/' + id + '/',
            data: {"read":true},
            method: 'PUT',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                if(data.is_active==false){
                    toastr.success(gettext('Alumne desactivat!'));
                }else{
                    toastr.success(gettext('Alumne activat!'));
                }
                table.ajax.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error modificant alumne'));
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
        'order': [[ 4, "desc" ]],
        stateSave: true,
        'dom': '<"top"iflp<"clear">>rt<"bottom"iflp<"clear">>',
        stateSaveCallback: function(settings,data) {
            localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) );
        },
        stateLoadCallback: function(settings) {
            return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) );
        },
        'columns': [
            { 'data': 'id' }
            ,{ 'data': 'center' }
            ,{ 'data': 'notification_text' }
            ,{ 'data': 'read' }
            ,{ 'data': 'created' }
        ],
        'columnDefs': [
            {
                'targets': 5,
                'sortable': false,
                'data': 'read',
                'render': function(value){
                    if(value){
                        return '<button title="' + gettext('Marcar com no llegit') + '" class="read_button btn btn-danger"></button>';
                    }else{
                        return '<button title="' + gettext('Marcar com llegit') + '" class="read_button btn btn-danger"></button>';
                    }
                }
            },
            {
                'targets':1,
                'title': gettext('Centre')
            },
            {
                'targets':2,
                'title': gettext('Notificacio')
            }
        ]
    } );

    $('input[name="radiollegit"]').on('change', function () {
        table.ajax.reload();
    });

    $('#notifications_list tbody').on('click', 'td button.read_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id;
        console.log(id);
        var read = row.data().read;
//        if(active){
//            confirmDialog(gettext("El professor està actiu i es marcarà com a inactiu. Això vol dir que no es podrà loginar. Segur que vols continuar?"),id,false);
//        }else{
//            confirmDialog(gettext("El professor està inactiu i es marcarà com a actiu. Això vol dir que no es podrà loginar. Segur que vols continuar?"),id,true);
//        }
    });
});