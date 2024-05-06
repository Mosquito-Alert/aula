$(document).ready(function() {

var delete_material = function(quizrun_id, to_state){
    $.ajax({
        url: '/api/delete_material/' + quizrun_id + '/',
        method: 'DELETE',
        dataType: 'json',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        success: function( data, textStatus, jqXHR ) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            toastr.error(gettext('Error esborrant material - ') + jqXHR.responseJSON.msg);
        }
    });
};

$('#materials tbody').on('click', 'td button.delete_button', function () {
    if(confirm(gettext("ATENCIÓ: S'esborrarà el material, incloent el fitxer, i l'alumne haurà de repetir la prova. Segur que vols continuar?"))){
        var quizrun_id = $(this).data('quizrun-id');
        delete_material(quizrun_id);
    }
});

});
