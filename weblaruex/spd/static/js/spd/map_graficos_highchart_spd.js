/*-------------------------------------------------------------------
# OPCIONES GENERALES DE CONFIGURACION DE UN GRAFICO
-------------------------------------------------------------------*/

Highcharts.setOptions({
    lang: {
        loading: 'Cargando...',
        months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        weekdays: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        exportButtonTitle: "Exportar",
        printButtonTitle: "Importar",
        rangeSelectorFrom: "Desde",
        rangeSelectorTo: "Hasta",
        rangeSelectorZoom: "Período",
        viewFullscreen: "Ver Modo Pantalla Completa",
        exitFullscreen: "Salir del modo Pantalla Completa",
        downloadPNG: 'Descargar imagen PNG',
        downloadJPEG: 'Descargar imagen JPEG',
        downloadPDF: 'Descargar imagen PDF',
        downloadSVG: 'Descargar imagen SVG',
        downloadCSV: 'Descargar CSV',
        downloadXLS: 'Descargar XLS',
        viewData: 'Ver Tabla de Datos',
        hideData: 'Ocultar Tabla de Datos',
        printChart: 'Imprimir',
        resetZoom: 'Reiniciar zoom',
        resetZoomTitle: 'Reiniciar zoom',
        thousandsSep: ",",
        decimalPoint: '.'
    }
});

