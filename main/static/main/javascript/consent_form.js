$(document).ready(function() {
    var mark_form_as_visited = function(){
        $.ajax({
            url: _post_visited_consent,
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                // silence is golden
            },
            error: function(jqXHR, textStatus, errorThrown){
                setFail();
                setProgressPending(question_id);
                toastr.error(gettext("Error marcant formulari com visitat"));
            }
        });
    }

    $("input[name='yesnoradios']").change(function(){
        //authorize(quizrun_id, $(this).val());
        console.log( $(this).val() );
    });

    $("input[name='yesnoradios_tutor']").change(function(){
        //authorize(quizrun_id, $(this).val());
        console.log( $(this).val() );
    });

    mark_form_as_visited();
    $("input[name='yesnoradios'][value=0]").attr('checked', true);
    $("input[name='yesnoradios_tutor'][value=0]").attr('checked', true);
});