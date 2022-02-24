$(document).ready(function(){
    for(var key in data){
        var content = data[key];
        var state = data[key]['state'];
        var type = data[key]['type'];
        var fileurl = data[key]['upload_url'];
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
        }
        $('#' + key + '_color').addClass( color_class );
        $('#' + key + '_state').html( icon );
        if(state == 'pending'){
            $('#' + key + '_linkp').hide();
        }else{
            var url = '#';
            if( type == 2 ){
                //url = '/quiz/poll_result/24/87/
                //url = '/quiz/poll_result/'  + key.split('_')[1] + '/' + key.split('_')[0] + '/';
                url = '/reports/poll_center_or_group/'  + key.split('_')[1] + '/' + center_id + '/' + key.split('_')[0] + '/';
            }else if ( type == 3 ){
                url = fileurl;
            }else{
                url = '/quiz/test_result/' + key.split('_')[1] + '/' + key.split('_')[0] +'/detail/';
            }
            $('#' + key + '_link').attr("href", url);
        }
    }
});