function GraficoNivelRio(nombreEstacion, N1, N2, N3) {
    var options = {
        chart: {
            /*http://jsfiddle.net/d_paul/yo1jy1ku/*/
            //plotBackgroundImage: 'https://i.pinimg.com/originals/58/9b/f2/589bf2475b5c47aeb1d3533d93fbbdf7.gif',
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        title: {
            text: 'Nivel de Río'
        },
        subtitle: {
            text: 'Valores registrados durante las últimas 24 horas'
        },
        credits: {
            enabled: false
        },
        caption: {
            useHTML: true,
            text: '<p style="margin:0;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:35px; height:30px"><b> Datos sujetos a validación</b></p>'
        },
        tooltip: {
            /*headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat:
            '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: "</table>",
            shared: true,
            useHTML: true*/

            shared: true,
            useHTML: true,
            formatter: function () {
                return '<h1 class="cursive-brush" style="color:#1B1C1C; opacity:0.6; font-size:24px">' + nombreEstacion + '</h1>' +
                    Highcharts.dateFormat('%e %b %Y', this.x) + ', ' +
                    Highcharts.dateFormat('%H:%M', this.x) + ' h<br>' +
                    '</b> Nivel de río: <b>' + this.y + 'm </b><br><br>' +
                    '<i class="fas fa-circle" style="color:rgb(96, 240, 162)"></i></b> Sin riesgo </b><br>' +
                    '<i class="fas fa-circle" style="color:rgb(255, 255, 116)"></i></b> N1: <b>' + N1 + 'm </b><br>' +
                    '<i class="fas fa-circle" style="color:rgb(255, 181, 83)"></i></b> N2: <b>' + N2 + 'm </b><br>' +
                    '<i class="fas fa-circle" style="color:rgb(255, 84, 72)"></i></b> N3: <b>' + N3 + 'm </b><br>';
            }
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
            },
            global: {
                useUTC: false,
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
        },
        yAxis: [{
            min: 0,
            allowDecimals: true,
            title: {
                text: '<b>Nivel de Río (metros) </b>',
            },
            gridLineWidth: 0.1,
            plotBands: [
                { // Sin avisos
                    from: -Infinity,
                    to: parseFloat(N1),
                    color: /*'rgba(174, 243, 202,0.9)'*/{
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(174, 243, 202,0.8)'],
                            [1, 'rgba(96, 240, 162,0.8)']
                        ]
                    },
                    label: {
                        text: 'Sin avisos',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N1: Amarillo
                    from: parseFloat(N1),
                    to: parseFloat(N2),
                    color: /*'rgba(255, 255, 188, 0.9)'*/{
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(255, 255, 188, 0.8)'],
                            [1, 'rgba(255, 255, 116, 0.8)']
                        ]
                    },
                    label: {
                        text: 'Nivel 1',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N2: Naranja
                    from: parseFloat(N2),
                    to: parseFloat(N3),
                    color:  /*'rgba(255, 197, 144,0.9)'*/{
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(255, 197, 144, 0.8)'],
                            [1, 'rgba(255, 181, 83, 0.8)']
                        ]
                    },
                    label: {
                        text: 'Nivel 2',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N3: Rojo
                    from: parseFloat(N3),
                    to: Infinity,
                    color: /*'rgba(255, 136, 127, 0.7)'*/{
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(255, 136, 127, 0.8)'],
                            [1, 'rgba(255, 84, 72, 0.8)']
                        ]
                    },
                    label: {
                        text: 'Nivel 3',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }

                    }
                }]
        }],
        navigator: {
            adaptToUpdatedData: false,
            series: {
                type: 'line',
                data: []
            }
        },
        series: [{
            name: "Nivel de Río registrado",
            type: 'areaspline',
            data: [],
            lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true
        },/*{
                name: "Nivel de Río predicho",
                data: [],
                dashStyle: 'Dash',
                lineColor: '#1B1C1C',
                showInNavigator: true
            }*/],
        legend: {
            enabled: false
        },
        exporting: {
            filename: new Date().toLocaleDateString() + '_Nivel_Rio_' + nombreEstacion,
            scale: 1,
            sourceWidth: 1100,
            sourceHeight: 475,
            allowHTML: true,
            buttons: {
                contextButton: {
                    menuItems: menuChart
                }
            },
            chartOptions: {
                title: {
                    text: nombreEstacion
                },
                subtitle: {
                    text: 'Valores de Nivel de Río registrados durante las últimas 24 horas'
                },
                /*chart: {
                    plotBackgroundImage: 'https://i.pinimg.com/originals/58/9b/f2/589bf2475b5c47aeb1d3533d93fbbdf7.gif'
                }*/
                /*chart: {
                    plotBackgroundImage: 'http://alerta2.es/static/img/spd/logos/logo_alerta2.svg'
                }*/
            }
            /*chart: {
                zoomType: 'x',
                style: {
                    fontFamily: 'Roboto, sans-serif'
                },
                events: {
                    http://jsfiddle.net/d_paul/yo1jy1ku/
                    load: function() {
                        console.log("Altura", this.chartHeight);
                        this.renderer.image('../../../static/img/spd/logos/logo_alerta2_transparente.png')/*, (this.chartWidth-110),  (this.chartHeight-100), 100, 30)
                        .attr({
                            zIndex:1000, x:'calc(50% - 25%)', y:'40%', width:'50%',height:'22%', opacity:0.3
                        })
                        .add();
                    }
                }
            },*/

        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500,
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }

    };
    return options;
}


