$(document).ready(function() {
    $('.correct-new').click(function(){
        var quizrun_id = $(this).data('quizrun');
        url = '/quiz/open_answer/new/' + quizrun_id;
        window.location.href = url;
    });

    $('.correct-edit').click(function(){
        var quizrun_id = $(this).data('correction');
        url = '/quiz/open_answer/update/' + quizrun_id;
        window.location.href = url;
    });
});
