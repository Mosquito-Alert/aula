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
            return consent_pupils.reduce( (acc, current) => acc && current );
        }
    }

    var init_interface = function(){
        for(var i=0; i < consent_pupils.length; i++){
            const consent_i = consent_pupils[i];
            const n = i + 1;
            if(consent_i == true){
                $("input[name='yesnoradios_" + n + "'][value=1]").attr('checked', true);
            }else{
                $("input[name='yesnoradios_" + n + "'][value=0]").attr('checked', true);
            }
        }
//        if( init_auth_group === true ){
//             $("input[name='yesnoradios'][value=1]").attr('checked', true);
//        }else{
//            $("input[name='yesnoradios'][value=0]").attr('checked', true);
//        }
        if( init_auth_tutor === true ){
            $("input[name='yesnoradios_tutor'][value=1]").attr('checked', true);
        }else{
            $("input[name='yesnoradios_tutor'][value=0]").attr('checked', true);
        }
        if( check_all_pupils() && init_auth_tutor ){
            setSuccess();
        }else{
            setFail();
        }
    }

    var authorize = function(consent_class, value, n){
        var _data;
        if(n==null){
            _data = { 'consent_class': consent_class, 'value': value };
        }else{
            _data = { 'consent_class': consent_class, 'value': value, 'n': n };
        }
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

    $(document).on('change', '.dynamic_yes_no', function() {
        const consent_class = 0;
        const value = $(this).val() == 0 ? false : true;
        const n = $(this).data('n');
        authorize(consent_class,value,n);
    });

    $("input[name='yesnoradios_tutor']").change(function(evt){
        const consent_class = 1;
        const value = $(this).val() == 0 ? false : true;
        authorize(consent_class,value);
    });

    mark_form_as_visited();
    init_interface();
});