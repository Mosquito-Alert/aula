$(document).ready(function() {

    var queryString = window.location.search;
    if(queryString!=null){
        var urlParams = new URLSearchParams(queryString);
        var suggested_order = urlParams.get('n');
        if(suggested_order!=null){
            if( $('#id_question_order').val() == '' ){
                $('#id_question_order').val(suggested_order);
            }
        }
    }

});