/*-------------------------------------------------------------------
# OPCIONES GENERALES DE CONFIGURACION DE UN GRAFICO
-------------------------------------------------------------------*/

//const { max } = require("./moment_locales.min");

Highcharts.setOptions({
    lang: {
        loading: '<i class="fa-solid fa-loader fa-spin-pulse"></i> Cargando...',
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
        resetZoom: '⤢',//'Reiniciar zoom',
        resetZoomTitle: 'Reiniciar zoom',
        thousandsSep: ",",
        decimalPoint: '.'
    },
    credits: {
        enabled: false
    },
    chart: {
        zoomType: 'xy',
        panning: {
            enabled: true,
            type: 'xy'
        },
        panKey: 'shift',
        plotBackgroundImage: 'http://alerta2.es/static/img/spd/logos/logo_alerta2_transparente.png',
        style: {
            fontFamily: 'Roboto, sans-serif'
        }
    },
    plotOptions: {
        global: {
            useUTC: false,
        }
    }
});


/*EXPORT TABLE
https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/studies/exporting-table-html
http://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/studies/exporting-table/
https://jsfiddle.net/BlackLabel/x5y9ephv/
https://jsfiddle.net/nzj53smb/1/
*/

Highcharts.getSVG = function (charts) {
    var svgArr = [],
        top = 0,
        width = 0,
        endWidth = 0;

    var graficos = Highcharts.charts;
    graficos.forEach(function (chart) {
        if (charts.includes(chart.renderTo.id)) {

            var svg = chart.getSVG({
                chart: {
                    backgroundColor: "#fff",
                    plotBackgroundImage: null,
                    width: 1200,
                    height: 500,
                }
            }
            /*{
                yAxis: [{
                    plotBands: [
                        { // Sin avisos
                            from: -Infinity,
                            to: +Infinity,
                            color: 'rgba(255, 255, 255,0.8)'
                        }
                    ]
                }],
                caption:{
                    text: null
                },
                chart:{
                    //backgroundColor: "#fff",
                    //plotBackgroundImage: null
                }
            }*/),
                // Get width/height of SVG for export
                svgWidth = +svg.match(
                    /^<svg[^>]*width\s*=\s*\"?(\d+)\"?[^>]*>/
                )[1],
                svgHeight = +svg.match(
                    /^<svg[^>]*height\s*=\s*\"?(\d+)\"?[^>]*>/
                )[1];

            svg = svg.replace(
                '<svg',
                '<g transform="translate(' + width + ', ' + top + ')" '
            );

            svg = svg.replace('</svg>', '</g>');

            width += svgWidth;
            endWidth = Math.max(endWidth, width)

            if (width === svgWidth) {
                width = 0;
                top += svgHeight;
            }

            svgArr.push(svg);
        }
    });

    /*Highcharts.each(charts, function (chart) {
        var svg = chart.getSVG(),
            // Get width/height of SVG for export
            svgWidth = +svg.match(
                /^<svg[^>]*width\s*=\s*\"?(\d+)\"?[^>]*>/
            )[1],
            svgHeight = +svg.match(
                /^<svg[^>]*height\s*=\s*\"?(\d+)\"?[^>]*>/
            )[1];

        svg = svg.replace(
            '<svg',
            '<g transform="translate(' + width + ', ' + top + ')" '
        );

        svg = svg.replace('</svg>', '</g>');

        width += svgWidth;
        endWidth = Math.max(endWidth, width)

        if (width === 3 * svgWidth) {
            width = 0;
            top += svgHeight;
        }

        svgArr.push(svg);
    });*/
    //top += svgHeight;
    return '<svg height="' + top + '" width="' + endWidth +
        '" version="1.1" xmlns="http://www.w3.org/2000/svg">' +
        svgArr.join('') + '</svg>';
};

/**
 * Create a global exportCharts method that takes an array of charts as an
 * argument, and exporting options as the second argument
 */
Highcharts.exportCharts = function (charts, options) {

    //console.log("ARRAY CHARTS", charts)

    /*var arr_charts = [];

    charts.forEach(async (chartId) => {
        arr_charts.push(Highcharts.charts.find(c => c.renderTo.id == chartId));
    })*/

    //console.log("ELEMENTS CHARTS", arr_charts)

    // Merge the options
    options = Highcharts.merge(Highcharts.getOptions().exporting, options);

    // Post to export server
    Highcharts.post(options.url, {
        filename: options.filename || 'chart',
        type: options.type,
        width: options.width,
        svg: Highcharts.getSVG(charts)
    });
};


