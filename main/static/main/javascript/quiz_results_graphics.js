$(document).ready(function() {
    graficBarras(data);
});

var graficBarras = function(){
    var nombreGrupo = [];
    var resultadosGrupo = [];
    var quizName;

    for(z=0; z<data.length; z++){
        if (Array.isArray(data[z])){
            for(i=0; i<data[z].length; i++){
                nombreGrupo.push(data[z][i]['taken_by']);
                resultadosGrupo.push(data[z][i]['questions_right']);
                quizName = data[z][i]['quiz'];
            }
        }else{
            if(data[z]['taken_by']){
                nombreGrupo.push(data[z]['taken_by']);
                resultadosGrupo.push(data[z]['questions_right']);
                quizName = data[z]['quiz'];
            }
        }
    }

    Highcharts.chart('container', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Resultats per grup de la prova ' + quizName
        },
        /*subtitle: {
            text: 'Source: WorldClimate.com'
        },*/
        xAxis: {
            categories: nombreGrupo,
            crosshair: true
        },
        yAxis: {
            min: 0,
            max: 10,
            title: {
                text: 'Respostes correctes'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y}</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: quizName,
            data: resultadosGrupo

        }]
    });

}

