$(document).ready(function() {
    var toggle_checked = function(quiz_id, group_id){
        $.ajax({
            url: _toggle_check_url,
            data: {"quiz_id":quiz_id, "group_id":group_id},
            method: 'POST',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
            },
            success: function( data, textStatus, jqXHR ) {
                if(textStatus=='nocontent'){
                    //unchecked
                    uncheck_tr(quiz_id, group_id);
                }else{
                    //checked
                    check_tr(quiz_id, group_id);
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                //toastr.error("Error iniciant prova")
            }
        });
    };

    var uncheck_tr = function(quiz_id, group_id){
        var tr = $('#tr_' + quiz_id + '_' + group_id);
        tr.removeClass('yes_visited');
        tr.addClass('no_visited');
    }

    var check_tr = function(quiz_id, group_id){
        var tr = $('#tr_' + quiz_id + '_' + group_id);
        tr.removeClass('no_visited');
        tr.addClass('yes_visited');
    }

    var adjust_ui = function(){
        $(".toggler").each(function( index, element ){
            $(this).removeAttr('checked');
        });
        for(var i = 0; i < checked_list.length; i++){
            $('#' + checked_list[i]).prop('checked', true);
        }
    }

    $(".toggler").click(function(){
        var quiz_id = $(this).data('quiz');
        var group_id = $(this).data('group');
        toggle_checked( quiz_id, group_id );
    });

    adjust_ui();

    $(".center_filter").click(function(){
        /*var querystring = window.location.search;
        console.log(querystring);
        var urlParams = new URLSearchParams(querystring);
        console.log(urlParams);*/
        var center_id = $(this).data('center-id');
        if(center_id == ''){
            window.location.href = "/upload_file/admin_board/";
        }else{
            window.location.href = "?center_id=" + center_id;
        }
    });
});