function LoadChart_ICA(info_estacion, contaminantes, FLAGS, ICA, elementChartICA) {

    map.spin(true, spinner_options_sidebar);

    Highcharts.chart(elementChartICA, {
        chart: {
            events: {
                load() {

                    if (!this.renderer.forExport) {
                        
                        if (contaminantes != undefined) {
                            contaminantes.forEach(async (contaminante) => {
                                const info_ICA = PropiedadesICA(contaminante.UTC, contaminante.Valor);
                                LoadData_Contaminante(
                                    info_estacion, // Informacion de la estación
                                    contaminante, // Informacion del contaminante
                                    info_ICA, // Indice de calidad del aire
                                    FLAGS, // Flags
                                    ICA, // Indices de Calidad del Aire
                                    "sparkline-" + contaminante.Acronimo, // Id del sparkline
                                    "chart-contaminante-" + contaminante.Acronimo, // Id del gráfico del contaminante
                                    "chart-ICA-" + contaminante.Acronimo, //Id del grafico linear para mostrar el rango del Índice de Calidad del Aire
                                    this
                                );
                            })
                        }
                        
                        map.spin(false);
                    }
                }
            }
        },
        boost: {
            useGPUTranslations: true,
            seriesThreshold: 2// Chart-level boost when there are more than 5 series in the chart
        },
        title: {
            text: "Índice de Calidad del Aire"
        },
        subtitle: {
            text: 'Evaluación de la calidad del aire para los diversos contaminantes atmosféricos durante las últimas 24 horas'
        },
        caption: {
            useHTML: true,
            text: `<p style="margin:0;display: inline-block; vertical-align: middle;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:30px; height:25px"><b> Datos sujetos a validación </b><a class="infoICA" href="#">+ Informacion <i class="fas fa-mouse-pointer"></i></a></p>`
        },
        plotOptions: {
            spline: {
                lineWidth: 4,
                states: {
                    hover: {
                        lineWidth: 5
                    }
                },
                marker: {
                    enabled: false
                }
            },
            series: {
                marker: {
                    enabled: false,
                    states: {
                        hover: {
                            enabled: false
                        }
                    }
                }
            }
        },
        tooltip: {
            shared: true,
            crosshairs: true
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
            max: 400, //(max_valor <= 400) ? 400 : Math.ceil(max_valor),
            gridLineColor: 'transparent',
            title: {
                text: null
            },
            plotBands: [{
                from: 0,
                to: 51,
                label: {
                    text: 'Buena',
                    align: 'center',
                    verticalAlign: 'middle',
                    style: {
                        'color': '#fff'//'#666666'
                    }
                },
                color: {
                    linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                    stops: [
                        [0, 'rgba(109, 128, 254,0.6)'],
                        [1, 'rgba(35, 210, 253,0.6)']
                    ]
                }
            }, {
                from: 51,
                to: 101,
                label: {
                    text: 'Razonablemente buena',
                    align: 'center',
                    verticalAlign: 'middle',
                    style: {
                        'color': '#fff'//'#666666'
                    }
                },
                color: {
                    linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                    stops: [
                        [0, 'rgba(0,172,193,0.6)'],
                        [1, 'rgba(41,244,153,0.6)']
                    ]
                }
            }, {
                from: 101,
                to: 151,
                label: {
                    text: 'Regular',
                    align: 'center',
                    verticalAlign: 'middle',
                    style: {
                        'color': '#fff'//'#666666'
                    }
                },
                color: {
                    linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                    stops: [
                        [0, 'rgba(205,220,57,0.6)'],
                        [1, 'rgba(253,216,53,0.6)']
                    ]
                }
            }, {
                from: 151,
                to: 201,
                label: {
                    text: 'Desfavorable',
                    align: 'center',
                    verticalAlign: 'middle',
                    style: {
                        'color': '#fff'//'#666666'
                    }
                },
                color: {
                    linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                    stops: [
                        [0, 'rgba(198,40,40,0.6)'],
                        [1, 'rgba(229,115,115,0.6)']
                    ]
                }
            }, {
                from: 201,
                to: 300,
                label: {
                    text: 'Muy desfavorable',
                    align: 'center',
                    verticalAlign: 'middle',
                    style: {
                        'color': '#fff'//'#666666'
                    }
                },
                color: {
                    linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                    stops: [
                        [0, 'rgba(123,36,28,0.6)'],
                        [1, 'rgba(203,67,53,0.6)']
                    ]
                }
            }, {
                from: 300,
                to: Infinity,
                label: {
                    text: 'Extremadamente desfavorable',
                    align: 'center',
                    verticalAlign: 'middle',
                    style: {
                        'color': '#fff'//'#666666'
                    }
                },
                color: {
                    linearGradient: { x1: 1, y1: 1, x2: 1, y2: 0 },
                    stops: [
                        [0, 'rgba(112, 124, 255, 0.6)'],
                        [1, 'rgba(250, 129, 232, 0.6)']
                    ]
                }
            }]
        }],
        series: [{
            showInLegend: false,
            data: [],
            visible: false
        }],
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            itemMarginTop: 10,
            itemMarginBottom: 10
        },
        exporting: {
            filename: `${moment().format("YYMMDD_HHmmss")}_ICA_${info_estacion.Nombre}`,
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
                    text: `${info_estacion.Nombre}`
                },
                subtitle: {
                    text: `Evaluación de la calidad del aire para los diversos contaminantes atmosféricos emitidos por el foco ${info_estacion.Foco} durante las últimas 24 horas a fecha ${moment().format("D MMM, YYYY")}`
                },
                caption: {
                    useHTML: true,
                    text: `<p style="margin:0;display: inline-block; vertical-align: middle;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:25px; height:20px"> Datos sujetos a validación</p>`
                },
            }
        }
    })

    // Mostrar el panel de información de los Flags
    $('.infoICA').click(function (e) { MostrarPanelICA(null, ICA); return e.preventDefault(); });
}

function LoadData_ActividadAnual(info_estacion, elementChartActividad) {

    map.spin(true, spinner_options_sidebar);

    $.ajax({
        type: "GET",
        dataType: "json",
        cache: false,
        url: url_getJsonActividadAnual,
        data: {
            i: info_estacion.I,
            y: 2022 //moment().year()
        },
        success: function (data) {
            
        },
        error: function () {
            console.log(`Error getJSON DATA Actividad Industrial ${moment().year()} ${info_estacion.Nombre} - ${info_estacion.Foco}`);
        },
        complete: function (response) {
            const data = (response.responseJSON==undefined) ? [] : response.responseJSON
            LoadChart_ActividadAnual(info_estacion, elementChartActividad, data);
            map.spin()
        }

    });
}