function GraficoPrecipitacion(nombreEstacion) {

    var options = {
        chart: {
            //plotBackgroundImage: 'https://i.pinimg.com/originals/58/9b/f2/589bf2475b5c47aeb1d3533d93fbbdf7.gif',
            type: 'column',
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        /*rangeSelector: {
            enabled:true
        },*/
        title: {
            text: 'Precipitación Acumulada en 1 hora'
        },
        subtitle: {
            text: 'Valores registrados durante las últimas 24 horas'
        },
        credits: {
            enabled: false
        },
        caption: {
            useHTML: true,
            text: '<p style="margin:0;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:35px; height:30px"><b> Datos sujetos a validación</b></p>'
        },
        legend: {
            enabled: false
        },
        tooltip: {
            shared: true,
            useHTML: true,
            formatter: function () {
                return '<h1 class="cursive-brush" style="color:#1B1C1C; opacity:0.6; font-size:24px">' + nombreEstacion + '</h1>' +
                    Highcharts.dateFormat('%e %b %Y', this.x) + ', ' +
                    Highcharts.dateFormat('%H:%M', this.x) + ' h<br>' +
                    '</b> Prec. Acum. 1h: <b>' + this.y + 'mm </b><br><br>' +
                    '<i class="fas fa-minus" style="color:rgb(255, 255, 116)"></i></b> Alerta amarilla por lluvias</b><br>' +
                    '<i class="fas fa-minus" style="color:rgb(255, 181, 83)"></i></b> Alerta naranja por lluvias </b><br>' +
                    '<i class="fas fa-minus" style="color:rgb(255, 84, 72)"></i></b> Alerta roja por lluvias </b><br>';
            }
        },
        plotOptions: {
            column: {
                borderWidth: 0.0
            },
            global: {
                useUTC: false,
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            }
        },
        yAxis: [{
            allowDecimals: true,
            title: {
                text: '<b>Precipitacion Acum. 1h (mm) </b>',
                /*style: {
                  color: 'Black'
                  }*/
            },
            gridLineWidth: 0.1,
            plotBands: [
                { // Sin avisos
                    from: -Infinity,
                    to: Infinity,
                    color: 'rgba(255, 255, 255,0.8)'
                }],
            plotLines: [{
                value: 15,
                zIndex: 2,
                width: 2,
                color: 'rgb(255, 255, 116)',
                dashStyle: 'longdashdot',
                label: {
                    text: 'Alerta amarilla por lluvias',
                    verticalAlign: 'bottom',
                    y: -5,
                    style: {
                        color: 'rgba(27,28,28,0.5)'
                    }

                }
            }, {
                value: 30,
                zIndex: 2,
                width: 2,
                color: 'rgb(255, 181, 83)',
                dashStyle: 'longdashdot',
                label: {
                    text: 'Alerta naranja por lluvias',
                    verticalAlign: 'bottom',
                    y: -5,
                    style: {
                        color: 'rgba(27,28,28,0.5)'
                    }

                }
            }, {
                value: 60,
                zIndex: 2,
                width: 2,
                color: 'rgb(255, 84, 72)',
                dashStyle: 'longdashdot',
                label: {
                    text: 'Alerta roja por lluvias',
                    verticalAlign: 'bottom',
                    y: -5,
                    style: {
                        color: 'rgba(27,28,28,0.5)'
                    }

                }
            }]
        }],
        series: [{
            name: "Precipitación registrada",
            data: [],
            type: 'column'
        },/*{
            name: "Precipitación predicha",
            data:[],
            type: 'column'
        }*/],
        exporting: {
            filename: new Date().toLocaleDateString() + '_Precipitacion_' + nombreEstacion,
            scale: 1,
            sourceWidth: 1100,
            sourceHeight: 475,
            allowHTML: true,
            buttons: {
                contextButton: {
                    menuItems: menuChart
                }
            },
            chartOptions: {
                title: {
                    text: nombreEstacion
                },
                subtitle: {
                    text: 'Valores de Nivel de Río registrados durante las últimas 24 horas'
                },
                /*chart: {
                    plotBackgroundImage: 'http://alerta2.es/static/img/spd/logos/logo_alerta2.svg'
                }*/
            }
        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }
    };
    return options;

}

function GraficoCompleto(nombreEstacion, N1, N2, N3) {
    var options = {
        chart: {
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            },
            backgroundColor:'rgba(255, 255, 255, 0.1)'
        },
        title: {
            text: nombreEstacion
        },
        subtitle: {
            text: 'Valores registrados durante las últimas 24 horas'
        },
        credits: {
            enabled: false
        },
        caption: {
            useHTML: true,
            text: '<p style="margin:0;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:35px; height:30px"><b> Datos sujetos a validación</b></p>'
        },
        tooltip: {
            shared: true,
            crosshairs: true
        },
        /*tooltip: {
            //headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            //pointFormat:
            //'<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            //'<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            //footerFormat: "</table>",
            //shared: true,
            //useHTML: true

            shared: true,
            useHTML: true,
            formatter: function () {
                return '<h1 class="cursive-brush" style="color:#1B1C1C; opacity:0.6; font-size:24px">' + nombreEstacion + '</h1>' +
                    Highcharts.dateFormat('%e %b %Y', this.x) + ', ' +
                    Highcharts.dateFormat('%H:%M', this.x) + ' h<br>' +
                    '</b> Nivel de río: <b>' + this.y + 'm </b><br><br>' +
                    '<i class="fas fa-circle" style="color:rgb(96, 240, 162)"></i></b> Sin riesgo </b><br>' +
                    '<i class="fas fa-circle" style="color:rgb(255, 255, 116)"></i></b> N1: <b>' + N1 + 'm </b><br>' +
                    '<i class="fas fa-circle" style="color:rgb(255, 181, 83)"></i></b> N2: <b>' + N2 + 'm </b><br>' +
                    '<i class="fas fa-circle" style="color:rgb(255, 84, 72)"></i></b> N3: <b>' + N3 + 'm </b><br>';
            }
        },*/
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
            },
            global: {
                useUTC: false,
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
        },
        yAxis: [{
            //min: 0,
            allowDecimals: true,
            title: {
                text: '<b>m</b>',
            },
            gridLineWidth: 0.1,
            /*plotBands: [
                { // Sin avisos
                    from: -Infinity,
                    to: parseFloat(N1),
                    color:{
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(174, 243, 202,0.8)'],
                            [1, 'rgba(96, 240, 162,0.8)']
                        ]
                    },
                    label: {
                        text: 'Sin avisos',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N1: Amarillo
                    from: parseFloat(N1),
                    to: parseFloat(N2),
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(255, 255, 188, 0.8)'],
                            [1, 'rgba(255, 255, 116, 0.8)']
                        ]
                    },
                    label: {
                        text: 'Nivel 1',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N2: Naranja
                    from: parseFloat(N2),
                    to: parseFloat(N3),
                    color:  {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(255, 197, 144, 0.8)'],
                            [1, 'rgba(255, 181, 83, 0.8)']
                        ]
                    },
                    label: {
                        text: 'Nivel 2',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }
                    }
                },
                { // Nivel N3: Rojo
                    from: parseFloat(N3),
                    to: Infinity,
                    color: {
                        linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgba(255, 136, 127, 0.8)'],
                            [1, 'rgba(255, 84, 72, 0.8)']
                        ]
                    },
                    label: {
                        text: 'Nivel 3',
                        verticalAlign: 'bottom',
                        y: -5,
                        style: {
                            color: '#606060'
                        }

                    }
                }]*/
        },
        {
            allowDecimals: true,
            opposite: true,
            /*labels: {
                style: {
                    color: '#87CEEB'
                }
            },*/
            title: {
                text: '<b>mm</b>',
                /*style: {
                  color: 'Black'
                  }*/
            },
            gridLineWidth: 0.1,
            plotBands: [
                { // Sin avisos
                    from: -Infinity,
                    to: Infinity,
                    color: 'rgba(255, 255, 255,0.8)'
                }],
            plotLines: [{
                value: 15,
                zIndex: 2,
                width: 2,
                color: 'rgb(255, 255, 116)',
                dashStyle: 'longdashdot',
                label: {
                    text: 'Alerta amarilla por lluvias',
                    verticalAlign: 'bottom',
                    y: -5,
                    style: {
                        color: 'rgba(27,28,28,0.5)'
                    }

                }
            }, {
                value: 30,
                zIndex: 2,
                width: 2,
                color: 'rgb(255, 181, 83)',
                dashStyle: 'longdashdot',
                label: {
                    text: 'Alerta naranja por lluvias',
                    verticalAlign: 'bottom',
                    y: -5,
                    style: {
                        color: 'rgba(27,28,28,0.5)'
                    }

                }
            }, {
                value: 60,
                zIndex: 2,
                width: 2,
                color: 'rgb(255, 84, 72)',
                dashStyle: 'longdashdot',
                label: {
                    text: 'Alerta roja por lluvias',
                    verticalAlign: 'bottom',
                    y: -5,
                    style: {
                        color: 'rgba(27,28,28,0.5)'
                    }

                }
            }]
        }],
        navigator: {
            adaptToUpdatedData: false,
            series: {
                type: 'line',
                data: []
            }
        },
        series: [{
            name: "Nivel de Río (m)",
            type: 'areaspline',
            fillColor: null,
            data: [],
            lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true,
            yAxis: 0
        }, {
            name: "Precipitación 1h (mm)",
            data: [],
            type: 'column',
            yAxis: 1
        }, {
            name: "Precipitación 1h en la cuenca (mm)",
            data: [],
            type: 'column',
            yAxis: 1
        }/*{
                name: "Nivel de Río predicho",
                data: [],
                dashStyle: 'Dash',
                lineColor: '#1B1C1C',
                showInNavigator: true
            }*/],
        legend: {
            enabled: false
        },
        exporting: {
            filename: new Date().toLocaleDateString() + '_' + nombreEstacion,
            scale: 1,
            sourceWidth: 1100,
            sourceHeight: 475,
            allowHTML: true,
            buttons: {
                contextButton: {
                    menuItems: menuChart
                }
            },
            chartOptions: {
                title: {
                    text: nombreEstacion
                },
                subtitle: {
                    text: 'Valores registrados durante las últimas 24 horas'
                },
            }
            /*chart: {
                zoomType: 'x',
                style: {
                    fontFamily: 'Roboto, sans-serif'
                },
                events: {
                    http://jsfiddle.net/d_paul/yo1jy1ku/
                    load: function() {
                        console.log("Altura", this.chartHeight);
                        this.renderer.image('../../../static/img/spd/logos/logo_alerta2_transparente.png')/*, (this.chartWidth-110),  (this.chartHeight-100), 100, 30)
                        .attr({
                            zIndex:1000, x:'calc(50% - 25%)', y:'40%', width:'50%',height:'22%', opacity:0.3
                        })
                        .add();
                    }
                }
            },*/

        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500,
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        }

    };
    return options;
}

