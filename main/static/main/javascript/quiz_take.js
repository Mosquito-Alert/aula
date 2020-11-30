$(document).ready( function () {

    $('input[type=radio][name=answers]').change(function() {
        console.log(this.value);
    });

});