from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from gestionmuestras.models_nuevo import *
from gestionmuestras.modelChurros import *
from gestionmuestras.forms import *

from copuma.models import ValorMuestraCopumaVolatil

from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import permission_required
from django.conf import settings

import os

from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, PageBreak, Image
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import io

from gestionmuestras.funciones_procesado import *

import pandas as pd


import csv
import os
import sys

@permission_required('auth.gestion_muestras')
def opcionesGestionMuestras(request):
    return render(
        request,
        "gestionmuestras/gmuestras.html",
        {
        }
    )

def cargarInfoGestmuesViejo():
    relacion_analisis = {"ANALISIS1":8, "ANALISIS2":9, "ANALISIS3":10, "ANALISIS4":1, "ANALISIS5":5, "ANALISIS6":2, "ANALISIS7":4, "ANALISIS8":20, "ANALISIS9":24, "ANALISIS10":22,"ANALISIS11":19, "ANALISIS12":16, "ANALISIS13": 15, "ANALISIS14": 13, "ANALISIS15":3, "ANALISIS16":14, "ANALISIS17":18, "ANALISIS18":7, "ANALISIS19":49, "ANALISIS20":50, "ANALISIS21":51, "ANALISIS22":52, "ANALISIS23":6, "ANALISIS24":1, "ANALISIS25":11}
    dir = 'bdd'

    '''
    # cargar los valores de los modelos in a df using pandas from file bdd\\ECOGIDA.DBF.xlsx
    df = pd.read_excel('bdd\\RECOGIDA.DBF.xlsx')
    for index, row in df.iterrows():
        print(index, " -- ", row["NUMERO"], "--", row["CSN"], "--", row["COD_PRO"], "--", row["COD_MEMO"], "--", row["RECOGE"], "--", row["SUMINIST"], "--", row["OBSERV"])
        recogida = GestmuesRecogida(numero=row["NUMERO"], csn=row["CSN"], procedencia=row["COD_PRO"], memoria=row["COD_MEMO"], suministra=row["SUMINIST"], observaciones=row["OBSERV"]).save(using='gestion_muestras')
    

    codigos_recogida = GestmuesRecogida.objects.using('gestion_muestras')

    for f in os.listdir(dir):
        if f.startswith("COLECCION_"):
            # cargo el excel con encoding utf-8
            df = pd.read_excel(dir+"\\"+f)
            # recorro el dataframe
            nombre_mes = f.replace("COLECCION_", "").replace(".DBF.xlsx", "").upper()
            for index, row in df.iterrows():
                suministra = str(row["SUMINIST"])
                print("ROW", row, "\nSUMINISTRA:", suministra, "\n========================\n")
                if row["NUMERO"] < 400 and codigos_recogida.filter(numero=row["NUMERO"]).exists():
                    recogida = codigos_recogida.filter(numero=row["NUMERO"]).get()
                    print("COLECCIION:", row, "\n========================\n", recogida)
                    # si recogida no es NaT almaceno fecha en fechaRecogida
                    fechaRecogida = None
                    if not pd.isna(row["FECHA"]):
                        fechaRecogida = datetime.strptime(str(row["FECHA"]), '%Y-%m-%d %H:%M:%S')
                    fechaRecogidaFinal = None
                    if not pd.isna(row["FECHAFIN"]):
                        fechaRecogidaFinal = datetime.strptime(str(row["FECHAFIN"]), '%Y-%m-%d %H:%M:%S')
                    fechaRecepcion = None
                    if not pd.isna(row["FECHARECP"]):
                        fechaRecepcion = datetime.strptime(str(row["FECHARECP"]), '%Y-%m-%d %H:%M:%S')
                    if not pd.isna(row["HORA"]):
                        hora = row["HORA"].replace(".",":")
                        fechaRecogida = fechaRecogida.replace(hour=int(hora.split(":")[0]), minute=int(hora.split(":")[1]))
                    if not pd.isna(row["HORAFIN"]):
                        hora = row["HORAFIN"].replace(".",":")
                        fechaRecogidaFinal = fechaRecogidaFinal.replace(hour=int(hora.split(":")[0]), minute=int(hora.split(":")[1]))

                    muestra_recogida = 0
                    if row["RECOGIDA"]:
                        muestra_recogida = 1
                    
                    filtro = None
                    if not pd.isna(row["NFILTRO"]):
                        filtro = row["NFILTRO"]
                    bomba = None
                    if not pd.isna(row["IBOMBA"]):
                        bomba = row["IBOMBA"]

                    print("FECHA RECOGIDA", fechaRecogida, fechaRecogidaFinal, fechaRecepcion, row["CSN"], row["COD_PRO"], row["COD_MEMO"], nombre_mes)
                    if recogida.csn != row["CSN"] or recogida.procedencia != row["COD_PRO"] or recogida.memoria != row["COD_MEMO"]:
                        coleccion = GestmuesColeccion(n_recogida=recogida, csn=row["CSN"], recoge=row["RECOGE"], suministra=suministra, observaciones=row["OBSERV"], recogido=muestra_recogida, fecha_recogida_inicial=fechaRecogida, fecha_recogida_final=fechaRecogidaFinal, fecha_recepcion=fechaRecepcion, conservacion=row["CONSERV"], nfiltro=filtro, ibomba=bomba, mes=nombre_mes).save(using='gestion_muestras')
                    else:
                        coleccion = GestmuesColeccion(n_recogida=recogida, recoge=row["RECOGE"], suministra=suministra, observaciones=row["OBSERV"], recogido=muestra_recogida, fecha_recogida_inicial=fechaRecogida, fecha_recogida_final=fechaRecogidaFinal, fecha_recepcion=fechaRecepcion, conservacion=row["CONSERV"], nfiltro=filtro, ibomba=bomba, mes=nombre_mes).save(using='gestion_muestras')
    
    
         
    noEncontradas = []
    determinaciones = Determinaciones.objects.using('gestion_muestras').all()
    for f in os.listdir(dir):
        
        if f.startswith("ANALISIS_"):
            df = pd.read_excel(dir+"\\"+f)
            nombre_mes = f.replace("ANALISIS_", "").replace(".DBF.xlsx", "").upper()
            for index, row in df.iterrows():
                for key in relacion_analisis:
                    if not pd.isna(row[key]):
                        if not pd.isna(row["NUMERO"]):
                            if GestmuesColeccion.objects.using('gestion_muestras').filter(n_recogida=int(row["NUMERO"]), mes=nombre_mes).exists():
                                print("BUSCO COLECCION", int(row["NUMERO"]), nombre_mes)
                                muestra = GestmuesColeccion.objects.using('gestion_muestras').filter(n_recogida=int(row["NUMERO"]), mes=nombre_mes).get()
                                determinacion = determinaciones.filter(identificador=relacion_analisis[key]).get()
                                GestmuesRelacionRecogidaDeterminacion(id_muestra_recogida=muestra,id_determinacion=determinacion,mes=nombre_mes).save(using='gestion_muestras')
                            else:
                                valor = {"numero":int(row["NUMERO"]), "mes":nombre_mes}
                                if valor not in noEncontradas:
                                    noEncontradas.append(valor)
    print("NO ENCONTRADAS\n", noEncontradas)
         '''   

def getBotonesGestion(request):
    return render(request, "gestionmuestras/botonesGestion.html", {"botones":BotonesEdicion.objects.using('gestion_muestras').values()})

def almacenarCodigosBarras(request):
    if 'codigos_barra' in request.session:
        print(request.POST.get('codigos'), "----\n", request.session['codigos_barra'])
        for item in json.loads(request.POST.get('codigos')):
            encontrado = False
            for etiqueta in request.session['codigos_barra']:
                if etiqueta["codigo"] == item["codigo"]:
                    etiqueta["cantidad"] = etiqueta["cantidad"] + item["cantidad"]
                    encontrado = True
            if not encontrado:
                request.session['codigos_barra'].append(item)
        
        print(request.session['codigos_barra'])
        request.session['codigos_barra'] = request.session['codigos_barra']
    else:
        request.session['codigos_barra'] = json.loads(request.POST.get('codigos'))
    return JsonResponse({}, safe=False)

def renovarCodigosBarras(request):
    request.session['codigos_barra'] = json.loads(request.POST.get('codigos'))
    return JsonResponse({}, safe=False)

def vaciarCodigosBarras(request):
    request.session.pop('codigos_barra')
    return render(request, "gestionmuestras/gmuestras.html", {})

def consultarEtiquetas(request):
    return render(request, "gestionmuestras/panelEtiquetas.html", {"etiquetas":request.session['codigos_barra']})

def consultarEtiquetasSeleccionadas(request):
    if 'codigos_barra' in request.session:
        return render(request, "gestionmuestras/panelEtiquetasGuardadas.html", {"etiquetas":request.session['codigos_barra']})
    else:
        return render(request, "gestionmuestras/panelEtiquetasGuardadas.html", {"etiquetas":""})