function LoadChart_ActividadAnual(info_estacion, elementChartActividad, data) {

    //Highcharts.getJSON(url_getActividadAnual + '?i=' + info_estacion.I, function (data) {
    //Highcharts.getJSON("http://127.0.0.1:8000/media/veiex/2022_3053_global.json", function (data) {

    const chart = Highcharts.ganttChart(elementChartActividad, {
        chart: {
            zoomType: 'x',
            panning: {
                enabled: true,
                type: 'x'
            },
            plotBackgroundImage: 'http://alerta2.es/static/img/spd/logos/logo_alerta2_transparente.png',
            events: {
                load() {

                    if (!this.renderer.forExport) {

                        const chart = this;
                        chart.showLoading('<i class="fa-solid fa-loader fa-spin-pulse"></i> Cargando...');

                        setTimeout(function () {

                            if (data.fecha_hora != null && data.year != null && data.valores != null && data.valores.length > 0) {

                                var firstDay = moment(data.year + '-01-01T00:00:00Z');
                                var lastDay = moment(data.year + '-12-31T23:59:59Z');

                                //Actualizo las propiedades del grafico
                                chart.update({
                                    xAxis: {
                                        min: firstDay,
                                        max: lastDay,
                                        lineColor: "rgb(204, 214, 235)"
                                    },
                                    yAxis: {
                                        lineColor: "rgb(204, 214, 235)"
                                    },
                                    caption: {
                                        useHTML: true,
                                        text: `(*) Última actualización ${moment(data.fecha_hora).format("D MMM, YYYY HH:SS")} h`,
                                    }
                                })

                                //Serie de datos
                                chart.series[0].setData(data.valores.map(function (point) {
                                    return {
                                        'start': moment(point.Start).valueOf(),
                                        'end': (moment(point.End).valueOf() > lastDay.valueOf()) ? lastDay.valueOf() : moment(point.End).valueOf(),
                                        'name': point.Propiedades.Nombre,
                                        'color': point.Propiedades.Color
                                    };
                                }))

                                chart.hideLoading();

                            }
                            else {
                                chart.update({
                                    xAxis: {
                                        lineColor: "transparent"
                                    },
                                    yAxis: {
                                        lineColor: "transparent"
                                    },
                                    rangeSelector: {
                                        enabled: false
                                    },
                                    navigator: {
                                        enabled: false
                                    },
                                    scrollbar: {
                                        enabled: false
                                    },
                                    exporting: {
                                        enabled: false
                                    }
                                })

                                //Sin datos
                                chart.showLoading('<i class="fa-solid fa-hexagon-exclamation" style="color:red;"></i> Sin datos')
                            }

                            map.spin(false);

                        }, 2000);
                    }
                }
            }
        },
        boost: {
            useGPUTranslations: true,
            seriesThreshold: 1// Chart-level boost when there are more than 5 series in the chart
        },
        title: {
            text: 'Actividad industrial'
        },
        subtitle: {
            text: `Periodo de funcionamiento efectivo durante el año ${moment().year()}`
        },
        xAxis: [{
            lineColor: "transparent",
            type: 'datetime',
            dateTimeLabelFormats: {
                millisecond: '%e. %b %H:%M',
                second: '%e. %b %H:%M',
                minute: '%e. %b %H:%M',
                hour: '%e. %b %H:%M',
                day: '%e. %b',
                week: '%e. %b',
                month: {
                    list: ['%B', '%b', '%m']
                },
                year: '%Y'
            },
            labels: {
                align: 'center'
            }
        }],
        yAxis: {
            uniqueNames: true,
            lineColor: "transparent"
        },
        navigator: {
            enabled: true,
            liveRedraw: true,
            xAxis: {
                dateTimeLabelFormats: {
                    day: '%Y',
                    week: '%Y',
                    month: '%Y',
                    year: '%Y'
                }
            }
        },
        scrollbar: {
            enabled: true
        },
        rangeSelector: {
            enabled: true,
            selected: 3,
            allButtonsEnabled: true,
            inputEnabled: true,
            buttons: [{
                type: 'all',
                count: 1,
                text: 'Todo'
            }, {
                type: 'month',
                count: 6,
                text: '6m'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'day',
                count: 1,
                text: '1d'
            }]

        },
        series: [{
            boostThreshold: 1,
            name: 'Actividad industrial',
            dataLabels: {
                verticalAlign: 'top',
                inside: false
            },
            data: []
        }],
        /*tooltip: {
            dateTimeLabelFormats: {
              millisecond: "%A, %b %e, %H:%M:%S.%L",
              second: "%A, %b %e, %H:%M:%S",
              minute: "%A, %b %e, %H:%M",
              hour: "%A, %b %e, %H:%M",
              day: "%A, %b %e, %Y",
              week: "TO CHANGE - Week from %A, %b %e, %Y",
              month: "%B %Y",
              year: "%Y"
            }
        },*/
        exporting: {
            filename: `${moment().format("YYMMDD")}_Actividad_Industrial_${info_estacion.Nombre}`,
            buttons: {
                contextButton: {
                    menuItems: menuChart//["viewFullscreen", "printChart", "separator", "downloadPNG", "downloadJPEG", "downloadSVG", "downloadPDF"]
                }
            },
            chartOptions: {
                title: {
                    text: `${info_estacion.Nombre} (${info_estacion.Foco})`
                },
                subtitle: {
                    text: `Actividad industrial durante el año ${moment().year()}`
                },
                chart: {
                    events: {
                        load: function () {
                            this.yAxis[0].addPlotBand({
                                from: -Infinity,
                                to: Infinity,
                                color: 'rgba(255,255,255,0.5)'
                            });
                        }
                    }
                }
            },
            csv: {
                columnHeaderFormatter: function (item, key) {

                    if (key == 'end') {
                        return {
                            topLevelColumnTitle: 'Actividad Industrial',
                            columnTitle: 'Fecha/Hora Final'
                        };
                    }
                    if (key == 'start') {
                        return {
                            topLevelColumnTitle: 'Actividad Industrial',
                            columnTitle: 'Fecha/Hora Inicial'
                        };
                    }
                    if (key == 'y') {
                        return {
                            topLevelColumnTitle: 'Actividad Industrial',
                            columnTitle: 'Estado'
                        };
                    }
                    return false
                }
            }
        }
    });

    Highcharts.addEvent(chart, 'exportData', function (e) {
        e.dataRows.forEach(function (el) {
            el.splice(0, 1);
        });
    });

    // Ajustar marca de agua de los graficos
    document.querySelectorAll('.highcharts-root > image')
        .forEach((function (x) { x.setAttribute("preserveAspectRatio", "meet"); }))
    //})
}

function LoadData_Contaminante(info_estacion, info_data, info_ICA, FLAGS, ICA, elementSparkline, elementChartContaminante, elementChartICA, elementChartICAGlobal) {

    $.ajax({
        type: "GET",
        dataType: "json",
        url: url_getDatos,
        data: {
            i: info_estacion.I,
            c: info_data.C,
            h: 24,
            dt: info_data.UTC
        },
        cache: false,
        success: function (data) {

            if (data.length > 0) {

                //Añado la serie al grafico ICA global
                elementChartICAGlobal.addSeries({
                    boostThreshold: 1,
                    name: info_data.Acronimo,
                    keys: ['Valor', 'Flag'],
                    data: data.map(function (point) {
                        return { 'x': moment(point.LOCAL).valueOf(), 'y': point.valor, 'Valor': point.valor, 'Flag': point.Flag }; //'Estado': point.Estado, 'color': point.Color 
                    })
                });

                //elementChartICAGlobal.redraw()
            }

            LoadChart_Contaminante(info_estacion, info_data, info_ICA, FLAGS, ICA, elementSparkline, elementChartContaminante, elementChartICA, data);
        },
        error: function () {
            console.log(`Error getJSON DATA Maximos Diarios ${info_data.Parametro} - ${info_estacion.Nombre} - ${info_estacion.Foco}`);
        },
        complete: function () {

        }

    });
}


