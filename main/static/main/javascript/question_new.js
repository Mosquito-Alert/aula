var row_editor;

$(document).ready(function() {

    row_editor = AEditor.create();

    $('#add_resposta').click(function(){
        row_editor.addAnswer('','',false);
    })

});