$(document).ready(function() {
    if(selected_center != -1){
        $('#id_belongs_to option[value=' + selected_center + ']').prop('selected', true);
    }
});