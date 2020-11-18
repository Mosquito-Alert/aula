$(document).ready( function () {
    $('.js-data-example-ajax').select2({
      ajax: {
        url: '/group/search/',
        dataType: 'json',
        delay: 250,
        processResults: function (data) {
            return {
                results: data
            };
        }
      }
    });

    $('#alum_form').submit(function() {
        $('#group_ids').val('');
        var group_ids = $("#id_select_group").select2('data');
        var ids = [];
        for(var i = 0; i < group_ids.length; i++){
            ids.push( group_ids[i].id );
        }
        $('#group_ids').val( ids.join(',') );
    });

    for(var i = 0; i < init_data.length; i++){
        $("#id_select_group").append(new Option(init_data[i].text, init_data[i].id, true, true));
    }

    /*
     programmatically add elems to select -> $("#id_select_group").append(new Option("Label", "1", true, true));
    */
});