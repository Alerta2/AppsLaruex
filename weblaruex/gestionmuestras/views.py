from django.shortcuts import redirect, render
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

from datetime import datetime, timedelta

import io

from gestionmuestras.funciones_procesado import *

import pandas as pd

import qrcode
from PIL import Image, ImageDraw, ImageFont

import csv
import os
import sys
import base64
from django.contrib.auth.models import User, Group
import secrets

@permission_required('auth.gestion_muestras')
def opcionesGestionMuestras(request):
    controlesTratatamiento = RelacionControlesTratamientos.objects.using('gestion_muestras')
    #crearTrillo()
    #return crearInformeTrilloCarbon(request)
    #return crearInformeTrilloEspectrometría(request)
    
    return render(
        request,
        "gestionmuestras/gmuestras.html",
        {
            "controlesTratamiento": controlesTratatamiento
        }
    )
    

def crearTrillo():
    muestras = [14329, 14359, 14408, 14331, 14375, 14409, 14412, 14330, 14360, 14372, 14407, 14373]
    
    for m in muestras:
        obtenerMedidas(m)

def obtenerMedidas(muestra):
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=muestra).get()
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida=muestra)
    if medidas.exists():
        if "-" in muestra.referencia_cliente:
            cacularActividades(muestra, medidas, muestra.referencia_cliente.split("-")[0].replace(" ",""), 1, False)
            cacularActividades(muestra, medidas, muestra.referencia_cliente.split("-")[1].replace(" ",""), 0.0227, True)
        else:
            cacularActividades(muestra, medidas, muestra.referencia_cliente, 1, False)

    else:
        print("No hay medidas para la muestra")

def cacularActividades(muestra, medidas, referencia, factor, recalculada):
    for m in medidas:
        if m.actividad < m.amd:
            resultado = "                    " + "{:.3e}".format(m.amd*factor)
        else:
            resultado = "{:.3e}".format(m.actividad*factor)+" "+"{:.3e}".format(m.actividad_error*factor)+" "+"{:.3e}".format(m.amd*factor)
        with open('trillo.DAT', 'a') as file:
            # Write data to the file
            agregado = ""
            if recalculada:
                agregado = "2"
            if m.determinacion_medida.determinacion.identificador != 8 or  (m.determinacion_medida.identificador >8 and m.determinacion_medida.identificador <29):
                file.write(referencia+"     C 23TRI"+muestra.codigo_recogida.codigo_procedencia.nombre.replace("TRILLO ","").zfill(3)+muestra.codigo_recogida.codigo_csn.codigo.zfill(2).replace("0"," ")+agregado+"  "+m.determinacion_medida.comentario_medida+" "+muestra.fecha_hora_recogida.strftime("%d-%m-%y")+" "+muestra.fecha_hora_recogida_2.strftime("%d-%m-%y")+"S"+m.fecha_analisis.strftime("%d-%m-%y")+" "+resultado+" 01\n")

def crearInformeTrilloCarbon(request):
    muestras = [14329, 14359, 14408, 14373]
    resultados = []
    for m in muestras:
        nuevos = obtenerMedidasCarbonTrillo(m)
        if nuevos:
            resultados = resultados + nuevos
    print(resultados)
    return render(
        request,
        "gestionmuestras/informes/informeYodo.html",
        {
            "medidas": resultados,
            "informe": {"anio":2024, "identificador":501}
        }
    )

def obtenerMedidasCarbonTrillo(muestra):
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=muestra).get()
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida=muestra)
    if medidas.exists():
        return cacularActividadYodo(muestra, medidas, muestra.referencia_cliente)
    else:
        print("No hay medidas para la muestra")
        return None

def cacularActividadYodo(muestra, medidas, referencia):
    resultados = []
    for m in medidas:
        resultado = {}
        if m.actividad < m.amd:
            resultado["actividad"] = "< "+"{:.3e}".format(m.amd)
            resultado["amd"] = "{:.3e}".format(m.amd)
        else:
            resultado["actividad"] = "{:.3e}".format(m.actividad)+"±"+"{:.3e}".format(m.actividad_error)
            resultado["amd"] = "{:.3e}".format(m.amd)
        
        resultado["referencia"] = referencia
        resultado["procedencia"] = "CN TRILLO("+muestra.codigo_recogida.codigo_procedencia.nombre.replace("TRILLO ","").zfill(3)+")"
        resultado["fecha_inicio"] = muestra.fecha_hora_recogida.strftime("%d-%m-%y")
        resultado["fecha_fin"] = muestra.fecha_hora_recogida_2.strftime("%d-%m-%y")
        resultado["fecha_referencia"] = muestra.fecha_hora_recogida_ref.strftime("%d-%m-%y")
        resultado["fecha_analisis"] = m.fecha_analisis.strftime("%d-%m-%y %H:%M")
        resultado["tiempo_contaje"] = m.tiempo_medida
        resultado["rendimiento"] = m.rendimiento
        resultado["cantidad_muestra"] = "{:.2f}".format(m.cantidad)
        resultados.append(resultado)
    return resultados


def crearInformeTrilloEspectrometría(request):
    muestra = 14412

    muestra, naturales, artificiales = obtenerMedidasEspectrometriaTrillo(muestra, False, 1)

    print(naturales[0])
    return render(
        request,
        "gestionmuestras/informes/informeEGamma.html",
        {
            "muestra": muestra,
            "cantidad": 4.0,
            "naturales": naturales,
            "artificiales": artificiales,
            "fecha_analisis": naturales[0]["fecha_analisis"],
            "informe": {"anio":2024, "identificador":501}
        }
    )

def obtenerMedidasEspectrometriaTrillo(muestra, recalculada, factor):
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=muestra).get()
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida=muestra)
    if medidas.exists():
        naturales, artificiales = calcularActividadEspectrometria(muestra, medidas, muestra.referencia_cliente, recalculada, factor)
        return muestra, naturales, artificiales
    else:
        print("No hay medidas para la muestra")
        return None

def calcularActividadEspectrometria(muestra, medidas, referencia, recalculada, factor):
    naturales = []
    artificiales = []
    for m in medidas:
        resultado = {}
        if m.actividad < m.amd:
            resultado["actividad"] = "< "+"{:.3e}".format(m.amd)
            resultado["amd"] = "{:.3e}".format(m.amd)
        else:
            resultado["actividad"] = "{:.3e}".format(m.actividad)+"±"+"{:.3e}".format(m.actividad_error)
            resultado["amd"] = "{:.3e}".format(m.amd)
        
        resultado["isotopo"] = m.determinacion_medida.nombre_medida
        resultado["referencia"] = referencia
        resultado["procedencia"] = "CN TRILLO("+muestra.codigo_recogida.codigo_procedencia.nombre.replace("TRILLO ","").zfill(3)+")"
        resultado["fecha_inicio"] = muestra.fecha_hora_recogida.strftime("%d-%m-%y")
        resultado["fecha_fin"] = muestra.fecha_hora_recogida_2.strftime("%d-%m-%y")
        resultado["fecha_referencia"] = muestra.fecha_hora_recogida_ref.strftime("%d-%m-%y")
        resultado["fecha_analisis"] = m.fecha_analisis.strftime("%d-%m-%y %H:%M")
        resultado["tiempo_contaje"] = m.tiempo_medida
        resultado["rendimiento"] = m.rendimiento
        resultado["cantidad_muestra"] = "{:.2f}".format(m.cantidad)
        if m.determinacion_medida.identificador in range(9,14):
            naturales.append(resultado)
        elif m.determinacion_medida.identificador in range(15,28):
            artificiales.append(resultado)
    return naturales, artificiales

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
        for item in json.loads(request.POST.get('codigos')):
            encontrado = False
            for etiqueta in request.session['codigos_barra']:
                if etiqueta["codigo"] == item["codigo"]:
                    etiqueta["cantidad"] = etiqueta["cantidad"] + item["cantidad"]
                    encontrado = True
            if not encontrado:
                request.session['codigos_barra'].append(item)
        
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
    fraccion = "Total"
    if RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida__identificador=id, id_parametro_muestra__identificador=24).exists():
        fraccion = RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida__identificador=id, id_parametro_muestra__identificador=24)[0].valor
    tipoMuestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id).get().codigo_recogida.codigo_csn.nombre
    etiqueta = {"codigo":"1"+str(id).zfill(6)+"000000", "texto":"M("+str(id)+") "+tipoMuestra+ " F:"+fraccion,"tipo":"muestra","cantidad":1}
    # comprueba si en codigos existentes está ya la etiqueta comparando el codigo
    if etiqueta not in listaAuxiliar:
        listaAuxiliar.append(etiqueta)

    # obtiene las alicuotas de la muestra
    alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=id).values('identificador', 'id_analiticas__nombre', 'fecha_hora_entrega', 'analista_tecnico__nombre', 'cantidad_muestra_analizada', 'estado_alicuota__descripcion') 
    for alicuota in alicuotas:
        etiqueta = {"codigo":"2"+str(id).zfill(6)+str(alicuota["identificador"]).zfill(6), "texto":"A("+str(id)+") "+alicuota["id_analiticas__nombre"]+ " F:"+fraccion,"tipo":"alicuota","cantidad":1}
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
    muestras = HistoricoRecogida.objects.using('gestion_muestras').exclude(estado_de_muestra__identificador_estado=99).order_by('-identificador').values('identificador', 'codigo_recogida__codigo_csn__nombre','cliente__nombre','codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__codigo_memoria__memoria', 'recepcionado_por__nombre', 'fecha_hora_recogida', 'fecha_hora_recepcion', 'estado_de_muestra__descripcion', 'referencia_cliente')
    return JsonResponse(list(muestras), safe=False)