function LoadChart_Contaminante(info_estacion, info_data, info_ICA, FLAGS, ICA, elementSparkline, elementChartContaminante, elementChartICA, data) {
    //Highcharts.getJSON(url_getDatos + '?i=' + info_estacion.I + '&c=' + info_data.C + '&h=24&dt=' + info_data.UTC, function (data) {

    map.spin(true, spinner_options_sidebar);

    // Pinto el sparkline 
    Highcharts.chart(elementSparkline, {
        chart: {
            zoomType: null,
            panning: null,
            margin: [0, 0, 0, 0],
            style: {
                overflow: 'visible'
            },
            backgroundColor: 'rgba(0,0,0,0)',
            events: {
                load() {

                    if (!this.renderer.forExport) {
                        if (data != null && data.length > 0) {
                            const chart = this;
                            chart.series[0].setData(
                                data.slice(-30).map(function (point) { // Cojo los ultimos 30 valores
                                    return [point.LOCAL, point.valor]
                                })
                            )
                        }
                    }
                }
            }
        },
        title: {
            text: ''
        },
        legend: {
            enabled: false
        },
        xAxis: {
            labels: {
                enabled: false
            },
            tickLength: 0,
            type: 'datetime',
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%b. %e',
                week: '%b. %e',
                month: '%b. %y',
                year: '%Y'
            }
        },
        yAxis: {
            title: {
                text: null
            },
            maxPadding: 0,
            minPadding: 0,
            gridLineWidth: 0,
            ticks: false,
            endOnTick: false,
            labels: {
                enabled: false
            }
        },
        tooltip: {
            enabled: false
        },
        plotOptions: {
            series: {
                enableMouseTracking: false,
                lineWidth: 1,
                shadow: false,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                marker: {
                    radius: 0
                }
            }
        },
        exporting: {
            enabled: false
        },
        series: [{
            type: 'line',
            color: '#fff',
            data: []
        }]
    });

    let max_valor = 0;

    if (data != null && data.length > 0) {
        max_valor = Math.max.apply(Math, data.map(o => o.valor));
    }

    $(function () {

        // Highcharts Linear-Gauge series plugin
        // https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/studies/linear-gauge-series

        (function (H) {
            H.seriesType('lineargauge', 'column', null, {
                setVisible: function () {
                    H.seriesTypes.column.prototype.setVisible.apply(this, arguments);
                    if (this.markLine) {
                        this.markLine[this.visible ? 'show' : 'hide']();
                    }
                },
                drawPoints: function () {
                    // Draw the Column like always
                    H.seriesTypes.column.prototype.drawPoints.apply(this, arguments);

                    // Add a Marker
                    var series = this,
                        chart = this.chart,
                        inverted = chart.inverted,
                        xAxis = this.xAxis,
                        yAxis = this.yAxis,
                        point = this.points[0], // we know there is only 1 point
                        markLine = this.markLine,
                        ani = markLine ? 'animate' : 'attr';

                    // Hide column
                    point.graphic.hide();

                    if (!markLine) {
                        var path = inverted ? ['M', 0, 0, 'L', -5, -5, 'L', 5, -5, 'L', 0, 0, 'L', 0, 0 + xAxis.len] : ['M', 0, 0, 'L', -5, -5, 'L', -5, 5, 'L', 0, 0, 'L', xAxis.len, 0];
                        markLine = this.markLine = chart.renderer.path(path)
                            .attr({
                                fill: series.color,
                                stroke: series.color,
                                'stroke-width': 1
                            }).add();
                    }
                    markLine[ani]({
                        translateX: inverted ? xAxis.left + yAxis.translate(point.y) : xAxis.left,
                        translateY: inverted ? xAxis.top : yAxis.top + yAxis.len - yAxis.translate(point.y)
                    });
                }
            });
        }(Highcharts));

        Highcharts.chart(elementChartICA, {
            chart: {
                zoomType: null,
                panning: null,
                type: 'lineargauge',
                inverted: true,
                height: 100,
                backgroundColor: 'transparent',
                events: {
                    load() {

                        if (!this.renderer.forExport) {

                            if (data != null && data.length > 0) {
                                const chart = this;
                                chart.series[0].setData(
                                    data.slice(-1).map(function (point) { // Cojo el último valor
                                        return [point.valor]
                                    })
                                )
                            }

                        }
                    }
                }
            },
            title: {
                text: 'Índice de calidad del aire',
                style: {
                    color: '#fff'
                }
            },
            exporting: {
                enabled: false
            },
            xAxis: {
                lineColor: 'transparent',
                labels: {
                    enabled: false
                },
                tickLength: 0
            },
            yAxis: {
                min: 0,
                max: (max_valor <= 400) ? 400 : Math.ceil(max_valor),
                tickLength: 0,
                tickWidth: 0,
                tickColor: 'transparent',
                gridLineColor: 'transparent',
                gridLineWidth: 0,
                minorTickInterval: 0,
                minorTickWidth: 0,
                minorTickLength: 0,
                minorGridLineWidth: 0,
                title: null,
                labels: {
                    format: '{value}',
                    style: {
                        color: '#fff'
                    }
                },
                plotBands: [{
                    text: 'Buena',
                    from: 0,
                    to: 51,
                    color: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(109, 128, 254)'],
                            [1, 'rgb(35, 210, 253)']
                        ]
                    },
                    //color: 'rgba(35,210,253,0.8)', // Buena
                    className: 'plotband-cursor',
                    events: {
                        click: function (e) {
                            MostrarPanelICA(info_ICA, ICA)
                        }
                    }
                }, {
                    text: "Razonablemente buena",
                    from: 51,
                    to: 101,
                    color: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                        stops: [
                            [0, '#00ACC1'],
                            [1, '#29f499']
                        ]
                    },
                    //color: 'rgba(41,244,153,0.8)', // Razonablemente buena
                    className: 'plotband-cursor',
                    events: {
                        click: function (e) {
                            MostrarPanelICA(info_ICA, ICA);
                        }
                    }
                }, {
                    text: "Regular",
                    from: 101,
                    to: 151,
                    color: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                        stops: [
                            [0, '#CDDC39'],
                            [1, '#FDD835']
                        ]
                    },
                    //color: 'rgba(253,216,53,0.8)', //Regular
                    className: 'plotband-cursor',
                    events: {
                        click: function (e) {
                            MostrarPanelICA(info_ICA, ICA);
                        }
                    }
                }, {
                    text: "Desfavorable",
                    from: 151,
                    to: 201,
                    color: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                        stops: [
                            [0, '#C62828'],
                            [1, '#E57373']
                        ]
                    },
                    //color: 'rgba(255, 0, 0,0.8)', //Desfavorable
                    className: 'plotband-cursor',
                    events: {
                        click: function (e) {
                            MostrarPanelICA(info_ICA, ICA);
                        }
                    }
                }, {
                    text: "Muy desfavorable",
                    from: 201,
                    to: 300,
                    color: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                        stops: [
                            [0, '#7B241C'],
                            [1, '#CB4335']
                        ]
                    },
                    //color: 'rgba(139,0,0,0.8)', //Muy desfavorable
                    className: 'plotband-cursor',
                    tooltipText: 'Muy desfavorable',
                    events: {
                        click: function (e) {
                            MostrarPanelICA(info_ICA, ICA);
                        }
                    }
                }, {
                    text: "Extremadamente desfavorable",
                    from: 300,
                    to: Infinity,
                    color: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                        stops: [
                            [0, 'rgb(112, 124, 255)'],
                            [1, 'rgb(250, 129, 232)']
                        ]
                    },
                    //color: 'rgba(175,122,197,0.8)', //Extremadamente desfavorable
                    className: 'plotband-cursor',
                    tooltipText: 'Extremadamente desfavorable',
                    events: {
                        click: function (e) {
                            MostrarPanelICA(info_ICA, ICA);
                        }
                    }
                }]
            },
            legend: {
                enabled: false
            },
            tooltip: {
                enabled: false
            },
            series: [{
                data: [-1],
                color: '#000000',
                dataLabels: {
                    enabled: true,
                    align: 'center',
                    format: '{point.y} ' + info_data.Unidades
                }
            }]

        }, // Add some life

            function (chart) {

            });
    });

    //Pinto el grafico del contaminante
    Highcharts.chart(elementChartContaminante, {
        chart: {
            zoomType: 'xy',
            plotBackgroundImage: 'http://alerta2.es/static/img/spd/logos/logo_alerta2_transparente.png',
            style: {
                fontFamily: 'Roboto, sans-serif'
            },
            events: {
                load() {

                    if (!this.renderer.forExport) {

                        const chart = this;
                        chart.showLoading();

                        setTimeout(function () {
                            if (data != null && data.length > 0) {

                                //Serie de datos (Periodo de actividad)
                                chart.series[0].setData(data.map(function (point) {
                                    if (point.Flag == 'I') {
                                        return { 'x': moment(point.LOCAL).valueOf(), 'y': null, 'Valor': null, 'Flag': null, 'Estado': null, 'segmentColor': null, 'color': null };
                                    }
                                    else {
                                        return { 'x': moment(point.LOCAL).valueOf(), 'y': point.valor, 'Valor': point.valor, 'Flag': point.Flag, 'Estado': point.Estado, 'segmentColor': point.Color, 'color': point.Color };
                                    }
                                }))

                                //Serie de datos (Periodo de inactividad)
                                chart.series[1].setData(data.map(function (point) {
                                    if (point.Flag == 'I') {
                                        return { 'x': moment(point.LOCAL).valueOf(), 'y': point.valor, 'Valor': point.valor, 'Flag': point.Flag, 'Estado': point.Estado, 'segmentColor': point.Color, 'color': point.Color };
                                    }
                                    else {
                                        return { 'x': moment(point.LOCAL).valueOf(), 'y': null, 'Valor': null, 'Flag': null, 'Estado': null, 'segmentColor': null, 'color': null };
                                    }
                                }))

                                //VLE
                                if (info_data.VLE != null) {
                                    chart.yAxis[0].addPlotLine({
                                        value: info_data.VLE,
                                        zIndex: 2,
                                        width: 2,
                                        color: 'rgb(255, 0, 0)',
                                        dashStyle: 'Solid',//'longdashdot',
                                        label: {
                                            text: 'VLE',
                                            verticalAlign: 'bottom',
                                            y: -5,
                                            style: {
                                                color: 'rgba(255, 0, 0, 0.6)'
                                            }
                                        }
                                    });
                                }

                                chart.hideLoading();
                            }
                            else {
                                //Sin datos
                                chart.showLoading('<i class="fa-solid fa-hexagon-exclamation" style="color:red;"></i> Sin datos')
                            }

                            map.spin(false, spinner_options_sidebar);

                        }, 2000);


                    }
                }
            }
        },
        title: {
            text: info_data.Parametro
        },
        subtitle: {
            text: 'Valores registrados durante las últimas 24 horas'
        },
        caption: {
            useHTML: true,
            text: '<p style="margin:0; display: inline-block; vertical-align: middle;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:30px; height:25px"><b> Datos sujetos a validación </b><a class="infoFlags" href="#">+ Informacion <i class="fas fa-mouse-pointer"></i></a></p>'
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat:
                '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: "</table>",
            shared: true,
            useHTML: true,
            pointFormatter: function (object) {
                return `<h5 style="font-family:'${"Bradley Hand ITC"}'; font-weight: bold; margin-left: auto; margin-right:auto">${info_estacion.Nombre}</h5>` +
                    `<p><b style="font-size:16px;">${this.y} ${info_data.Unidades}</b> *(${info_data.Acronimo})<br>` +
                    //Highcharts.dateFormat('%e %b %Y', this.x) + ', ' +
                    //Highcharts.dateFormat('%H:%M', this.x) + ' h</p>' +
                    //'<p><b>Foco:</b> ' + info_estacion.Foco + '</p>' +
                    `<p><i class="fas fa-circle" style="color:rgb(255, 0, 0)"></i><b>  VLE ${info_data.VLE} ${info_data.Unidades}</b></p>` +
                    `<p style="font-size:10px; margin-bottom:0px;">(*) ${this.Estado}</p>`;
            }
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
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
                text: '<b>' + info_data.Acronimo + ' (' + info_data.Unidades + ')</b>',
            },
            gridLineWidth: 0.1
        }],
        /*navigator: {
            adaptToUpdatedData: false,
            series: {
                type: 'line',
                data: []
            }
        },*/
        series: [{
            name: "Periodo actividad", //info_data.Parametro,
            keys: ['Valor', 'Flag'],
            //type: 'areaspline',
            type: 'coloredline',
            data: [],
            //lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true,
        }, {
            name: "Periodo inactividad", //info_data.Parametro,
            keys: ['Valor', 'Flag'],
            dashStyle: 'ShortDash',
            //type: 'areaspline',
            type: 'coloredline',
            data: [],
            //lineColor: 'rgb(17, 43, 115)',
            showInNavigator: true,
        }/*https://jsfiddle.net/3169Lcdr/, {
                name: "Flag",
                data: [],
                type: 'areaspline',
                lineWidth: 0,
                linkedTo: ':previous',
                color: '#7cbaff',
                marker: {
                    enabled: false
                }
            },*/],
        legend: {
            enabled: true
        },
        exporting: {
            filename: `${moment().format("YYMMDD_HHmmss")}_${info_data.Parametro}_${info_estacion.Nombre}`,
            scale: 1,
            sourceWidth: 1200,
            sourceHeight: 540,
            allowHTML: true,
            buttons: {
                contextButton: {
                    menuItems: menuChart
                }
            },
            chartOptions: {
                title: {
                    text: info_estacion.Nombre
                },
                subtitle: {
                    text: `Valores de ${info_data.Parametro} registrados por el foco ${info_estacion.Foco} durante las últimas 24 horas a fecha ${data.slice(-1).map(function (point) { return moment(point.LOCAL).format("D MMM, YYYY HH:SS") })} h`
                },
                chart: {
                    events: {
                        load: function () {
                            this.yAxis[0].addPlotBand({
                                from: -Infinity,
                                to: Infinity,
                                color: 'rgba(255,255,255,0.5)'
                            });
                        }
                    }
                },
                caption: {
                    useHTML: true,
                    text: `<p style="margin:0;display: inline-block; vertical-align: middle;"><img src="http://alerta2.es/static/img/spd/iconos/aviso.png" style="width:25px; height:20px"> Datos sujetos a validación<br>
                    (*) Valor Límite de Emisión (VLE) ${info_data.VLE} ${info_data.Unidades}</p>`
                }
            }
        }
    })

    // Ajustar marca de agua de los graficos
    document.querySelectorAll('.highcharts-root > image')
        .forEach((function (x) { x.setAttribute("preserveAspectRatio", "meet"); }))

    // Mostrar el panel de información de los Flags
    $('.infoFlags').click(function (e) { e.preventDefault(); MostrarPanelFlags(FLAGS); return false; });


    //})


}

