$(document).ready( function () {
    var create_run = function(quiz_id, taken_by){
        $.ajax({
            url: _run_create_url,
            data: {"quiz_id":quiz_id, "taken_by":taken_by, "run_number":1},
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                var start_run_url = '/quiz/take_upload/' + quiz_id + '/' + data.run_id + '/';
                location.href = start_run_url;
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error("Error iniciant prova")
            }
        });
    };

    $('div.col-md-6.alert.alert-info.todo').on('click', 'div.row.mt-3 div.col-md-6.done_quizzes button.btn.btn-success.take_upload', function () {
        var taken_by = $(this).data('taken_by');
        var quiz_id =  $(this).data('quiz_id');
        create_run(quiz_id,taken_by);
    });
});
