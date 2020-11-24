(function(){

    if (typeof AEditor === 'undefined') this.AEditor = {};

    AEditor.data = [];

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
            data: []
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
                AEditor.addAnswer( options.data[i].id, options.data[i].question_id, options.data[i].text, options.data[i].is_correct );
            }
        }else{
            AEditor.domElem.empty();
        }
        AEditor.template_id = options.template_id;
        return AEditor;
    }

    AEditor.addAnswer = function(label, text, is_correct){
        var id = AEditor.getId();
        AEditor.data.push({ 'id': id, 'label':label, 'text':text, 'is_correct':is_correct });
        var template = $('#' + AEditor.template_id).html();
        var data = {'row_id': id};
        AEditor.domElem.append(Mustache.render(template,data));
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

    $("#answers").on("click", "button.answer_delete", function(event){
        var button_id = $(this).attr('id');
        var row_id = button_id.split('_')[1];
        AEditor.removeAnswer(row_id);
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