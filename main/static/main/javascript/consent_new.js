$(document).ready(function() {

    var setFail = function(){
        $('.no_consent_message').show();
        $('.yes_consent_message').hide();
    }

    var setSuccess = function(){
        $('.no_consent_message').hide();
        $('.yes_consent_message').show();
    }

    var check_all_pupils = function(){
        if(consent_pupils.length == 0){
            return false;
        }else{
            return consent_pupils.reduce( (acc, current) => acc && current.datause_pupil && current.datashare_pupil );
        }
    }

    var check_all_tutors = function(){
        if(consent_pupils.length == 0){
            return false;
        }else{
            return consent_pupils.reduce( (acc, current) => acc && current.datause_tutor && current.datashare_tutor );
        }
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

    var init_interface = function(){
        for(var i=0; i < consent_pupils.length; i++){
            const consent_i = consent_pupils[i];
            const n = consent_i.n;
            $('#datause_pupil_' + n).prop('checked', consent_i.datause_pupil);
            $('#datause_tutor_' + n).prop('checked', consent_i.datause_tutor);
            $('#datashare_pupil_' + n).prop('checked', consent_i.datashare_pupil);
            $('#datashare_tutor_' + n).prop('checked', consent_i.datashare_pupil);
        }
        const pupils = check_all_pupils();
        if( pupils && check_all_tutors() ){
            setSuccess();
        }else{
            setFail();
        }
    }

    var authorize = function(pupil_or_tutor, use_or_share, value, n){
        var _data = { 'pupil_or_tutor': pupil_or_tutor, 'use_or_share':use_or_share, 'value': value, 'n':n };
        $.ajax({
            url: _post_consent,
            method: 'POST',
            data: _data,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                // silence is golden
                if(data.full_consent){
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

    $(document).on('change', '.dynamic_control', function() {
        const value = $(this).prop('checked');
        const n = $(this).data('n');
        const use_or_share = $(this).data('datatype');
        const pupil_or_tutor = $(this).data('usertype');
        authorize(pupil_or_tutor, use_or_share, value, n);
    });

    mark_form_as_visited();
    init_interface();
});