function getPointCategoryName(point, dimension) {
    var series = point.series,
        isY = dimension === 'y',
        axis = series[isY ? 'yAxis' : 'xAxis'];
    return axis.categories[point[isY ? 'y' : 'x']];
}


function LoadData_Promedios(info_estacion, info_data, elementChartGauge) {

    map.spin(true, spinner_options_sidebar);

    $.ajax({
        type: "GET",
        dataType: "json",
        url: url_getPromedios,
        data: {
            i: info_estacion.I,
            c: info_data.C,
            vle: info_data.VLE
        },
        cache: false,
        success: function (data) {
            LoadGauge_Promedios(info_estacion, info_data, elementChartGauge, data);
        },
        error: function () {
            console.log("Error getJSON DATA Promedios semihorarios existentes");
        },
        complete: function () {
            map.spin(false);
        }

    });
}

function LoadGauge_Promedios(info_estacion, info_data, elementChartGauge, data) {

    map.spin(true, spinner_options_sidebar);

    var html_icon_sh_100vle = (data.cond_semihorario_100vle == true) ? '<i class="fa-solid fa-thumbs-up" style="font-size:25px; color:#55BF3B;"></i>' : '<i class="fa-solid fa-thumbs-down" style="font-size:25px; color:#CB4335;"></i>';
    var html_icon_sh_125vle = (data.cond_valor_125vle == true) ? '<i class="fa-solid fa-thumbs-up" style="font-size:25px; color:#55BF3B;"></i>' : '<i class="fa-solid fa-thumbs-down" style="font-size:25px; color:#CB4335;"></i>';
    var html_icon_d_100vle = (data.cond_diario_100vle == true) ? '<i class="fa-solid fa-thumbs-up" style="font-size:25px; color:#55BF3B;"></i>' : '<i class="fa-solid fa-thumbs-down" style="font-size:25px; color:#CB4335;"></i>';

    var estado = '';
    var color = 'transparent'
    const arr = (data.cond_diario_100vle != null) ? [data.cond_valor_125vle, data.cond_semihorario_100vle, data.cond_diario_100vle] : [data.cond_valor_125vle, data.cond_semihorario_100vle]
    const count = arr.filter(Boolean).length;
    if (count == arr.length) {
        estado = 'Cumple'; // Cumple todos los criterios
        color = '#55BF3B'; // verde
    }
    else if (count == 0) {
        estado = 'No cumple'; // No Cumple ningun criterio
        color = '#CB4335'; // rojo
    }
    else {
        estado = 'No cumple'; // No cumple algún criterio
        color = '#F1C40F'; // amarillo
    }
    //var estado = (data.cond_valor_125vle == true && data.cond_semihorario_100vle == true) ? 'Cumple' : 'No cumple';


    var html_caption = (data.cond_diario_100vle != null) ?
        `<p class="caption-gauge">(*) En el caso del contaminante <span style="color: white"><b>${info_data.Parametro}
    (${info_data.Acronimo})</b></span> monitorizado en continuo, se considera que ha respetado el Valor Límite de Emisión 
    (VLE), para las horas de funcionamiento dentro de un año natural si <span style="color: white"><sup>[1]</sup> al menos el 94% de los
    valores medios semihorarios validados del año no supera el <b>100 % del VLE (${info_data.VLE} ${info_data.Unidades})</b></span>
    establecido, <span style="color: white"><sup>[2]</sup> ningún valor medio semihorario validado supera el <b>125 % del VLE
    (${info_data.VLE * 1.25} ${info_data.Unidades})</b></span> y <span style="color: white"><sup>[3]</sup> ningún valor medio diario
    supera el 100 % del VLE (${info_data.VLE} ${info_data.Unidades})</b></span><p>`
        :
        `<p class="caption-gauge">(*) En el caso del contaminante <span style="color: white"><b>${info_data.Parametro}
    (${info_data.Acronimo})</b></span> monitorizado en continuo, se considera que ha respetado el Valor Límite de Emisión 
    (VLE), para las horas de funcionamiento dentro de un año natural si <span style="color: white"><sup>[1]</sup> al menos el 94% de los
    valores medios semihorarios validados del año no supera el <b>100 % del VLE (${info_data.VLE} ${info_data.Unidades})</b></span>
    establecido y <span style="color: white"><sup>[2]</sup> ningún valor medio semihorario validado supera el <b>125 % del VLE
    (${info_data.VLE * 1.25} ${info_data.Unidades})</b></span><p>`;

    var html_gauge = (data.cond_diario_100vle != null) ?
        `<div style="text-align:center; font-size:25px; color:white;">
    <span style="font-size:12px;color:white"><sup>[1]</sup></span>
    <span style="font-size:25px;color:white">{y}</span>
    <span style="font-size:12px;color:white"> % </span>
    ${html_icon_sh_100vle}
    <br>
    <span style="font-size:12px;color:white"><sup>[2]</sup></span>
    <span style="font-size:25px;color:white"> ${data.promedio_SH_maximo}</span>
    <span style="font-size:12px;color:white"> ${info_data.Unidades} </span>
    ${html_icon_sh_125vle}
    <br>
    <span style="font-size:12px;color:white"><sup>[3]</sup></span>
    <span style="font-size:25px;color:white"> ${data.promedio_D_maximo}</span>
    <span style="font-size:12px;color:white"> ${info_data.Unidades} </span>
    ${html_icon_d_100vle}
    </div>`
        :
        `<div style="text-align:center; font-size:25px; color:white;">
    <span style="font-size:12px;color:white"><sup>[1]</sup></span>
    <span style="font-size:25px;color:white">{y}</span>
    <span style="font-size:12px;color:white"> % </span>
    ${html_icon_sh_100vle}
    <br>
    <span style="font-size:12px;color:white"><sup>[2]</sup></span>
    <span style="font-size:25px;color:white"> ${data.promedio_SH_maximo}</span>
    <span style="font-size:12px;color:white"> ${info_data.Unidades} </span>
    ${html_icon_sh_125vle}
    </div>`;

    $("#description-"+elementChartGauge).html(html_caption);


    Highcharts.chart(elementChartGauge, {
        chart: {
            zoomType: null,
            panning: null,
            type: 'solidgauge',
            height: 300,
            backgroundColor: 'transparent',
            events: {
                load() {
                    if (!this.renderer.forExport) {

                        const chart = this

                        if (data.porcentaje_SH_apto != null) {

                            chart.series[0].setData([data.porcentaje_SH_apto]);

                            chart.update({
                                yAxis: {
                                    title: {
                                        useHTML: true,
                                        text: `<p style="background:${color}; padding:5px; border-radius:5px;"><b>${estado}</b></p>`
                                    }
                                }
                            })
                        }

                        map.spin(false)
                    }
                }
            }
        },

        title: {
            text: "Promedios validados",
            style: {
                color: '#fff'
            }
        },

        pane: {
            center: ['50%', '50%'],
            size: '90%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
            }
        },
        /*caption: {
            useHTML: true,
            text: html_caption,
            style: {
                color: '#fff'
            }
        },*/
        tooltip: {
            enabled: false
        },
        exporting: {
            enabled: false,
        },
        yAxis: {
            min: 0,
            max: 100,
            tickPositions: [0, 94, 100],
            tickColor: 'transparent',
            tickWidth: 3,
            tickLength: 200,
            labels: {
                distance: 12,
                y: 3,
                style: {
                    color: '#fff'
                }
            },
            title: {
                text: 'Sin datos',
                y: 20,
                style: {
                    color: '#fff'
                }
            },
            stops: [
                [0.94, '#CB4335'], // red - No cumple el 94%
                [0.94, '#55BF3B'] // green - Si cumple el 94%

            ],
            lineWidth: 0,
            minorTickInterval: null,
            tickAmount: 2
        },

        plotOptions: {
            series: {
                dataGrouping: {
                    approximation: 'sum',
                    enabled: true
                }
            },
            solidgauge: {
                dataLabels: {
                    y: 5,
                    borderWidth: 0,
                    useHTML: true
                }
            }
        },
        series: [{
            name: 'Speed',
            data: [],
            dataLabels: {
                format: html_gauge,
                color: '#fff',
            },
            tooltip: {
                valueSuffix: ' %'
            }
        }]
    })

    // Ajustar marca de agua de los graficos
    document.querySelectorAll('.highcharts-root > image')
        .forEach((function (x) { x.setAttribute("preserveAspectRatio", "meet"); }))

}

