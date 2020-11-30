$(document).ready(function() {
    $('#add_question').click(function(){
        window.location.href = _question_new_url + quiz_id + "/" + '?n=' + suggested_new_order;
    });

    $('.delete_button').click(function(){
        var question_id = $(this).attr('id');
        confirmDialog("ATENCIÓ: s'esborrarà la pregunta i totes les respostes. Segur que vols continuar?", question_id);
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
                toastr.success('Pregunta eliminada!');
                $('#question_' + id).remove();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error eliminant pregunta');
            }
        });
    };

    var confirmDialog = function(message,id){
        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: 'Eliminant pregunta...', zIndex: 10000, autoOpen: true,
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