@permission_required('auth.visualizacion_muestras')
def getInfoMuestra(request, id_muestra):
    informe = None
    hojasTipo = HojaPredefinida.objects.using('gestion_muestras').values()

    if 'auth.informes_muestra_lectura' in request.user.get_all_permissions():
        if RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=id_muestra).exists():
            informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=id_muestra)[0]
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=id_muestra)[0]
    parametros = ParametrosMuestra.objects.using('gestion_muestras').values()
    tecnicos = Usuarios.objects.using('gestion_muestras').filter(activo=1)
    return render(
        request,
        "gestionmuestras/informacionMuestra.html",
        {
            "muestra":muestra,
            "informe":informe,
            "parametros":parametros,
            "hojasTipo":hojasTipo,
            "tecnicos":tecnicos,
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
            muestra = alicuota.id_historico_recogida,
            evento = "Alicuotas",
            fecha_evento = datetime.now(),
            comentario = "Se ha generado un duplicado de la alícuota "+str(alicuota.identificador) + "("+relacionTratamiento.cod_reducido+")",
            usuario = request.user.id
        ).save(using='gestion_muestras')    
    return JsonResponse({"resultado":True}, safe=False)

@permission_required('auth.visualizacion_muestras')
def getInfoMuestraForm(request):
    httpresponse = reverse('gestionmuestras:gestmuesGetInfoMuestra',kwargs={'id_muestra':request.POST.get('id_muestra')})
    return redirect(httpresponse)

@permission_required('auth.visualizacion_muestras')
def getAlicuotasMuestra(request, id_muestra):
    alicuotas = list(RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=id_muestra).values('identificador', 'id_analiticas__identificador', 'id_analiticas__nombre', 'fecha_hora_entrega', 'analista_tecnico__identificador', 'analista_tecnico__nombre', 'cantidad_muestra_analizada', 'estado_alicuota__descripcion'))
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida__identificador=id_muestra)
    for a in alicuotas:
        if medidas.filter(id_alicuota__identificador=a["identificador"]).exists():
            a["medida"] = True
        else:
            a["medida"] = False
    return JsonResponse(alicuotas, safe=False)

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
        print(request.POST, "ID MUESTRA", historico, "CODIGO BARRAS", codigoBarras)
        for key in request.POST:
            if "parametro_" in key:
                valor = request.POST.get(key)
                id_parametro = key.replace('parametro_', '')
                if "float" in ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=id_parametro)[0].tipo:
                    valor.replace(",", ".")
                RelacionHistoricoParametrosMuestra(
                    id_historico_recogida = historico,
                    id_parametro_muestra = ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=id_parametro)[0],
                    valor = valor
                ).save(using='gestion_muestras')

        n_informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(anio=datetime.now().year).order_by('-identificador')[0].identificador+1
        anio_informe = datetime.now().year
        RelacionInformesMuestra(identificador = n_informe, codigo_muestra_asociada = id_muestra, anio = anio_informe).save(using='gestion_muestras')
    
        # insertar evento notificando la creación de la muestra
        EventosMuestras(
            muestra = historico,
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
            muestra = historico,
            evento = "Modificación",
            fecha_evento = datetime.now(),
            comentario=request.POST.get('inputMotivoModificacion'),
            usuario = request.user.id
        ).save(using='gestion_muestras')

        mensaje = MonitorizaMensajesTipo.objects.using('spd').filter(id=51).get()
        titulo = mensaje.mensaje.replace("<id_muestra>", str(id_muestra))
        descripcion = mensaje.descripcion.replace("<id_muestra>", str(id_muestra)).replace("<cliente>", historico.cliente.nombre).replace("<motivo>", request.POST.get('inputMotivoModificacion'))

        MensajesTelegram(id_area=4,id_estacion=None,fecha_hora_utc=datetime.now(pytz.timezone("Europe/Madrid")),mensaje=titulo,descripcion=descripcion,icono=mensaje.icono,estado=mensaje.estado,id_telegram=settings.ID_CHAT_GESTION_MUESTRAS,silenciar=mensaje.silenciar, confirmar=mensaje.confirmar).save(using='spd')

        return redirect(reverse('gestionmuestras:gestmuesGetInfoMuestra',kwargs={'id_muestra':id_muestra}))
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

@permission_required('auth.gestion_muestras')
def consultarParametrosMuestra(request, id_muestra):
    informacionMuestraParametros = RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida__identificador=id_muestra)
    return render(request, "gestionmuestras/informacionMuestraParametros.html", {"parametros": informacionMuestraParametros})

@permission_required('auth.gestion_muestras')
def consultarHojaTipo(request, hoja, muestra, alicuota=None):
    urlmuestra =  "http://www.alerta2.es" + reverse('gestionmuestras:gestmuesGetInfoMuestra',kwargs={'id_muestra':muestra})
    if alicuota is not None:
        url = "http://www.alerta2.es" + reverse('gestionmuestras:gestmuesConsultarHojaTipo',kwargs={'hoja':hoja, 'muestra':muestra, 'alicuota':alicuota})
    else:
        url = "http://www.alerta2.es" + reverse('gestionmuestras:gestmuesConsultarHojaTipo',kwargs={'hoja':hoja, 'muestra':muestra})

    hojaEncontrada = HojaPredefinida.objects.using('gestion_muestras').filter(identificador=hoja).get()
    valoresHoja = HojaPredefinidaValores.objects.using('gestion_muestras').filter(id_hoja_predefinida=hojaEncontrada)
    parametrosMuestra = None
    parametrosAlicuota = None
    muestraEncontrada = None
    alicuotaEncontrada = None
    alicuotasAsociadas = None
    volAlicuotas = None
    parametrosMuestraExistentes = None
    if HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=muestra).exists():
        muestraEncontrada = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=muestra).get()
        
        if "vol_alicuotas" in hojaEncontrada.especiales:
            volAlicuotas = []
            alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=muestra)
            for a in alicuotas:
                tratamiento = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a)[0]
                volAlicuotas.append({"alicuota":a, "tratamiento":tratamiento})
        elif alicuota is None:
            alicuotasAsociadas = str(list(set(list(RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=muestra).values_list('id_analiticas__nombre', flat=True))))).replace("[","").replace("]","").replace("'","")
        
        for buscado in valoresHoja.filter(origen='muestra'):
            if parametrosMuestra is None:
                parametrosMuestra = []
            if buscado.rellenar == "si":
                if RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida=muestra).exists():
                    parametrosMuestraExistentes = RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida=muestra)
                    if parametrosMuestraExistentes.filter(id_parametro_muestra=buscado.id_parametro_muestra).exists():
                        parametrosMuestra.append({"parametro":buscado.id_parametro_muestra ,"valor":parametrosMuestraExistentes.filter(id_parametro_muestra=buscado.id_parametro_muestra).get().valor, "rellenar":buscado.rellenar})
                    else:
                        parametrosMuestra.append({"parametro":buscado.id_parametro_muestra ,"valor":"*", "rellenar":buscado.rellenar})
            else:
                parametrosMuestra.append({"parametro":buscado.id_parametro_muestra, "rellenar":buscado.rellenar})
    print("valoresHoja", valoresHoja)
    for buscado in valoresHoja.filter(origen__startswith='alicuota'):
        print(buscado.origen.split("|"))
        if RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=muestra, id_analiticas__identificador=buscado.origen.split("|")[1]).exists():
            if parametrosAlicuota is None:
                parametrosAlicuota = []
            parametrosAlicuota.append({"parametro":buscado.id_parametro_muestra, "rellenar":buscado.rellenar, "determinacion":Determinaciones.objects.using('gestion_muestras').filter(identificador=buscado.origen.split("|")[1]).get().nombre})
    '''
    if alicuota is not None:
        
        if RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=alicuota).exists():
            alicuotaEncontrada = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=alicuota).get()
            print("busco")
            for buscado in valoresHoja.filter(origen__icontains='alicuota'):
                print(buscado)
                if parametrosAlicuota is None:
                    parametrosAlicuota = []
                if buscado.rellenar == "si":
                    if RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica=alicuota).exists():
                        parametrosAlicuotaExistentes = RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica=alicuota)
                        if parametrosAlicuotaExistentes.filter(id_parametro_analitica=buscado.id_parametro_muestra).exists():
                            parametrosAlicuota.append({"parametro":buscado.id_parametro_muestra ,"valor":parametrosMuestraExistentes.filter(id_parametro_muestra=buscado.id_parametro_muestra).get().valor, "rellenar":buscado.rellenar})
                        else:
                            parametrosAlicuota.append({"parametro":buscado.id_parametro_muestra ,"valor":"*", "rellenar":buscado.rellenar})
                else:
                    parametrosAlicuota.append({"parametro":buscado.id_parametro_muestra, "rellenar":buscado.rellenar})
                '''

    imagenURLMuestra = generadorQR("Muestra", urlmuestra)
    str_equivalent_image_muestra = base64.b64encode(imagenURLMuestra.getvalue()).decode()
    imagen = generadorQR("Hoja", url)
    str_equivalent_image = base64.b64encode(imagen.getvalue()).decode()    

    
    return render(request, "gestionmuestras/hojaPredefinida.html", {"hoja": hoja, "muestra": muestraEncontrada, "alicuota": alicuotaEncontrada, "parametrosMuestra": parametrosMuestra, "parametrosAlicuota": parametrosAlicuota, "imagenMuestra": str_equivalent_image_muestra, "imagen": str_equivalent_image, "alicuotasAsociadas": alicuotasAsociadas, "volAlicuotas": volAlicuotas})


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
    parametros = RelacionTipoDeterminacionParametros.objects.using('gestion_muestras').filter(tipo=tipo,determinacion__isnull=True).values("parametro__identificador", "parametro__nombre","parametro__descripcion","valor_recomendado", "parametro__tipo")
    return JsonResponse({"parametros":list(parametros)}, safe=False)
        