function LoadData_MaximosDiarios(info_estacion, info_data, elementChartHeatMap) {

    map.spin(true, spinner_options_sidebar);

    $.ajax({
        type: "GET",
        dataType: "json",
        url: url_getHeatMap,
        data: {
            i: info_estacion.I,
            c: info_data.C,
            dt: info_data.UTC
        },
        cache: false,
        success: function (data) {
            LoadHeatMap_MaximosDiarios(info_estacion, info_data, elementChartHeatMap, data);
        },
        error: function () {
            console.log("Error getJSON DATA Maximos Diarios");
        },
        complete: function () {
            map.spin(false);
        }

    });
}

function LoadHeatMap_MaximosDiarios(info_estacion, info_data, elementChartHeatMap, data) {
    //Highcharts.getJSON(url_getHeatMap + '?i=' + info_estacion.I + '&c=' + info_data.C + '&dt=' + info_data.UTC, function (data) {

    map.spin(true, spinner_options_sidebar);

    Highcharts.chart(elementChartHeatMap, {
        chart: {
            type: 'heatmap',
            /*plotBackgroundImage: 'http://alerta2.es/static/img/spd/logos/logo_alerta2_transparente.png',*/
            events: {
                load() {

                    if (!this.renderer.forExport) {

                        let chart = this;
                        chart.showLoading('<i class="fa-solid fa-loader fa-spin-pulse"></i> Cargando...');

                        setTimeout(function () {
                            if (data.maximos_diarios != null && data.maximos_diarios.length > 0) {

                                //Serie de datos
                                chart.series[0].setData(data.maximos_diarios.map(function (point) {
                                    return [point.x, point.y, point.Valor]
                                }))

                                chart.hideLoading();
                            }
                            else {
                                //Sin datos
                                chart.showLoading('<i class="fa-solid fa-hexagon-exclamation" style="color:red;"></i> Sin datos')
                            }

                            map.spin(false);

                        }, 2000);
                    }
                }
            }
        },

        /*accessibility: {
            description: 'We see how temperatures are warmer during the day, especially from around 9am to 9pm. May 8th through 11th are also overall colder days compared to the rest. Overall the temperatures range from around -1 degrees C to around 23 degrees C.'
        },*/

        title: {
            text: 'Máximos diarios',
        },

        subtitle: {
            text: `Variación máxima diaria de ${info_data.Parametro} durante el año ${moment().year()}`
        },

        xAxis: {
            categories: Array.from({ length: 31 }, (_, i) => i + 1)
        },

        yAxis: {
            gridLineColor: 'transparent',
            reversed: true,
            categories: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            title: {
                text: null
            }
        },

        colorAxis: {
            min: 0,
            max: info_data.VLE * 2,
            stops: [
                [0, '#ABEBC6'],
                [0.5, '#58D68D'],
                [0.5, '#EC7063'],
                [1, '#B03A2E']
            ]
        },
        tooltip: {
            useHTML: true,
            formatter: function () {
                return `<h5 style = "font-family:'${"Bradley Hand ITC"}'; font-weight: bold; margin-left: auto; margin-right:auto"> ${info_estacion.Nombre}</h5>
                <p><b style="font-size:16px;">${this.point.value} ${info_data.Unidades} </b>(${info_data.Acronimo}) *<br>
                ${getPointCategoryName(this.point, 'x')}, ${getPointCategoryName(this.point, 'y')} ${moment().year()}</p>
                <p><i class="fas fa-circle" style="color:#CB4335"></i><b>  VLE ${info_data.VLE} ${info_data.Unidades}</b></p>
                <p style="font-size:10px; margin-bottom:0px;">(*) Dato válido</p>`;
            }
        },

        /*tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat:
                '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: "</table>",
            shared: true,
            useHTML: true,
            pointFormatter: function (object) {
                return '<h5 style="font-family:' + "Bradley Hand ITC" + '; font-weight: bold; margin-left: auto; margin-right:auto">' + info_estacion.Nombre + '</h5>' +
                    '<p><b style="font-size:16px;">' + this.y + ' ' + info_data.Unidades + ' </b>(' + info_data.Acronimo + ') *<br>' +
                    //Highcharts.dateFormat('%e %b %Y', this.x) + ', ' +
                    //Highcharts.dateFormat('%H:%M', this.x) + ' h</p>' +
                    //'<p><b>Foco:</b> ' + info_estacion.Foco + '</p>' +
                    '<p><i class="fas fa-circle" style="color:rgb(255, 0, 0)"></i></b>  VLE ' + info_data.VLE + ' mg/Nm³</b></p>' +
                    '<p style="font-size:10px; margin-bottom:0px;">(*) ' + this.Estado + '</p>';
            }
        },*/

        series: [{
            name: 'Máximos por día',
            borderWidth: 1,
            borderColor: 'white',
            data: [],
            dataLabels: {
                enabled: false,
                color: '#000000'
            },
            accessibility: {
                enabled: false
            }
        }],
        /*series: [{
            borderWidth: 0,
            colsize: 24 * 36e5, // one day
            tooltip: {
                headerFormat: 'Temperature<br/>',
                pointFormat: '{point.x:%e %b, %Y} {point.y}:00: <b>{point.value} ℃</b>'
            },
            accessibility: {
                enabled: false
            }
        }]*/
        exporting: {
            filename: `${moment().format("YYMMDD_HHmmss")}_MaximosDiarios_${info_data.Acronimo}_${info_estacion.Nombre}`,
            scale: 1,
            sourceWidth: 1200,
            sourceHeight: 520,
            allowHTML: true,
            buttons: {
                contextButton: {
                    menuItems: menuChart
                }
            },
            chartOptions: {
                title: {
                    text: info_estacion.Nombre
                },
                subtitle: {
                    text: `Variación máxima diaria de ${info_data.Parametro} registrada por el foco ${info_estacion.Foco} durante el año ${moment().year()} a fecha ${moment().format("D MMM, YYYY")}`
                },
                chart: {
                    events: {
                        load: function () {
                            this.yAxis[0].addPlotBand({
                                from: -Infinity,
                                to: Infinity,
                                color: 'rgba(255,255,255,0.8)'
                            });
                        }
                    }
                },
                caption: {
                    useHTML: true,
                    text: `<p>(*) Valor Límite de Emisión (VLE) <span style = "color:#CB4335">${info_data.VLE} ${info_data.Unidades}</span ></p>`
                }
            },
            csv: {
                columnHeaderFormatter: function (item, key) {
                    /*if (!item || item instanceof Highcharts.Axis) {
                        return 'Día'
                    } else {
                        return item.name;
                    }*/

                    if (!key) {
                        return 'Día'
                    }
                    if (key == 'y') {
                        return {
                            topLevelColumnTitle: 'Máximos diarios',
                            columnTitle: 'Mes'
                        };
                    }
                    if (key == 'value') {
                        return {
                            topLevelColumnTitle: 'Máximos diarios',
                            columnTitle: 'Valor'
                        };
                    }
                    return false
                }
            }
        },
    });


    // Ajustar marca de agua de los graficos
    document.querySelectorAll('.highcharts-root > image')
        .forEach((function (x) { x.setAttribute("preserveAspectRatio", "meet"); }))

    //});
}



