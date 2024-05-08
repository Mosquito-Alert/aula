var reset_row = function(quizrun_id){
    var controls = ['uploadedflag','linkfile','uploaddate','delete'];
    for(var i=0; i < controls.length; i++){
        if(controls[i]=='uploadedflag'){
            $('#' + quizrun_id + '_' + controls[i]).html('<i class="fas fa-times" style="color: red;" aria-hidden="true"></i>');
        }else{
            $('#' + quizrun_id + '_' + controls[i]).html(' - ');
        }
    }
}

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
            //location.reload();
            reset_row(quizrun_id);
            toastr.success(gettext('Material esborrat amb èxit!'));
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
