var get_highest_question_number = function(){
    var numbers = [];
    $("[class^='ord_']").each(function(index, el){
        var class_name = $(this).attr('class');
        var order = parseInt( class_name.split('_')[1] );
        numbers.push(order);
    });
    var max_idx;
    max_idx = Math.max.apply(Math, numbers);
    if(max_idx){
        return max_idx + 1;
    }else{
        return 1;
    }
}


$(document).ready(function() {

    $('#add_question').click(function(){
        window.location.href = _question_new_url + quiz_id + "/" + '?n=' + suggested_new_order;
    });

    $('#add_question_link').click(function(){
        window.location.href = _question_link_new_url + quiz_id + "/" + '?n=' + suggested_new_order;
    });

    $('#add_poll_question').click(function(){
        window.location.href = _question_poll_new_url + quiz_id + "/" + '?n=' + suggested_new_order;
    });

    $('#add_fileupload_question').click(function(){
        window.location.href = _question_upload_new_url + quiz_id + "/" + '?n=' + suggested_new_order;
    });

    $('.delete_button').click(function(){
        var question_id = $(this).attr('id');
        confirmDialog(gettext("ATENCIÓ: s'esborrarà la pregunta i totes les respostes. Segur que vols continuar?"), question_id);
    });

    var delete_question = function(id){
        $.ajax({
            url: _question_delete_url + id + '/',
            method: 'DELETE',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Pregunta eliminada!'));
                $('#question_' + id).remove();
                suggested_new_order = get_highest_question_number();
                if( $('#questions').children().length == 0 ){
                    $('#add_fileupload_question').removeClass('hidden');
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error eliminant pregunta'));
                suggested_new_order = get_highest_question_number();
            }
        });
    };

    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: gettext('Eliminant pregunta...'), zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Yes: function () {
                        delete_question(id);
                        $(this).dialog("close");
                    },
                    No: function () {
                        $(this).dialog("close");
                    }
                },
                close: function (event, ui) {
                    $(this).remove();
                }
        });
    };
});
