$(document).ready(function() {
    var load_quizzes = function(campaign_id, dest_selector_id){
        $.ajax({
            url: _quizzes_list_url,
            method: 'GET',
            contentType: "application/json; charset=utf-8",
            data: { 'campaign_id': campaign_id},
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                init_select(dest_selector_id,data);
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error recuperant llista de proves'));
            }
        });
    };

    var init_select = function(select_id, data){
        $(select_id).empty().append('<option value="0">----</option>');
        for(var i = 0; i < data.length; i++){
            $(select_id).append($('<option>', {
                value: data[i].id,
                text: data[i].seq + ' - ' +data[i].name
            }));
        }
    };

    $('#origin_campaign').on('change',function(){
        let campaign_id = $(this).val();
        load_quizzes(campaign_id,'#origin_test');
    });
});
