$(document).ready( function () {

    var delete_quizrun = function(id){
        $.ajax({
            url: '/quizrun/delete/' + id + '/',
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                toastr.success(gettext('Intent eliminat'));
                $("#runsList").load(" #runsList");
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error eliminant l\'intent'));
            }
        });
    };


    $('tbody').on('click', 'td button.delete_quizrun', function () {
        var id = $(this).attr('id');

        var message = gettext("Segur que vols eliminar les dades d'aquest intent?");

        $('<div></div>').appendTo('body')
            .html('<div><h6>'+message+'</h6></div>')
            .dialog({
                modal: true, title: gettext("Eliminant dades d'intent..."), zIndex: 10000, autoOpen: true,
                width: 'auto', resizable: false,
                buttons: {
                    Si: function () {
                        delete_quizrun(id);
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

        /*if(active){
            confirmDialog("El professor està actiu i es marcarà com a inactiu. Això vol dir que no es podrà loginar. Segur que vols continuar?",id,false);
        }else{
            confirmDialog("El professor està inactiu i es marcarà com a actiu. Això vol dir que no es podrà loginar. Segur que vols continuar?",id,true);
        }*/
    });

});



var confirmDialog = function(message,id, to_state){
    $('<div></div>').appendTo('body')
        .html('<div><h6>'+message+'</h6></div>')
        .dialog({
            modal: true, title: gettext('Inactivant alumne...'), zIndex: 10000, autoOpen: true,
            width: 'auto', resizable: false,
            buttons: {
                Yes: function () {
                    delete_alum(id,to_state);
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
