$(document).ready(function() {

    $('.languageSelector').click(function (){
        var lang = $(this).attr('value');
        $('#languageForm').append('<input type="hidden" name="language" value="' + lang + '" />');
        $('#languageForm').submit();
    });

    //$(".languageSelector option[value='" + currentLang + "']").attr("selected","selected");
});
