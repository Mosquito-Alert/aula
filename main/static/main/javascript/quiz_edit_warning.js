function Confirm(title, msg, resp1, resp2) {
    var mensaje =  "<div class='warning-message'>" +
                    "<div class='dialog'><div class='closeIcon'>" +
                     "<p><i class='fa fa-close cancelAction'></i></p></div>" +
                    "<div class='dialog-msg'>" +
                    "<p class='warningIcon'><i class='fas fa-exclamation-triangle fa-3x'></i></p>" +
                    " <p> " + msg + " </p> " +
                 "</div>" +
                 "<footer>" +
                     "<div class='controls'>" +
                         " <button type='button' class='btn btn-primary doAction'>" + resp1 + "</button> " +
                         " <button type='button' class='btn btn-danger cancelAction'>" + resp2 + "</button> " +
                     "</div>" +
                 "</footer>" +
              "</div>" +
            "</div>";

    $('#dialog-confirm').prepend(mensaje);

    $('.doAction').click(function () {
        $(this).parents('.warning-message').fadeOut(500, function () {
            $(this).remove();
        });
        $("form").submit();
    });

    $('.cancelAction').click(function () {
        $(this).parents('.warning-message').fadeOut(500, function () {
            $(this).remove();
        });
    });
};





$('#quizSubmitForm').click(function (e) {
    var publishChecked = $('#id_published').is(":checked");
    if (publishChecked){
        e.preventDefault();
        Confirm(_title_warning_dialog, _message_warning_dialog, _aff_warning_dialog, _neg_warning_dialog);
    }
});