# definir entrada codigos de barras y textos
def crearCodigosBarras(request):
   
    buffer = io.BytesIO()
    # Define the page size in mm
    page_width = 62 * mm
    page_height = 28 * mm
    text_height_mm = 6
    # Create a PDF document
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height)) 

    # Crear una lista para almacenar elementos en el PDF

    for item in request.session['codigos_barra']:
        if item["tipo"] == "muestra":
            options = {
                'dpi': 800,
                'module_height': 5,
                'module_width': 0.3,
                'quiet_zone': 1,
                'font_size': 4,
                'text_distance': 2
            }
            barcode_format = barcode.get_barcode_class('code128')
            my_barcode = barcode_format(item["codigo"], writer=ImageWriter())
            barcode_image = my_barcode.save(settings.MEDIA_ROOT+"/barcodes/"+ item["codigo"], options = options)

            for i in range(item["cantidad"]):
                c.drawImage(barcode_image, page_width*.125, 8, width=page_width*.75, height=page_height)            
                c.setFont("Helvetica", text_height_mm*1.6)
                c.drawCentredString(page_width/2, 15, item["texto"])
                c.showPage()



        elif item["tipo"] == "alicuota":
            # defino las opciones para la etiqueta de alicuota
            # esta etiqueta tiene el mismo tamaño pero tiene dos códigos de barras
            # el primero es el código será el código de la muestra y el segundo el codigo reducido
            # el texto debajo del primero es el mismo que el de la muestra
            # el texto debajo del segundo es el codigo reducido
            options = {
                'dpi': 800,
                'module_height': 5,
                'module_width': 0.3,
                'quiet_zone': 1,
                'font_size': 4,
                'text_distance': 2.5
            }
            barcode_format = barcode.get_barcode_class('code128')
            my_barcode = barcode_format(item["codigo"], writer=ImageWriter())
            barcode_image = my_barcode.save(settings.MEDIA_ROOT+"/barcodes/"+ item["codigo"], options = options)

            
            barcode_format_2 = barcode.get_barcode_class('code128')
            my_barcode_2 = barcode_format_2(item["codigo_reducido"], writer=ImageWriter())
            barcode_image_2 = my_barcode_2.save(settings.MEDIA_ROOT+"/barcodes/"+ item["codigo_reducido"], options = options)

            for i in range(item["cantidad"]):
                c.drawImage(barcode_image, page_width*.125, 0, width=page_width*.75, height=page_height/2)
                c.drawImage(barcode_image_2, page_width*.125, page_height/2, width=page_width*.75, height=page_height/2)

                c.setFont("Helvetica", text_height_mm)
                c.drawCentredString(page_width/2, page_height/2, item["texto"])
                c.showPage()
    c.save()
 
    dir = settings.MEDIA_ROOT+"/barcodes/"
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

    buffer.seek(0)
    return FileResponse(buffer, filename="etiquetas.pdf", content_type='application/force-download')

def modificarCodigosExistentes(request):
    return JsonResponse({}, safe=False)

def eliminarCodigosExistentes(request, codigo):
    # elimina el elemento cuyo codigo coincide con el codigo pasado del listado en request.session['codigos_barra']
    auxList = []
    for item in request.session['codigos_barra']:
        if item["codigo"] == codigo:
            request.session['codigos_barra'].remove(item)
        else:
            auxList.append(item)
    request.session['codigo_barra'] = auxList
    return JsonResponse({}, safe=False)

def etiquetasSeleccionar(request, id):
    listaAuxiliar = []

    tipoMuestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id).get().codigo_recogida.codigo_csn.nombre
    etiqueta = {"codigo":"1"+str(id).zfill(6)+"000000", "texto":"M("+str(id)+") "+tipoMuestra,"tipo":"muestra","cantidad":1}
    # comprueba si en codigos existentes está ya la etiqueta comparando el codigo
    if etiqueta not in listaAuxiliar:
        listaAuxiliar.append(etiqueta)

    # obtiene las alicuotas de la muestra
    alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=id).values('identificador', 'id_analiticas__nombre', 'fecha_hora_entrega', 'analista_tecnico__nombre', 'cantidad_muestra_analizada', 'estado_alicuota__descripcion') 
    for alicuota in alicuotas:
        etiqueta = {"codigo":"2"+str(id).zfill(6)+str(alicuota["identificador"]).zfill(6), "texto":"A("+str(id)+") "+alicuota["id_analiticas__nombre"],"tipo":"alicuota","cantidad":1}
        # localizar codigo reducido en relacion analitica tratamiento
        if RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota["identificador"]).exists():
            etiqueta["codigo_reducido"] = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota["identificador"])[0].cod_reducido

        # comprueba si en codigos existentes está ya la etiqueta comparando el codigo
        if etiqueta not in listaAuxiliar:
            listaAuxiliar.append(etiqueta)
    
    return render(request, "gestionmuestras/panelEtiquetas.html", {"etiquetas":listaAuxiliar})

@permission_required('auth.visualizacion_muestras')
def listadoMuestras(request):
    return render(request, "gestionmuestras/listadoMuestras.html", {})


@permission_required('auth.visualizacion_muestras')
def listadoMuestrasDatos(request):
    
    muestras = HistoricoRecogida.objects.using('gestion_muestras').order_by('-identificador').values('identificador', 'codigo_recogida__codigo_csn__nombre','cliente__nombre','codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__codigo_memoria__memoria', 'recepcionado_por__nombre', 'fecha_hora_recogida', 'fecha_hora_recepcion', 'estado_de_muestra__descripcion', 'referencia_cliente')

    return JsonResponse(list(muestras), safe=False)


@permission_required('auth.visualizacion_muestras')
def getInfoMuestra(request, id_muestra):
    informe = None
    if 'auth.informes_muestra_lectura' in request.user.get_all_permissions():
        if RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=id_muestra).exists():
            informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=id_muestra)[0]
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id_muestra)[0]
    return render(
        request,
        "gestionmuestras/informacionMuestra.html",
        {
            "muestra":muestra,
            "informe":informe
        }
    )


@permission_required('auth.gestion_admin')
def borrarAlicuota(request, id_alicuota):
    informe = None
    RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=id_alicuota).delete()
    RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica_id=id_alicuota).delete()
    RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=id_alicuota).delete()
    return JsonResponse({"resultado":True}, safe=False)

@csrf_exempt
@permission_required('auth.insercion_muestras')
def duplicarAlicuota(request):
    print(request.POST)
    alicuota = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=request.POST.get('id'), id_analiticas__identificador=request.POST.get('determinacion'))[0]
    relacionTratamiento = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=request.POST.get('id'))[0]
    
    alicuota.pk = None
    alicuota.save(using='gestion_muestras')
    relacionTratamiento.pk = None
    relacionTratamiento.id_muestra_analitica = alicuota
    codigos = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento=relacionTratamiento.tratamiento.identificador).get().id_muestra_codigo
    relacionTratamiento.cod_reducido = codigos.codigo+str(codigos.posicion)+"_DU"
    relacionTratamiento.paso_actual = 0
    relacionTratamiento.fecha_inicio = datetime.now()
    relacionTratamiento.fecha_fin = None
    codigos.posicion = codigos.posicion+1
    codigos.save(using='gestion_muestras')
    relacionTratamiento.save(using='gestion_muestras')
    EventosMuestras(
            muestra = alicuota.id_historico_recogida.identificador,
            evento = "Recepción",
            fecha_evento = datetime.now(),
            comentario = "Se ha generado un duplicado de la alícuota "+str(alicuota.identificador) + "("+relacionTratamiento.cod_reducido+")",
            usuario = request.user.id
        ).save(using='gestion_muestras')    
    return JsonResponse({"resultado":True}, safe=False)

@permission_required('auth.visualizacion_muestras')
def getInfoMuestraForm(request):
    return getInfoMuestra(request, request.POST.get('id_muestra'))

@permission_required('auth.visualizacion_muestras')
def getAlicuotasMuestra(request, id_muestra):
    alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=id_muestra).values('identificador', 'id_analiticas__identificador', 'id_analiticas__nombre', 'fecha_hora_entrega', 'analista_tecnico__identificador', 'analista_tecnico__nombre', 'cantidad_muestra_analizada', 'estado_alicuota__descripcion')
    return JsonResponse(list(alicuotas), safe=False)

@permission_required('auth.insercion_muestras')
def insertarMuestra(request):
    if request.method == "POST":

        if RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn__nombre=request.POST.get('codigoCSN').split("_")[1], codigo_procedencia__nombre=request.POST.get('localizacion'), codigo_memoria__memoria=request.POST.get('memoria')).exists():
            recogida = RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn__nombre=request.POST.get('codigoCSN').split("_")[1], codigo_procedencia__nombre=request.POST.get('localizacion'), codigo_memoria__memoria=request.POST.get('memoria'))[0]
            if request.POST.get('inputComentarioGeneral') != '':
                recogida.observaciones = recogida.observaciones + '\n' + request.POST.get('inputComentarioGeneral')
                recogida.save(using='gestion_muestras')
        else:
            recogida = RecogidaGeneral(
                codigo_csn = CodMuestras.objects.using('gestion_muestras').filter(nombre=request.POST.get('codigoCSN').split("_")[1])[0], 
                codigo_procedencia= Procedencias.objects.using('gestion_muestras').filter(nombre=request.POST.get('localizacion'))[0], 
                codigo_memoria = Memorias.objects.using('gestion_muestras').filter(memoria=request.POST.get('memoria'))[0] , 
                observaciones = request.POST.get('inputComentarioGeneral'), 
                frecuencia_de_recogida = FrecuenciaRecogida.objects.using('gestion_muestras').filter(nombre=request.POST.get('frecuencia'))[0]
                )
            recogida.save(using='gestion_muestras')

        '''
        rutaFoto = ""
        if(request.POST.get('foto_webcam') != ''):
            print("guardar foto y calcular ruta") 
            rutaFoto = "/gestionMuestras/fotosMuestras/"+str(recogida.identificador)+"_"+request.POST.get('fechaRecepcion')+"_"+request.POST.get('horaRecepcion')+".jpg"
            f = open(settings.MEDIA_ROOT+rutaFoto, "w")
            f.write(request.POST.get('foto_webcam'))
            f.close()
        '''

        historico = HistoricoRecogida(
            codigo_recogida = recogida,
            codigo_barras = "0000000000000",
            recepcionado_por = Usuarios.objects.using('gestion_muestras').filter(usuario_django=request.user.id)[0],
            cliente = Clientes.objects.using('gestion_muestras').filter(nombre=request.POST.get('cliente'))[0],
            suministrador = Suministradores.objects.using('gestion_muestras').filter(nombre=request.POST.get('suministrador'))[0],
            fecha_hora_recogida = request.POST.get('fechaRecogidaInicio'),
            fecha_hora_recogida_2 = request.POST.get('fechaRecogidaFin') ,
            fecha_hora_recogida_ref = request.POST.get('fechaRecogidaReferencia'),
            fecha_hora_recepcion = request.POST.get('fechaRecepcion'),
            estado_de_muestra = EstadoMuestras.objects.using('gestion_muestras').filter(identificador_estado=1)[0],
            referencia_cliente = request.POST.get('referencia'),
            comentarios = request.POST.get('inputComentarioParticular')
        )
        
        historico.save(using='gestion_muestras')
        id_muestra = historico.identificador
        codigoBarras = generarCodigoBarras(id_muestra, None)
        historico.codigo_barras = codigoBarras
        historico.save(using='gestion_muestras')

        n_informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(anio=datetime.now().year).order_by('-identificador')[0].identificador+1
        anio_informe = datetime.now().year
        RelacionInformesMuestra(identificador = n_informe, codigo_muestra_asociada = id_muestra, anio = anio_informe).save(using='gestion_muestras')
    
        # insertar evento notificando la creación de la muestra
        EventosMuestras(
            muestra = id_muestra,
            evento = "Recepción",
            fecha_evento = datetime.now(),
            comentario = "Creada muestra y asignado número de informe "+str(n_informe),
            usuario = request.user.id
        ).save(using='gestion_muestras')

        mensaje = MonitorizaMensajesTipo.objects.using('spd').filter(id=50).get()
        titulo = mensaje.mensaje.replace("<id_muestra>", str(id_muestra))
        descripcion = mensaje.descripcion.replace("<id_muestra>", str(id_muestra)).replace("<cliente>", historico.cliente.nombre).replace("<informe>", str(n_informe)+"/"+str(anio_informe))

        MensajesTelegram(id_area=4,id_estacion=None,fecha_hora_utc=datetime.now(pytz.timezone("Europe/Madrid")),mensaje=titulo,descripcion=descripcion,icono=mensaje.icono,estado=mensaje.estado,id_telegram=settings.ID_CHAT_GESTION_MUESTRAS,silenciar=mensaje.silenciar, confirmar=mensaje.confirmar).save(using='spd')

        determinaciones = Determinaciones.objects.using('gestion_muestras').order_by('nombre').values()
        predefinidas = MedidasPredefinidas.objects.using('gestion_muestras').values()

        return render(request, "gestionmuestras/insertarAlicuotas.html", {
            "id_muestra":id_muestra,
            "determinaciones":determinaciones,
            "predefinidas":predefinidas
        })
    else:
        memorias = Memorias.objects.using('gestion_muestras').order_by('descripcion').values()
        codMuestras = CodMuestras.objects.using('gestion_muestras').order_by('nombre').values()
        frecuencias = FrecuenciaRecogida.objects.using('gestion_muestras').order_by('-identificador').values()
        suministradores = Suministradores.objects.using('gestion_muestras').order_by('nombre').values()
        clientes = Clientes.objects.using('gestion_muestras').order_by('nombre').values()
        localizaciones = Procedencias.objects.using('gestion_muestras').order_by('nombre').values()
        parametros = ParametrosMuestra.objects.using('gestion_muestras').values()
        textos = FrasesPredefinidas.objects.using('gestion_muestras').values()
        return render(
            request,
            "gestionmuestras/insertarMuestra.html",
            {
                "memorias":memorias,
                "codMuestras":codMuestras,
                "frecuencias":frecuencias,
                "suministradores":suministradores,
                "clientes":clientes,
                "localizaciones":localizaciones,
                "parametros":parametros,
                "textos":textos
            }
        )

