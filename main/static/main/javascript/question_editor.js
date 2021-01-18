(function(){

    if (typeof AEditor === 'undefined') this.AEditor = {};

    AEditor.data = [];

    AEditor.is_poll = false;

    AEditor.domElem = null;

    AEditor.template_id = null;

    AEditor.getId = function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    AEditor.create = function(options){
        options = options || {};
        options = $.extend({},
        {
            div: 'answers',
            template_id: 'row_template',
            data: [],
            is_poll: false
        },
        options);
        if ($('#' + options.div).length ) {
            AEditor.domElem = $('#' + options.div);
        }else{
            throw "Div with id " + options.div + " does not exist";
        }
        if(options.data.length > 0){
            for(var i = 0; i < options.data.length; i++){
                var answer = options.data[i];
                AEditor.addAnswer( options.data[i].label, options.data[i].text, options.data[i].is_correct, options.data[i].id );
            }
        }else{
            AEditor.domElem.empty();
        }
        AEditor.template_id = options.template_id;
        AEditor.is_poll = options.is_poll;
        return AEditor;
    }

    AEditor.addAnswer = function(label, text, is_correct, id){
        if(id == null){
            id = AEditor.getId();
        }
        AEditor.data.push({ 'id': id, 'label':label, 'text':text, 'is_correct':is_correct });
        var template = $('#' + AEditor.template_id).html();
        var data = {'row_id': id};
        AEditor.domElem.append(Mustache.render(template,data));
        if(!AEditor.is_poll){
            $('#correct_' + id).prop( "checked", is_correct );
        }
        $('#label_' + id).val(label);
        $('#text_' + id).val(text);
    }

    AEditor.removeAnswer = function(id){
        for(var i = 0; i < AEditor.data.length; i++){
            var curr = AEditor.data[i];
            if(curr.id == id){
                AEditor.data.splice(i,1);
            }
        }
        $('#' + id).remove();
    }

    AEditor.updateData = function(id,key,value){
        for(var i = 0; i < AEditor.data.length; i++){
            var elem = AEditor.data[i];
            if(elem.id == id){
                elem[key] = value;
            }
        }
    }

    AEditor.getData = function(){
        console.log(AEditor.data);
    }

    AEditor.setData = function(data){
        for(var i = 0; i < data.length; i++){
            AEditor.addAnswer(data[i].label,data[i].text,data[i].is_correct,data[i].id);
        }
    }

    AEditor.validate = function(){
        // validation
        // All labels must be different
        // All labels must be non-empty
        // All texts must be non-empty
        // There must be at least a correct answer
        labels = [];
        errors = {};
        $('.answer-error').remove();
        var one_correct = false;
        if(AEditor.data.length == 0){
            $('#general_errors').html('<span><small class="text-danger answer-error"><strong>No has afegit cap resposta per la pregunta.</strong></small></span>');
            return false;
        }
        for(var i = 0; i < AEditor.data.length; i++){
            row = AEditor.data[i];
            if(row.label == null || row.label == ''){
                if ( errors['label_' + row.id] == null ){
                    errors['label_' + row.id] = [];
                }
                errors['label_' + row.id].push("L\'etiqueta de la pregunta no pot estar en blanc");
            }
            if(row.text == null || row.text == ''){
                if( errors['text_' + row.id] == null ){
                    errors['text_' + row.id] = [];
                }
                errors['text_' + row.id].push("El text de la pregunta no pot estar en blanc");
            }
            if(row.is_correct == true){
                one_correct = true;
            }
            if(labels.includes(row.label)){
                if(errors['label_' + row.id] == null){
                    errors['label_' + row.id] = [];
                }
                errors['label_' + row.id].push("L\'etiqueta està repetida, ha de ser única");
            }
            labels.push(row.label);
        }
        for(var dom_id in errors){
            for(var i = 0; i < errors[dom_id].length; i++){
                $('#' + dom_id).after('<span><small class="text-danger answer-error"><strong>' + errors[dom_id] + '</strong></small></span>');
            }
        }
        if(!one_correct){
            if (!AEditor.is_poll){
                $('#general_errors').html('<span><small class="text-danger answer-error"><strong>Cal marcar com a mínim una resposta com a correcta.</strong></small></span>')
            }
        }

        if ( (!one_correct && !AEditor.is_poll) || Object.keys(errors) > 0){
            return false;
        }

        return true;
    }

    $("#answers").on("click", "button.answer_delete", function(event){
        if(confirm("S'esborrarà la pregunta! Segur?") == true){
            var button_id = $(this).attr('id');
            var row_id = button_id.split('_')[1];
            AEditor.removeAnswer(row_id);
        }else{
            return false;
        }
    });

    $("#answers").on("focusout", "input.answer_label", function(event){
        var label_value = $(this).val();
        var label_id = $(this).attr('id');
        var row_id = label_id.split('_')[1];
        AEditor.updateData( row_id,'label',label_value );
    });

    $("#answers").on("click", "input.answer_correct", function(event){
        var check_value = $(this).is(":checked");
        var check_id = $(this).attr('id');
        var row_id = check_id.split('_')[1];
        if(check_value == true){
            for(var i = 0; i < AEditor.data.length; i++){
                if( AEditor.data[i].id != row_id ){
                    if ( $('#correct_' + AEditor.data[i].id).is(":checked") ){
                        $('#correct_' + AEditor.data[i].id).prop( "checked", false );
                        AEditor.updateData( AEditor.data[i].id,'is_correct', false );
                    }
                }
            }
        }
        AEditor.updateData( row_id,'is_correct', check_value );
    });

    $("#answers").on("focusout", "textarea.answer_text", function(event){
        var text_value = $(this).val();
        var text_id = $(this).attr('id');
        var row_id = text_id.split('_')[1];
        AEditor.updateData( row_id,'text', text_value );
    });


})();