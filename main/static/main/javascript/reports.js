$(document).ready( function () {

    var generate_query_poll_center_or_group = function(poll_id, center_id, group_id){
        if(group_id == null || group_id == ''){
            var url = '/reports/poll_center_or_group/' + poll_id + '/' + center_id + '/';
        }else{
            var url = '/reports/poll_center_or_group/' + poll_id + '/' + center_id + '/' + group_id + '/';
        }
        window.open(url, '_blank').focus();
    }

    var generate_progress_center = function(center_id){
        var url = '/reports/center_progress/' + center_id + '/';
        window.open(url, '_blank').focus();
    }

    var load_groups_by_center = function(center_id){
        $('#select_poll_group').attr("disabled",true);
        $('#loading_group').show();
        $.ajax({
            url: '/api/group_combo/',
            data: { 'center_id': parseInt(center_id) },
            method: 'GET',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                $('#select_poll_group').attr("disabled",false);
                $('#loading_group').hide();
                var options = ['<option value="">...</option>'];
                for(var i = 0; i < data.length; i++){
                    options.push('<option value="' + data[i].id + '">' + data[i].public_name + '</option>')
                }
                $('#select_poll_group').html(options.join());
            },
            error: function(jqXHR, textStatus, errorThrown){
                toastr.error(gettext('Error recuperant llista de grups per centre'));
                $('#select_poll_group').attr("disabled",false);
                $('#loading_group').hide();
            }
        });
    };

    $("#select_poll_center").change(function () {
        var center_id = this.value;
        load_groups_by_center(center_id);
        console.log(center_id);
    });

    $('#poll_group_class').click( function(){
        var poll_id = $('#select_poll').val();
        var center_id = $('#select_poll_center').val();
        var group_id = $('#select_poll_group').val();
        generate_query_poll_center_or_group(poll_id,center_id,group_id);
    } );

    $('#progress_center').click( function(){
        var center_id = $('#select_progress_center').val();
        generate_progress_center(center_id);
    } );
});
