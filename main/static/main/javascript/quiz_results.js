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
            { 'data': 'seq' },
            { 'data': 'author.username' },
            { 'data': 'type_text' },
            {'data': 'test_results'}
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
                'title': gettext('Nom autor'),
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
                'title': gettext('Tipus de prova')
            },
            {
                'targets': 4,
                'title': gettext('Veure resultats'),
                'data': 'test_results',
                'sortable': false,
                'render': function(value){
                    return '<button title="' + gettext('Veure resultats') + '" class="check_results btn btn-info"><i class="far fa-eye" aria-hidden="true"></i></button>';
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
        }else if(testType === 2 || testType === 4){ //POLL
            console.log(_poll_results)
            window.location.href = _poll_results.replace('0', quiz_id); + '/';
        }else if(testType === 6){ //OPEN ANSWER TEACHER
            window.location.href = _teacher_open_results.replace('0', quiz_id); + '/';
        }
    });
});