@permission_required('auth.insercion_muestras')
def modificarMuestra(request, id_muestra):
    if request.method == "POST":
        print(request.POST)
        if RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn__nombre=request.POST.get('codigoCSN').split("_")[1], codigo_procedencia__nombre=request.POST.get('localizacion'), codigo_memoria__memoria=request.POST.get('memoria')).exists():
            recogida = RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn__nombre=request.POST.get('codigoCSN').split("_")[1], codigo_procedencia__nombre=request.POST.get('localizacion'), codigo_memoria__memoria=request.POST.get('memoria'))[0]
            if request.POST.get('inputComentarioGeneral') != '':
                recogida.observaciones = recogida.observaciones + '\n' + request.POST.get('inputComentarioGeneral')
                recogida.save(using='gestion_muestras')
        else:
            recogida = RecogidaGeneral(
                codigo_csn = CodMuestras.objects.using('gestion_muestras').filter(nombre=request.POST.get('codigoCSN').split("_")[1])[0], 
                codigo_procedencia= Procedencias.objects.using('gestion_muestras').filter(nombre=request.POST.get('localizacion'))[0], 
                codigo_memoria = Memorias.objects.using('gestion_muestras').filter(memoria=request.POST.get('memoria'))[0] , 
                observaciones = request.POST.get('inputComentarioGeneral'), 
                frecuencia_de_recogida = FrecuenciaRecogida.objects.using('gestion_muestras').filter(nombre=request.POST.get('frecuencia'))[0]
                )
            recogida.save(using='gestion_muestras')

        historico = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id_muestra).get()
        historico.codigo_recogida = recogida
        historico.recepcionado_por = Usuarios.objects.using('gestion_muestras').filter(usuario_django=request.user.id)[0]
        historico.cliente = Clientes.objects.using('gestion_muestras').filter(nombre=request.POST.get('cliente'))[0]
        historico.suministrador = Suministradores.objects.using('gestion_muestras').filter(nombre=request.POST.get('suministrador'))[0]
        historico.fecha_hora_recogida = request.POST.get('fechaRecogidaInicio')
        historico.fecha_hora_recogida_2 = request.POST.get('fechaRecogidaFin')
        historico.fecha_hora_recogida_ref = request.POST.get('fechaRecogidaReferencia')
        historico.fecha_hora_recepcion = request.POST.get('fechaRecepcion')
        historico.referencia_cliente = request.POST.get('referencia')
        historico.comentarios = request.POST.get('inputComentarioParticular')
        historico.save(using='gestion_muestras')
        
        # insertar evento notificando la creación de la muestra
        EventosMuestras(
            muestra = id_muestra,
            evento = "Modificación",
            fecha_evento = datetime.now(),
            comentario=request.POST.get('inputMotivoModificacion'),
            usuario = request.user.id
        ).save(using='gestion_muestras')

        mensaje = MonitorizaMensajesTipo.objects.using('spd').filter(id=51).get()
        titulo = mensaje.mensaje.replace("<id_muestra>", str(id_muestra))
        descripcion = mensaje.descripcion.replace("<id_muestra>", str(id_muestra)).replace("<cliente>", historico.cliente.nombre).replace("<motivo>", request.POST.get('inputMotivoModificacion'))

        MensajesTelegram(id_area=4,id_estacion=None,fecha_hora_utc=datetime.now(pytz.timezone("Europe/Madrid")),mensaje=titulo,descripcion=descripcion,icono=mensaje.icono,estado=mensaje.estado,id_telegram=settings.ID_CHAT_GESTION_MUESTRAS,silenciar=mensaje.silenciar, confirmar=mensaje.confirmar).save(using='spd')

        return getInfoMuestra(request, id_muestra)
    else:
        memorias = Memorias.objects.using('gestion_muestras').order_by('descripcion').values()
        codMuestras = CodMuestras.objects.using('gestion_muestras').order_by('nombre').values()
        frecuencias = FrecuenciaRecogida.objects.using('gestion_muestras').order_by('-identificador').values()
        suministradores = Suministradores.objects.using('gestion_muestras').order_by('nombre').values()
        clientes = Clientes.objects.using('gestion_muestras').order_by('nombre').values()
        localizaciones = Procedencias.objects.using('gestion_muestras').order_by('nombre').values()
        parametros = ParametrosMuestra.objects.using('gestion_muestras').values()
        return render(
            request,
            "gestionmuestras/modificarMuestra.html",
            {
                "muestra":HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id_muestra).get(),
                "memorias":memorias,
                "codMuestras":codMuestras,
                "frecuencias":frecuencias,
                "suministradores":suministradores,
                "clientes":clientes,
                "localizaciones":localizaciones,
                "parametros":parametros,
            }
        )

@permission_required('auth.insercion_muestras')
def insertarAlicuotas(request, id_muestra):
    determinaciones = Determinaciones.objects.using('gestion_muestras').order_by('nombre').values()
    predefinidas = MedidasPredefinidas.objects.using('gestion_muestras').values()

    return render(request, "gestionmuestras/insertarAlicuotas.html", {
        "id_muestra":id_muestra,
        "determinaciones":determinaciones,
        "predefinidas":predefinidas
    })

@permission_required('auth.insercion_muestras')
def consultarParametrosTipo(request, tipo):
    parametros = RelacionTipoDeterminacionParametros.objects.using('gestion_muestras').filter(tipo=tipo,determinacion__isnull=True).values("parametro__nombre","parametro__descripcion","valor_recomendado")
    return JsonResponse({"parametros":list(parametros)}, safe=False)
        
@permission_required('auth.insercion_muestras')
def insertarDeterminaciones(request):
    determinacionesInsertadas = []
    relacionDeterminacion = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras')
    for key in request.POST:
        if request.POST.get(key) == "on":
            tratamientos = relacionDeterminacion.filter(id_determinacion=key).values("id_determinacion__identificador", "id_determinacion__nombre", "id_tratamiento__identificador", "id_tratamiento__descripcion", "por_defecto")
            determinacionesInsertadas.append({"determinacion":key, "determinacion_nombre":tratamientos[0]["id_determinacion__nombre"], "tratamientos":tratamientos})

    return render(request, "gestionmuestras/asignacionTratamiento.html", {
        "id_muestra": request.POST.get("id_muestra"),
        "determinacionesInsertadas": determinacionesInsertadas,
    })
    

@permission_required('auth.insercion_muestras')
def insertarTratamientos(request):
    tratamientosModelo = Tratamiento.objects.using('gestion_muestras')
    determinacionesModelo = Determinaciones.objects.using('gestion_muestras')

    tratamientos = []
    controles_requeridos = []

    for key in request.POST:
        if request.POST.get(key) == "on":
            tecnicos = RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(procedimiento=key.split("_")[2]).values("responsable", "sustituto_1","sustituto_2","sustituto_3").get()
            tratamientos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]]})

            # obtengo los controles requeridos para el tratamiento
            controles = MuestraActualCodigo.objects.using('gestion_muestras').filter(id=RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento= key.split("_")[2]).get().id_muestra_codigo.id).get()
            if controles.duplicada_pos == 0:
                controles_requeridos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "control":"duplicado", "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]]})
            if controles.control_pos == 0:
                controles_requeridos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "control":"control", "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]]})
            if controles.blanco_pos == 0:
                controles_requeridos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "control":"blanco", "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]]})


    return render(request, "gestionmuestras/tareasPostInsercion.html", {
        "id_muestra": request.POST.get("id_muestra"),
        "tratamientos": tratamientos,
        "controles_requeridos": controles_requeridos
    })