@permission_required('auth.insercion_muestras')
def insertarParametros(request):
    print(request.POST)
    valor = request.POST.get("inputValorParametro")
    if "float" in ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=request.POST.get("parametroAdicional")).get().tipo:
        valor.replace(",", ".")
    RelacionHistoricoParametrosMuestra(id_historico_recogida=HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get("id_muestra")).get(), id_parametro_muestra=ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=request.POST.get("parametroAdicional")).get(), valor=valor).save(using='gestion_muestras')
    return JsonResponse({"status":"ok"}, safe=False)
    

@permission_required('auth.insercion_muestras')
def insertarDeterminaciones(request):
    determinacionesInsertadas = []
    relacionDeterminacion = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras')
    parametros = RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida=request.POST.get("id_muestra"))
    for key in request.POST:
        if request.POST.get(key) == "on":
            if relacionDeterminacion.filter(id_determinacion=key).exists():
                tratamientos = list(relacionDeterminacion.filter(id_determinacion=key).values("id_determinacion__identificador", "id_determinacion__nombre", "id_tratamiento__identificador", "id_tratamiento__descripcion", "por_defecto"))
                determinacionesInsertadas.append({"determinacion":key, "determinacion_nombre":tratamientos[0]["id_determinacion__nombre"], "tratamientos":tratamientos})
            else:
                return render(request, "gestionmuestras/errorInsercion.html", {
                    "problema": "Existe un problema con la determinación "+key+" no se han encontrado tratamientos asociados en la tabla 'RelacionDeterminacionesTratamientos'."
                })

    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get("id_muestra")).get()

    for d in determinacionesInsertadas:
        tratamientosSeleccionados = []
        if CondicionesTratamiento.objects.using('gestion_muestras').filter(id_relacion_det_trat__id_determinacion=d["determinacion"], tipo_muestra=muestra.codigo_recogida.codigo_csn.tipo.tipo_muestra_id).exists():
            for trat in d["tratamientos"]:
                trat["por_defecto"] = 0
        condiciones = CondicionesTratamiento.objects.using('gestion_muestras').filter(id_relacion_det_trat__id_determinacion=d["determinacion"], tipo_muestra=muestra.codigo_recogida.codigo_csn.tipo.tipo_muestra_id)
        for c in condiciones:
            seleccionado = False
            parametrosCondicion = re.findall(r'\{([^}]*)\}', c.condicion)
            for pc in parametrosCondicion:
                if parametros.filter(id_parametro_muestra__identificador=pc).exists():
                    calculo = c.condicion
                    calculo = c.condicion.replace("{"+pc+"}", parametros.filter(id_parametro_muestra__identificador=pc).get().valor)
                    if evaluarFuncion(calculo):
                        seleccionado = True
                        tratamientosSeleccionados.append(c.id_relacion_det_trat.id_tratamiento.identificador)

            if seleccionado:
                for tratValido in tratamientosSeleccionados:
                    for trat in d["tratamientos"]:
                        if trat["id_tratamiento__identificador"] == tratValido:
                            trat["por_defecto"] = 1
        

    return render(request, "gestionmuestras/asignacionTratamiento.html", {
        "id_muestra": request.POST.get("id_muestra"),
        "determinacionesInsertadas": determinacionesInsertadas,
    })
    

@permission_required('auth.insercion_muestras')
def insertarTratamientos(request):
    tratamientosModelo = Tratamiento.objects.using('gestion_muestras')
    determinacionesModelo = Determinaciones.objects.using('gestion_muestras')
    
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get("id_muestra")).get()
    parametros = RelacionHistoricoParametrosMuestra.objects.using('gestion_muestras').filter(id_historico_recogida=request.POST.get("id_muestra"))
    cant_muestra = 0
    if parametros.filter(id_parametro_muestra__identificador="12").exists():
        cant_muestra= float(parametros.filter(id_parametro_muestra__identificador="12").get().valor.replace(",", "."))
    unidad_muestra = "" 
    if parametros.filter(id_parametro_muestra__identificador="13").exists():
        unidad_muestra = parametros.filter(id_parametro_muestra__identificador="13").get().valor
        
    if parametros.filter(id_parametro_muestra__identificador="22").exists():
        cant_muestra_restante = float(parametros.filter(id_parametro_muestra__identificador="22").get().valor)
    else:
        RelacionHistoricoParametrosMuestra(id_historico_recogida=muestra, id_parametro_muestra=ParametrosMuestra.objects.using('gestion_muestras').filter(identificador=22).get(), valor=cant_muestra).save(using='gestion_muestras')
        cant_muestra_restante = cant_muestra

    tratamientos = []
    controles_requeridos = []
    mensaje = ""

    for key in request.POST:
        if request.POST.get(key) == "on":
            empleados = Usuarios.objects.using('gestion_muestras').filter(activo=1)
            calculo = 0.0
            tecnicos = RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(procedimiento=key.split("_")[2]).values("responsable", "sustituto_1","sustituto_2","sustituto_3").get()
            if RelacionTipoMuestraDeterminacionCantidad.objects.using('gestion_muestras').filter(id_tipo_muestra=muestra.codigo_recogida.codigo_csn.tipo.tipo_muestra_id, id_tratamiento=key.split("_")[2]).exists():
                relacionDetCantidad = RelacionTipoMuestraDeterminacionCantidad.objects.using('gestion_muestras').filter(id_tipo_muestra=muestra.codigo_recogida.codigo_csn.tipo.tipo_muestra_id, id_tratamiento=key.split("_")[2]).get()
                if relacionDetCantidad.formula:
                    realizar = False
                    if relacionDetCantidad.condicion:
                        parametrosCondicion = re.findall(r'\{([^}]*)\}', relacionDetCantidad.condicion)
                        condicion = relacionDetCantidad.condicion
                        for pc in parametrosCondicion:
                            if parametros.filter(id_parametro_muestra__identificador=pc).exists():
                                condicion = condicion.replace("{"+pc+"}", parametros.filter(id_parametro_muestra__identificador=pc).get().valor)
                        if evaluarFuncion(condicion):
                            realizar = True
                        else:
                            realizar = False
                    else:
                        realizar = True
                    
                    if realizar:
                        parametrosCondicion = re.findall(r'\{([^}]*)\}', relacionDetCantidad.formula)
                        for pc in parametrosCondicion:
                        
                            if parametros.filter(id_parametro_muestra__identificador=pc).exists():
                                calculo = relacionDetCantidad.formula
                                calculo = relacionDetCantidad.formula.replace("{"+pc+"}", parametros.filter(id_parametro_muestra__identificador=pc).get().valor)
                                
                                cantidad =  round(evaluarFuncion(calculo),2)
                            else:
                                cantidad = relacionDetCantidad.valor
                    else:
                        cantidad = relacionDetCantidad.valor

                else:
                    cantidad = relacionDetCantidad.valor
                unidad = relacionDetCantidad.unidad
            else:
                cantidad = 0.0
                unidad = unidad_muestra
                mensaje = mensaje + "No se ha encontrado la relación de cantidad para la determinación "+key.split("_")[1]+" y el tipo de muestra "+str(muestra.codigo_recogida.codigo_csn.tipo.descripcion)+"<br>"

            cant_muestra_restante = round(cant_muestra_restante - float(cantidad),3)
            cantidad = str(cantidad).replace(",", ".")
            tratamientos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]], "cantidad": cantidad, "unidad":unidad})

            # obtengo los controles requeridos para el tratamiento
            controles = MuestraActualCodigo.objects.using('gestion_muestras').filter(id=RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento= key.split("_")[2]).get().id_muestra_codigo.id).get()
            if controles.duplicada_pos == 0:
                cant_muestra_restante = round(cant_muestra_restante - float(cantidad),3)
                controles_requeridos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "control":"duplicado", "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]], "cantidad": cantidad, "unidad":unidad})
            if controles.control_pos == 0:
                cant_muestra_restante = round(cant_muestra_restante - float(cantidad),3)
                controles_requeridos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "control":"control", "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]], "cantidad": cantidad, "unidad":unidad})
            if controles.blanco_pos == 0:
                cant_muestra_restante = round(cant_muestra_restante - float(cantidad),3)
                controles_requeridos.append({"key":key, "muestra":key.split("_")[0], "determinacion":determinacionesModelo.filter(identificador=key.split("_")[1]).get(), "tratamiento":tratamientosModelo.filter(identificador=key.split("_")[2]).get(), "control":"blanco", "tecnico": [tecnicos["responsable"], tecnicos["sustituto_1"], tecnicos["sustituto_2"], tecnicos["sustituto_3"]], "cantidad": cantidad, "unidad":unidad})

    return render(request, "gestionmuestras/tareasPostInsercion.html", {
        "mensaje": mensaje,
        "id_muestra": request.POST.get("id_muestra"),
        "cantidad_muestra": cant_muestra,
        "cantidad_muestra_restante": cant_muestra_restante,
        "unidad_muestra": unidad_muestra,
        "tratamientos": tratamientos,
        "controles_requeridos": controles_requeridos,
        "empleados": empleados
    })

