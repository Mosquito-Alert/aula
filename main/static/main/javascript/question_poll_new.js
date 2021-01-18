var row_editor;

$(document).ready(function() {

    row_editor = AEditor.create({is_poll:true});

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

});