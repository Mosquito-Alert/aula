$(document).ready(function() {

    var control_list = [
        "#test_copy",
        "#destination_campaign",
        "#destination_test",
        "#origin_campaign",
        "#origin_test",
    ];

    var start_test_load_spinner = function(){
        $("#origin_test").prop("disabled",true);
        $('#progress_load_tests').show();
    }

    var stop_test_load_spinner = function(){
        $("#origin_test").prop("disabled",false);
        $('#progress_load_tests').hide();
    }

    var start_copy_spinner = function(){
        lock_ui();
        $('#progress_copy_tests').show();
    }

    var stop_copy_spinner = function(){
        unlock_ui();
        $('#progress_copy_tests').hide();
    }

    var lock_ui = function(){
        for(var i = 0; i < control_list.length; i++){
            $(control_list[i]).prop("disabled",true);
        }
    }

    var unlock_ui = function(){
        for(var i = 0; i < control_list.length; i++){
            $(control_list[i]).prop("disabled",false);
        }
    }

    var reset_ui = function(){
        for(var i = 0; i < control_list.length; i++){
            $(control_list[i]).val("");
        }
        $('#success_info').hide();
    }

    var show_success_info = function(data){
        $('#success_info').show();
        const name = data.new_quiz.name;
        const browse_link = data.new_quiz.quiz_browse_url;
        const edit_link = data.new_quiz.quiz_edit_url;
        const nom_de_la_prova = gettext('Nom de la nova prova:');
        const enllac_a_la_nova_prova = gettext('Enllaç a la nova prova (consultar):');
        const enllac_a_la_nova_prova_editar = gettext('Enllaç a la nova prova (editar):');
        const message = `<li>${nom_de_la_prova} ${name}  </li><li>${enllac_a_la_nova_prova} <a href="${browse_link}" target="_blank">${name}</a> </li><li>${enllac_a_la_nova_prova_editar} <a href="${edit_link}" target="_blank">${name}</a> </li>`;
        $('#success_details').html(message);
    }

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
                stop_test_load_spinner();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error recuperant llista de proves'));
                stop_test_load_spinner();
            }
        });
    };

    var do_copy = function( new_campaign_id, original_quiz_id, new_name ){
        start_copy_spinner();
        $.ajax({
            url: _api_copytest_url,
            method: 'POST',
            data: { 'quiz_id': original_quiz_id, 'campaign_to': new_campaign_id, 'quiz_name': new_name},
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                console.log(data);
                stop_copy_spinner();
                show_success_info(data);
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext(gettext('Error copiant prova:') + ' ' + errorThrown));
                stop_copy_spinner();
            }
        });
    }

    var init_select = function(select_id, data){
        $(select_id).empty().append('<option value="0">----</option>');
        for(var i = 0; i < data.length; i++){
            $(select_id).append($('<option>', {
                value: data[i].id,
                text: data[i].seq + ' - ' +data[i].name
            }));
        }
    };

    var reset_ui = function(){
    }

    $('#origin_campaign').on('change',function(){
        let campaign_id = $(this).val();
        start_test_load_spinner();
        if(campaign_id!="0"){
            load_quizzes(campaign_id,'#origin_test');
        }else{
            init_select('#origin_test',[]);
        }
    });

    $('#test_copy').on('click',function(){
        var new_campaign_id = $('#destination_campaign').val();
        var original_quiz_id = $('#origin_test').val();
        var name = $('#destination_test').val();
        if(new_campaign_id == ''){
            toastr.info(gettext("Cal seleccionar la campanya a la que es copiarà la prova"));
            return;
        }
        if(original_quiz_id == ''){
            toastr.info(gettext("Cal seleccionar la prova que es vol copiar"));
            return;
        }
        do_copy(new_campaign_id, original_quiz_id, name);
    });
});
