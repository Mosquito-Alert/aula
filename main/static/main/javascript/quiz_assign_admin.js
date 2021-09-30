$(document).ready(function() {

    var load_group_names = function(){
        $.ajax({
            url: '/api/group_name/',
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                var group_name = data.group_name;
                var group_slug = data.group_slug;
                $('#id_username').val(group_slug);
                $('#id_group_public_name').val(group_name);
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error recuperant nom de grup'));
            }
        });
    };

    var load_tutors = function(center_id){
        $('#tutor').attr("disabled",true);
        $.ajax({
            url: '/api/tutor_combo/',
            data: { 'center_id': parseInt(center_id) },
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                $('#tutor').attr("disabled",false);
                var options = ['<option value="-1">' + gettext('Select tutor...') + '</option>'];
                for(var i = 0; i < data.length; i++){
                    options.push('<option value="' + data[i].id + '">' + data[i].username + '</option>')
                }
                $('#tutor').html(options.join());
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error recuperant llista de tutors per centre'));
                $('#tutor').attr("disabled",false);
            }
        });
    };

    $('#center').change(function(){
        var selected_value = $(this).val()
        load_tutors(selected_value);
        $('#id_select_alum').val(null).trigger("change");
        $('#id_select_quiz').val(null).trigger("change");
        $('#id_select_group').val(null).trigger("change");
    });

    $('#tutor').change(function(){
        var selected_value = $(this).val();
        $('#id_select_alum').empty().trigger("change");
        if(selected_value!="-1"){
            $('#id_select_alum').attr("disabled",false);
            $('#id_select_quiz').attr("disabled",false);
            $('#id_select_group').attr("disabled",false);
        }else{
            $('#id_select_alum').attr("disabled",true);
            $('#id_select_quiz').attr("disabled",true);
            $('#id_select_group').attr("disabled",true);
        }
        $('#id_select_alum').val(null).trigger("change");
        $('#id_select_quiz').val(null).trigger("change");
        $('#id_select_group').val(null).trigger("change");
    });

    $('#id_select_alum').select2({
      ajax: {
        url: '/alum/search/',
        dataType: 'json',
        delay: 250,
        processResults: function (data) {
            return {
                results: data
            };
        },
        data: function(term,page){
            return {
                q: term,
                tutor_id: $("#tutor").val()
            };
        }
      }
    });

    $('#id_select_quiz').select2({
      ajax: {
        url: '/quiz/search/',
        dataType: 'json',
        delay: 250,
        processResults: function (data) {
            return {
                results: data
            };
        },
        data: function(term,page){
            return {
                q: term,
                tutor_id: $("#tutor").val()
            };
        }
      }
    });

    $('#id_select_group').select2({
      ajax: {
        url: '/group/search/',
        dataType: 'json',
        delay: 250,
        processResults: function (data) {
            return {
                results: data
            };
        },
        data: function(term,page){
            return {
                q: term,
                tutor_id: $("#tutor").val()
            };
        }
      }
    });

    $('#id_select_alum').attr("disabled",true);
    $('#id_select_quiz').attr("disabled",true);
    $('#id_select_group').attr("disabled",true);

    var resetUI = function(){
        $('#id_select_alum').val(null).trigger("change");
        $('#id_select_quiz').val(null).trigger("change");
        $('#id_select_group').val(null).trigger("change");
        $('#id_select_alum').attr("disabled",true);
        $('#id_select_quiz').attr("disabled",true);
        $('#id_select_group').attr("disabled",true);
        $('#tutor').empty();
        $('#tutor').html("<option selected>" + gettext('Tria primer un centre...') + "</option>");
        $('#center').val("-1");
    }

    $('input[type=radio][name=assignto]').change(function() {
        if (this.value == 'alum') {
            resetUI();
            $('#select_group').hide();
            $('#select_alum').show();
        }
        else if (this.value == 'group') {
            resetUI();
            $('#select_group').show();
            //$('#select_group').addClass("col-md-3");
            $('#select_alum').hide();
        }
    });


});
