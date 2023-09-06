function LogoFooter(){
    var html = []
    html.push('<img src="/static/img/spd/logos/logo_alerta2_transparente.png" style="max-height:50px; float:left" alt="">');
    return html.join('')
}

function footerStyle(column) {
  return {
    css: { 'border-color': 'rgba(0, 0, 0, 0)' }
  }
}

function loadingTemplate(message) {
    return '<i class="fa fa-spinner fa-spin fa-fw fa-2x"></i>'
}