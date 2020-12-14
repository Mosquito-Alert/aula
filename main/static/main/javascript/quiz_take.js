$(document).ready( function () {

    var setSuccess = function(){
        $('#status').removeClass('icon_fail');
        $('#status').addClass('icon_success');
    }

    $('input[type=radio][name=answers]').change(function() {
        console.log(this.value);
        setSuccess();
    });

    $('.open-link').click(function(){
        setSuccess();
        //console.log($(this).dataset.link);
        window.open(this.dataset.link,'_blank','resizable=yes')
    });

});