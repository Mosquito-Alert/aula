$(document).ready(function() {
    var setFail = function(){
        $('.no_consent_message').show();
        $('.yes_consent_message').hide();
    }

    var setSuccess = function(){
        $('.no_consent_message').hide();
        $('.yes_consent_message').show();
    }

    var init_interface = function(){
        if( init_auth_group === true ){
             $("input[name='yesnoradios'][value=1]").attr('checked', true);
        }else{
            $("input[name='yesnoradios'][value=0]").attr('checked', true);
        }
        if( init_auth_tutor === true ){
            $("input[name='yesnoradios_tutor'][value=1]").attr('checked', true);
        }else{
            $("input[name='yesnoradios_tutor'][value=0]").attr('checked', true);
        }
        if( init_auth_group && init_auth_tutor ){
            setSuccess();
        }else{
            setFail();
        }
    }

    var authorize = function(consent_class, value){
        $.ajax({
            url: _post_consent,
            method: 'POST',
            data: { 'consent_class': consent_class, 'value': value },
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                // silence is golden
                if(data.auth_group && data.auth_tutor){
                    setSuccess();
                }else{
                    setFail();
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext("Error escrivint autorització"));
            }
        });
    }
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
                toastr.error(gettext("Error marcant formulari com visitat"));
            }
        });
    }

    $("input[name='yesnoradios']").change(function(evt){
        //authorize(quizrun_id, $(this).val());
        const consent_class = 0;
        const value = $(this).val() == 0 ? false : true;
        authorize(consent_class,value);
        //console.log( $(this).val() );
    });

    $("input[name='yesnoradios_tutor']").change(function(evt){
        //authorize(quizrun_id, $(this).val());
        const consent_class = 1;
        const value = $(this).val() == 0 ? false : true;
        authorize(consent_class,value);
        //console.log( $(this).val() );
    });

    mark_form_as_visited();
    init_interface();
});