@permission_required('auth.insercion_muestras')
def finalizarInsercion(request):
    muestra = 0

    alicuotasInsertadas = []

    for key in request.POST:
        
        if "_cantidad" not in key:
            if key == "csrfmiddlewaretoken":
                continue
            muestra = key.split("_")[0]
            alicuota = 'Analitica'
            if len(key.split("_")) > 3:
                alicuota = key.split("_")[3]

            
            cantidad = request.POST.get(key+"_cantidad")
            
            muestrasAnalitica = RelacionHistoricoMuestraAnaliticas(id_historico_recogida=HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=key.split("_")[0]).get(), id_analiticas=Determinaciones.objects.using('gestion_muestras').filter(identificador=key.split("_")[1]).get(), fecha_hora_entrega=datetime.now(), analista_tecnico=Usuarios.objects.using('gestion_muestras').filter(nombre=request.POST.get(key)).get(), descripcion='FTOTAL', alicuota=alicuota, estado_alicuota=EstadoMuestras.objects.using('gestion_muestras').filter(identificador_estado=1).get(), cantidad_muestra_analizada=cantidad)

            muestrasAnalitica.save(using='gestion_muestras')
            muestrasAnalitica.codigo_barras = generarCodigoBarras(int(key.split("_")[0]), muestrasAnalitica.identificador)
            muestrasAnalitica.save(using='gestion_muestras')

            codigos = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento__identificador=key.split("_")[2]).get().id_muestra_codigo
            codigo_reducido = codigos.codigo+str(codigos.posicion)
            
            
            alicuotasInsertadas.append(str(muestrasAnalitica.identificador)+" ("+codigo_reducido+") " + str(muestrasAnalitica.id_analiticas.nombre) )

            print("consultando", key.split("_")[2], codigos.codigo)

            if RelacionControlesTratamientos.objects.using('gestion_muestras').filter(id_muestra_historico__identificador=key.split("_")[0], codigo=codigos.codigo).exists():
                if RelacionControlesTratamientos.objects.using('gestion_muestras').filter(id_muestra_historico__identificador=key.split("_")[0], codigo=codigos.codigo).get().tipo_control == 'BL':
                    alicuota = 'blanco'
                elif RelacionControlesTratamientos.objects.using('gestion_muestras').filter(id_muestra_historico__identificador=key.split("_")[0], codigo=codigos.codigo).get().tipo_control == 'CER':
                    alicuota = 'certificada'
                elif RelacionControlesTratamientos.objects.using('gestion_muestras').filter(id_muestra_historico__identificador=key.split("_")[0], codigo=codigos.codigo).get().tipo_control == 'CTR':
                    alicuota = 'control'
                


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
                muestrasAnalitica.save(using='gestion_muestras')
            elif alicuota == 'duplicado':
                codigo_reducido = codigo_reducido + "_DU"
                codigos.duplicada_pos = codigos.duplicada
            elif alicuota == 'control':
                codigo_reducido = codigo_reducido + "_CTR"
                codigos.control_pos = codigos.control
                muestrasAnalitica.id_historico_recogida = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(tipo_control='CTR', codigo=codigos.codigo)[0].id_muestra_historico
                muestrasAnalitica.save(using='gestion_muestras')
            elif alicuota == 'certificada':
                codigo_reducido = codigo_reducido + "_CER"
                codigos.control_pos = codigos.control
                muestrasAnalitica.id_historico_recogida = RelacionControlesTratamientos.objects.using('gestion_muestras').filter(tipo_control='CER', codigo=codigos.codigo)[0].id_muestra_historico
                muestrasAnalitica.save(using='gestion_muestras')
            codigos.save(using='gestion_muestras')
            

            RelacionAnaliticasTratamiento(id_muestra_analitica=muestrasAnalitica, tratamiento=Tratamiento.objects.using('gestion_muestras').filter(identificador=key.split("_")[2]).get(), cod_reducido=codigo_reducido, fecha_inicio=datetime.now(), analista=Usuarios.objects.using('gestion_muestras').filter(nombre=request.POST.get(key)).get(), paso_actual=0).save(using='gestion_muestras')
            NotificacionesAsignacion(id_alicuota=muestrasAnalitica, usuario=Usuarios.objects.using('gestion_muestras').filter(nombre=request.POST.get(key)).get(), fecha_asignacion=datetime.now(), notificado=0).save(using='gestion_muestras')

    EventosMuestras(
        muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=key.split("_")[0]).get(),
        evento = "Alicuotas",
        fecha_evento = datetime.now(),
        comentario = "Generadas alicuotas de la muestra " + str(key.split("_")[0]) + ": " + str(alicuotasInsertadas).replace("[","").replace("]","").replace("'",""),
        usuario = request.user.id
    ).save(using='gestion_muestras')  

    # dedirigir la vista a la muestra
    return redirect(reverse('gestionmuestras:gestmuesGetInfoMuestra',kwargs={'id_muestra':muestra}))

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

def traspasarAlicuota(request):
    usuario = Usuarios.objects.using('gestion_muestras').filter(identificador=request.POST.get("inputNuevoTecnico")).get()
    alicuota = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=request.POST.get("id_alicuota")).get()
    alicuota.analista_tecnico = usuario
    alicuota.save(using='gestion_muestras')
    if RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota, fecha_fin__isnull=True).exists():
        tratamiento = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota, fecha_fin__isnull=True)[0]
        tratamiento.analista = usuario
        tratamiento.save(using='gestion_muestras')
        NotificacionesAsignacion(id_alicuota=alicuota, usuario=usuario, fecha_asignacion=datetime.now(), notificado=0).save(using='gestion_muestras')
    return JsonResponse({"status":"ok"}, safe=False)

def muestrasRecepcionadas(request):
    muestrasEncontradas = []
    memorias = Memorias.objects.using('gestion_muestras')
    determinaciones = Determinaciones.objects.using('gestion_muestras')
    if request.method == "POST":
        muestras = EventosMuestras.objects.using('gestion_muestras').order_by('muestra__identificador', 'fecha_evento')
        if request.POST.get("fechaInicio") != "":
            muestras = muestras.filter(fecha_evento__gte=request.POST.get("fechaInicio"))
        if request.POST.get("fechaFin") != "":
            muestras = muestras.filter(fecha_evento__lte=request.POST.get("fechaFin"))
        if  "memorias" in request.POST:
            if request.POST.get("memoria") != "":
                muestras = muestras.filter(muestra__codigo_recogida__codigo_memoria__codigo_memoria__in=request.POST.getlist("memorias"))
        for m in muestras:    
            alicuotasEncontradas = []
            insertar = True
            alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=m.muestra)
            
            if "determinaciones" in request.POST:
                if request.POST.get("determinaciones") != "":
                    insertar = False
                    if alicuotas.filter(id_analiticas__identificador__in=request.POST.getlist("determinaciones")).exists():
                        insertar = True
            for a in alicuotas:
                tratamientos = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a)
                alicuotasEncontradas.append({"alicuota":a, "tratamientos":tratamientos})
            if insertar:
                muestrasEncontradas.append({"muestra":m, "alicuotas":alicuotasEncontradas})
    else:
        ayer = datetime.now() - timedelta(days=1)
        muestras = EventosMuestras.objects.using('gestion_muestras').filter(fecha_evento__date__gte=ayer.date()).order_by('muestra__identificador', 'fecha_evento')
        for m in muestras:    
            alicuotasEncontradas = []
            alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=m.muestra)
            for a in alicuotas:
                tratamientos = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a)
                alicuotasEncontradas.append({"alicuota":a, "tratamientos":tratamientos})
            muestrasEncontradas.append({"muestra":m, "alicuotas":alicuotasEncontradas})

    return render(request, "gestionmuestras/muestrasRecepcionadas.html", 
                  {
                      "muestras":muestrasEncontradas,
                      "memorias":memorias,
                      "determinaciones":determinaciones
                   })

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
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__identificador=id_alicuota).values('cod_reducido', 'determinacion_medida__nombre_medida', 'fecha_analisis', 'actividad', 'actividad_error', 'amd', 'tiempo_medida', 'cantidad', 'rendimiento', 'seleccionado')
    parametros = RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica__identificador=id_alicuota)
    return render(request, "gestionmuestras/infoAlicuota.html", {"id_alicuota":id_alicuota, "tratamientos":list(tratamientos), "parametros":list(parametros), "medidas":list(medidas)})

@permission_required('auth.visualizacion_muestras')
def infoAlicuotaMedidas(request, id_muestra):
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida__identificador=id_muestra).values('cod_reducido', 'determinacion_medida__nombre_medida', 'fecha_analisis', 'actividad', 'actividad_error', 'amd', 'tiempo_medida', 'cantidad', 'rendimiento', 'seleccionado')
    return render(request, "gestionmuestras/infoAlicuotaMedidas.html", {"id_muestra":id_muestra, "medidas":list(medidas)})

@permission_required('auth.visualizacion_muestras')
def verificarMuestra(request):
    '''
    from django.contrib.auth.models import Group
import pandas as pd
    users_in_group = Group.objects.get(name="group name").user_set.all()
    
    if user in users_in_group:
        # do something
    '''
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.POST.get('id_muestra')).get()

        
    return JsonResponse({}, safe=False)


