$(document).ready( function () {
    var table = $('#test_list').DataTable( {
        'ajax':{
            'url': _test_list_url,
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
            { 'data': 'type' },
            {'data': 'test_results'}
        ],

        'columnDefs': [
            {
                'targets':0,
                'title': 'Nom de la prova'
            },
            {
                'targets':1,
                'title': 'Nom de l\'autor',
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
                'title': 'Tipus de prova',
                'render': function(value){
                    if (value === 0){
                        return "Test"
                    }else if(value === 2){
                        return "Enquesta"
                    }
                }
            },
            {
                'targets': 3,
                'title': 'Veure resultats',
                'data': 'test_results',
                'sortable': false,
                'render': function(value){
                    return '<button title="Veure resultats" class="check_results btn btn-info"><i class="far fa-eye" aria-hidden="true"></i></button>';
                }
            },

        ]
    });

    $('#test_list tbody').on('click', 'td button.check_results', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var quiz_id = row.data().id;
        var testType = row.data().type;

        if (testType === 0){ //Test
            console.log(_test_results);
            window.location.href = _test_results.replace('0', quiz_id); + '/';
        }else if(testType === 2){ //POLL
            console.log(_poll_results)
            window.location.href = _poll_results.replace('0', quiz_id); + '/';
        }
    });
});
