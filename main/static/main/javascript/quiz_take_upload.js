$(document).ready( function () {
    $("#fileupload").fileupload({
        dataType: 'json',
        formData: [
            { name: "csrfmiddlewaretoken", value: "{{ csrf_token }}"}
        ],
        add: function (e, data){
            var uploadFile = data.files[0];
            var goUpload = true;
            if (!(/\.(zip)$/i).test(uploadFile.name)) {
                toastr.error(gettext('Només es permeten fitxers zip'));
                goUpload = false;
            }
            if (goUpload == true) {
                data.submit();
            }
            $('#spinner').hide();
        },
        done: function (e, data) {
          $('#spinner').show();
          if (data.result.is_valid) {
            $("#gallery tbody").html(
            "<tr id='tr_" + data.result.id + "'>" +
                "<td>" +
                    "<a target='_blank' href='" + data.result.url +  "'>" +
                        gettext("Fitxer pujat amb èxit!") +
                    "</a> <i class='fas fa-thumbs-up'></i>" +
                "</td>" +
                "<td>" +
                    "<a href='#' class='btn btn-danger btn-sm btn-del btn-del-img deleteFile' id="+ data.result.id +">Eliminar</a>" +
                "</td>" +
            "<tr>");
            $('#file_name').val(data.result.url);
            $('.end_button').show();
            $('.save_hub_button').hide();
          }else{
            alert("File type " + data.result.invalid_file_type + " not allowed. Must be a zip file.");
          }
          $('#spinner').hide();
        }
    });

    var complete = function(quizrun_id, file_path){
        $.ajax({
            url: _quiz_complete_upload,
            data: {'id':quizrun_id,'path':file_path},
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Prova finalitzada!'));
                window.location.href = _quiz_complete_url;
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error completant prova'));
            }
        });
    };

    var authorize = function(quizrun_id, value){
        $.ajax({
            url: _authorize,
            data: {'quizrun_id':quizrun_id,'value':value},
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {

            },
            error: function(jqXHR, textStatus, errorThrown){

            }
        });
    }

    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

    var complete_upload = function(){
        var file_path = $('#file_name').val();
        complete(quizrun_id,file_path);
    }

    $("#done-button").click(function () {
        complete_upload();
    });

    $(document).on('click', '.deleteFile', function() {
        if( confirm(gettext("Eliminar el fitxer?")) ){
            $("#gallery tbody").html('');
            $('.end_button').hide();
        }
    });

    $("input[name='yesnoradios']").change(function(){
        authorize(quizrun_id, $(this).val());
    });

    if( checked_value == true ){
        $("input[name='yesnoradios'][value=1]").attr('checked', true);
    }else{
        $("input[name='yesnoradios'][value=0]").attr('checked', true);
    }
});
