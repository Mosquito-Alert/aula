$(document).ready(function(){
    $('.header').click(function(){
        var this_id = this.id;
        var id = this_id.split('_')[2];
        $('#quiz_content_' + id).slideToggle('slow');
        $(this).find('i').toggleClass('fa-plus-square fa-minus-square');
    });
});
