$(document).ready(function(){
    for(var key in data){
        var content = data[key];
        $('#' + key + '_howmany').text( data[key]['n'] );
        $('#' + key + '_total').text( data[key]['total'] );
        $('#' + key + '_progress').width( data[key]['perc'] + '%' );
        $('#' + key + '_progress').text( data[key]['perc'] + '%' );
    }
});
