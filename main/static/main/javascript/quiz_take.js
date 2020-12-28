$(document).ready( function () {

    var post_answer = function(id, chosen_answer_id){
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
            },
            error: function(jqXHR, textStatus, errorThrown){
                setFail();
                toastr.error("Error escrivint resposta")
            }
        });
    };

    var user_input_to_ui = function(user_input){
        if(user_input.answered){
            setSuccess();
        }else{
            setFail();
        }
        if(user_input.chosen_answer_id){
            $('input[type=radio][name=answers][value=' + user_input.chosen_answer_id + ']').attr('checked', true);
        }else{
            $('input[name="answers"]').attr('checked', false);
        }
    }

    var setSuccess = function(){
        $('#status').removeClass('icon_fail');
        $('#status').addClass('icon_success');
    }

    var setFail = function(){
        $('#status').removeClass('icon_success');
        $('#status').addClass('icon_fail');
    }

    $('input[type=radio][name=answers]').change(function() {
        /*console.log(this.value);*/
        /*setSuccess();*/
        post_answer( user_input.id, this.value );
    });

    $('.open-link').click(function(){
        //setSuccess();
        //console.log($(this).dataset.link);
        post_answer( user_input.id );
        window.open(this.dataset.link,'_blank','resizable=yes')
    });

    user_input_to_ui(user_input);

});