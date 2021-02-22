$(document).ready( function () {

    var post_answer = function(id, chosen_answer_id, question_id){
        var _data = {};
        _data.id = id;
        if (chosen_answer_id){
            _data.answer_id = chosen_answer_id;
        }
        $.ajax({
            url: _post_answer_url,
            data: _data,
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                setSuccess();
                setProgressDone(question_id);
                if(data.done==true){
                    showFinishButton();
                }else{
                    hideFinishButton();
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                setFail();
                setProgressPending(question_id);
                toastr.error("Error escrivint resposta");
            }
        });
    };

    var finish_quiz = function(id){
        $.ajax({
            url: _finish_quiz_url,
            data: {"id":id},
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                location.href = _summary_run_finish_url;
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error("Error finalitzant prova");
            }
        });
    }

    var confirmDialog = function(message,run_id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: 'Finalitzant prova...', zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        finish_quiz(run_id);
                        $(this).dialog("close");
                    },
                    No: function () {
                        $(this).dialog("close");
                    }
                },
                close: function (event, ui) {
                    $(this).remove();
                }
        });
    };

    var user_input_to_ui = function(user_input){
        if(user_input.chosen_answer_id){
            $('input[type=radio][name=answers][value=' + user_input.chosen_answer_id + ']').attr('checked', true);
        }else{
            $('input[name="answers"]').attr('checked', false);
        }
    }

    var setProgressDone = function(id_question){
        $('#question_' + id_question).removeClass('progress_pending');
        $('#question_' + id_question).addClass('progress_done');
    }

    var setProgressPending = function(id_question){
        $('#question_' + id_question).removeClass('progress_done');
        $('#question_' + id_question).addClass('progress_pending');
    }

    var setSuccess = function(){
        $('#status').removeClass('icon_fail');
        $('#status').addClass('icon_success');
    }

    var setFail = function(){
        $('#status').removeClass('icon_success');
        $('#status').addClass('icon_fail');
    }

    var showFinishButton = function(){
        $('.end_button').show();
    }

    var hideFinishButton = function(){
        $('.end_button').hide();
    }

    $('input[type=radio][name=answers]').change(function() {
        post_answer( user_input.id, this.value, this.dataset.questionid );
    });

    $('.open-link').click(function(){
        post_answer( user_input.id, null, this.dataset.id );
        window.open(this.dataset.link,'_blank','resizable=yes')
    });

    user_input_to_ui(user_input);

    if(all_questions_answered == true){
        showFinishButton();
    }

    $('#done-button').click(function(){
        var message = "Estàs a punt de finalitzar la prova. Si continues, no la podràs modificar més (tot i que pots repetir-la més tard) i rebràs el resultat en pantalla. Vols continuar?";
        confirmDialog(message, run_id);
    });

});