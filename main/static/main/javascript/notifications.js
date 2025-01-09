$(document).ready( function () {
    var table = $('#notifications_list').DataTable( {
        'ajax': {
            'url': _notification_list_url,
            'dataType': 'json',
            'data': function(d){
                const selectedValue = $('input[name="radiollegit"]:checked').val();
                console.log(`Selected: ${selectedValue}`);
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
                'data': 'is_active',
                'sortable': false,
                'render': function(value){
                    return '<button title="' + gettext('Desactivar usuari') + '" class="delete_button btn btn-danger"><i class="fas fa-backspace"></i></button>';
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
});