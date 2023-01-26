$(document).ready(function(){
    for(var key in data){
        var content = data[key];
        var state = data[key]['state'];
        var type = data[key]['type'];
        var fileurl = data[key]['upload_url'];
        var correction_id = data[key]['correction_id'];
        var icon = "";
        var color_class = "";
        if(state == 'pending'){
            icon = '<i class="fas fa-times"></i>';
            color_class = 'alert-danger';
        }else if(state == 'done'){
            icon = '<i class="fas fa-check"></i>';
            color_class = 'alert-success';
        }else if(state == 'progress'){
            icon = '<i class="fas fa-hourglass"></i>';
            color_class = 'alert-warning';
        }else if(state == 'pending_correction'){
            icon = '<i class="fas fa-ellipsis-h"></i>';
            color_class = 'alert-warning';
        }else if(state == 'corrected'){
            icon = '<i class="fas fa-check"></i>';
            color_class = 'alert-success';
        }
        $('#' + key + '_color').addClass( color_class );
        $('#' + key + '_state').html( icon );
        if(state == 'pending' || state == 'pending_correction' || state == 'progress'){
            $('#' + key + '_linkp').hide();
        }else{
            var url = '#';
            if( type == 2 ){
                url = '/reports/poll_center_or_group/'  + key.split('_')[1] + '/' + center_id + '/' + key.split('_')[0] + '/';
            }else if ( type == 3 ){
                url = fileurl;
            }else if ( type == 5 ){
                if( state == 'corrected' ){
                    url = '/quiz/open_answer/detail/' + correction_id;
                }
            }else{
                url = '/quiz/test_result/' + key.split('_')[1] + '/' + key.split('_')[0] +'/detail/';
            }
            $('#' + key + '_link').attr("href", url);
        }
    }
});
