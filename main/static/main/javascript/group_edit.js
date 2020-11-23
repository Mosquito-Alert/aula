$(document).ready(function() {
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

    $(document).on('click', '.deleteFoto', function() {
        if( confirm("Eliminar la foto?") ){
            $("#gallery tbody").html('');
            $('#id_photo_path').val('');
        }
    });

    $('#center').change(function(){
        var selected_value = $(this).val()
        load_tutors(selected_value);
    });

    $('#tutor').change(function(){
        var selected_value = $(this).val();
        $('#id_select_alum').empty().trigger("change");
        if(selected_value!="-1"){
            $('#id_select_alum').attr("disabled",false);
        }else{
            $('#id_select_alum').attr("disabled",true);
        }
        console.log(selected_value);
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

    //$('#id_select_alum').attr("disabled",true);

    if(selected_center != -1){
        $('#center option[value=' + selected_center + ']').prop('selected', true);
        load_tutors(selected_center).then(
            function(){
                if(selected_tutor != -1){
                    $('#tutor option[value=' + selected_tutor + ']').prop('selected', true);
                }
            },
            function(error){
                console.log(error);
            }
        );
    }

    /*if(selected_tutor != -1){
        $('#id_teacher option[value=' + selected_tutor + ']').prop('selected', true);
    }*/

    for(var i = 0; i < init_data.length; i++){
        $("#id_select_alum").append(new Option(init_data[i].text, init_data[i].id, true, true));
    }

    $('#group_form').submit(function() {
        $('#alum_ids').val('');
        var alum_ids = $("#id_select_alum").select2('data');
        var ids = [];
        for(var i = 0; i < alum_ids.length; i++){
            ids.push( alum_ids[i].id );
        }
        $('#alum_ids').val( ids.join(',') );
    });
});