@permission_required('auth.insercion_muestras')
def finalizarInsercion(request):
    muestra = 0
    for key in request.POST:
        print(key, request.POST.get(key))

        if key == "csrfmiddlewaretoken":
            continue
        muestra = key.split("_")[0]

        alicuota = 'Analitica'
        if len(key.split("_")) > 3:
            alicuota = key.split("_")[3]
            
        muestrasAnalitica = RelacionHistoricoMuestraAnaliticas(id_historico_recogida=HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=key.split("_")[0]).get(), id_analiticas=Determinaciones.objects.using('gestion_muestras').filter(identificador=key.split("_")[1]).get(), fecha_hora_entrega=datetime.now(), analista_tecnico=Usuarios.objects.using('gestion_muestras').filter(nombre=request.POST.get(key)).get(), descripcion='FTOTAL', alicuota=alicuota, estado_alicuota=EstadoMuestras.objects.using('gestion_muestras').filter(identificador_estado=0).get())

        muestrasAnalitica.save(using='gestion_muestras')
        muestrasAnalitica.codigo_barras = generarCodigoBarras(int(key.split("_")[0]), muestrasAnalitica.identificador)
        muestrasAnalitica.save(using='gestion_muestras')

        codigos = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento__identificador=key.split("_")[2]).get().id_muestra_codigo
        codigo_reducido = codigos.codigo+str(codigos.posicion)
        
        codigos.posicion = codigos.posicion+1
        if alicuota == 'Analitica':
            if codigos.duplicada_pos > 0:
                codigos.duplicada_pos = codigos.duplicada_pos-1
            if codigos.control_pos > 0:
                codigos.control_pos = codigos.control_pos-1
            if codigos.blanco_pos > 0:
                codigos.blanco_pos = codigos.blanco_pos-1
            
        if alicuota == 'blanco':
            codigo_reducido = codigo_reducido + "_BL"
            codigos.blanco_pos = codigos.blanco
            muestrasAnalitica.id_historico_recogida = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(tipo_control='BL', codigo=codigos.codigo)[0].id_muestra_historico
        elif alicuota == 'duplicado':
            codigo_reducido = codigo_reducido + "_DU"
            codigos.duplicada_pos = codigos.duplicada
        elif alicuota == 'control':
            codigo_reducido = codigo_reducido + "_CTR"
            codigos.control_pos = codigos.control
            muestrasAnalitica.id_historico_recogida = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(tipo_control='CTR', codigo=codigos.codigo)[0].id_muestra_historico
        codigos.save(using='gestion_muestras')
        

        RelacionAnaliticasTratamiento(id_muestra_analitica=muestrasAnalitica, tratamiento=Tratamiento.objects.using('gestion_muestras').filter(identificador=key.split("_")[2]).get(), cod_reducido=codigo_reducido, fecha_inicio=datetime.now(), analista=Usuarios.objects.using('gestion_muestras').filter(nombre=request.POST.get(key)).get(), paso_actual=0).save(using='gestion_muestras')
        

    # dedirigir la vista a la muestra
    return getInfoMuestra(request, muestra)


@permission_required('auth.insercion_muestras')
def obtenerValoresUltimaMuestra(request):
    # obtengo el ultimo valor del model historicoRecogida
    historico = HistoricoRecogida.objects.using('gestion_muestras').order_by('-identificador').values('codigo_recogida__codigo_memoria__memoria', 'codigo_recogida__codigo_csn__tipo_id', 'codigo_recogida__codigo_csn__nombre', 'codigo_recogida__frecuencia_de_recogida__nombre', 'suministrador__nombre', 'cliente__nombre', 'codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__observaciones', 'fecha_hora_recogida', 'fecha_hora_recogida_2','fecha_hora_recogida_ref')[0]
    return JsonResponse({"muestra": historico}, safe=False)

@permission_required('auth.insercion_muestras')
def obtenerComentarioRecogidaGeneral(request):
    if (RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_memoria__memoria=request.POST["memoria"], codigo_csn__nombre=request.POST["codigoCSN"], codigo_procedencia__nombre=request.POST["localizacion"]).exists()):
        # obtengo el valor del comentario de recogida general dada la memoria, el codigo de csn y la procedencia
        recogida = RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_memoria__memoria=request.POST["memoria"], codigo_csn__nombre=request.POST["codigoCSN"], codigo_procedencia__nombre=request.POST["localizacion"]).values('observaciones')[0]
        return JsonResponse({"comentario":recogida["observaciones"]}, safe=False)
    else:
        return JsonResponse({"comentario":""}, safe=False)

def generarCodigoBarras(idMuestra, idAlicuota):
    if idAlicuota is None:
        return "1"+("%06d" % idMuestra)+("%06d" % 0)
    else:      
        return "2"+("%06d" % idMuestra)+("%06d" % idAlicuota)


@permission_required('auth.visualizacion_muestras')
def muestrasInforme(request):
    return render(request, "gestionmuestras/muestrasInformes.html", {})


@permission_required('auth.visualizacion_muestras')
def muestrasInformeDatos(request):
    muestras = HistoricoRecogida.objects.using('gestion_muestras').filter(estado_de_muestra=4).order_by('-identificador').values('identificador', 'codigo_recogida__codigo_csn__nombre','cliente__nombre','codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__codigo_memoria__memoria', 'recepcionado_por__nombre', 'fecha_hora_recogida', 'fecha_hora_recepcion', 'estado_de_muestra__descripcion', 'referencia_cliente')

    return JsonResponse(list(muestras), safe=False)

@permission_required('auth.visualizacion_muestras')
def consultorMedidas(request):
    if request.method == "POST":
        memorias, clientes, determinaciones, estados, tipos = [], [], [], [], []
        for k, v in request.POST.items():
            if k.startswith("memoria_") and v == "on":
                memorias.append(k.replace("memoria_",""))
            if k.startswith("cliente_") and v == "on":
                clientes.append(int(k.replace("cliente_","")))
            if k.startswith("determinacion_") and v == "on":
                determinaciones.append(int(k.replace("determinacion_","")))
            if k.startswith("estado_") and v == "on":
                estados.append(int(k.replace("estado_","")))
            if k.startswith("tipo_") and v == "on":
                tipos.append(k.replace("tipo_",""))

        muestras = ResultadosMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida__fecha_hora_recogida__gte=request.POST.get('fechaInicio'), id_alicuota__id_historico_recogida__fecha_hora_recogida__lte=request.POST.get('fechaFin'))
        if len(memorias) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__codigo_recogida__codigo_memoria__codigo_memoria__in=memorias)
        if len(clientes) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__cliente__identificador__in=clientes)
        if len(determinaciones) > 0:
            muestras = muestras.filter(id_alicuota__id_analiticas__identificador__in=determinaciones)
        if len(estados) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__estado_de_muestra__identificador_estado__in=estados)
        if len(tipos) > 0:
            muestras = muestras.filter(id_alicuota__id_historico_recogida__codigo_recogida__codigo_csn__codigo__in=tipos)

        return render(request, "gestionmuestras/consultorMedidasResultados.html", {"muestras":muestras})
    else:
        memorias = Memorias.objects.using('gestion_muestras').order_by('descripcion')
        tiposMuestras = CodMuestras.objects.using('gestion_muestras').order_by('nombre')
        determinaciones = Determinaciones.objects.using('gestion_muestras')
        clientes = Clientes.objects.using('gestion_muestras').order_by('nombre')
        estados = EstadoMuestras.objects.using('gestion_muestras').order_by('descripcion')
        return render(request, "gestionmuestras/consultorMedidas.html", {"memorias":memorias, "tiposMuestras":tiposMuestras, "determinaciones":determinaciones, "clientes":clientes, "estados":estados})

@permission_required('auth.visualizacion_muestras')
def listadoChurros(request):
    return render(request, "gestionmuestras/listadoChurros.html", {})


@permission_required('auth.visualizacion_muestras')
def listadoChurrosDatos(request):
    muestras = Churros.objects.using('geslabChurros').order_by('-f_analisis').values('memoria__memoria', 'muestra__nombre', 'analisis__descripcion', 'isotopo__descripcion', 'f_rec_ini', 'f_rec_fin', 'dias', 'f_analisis', 'muestra_compartida', 'actividad', 'error', 'lid', 'submuestras', 'tiempo_medida', 'cantidad_muestra_recogida', 'cantidad_muestra_analizada', 'rendimiento')

    return JsonResponse(list(muestras), safe=False)

@permission_required('auth.visualizacion_muestras')
def capturarInformeAlfa(request):
    if request.method == "POST":
        fichero = request.FILES['inputFile']
        datos = procesarInformeAlfa(fichero)
        return render(request, "gestionmuestras/capturarInformeAlfa.html", {"datos":datos})
    else:
        return render(request, "gestionmuestras/capturarInformeAlfa.html", {})

@permission_required('auth.visualizacion_muestras')
def capturarDBFgestmues(request):
    if request.method == "POST":
        fichero = request.FILES['inputFile']

        with open("recogida.dbf", "wb+") as f:
            for chunk in fichero.chunks():
                f.write(chunk)
        
        datos = procesarDBFgestmues("recogida.dbf")
        if "recogida.dbf":
            os.remove("recogida.dbf")
        return render(request, "gestionmuestras/cargarDBFgestmues.html", {"datos":datos})
    else:
        return render(request, "gestionmuestras/cargarDBFgestmues.html", {})
    
@permission_required('auth.visualizacion_muestras')
def capturarExcelCopuma(request):
    if request.method == "POST":
        fichero = request.FILES['inputFile']
        with open("excel.xlsx", "wb+") as f:
            for chunk in fichero.chunks():
                f.write(chunk)
        
        datos = procesarExcelCopuma("excel.xlsx")
        return render(request, "gestionmuestras/capturarExcelCopuma.html", {"datos":datos})
    else:
        return render(request, "gestionmuestras/capturarExcelCopuma.html", {})
    
