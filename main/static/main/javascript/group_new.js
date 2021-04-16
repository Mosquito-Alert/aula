$(document).ready(function() {
    var load_group_names = function(){
        $.ajax({
            url: _random_url,
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
                toastr.error('Error recuperant nom de grup');
            }
        });
    };

    var load_tutors = function(center_id){
        var def = $.Deferred();
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
                var options = ['<option value="-1">Select tutor...</option>'];
                for(var i = 0; i < data.length; i++){
                    options.push('<option value="' + data[i].id + '">' + data[i].username + '</option>')
                }
                $('#tutor').html(options.join());
                def.resolve();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error recuperant llista de tutors per centre');
                $('#tutor').attr("disabled",false);
                def.reject(textStatus);
            }
        });
        return def.promise();
    };

    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

    $("#fileupload").fileupload({
        dataType: 'json',
        formData: [
            { name: "csrfmiddlewaretoken", value: "{{ csrf_token }}"}
        ],
        done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
          if (data.result.is_valid) {
            $("#gallery tbody").html(
            "<tr id='tr_" + data.result.id + "'>" +
                "<td>" +
                    "<a target='_blank' href='" + data.result.url +  "'>" +
                        "<img id="+ data.result.id +" style='height: 150px;' src='" + data.result.url + "'>" +
                    "</a>" +
                "</td>" +
                "<td>" +
                    "<a href='#' class='btn btn-danger btn-sm btn-del btn-del-img imatgeRodal deleteFoto' id="+ data.result.id +">Eliminar</a>" +
                "</td>" +
            "<tr>");
            //setJSONFotos(data.result.id);
            $('#id_photo_path').val(data.result.url);
          }else{
            alert(data.result.error_imagen);
          }
        }
    });

    $(document).on('click', '.deleteFoto', function() {
        if( confirm("Eliminar la foto?") ){
            $("#gallery tbody").html('');
        }
    });

    $(document).on('click', '.suggest-fields', function() {
        $('#id_password1').val(utils.generate_random_password_4());
        load_group_names();
    });

    $('#center').change(function(){
        var selected_value = $(this).val()
        $('#group_center').val(selected_value);
        load_tutors(selected_value);
    });

    $('#tutor').change(function(){
        var selected_value = $(this).val();
        $('#group_teacher').val(selected_value);
    });

    $('#group_form').submit(function() {
        var selected_tutor = $('#group_teacher').val();
        if(selected_tutor==null || selected_tutor == '' || selected_tutor == '-1'){
            $("#tutor").addClass("is-invalid");
            $("#selected_tutor").append('<p id="error_1_id_username" class="invalid-feedback"><strong>Si us plau, tria el tutor del grup del desplegable</strong></p>')
            return false;
        }
    });

    var init_ui = function(){
        var selected_center = $('#group_center').val();
        var selected_tutor = $('#group_teacher').val();
        if( selected_center!=null && selected_center != '' && selected_center != '-1'){
            $('#center option[value=' + selected_center + ']').prop('selected', true);
            load_tutors(selected_center).then(
                function(){
                    if( selected_tutor != null && selected_tutor != '-1' ){
                        $('#tutor option[value=' + selected_tutor + ']').prop('selected', true);
                    }
                },
                function(error){
                    console.log(error);
                }
            );
        }
    }

    init_ui();


});
