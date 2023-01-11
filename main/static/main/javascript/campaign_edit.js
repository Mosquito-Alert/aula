$(document).ready(function() {
    $(function () {
        $("#id_start_date").datepicker({
          format:'dd/mm/yyyy',
        });
        $("#id_end_date").datepicker({
          format:'dd/mm/yyyy',
        });
    });

    tinymce.init({
      selector: '#id_html_header_groups',
      plugins: 'image'
    });

    tinymce.init({
      selector: '#id_html_header_teachers',
      plugins: 'image'
    });
});