function MostrarPanelICA(info_ICA, ICA) {

    var html_estado = "";

    if (info_ICA != null) {
        html_estado += "<div class = '" + info_ICA.clase + "' style='padding: 5px 10px; color:#fff; display: inline-block; font-size: 40px; border-radius:40px; position: relative; margin: 0 auto; margin-bottom: 30px'>" +
            "<i class='" + info_ICA.icono + "'></i> " +
            info_ICA.descripcion + "</div>";
    }

    var html_ica = "";

    ICA.forEach(function (element) {
        html_ica +=
            `<p class="icon-description-ICA">
            <b class= "card-${element.Color}">
            <i class= "${element.Icono} fa-xl"></i>
            ${element.Rango}</b> ${element.Descripcion}.</p >`;
    })

    Swal.fire({
        html:
            "<h3 class='text-bradley' style='font-size:30px'><b>Índice de Calidad del Aire</b></h3>" +
            "<div class='linea-divisoria'></div>" +
            "<br>" +
            html_estado +
            html_ica +
            '<p style="font-size: 11px; text-align:left">(*) El Índice de Calidad del Aire (ICA) es una medida que se utiliza para evaluar' +
            ' la calidad del aire en una determinada área geográfica. Se basa en la medición de diversos contaminantes atmosféricos, como' +
            ' partículas, ozono, monóxido de carbono, dióxido de nitrógeno, entre otros. El ICA se utiliza como una herramienta para informar' +
            ' a la población sobre los niveles de contaminación del aire en comparación con los estándares de calidad del aire establecidos' +
            ' por la Organización Mundial de la Salud (OMS) y para tomar medidas que contribuyan a reducir los riesgos para salud pública y' +
            ' el medio ambiente. </p>',
        showConfirmButton: false,
        timer: 100000,
        timerProgressBar: true,
        focusConfirm: false,
        showCloseButton: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    })
}

function MostrarPanelFlags(flags) {

    var html_flags = ""

    flags.forEach(function (element) {
        html_flags +=
            `<p style="text-align:left; font-size:14px">
            <i class="fas fa-circle" style="color:${element.Color}; stroke: #1B1C1C; stroke-width: 20; padding-left:2px"></i>
            <b> ${element.Flag}</b > - ${element.Descripcion}.</p >`;
    })

    Swal.fire({
        html:
            "<h3 class='text-bradley' style='font-size:30px'><b>Códigos de validación</b></h3>" +
            "<div class='linea-divisoria'></div>" +
            "<br>" +
            html_flags +
            '<p style="font-size: 11px; text-align:left">(*) Los códigos de validación son un conjunto de reglas y criterios que se utilizan' +
            ' para verificar los datos ingresados en el sistema y/o en las bases de datos. Cada valor dosminutal de cada variable tendrá' +
            ' asignado un código de validación. Estos códigos han sido diseñados por la DGMA para validar la información en términos de su contenido.</p>',
        showConfirmButton: false,
        timer: 100000,
        timerProgressBar: true,
        focusConfirm: false,
        showCloseButton: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    })
}
