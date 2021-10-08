$(document).ready(function(){
    for(var key in data){
        var content = data[key];
        var state = data[key]['state'];
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
    }
});