@permission_required('auth.visualizacion_muestras')
def infoAlicuota(request, id_alicuota):
    tratamientos = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=id_alicuota).values('identificador','cod_reducido','tratamiento__descripcion','fecha_inicio','fecha_fin','analista__nombre','paso_actual')
    return JsonResponse(list(tratamientos), safe=False)


@permission_required('auth.visualizacion_muestras')
def verificarMuestra(request):
    '''
    from django.contrib.auth.models import Group
    users_in_group = Group.objects.get(name="group name").user_set.all()
    
    if user in users_in_group:
        # do something
    '''
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_muestra')).get()

        
    return JsonResponse({}, safe=False)

@permission_required('auth.visualizacion_muestras')
def consultaDuplicados(request):
    if request.method == "POST":

        muestrasConDuplicados = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(cod_reducido__contains="DU", id_muestra_analitica__id_historico_recogida__fecha_hora_recogida__range=(request.POST.get('fechaInicio'),request.POST.get('fechaFin'))).filter(cod_reducido__contains=request.POST.get('procedimiento')).values_list("id_muestra_analitica__id_historico_recogida")

        muestras = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(cod_reducido__contains=request.POST.get('procedimiento'), id_muestra_analitica__id_historico_recogida__in=list(muestrasConDuplicados), tratamiento__identificador=3).order_by('id_muestra_analitica__id_historico_recogida')

        resultados = []
        resultado = None
        labels, data1, data2 = [], [], []

        for muestra in muestras:
            duplicada = muestra.cod_reducido.endswith("DU")
            if resultado is None:
                resultado = {}
                resultado["muestra"] = muestra.id_muestra_analitica.id_historico_recogida.identificador
            if resultado["muestra"] != muestra.id_muestra_analitica.id_historico_recogida.identificador:
                if resultado["muestra"] is not None and ("actividad_original" in resultado and resultado["actividad_original"] is not None) and ("actividad_duplicada" in resultado and resultado["actividad_duplicada"] is not None):
                    labels.append(resultado["muestra"])
                    data1.append([round(resultado["actividad_original"]+resultado["error_original"], 3), round(resultado["actividad_original"], 3), round(resultado["actividad_original"]-resultado["error_original"], 3)])
                    data2.append([round(resultado["actividad_duplicada"]+resultado["error_duplicada"], 3), round(resultado["actividad_duplicada"], 3), round(resultado["actividad_duplicada"]-resultado["error_duplicada"], 3)])
                    resultado = calcularControles(resultado, request.POST.get('procedimiento'), request.POST.get('medida'))
                resultados.append(resultado)
                resultado = {}
                resultado["muestra"] = muestra.id_muestra_analitica.id_historico_recogida.identificador

            if duplicada:
                resultado["duplicada"] = muestra.cod_reducido
            else:
                resultado["original"] = muestra.cod_reducido
            try:
                registroAB = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(cod_reducido=muestra.cod_reducido, parametro=request.POST.get('medida')).get()
                if duplicada:
                    resultado["actividad_duplicada"] = registroAB.actividad
                    resultado["error_duplicada"] = registroAB.incertidumbre
                    resultado["amd_duplicada"] = registroAB.amd
                else:
                    resultado["actividad_original"] = registroAB.actividad
                    resultado["error_original"] = registroAB.incertidumbre
                    resultado["amd_original"] = registroAB.amd
                    
            except:
                if duplicada:
                    resultado["actividad_duplicada"] = None
                    resultado["error_duplicada"] = None
                    resultado["amd_duplicada"] = None
                else:
                    resultado["actividad_original"] = None
                    resultado["error_original"] = None
                    resultado["amd_original"] = None
        
        if resultado and resultado["muestra"] is not None and resultado["actividad_original"] is not None and resultado["actividad_duplicada"] is not None:
            labels.append(resultado["muestra"])
            data1.append([round(resultado["actividad_original"]+resultado["error_original"], 3), round(resultado["actividad_original"], 3), round(resultado["actividad_original"]-resultado["error_original"], 3)])
            data2.append([round(resultado["actividad_duplicada"]+resultado["error_duplicada"], 3), round(resultado["actividad_duplicada"], 3), round(resultado["actividad_duplicada"]-resultado["error_duplicada"], 3)])
            resultado = calcularControles(resultado, request.POST.get('procedimiento'), request.POST.get('medida'))
        resultados.append(resultado)

        return render(request, "gestionmuestras/consultaDuplicados.html", {"resultados":resultados, "labels": labels, "data1": data1, "data2": data2})
    else:
        return render(request, "gestionmuestras/consultaDuplicados.html", {})
    
def calcularControles(resultado, procedimiento, medida):
    if resultado["actividad_original"] < resultado["amd_original"] or resultado["actividad_duplicada"] < resultado["amd_duplicada"]:
        resultado["control"] = "OK"
        resultado["descripcion"] = "Valor inferior al AMD"
        resultado["factor"] = 1
        resultado["factor2"] = "OK"
        return resultado
    else:
        if resultado["actividad_original"] > resultado["actividad_duplicada"]:
            return verificarResultado(resultado, resultado["actividad_original"], resultado["error_original"], resultado["actividad_duplicada"], resultado["error_duplicada"], obtenerFactor(procedimiento, medida))
        else:
            return verificarResultado(resultado, resultado["actividad_duplicada"], resultado["error_duplicada"], resultado["actividad_original"], resultado["error_original"], obtenerFactor(procedimiento, medida))

def verificarResultado(resultado, mayor, errorAbajoMayor, menor, errorArribaMenor, factorCorrecto):
    factor = round(mayor / menor,2)
    if factor > factorCorrecto:
        resultado["control"] = "ERROR"
        resultado["descripcion"] = "Valor fuera de rango"
        resultado["factor"] = factor
    else:
        resultado["control"] = "OK"
        resultado["descripcion"] = "Valor dentro de rango"
        resultado["factor"] = factor

    rango1Max = mayor + errorAbajoMayor
    rango1Min = mayor - errorAbajoMayor
    rango2Max = menor + errorArribaMenor
    rango2Min = menor - errorArribaMenor

    # comprobar si coinciden valores entre los rangos
    if (rango1Max > rango2Max and rango1Min < rango2Max) or (rango1Max > rango2Min and rango1Min < rango2Min) or (rango1Max > rango2Max and rango1Min < rango2Min) or (rango1Max < rango2Max and rango1Min > rango2Min):
        resultado["factor2"] = "OK"
    else:
        resultado["factor2"] = "ERROR"
    return resultado

def obtenerFactor(procedimiento, medida):
    if procedimiento == "AB" and medida == "ALFA":
        return 1.3
    if procedimiento == "AB" and medida == "BETA":
        return 1.1
    if procedimiento == "CP" and medida == "ALFA":
        return 1.4
    return 1

@permission_required('auth.gestion_recolector')
def consultarMuestrasRecoger(request):
    return render(request, "gestionmuestras/muestrasRecolectar.html", {})


@permission_required('auth.gestion_recolector')
def consultarMuestrasRecogerDatos(request):
    muestras = GestmuesColeccion.objects.using('gestion_muestras').values('n_recogida__numero', 'n_recogida__csn__nombre', 'n_recogida__procedencia__nombre', 'n_recogida__memoria__memoria', 'csn__nombre', 'recoge', 'n_recogida__suministra', 'suministra', 'observaciones', 'n_recogida__observaciones', 'recogido', 'fecha_recogida_inicial', 'fecha_recogida_final', 'fecha_recepcion', 'conservacion', 'nfiltro', 'ibomba', 'mes')
    return JsonResponse(list(muestras), safe=False)