@permission_required('auth.gestion_informes')
def listadoMuestrasInforme(request): 
    memorias = Memorias.objects.using('gestion_muestras').order_by('descripcion')
    clientes = Clientes.objects.using('gestion_muestras').order_by('nombre')
    estados = EstadoMuestras.objects.using('gestion_muestras').order_by('descripcion')
    tipoMuestra = CodMuestras.objects.using('gestion_muestras').order_by('nombre')
    return render(request, "gestionmuestras/listadoMuestrasInforme.html", {"memorias":memorias, "clientes":clientes, "estados":estados, "tipoMuestra":tipoMuestra})

@permission_required('auth.gestion_informes')
def listadoMuestrasInformeDatos(request):
    muestras = HistoricoRecogida.objects.using('gestion_muestras').filter(estado_de_muestra__in=[1,2,3,4]).values('identificador', 'codigo_recogida__codigo_csn__nombre','cliente__nombre','codigo_recogida__codigo_procedencia__nombre', 'codigo_recogida__codigo_memoria__memoria', 'recepcionado_por__nombre', 'fecha_hora_recogida', 'fecha_hora_recepcion', 'estado_de_muestra__descripcion', 'referencia_cliente')

    if request.GET.get('memoria') is not None and request.GET.get('memoria') != "":
        muestras = muestras.filter(codigo_recogida__codigo_memoria__codigo_memoria=request.GET.get('memoria'))
    if request.GET.get('cliente') is not None and request.GET.get('cliente') != "":
        muestras = muestras.filter(cliente__identificador=request.GET.get('cliente'))
    if request.GET.get('estado') is not None and request.GET.get('estado') != "":
        muestras = muestras.filter(estado_de_muestra__identificador_estado=request.GET.get('estado'))
    if request.GET.get('tipoMuestra') is not None and request.GET.get('tipoMuestra') != "":
        muestras = muestras.filter(codigo_recogida__codigo_csn__codigo=request.GET.get('tipoMuestra'))

    return JsonResponse(list(muestras), safe=False)


def informeAnalizarAlfaBeta(encontrados, muestra, medidas, alicuotas, tratamientos):
    informeAnalizarAlfa(encontrados, muestra, medidas, alicuotas, tratamientos)
    informeAnalizarBeta(encontrados, muestra, medidas, alicuotas, tratamientos)

def informeAnalizarAlfa(encontrados, muestra, medidas, alicuotas, tratamientos):
    alicuotas = alicuotas.filter(id_historico_recogida=muestra, id_analiticas__in=[1,2])
    medidasAlfa = medidas.filter(determinacion_medida__identificador=1)
    tratamientoAlcance = None
    for a in alicuotas:
        if medidasAlfa.filter(id_alicuota=a).exists():
            medida = medidasAlfa.filter(id_alicuota=a).get()
        else:
            medida = None
        if tratamientos.filter(id_muestra_analitica=a).exists():
            tratamientosAlicuota = tratamientos.filter(id_muestra_analitica=a)
        
        if not encontrados["alfa"]:
            encontrados["alfa"] = []
        
        if tratamientosAlicuota.filter(tratamiento__alcance__isnull=False).exists():
            tratamientoAlcance = tratamientosAlicuota.filter(tratamiento__alcance__isnull=False)[0].tratamiento

        encontrados["alfa"].append({"alicuota":a, "medida":medida, "tratamientos":list(tratamientosAlicuota), "tratamientoAlcance":tratamientoAlcance})


def informeAnalizarBeta(encontrados, muestra, medidas, alicuotas, tratamientos):
    alicuotas = alicuotas.filter(id_historico_recogida=muestra, id_analiticas__in=[5,2])
    medidasAlfa = medidas.filter(determinacion_medida__identificador=2)
    tratamientoAlcance = None
    for a in alicuotas:
        if medidasAlfa.filter(id_alicuota=a).exists():
            medida = medidasAlfa.filter(id_alicuota=a).get()
        else:
            medida = None
        if tratamientos.filter(id_muestra_analitica=a).exists():
            tratamientosAlicuota = tratamientos.filter(id_muestra_analitica=a)
        
        if not encontrados["beta"]:
            encontrados["beta"] = []
            
        if tratamientosAlicuota.filter(tratamiento__alcance__isnull=False).exists():
            tratamientoAlcance = tratamientosAlicuota.filter(tratamiento__alcance__isnull=False)[0].tratamiento

        if not tratamientosAlicuota.filter(tratamiento__identificador=1).exists():
            encontrados["beta"].append({"alicuota":a, "medida":medida, "tratamientos":list(tratamientosAlicuota), "tratamientoAlcance":tratamientoAlcance})

def informeAnalizarBetaResto(encontrados, muestra, medidas, alicuotas, tratamientos):
    alicuotas = alicuotas.filter(id_historico_recogida=muestra, id_analiticas__in=[4])
    medidasAlfa = medidas.filter(determinacion_medida__identificador=3)
    tratamientoAlcance = None
    for a in alicuotas:
        if medidasAlfa.filter(id_alicuota=a).exists():
            medida = medidasAlfa.filter(id_alicuota=a).get()
        else:
            medida = None
        if tratamientos.filter(id_muestra_analitica=a).exists():
            tratamientosAlicuota = tratamientos.filter(id_muestra_analitica=a)
        
        if not encontrados["betaresto"]:
            encontrados["betaresto"] = []
            
        if tratamientosAlicuota.filter(tratamiento__alcance__isnull=False).exists():
            tratamientoAlcance = tratamientosAlicuota.filter(tratamiento__alcance__isnull=False)[0].tratamiento

        encontrados["betaresto"].append({"alicuota":a, "medida":medida, "tratamientos":list(tratamientosAlicuota), "tratamientoAlcance":tratamientoAlcance})

def informeAnalizarRadon(encontrados, muestra, medidas, alicuotas, tratamientos):
    alicuotas = alicuotas.filter(id_historico_recogida=muestra, id_analiticas__in=[18])
    medidasAlfa = medidas.filter(determinacion_medida__identificador=5)
    tratamientoAlcance = None
    for a in alicuotas:
        if medidasAlfa.filter(id_alicuota=a).exists():
            medida = medidasAlfa.filter(id_alicuota=a).get()
        else:
            medida = None
        if tratamientos.filter(id_muestra_analitica=a).exists():
            tratamientosAlicuota = tratamientos.filter(id_muestra_analitica=a)
        
        if not encontrados["radon"]:
            encontrados["radon"] = []
            
        if tratamientosAlicuota.filter(tratamiento__alcance__isnull=False).exists():
            tratamientoAlcance = tratamientosAlicuota.filter(tratamiento__alcance__isnull=False)[0].tratamiento

        encontrados["radon"].append({"alicuota":a, "medida":medida, "tratamientos":list(tratamientosAlicuota), "tratamientoAlcance":tratamientoAlcance})

def informeAnalizarTritio(encontrados, muestra, medidas, alicuotas, tratamientos):
    alicuotas = alicuotas.filter(id_historico_recogida=muestra, id_analiticas__in=[20])
    medidasAlfa = medidas.filter(determinacion_medida__identificador=6)
    tratamientoAlcance = None
    for a in alicuotas:
        if medidasAlfa.filter(id_alicuota=a).exists():
            medida = medidasAlfa.filter(id_alicuota=a).get()
        else:
            medida = None
        if tratamientos.filter(id_muestra_analitica=a).exists():
            tratamientosAlicuota = tratamientos.filter(id_muestra_analitica=a)
        
        if not encontrados["tritio"]:
            encontrados["tritio"] = []
        if tratamientosAlicuota.filter(tratamiento__alcance__isnull=False).exists():
            tratamientoAlcance = tratamientosAlicuota.filter(tratamiento__alcance__isnull=False)[0].tratamiento

        encontrados["tritio"].append({"alicuota":a, "medida":medida, "tratamientos":list(tratamientosAlicuota), "tratamientoAlcance":tratamientoAlcance})

def informeAnalizarDIT(encontrados, muestra, medidas, alicuotas, tratamientos):
    encontrados["dit"] = True

selectorMedida = {1:informeAnalizarAlfa, 2:informeAnalizarAlfaBeta, 5:informeAnalizarBeta, 4:informeAnalizarBetaResto, 18:informeAnalizarRadon, 20:informeAnalizarTritio, 44: None, 47:informeAnalizarDIT}

@permission_required('auth.gestion_informes')
def seleccionInforme(request):
    encontrados = {"alfa":False, "beta":False, "betaresto": False, "radon":False, "tritio":False, "dit":False}
    informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=request.GET.get('muestra')).get()
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.GET.get('muestra')).get()
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida__identificador=request.GET.get('muestra')).all()
    alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=request.GET.get('muestra')).all()
    tratamientos = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica__id_historico_recogida__identificador=request.GET.get('muestra')).all()

    for a in alicuotas.values('id_analiticas').distinct():
        if selectorMedida[a["id_analiticas"]]:
            selectorMedida[a["id_analiticas"]](encontrados, muestra, medidas, alicuotas, tratamientos)

    return render(request, "gestionmuestras/seleccionInforme.html", {"hoy":datetime.now() ,"muestra":muestra, "informe":informe, "encontrados": encontrados})


@permission_required('auth.gestion_informes')
def generacionInforme(request):
    informe = RelacionInformesMuestra.objects.using('gestion_muestras').filter(codigo_muestra_asociada=request.GET.get('muestra')).get()
    muestra = HistoricoRecogida.objects.using('gestion_muestras').filter(identificador=request.GET.get('muestra')).get()
    medidas = RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota__id_historico_recogida__identificador=request.GET.get('muestra'))
    print(informe, muestra, medidas)
    return render(request, "gestionmuestras/informeMuestra.html", {"hoy":datetime.now() ,"muestra":muestra, "informe":informe, "medidas":medidas})

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

