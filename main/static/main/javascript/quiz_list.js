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
        ],
        'columnDefs': [
            {
                'targets':0,
                'title': 'Nom de la prova'
            },
            {
                'targets':1,
                'title': 'Autor'
            },
            {
                'targets':2,
                'title': 'Centre'
            },
            {
                'targets': 3,
                'sortable': false,
                'render': function(value){
                    return '<button title="Editar" class="edit_button btn btn-info"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></button>';
                }
            },
        ]
    } );

    $('#quiz_list tbody').on('click', 'td button.edit_button', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var id = row.data().id
        window.location.href = _quiz_update_url + id + '/';
    });
});