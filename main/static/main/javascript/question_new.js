var row_editor;

$(document).ready(function() {

    row_editor = AEditor.create();

    $('#add_resposta').click(function(){
        row_editor.addAnswer('','',false);
    })

    $('#question_form').submit(function() {
        if (row_editor.validate() == true){
            var answers_data = JSON.stringify(row_editor.data);
            $('#id_answers_json').val(answers_data);
        }else{
            return false;
        }
    });

    if( init_answers ){
        row_editor.setData(init_answers);
    }

    var queryString = window.location.search;
    if(queryString!=null){
        var urlParams = new URLSearchParams(queryString);
        var suggested_order = urlParams.get('n');
        if(suggested_order!=null){
            if( $('#id_question_order').val() == '' ){
                $('#id_question_order').val(suggested_order);
            }
        }
    }

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
            console.log(data.result.url);
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



});