@permission_required('auth.gestion_tecnico')
def alicuotasAsignadas(request):
    return render(request, "gestionmuestras/alicuotasAsignadas.html", {})

@permission_required('auth.gestion_tecnico')
def alicuotasAsignadasDatos(request, antiguas=None, tecnicos=None):
    
    tecnico = Usuarios.objects.using('gestion_muestras').filter(usuario_django=request.user.id).get().nombre

    alicuotas = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(analista__nombre=tecnico)
    if antiguas == None or antiguas == "No":
        alicuotas = alicuotas.filter(fecha_fin__isnull=True)
    
    alicuotas = list(alicuotas.values('identificador', 'id_muestra_analitica__id_historico_recogida__identificador', 'id_muestra_analitica', 'tratamiento__descripcion', 'cod_reducido', 'fecha_inicio', 'fecha_fin', 'paso_actual', 'analista__nombre', 'analista__usuario_django'))

    for alicuota in alicuotas:
        alicuota["propio"] = "Si"

    if tecnicos == None or tecnicos == "No":
        return JsonResponse(alicuotas, safe=False)
    else:
        procedimientosR = list(RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(responsable=tecnico).values_list('procedimiento', flat=True))
        procedimientos1 = list(RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(sustituto_1=tecnico).values_list('procedimiento', flat=True))
        procedimientos2 = list(RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(sustituto_2=tecnico).values_list('procedimiento', flat=True))
        procedimientos3 = list(RelacionProcedimientosResponsables.objects.using('gestion_muestras').filter(sustituto_3=tecnico).values_list('procedimiento', flat=True))
        procedimientos = list(set(procedimientosR) | set(procedimientos1) | set(procedimientos2) | set(procedimientos3))
        alicuotasSustitutas = list(RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(tratamiento__identificador__in=procedimientos, fecha_fin__isnull=True).exclude(analista__nombre=tecnico).values('identificador', 'id_muestra_analitica__id_historico_recogida__identificador', 'id_muestra_analitica', 'tratamiento__descripcion', 'cod_reducido', 'fecha_inicio', 'fecha_fin', 'paso_actual', 'analista__nombre', 'analista__usuario_django'))
        return JsonResponse(alicuotas+alicuotasSustitutas, safe=False)

@permission_required('auth.gestion_tecnico')
def notificacionesPendientes(request):
    notificaciones = NotificacionesAsignacion.objects.using('gestion_muestras').filter(usuario__usuario_django=request.user.id, notificado=0).values('id', 'id_alicuota', 'id_alicuota__id_analiticas__nombre', 'id_alicuota__id_historico_recogida','fecha_asignacion')
    return JsonResponse(list(notificaciones), safe=False)

@permission_required('auth.gestion_tecnico')
def verificarNotificado(request):
    notificacion = NotificacionesAsignacion.objects.using('gestion_muestras').filter(id=request.POST.get('id')).get()
    notificacion.notificado = 1
    notificacion.save()
    return JsonResponse({}, safe=False)

@permission_required('auth.gestion_recolector')
def consultarMuestrasRecoger(request):
    return render(request, "gestionmuestras/muestrasRecolectar.html", {})


@permission_required('auth.gestion_recolector')
def consultarMuestrasRecogerDatos(request, mes=None, recogido=None):
    muestras = GestmuesColeccion.objects.using('gestion_muestras').values('n_recogida__numero', 'n_recogida__csn__nombre', 'n_recogida__procedencia__nombre', 'n_recogida__memoria__memoria', 'csn__nombre', 'recoge', 'n_recogida__suministra', 'suministra', 'observaciones', 'n_recogida__observaciones', 'recogido', 'fecha_recogida_inicial', 'fecha_recogida_final', 'fecha_recepcion', 'conservacion', 'nfiltro', 'ibomba', 'mes')
    if mes and mes != "-1":
        muestras = muestras.filter(mes=mes)
    if recogido and recogido != "-1":
        muestras = muestras.filter(recogido=recogido)

    return JsonResponse(list(muestras), safe=False)

