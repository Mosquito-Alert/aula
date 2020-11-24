<div id="{{ row_id }}" class="row">
    <div class="col-md-3">
        <label>Etiqueta</label>
        <input id="{{ label_id }}" class="form-control label" placeholder="Etiqueta">
    </div>
    <div class="col-md-6">
        <label>Text de la resposta</label>
        <textarea id="{{ text_id }}" name="text" cols="40" rows="3" class="form-control textarea form-control text"></textarea>
    </div>
    <div class="col-md-3">
        <label>Resposta correcta?</label>
        <input id="{{ correct_id }}" class="form-control correct form-check-input" type="checkbox" value="Resposta correcta?">
    </div>
</div>