function GraficoEmbalse(nombreEstacion) {
    var options = {
        chart: {
            zoomType: 'x',
            style: {
                fontFamily: 'Roboto, sans-serif'
            }
        },
        title: {
            text: 'Embalse'
        },
        subtitle: {
            text: 'Valores registrados durante las últimas 24 horas'
        },
        credits: {
            enabled: false
        },
        caption: {
            useHTML: true,
            text: '<p style="margin:0;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:35px; height:30px"><b> Datos sujetos a validación</b></p>'
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
            },
            global: {
                useUTC: false,
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            },
            title: {
                text: 'Fecha/Hora'
            },
        },
        yAxis: [{
            min: 0,
            allowDecimals: true,
            title: false,
            gridLineWidth: 0.1,
            labels: {
                style: {
                    color: '#9370DB'
                }
            },
            plotBands: [
                {
                    from: -Infinity,
                    to: Infinity,
                    color: 'rgba(255, 255, 255,0.8)'
                }
            ],
        }],
        navigator: {
            adaptToUpdatedData: false,
            series: {
                type: 'line',
                data: []
            }
        },
        series: [{
            name: "Volumen Porcentual (%)",
            type: 'line',
            dashStyle: 'Dash',
            data: [],
            color: '#9370DB',
            showInNavigator: true
        }],
        legend: {
            enabled: false
        },
        exporting: {
            filename: new Date().toLocaleDateString() + '_Embalse_' + nombreEstacion,
            scale: 1,
            sourceWidth: 1100,
            sourceHeight: 475,
            allowHTML: true,
            buttons: {
                contextButton: {
                    menuItems: menuChart
                }
            },
            chartOptions: {
                title: {
                    text: 'Embalse de ' + nombreEstacion
                },
                subtitle: {
                    text: 'Valores registrados durante las últimas 24 horas'
                },
            }
        },
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500,
                },
                chartOptions: {
                    plotOptions: {
                        series: {
                            marker: {
                                radius: 2.5
                            }
                        },
                        areaspline: {
                            fillOpacity: 0.5
                        }
                    }
                }
            }]
        },
        tooltip: {
            shared: true,
            crosshairs: true
        },

    };
    return options;
}



