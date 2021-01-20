$(document).ready( function () {

    var load_reqs = function(author_id){
        var def = $.Deferred();
        $('#id_req').attr("disabled",true);
        $.ajax({
            url: '/api/requirements_combo/',
            data: { 'author_id': parseInt(author_id) },
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                $('#id_req').attr("disabled",false);
                var options = ['<option value="-1">--------</option>'];
                for(var i = 0; i < data.length; i++){
                    options.push('<option value="' + data[i].id + '">' + data[i].name + '</option>')
                }
                $('#id_req').html(options.join());
                def.resolve();
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error('Error recuperant llista de requeriments');
                $('#id_req').attr("disabled",false);
                def.reject(textStatus);
            }
        });
        return def.promise();
    };

    $('#id_req').change(function(){
        $('#id_requisite').val($(this).val());
    });

    $('#id_author').change(function(){
        load_reqs($(this).val());
    });
});