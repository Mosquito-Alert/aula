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
                toastr.error('Només es permeten fitxers zip');
                goUpload = false;
            }
            if (goUpload == true) {
                data.submit();
            }
        },
        done: function (e, data) {
          if (data.result.is_valid) {
            $("#gallery tbody").html(
            "<tr id='tr_" + data.result.id + "'>" +
                "<td>" +
                    "<a target='_blank' href='" + data.result.url +  "'>" +
                        "Fitxer pujat amb èxit!" +
                    "</a> <i class='fas fa-thumbs-up'></i>" +
                "</td>" +
                "<td>" +
                    "<a href='#' class='btn btn-danger btn-sm btn-del btn-del-img deleteFile' id="+ data.result.id +">Eliminar</a>" +
                "</td>" +
            "<tr>");
            $('#file_name').val(data.result.url);
            $('.end_button').show();
          }else{
            alert(data.result.error_imagen);
          }
        }
    });

    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

    $(".done-button").click(function () {

    });

    $(document).on('click', '.deleteFile', function() {
        if( confirm("Eliminar el fitxer?") ){
            $("#gallery tbody").html('');
            $('.end_button').hide();
        }
    });
});