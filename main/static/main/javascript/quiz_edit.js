$(document).ready(function() {
    $('#add_question').click(function(){
        console.log("click");
        window.location.href = _question_new_url + quiz_id + "/";
    });
});