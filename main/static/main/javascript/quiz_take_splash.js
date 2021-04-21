$(document).ready( function () {

    $('#start_quiz').click(function(){
        create_run(quiz_id,taken_by,current_run);
    });

    var create_run = function(quiz_id, taken_by, run_number){
        $.ajax({
            url: _run_create_url,
            data: {"quiz_id":quiz_id, "taken_by":taken_by, "run_number":run_number},
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                var start_run_url = '/quiz/take/' + quiz_id + '/1/' + data.run_id + '/';
                location.href = start_run_url;
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error iniciant prova'));
            }
        });
    };

});