@permission_required('auth.visualizacion_muestras')
def consultarVRAEx(request):
    insertadas = []
    muestras = HistoricoRecogida.objects.using('gestion_muestras').filter(codigo_recogida__codigo_memoria='G', fecha_hora_recogida__gte='2022-01-01 00:00:00').order_by('-identificador')
    for m in muestras:
        procedencia = RelacionProcedenciasGestionVraex.objects.using('gestion_muestras').filter(id_gestion_muestras=m.codigo_recogida.codigo_procedencia.codigo).get()
        tritio = {"actividad":0, "error":0, "amd":0, "muestras":0, "fecha_recogida_inicial":m.fecha_hora_recogida, "fecha_recogida_final":m.fecha_hora_recogida_2, "fecha_medida": None, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.id_vraex, "Muestra": m.codigo_recogida.codigo_csn.codigo, "CodIsotopo": "H", "CodAnalisis": "H", "Masa": 3}
        alfa = {"actividad":0, "error":0, "amd":0, "muestras":0, "fecha_recogida_inicial":m.fecha_hora_recogida, "fecha_recogida_final":m.fecha_hora_recogida_2, "fecha_medida": None, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.id_vraex, "Muestra": m.codigo_recogida.codigo_csn.codigo, "CodIsotopo": "", "CodAnalisis": "AT", "Masa": -1}
        beta = {"actividad":0, "error":0, "amd":0, "muestras":0, "fecha_recogida_inicial":m.fecha_hora_recogida, "fecha_recogida_final":m.fecha_hora_recogida_2, "fecha_medida": None, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.id_vraex, "Muestra": m.codigo_recogida.codigo_csn.codigo, "CodIsotopo": "", "CodAnalisis": "BT", "Masa": -1}
        '''
        if not RelacionProcedenciasGestionVraex.objects.using('gestion_muestras').filter(id_gestion_muestras=m.codigo_recogida.codigo_procedencia.codigo).exists():
            print("No existe relacion. Crearla")
            valor = input("Introduce el id relacionado con la muestra (" + str(m.codigo_recogida.codigo_procedencia.codigo) +" , " + m.codigo_recogida.codigo_procedencia.nombre +")")
            relacion = RelacionProcedenciasGestionVraex(id_gestion_muestras=m.codigo_recogida.codigo_procedencia.codigo, id_vraex=valor)
            relacion.save(using='gestion_muestras')
        '''
        alicuotas = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica__id_historico_recogida=m.identificador)
        for a in alicuotas:
            if a.tratamiento.identificador == 18:
                try:
                    medida = RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica=a.id_muestra_analitica.identificador, id_parametro_analitica=46).get()
                    if "<" in medida.valor:
                        tritio["actividad"] = 0
                        tritio["error"] = 0
                        tritio["amd"] = tritio["amd"] + float(medida.valor.split("<")[1])/100
                        tritio["muestras"] = tritio["muestras"] + 1
                        tritio["fecha_medida"] = a.fecha_inicio
                    elif "±" in medida.valor:
                        tritio["actividad"] = tritio["actividad"] + float(medida.valor.split("±")[0])/100
                        tritio["amd"] = RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica=a.id_muestra_analitica.identificador, id_parametro_analitica=44).get().valor/100
                        tritio["muestras"] = tritio["muestras"] + 1
                        tritio["fecha_medida"] = a.fecha_inicio
                except:
                    continue
                
            elif a.tratamiento.identificador == 3:
                medidas = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(cod_reducido=a.cod_reducido)
                for m in medidas:
                    if m.parametro == "ALFA":
                        alfa["actividad"] = alfa["actividad"] + m.actividad*1000
                        alfa["error"] = alfa["error"] + m.incertidumbre*1000
                        alfa["amd"] = alfa["amd"] + m.amd*1000
                        alfa["muestras"] = alfa["muestras"] + 1
                        alfa["fecha_medida"] = m.fecha
                    elif m.parametro == "BETA":
                        beta["actividad"] = beta["actividad"] + m.actividad*1000
                        beta["error"] = beta["error"] + m.incertidumbre*1000
                        beta["amd"] = beta["amd"] + m.amd*1000
                        beta["muestras"] = beta["muestras"] + 1
                        beta["fecha_medida"] = m.fecha
        if tritio["muestras"] > 0:
            tritio["actividad"] = tritio["actividad"] / tritio["muestras"]
            tritio["error"] = tritio["error"] / tritio["muestras"]
            tritio["amd"] = tritio["amd"] / tritio["muestras"]
            
            if not ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra=tritio["Muestra"], isotopo_codisotopo=tritio["CodIsotopo"], isotopo_analisis_codanalisis=tritio["CodAnalisis"], fecha_recogida_inicial=tritio["fecha_recogida_inicial"]).exists():
          
          
                insertadas.append(tritio)
                ValorMuestraCopumaVolatil(motivo_muestreo_codmuestreo=tritio["motivo"], fecha_recogida_inicial=tritio["fecha_recogida_inicial"], fecha_recogida_final=tritio["fecha_recogida_final"], fecha_analisis=tritio["fecha_medida"], instalacion_codinstalacion=tritio["Instalacion"], laboratorio_codlaboratorio=tritio["Laboratorio"], muestra_codmuestra=tritio["Muestra"], isotopo_codisotopo=tritio["CodIsotopo"], isotopo_analisis_codanalisis=tritio["CodAnalisis"], estacion_codprocedencia=tritio["Procedencia"], masa=tritio["Masa"], metaestable="N", compartida="N", actividad_medida=tritio["actividad"], error_actividad_medida=tritio["error"], lid_medida=tritio["amd"], numero_muestras=tritio["muestras"],fecha_subida_fichero=datetime.now(), verificado=0, csn=0).save(using='gestion_memoria')
        if alfa["muestras"] > 0:
            alfa["actividad"] = alfa["actividad"] / alfa["muestras"]
            alfa["error"] = alfa["error"] / alfa["muestras"]
            alfa["amd"] = alfa["amd"] / alfa["muestras"]
            if not ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra=alfa["Muestra"], isotopo_codisotopo=alfa["CodIsotopo"], isotopo_analisis_codanalisis=alfa["CodAnalisis"], fecha_recogida_inicial=alfa["fecha_recogida_inicial"]).exists():
                print("guardar")
                print("Alfa:", alfa)
                insertadas.append(alfa)
                ValorMuestraCopumaVolatil(motivo_muestreo_codmuestreo=alfa["motivo"], fecha_recogida_inicial=alfa["fecha_recogida_inicial"], fecha_recogida_final=alfa["fecha_recogida_final"], fecha_analisis=alfa["fecha_medida"], instalacion_codinstalacion=alfa["Instalacion"], laboratorio_codlaboratorio=alfa["Laboratorio"], muestra_codmuestra=alfa["Muestra"], isotopo_codisotopo=alfa["CodIsotopo"], isotopo_analisis_codanalisis=alfa["CodAnalisis"], estacion_codprocedencia=alfa["Procedencia"], masa=alfa["Masa"], metaestable="N", compartida="N", actividad_medida=alfa["actividad"], error_actividad_medida=alfa["error"], lid_medida=alfa["amd"], numero_muestras=alfa["muestras"],fecha_subida_fichero=datetime.now(), verificado=0, csn=0).save(using='gestion_memoria')
        if beta["muestras"] > 0:
            beta["actividad"] = beta["actividad"] / beta["muestras"]
            beta["error"] = beta["error"] / beta["muestras"]
            beta["amd"] = beta["amd"] / beta["muestras"]
            if not ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra=beta["Muestra"], isotopo_codisotopo=beta["CodIsotopo"], isotopo_analisis_codanalisis=beta["CodAnalisis"], fecha_recogida_inicial=beta["fecha_recogida_inicial"]).exists():
                print("guardar")
                print("Beta:", beta)
                insertadas.append(beta)
                ValorMuestraCopumaVolatil(motivo_muestreo_codmuestreo=beta["motivo"], fecha_recogida_inicial=beta["fecha_recogida_inicial"], fecha_recogida_final=beta["fecha_recogida_final"], fecha_analisis=beta["fecha_medida"], instalacion_codinstalacion=beta["Instalacion"], laboratorio_codlaboratorio=beta["Laboratorio"], muestra_codmuestra=beta["Muestra"], isotopo_codisotopo=beta["CodIsotopo"], isotopo_analisis_codanalisis=beta["CodAnalisis"], estacion_codprocedencia=beta["Procedencia"], masa=beta["Masa"], metaestable="N", compartida="N", actividad_medida=beta["actividad"], error_actividad_medida=beta["error"], lid_medida=beta["amd"], numero_muestras=beta["muestras"],fecha_subida_fichero=datetime.now(), verificado=0, csn=0).save(using='gestion_memoria')
        if tritio["muestras"] > 0 or alfa["muestras"] > 0 or beta["muestras"] > 0:

            '''
            if tritio["muestras"] > 0:
                guardarMedidaVraex(tritio)
            if alfa["muestras"] > 0:
                guardarMedidaVraex(alfa)
            if beta["muestras"] > 0:
                guardarMedidaVraex(beta)
            '''
    return JsonResponse({"insertadas":insertadas}, safe=False)

# metodos crud para gestion de codigos de muestras
@permission_required('auth.insercion_muestras')
def gestionCodigosMuestras(request):
    return render(request, "gestionmuestras/crudCodigosMuestras.html", {})


@permission_required('auth.insercion_muestras')
def gestionCodigosMuestrasDatos(request):
    codigos = CodMuestras.objects.using('gestion_muestras').order_by('codigo').values('codigo', 'nombre', 'tipo__descripcion', 'etiquetas', 'nombre_pt')
    return JsonResponse(list(codigos), safe=False)

@permission_required('auth.insercion_muestras')
def gestionCodigosMuestrasNuevo(request):
    if request.method == "POST":
        cod = CodMuestras(codigo=request.POST.get('codigo'), nombre=request.POST.get('nombre'), tipo=TipoDeMuestras.objects.using('gestion_muestras').filter(tipo_muestra_id=request.POST.get('tipo')).get(), etiquetas=request.POST.get('etiquetas'), nombre_pt=request.POST.get('nombre_pt'))
        cod.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudCodigosMuestras.html", {})
    else:
        # devuelve el formulario para crear un nuevo codigo de muestra
        return render(request, "gestionmuestras/crudFormulario.html", {"form":CodMuestrasForm()})
    
@permission_required('auth.insercion_muestras')
def gestionCodigosMuestrasEditar(request):
    if request.POST.get('consulta') != '1':
        cod = CodMuestras.objects.using('gestion_muestras').filter(codigo=request.POST.get('codigo')).get()
        cod.nombre = request.POST.get('nombre')
        cod.tipo = TipoDeMuestras.objects.using('gestion_muestras').filter(tipo_muestra_id=request.POST.get('tipo')).get()
        cod.etiquetas = request.POST.get('etiquetas')
        cod.nombre_pt = request.POST.get('nombre_pt')
        cod.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudCodigosMuestras.html", {})
    else:
        cod = CodMuestras.objects.using('gestion_muestras').filter(codigo=request.POST.get('codigo')).values('codigo', 'nombre', 'tipo__tipo_muestra_id', 'etiquetas', 'nombre_pt')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":CodMuestrasEditarForm(initial=cod)})

@permission_required('auth.insercion_muestras')
def gestionCodigosMuestrasBorrar(request):
    if request.method == "POST":
        cod = CodMuestras.objects.using('gestion_muestras').filter(codigo=request.POST.get('codigo')).get()
        cod.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para gestion de clientes
# parametros: identificador, nombre, descripcion, direccion, telefono, fax, email, persona_contacto, nif, idioma, password, informar 
@permission_required('auth.insercion_muestras')
def gestionClientes(request):
    return render(request, "gestionmuestras/crudClientes.html", {})

@permission_required('auth.insercion_muestras')
def gestionClientesDatos(request):
    clientes = Clientes.objects.using('gestion_muestras').order_by('nombre').values('identificador', 'nombre', 'direccion', 'telefono', 'fax', 'email', 'persona_contacto', 'descripcion', 'nif', 'idioma', 'password', 'informar')
    return JsonResponse(list(clientes), safe=False)

@permission_required('auth.insercion_muestras')
def gestionClientesNuevo(request):
    print(request.POST)
    if request.method == "POST":
        cliente = Clientes(nombre=request.POST.get('nombre'), direccion=request.POST.get('direccion'), telefono=request.POST.get('telefono'), fax=request.POST.get('fax'), email=request.POST.get('email'), persona_contacto=request.POST.get('persona_contacto'), descripcion=request.POST.get('descripcion'), nif = request.POST.get('nif'))
        cliente.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudClientes.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":ClientesForm()})
    