function GraficoSubcuenca(infoEstacion) {

    (async () => {

        // Obtengo el mapa de la subcuenca que deseo pintar
        const topology = await fetch(
            '../../../static/js/spd/shapefiles/subcuencas/subcuenca' + infoEstacion.info[0].Id + '.geojson'
        ).then(response => response.json());

        //https://cdn.jsdelivr.net/gh/highcharts/highcharts@1e9e659c2d60fbe27ef0b41e2f93112dd68fb7a3/samples/data/european-train-stations-near-airports.json
        Highcharts.getJSON('../../../private/datos/estaciones/pluvio/?id=' + infoEstacion.info[0].Id, function (data) {

            Highcharts.mapChart('highcharts-figure-subcuenca', {
                chart: {
                    map: topology,
                    backgroundColor: 'rgba(255, 255, 255, 0)',
                    style: {
                        fontFamily: 'Roboto, sans-serif'
                    }
                },
                title: {
                    text: 'Subcuenca'
                },
                subtitle: {
                    text: infoEstacion.info[0].Nombre
                },
                tooltip: {
                    headerFormat: '',
                    pointFormat: '<b>{point.InfoMarker.Nombre}</b><br>{point.InfoMarker.Tipo} - {point.InfoMarker.Red}<br>'
                        //+'Lat: {point.lat:.2f}, Lon: {point.lon:.2f}<br>'
                        + 'Estado: {point.Estado}'
                },
                navigation: {
                    buttonOptions: {
                        enabled: false
                    }
                },
                credits: {
                    enabled: false
                },
                plotOptions: {
                    mappoint: {
                        marker: {
                            fillColor: '#FFFFFF',
                            lineColor: '#000000',
                            lineWidth: 1,
                            symbol: 'triangle'
                        }
                    }
                },
                series: [{
                    name: 'Subcuenca',
                    borderColor: 'rgba(27,28,28, 0.5)',
                    nullColor: 'rgba(185,85,211,0.3)',
                    showInLegend: false,
                }, {
                    type: 'mappoint',
                    name: 'Estaciones',
                    showInLegend: false,
                    data: data.map((infoEstacion, index) => {

                        //Es un embalse
                        if (infoEstacion['T'] == 2) {
                            console.log(embalses)
                            var info = embalses.features.filter(function (feature) {
                                return feature.properties.Id == infoEstacion['Id'];
                            });
                        }
                        //No es un embalse
                        else {
                            var info = estaciones.features.filter(function (feature) {
                                return feature.properties.Id == infoEstacion['Id'];
                            });
                        }

                        return {
                            lat: infoEstacion['lat'],
                            lon: infoEstacion['lon'],
                            InfoMarker: infoEstacion,
                            Estado: DescripcionEstadoEstacion(info.length > 0 ? info[0].properties.Estado : 10),
                            marker: IconMarkerSubcuenca(infoEstacion, info.length > 0 ? info[0].properties.Estado : null)
                        }
                    }),
                    marker: {
                        enabled: true
                    }
                }]
            });
        });
    })();
}


function IconMarkerSubcuenca(infoEstacion, estado) {

    // Si se trata de un embalse
    if (infoEstacion['T'] == 2) {
        return {
            width: 25,
            height: 25,
            symbol: 'url(../../../static/img/spd/iconos/reservoir.png)'
        }
    }
    else {

        // Si es de la Red SPIDA
        if (infoEstacion['T'] == 5) {
            return {
                fillColor: colorIconMarkerEstacion(estado),
                lineColor: '#1B1C1C',
                lineWidth: 1,
                symbol: 'url(../../../static/img/spd/iconos/water_tower.png)'
            }
        }
        // Para el resto
        else {
            return {
                fillColor: colorIconMarkerEstacion(estado),
                lineColor: '#1B1C1C',
                lineWidth: 1,
                symbol: 'circle'
            }
        }
    }
};