@permission_required('auth.visualizacion_muestras')
def consultarVRAEx(request):
    insertadas = []
    '''
    RecogidaGeneral =  GestmuesRecogida.objects.using('gestion_muestras').filter(memoria='G')
    muestrasAlfaBeta = Muestra.objects.using('alfabeta').filter(fecharecogida__gte='2023-01-01 00:00:00')
    for recogida in RecogidaGeneral:
        if muestrasAlfaBeta.filter(clave__contains=str(recogida.numero)+recogida.csn.codigo).exists():
            for m in muestrasAlfaBeta.filter(clave__contains=str(recogida.numero)+recogida.csn.codigo):
                alicuotas = Alicuota.objects.using('alfabeta').filter(muestra_clave=m)
                for a in alicuotas:
                    if Actividadeficienciabeta.objects.using('alfabeta').filter(medida__contains=a.codigoreducido).exists():
                        medidas = Actividadeficienciabeta.objects.using('alfabeta').filter(medida__contains=a.codigoreducido)
                        for medida in medidas:
                            # imprimir los valores: medida,actividad,actividadminimadetectable,incertidumbrecombinada
                            fecha = Medida.objects.using('alfabeta').filter(id=medida.medida).get().fecha
                            
                            procedencia = GestmuesRecogida.objects.using('gestion_muestras').filter(numero=recogida.numero, csn=recogida.csn).get()
                            estroncio = {"actividad":medida.actividad, "error":medida.incertidumbrecombinada, "amd":medida.actividadminimadetectable, "muestras":1, "fecha_recogida_inicial":m.fecharecogida, "fecha_recogida_final":m.fechafinrecogida, "fecha_medida": fecha, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.procedencia.codigo, "Muestra": recogida.csn.codigo, "CodIsotopo": "Sr", "CodAnalisis": "SR", "Masa": 90}
                            if estroncio["Muestra"] in ["SP","LV","LC"]:
                                estroncio["actividad"] = estroncio["actividad"] * 1000
                                estroncio["error"] = estroncio["error"] * 1000
                                estroncio["amd"] = estroncio["amd"] * 1000
                            if estroncio["Muestra"] in ["PP"]:
                                estroncio["actividad"] = estroncio["actividad"] / 1000
                                estroncio["error"] = estroncio["error"] / 1000
                                estroncio["amd"] = estroncio["amd"] / 1000

                            if not ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(muestra_codmuestra=estroncio["Muestra"], isotopo_codisotopo=estroncio["CodIsotopo"], isotopo_analisis_codanalisis=estroncio["CodAnalisis"], fecha_recogida_inicial=estroncio["fecha_recogida_inicial"]).exists():
                                insertadas.append(estroncio)
                                ValorMuestraCopumaVolatil(motivo_muestreo_codmuestreo=estroncio["motivo"], fecha_recogida_inicial=estroncio["fecha_recogida_inicial"], fecha_recogida_final=estroncio["fecha_recogida_final"], fecha_analisis=estroncio["fecha_medida"], instalacion_codinstalacion=estroncio["Instalacion"], laboratorio_codlaboratorio=estroncio["Laboratorio"], muestra_codmuestra=estroncio["Muestra"], isotopo_codisotopo=estroncio["CodIsotopo"], isotopo_analisis_codanalisis=estroncio["CodAnalisis"], estacion_codprocedencia=estroncio["Procedencia"], masa=estroncio["Masa"], metaestable="N", compartida="N", actividad_medida=estroncio["actividad"], error_actividad_medida=estroncio["error"], lid_medida=estroncio["amd"], numero_muestras=estroncio["muestras"],fecha_subida_fichero=datetime.now(), verificado=0, csn=0).save(using='gestion_memoria')

        else:
            print("No existe", recogida)
    '''
    muestras = HistoricoRecogida.objects.using('gestion_muestras').filter(codigo_recogida__codigo_memoria='G', fecha_hora_recogida__gte='2023-01-01 00:00:00').order_by('-identificador')
    for m in muestras:
        procedencia = RelacionProcedenciasGestionVraex.objects.using('gestion_muestras').filter(id_gestion_muestras=m.codigo_recogida.codigo_procedencia.codigo).get()
        tritio = {"actividad":0, "error":0, "amd":0, "muestras":0, "fecha_recogida_inicial":m.fecha_hora_recogida, "fecha_recogida_final":m.fecha_hora_recogida_2, "fecha_medida": None, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.id_vraex, "Muestra": m.codigo_recogida.codigo_csn.codigo, "CodIsotopo": "H", "CodAnalisis": "H", "Masa": 3}
        alfa = {"actividad":0, "error":0, "amd":0, "muestras":0, "fecha_recogida_inicial":m.fecha_hora_recogida, "fecha_recogida_final":m.fecha_hora_recogida_2, "fecha_medida": None, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.id_vraex, "Muestra": m.codigo_recogida.codigo_csn.codigo, "CodIsotopo": "", "CodAnalisis": "AT", "Masa": -1}
        beta = {"actividad":0, "error":0, "amd":0, "muestras":0, "fecha_recogida_inicial":m.fecha_hora_recogida, "fecha_recogida_final":m.fecha_hora_recogida_2, "fecha_medida": None, "motivo": "C", "Instalacion": "ALM", "Laboratorio": 23, "Procedencia": procedencia.id_vraex, "Muestra": m.codigo_recogida.codigo_csn.codigo, "CodIsotopo": "", "CodAnalisis": "BT", "Masa": -1}

        if not RelacionProcedenciasGestionVraex.objects.using('gestion_muestras').filter(id_gestion_muestras=m.codigo_recogida.codigo_procedencia.codigo).exists():
            print("No existe relacion. Crearla")
            valor = input("Introduce el id relacionado con la muestra (" + str(m.codigo_recogida.codigo_procedencia.codigo) +" , " + m.codigo_recogida.codigo_procedencia.nombre +")")
            relacion = RelacionProcedenciasGestionVraex(id_gestion_muestras=m.codigo_recogida.codigo_procedencia.codigo, id_vraex=valor)
            relacion.save(using='gestion_muestras')

        alicuotas = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica__id_historico_recogida=m.identificador)
        for a in alicuotas:
            if a.tratamiento.identificador == 18 or a.tratamiento.identificador == 5:
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
        '''
        if tritio["muestras"] > 0 or alfa["muestras"] > 0 or beta["muestras"] > 0:

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
    if request.method == "POST":
        cliente = Clientes(nombre=request.POST.get('nombre'), direccion=request.POST.get('direccion'), telefono=request.POST.get('telefono'), fax=request.POST.get('fax'), email=request.POST.get('email'), persona_contacto=request.POST.get('persona_contacto'), descripcion=request.POST.get('descripcion'), nif = request.POST.get('nif'))
        cliente.save(using='gestion_muestras')
        '''
            password = secrets.token_urlsafe(10)
            usuario = User.objects.create_user(username=c.nombre, email=c.email, password=password)
            grupo = Group.objects.get(name='Clientes Gestion Muestras') 
            grupo.user_set.add(usuario)
        '''
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
    
# metodos crud para gestion de procedencias
# parametros: codigo, nombre
@permission_required('auth.insercion_muestras')
def gestionProcedencias(request):
    return render(request, "gestionmuestras/crudProcedencias.html", {})

@permission_required('auth.insercion_muestras')
def gestionProcedenciasDatos(request):
    procedencias = Procedencias.objects.using('gestion_muestras').order_by('nombre').values('codigo', 'nombre')
    return JsonResponse(list(procedencias), safe=False)

@permission_required('auth.insercion_muestras')
def gestionProcedenciasNuevo(request):
    if request.method == "POST":
        procedencia = Procedencias(nombre=request.POST.get('nombre'))
        procedencia.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudProcedencias.html", {})
    else:
        return render(request, "gestionmuestras/crudFormulario.html", {"form":ProcedenciasForm()})
    
@permission_required('auth.insercion_muestras')
def gestionProcedenciasEditar(request):
    if request.POST.get('consulta') != '1':
        procedencia = Procedencias.objects.using('gestion_muestras').filter(identificador=request.POST.get('codigo')).get()
        procedencia.nombre = request.POST.get('nombre')
        procedencia.save(using='gestion_muestras')
        return render(request, "gestionmuestras/crudProcedencias.html", {})
    else:
        procedencia = Procedencias.objects.using('gestion_muestras').filter(identificador=request.POST.get('codigo')).values('codigo', 'nombre')[0]

        return render(request, "gestionmuestras/crudFormulario.html", {"form":ProcedenciasEditarForm(initial=procedencia)})
    
@permission_required('auth.insercion_muestras')
def gestionProcedenciasBorrar(request):
    if request.method == "POST":
        procedencia = Procedencias.objects.using('gestion_muestras').filter(identificador=request.POST.get('codigo')).get()
        procedencia.delete(using='gestion_muestras')
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
    relaciones = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').order_by('id_determinacion').values('identificador', 'id_determinacion__identificador', 'id_determinacion__nombre', 'id_tratamiento__identificador', 'id_tratamiento__descripcion', 'id_tratamiento__medida')
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
    

# metodos crud para la gestion de tratamiento codigos muestras
# parametros: id, id_muestra_codigo, id_tratamiento

@permission_required('auth.insercion_muestras')
def gestionProcesoDeterminaciones(request):
    return render(request, "gestionmuestras/crudProcesoDeterminaciones.html", {})

@permission_required('auth.insercion_muestras')
def gestionProcesoDeterminacionesDatos(request):
    
    resultados = []
    relacionTratamientoDeterminaciones = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').order_by('id_tratamiento').values('id_determinacion','id_determinacion__identificador','id_determinacion__nombre', 'id_tratamiento', 'id_tratamiento__identificador', 'id_tratamiento__descripcion')
    for r in relacionTratamientoDeterminaciones:
        tratamientosCodigos = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento__identificador=r['id_tratamiento__identificador']).values('id_muestra_codigo__codigo')
        for t in tratamientosCodigos:
            resultados.append({**r, **t})
    return JsonResponse(resultados, safe=False)

@permission_required('auth.gestion_muestras')
def graficoRelacionesTratamientos(request):
    if request.method == "POST":
        grafo = []
        det = Determinaciones.objects.using('gestion_muestras').values('identificador','nombre')
        determinacion = Determinaciones.objects.using('gestion_muestras').filter(identificador=request.POST.get('determinacion')).order_by('nombre').values('identificador','nombre')
        for d in determinacion:
            grafo.append(["Muestra", d['nombre']])

        tratamientosIncluidos = []
        relacionDetTrat = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').filter(id_determinacion__identificador=request.POST.get('determinacion')).values('id_determinacion__nombre', 'id_tratamiento__identificador', 'id_tratamiento__descripcion')
        for rdt in relacionDetTrat:
            tratamientosIncluidos.append(rdt['id_tratamiento__identificador'])
            grafo.append([rdt['id_determinacion__nombre'], rdt['id_tratamiento__descripcion']])

        relacionTratMues = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').filter(id_tratamiento__identificador__in=tratamientosIncluidos).values('id_tratamiento__descripcion', 'id_muestra_codigo__codigo')
        for rtm in relacionTratMues:
            grafo.append([rtm['id_tratamiento__descripcion'], rtm['id_muestra_codigo__codigo']])

        return render(request, "gestionmuestras/graficosRelacionTratamientos.html", {"datos":grafo, "determinaciones":det})
    else:
        grafo = []
        det = Determinaciones.objects.using('gestion_muestras').order_by('nombre').values('identificador','nombre')
        for d in det:
            grafo.append(["Muestra", d['nombre']])
        relacionDetTrat = RelacionDeterminacionesTratamientos.objects.using('gestion_muestras').values('id_determinacion__nombre', 'id_tratamiento__descripcion')
        for rdt in relacionDetTrat:
            grafo.append([rdt['id_determinacion__nombre'], rdt['id_tratamiento__descripcion']])

        relacionTratMues = RelacionTratamientosMuestraCodigo.objects.using('gestion_muestras').values('id_tratamiento__descripcion', 'id_muestra_codigo__codigo')
        for rtm in relacionTratMues:
            grafo.append([rtm['id_tratamiento__descripcion'], rtm['id_muestra_codigo__codigo']])

        return render(request, "gestionmuestras/graficosRelacionTratamientos.html", {"datos":grafo, "determinaciones":det})
    

'''
Metodo para calcular las medidas existentes en la base de datos de gestion de muestras
'''
@permission_required('auth.gestion_muestras')
def calcularMedidasExistentes(request):
    
    delay = datetime.now() - timedelta(days=150)
    alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida__fecha_hora_recepcion__gte=delay).all()
    
    #alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').all()
    
    relacionesMedida = DeterminacionMedidaInforme.objects.using('gestion_muestras').all()
    nuevasMedidas = []
    for a in alicuotas:
        if a.id_analiticas.identificador == 1: # alfa total
            medidas = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(id_alicuota=a.identificador, parametro='ALFA')
            for medida in medidas:
                if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=medida.cod_reducido, fecha_analisis=medida.fecha, determinacion_medida=relacionesMedida.filter(identificador=1).get()).exists():
                    RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=medida.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=1).get(), fecha_analisis=medida.fecha, actividad=medida.actividad, actividad_error=medida.incertidumbre, amd=medida.amd, tiempo_medida=medida.tiempo_cuenta, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                    nuevasMedidas.append({"Medida": "ALFA TOTAL", "Cod_reducido": medida.cod_reducido, "Fecha": medida.fecha, "Actividad": medida.actividad, "Incertidumbre": medida.incertidumbre, "AMD": medida.amd, "Tiempo": medida.tiempo_cuenta, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})
        elif a.id_analiticas.identificador == 5: # beta total
            medidas = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(id_alicuota=a.identificador, parametro='BETA')
            for medida in medidas:
                if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=medida.cod_reducido, fecha_analisis=medida.fecha, determinacion_medida=relacionesMedida.filter(identificador=2).get()).exists():
                    RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=medida.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=2).get(), fecha_analisis=medida.fecha, actividad=medida.actividad, actividad_error=medida.incertidumbre, amd=medida.amd, tiempo_medida=medida.tiempo_cuenta, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                    nuevasMedidas.append({"Medida": "BETA TOTAL", "Cod_reducido": medida.cod_reducido, "Fecha": medida.fecha, "Actividad": medida.actividad, "Incertidumbre": medida.incertidumbre, "AMD": medida.amd, "Tiempo": medida.tiempo_cuenta, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})
        elif a.id_analiticas.identificador == 2: # alfa/beta
            medidas = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(id_alicuota=a.identificador, parametro='ALFA')
            for medida in medidas:
                if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=medida.cod_reducido, fecha_analisis=medida.fecha, determinacion_medida=relacionesMedida.filter(identificador=1).get()).exists():
                    RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=medida.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=1).get(), fecha_analisis=medida.fecha, actividad=medida.actividad, actividad_error=medida.incertidumbre, amd=medida.amd, tiempo_medida=medida.tiempo_cuenta, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                    nuevasMedidas.append({"Medida": "ALFA", "Cod_reducido": medida.cod_reducido, "Fecha": medida.fecha, "Actividad": medida.actividad, "Incertidumbre": medida.incertidumbre, "AMD": medida.amd, "Tiempo": medida.tiempo_cuenta, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})

            medidas = RelacionTratamientoAlfabetaResultado.objects.using('gestion_muestras').filter(id_alicuota=a.identificador, parametro='BETA')
            for medida in medidas:
                if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=medida.cod_reducido, fecha_analisis=medida.fecha, determinacion_medida=relacionesMedida.filter(identificador=2).get()).exists():
                    RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=medida.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=2).get(), fecha_analisis=medida.fecha, actividad=medida.actividad, actividad_error=medida.incertidumbre, amd=medida.amd, tiempo_medida=medida.tiempo_cuenta, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                    nuevasMedidas.append({"Medida": "BETA", "Cod_reducido": medida.cod_reducido, "Fecha": medida.fecha, "Actividad": medida.actividad, "Incertidumbre": medida.incertidumbre, "AMD": medida.amd, "Tiempo": medida.tiempo_cuenta, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})
        elif a.id_analiticas.identificador == 4: # beta resto
            medidas = RelacionKBetaBetaresto.objects.using('gestion_muestras').filter(id_alicuota_br=a.identificador)
            for medida in medidas:
                if RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a).exists():
                    rat = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a).order_by('-fecha_inicio')[0]
                    if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=rat.cod_reducido, fecha_analisis=rat.fecha_fin, determinacion_medida=relacionesMedida.filter(identificador=3).get()).exists() and rat.fecha_fin is not None:
                        
                        RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=rat.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=3).get(), fecha_analisis=rat.fecha_fin, actividad=medida.resultado, actividad_error=medida.error, amd=0.0, tiempo_medida=medida.tiempo_cuenta, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                        nuevasMedidas.append({"Medida": "BETA RESTO", "Cod_reducido": rat.cod_reducido, "Fecha": rat.fecha_fin, "Actividad": medida.resultado, "Incertidumbre": medida.error, "AMD": 0.0, "Tiempo": medida.tiempo_cuenta, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})
        elif a.id_analiticas.identificador == 20: # tritio
            parametros = RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica=a)
            if parametros.filter(id_parametro_analitica__identificador=42).exists():
                if RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a).exists() and RelacionTratamientoRegistroResultado.objects.using('gestion_muestras').filter(id_analitica=a.identificador, fondo='NO').exists():
                    ciclos = RelacionTratamientoRegistroResultado.objects.using('gestion_muestras').filter(id_analitica=a.identificador, fondo='NO').order_by('-fecha0')[0]

                    rat = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a)[0]

                    actividad = float(parametros.filter(id_parametro_analitica__identificador=43).order_by('-identificador')[0].valor.replace(',', '.'))
                    error = float(parametros.filter(id_parametro_analitica__identificador=45).order_by('-identificador')[0].valor.replace(',', '.'))
                    amd = float(parametros.filter(id_parametro_analitica__identificador=44).order_by('-identificador')[0].valor.replace(',', '.'))
                    
                    if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=rat.cod_reducido, fecha_analisis=ciclos.fecha0, determinacion_medida=relacionesMedida.filter(identificador=6).get()).exists():
                        RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=rat.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=6).get(), fecha_analisis=ciclos.fecha0, actividad=actividad, actividad_error=error, amd=amd, tiempo_medida=ciclos.ctime*ciclos.numciclosleidos*60, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                        nuevasMedidas.append({"Medida": "TRITIO", "Cod_reducido": rat.cod_reducido, "Fecha": ciclos.fecha0, "Actividad": actividad, "Incertidumbre": error, "AMD": amd, "Tiempo": ciclos.ctime*ciclos.numciclosleidos*60, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})
                        
        elif a.id_analiticas.identificador == 18: # radon
            parametros = RelacionParametrosAnalitica.objects.using('gestion_muestras').filter(id_analitica=a)
            print("alicuota", a.identificador)
            if parametros.filter(id_parametro_analitica__identificador=42).exists():
                if RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a).exists() and RelacionTratamientoRegistroResultado.objects.using('gestion_muestras').filter(id_analitica=a.identificador, fondo='NO').exists():
                    ciclos = RelacionTratamientoRegistroResultado.objects.using('gestion_muestras').filter(id_analitica=a.identificador, fondo='NO').order_by('-fecha0')[0]

                    rat = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=a)[0]

                    actividad = float(parametros.filter(id_parametro_analitica__identificador=43).order_by('-identificador')[0].valor.replace(',', '.'))
                    error = float(parametros.filter(id_parametro_analitica__identificador=45).order_by('-identificador')[0].valor.replace(',', '.'))
                    amd = float(parametros.filter(id_parametro_analitica__identificador=44).order_by('-identificador')[0].valor.replace(',', '.'))

                    if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=a, cod_reducido=rat.cod_reducido, fecha_analisis=ciclos.fecha0, determinacion_medida=relacionesMedida.filter(identificador=5).get()).exists():
                        RelacionAlicuotasMedidas(id_alicuota=a, cod_reducido=rat.cod_reducido, determinacion_medida=relacionesMedida.filter(identificador=5).get(), fecha_analisis=ciclos.fecha0, actividad=actividad, actividad_error=error, amd=amd, tiempo_medida=ciclos.ctime*ciclos.numciclosleidos*60, cantidad=a.cantidad_muestra_analizada, rendimiento=0, seleccionado=0).save(using='gestion_muestras')
                        nuevasMedidas.append({"Medida": "RADON", "Cod_reducido": rat.cod_reducido, "Fecha": ciclos.fecha0, "Actividad": actividad, "Incertidumbre": error, "AMD": amd, "Tiempo": ciclos.ctime*ciclos.numciclosleidos*60, "Cantidad": a.cantidad_muestra_analizada, "Rendimiento": 0, "Seleccionado": 0})

    if len(nuevasMedidas) == 0:
        return render(request, "gestionmuestras/nuevasMedidasEncontradas.html", {"Error": "No se han encontrado nuevas medidas"})
    return render(request, "gestionmuestras/nuevasMedidasEncontradas.html", {"nuevasMedidas": nuevasMedidas})


def generadorQR(codigo, url):
    # Generar la imagen del QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size= 20,
        border=8,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Crear un objeto io.BytesIO para guardar la imagen en memoria
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Crear un objeto Image para añadir el texto debajo de la imagen del QR
    img_pil = Image.open(buffer)
    draw = ImageDraw.Draw(img_pil)
    text = f"{codigo}"
    #font =ImageFont.load_default()
    font = ImageFont.truetype("arial.ttf", 150)
    text_width, text_height = draw.textsize(text, font=font)
    x = (img_pil.width - text_width) / 2
    y = img_pil.height - text_height - 5
    draw.text((x, y), text, font=font, fill='black')

    # Crear un objeto io.BytesIO para guardar la imagen final en memoria
    buffer2 = io.BytesIO()
    img_pil.save(buffer2, format='PNG')
    buffer2.seek(0)
    return buffer2

def generadorCodigoBarras(texto, codigo):
    options = {
        'dpi': 800,
        'module_height': 5,
        'module_width': 0.3,
        'quiet_zone': 1,
        'font_size': 4,
        'text_distance': 2.5
    }
    barcode_format = barcode.get_barcode_class('code128')
    my_barcode = barcode_format(codigo, writer=ImageWriter())


@permission_required('auth.gestion_cliente')
def vistaCliente(request):
    usuario = {"nombre":User.objects.get(username=request.user), "last_login":User.objects.get(username=request.user).last_login, "password":User.objects.get(username=request.user).password}
    print(request.user)
    cliente = Clientes.objects.using('gestion_muestras').filter(identificador=156).get()
    muestras = HistoricoRecogida.objects.using('gestion_muestras').filter(cliente=cliente).order_by('-identificador').values('identificador', 'codigo_recogida__codigo_csn__nombre','codigo_recogida__codigo_procedencia__nombre', 'fecha_hora_recepcion', 'fecha_hora_recogida_ref', 'referencia_cliente', 'estado_de_muestra__identificador_estado', 'estado_de_muestra__descripcion', 'estado_de_muestra__icono')
    return render(request, "gestionmuestras/vistaCliente.html", {"usuario":usuario, "cliente":cliente, "muestras":muestras})

@permission_required('auth.admin')
def stamp(request):
    return render(request, "gestionmuestras/listaStamp.html", {})


@permission_required('auth.admin')
def stampDatos(request):
    stamps = Stamp.objects.using('gestion_muestras').all()
    return JsonResponse(list(stamps.values('id', 'nombre', 'pais', 'serie', 'anio', 'denominacion', 'color', 'fecha_exacta','fecha_modificacion')), safe=False)

@permission_required('auth.admin')
def stampVerificar(request, id):
    stampBuscado = Stamp.objects.using('gestion_muestras').filter(id=id).get()
    stampBuscado.fecha_modificacion = datetime.now()
    stampBuscado.save(using='gestion_muestras')
    return JsonResponse({}, safe=False)

def evaluarFuncion(funcion):
    evaluacion = eval(funcion)
    if type(evaluacion) == tuple:
        return evaluacion[1]
    else:
        return evaluacion