@permission_required('auth.insercion_muestras')
def gestionClientesEditar(request):
    if request.POST.get('consulta') != '1':
        cliente = Clientes.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        cliente.nombre = request.POST.get('nombre')
        cliente.direccion = request.POST.get('direccion')
        cliente.telefono = request.POST.get('telefono')
        cliente.fax = request.POST.get('fax')
        cliente.email = request.POST.get('email')
        cliente.persona_contacto = request.POST.get('persona_contacto')
        cliente.descripcion = request.POST.get('descripcion')
        cliente.nif = request.POST.get('nif')
        cliente.idioma = request.POST.get('idioma')
        cliente.password = request.POST.get('password')
        cliente.informar = request.POST.get('informar')
        cliente.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudClientes.html", {})
    else:
        cliente = Clientes.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).values('identificador', 'nombre', 'direccion', 'telefono', 'fax', 'email', 'persona_contacto', 'descripcion', 'nif', 'idioma', 'password', 'informar')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":ClientesEditarForm(initial=cliente)})

@permission_required('auth.insercion_muestras')
def gestionClientesBorrar(request):
    if request.method == "POST":
        cliente = Clientes.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        cliente.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)

# metodos crud para gestion de memorias
# parametros: codigo_memoria, memoria, base_datos_geslab, descripcion, ajuste_semana
@permission_required('auth.insercion_muestras')
def gestionMemorias(request):
    return render(request, "gestionmuestras/crudMemorias.html", {})

@permission_required('auth.insercion_muestras')
def gestionMemoriasDatos(request):
    memorias = Memorias.objects.using('gestion_muestras').order_by('memoria').values('codigo_memoria', 'memoria', 'base_datos_geslab', 'descripcion', 'ajuste_semana')
    return JsonResponse(list(memorias), safe=False)

@permission_required('auth.insercion_muestras')
def gestionMemoriasNuevo(request):
    if request.method == "POST":
        memoria = Memorias(memoria=request.POST.get('memoria'), base_datos_geslab=request.POST.get('base_datos_geslab'), descripcion=request.POST.get('descripcion'), ajuste_semana=request.POST.get('ajuste_semana'))
        memoria.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudMemorias.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":MemoriasForm()})
    
@permission_required('auth.insercion_muestras')
def gestionMemoriasEditar(request):
    if request.POST.get('consulta') != '1':
        memoria = Memorias.objects.using('gestion_muestras').filter(codigo_memoria=request.POST.get('codigo_memoria')).get()
        memoria.memoria = request.POST.get('memoria')
        memoria.base_datos_geslab = request.POST.get('base_datos_geslab')
        memoria.descripcion = request.POST.get('descripcion')
        memoria.ajuste_semana = request.POST.get('ajuste_semana')
        memoria.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudMemorias.html", {})
    else:
        memoria = Memorias.objects.using('gestion_muestras').filter(codigo_memoria=request.POST.get('codigo_memoria')).values('codigo_memoria', 'memoria', 'base_datos_geslab', 'descripcion', 'ajuste_semana')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":MemoriasEditarForm(initial=memoria)})

@permission_required('auth.insercion_muestras')
def gestionMemoriasBorrar(request):
    if request.method == "POST":
        memoria = Memorias.objects.using('gestion_muestras').filter(codigo_memoria=request.POST.get('codigo_memoria')).get()
        memoria.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)

# metodos crud para gestion de muestra actual codigo
# parametros: codigo, posicion, duplicada, duplicada_pos, control, control_pos, blanco, blanco_pos, tiempo_en_lab

@permission_required('auth.insercion_muestras')
def gestionMuestraActualCodigo(request):
    return render(request, "gestionmuestras/crudMuestraActualCodigo.html", {})

@permission_required('auth.insercion_muestras')
def gestionMuestraActualCodigoDatos(request):
    codigos = MuestraActualCodigo.objects.using('gestion_muestras').order_by('codigo').values('id', 'codigo', 'posicion', 'duplicada', 'duplicada_pos', 'control', 'control_pos', 'blanco', 'blanco_pos', 'tiempo_en_lab')
    return JsonResponse(list(codigos), safe=False)

@permission_required('auth.insercion_muestras')
def gestionMuestraActualCodigoNuevo(request):
    if request.method == "POST":
        codigo = MuestraActualCodigo(codigo=request.POST.get('codigo'), posicion=request.POST.get('posicion'), duplicada=request.POST.get('duplicada'), duplicada_pos=request.POST.get('duplicada_pos'), control=request.POST.get('control'), control_pos=request.POST.get('control_pos'), blanco=request.POST.get('blanco'), blanco_pos=request.POST.get('blanco_pos'), tiempo_en_lab=request.POST.get('tiempo_en_lab'))
        codigo.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudMuestraActualCodigo.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":MuestraActualCodigoForm()})
    
@permission_required('auth.insercion_muestras')
def gestionMuestraActualCodigoEditar(request):
    if request.POST.get('consulta') != '1':
        codigo = MuestraActualCodigo.objects.using('gestion_muestras').filter(id=request.POST.get('codigo')).get()
        codigo.posicion = request.POST.get('posicion')
        codigo.duplicada = request.POST.get('duplicada')
        codigo.duplicada_pos = request.POST.get('duplicada_pos')
        codigo.control = request.POST.get('control')
        codigo.control_pos = request.POST.get('control_pos')
        codigo.blanco = request.POST.get('blanco')
        codigo.blanco_pos = request.POST.get('blanco_pos')
        codigo.tiempo_en_lab = request.POST.get('tiempo_en_lab')
        codigo.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudMuestraActualCodigo.html", {})
    else:
        codigo = MuestraActualCodigo.objects.using('gestion_muestras').filter(id=request.POST.get('codigo')).values('codigo', 'posicion', 'duplicada', 'duplicada_pos', 'control', 'control_pos', 'blanco', 'blanco_pos', 'tiempo_en_lab')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":MuestraActualCodigoEditarForm(initial=codigo)})

@permission_required('auth.insercion_muestras')
def gestionMuestraActualCodigoBorrar(request):
    if request.method == "POST":
        codigo = MuestraActualCodigo.objects.using('gestion_muestras').filter(id=request.POST.get('codigo')).get()
        codigo.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para gestion de parametros de muestra
# parametros: identificador, nombre, descripcion, muestra
@permission_required('auth.insercion_muestras')
def gestionParametro(request):
    return render(request, "gestionmuestras/crudParametrosMuestra.html", {})

@permission_required('auth.insercion_muestras')
def gestionParametroDatos(request):
    parametros = ParametrosMuestra.objects.using('gestion_muestras').order_by('nombre').values('identificador', 'nombre', 'descripcion', 'muestra')
    return JsonResponse(list(parametros), safe=False)

@permission_required('auth.insercion_muestras')
def gestionParametroNuevo(request):
    if request.method == "POST":
        parametro = ParametrosMuestra(nombre=request.POST.get('nombre'), descripcion=request.POST.get('descripcion'), muestra=request.POST.get('muestra'))
        parametro.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudParametrosMuestra.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":ParametrosMuestraForm()})
    
@permission_required('auth.insercion_muestras')
def gestionParametroEditar(request):
    if request.POST.get('consulta') != '1':
        parametro = ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        parametro.nombre = request.POST.get('nombre')
        parametro.descripcion = request.POST.get('descripcion')
        parametro.muestra = request.POST.get('muestra')
        parametro.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudParametrosMuestra.html", {})
    else:
        parametro = ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).values('identificador', 'nombre', 'descripcion', 'muestra')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":ParametrosMuestraEditarForm(initial=parametro)})
    
@permission_required('auth.insercion_muestras')
def gestionParametroBorrar(request):
    if request.method == "POST":
        parametro = ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        parametro.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para la gestion de la relacion de controles con tratamientos
# parametros: identificador, tipo_control, codigo, id_muestra_historico

@permission_required('auth.insercion_muestras')
def gestionRelacionControlTratamiento(request):
    return render(request, "gestionmuestras/crudControlTratamiento.html", {})

@permission_required('auth.insercion_muestras')
def gestionRelacionControlTratamientoDatos(request):
    relaciones = RelacionControlesTratamientos.objects.using('gestion_muestras').order_by('codigo').values('identificador', 'tipo_control', 'codigo', 'id_muestra_historico')
    return JsonResponse(list(relaciones), safe=False)

@permission_required('auth.insercion_muestras')
def gestionRelacionControlTratamientoNuevo(request):
    if request.method == "POST":
        relacion = RelacionControlesTratamientos(tipo_control=request.POST.get('tipo_control'), codigo=request.POST.get('codigo'), id_muestra_historico=HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_muestra_historico')).get())
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudControlTratamiento.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":RelacionControlTratamientoForm()})

@permission_required('auth.insercion_muestras')
def gestionRelacionControlTratamientoEditar(request):
    if request.POST.get('consulta') != '1':
        relacion = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        relacion.tipo_control = request.POST.get('tipo_control')
        relacion.codigo = request.POST.get('codigo')
        relacion.id_muestra_historico = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_muestra_historico')).get()
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudControlTratamiento.html", {})
    else:
        relacion = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).values('identificador', 'tipo_control', 'codigo', 'id_muestra_historico')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":RelacionControlTratamientoEditarForm(initial=relacion)})
    
@permission_required('auth.insercion_muestras')
def gestionRelacionControlTratamientoBorrar(request):
    if request.method == "POST":
        relacion = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        relacion.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para la gestion de la relacion de determinaciones con tratamientos
# parametros: id_determinacion, id_tratamiento, por_defecto
    
@permission_required('auth.insercion_muestras')
def gestionRelacionDeterminacionTratamiento(request):
    return render(request, "gestionmuestras/crudRelacionDeterminacionTratamiento.html", {})

@permission_required('auth.insercion_muestras')
def gestionRelacionDeterminacionTratamientoDatos(request):
    relaciones = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').order_by('id_determinacion').values('id_determinacion__identificador', 'id_determinacion__nombre', 'id_tratamiento__identificador', 'id_tratamiento__descripcion', 'id_tratamiento__medida')
    return JsonResponse(list(relaciones), safe=False)

@permission_required('auth.insercion_muestras')
def gestionRelacionDeterminacionTratamientoNuevo(request):
    if request.method == "POST":
        relacion = RelacionDeterminacionesTratamientos(id_determinacion=Determinaciones.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_determinacion')).get(), id_tratamiento=Tratamiento.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_tratamiento')).get(), por_defecto=request.POST.get('por_defecto'))
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudRelacionDeterminacionTratamiento.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":RelacionDeterminacionTratamientoForm()})

@permission_required('auth.insercion_muestras')
def gestionRelacionDeterminacionTratamientoEditar(request):
    if request.POST.get('consulta') != '1':
        relacion = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').filter(id_determinacion=request.POST.get('id_determinacion'), id_tratamiento=request.POST.get('id_tratamiento')).get()
        relacion.por_defecto = request.POST.get('por_defecto')
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudRelacionDeterminacionTratamiento.html", {})
    else:
        relacion = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').filter(id_determinacion=request.POST.get('id_determinacion'), id_tratamiento=request.POST.get('id_tratamiento')).values('id_determinacion', 'id_tratamiento', 'por_defecto')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":RelacionDeterminacionTratamientoEditarForm(initial=relacion)})
    
@permission_required('auth.insercion_muestras')
def gestionRelacionDeterminacionTratamientoBorrar(request):
    if request.method == "POST":
        relacion = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').filter(id_determinacion=request.POST.get('id_determinacion'), id_tratamiento=request.POST.get('id_tratamiento')).get()
        relacion.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para la gestion de las frases predefinidas
# parametros: identificador, texto, destino

@permission_required('auth.insercion_muestras')
def gestionFrasePredefinida(request):
    return render(request, "gestionmuestras/crudFrasePredefinida.html", {})

@permission_required('auth.insercion_muestras')
def gestionFrasePredefinidaDatos(request):
    frases = FrasesPredefinidas.objects.using('gestion_muestras').order_by('texto').values('identificador', 'texto', 'destino')
    return JsonResponse(list(frases), safe=False)

@permission_required('auth.insercion_muestras')
def gestionFrasePredefinidaNuevo(request):
    if request.method == "POST":
        frase = FrasesPredefinidas(texto=request.POST.get('texto'), destino=request.POST.get('destino'))
        frase.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudFrasePredefinida.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":FrasesPredefinidasForm()})
    
@permission_required('auth.insercion_muestras')
def gestionFrasePredefinidaEditar(request):
    if request.POST.get('consulta') != '1':
        frase = FrasesPredefinidas.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        frase.texto = request.POST.get('texto')
        frase.destino = request.POST.get('destino')
        frase.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudFrasePredefinida.html", {})
    else:
        frase = FrasesPredefinidas.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).values('identificador', 'texto', 'destino')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":FrasesPredefinidasEditarForm(initial=frase)})
    
@permission_required('auth.insercion_muestras')
def gestionFrasePredefinidaBorrar(request):
    if request.method == "POST":
        frase = FrasesPredefinidas.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        frase.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para la gestion de las determinaciones
# parametros: identificador, nombre

@permission_required('auth.insercion_muestras')
def gestionDeterminacion(request):
    return render(request, "gestionmuestras/crudDeterminacion.html", {})

@permission_required('auth.insercion_muestras')
def gestionDeterminacionDatos(request):
    determinaciones = Determinaciones.objects.using('gestion_muestras').order_by('nombre').values('identificador', 'nombre')
    return JsonResponse(list(determinaciones), safe=False)

@permission_required('auth.insercion_muestras')
def gestionDeterminacionNuevo(request):
    if request.method == "POST":
        determinacion = Determinaciones(nombre=request.POST.get('nombre'))
        determinacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudDeterminacion.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":DeterminacionesForm()})

@permission_required('auth.insercion_muestras')
def gestionDeterminacionEditar(request):
    if request.POST.get('consulta') != '1':
        determinacion = Determinaciones.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        determinacion.nombre = request.POST.get('nombre')
        determinacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudDeterminacion.html", {})
    else:
        determinacion = Determinaciones.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).values('identificador', 'nombre')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":DeterminacionesEditarForm(initial=determinacion)})
    
@permission_required('auth.insercion_muestras')
def gestionDeterminacionBorrar(request):
    if request.method == "POST":
        determinacion = Determinaciones.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        determinacion.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para la gestion de los tratamientos
# parametros: identificador, descripcion, medida, tiempo_en_lab, alcance

@permission_required('auth.insercion_muestras')
def gestionTratamiento(request):
    return render(request, "gestionmuestras/crudTratamiento.html", {})

@permission_required('auth.insercion_muestras')
def gestionTratamientoDatos(request):
    tratamientos = Tratamiento.objects.using('gestion_muestras').order_by('descripcion').values('identificador', 'descripcion', 'medida', 'tiempo_en_lab', 'alcance')
    return JsonResponse(list(tratamientos), safe=False)

@permission_required('auth.insercion_muestras')
def gestionTratamientoNuevo(request):
    if request.method == "POST":
        tratamiento = Tratamiento(descripcion=request.POST.get('descripcion'), medida=request.POST.get('medida'), tiempo_en_lab=request.POST.get('tiempo_en_lab'), alcance=request.POST.get('alcance'))
        tratamiento.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudTratamiento.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":TratamientoForm()})
    
@permission_required('auth.insercion_muestras')
def gestionTratamientoEditar(request):
    if request.POST.get('consulta') != '1':
        tratamiento = Tratamiento.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        tratamiento.descripcion = request.POST.get('descripcion')
        tratamiento.medida = request.POST.get('medida')
        tratamiento.tiempo_en_lab = request.POST.get('tiempo_en_lab')
        tratamiento.alcance = request.POST.get('alcance')
        tratamiento.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudTratamiento.html", {})
    else:
        tratamiento = Tratamiento.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).values('identificador', 'descripcion', 'medida', 'tiempo_en_lab', 'alcance')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":TratamientoEditarForm(initial=tratamiento)})
    
@permission_required('auth.insercion_muestras')
def gestionTratamientoBorrar(request):
    if request.method == "POST":
        tratamiento = Tratamiento.objects.using('gestion_muestras').filter(identificador=request.POST.get('identificador')).get()
        tratamiento.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)

# metodos crud para la gestion de la relacion de tratamiento con responsables
# parametros: procedimiento, responsable, sustituto_1, sustituto_2, sustituto_3, descripcion

@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoResponsable(request):
    return render(request, "gestionmuestras/crudRelacionTratamientoResponsable.html", {})

@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoResponsableDatos(request):
    relaciones = RelacionProcedimientosResponsables.objects.using('gestion_muestras').order_by('procedimiento').values('procedimiento__identificador', 'procedimiento__descripcion', 'responsable', 'sustituto_1', 'sustituto_2', 'sustituto_3', 'descripcion')
    return JsonResponse(list(relaciones), safe=False)

@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoResponsableNuevo(request):
    if request.method == "POST":
        relacion = RelacionProcedimientosResponsables(procedimiento=request.POST.get('procedimiento'), responsable=request.POST.get('responsable'), sustituto_1=request.POST.get('sustituto_1'), sustituto_2=request.POST.get('sustituto_2'), sustituto_3=request.POST.get('sustituto_3'), descripcion=request.POST.get('descripcion'))
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudRelacionTratamientoResponsable.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":RelacionTratamientoResponsableForm()})
    
@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoResponsableEditar(request):
    if request.POST.get('consulta') != '1':
        relacion = RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(procedimiento__identificador=request.POST.get('identificador')).get()
        relacion.responsable = request.POST.get('responsable')
        relacion.sustituto_1 = request.POST.get('sustituto_1')
        relacion.sustituto_2 = request.POST.get('sustituto_2')
        relacion.sustituto_3 = request.POST.get('sustituto_3')
        relacion.descripcion = request.POST.get('descripcion')
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudRelacionTratamientoResponsable.html", {})
    else:
        print(request.POST)
        relacion = RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(procedimiento__identificador=request.POST.get('identificador')).values('procedimiento', 'responsable', 'sustituto_1', 'sustituto_2', 'sustituto_3', 'descripcion')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":RelacionTratamientoResponsableEditarForm(initial=relacion)})
    
@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoResponsableBorrar(request):
    if request.method == "POST":
        relacion = RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(procedimiento=request.POST.get('identificador')).get()
        relacion.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
# metodos crud para la gestion de tratamiento codigos muestras
# parametros: id, id_muestra_codigo, id_tratamiento

@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoMuestraCodigo(request):
    return render(request, "gestionmuestras/crudTratamientoCodigoMuestra.html", {})

@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoMuestraCodigoDatos(request):
    relaciones = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').order_by('id_muestra_codigo').values('id', 'id_muestra_codigo', 'id_muestra_codigo__codigo', 'id_tratamiento', 'id_tratamiento__descripcion')
    return JsonResponse(list(relaciones), safe=False)

@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoMuestraCodigoNuevo(request):
    if request.method == "POST":
        relacion = RelacionTratamientosMuestraCodigo(id_muestra_codigo=request.POST.get('id_muestra_codigo'), id_tratamiento=request.POST.get('id_tratamiento'))
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudTratamientoCodigoMuestra.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":TratamientosMuestrasCodigoForm()})
    
@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoMuestraCodigoEditar(request):
    if request.POST.get('consulta') != '1':
        relacion = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id=request.POST.get('id')).get()
        relacion.id_muestra_codigo = request.POST.get('id_muestra_codigo')
        relacion.id_tratamiento = request.POST.get('id_tratamiento')
        relacion.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudTratamientoCodigoMuestra.html", {})
    else:
        relacion = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id=request.POST.get('id')).values('id', 'id_muestra_codigo', 'id_tratamiento')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":TratamientosMuestrasCodigoEditarForm(initial=relacion)})
    
@permission_required('auth.insercion_muestras')
def gestionRelacionTratamientoMuestraCodigoBorrar(request):
    if request.method == "POST":
        relacion = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id=request.POST.get('id')).get()
        relacion.delete(using='gestion_muestras')
        return JsonResponse({}, safe=False)
    else:
        return JsonResponse({}, safe=False)
    
