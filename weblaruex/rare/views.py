import datetime
from symbol import factor
from django.db.models import Avg
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum
from django.db.models.aggregates import StdDev
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.query import QuerySet
from django.contrib.auth.decorators import user_passes_test
import csv

from django.db.models import Max, F, Window

import os

import pytz
import logging
import hashlib

import simplejson
from django.utils import timezone
from datetime import datetime, timedelta, timezone, date
from time import gmtime, strftime

from .models import *

import math
import pytz as tz

import xlsxwriter
import pyproj

import ftplib
import shutil

import cv2

from rare.forms import FechasInforme
from cryptography.fernet import Fernet # librerias de encriptacion
from Crypto.Hash import MD5 # pip install pycryptodome

from clasesPropias.generarFechas import *
from clasesPropias.consultasGuardias import *


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

#url para calcular la matriz y cambiar el mapa para que acepte el id del mapa
def calculate_matrix(lat, lon, n_points, side, metros, mapa):
    coordinates = []
    turn = True
    direccion = True
    line = 0
    grados = 90
    actual_longitude, actual_latitude = lon,lat
    for i in range(n_points):
        line += 1
        actual_longitude, actual_latitude,backazimuth = pyproj.Geod(ellps='WGS84').fwd(actual_longitude, actual_latitude,grados,metros)
        coordinates.append({"id":i+1,"npos":i+1,"lat":actual_latitude,"lon":actual_longitude})
        pos = PosicionesProyectosMedida(npos=i+1,proyecto=mapa,lat=float(actual_latitude),lon=float(actual_longitude))
        pos.save(using='rvra')

        if ((line % side )==0):
            if (direccion):
                grados = grados + 90
            else:
                grados = grados - 90
            turn = False
        elif (not turn):
            if (direccion):
                grados = grados + 90
            else:
                grados = grados - 90
            direccion = not direccion
            turn = True
    return coordinates


def recepcionInformacionRedes(request):
    if request.method == "POST":
        print("ha llegado un post", request.POST)
        print("FILES:", request.FILES, "\nPOST:", request.POST)
        if os.path.exists(settings.STATION_FILES+request.POST.get('fichero')+".zip"):
            os.remove(settings.STATION_FILES+request.POST.get('fichero')+".zip")
        if os.path.exists(settings.STATION_FILES+request.POST.get('fichero')+".ef"):
            os.remove(settings.STATION_FILES+request.POST.get('fichero')+".ef")
        if os.path.exists(settings.STATION_FILES+request.POST.get('fichero')):
            shutil.rmtree(settings.STATION_FILES+request.POST.get('fichero'))
        handle_uploaded_file(settings.STATION_FILES+request.POST.get('fichero')+'.ef', request.FILES['file0'])
        decrypt(settings.STATION_FILES+request.POST.get('fichero')+'.ef',settings.STATION_FILES+request.POST.get('fichero')+".zip",load_key(request.POST.get('key')))
        hashCalculado = getmd5file(settings.STATION_FILES+request.POST.get('fichero')+".zip")
        print("HASH", hashCalculado)
        if hashCalculado == request.POST.get('hash'):
            file_size = os.path.getsize(settings.STATION_FILES+request.POST.get('fichero')+".zip")
            descomprimirZip(settings.STATION_FILES+request.POST.get('fichero')+".zip", settings.STATION_FILES+request.POST.get('fichero'))
            registrarEntregaCorrecta(request.POST.get('station'), request.POST.get('key'), request.POST.get('network'), request.POST.get('conexion'), hashCalculado, request.POST.get('hash'), file_size)
            almacenarInformacion(settings.STATION_FILES+request.POST.get('fichero'))
            return JsonResponse({"hash":"CORRECTO"}, safe=False)
        else:
            return JsonResponse({"hash":"INCORRECTO"}, safe=False)
        
    else:
        return render(
            request,
            "formInfo.html",
            {}
        )
   
   
def almacenarInformacion(ruta):
    print("ALMACENAR INFORMACION")
    if os.path.exists(ruta):
        ficheros = os.listdir(ruta)
        for fichero in ficheros:
            if fichero.endswith(".csv"):
                if fichero == "espectrometria.csv":
                    cargarEspectrometria(ruta+"/"+fichero)
                elif fichero == "espectrometriaAcumulado.csv":
                    cargarEspectrometriaAcumulado(ruta+"/"+fichero)
                elif fichero == "estMeteorologica.csv":
                    cargarEstMeteorologica(ruta+"/"+fichero)
                elif fichero == "gammaYRadioyodos.csv":
                    cargarGammaYRadioyodos(ruta+"/"+fichero)
                elif fichero == "paramControl.csv":
                    cargarParametros(ruta+"/"+fichero)
                elif fichero == "ultimosValores.csv":
                    cargarUltimosValores(ruta+"/"+fichero)

def registrarEntregaCorrecta(estacion, clave, red, conexion, hashCalculado, hashRecibido, tamanioFichero):
    print("REGISTRANDO ENTREGA CORRECTA: ", estacion, clave, red, conexion, hashCalculado, hashRecibido, tamanioFichero)
    Entregasestaciones.objects.using('rvra').create(id_estacion=Estaciones.objects.using('rvra').filter(id=estacion).get(), clave=clave, red=red, conexion=TipoConexion.objects.using('rvra').filter(tipo=conexion).get(), hashcalculado=hashCalculado, hashrecibido=hashRecibido, tamaniofichero=tamanioFichero)

def cargarEspectrometria(ruta):
    data = pd.read_csv(ruta)
    df = pd.DataFrame(data)
    print("Total datos cargarEspectrometria:", len(df.index))
    for index, row in df.iterrows():
        print(f'Index: {index}, row: {row.values}')
        print("Tengo que insertar: ", row['fecha_hora'], row['relacion_detectores_estacion_id'], row['isotopos_id'], row['actividad'], row['error'], row['amd'], row['valido'])
        EstEspecGamma.objects.using('rvra').create(fecha_hora=row['fecha_hora'], relacion_detectores_estacion_id=row['relacion_detectores_estacion_id'], isotopos_id=row['isotopos_id'], actividad=row['actividad'], error=row['error'], amd=row['amd'], valido=row['valido'])


def cargarEspectrometriaAcumulado(ruta):
    data = pd.read_csv(ruta)
    df = pd.DataFrame(data)
    print("Total datos cargarEspectrometriaAcumulado:", len(df.index))
    for index, row in df.iterrows():
        print(f'Index: {index}, row: {row.values}')
        print("Tengo que insertar: ", row['fecha_hora'], row['relacion_detectores_estacion_id'], row['isotopos_id'], row['actividad'], row['error'], row['amd'], row['valido'])
        EstEspecGammaAcumulados.objects.using('rvra').create(fecha_hora=row['fecha_hora'], relacion_detectores_estacion_id=row['relacion_detectores_estacion_id'], isotopos_id=row['isotopos_id'], actividad=row['actividad'], error=row['error'], amd=row['amd'], valido=row['valido'])

def cargarEstMeteorologica(ruta):
    data = pd.read_csv(ruta)
    df = pd.DataFrame(data)
    print("Total datos cargarEstMeteorologica:", len(df.index))
    for index, row in df.iterrows():
        print(f'Index: {index}, row: {row.values}')
        print("Tengo que insertar: ", row['fecha_hora'], row['estaciones'], row['canales'], row['valor'], row['valido'])
        if not EstMeteorologicas.objects.using('rvra').filter(fecha_hora=row['fecha_hora'], estaciones=Estaciones.objects.using('rvra').filter(id=row['estaciones']).get(), canales=Canales.objects.using('rvra').filter(id=row['canales']).get()).exists():  
            EstMeteorologicas.objects.using('rvra').create(fecha_hora=row['fecha_hora'], estaciones=Estaciones.objects.using('rvra').filter(id=row['estaciones']).get(), canales=Canales.objects.using('rvra').filter(id=row['canales']).get(), valor=row['valor'], valido=row['valido'])

def cargarGammaYRadioyodos(ruta):
    data = pd.read_csv(ruta)
    df = pd.DataFrame(data)
    print("Total datos cargarGammaYRadioyodos:", len(df.index))
    for index, row in df.iterrows():
        print(f'Index: {index}, row: {row.values}')
        print("Tengo que insertar: ", row['fecha_hora'], row['estaciones'], row['canales'], row['valor'], row['valido'])
        if not EstGamYRadioyodosFK.objects.using('rvra').filter(fecha_hora=row['fecha_hora'], estaciones=Estaciones.objects.using('rvra').filter(id=row['estaciones']).get(), canales=Canales.objects.using('rvra').filter(id=row['canales']).get()).exists():  
            EstGamYRadioyodosFK.objects.using('rvra').create(fecha_hora=row['fecha_hora'], estaciones=Estaciones.objects.using('rvra').filter(id=row['estaciones']).get(), canales=Canales.objects.using('rvra').filter(id=row['canales']).get(), valor=row['valor'], valido=row['valido'])

def cargarParametros(ruta):
    data = pd.read_csv(ruta)
    df = pd.DataFrame(data)
    print("Total datos cargarParametros:", len(df.index))
    for index, row in df.iterrows():
        print(f'Index: {index}, row: {row.values}')
        print("Tengo que insertar: ", row['fecha_hora'], row['estaciones_id'], row['canales'], row['valor'], row['valido'])
        if not ParamControl.objects.using('rvra').filter(fecha_hora=row['fecha_hora'], estaciones=Estaciones.objects.using('rvra').filter(id=row['estaciones_id']).get(), canales=Canales.objects.using('rvra').filter(id=row['canales']).get()).exists():  
            ParamControl.objects.using('rvra').create(fecha_hora=row['fecha_hora'], estaciones=Estaciones.objects.using('rvra').filter(id=row['estaciones_id']).get(), canales=Canales.objects.using('rvra').filter(id=row['canales']).get(), valor=row['valor'], valido=row['valido'])

def cargarUltimosValores(ruta):
    data = pd.read_csv(ruta)
    df = pd.DataFrame(data)
    print("Total datos cargarUltimosValores:", len(df.index))
    for index, row in df.iterrows():
        print(f'Index: {index}, row: {row.values}')
        print("Tengo que insertar: ", row['fecha_hora'], row['estacion_id'], row['can_det_est'], row['isotopo_id'], row['valor'], row['color'], row['error'], row['amd'], row['unidades'])
        UltimosValoresRecibidos.objects.using('rvra').filter(estacion_id=row['estacion_id'], can_det_est=row['can_det_est'], isotopo_id=row['isotopo_id']).update(fecha_hora=row['fecha_hora'], valor=row['valor'], color=row['color'], error=row['error'], amd=row['amd'], unidades=row['unidades'])

def descomprimirZip(fichero, ruta):
    shutil.unpack_archive(fichero, ruta)
    
def load_key(nombre):
    print("CLAVE", settings.STATION_KEYS+nombre+".key")
    return open(settings.STATION_KEYS+nombre+".key", "rb").read()

def decrypt(encryptedFile, filename, key):
    f = Fernet(key)
    with open(encryptedFile, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)

    # write the original file
    with open(filename, "wb") as file:
        file.write(decrypted_data)

def getmd5file(archivo):
    try:
        chunk_size = 8192
        hashmd5 = MD5.new()
        with open(archivo, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if len(chunk):
                    hashmd5.update(chunk)
                else:
                    break
        return hashmd5.hexdigest()
    except Exception as e:
        return ""
    except:
        return ""

def handle_uploaded_file(destino, f):
    with open(destino, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def calcularPuntos(request):
    coords = calculate_matrix(request.POST.get('idPuntoLat'), request.POST.get('idPuntoLon'), int(request.POST.get('numPuntos')), int(request.POST.get('linea')), int(request.POST.get('metros')), request.POST.get('mapa'))
    
    proyectos = PosicionesProyectosMedida.objects.using('rvra').values()
    return render(
        request,
        "listadoMapasProyectos.html",
        {
            "proyectos": proyectos,
        }
    )

def medidasElHondon(request, id_mapa):
    if request.method == "POST":
        hoy = datetime.now()
        RelacionPosicionesMedidas(id_punto=request.POST.get('idPunto'),analista=request.POST.get('analista'),
        fecha_hora=hoy,dosis=request.POST.get('dosis'),cuentas=request.POST.get('cuentas'),tiempo_medida=request.POST.get('tiempo_medida'),
        tiempo_medida_unidad=request.POST.get('tiempo_medida_unidad'),comentario=request.POST.get('comentario')).save(using='rvra')
    coords = PosicionesProyectosMedida.objects.using('rvra').filter(proyecto=id_mapa).values()
    return render(
        request,
        "mapaMedidas.html",
        {
            "id_mapa": id_mapa,
            "coords": coords,
        }
    )
    
def medidasElHondonJuan(request):
    coords = []
    id_mapa = "Hondon102021"
    puntos = RelacionPosicionesMedidas.objects.using('rvra').filter(analista='Juan')
    posiciones = PosicionesProyectosMedida.objects.using('rvra').all()
    for p in puntos:
        posicion = posiciones.filter(id=p.id_punto)[0]
        coords.append({"id":posicion.id,"npos":posicion.npos, "lat":posicion.lat, "lon":posicion.lon, "cuentas":p.cuentas, "tmedidad":p.tiempo_medida})
    return render(
        request,
        "mapaMedidasHondon.html",
        {
            "id_mapa": id_mapa,
            "coords": coords,
        }
    )

def proyectosMedida(request):
    proyectos = PosicionesProyectosMedida.objects.using('rvra').values()
    return render(
        request,
        "listadoMapasProyectos.html",
        {
            "proyectos": proyectos,
        }
    )

def httpsVerify(request):
    return FileResponse(open(settings.MEDIA_ROOT+"/ED84F28D70253E0617BDDA0714A304B6.txt", 'rb'), content_type='text/plain')

def consultarInformacionMedida(request, id):
    medidas = RelacionPosicionesMedidas.objects.using('rvra').filter(id_punto=id).order_by('fecha_hora')
    html = render_to_string('informacionMedidasPunto.html', {'medidas': medidas})
    return HttpResponse(html)


######################### RAREX #########################
######################### RAREX PUBLICO #########################

######################### RAREX PRIVADO #########################
def getPortadaRarex(request):
    user = request.user
    return render(
        request,
        "portadaRarex.html",
        {
            "user":user,
        }
    )

def getPortadaRadiacion(request):
    user = request.user
    return render(
        request,
        "portadaRadiacion.html",
        {
            "user":user,
        }
    )


# MAPA RAREX LIVE
@permission_required('auth.red_live')
def getMapaEstado(request):
    return render(request, "mapaRareLive.html")

# CONSULTA RECARGA MAPA DATOS RAREX LIVE
@permission_required('auth.red_live')
def getMapaEstadoActual(request):
    listaEstaciones = []
    listaEstacionesTotales = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]
    ultimos_valores_recibidos = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=1,estacion_id__in=listaEstacionesTotales)
    estaciones = Estaciones.objects.using('rvra').filter(id__in=listaEstacionesTotales)
    relaciones = Relacion.objects.using('rvra').filter(estac__in=listaEstacionesTotales).filter(canal=1)

    hoy = datetime.now(timezone.utc) + timedelta(hours=1)

    for ultimo_valor in ultimos_valores_recibidos:
        estacionAuxiliar = {}

        for aux in estaciones:
            if aux.id == ultimo_valor.estacion_id:
                estacion = aux
        estacionAuxiliar["id"] = estacion.id
        estacionAuxiliar["nombre"] = estacion.nombre
        estacionAuxiliar["lat"] = estacion.map_lat
        estacionAuxiliar["lon"] = estacion.map_lon

        relacion = []
        for aux in relaciones:
            if aux.estac == ultimo_valor.estacion_id:
                relacion.append(aux)
                estacionAuxiliar["fondo"] = round(aux.monitorizar, 2)

        estacionAuxiliar["valor"] = round(ultimo_valor.valor, 2)
        estacionAuxiliar["fecha"] = ultimo_valor.fecha_hora.strftime("%d/%m/%Y, %H:%M")
        dif = hoy - ultimo_valor.fecha_hora
        diferencia = hoy - ultimo_valor.fecha_hora
        if (ultimo_valor.estacion_id in [5, 54, 55] and diferencia > timedelta(hours=2)) or (
                ultimo_valor.estacion_id not in [5, 54, 55] and diferencia > timedelta(hours=1)):
            estacionAuxiliar["retraso"] = 1
        elif (ultimo_valor.estacion_id in [5, 54, 55] and diferencia > timedelta(hours=3)) or (
                ultimo_valor.estacion_id not in [5, 54, 55] and diferencia > timedelta(hours=2)):
            estacionAuxiliar["retraso"] = 2
        else:
            estacionAuxiliar["retraso"] = 0

        textoUnidades = "Bq/m3"
        textoTipo = "aire"
        listaAguas = [12, 13, 57]
        if (ultimo_valor.estacion_id in listaAguas):
            textoTipo = "agua"
            textoUnidades = "Bq/L"
        estacionAuxiliar["unidad"] = textoUnidades
        estacionAuxiliar["tipo"] = textoTipo
        listaEstaciones.append(estacionAuxiliar)

    user = request.user
    valores = {"lista": listaEstaciones}
    jsonValores = simplejson.dumps(valores, default=myconverter)
    return JsonResponse(jsonValores, safe=False)
    

@permission_required('auth.red_live')
def solicitarCalculoMediasRareDosis(request):
    mediasIntactas, mediasRecalculadas, mediasNuevas, mediasNull = recalculoMediasDosis()
    return JsonResponse({"mediasIntactas":mediasIntactas, "mediasRecalculadas": mediasRecalculadas, "mediasNuevas": mediasNuevas, "mediasNull":mediasNull}, safe=False)

def recalculoMediasDosis():
    dias = datetime.now(timezone.utc) - timedelta(days=3)
    estaciones = [1, 2, 3, 4, 5 , 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57, 61]
    mediasIntactas, mediasRecalculadas, mediasNuevas, mediasNull = 0, 0, 0, 0
    canal = Canales.objects.using('rvra').filter(id=1).get()
    for x in estaciones:
        estacion = Estaciones.objects.using('rvra').filter(id=x).get()
        today = date.today()
        fechaAux = dias.date()
        while fechaAux < today:
            if EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__date=fechaAux,estaciones=x,canales=1,valido=1).exists():
                #calculo medias
                media = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__date=fechaAux,estaciones=x,canales=1,valido=1).aggregate(Avg('valor'))
                if MediasDiarias.objects.using('rvra').filter(fecha=fechaAux, id_estacion=estacion, id_detector=0, id_canal=canal).exists():
                    mediaUltima = MediasDiarias.objects.using('rvra').filter(fecha=fechaAux, id_estacion=estacion, id_detector=0, id_canal=canal).get()
                    if mediaUltima.valor == round(media['valor__avg'], 3):
                        mediasIntactas += 1
                    else:
                        mediaUltima.valor = round(media['valor__avg'], 3)
                        mediasRecalculadas += 1
                else:
                    MediasDiarias.objects.using('rvra').create(fecha=fechaAux, id_estacion=estacion, id_detector=0, id_canal=canal, valor=round(media['valor__avg'],3))
                    mediasNuevas += 1
            else:
                if MediasDiarias.objects.using('rvra').filter(fecha=fechaAux, id_estacion=estacion, id_detector=0, id_canal=canal).exists():
                    mediaUltima = MediasDiarias.objects.using('rvra').filter(fecha=fechaAux, id_estacion=estacion, id_detector=0, id_canal=canal).get()
                    mediaUltima.valor = None
                else:
                    m = MediasDiarias.objects.using('rvra').create(fecha=fechaAux, id_estacion=Estaciones.objects.using('rvra').filter(id=x).get(), id_detector=0, id_canal=canal, valor=None)
                mediasNull += 1
            fechaAux += timedelta(days=1)
    return mediasIntactas, mediasRecalculadas, mediasNuevas, mediasNull

# CONSULTA RECARGA MAPA DATOS APA LIVE
@permission_required('auth.red_live')
def getMapaEstadoActualAPA(request):
    listaEstaciones = []
    listaEstacionesTotales = [10]
    ultimos_valores_recibidos = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=1025, isotopo_id=14,estacion_id__in=listaEstacionesTotales)
    estaciones = Estaciones.objects.using('rvra').filter(id__in=listaEstacionesTotales)
    relaciones = Relacion.objects.using('rvra').filter(estac__in=listaEstacionesTotales).filter(canal=1)

    hoy = datetime.now(timezone.utc) + timedelta(hours=1)

    for ultimo_valor in ultimos_valores_recibidos:
        estacionAuxiliar = {}

        for aux in estaciones:
            if aux.id == ultimo_valor.estacion_id:
                estacion = aux
        estacionAuxiliar["id"] = estacion.id
        estacionAuxiliar["nombre"] = "EVORA"
        estacionAuxiliar["lat"] = 38.536
        estacionAuxiliar["lon"] = -7.888

        relacion = []
        for aux in relaciones:
            if aux.estac == ultimo_valor.estacion_id:
                relacion.append(aux)
                estacionAuxiliar["fondo"] = round(aux.monitorizar, 3)

        estacionAuxiliar["valor"] = round(ultimo_valor.valor, 3)
        estacionAuxiliar["amd"] = round(ultimo_valor.amd, 3)
        estacionAuxiliar["fecha"] = ultimo_valor.fecha_hora.strftime("%d/%m/%Y, %H:%M")
        dif = hoy - ultimo_valor.fecha_hora
        diferencia = hoy - ultimo_valor.fecha_hora
        if (ultimo_valor.estacion_id in [5, 54, 55] and diferencia > timedelta(hours=2)) or (
                ultimo_valor.estacion_id not in [5, 54, 55] and diferencia > timedelta(hours=1)):
            estacionAuxiliar["retraso"] = 1
        elif (ultimo_valor.estacion_id in [5, 54, 55] and diferencia > timedelta(hours=3)) or (
                ultimo_valor.estacion_id not in [5, 54, 55] and diferencia > timedelta(hours=2)):
            estacionAuxiliar["retraso"] = 2
        else:
            estacionAuxiliar["retraso"] = 0

        textoUnidades = "Bq/m3"
        textoTipo = "aire"
        listaAguas = [12, 13, 57]
        if (ultimo_valor.estacion_id in listaAguas):
            textoTipo = "agua"
            textoUnidades = "Bq/L"
        estacionAuxiliar["unidad"] = textoUnidades
        estacionAuxiliar["tipo"] = textoTipo
        listaEstaciones.append(estacionAuxiliar)

    user = request.user
    valores = {"lista": listaEstaciones}
    jsonValores = simplejson.dumps(valores, default=myconverter)
    return JsonResponse(jsonValores, safe=False)

# MAPA DRONE RAREX LIVE
@permission_required('auth.red_live')
def getMapaDroneEstado(request):
    return render(request, "mapaRareDrone.html")

# CONSULTA RECARGA MAPA DATOS RAREX LIVE
@permission_required('auth.red_live')
def getMapaDroneEstadoActual(request):
    listaEstaciones = []
    listaEstacionesTotales = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]
    ultimos_valores_recibidos = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=1).filter(
        estacion_id__in=listaEstacionesTotales)
    estaciones = Estaciones.objects.using('rvra').filter(id__in=listaEstacionesTotales)
    relaciones = Relacion.objects.using('rvra').filter(estac__in=listaEstacionesTotales).filter(canal=1)

    hoy = datetime.now(timezone.utc) + timedelta(hours=1)

    for ultimo_valor in ultimos_valores_recibidos:
        estacionAuxiliar = {}

        for aux in estaciones:
            if aux.id == ultimo_valor.estacion_id:
                estacion = aux
        estacionAuxiliar["id"] = estacion.id
        estacionAuxiliar["nombre"] = estacion.nombre
        estacionAuxiliar["lat"] = estacion.map_lat
        estacionAuxiliar["lon"] = estacion.map_lon

        relacion = []
        for aux in relaciones:
            if aux.estac == ultimo_valor.estacion_id:
                relacion.append(aux)
                estacionAuxiliar["fondo"] = round(aux.monitorizar, 2)

        estacionAuxiliar["valor"] = round(ultimo_valor.valor, 2)
        estacionAuxiliar["fecha"] = ultimo_valor.fecha_hora.strftime("%d/%m/%Y, %H:%M")
        dif = hoy - ultimo_valor.fecha_hora
        diferencia = hoy - ultimo_valor.fecha_hora
        if (ultimo_valor.estacion_id in [5, 54, 55] and diferencia > timedelta(hours=2)) or (
                ultimo_valor.estacion_id not in [5, 54, 55] and diferencia > timedelta(hours=1)):
            estacionAuxiliar["retraso"] = 1
        elif (ultimo_valor.estacion_id in [5, 54, 55] and diferencia > timedelta(hours=3)) or (
                ultimo_valor.estacion_id not in [5, 54, 55] and diferencia > timedelta(hours=2)):
            estacionAuxiliar["retraso"] = 2
        else:
            estacionAuxiliar["retraso"] = 0

        textoUnidades = "Bq/m3"
        textoTipo = "aire"
        listaAguas = [12, 13, 57]
        if (ultimo_valor.estacion_id in listaAguas):
            textoTipo = "agua"
            textoUnidades = "Bq/L"
        estacionAuxiliar["unidad"] = textoUnidades
        estacionAuxiliar["tipo"] = textoTipo
        listaEstaciones.append(estacionAuxiliar)

    user = request.user
    valores = {"lista": listaEstaciones}
    jsonValores = simplejson.dumps(valores, default=myconverter)
    return JsonResponse(jsonValores, safe=False)

# CONSULTA RECARGA MAPA DATOS RAREX LIVE
@permission_required('auth.red_live')
def getUltimosMensajes(request):
    mensajes = MensajeHistoenvio.objects.using('rvra').filter(remite="Juan Baeza").order_by('-fecha')[:5].values()
    return JsonResponse({"mensajes": list(mensajes)}, safe=False)


@permission_required('auth.red_live')
def getDispositivosMoviles(request):
    # id, id_estacion, tipo, nombre, activo
    dispositivos = DispositivosMoviles.objects.using('rvra')
    html = render_to_string('datos_mapa_disp_moviles.html', {'dispositivos': dispositivos})
    return HttpResponse(html)

def dmm_to_dd(coord):
    degrees = int(coord[:2])
    minutes = float(coord[3:-2])
    dd = degrees + (minutes/60)
    if "S" in coord or "W" in coord:
        dd = -dd
    return dd

@permission_required('auth.red_live')
def getUltimoValorMovil(request, tipo, id_estacion, marker_id):
    medidas = []
    if tipo == "DRONE":
        medidas = MedidasEstacionMovil.objects.using('rvra').filter(id_estacion=id_estacion).order_by('-id')[:1].values()
    elif tipo == "FURGONETA":
        labmovil = UMovil.objects.using('csn').order_by('-id')[:1].values()
        lat, lon = dmm_to_dd(labmovil[0]["cadena"][:11]), dmm_to_dd(labmovil[0]["cadena"][12:23])
        dosis = labmovil[0]["cadena"][24:]
        medidas.append(
            {
                "id": labmovil[0]["id"], 
                "fecha_medida": labmovil[0]["fecha_hora"],
                "cuentas": None,
                "dosis": float(dosis.replace(",", ".")),
                "lat": lat,
                "lon": lon,
                "distancia": 1,
                "altura": 1
             })

    labels = []
    if medidas[0]["cuentas"] != None:
        for i in range(len(medidas[0]["cuentas"].split(","))):
            labels.append(i)
    return JsonResponse({"valor": medidas[0], "marker_id": marker_id, "labels": labels}, safe=False)

@permission_required('auth.rarex_drone')
def getSesionesMedidaMovil(request):
    return render(request, "sesionesMedidaMovil.html")

@permission_required('auth.rarex_drone')
def getSesionMedida(request, id_sesion):
    sesion = SesionesMoviles.objects.using('rvra').filter(id=id_sesion)[0]

    medidas = MedidasEstacionMovil.objects.using('rvra').filter(id_estacion=sesion.id_disp_movil.id_estacion, fecha_medida__gte=sesion.fecha_inicio, fecha_medida__lte=sesion.fecha_fin).values()

    return JsonResponse({"sesion": id_sesion, "tipo": sesion.id_disp_movil.tipo, "medidas": list(medidas)}, safe=False)

@permission_required('auth.rarex_drone')
def getSesionesMedidaMovilCarga(request):
    sesiones = []
    consultaSesiones = SesionesMoviles.objects.using('rvra').order_by('-id')
    medidas = MedidasEstacionMovil.objects.using('rvra')
    for c in consultaSesiones:
        if (medidas.filter(id_estacion=c.id_disp_movil.id_estacion, fecha_medida__gte=c.fecha_inicio, fecha_medida__lte=c.fecha_fin).exists()):
            sesion = {"infoSesion": c, "valorPrimero": medidas.filter(id_estacion=c.id_disp_movil.id_estacion, fecha_medida__gte=c.fecha_inicio, fecha_medida__lte=c.fecha_fin)[0], "total": len(medidas.filter(id_estacion=c.id_disp_movil.id_estacion, fecha_medida__gte=c.fecha_inicio, fecha_medida__lte=c.fecha_fin))}
        else:
            sesion = {"infoSesion": c}
        sesiones.append(sesion)

    html = render_to_string('infoSesionesDispMoviles.html', {'sesiones': sesiones})
    return HttpResponse(html)

@permission_required('auth.red_live')
def getUltimoParametrosMovil(request, id_estacion):
    valores = []
    parametros = ParamControl.objects.using('rvra').filter(estaciones__id=id_estacion)
    if parametros.filter(canales__id=5).exists():
        valores.append(parametros.filter(canales__id=5)[0])
    if parametros.filter(canales__id=6).exists():
        valores.append(parametros.filter(canales__id=6)[0])
    if parametros.filter(canales__id=7).exists():
        valores.append(parametros.filter(canales__id=7)[0])
    if parametros.filter(canales__id=8).exists():
        valores.append(parametros.filter(canales__id=8)[0])
    if parametros.filter(canales__id=9).exists():
        valores.append(parametros.filter(canales__id=9)[0])
    if parametros.filter(canales__id=10).exists():
        valores.append(parametros.filter(canales__id=10)[0])
    if parametros.filter(canales__id=11).exists():
        valores.append(parametros.filter(canales__id=11)[0])
    if parametros.filter(canales__id=12).exists():
        valores.append(parametros.filter(canales__id=12)[0])
    if parametros.filter(canales__id=80).exists():
        valores.append(parametros.filter(canales__id=80)[0])
    if parametros.filter(canales__id=83).exists():
        valores.append(parametros.filter(canales__id=83)[0])

    html = id_estacion + "$" + render_to_string('parametros_disp_moviles.html', {'id_estacion':id_estacion, 'parametros': valores})
    
    return HttpResponse(html)

# CONSULTA MAPA DIARIO RAREX
def getMapaMedia(request):
    listaEstaciones = []
    hoy = date.today()
    ayer = date.today() - timedelta(days=1)
    mes = date.today() - timedelta(days=31)
    unAnio = date.today() - timedelta(days=365)
    listaEstacionesTotales = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]

    ubicaciones = UbicacionesInteres.objects.using('rvra')
    for ubi in ubicaciones:
        estacionAuxiliar = {}
        estacionAuxiliar["id"] = ubi.id_ubicacion
        estacionAuxiliar["nombre"] = ubi.nombre
        estacionAuxiliar["lat"] = ubi.lat
        estacionAuxiliar["lon"] = ubi.lon
        estacionAuxiliar["tipo"] = ubi.tipo
        listaEstaciones.append(estacionAuxiliar)

    user = request.user
    jsonListaEstaciones = simplejson.dumps(listaEstaciones, default=myconverter)
    return render(request, "mapaRareMedia.html",
                  {"user": user, "estaciones": listaEstaciones, "json_estaciones": jsonListaEstaciones})
    # return render(request, "mapaRareMedia.html", {"user":user,"estaciones":listaEstaciones,"json_estaciones":jsonListaEstaciones,"media":actividad, "fechas":fechas})

'''
@permission_required('auth.mapa_diario')
def getMapaMedia(request):
    return render(request, "mapaRareMedia.html")
'''

# RECARGA VALORES MEDIA RAREX
'''
@permission_required('auth.mapa_diario')
def getValoresMedia(request):
    listaEstaciones = []
    hoy = date.today()
    ayer = date.today() - timedelta(days=1)
    mes = date.today() - timedelta(days=31)
    unAnio = date.today() - timedelta(days=365)
    listaEstacionesTotales = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]
    estaciones = Estaciones.objects.using('rvra').filter(id__in=listaEstacionesTotales)
    total = 0
    medias = MediasDiarias.objects.using('rvra').filter(id_canal=1).filter(fecha__gte=mes).order_by('-fecha')
    for estacion in estaciones:
        estacionAuxiliar = {}
        estacionAuxiliar["id"] = estacion.id
        estacionAuxiliar["nombre"] = estacion.nombre.encode("UTF-8")
        estacionAuxiliar["unidad"] = "uSv/h"
        estacionAuxiliar["lat"] = estacion.map_lat
        estacionAuxiliar["lon"] = estacion.map_lon
        estacionAuxiliar["tipo"] = 'RARE'
        estacionAuxiliar["fondo"] = round(
            MediasDiarias.objects.using('rvra').filter(id_estacion=estacionAuxiliar["id"]).filter(id_canal=1).aggregate(
                Avg('valor'))["valor__avg"], 2)
        

        infoEstacion = InformacionesEstaciones.objects.using("rvra").filter(id_estacion=estacion.id)[0]
        ayerInicio = datetime.today() - timedelta(days=1)
        ayerFin = datetime.today() - timedelta(days=1)
        ayerInicio = ayerInicio.replace(hour=0, minute=0, second=0)
        ayerFin = ayerFin.replace(hour=23, minute=59, second=59)
        numValoresDosis = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__gte=ayerInicio, fecha_hora__lte=ayerFin).filter(canales=1).filter(estaciones=estacion.id).count()
        valNecesarios = 24 * 60 * 60 / infoEstacion.tiempo_consulta
        operatividadDosis = int((numValoresDosis / valNecesarios) * 100)
        if operatividadDosis > 100:
            operatividadDosis = 100
        estacionAuxiliar["operatividad"] = operatividadDosis

        listaEstaciones.append(estacionAuxiliar)

    media, mediaAnual, actividad = 0.0, 0.0, 0.0
    fechas = []
    if len(listaEstaciones) > 0 and len(valores) != 0:
        maximo = {"valor": 0}
        for est in listaEstaciones:
            if est["valor"] != None:
                if maximo["valor"] < est["valor"]:
                    maximo = est

        media = (maximo["valor"] * 24 * 365)
        mediaAnual = (maximo["fondo"] * 24 * 365)
        actividad = round(media - mediaAnual, 3)
        if actividad <= 0:
            actividad = 0.0
        fechas = maximo["fechas"][::-1]

    user = request.user
    valores = {"listaEstaciones": listaEstaciones, "media": actividad, "fechas": fechas}
    jsonValores = simplejson.dumps(valores, default=myconverter)
    return JsonResponse(jsonValores, safe=False)

'''
'''
@permission_required('auth.mapa_diario')
def getValoresMedia(request):
    medias = []
    listaEstacionesTotales = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]
    sql = 'SELECT * FROM ( SELECT * FROM medias_diarias WHERE ID_CANAL=1 AND ID_ESTACION IN ('+listaEstacionesTotales+') ORDER BY FECHA DESC ) AS X GROUP BY ID_ESTACION'
    for media in MediasDiarias.objects.using('rvra').raw(sql):
        medias.append({"fecha":media.fecha,"estacion":media.id_estacion.id,"nombre":media.id_estacion.nombre,"lat":media.id_estacion.map_lat,"lon":media.id_estacion.map_lon,"valor":media.valor})
    result= MediasDiarias.objects.using('rvra').filter(id_canal__id=1, id_estacion__id__in=listaEstacionesTotales).order_by('-id_estacion').values('id_estacion','valor').annotate(max_fecha=Max('fecha'))

    #return JsonResponse({"medias":medias}, safe=False)
    return JsonResponse(list(result), safe=False)

'''
def getValoresMedia(request):
    listaEstaciones = []
    hoy = date.today()
    ayer = date.today() - timedelta(days=1)
    mes = date.today() - timedelta(days=31)
    tiempoFondo = date.today() - timedelta(days=14)
    unAnio = date.today() - timedelta(days=365)
    listaEstacionesTotales = [1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 40, 53, 54, 55, 56, 57]
    estaciones = Estaciones.objects.using('rvra').filter(id__in=listaEstacionesTotales)
    total = 0
    medias = MediasDiarias.objects.using('rvra').filter(id_canal=1, fecha__gte=mes, id_estacion__id__in=estaciones).order_by('-fecha')
    for estacion in estaciones:
        estacionAuxiliar = {}
        estacionAuxiliar["id"] = estacion.id
        estacionAuxiliar["nombre"] = estacion.nombre.encode("UTF-8")
        estacionAuxiliar["unidad"] = "uSv/h"
        estacionAuxiliar["lat"] = estacion.map_lat
        estacionAuxiliar["lon"] = estacion.map_lon
        estacionAuxiliar["tipo"] = 'RARE'
        # estacionAuxiliar["fondo"] = round(MediasDiarias.objects.using('rvra').filter(id_estacion=estacionAuxiliar["id"]).filter(id_canal=1).filter(fecha__lt=ayer).filter(fecha__gte=unAnio).aggregate(Avg('valor'))["valor__avg"], 2)
        # apaño para medias
        media = MediasDiarias.objects.using('rvra').filter(id_estacion=estacionAuxiliar["id"], id_canal=1, id_detector=0, fecha__gt=tiempoFondo).aggregate(
                Avg('valor'))["valor__avg"]
        if media is not None:
            estacionAuxiliar["fondo"] = round(media, 2)
        
        valores, fechas = [], []
        mediasEstacion = medias.filter(id_estacion=estacion.id)
        for media in mediasEstacion:
            valores.append(media.valor)
            fechas.append(str(media.fecha))
        if (len(valores) != 0):
            estacionAuxiliar["valores"] = valores
            estacionAuxiliar["fechas"] = fechas
            estacionAuxiliar["valor"] = valores[0]
            total = valores[0]
            if (str(ayer) == fechas[0]) and (valores[0] != None):
                estacionAuxiliar["actualizado"] = 1
            else:
                estacionAuxiliar["actualizado"] = 0
            estacionAuxiliar["fecha"] = str(fechas[0])

        infoEstacion = InformacionesEstaciones.objects.using("rvra").filter(id_estacion=estacion.id)[0]
        ayerInicio = datetime.today() - timedelta(days=1)
        ayerFin = datetime.today() - timedelta(days=1)
        ayerInicio = ayerInicio.replace(hour=0, minute=0, second=0)
        ayerFin = ayerFin.replace(hour=23, minute=59, second=59)
        numValoresDosis = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__gte=ayerInicio, fecha_hora__lte=ayerFin).filter(canales=1).filter(estaciones=estacion.id).count()
        valNecesarios = 24 * 60 * 60 / infoEstacion.tiempo_consulta
        operatividadDosis = int((numValoresDosis / valNecesarios) * 100)
        if operatividadDosis > 100:
            operatividadDosis = 100
        estacionAuxiliar["operatividad"] = operatividadDosis

        listaEstaciones.append(estacionAuxiliar)

    media, mediaAnual, actividad = 0.0, 0.0, 0.0
    fechas = []
    if len(listaEstaciones) > 0 and len(valores) != 0:
        maximo = {"valor": 0}
        for est in listaEstaciones:
            if est["valor"] != None:
                if maximo["valor"] < est["valor"]:
                    maximo = est

        media = (maximo["valor"] * 24 * 365)
        mediaAnual = (maximo["fondo"] * 24 * 365)
        actividad = round(media - mediaAnual, 3)
        if actividad <= 0:
            actividad = 0.0
        fechas = maximo["fechas"][::-1]

    user = request.user
    valores = {"listaEstaciones": listaEstaciones, "media": actividad, "fechas": fechas}
    jsonValores = simplejson.dumps(valores, default=myconverter)
    return JsonResponse(jsonValores, safe=False)


# CONSULTA INFORMACION ESTACION RAREX LIVE
@permission_required('auth.red_live')
def getStationData(request, cod_estacion):
    user = request.user

    ultimasHoras4 = datetime.now(timezone.utc) - timedelta(hours=3)
    ultimasHoras6 = datetime.now(timezone.utc) - timedelta(hours=6)

    estacionesTotales = InformacionesEstaciones.objects.using('rvra')
    infoEstacion = InformacionesEstaciones.objects.using('rvra').filter(id_estacion=cod_estacion)[0]

    valores_dosis = getGamaYodo(cod_estacion, ultimasHoras4)
    ultimo_valor = getUltimoRadioYodo(cod_estacion, ultimasHoras6)

    return render(request, "datos_estacion.html",
                  {"user": user, "estacion":infoEstacion, "estaciones":estacionesTotales, 
                  "valores_dosis": valores_dosis, "ultimo_valor": ultimo_valor})

# CONSULTA INFORMACION ESTACION RAREX LIVE
@permission_required('auth.acceso_rarex_externo')
def getStationDataService(request, cod_estacion):
    user = request.user

    if RelacionPermisoUsuarioEstacion.objects.using('rvra').filter(id_usuario=request.user.id, id_estacion=cod_estacion).exists():
        ultimasHoras4 = datetime.now(timezone.utc) - timedelta(hours=3)
        ultimasHoras6 = datetime.now(timezone.utc) - timedelta(hours=6)

        estacionesTotales = InformacionesEstaciones.objects.using('rvra').filter(id_estacion=cod_estacion)
        infoEstacion = InformacionesEstaciones.objects.using('rvra').filter(id_estacion=cod_estacion)[0]

        valores_dosis = getGamaYodo(cod_estacion, ultimasHoras4)
        ultimo_valor = getUltimoRadioYodo(cod_estacion, ultimasHoras6)

        return render(request, "datos_estacion.html",
                    {"user": user, "estacion":infoEstacion, "estaciones":estacionesTotales, 
                    "valores_dosis": valores_dosis, "ultimo_valor": ultimo_valor})
    else:
        return getMapaMedia(request)

def getUbicacionesInteres(request):
    ubicaciones = UbicacionesInteres.objects.using('rvra').values()
    return JsonResponse(list(ubicaciones), safe=False)

@permission_required('auth.red_live_carga')
def getStationDataSection(request, cod_estacion, seccion):
    if seccion == "conexiones":
        html = consultaSeccionConexiones(cod_estacion)
    elif seccion == "estado":
        html = consultaSeccionEstado(cod_estacion)
    elif seccion == "meteorologia":
        html = consultaSeccionMeteorologia(cod_estacion)
    elif seccion == "detectores":
        html = consultaSeccionDetectores(cod_estacion)
    elif seccion == "radon_yodo":
        html = consultaSeccionRadonYodo(cod_estacion)
    elif seccion == "yodo_cesio":
        html = consultaSeccionYodoCesio(cod_estacion)
    elif seccion == "infomapa":
        return JsonResponse(consultaSeccionInfoMapa(cod_estacion), safe=False)
    return HttpResponse(html)

def consultaSeccionInfoMapa(cod_estacion):
    infoEstacion = InformacionesEstaciones.objects.using('rvra').filter(id_estacion=cod_estacion)[0]
    cod_estacion = id_meteo_relacionado(cod_estacion)
    estMeteorologicas_precipitacion = EstMeteorologicas.objects.using("rvra").filter(estaciones=cod_estacion,
        canales=10).order_by('-fecha_hora')[0]
    estMeteorologicas_direccion_viento = EstMeteorologicas.objects.using("rvra").filter(estaciones=cod_estacion,
        canales=7).order_by('-fecha_hora')[0]
    estMeteorologicas_velocidad_viento = EstMeteorologicas.objects.using("rvra").filter(estaciones=cod_estacion,
        canales=6).order_by('-fecha_hora')[0]
    return {"precipitacion": estMeteorologicas_precipitacion.valor, "direccion_viento": estMeteorologicas_direccion_viento.valor, "velocidad_viento": estMeteorologicas_velocidad_viento.valor, "direccion_riesgo": infoEstacion.angulo_riesgo, "distancia_riesgo": infoEstacion.distancia}

def consultaSeccionConexiones(cod_estacion):   
    conexiones = getConexiones(cod_estacion)
    html = render_to_string('datos_estacion_conexion.html', {'conexiones': conexiones})
    return html

def consultaSeccionEstado(cod_estacion):   
    infoEstacion = InformacionesEstaciones.objects.using('rvra').filter(id_estacion=cod_estacion)[0]
    ultimasHoras6 = datetime.now(timezone.utc) - timedelta(hours=6)
    ayer = datetime.now(timezone.utc) - timedelta(hours=23)
    ultimo_valor = getUltimoRadioYodo(cod_estacion, ultimasHoras6)
    estado = consultaEstadoEstacion(cod_estacion, ayer)

    if "velVientoV" in estado:
        tiempo = int(round(((infoEstacion.distancia / estado["velVientoV"]) / 60), 0))
        html = render_to_string('datos_estacion_estado.html', {'ultimo_valor':ultimo_valor, 'estado': estado, 'tiempo': tiempo})
    else:
        html = render_to_string('datos_estacion_estado.html', {'ultimo_valor':ultimo_valor, 'estado': estado})
    return html

def consultaSeccionMeteorologia(cod_estacion):   
    cod_estacion = id_meteo_relacionado(cod_estacion)
    ultimasHoras11 = datetime.now(timezone.utc) - timedelta(hours=11)
    meteorologias_maximas = getMeteorologia(cod_estacion, ultimasHoras11)
    if len(meteorologias_maximas) != 0:
        for meteo in meteorologias_maximas:
            if meteo["maxima_presion"] > 2:
                icono_lluvia = "lluvia"
            elif meteo["maxima_presion"] > 0:
                icono_lluvia = "llovizna"
            else:
                icono_lluvia = "sol"
            meteo["icometeo"] = icono_lluvia
    html = render_to_string('datos_estacion_meteorologia.html', {'meteorologias_maximas':meteorologias_maximas})
    return html


def consultaSeccionDetectores(cod_estacion):   
    valores_detectores = getIsotopos(cod_estacion)
    html = render_to_string('datos_estacion_detectores.html', {'valores_detectores':valores_detectores})
    return html

def consultaSeccionRadonYodo(cod_estacion):   
    lista_radon_yodo = getRadioYodo(cod_estacion)
    html = render_to_string('datos_estacion_radon_yodo.html', {'estacion':cod_estacion, 'lista_radon_yodo':lista_radon_yodo})
    return html

def consultaSeccionYodoCesio(cod_estacion):   
    lista_yodo_cesio = getYodoCesio(cod_estacion)
    html = render_to_string('datos_estacion_yodo_cesio.html', {'estacion':cod_estacion, 'lista_yodo_cesio':lista_yodo_cesio})
    return html

# CONSULTA ESTADO PARAMETROS ESTACION RAREX LIVE
def consultaEstadoEstacion(id_estacion, fechaInicio):
    estado = {}
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=4,estacion_id=id_estacion,fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    infoEstacion = InformacionesEstaciones.objects.using('rvra').filter(id_estacion=id_estacion)[0]
    
    if len(valores_recibido) != 0:
        estado["caudalV"] = valores_recibido[0].valor
        estado["caudalU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=5, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["temperaturaV"] = valores_recibido[0].valor
        estado["temperaturaU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=6, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["velVientoV"] = valores_recibido[0].valor
        estado["velVientoU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=7, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["dirVientoV"] = int(valores_recibido[0].valor)
        estado["dirVientoU"] = valores_recibido[0].unidades
        estado["dirVientoRiesgo"] = infoEstacion.angulo_riesgo
        estado["dirVientoRiesgoMax"] = infoEstacion.angulo_riesgo_max
        estado["dirVientoRiesgoMin"] = infoEstacion.angulo_riesgo_min
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=8, estacion_id=id_estacion,fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["temperaturaFueraV"] = valores_recibido[0].valor
        estado["temperaturaFueraU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=9, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["humedadV"] = valores_recibido[0].valor
        estado["humedadU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=10, estacion_id=id_meteo_relacionado(id_estacion), fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["lluviaV"] = valores_recibido[0].valor
        estado["lluviaU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=11, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["bateriaV"] = valores_recibido[0].valor
        estado["bateriaU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=12, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["presionV"] = valores_recibido[0].valor
        estado["presionU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=13, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["radiacionSolarV"] = valores_recibido[0].valor
        estado["radiacionSolarU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=18, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["flowV"] = valores_recibido[0].valor
        estado["flowU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=19, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["temperaturaAguaV"] = valores_recibido[0].valor
        estado["temperaturaAguaU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=33, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["temperaturaGenitronV"] = valores_recibido[0].valor
        estado["temperaturaGenitronU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=34, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["tensionEntradaV"] = valores_recibido[0].valor
        estado["tensionEntradaU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=35, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["tensionSalidaV"] = valores_recibido[0].valor
        estado["tensionSalida"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=36, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["cargaSaiV"] = valores_recibido[0].valor
        estado["cargaSaiU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=37, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["temperaturaDetectorV"] = valores_recibido[0].valor
        estado["temperaturaDetectorU"] = valores_recibido[0].unidades
    valores_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=62, estacion_id=id_estacion, fecha_hora__gte=fechaInicio).order_by('-fecha_hora')
    if len(valores_recibido) != 0:
        estado["caudalCartuchoV"] = valores_recibido[0].valor
        estado["caudalCartuchoU"] = valores_recibido[0].unidades
    return estado

# CONSULTA CONEXIONES ESTACION RAREX LIVE
def getConexiones(id_estacion):
    conexiones = []
    conexEstacion = ControlConexiones.objects.using('rvra').filter(estacion=id_estacion)
    for con in conexEstacion:
        tipoCon = TipoConexion.objects.using('rvra').filter(id_conex=con.conexion)[0]
        conexiones.append({"conexion": tipoCon.tipo, "fecha": con.fecha_hora})
    return conexiones


# CONSULTA DE LOS VALORES DE TASA DE DOSIS PARA LA ESTACION DADA DESDE LA FECHA/HORA DADA. DEVUELVE LISTA DE JSON CON {fecha, valor, nivel_alerta, nivel_emergencia}
def getGamaYodo(id_estacion, fechaInicio):
    estGamYRadioyodos = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__gt=fechaInicio).filter(
        canales=1).filter(estaciones=id_estacion).order_by('fecha_hora')
    relacion = Relacion.objects.using('rvra').filter(estac=id_estacion).filter(canal=1)
    if len(relacion) != 0:
        amd = relacion[0].monitorizar
    lista_dosis = []
    for val in estGamYRadioyodos:
        lista_dosis.append(
            {"fecha": val.fecha_hora, "valor": round(val.valor,3), "alerta": round(amd + 0.114,3), "emergencia": round(amd + 0.228,3)})
    return lista_dosis
    # CONSULTA DE LOS VALORES DE TASA DE DOSIS PARA LA ESTACION DADA DESDE LA FECHA/HORA DADA. DEVUELVE LISTA DE JSON CON {fecha, valor, nivel_alerta, nivel_emergencia}
    
def getGamaYodoAPA(id_estacion, fechaInicio):
    estGamYRadioyodos = EstEspecGamma.objects.using('rvra').filter(fecha_hora__gt=fechaInicio).filter(
        relacion_detectores_estacion_id=1025,isotopos_id=14).order_by('fecha_hora')
    relacion = Relacion.objects.using('rvra').filter(estac=id_estacion).filter(canal=1)
    if len(relacion) != 0:
        amd = relacion[0].monitorizar
    lista_dosis = []
    for val in estGamYRadioyodos:
        lista_dosis.append(
            {"fecha": val.fecha_hora, "valor": round(val.actividad,3), "alerta": round(12*1.3,3), "emergencia": round(12*1.5,3)})
    return lista_dosis


# CONSULTA DEL ULTIMO VALOR DE RADIOYODO PARA LA ESTACION DADA. DEVUELVE VALOR JSON CON {valor, fecha, retraso} donde retraso es 1 si tiene más de 6 horas, 0 si no
def getUltimoRadioYodo(id_estacion, fechaInicio):
    valor_recibido = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=1).filter(estacion_id=id_estacion)
    if len(valor_recibido) != 0:
        if valor_recibido != "":
            if fechaInicio > valor_recibido[0].fecha_hora:
                return {"ultimoValor": valor_recibido[0].valor, "fecha": valor_recibido[0].fecha_hora, "retraso": 1}
            else:
                return {"ultimoValor": valor_recibido[0].valor, "fecha": valor_recibido[0].fecha_hora, "retraso": 0}
    else:
        return {"ultimoValor": None, "fecha": None, "retraso": None}


# CONSULTA DE LOS VALORES DE LOS ISOTOPOS PARA LA ESTACION DADA. DEVUELVE LISTA DE JSON CON {fecha, valor, nivel_alerta, nivel_emergencia}
def getIsotopos(id_estacion):
    valores_detectores = []

    datosEstacion = ConfigEstacionWebrarex.objects.using('rvra').filter(id_estacion=id_estacion)

    detectores = datosEstacion.values('id_detector','tipo_detector').distinct()
    for detector in detectores:
        isotoposDetector = datosEstacion.filter(tipo_detector=detector["tipo_detector"]).values_list('isotopo', flat=True)
        lista_detectores_isotopos = []
        ultimo_valor_isotopo = UltimosValoresRecibidos.objects.using('rvra').filter(can_det_est=detector["id_detector"]).filter(isotopo_id__in=isotoposDetector).filter(estacion_id=id_estacion)
        for valor in ultimo_valor_isotopo:
            configChart = datosEstacion.filter(isotopo=valor.isotopo_id, id_detector=detector["id_detector"])[0]

            isotopo = Isotopos.objects.using('rvra').filter(id=valor.isotopo_id)[0]
            nombre = convertir_subindice(isotopo.n_iso)
            diff = valor.fecha_hora-datetime.now(timezone.utc)
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            lista_detectores_isotopos.append(
                {"id": valor.isotopo_id, "id_detector": detector["id_detector"], "abreviado": nombre, "nombre": isotopo.n_iso, "artificial": isotopo.artificial, 
                 "valor": valor.valor, "amd": valor.amd, "fecha": valor.fecha_hora, "unidad": configChart.unidades, "retraso": abs(hours)})
        valores_detectores.append({"nombre_detector": detector["tipo_detector"], "lista_valores": lista_detectores_isotopos})

    return valores_detectores


# CONSULTA RADIOYODOS ESTACION RAREX LIVE
def getRadioYodo(id_estacion):
    lista_radon_yodo = []
    relaciones = Relacion.objects.using('rvra').filter(estac=id_estacion).filter(canal__in=[14, 15, 16, 17])
    for relacion in relaciones:
        nombre = Canales.objects.using('rvra').filter(id=relacion.canal)[0].nombre
        ultimo_valor_radon_yodo = UltimosValoresRecibidos.objects.using('rvra').filter(
            can_det_est=relacion.canal).filter(estacion_id=id_estacion)
        if len(ultimo_valor_radon_yodo) != 0:
            diff = ultimo_valor_radon_yodo[0].fecha_hora-datetime.now(timezone.utc)
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            lista_radon_yodo.append(
                {"id_canal": relacion.canal, "nombre": nombre, "valor": ultimo_valor_radon_yodo[0].valor,
                 "amd": ultimo_valor_radon_yodo[0].amd, "fecha": ultimo_valor_radon_yodo[0].fecha_hora, "retraso": abs(hours)})
    return lista_radon_yodo

# CONSULTA YODOS Y CESIOS ESTACION RAREX LIVE
def getYodoCesio(id_estacion):
    lista_yodo_cesio = []
    relaciones = Relacion.objects.using("rvra").filter(estac=id_estacion).filter(canal__in=[2, 3])
    for relacion in relaciones:
        nombre = Canales.objects.using("rvra").filter(id=relacion.canal)[0].nombre
        ultimo_valor_yodo_cesio = UltimosValoresRecibidos.objects.using("rvra").filter(can_det_est=relacion.canal).filter(
            estacion_id=id_estacion)[0]
        diff = ultimo_valor_yodo_cesio.fecha_hora-datetime.now(timezone.utc)
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        lista_yodo_cesio.append({"id_canal": relacion.canal, "nombre": nombre, "valor": ultimo_valor_yodo_cesio.valor,
                                "amd": ultimo_valor_yodo_cesio.amd, "fecha": ultimo_valor_yodo_cesio.fecha_hora, "retraso": abs(hours)})
    return lista_yodo_cesio


# CONSULTA METEOROLOGIA ESTACION RAREX LIVE
def getMeteorologia(id_estacion, fechaInicio):
    estMeteorologicas_temperatura = EstMeteorologicas.objects.using("rvra").filter(estaciones=id_estacion).filter(
        canales=8).filter(fecha_hora__gt=fechaInicio)
    estMeteorologicas_precipitacion = EstMeteorologicas.objects.using("rvra").filter(estaciones=id_estacion).filter(
        canales=10).filter(fecha_hora__gt=fechaInicio)
    estMeteorologicas_direccion_viento = EstMeteorologicas.objects.using("rvra").filter(estaciones=id_estacion).filter(
        canales=7).filter(fecha_hora__gt=fechaInicio)
    estMeteorologicas_velocidad_viento = EstMeteorologicas.objects.using("rvra").filter(estaciones=id_estacion).filter(
        canales=6).filter(fecha_hora__gt=fechaInicio)

    meteorologia_maximas = []
    maximo_tem = -10000
    maximo_pre = -10000
    direccion_viento = -1
    if len(estMeteorologicas_precipitacion) != 0:
        fecha = (estMeteorologicas_precipitacion[0].fecha_hora + timedelta(hours=1)).strftime("%Y-%m-%d %H")
        for i in range(len(list(estMeteorologicas_precipitacion))):
            est = estMeteorologicas_precipitacion[i]
            fecha_est = (est.fecha_hora + timedelta(hours=1)).strftime("%Y-%m-%d %H")
            if (fecha != fecha_est):
                maximo_tem = estMeteorologicas_temperatura[i].valor
                direccion_viento = estMeteorologicas_direccion_viento[i].valor
                velocidad_viento = estMeteorologicas_velocidad_viento[i].valor
                meteorologia_maximas.append(
                    {"hora": fecha.split(" ")[1], "maxima_temperatura": maximo_tem, "maxima_presion": maximo_pre,
                     "direccion_viento": direccion_viento, "velocidad_viento": velocidad_viento})
                fecha = fecha_est
                maximo_pre = -10000
            if (est.valor > maximo_pre):
                maximo_pre = est.valor
        return meteorologia_maximas[-12:]
    else:
        return meteorologia_maximas[-12:]


# CONSULTA PRECIPITACIONES ESTACION RAREX LIVE
def getPrecipitaciones(cod_estacion):
    ultimo_valor_precipitacion = UltimosValoresRecibidos.objects.using("rvra").filter(can_det_est=10).filter(
        estacion_id=cod_estacion)
    if len(ultimo_valor_precipitacion) != 0:
        return {"precipitacion": ultimo_valor_precipitacion[0].valor}
    else:
        return "None"

# ESTACIONES METEO CERCANAS PARA LAS ESTACIONES QUE NO DISPONEN ##### CAMBIAR A BR #####
def id_meteo_relacionado(cod_estacion):
    if (int(cod_estacion) == 1):
        return 40
    elif (int(cod_estacion) == 3):
        return 40
    elif (int(cod_estacion) == 7):
        return 40
    elif (int(cod_estacion) == 8):
        return 40
    elif (int(cod_estacion) == 11):
        return 40
    else:
        return cod_estacion

# CONVERTIR VALORES A SUBINDICE PARA NOMBRE DE ISOTOPOS
def convertir_subindice(texto):
    try:
        nombre_isotopo = ""
        elemento = texto.split("-")[0]
        numero = texto.split("-")[1]
        for l in range(len(numero)):
            if (int(numero[l]) == 0):
                nombre_isotopo += "&#8304;"
            if (int(numero[l]) <= 3 and int(numero[l]) > 0):
                nombre_isotopo += '&sup' + str(numero[l]) + ';'
            if (int(numero[l]) > 3 and int(numero[l]) <= 5):
                nombre_isotopo += "&#830" + str(int(numero[l]) + 4) + ";"
            if (int(numero[l]) > 5):
                nombre_isotopo += "&#83" + str(int(numero[l]) + 4) + ";"
        primero = True
        elemento_final = elemento[0]
        for l in range(len(elemento)):
            if primero == False:
                elemento_final += elemento[l].lower()
            primero = False
        return nombre_isotopo + elemento_final
    except:
        return texto


# CONSULTA ISOTOPO ESTACION RAREX LIVE
@permission_required('auth.red_live')
def getIsotopoEstacion(request, id_detector, id_isotopo):
    configChart = ConfigEstacionWebrarex.objects.using('rvra').filter(isotopo=id_isotopo, id_detector=id_detector)[0]
    isotopo = Isotopos.objects.using('rvra').filter(id=id_isotopo)[0]
    ayer = datetime.now(timezone.utc) - timedelta(hours=5)
    estEspecGamma = EstEspecGamma.objects.using("rvra").filter(fecha_hora__gt=ayer).filter(
        relacion_detectores_estacion_id=id_detector).filter(isotopos_id=id_isotopo).order_by('fecha_hora')
    values = []
    for valor in estEspecGamma:
        values.append({"valor": valor.actividad, "amd": valor.amd, "fecha": valor.fecha_hora})
    datos = {"Medida":isotopo.n_iso, "Unidades": configChart.unidades, "Values":values}

    return JsonResponse(datos, safe=False)


# CONSULTA CANAL ESTACION RAREX LIVE
@permission_required('auth.red_live')
def getCanalEstacion(request, id_estacion, id_canal):
    configChart = Canales.objects.using('rvra').filter(id=id_canal)[0]
    ayer = datetime.now(timezone.utc) - timedelta(hours=5)
    estGamYRadioyodos = EstGamYRadioyodos.objects.using("rvra").filter(fecha_hora__gt=ayer).filter(
        estaciones=id_estacion).filter(canales=id_canal).order_by('fecha_hora')
    values = []
    for valor in estGamYRadioyodos:
        values.append({"valor": valor.valor, "fecha": valor.fecha_hora})

    datos = {"Medida":configChart.nombre, "Unidades": configChart.unidades, "Values":values}

    return JsonResponse(datos, safe=False)

######################### GUARDIAS #########################

# CONSULTA GRAFICAS GUARDIA RAREX
@permission_required('auth.guardia_rarex')
def getGuardiaRare(request):
    botones = consultarBotonesGraficas('rvra')
    simulacro = SimulacrosRarex.objects.using('rvra').filter(estado=1).exists()
    return render(
        request,
        "guardia_rare.html",
        {"desbloqueo":0, "red":"rvra", "listaBotones": botones, "simulacro": simulacro}
    )

# CONSULTA GRAFICAS GUARDIA CSM
@permission_required('auth.guardia_rarex')
def getGuardiaCSN(request):
    botones = consultarBotonesGraficas('csn')
    return render(
        request,
        "guardia_rare.html",
        {"desbloqueo":0, "red":"csn", "listaBotones": botones}
    )

# CONSULTA GRAFICAS GUARDIA SPIDA
@permission_required('auth.guardia_spida')
def getGuardiaSpida(request):
    botones = consultarBotonesGraficas('spida')
    calculoMediasDiarias()
    return render(
        request,
        "guardia_rare.html",
        {"desbloqueo":0, "red": "spida", "listaBotones": botones}
    )

def calculoMediasDiarias():
    dias = datetime.now(timezone.utc)
    dias = dias.replace(hour=0, minute=0, second=0)
    dias = dias - timedelta(days=15)
    estaciones = EstGamYRadioyodos.objects.using('rvra').filter(canales=1, valido=1, fecha_hora__gte=dias, estaciones__lte=60).values('estaciones').annotate(dcount=Count('estaciones'))
    for est in estaciones:
        mediasCalculadas, estacion, existe = [], None, None
        valores = EstGamYRadioyodos.objects.using('rvra').filter(estaciones=est["estaciones"], canales=1, valido=1, fecha_hora__gte=dias)
        f_ini, valor = None, []
        for v in valores:
            if f_ini is None:
                f_ini = v.fecha_hora.date()
            if f_ini == v.fecha_hora.date():
                valor.append(v.valor)
            else:
                mediasCalculadas.append({"Fecha": f_ini, "Media": round(sum(valor)/len(valor),4)})
                f_ini = v.fecha_hora.date()
                valor = []
                valor.append(v.valor)
        insertarMedias(est["estaciones"], 1, mediasCalculadas)

def insertarMedias(estacion, canal, medias):
        for media in medias:
            existe = MediasDiarias.objects.using('rvra').filter(fecha=media["Fecha"], id_estacion=Estaciones(id=estacion), id_detector=0, id_canal=Canales(id=canal))
            if len(existe) == 0:
                m = MediasDiarias(fecha=media["Fecha"], id_estacion=Estaciones(id=estacion), id_detector=0, id_canal=Canales(id=canal), valor=media["Media"])
                m.save(using='rvra')

# CONSULTA GRAFICAS CONSULTA RAREX
@permission_required('auth.consulta_rarex')
def getConsultaRare(request):
    simulacro = SimulacrosRarex.objects.using('rvra').filter(estado=1).exists()
    botones = consultarBotonesGraficas('rvra')
    return render(
        request,
        "guardia_rare.html",
        {"desbloqueo":1, "red":"rvra", "listaBotones": botones, "simulacro": simulacro}
    )

# CONSULTA GRAFICAS CONSULTA CSN
@permission_required('auth.consulta_csn')
def getConsultaCSN(request):
    botones = consultarBotonesGraficas('csn')
    return render(
        request,
        "guardia_rare.html",
        {"desbloqueo":1, "red":"csn", "listaBotones": botones}
    )

# CONSULTA GRAFICAS CONSULTA SPIDA
@permission_required('auth.consulta_spida')
def getConsultaSpida(request):
    botones = consultarBotonesGraficas('spida')
    return render(
        request,
        "guardia_rare.html",
        {"desbloqueo":1, "red": "spida", "listaBotones": botones}
    )

# CONSULTA BOTONES GRAFICAS
def consultarBotonesGraficas(bd):
    botones = []
    listaBotones = ConfigGraficasRare.objects.using('rvra').filter(red=bd).values('id_boton', 'nombre_boton').order_by(
        'id_boton').distinct()
    for l in listaBotones:
        subbotones = ConfigGraficasRare.objects.using('rvra').filter(id_boton=l["id_boton"]).values('id_subseccion', 'nombre_subseccion').distinct()
        botones.append({"id_boton": l["id_boton"], "nombre_boton": l["nombre_boton"], "subbotones": subbotones})
    return botones

# CONSULTA GRUPO DE GRAFICAS
@permission_required('auth.graficas')
def getGuardiaGroup(request, id_grupo, id_subgrupo):
    values = consultarGraficas(id_grupo, id_subgrupo)
    return JsonResponse(values, safe=False)

# CONSULTA SUBGRUPO DE GRAFICAS
def consultarGraficas(id_grupo, id_subgrupo):
    values = []
    configInicial = ConfigGraficasRare.objects.using('rvra').filter(id_boton=id_grupo).filter(id_subseccion=id_subgrupo).values(
        'nombre_subseccion','red')[0]
    nombreSubseccion = configInicial["nombre_subseccion"]
    bd = configInicial["red"]
    configSiguiente = ConfigGraficasRare.objects.using('rvra').filter(id_boton=id_grupo).filter(
        id_subseccion=int(id_subgrupo) + 1)
    siguiente = {}
    if len(configSiguiente) > 0:
        siguiente = {"tituloSubSeccion": nombreSubseccion, "siguienteGrupo": id_grupo,
                     "siguienteSubgrupo": int(id_subgrupo) + 1}
    else:
        configSiguiente2 = ConfigGraficasRare.objects.using('rvra').filter(id_boton=int(id_grupo) + 1)
        if len(configSiguiente2) > 0:
            siguiente = {"tituloSubSeccion": nombreSubseccion, "siguienteGrupo": int(id_grupo) + 1,
                         "siguienteSubgrupo": 0}
        else:
            siguiente = {"tituloSubSeccion": nombreSubseccion, "siguienteGrupo": 0, "siguienteSubgrupo": 0}

    values.append(siguiente)

    configs = ConfigGraficasRare.objects.using('rvra').filter(id_boton=id_grupo).filter(id_subseccion=id_subgrupo)
    siguiente["tamanio"] = configs[0].tamanio

    if configs[0].id_estacion in [997, 998, 999]:
        series = []
        fechas = []
        fechasTemp = []
        estaciones_media = []
        ejes = []
        if configs[0].id_estacion == 997:
            estaciones_media = [1, 3, 7, 8, 10, 11, 12, 13, 40]
        elif configs[0].id_estacion == 998:
            estaciones_media = [2, 4, 53, 56, 57]
        elif configs[0].id_estacion == 999:
            estaciones_media = [5, 54, 55]
        dias = datetime.now(timezone.utc) - timedelta(days=configs[0].dias)
        estaciones = Estaciones.objects.using(bd).filter(id__in=estaciones_media)
        for est in estaciones:
            serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=configs[0].series)[0]
            if serieConf.tabla == "Medias":
                fechasTemp, serie = consultasMedias(bd, est.id, serieConf.canal, dias, serieConf, est.nombre)
            if not (fechasTemp is None):
                fechas = fechasTemp
            series.append(serie)
            if serieConf.ejemain == 1:
                if serieConf.eje == "izquierda":
                    eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                           "title": {"text": serieConf.textoeje}}
                    nombreSerie = serieConf.nombre
                else:
                    eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                           "title": {"text": serieConf.textoeje}}
                    nombreSerie = serieConf.nombre
            ejes.append(eje)
        values.append({"id_chart": configs[0].id, "fechas": fechas, "series": series, "ejes": eje})
    else:
        for configGrafica in configs:
            series = []
            fechas = []
            ejes = []
            dias = datetime.now(timezone.utc) - timedelta(days=configGrafica.dias)
            est = Estaciones.objects.using(bd).filter(id=configGrafica.id_estacion)[0]
            estacion = {"id": est.id, "nombre": est.nombre}

            seriesConfigs = None
            datosMonitorizados = None
            seriesMonitorizadas = []
            if configGrafica.series.find(",") >= 0:
                seriesConfigs = configGrafica.series.split(",")
                nombreSerie = ""
                for idSerieConf in seriesConfigs:
                    eje = {}
                    serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=idSerieConf)[0]

                    fechasTemp, serie, diferencia = obtenerInfoChart(bd, serieConf, est, dias, configGrafica)
                    if not (fechasTemp is None):
                        fechas = fechasTemp

                    if datosMonitorizados is None:
                        if serieConf.tabla == 'Espec':
                            # datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=configGrafica.detector, isotopo_id=serieConf.canal, n1_activo=1)
                            datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=configGrafica.detector, isotopo__id=serieConf.canal)
                            
                        elif serieConf.tabla == 'EspecAcum':
                            datosMonitorizados = []
                        else:
                            # datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=serieConf.canal, n1_activo=1)
                            datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=serieConf.canal)
                        if len(datosMonitorizados) > 0:
                            seriesMonitorizadas = seriesMonitoriza(datosMonitorizados[0], fechas)

                    series.append(serie)

                    if serieConf.ejemain == 1:
                        if serieConf.eje == "izquierda":
                            eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                                   "title": {"text": serieConf.textoeje}}
                            nombreSerie = serieConf.nombre
                        else:
                            eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                                   "title": {"text": serieConf.textoeje}}
                            nombreSerie = serieConf.nombre
                    else:
                        if serieConf.eje == "izquierda":
                            eje = {"seriesName": nombreSerie, "opposite": False, "show": False}
                        else:
                            eje = {"seriesName": nombreSerie, "opposite": True, "show": False}
                    ejes.append(eje)

                    if len(seriesMonitorizadas) > 0:
                        ejeAux = {"seriesName": serieConf.nombre, "opposite": False, "show": False,
                                  "title": {"text": serieConf.textoeje}}
                        for s in seriesMonitorizadas:
                            series.append(s)
                            ejes.append(ejeAux)
                        seriesMonitorizadas = []
            else:
                eje = {}
                serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=configGrafica.series)[0]

                fechasTemp, serie, diferencia = obtenerInfoChart(bd, serieConf, est, dias, configGrafica)
                if not (fechasTemp is None):
                    fechas = fechasTemp

                if datosMonitorizados is None:
                    if serieConf.tabla == 'Espec':
                        # datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=configGrafica.detector, isotopo_id__id=serieConf.canal, n1_activo=1)
                        datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=configGrafica.detector, isotopo__id=serieConf.canal)
                    elif serieConf.tabla == 'EspecAcum':
                        datosMonitorizados = []
                    else:
                        # datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=serieConf.canal, n1_activo=1)
                        datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=serieConf.canal)

                    if len(datosMonitorizados) > 0:
                        seriesMonitorizadas = seriesMonitoriza(datosMonitorizados[0], fechas)

                if serieConf.eje == "izquierda":
                    eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                           "title": {"text": serieConf.textoeje}}
                else:
                    eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                           "title": {"text": serieConf.textoeje}}
                series.append(serie)
                ejes.append(eje)

                if len(seriesMonitorizadas) > 0:
                    ejeAux = {"seriesName": serieConf.nombre, "opposite": False, "show": False, "title": {"text": serieConf.textoeje}}
                    for s in seriesMonitorizadas:
                        series.append(s)
                        ejes.append(ejeAux)
                    seriesMonitorizadas = []

            tiempo, tramoSinDatos, fondoDiv, nivel, alerta = comprobacionesAvisos(serieConf, fechas, diferencia)
            
            values.append({"id_chart": configGrafica.id, "tamanio": configGrafica.tamanio, "fondoDiv": fondoDiv, "tiempo": tiempo, "nivel": nivel, "tramoSinDatos": tramoSinDatos, "alerta":alerta, "estacion": estacion, "diferencia": diferencia, "fechas": fechas, "series": series, "ejes": ejes})
    return values


@permission_required('auth.graficas')
def getChartReload(request, id_chart):
    idChart = id_chart.replace('chartid_', '')
    config = ConfigGraficasRare.objects.using('rvra').filter(id=idChart)[0]
    bd = config.red
    series = []
    fechas = []
    ejes = []
    dias = datetime.now(timezone.utc) - timedelta(days=config.dias)
    est = Estaciones.objects.using(bd).filter(id=config.id_estacion)[0]
    estacion = {"id": est.id, "nombre": est.nombre}

    seriesConfigs = None
    datosMonitorizados = None
    seriesMonitorizadas = []
    if config.series.find(",") >= 0:
        seriesConfigs = config.series.split(",")
        nombreSerie = ""
        for idSerieConf in seriesConfigs:
            eje = {}
            serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=idSerieConf)[0]

            fechasTemp, serie, diferencia = obtenerInfoChart(bd, serieConf, est, dias, config)
            if not (fechasTemp is None):
                fechas = fechasTemp

            if datosMonitorizados is None:
                if serieConf.tabla == 'Espec':
                    # datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=config.detector, isotopo_id=serieConf.canal,  n1_activo=1)
                    datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=config.detector, isotopo__id=serieConf.canal)
                elif serieConf.tabla == 'EspecAcum':
                    datosMonitorizados = []
                else:
                    # datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=serieConf.canal, n1_activo=1)
                    datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=serieConf.canal)
                if len(datosMonitorizados) > 0:
                    seriesMonitorizadas = seriesMonitoriza(datosMonitorizados[0], fechas)

            series.append(serie)

            if serieConf.ejemain == 1:
                if serieConf.eje == "izquierda":
                    eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                           "title": {"text": serieConf.textoeje}}
                    nombreSerie = serieConf.nombre
                else:
                    eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                           "title": {"text": serieConf.textoeje}}
                    nombreSerie = serieConf.nombre
            else:
                if serieConf.eje == "izquierda":
                    eje = {"seriesName": nombreSerie, "opposite": False, "show": False}
                else:
                    eje = {"seriesName": nombreSerie, "opposite": True, "show": False}
            ejes.append(eje)

            if len(seriesMonitorizadas) > 0:
                ejeAux = {"seriesName": serieConf.nombre, "opposite": False, "show": False,
                          "title": {"text": serieConf.textoeje}}
                for s in seriesMonitorizadas:
                    series.append(s)
                    ejes.append(ejeAux)
                seriesMonitorizadas = []
    else:
        eje = {}
        serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=config.series)[0]

        fechasTemp, serie, diferencia = obtenerInfoChart(bd, serieConf, est, dias, config)
        if not (fechasTemp is None):
            fechas = fechasTemp

        if datosMonitorizados is None:
            if serieConf.tabla == 'Espec':
                #datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=config.detector,  isotopo_id=serieConf.canal, n1_activo=1)
                datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=config.detector, isotopo__id=serieConf.canal)
            elif serieConf.tabla == 'EspecAcum':
                datosMonitorizados = []
            else:
                #datosMonitorizados = DatosMonitorizables.objects.using('rvra').filter(estacion_id=est.id, can_det_est=serieConf.canal, n1_activo=1)
                datosMonitorizados = ConfigMonitoriza.objects.using('rvra').filter(estacion__id=est.id, can_det_est=serieConf.canal)
            if len(datosMonitorizados) > 0:
                seriesMonitorizadas = seriesMonitoriza(datosMonitorizados[0], fechas)

        if serieConf.eje == "izquierda":
            eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                   "title": {"text": serieConf.textoeje}}
        else:
            eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                   "title": {"text": serieConf.textoeje}}
        series.append(serie)
        ejes.append(eje)

        if len(seriesMonitorizadas) > 0:
            ejeAux = {"seriesName": serieConf.nombre, "opposite": False, "show": False,
                      "title": {"text": serieConf.textoeje}}
            for s in seriesMonitorizadas:
                series.append(s)
                ejes.append(ejeAux)
            seriesMonitorizadas = []

    tiempo, tramoSinDatos, fondoDiv, nivel, alerta = comprobacionesAvisos(serieConf, fechas, diferencia)

    values = {"id_chart": id_chart, "tamanio": config.tamanio, "fondoDiv": fondoDiv, "tiempo": tiempo,
         "nivel": nivel, "tramoSinDatos": tramoSinDatos, "alerta": alerta, "estacion": estacion,
         "diferencia": diferencia, "fechas": fechas, "series": series, "ejes": ejes}
    return JsonResponse(values, safe=False)


# METODO PARA RECARGA DE UNA GRAFICA
@permission_required('auth.graficas')
def getChartReload2(request, id_chart):
    idChart = id_chart.replace('chartid_','')
    config = ConfigGraficasRare.objects.using('rvra').filter(id=idChart)[0]
    bd = config.red
    series = []
    fechas = []
    ejes = []
    dias = datetime.now(timezone.utc) - timedelta(days=config.dias)
    est = Estaciones.objects.using(bd).filter(id=config.id_estacion)[0]
    estacion = {"id": est.id, "nombre": est.nombre}

    seriesConfigs = None

    if config.series.find(",") >= 0:
        seriesConfigs = config.series.split(",")
        nombreSerie = ""
        for idSerieConf in seriesConfigs:
            eje = {}
            serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=idSerieConf)[0]
            fechasTemp, serie, diferencia = obtenerInfoChart(bd, serieConf, est, dias, config)
            if not (fechasTemp is None):
                fechas = fechasTemp
            series.append(serie)
            if serieConf.ejemain == 1:
                if serieConf.eje == "izquierda":
                    eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                           "title": {"text": serieConf.textoeje}}
                    nombreSerie = serieConf.nombre
                else:
                    eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                           "title": {"text": serieConf.textoeje}}
                    nombreSerie = serieConf.nombre
            else:
                if serieConf.eje == "izquierda":
                    eje = {"seriesName": nombreSerie, "opposite": False, "show": False}
                else:
                    eje = {"seriesName": nombreSerie, "opposite": True, "show": False}
            ejes.append(eje)
    else:
        eje = {}
        serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=config.series)[0]
        fechasTemp, serie, diferencia = obtenerInfoChart(bd, serieConf, est, dias, config)
        if not (fechasTemp is None):
            fechas = fechasTemp
        if serieConf.eje == "izquierda":
            eje = {"seriesName": serieConf.nombre, "opposite": False, "show": True,
                   "title": {"text": serieConf.textoeje}}
        else:
            eje = {"seriesName": serieConf.nombre, "opposite": True, "show": True,
                   "title": {"text": serieConf.textoeje}}
        series.append(serie)
        ejes.append(eje)
    tiempo, tramoSinDatos, fondoDiv, nivel, alerta = comprobacionesAvisos(serieConf, fechas, diferencia)

    values = {"id":id_chart, "diferencia": diferencia, "fondoDiv": fondoDiv, "tiempo": tiempo, "nivel": nivel, "tramoSinDatos": tramoSinDatos, "alerta":alerta, "fechas": fechas, "series": series, "ejes": ejes}
    return JsonResponse(values, safe=False)

# METODO DE COMPROBACION DE AVISOS DE ALERTA
def comprobacionesAvisos(serieConf, fechas, diferenciaDatos):
    primerAviso = datetime.now(tz.timezone("Europe/Madrid")) - timedelta(hours=serieConf.horasAviso)
    segundoAviso = datetime.now(tz.timezone("Europe/Madrid")) - timedelta(hours=serieConf.horasAlerta)
    tiempo, fondoDiv, nivel, alerta, tramoSinDatos = "success", "blanco", "", "", "success"

    if len(fechas) > 0:
        if fechas[len(fechas)-2] < primerAviso and fechas[len(fechas)-2] > segundoAviso:
            tiempo = "warning"
            fondoDiv = "amarillo"
            alerta += "Datos retrasados en más de " + str(serieConf.horasAviso) + " horas\n"
        elif fechas[len(fechas)-2] < segundoAviso:
            tiempo = "danger"
            fondoDiv = "rojo"
            alerta += "Datos retrasados en más de " + str(serieConf.horasAlerta) + " horas\n"

    if diferenciaDatos is not None:
        if diferenciaDatos > serieConf.horasIncidencia:
            fondoDiv = "rojo"
            tramoSinDatos = "danger"
            alerta += "Ausencia de datos en " + str(diferenciaDatos) + " horas, incidencia necesaría al superar " + str(serieConf.horasIncidencia) + " horas\n"
        elif diferenciaDatos > (serieConf.horasIncidencia/2):
            tramoSinDatos = "warning"
            alerta += "Ausencia de datos en " + str(diferenciaDatos) + " horas\n"

    return tiempo, tramoSinDatos, fondoDiv, nivel, alerta

# METODO QUE OBTIENE LAS SERIES DE MONITORIZACION
def seriesMonitoriza(datosMonitorizados, fechas):
    series = []
    if datosMonitorizados.can_det_est == 1 and datosMonitorizados.isotopo.id == 0:
        series = calcularNivelesDosis(datosMonitorizados.med_anio_ant, datosMonitorizados.factor_n1, datosMonitorizados.factor_n2, datosMonitorizados.factor_n3, fechas)
    elif datosMonitorizados.isotopo.id == 0:
        series = calcularNivelesParametro(datosMonitorizados.factor_n1, datosMonitorizados.factor_n2, datosMonitorizados.factor_n3, fechas)
    else:
        series = calcularNivelesEspectrometria(datosMonitorizados.med_amd_anio_ant, datosMonitorizados.factor_n1, datosMonitorizados.factor_n2, datosMonitorizados.factor_n3, fechas)
    return series

# METODO QUE CALCULA LOS NIVELES DE ALERTA DE DOSIS
def calcularNivelesParametro(factor_n1, factor_n2, factor_n3, fechas):
    series, medidasN1, medidasN2, medidasN3 = [], [], [], []
    for fecha in fechas:
        if factor_n1 != 1:
            medidasN1.append(factor_n1)
        if factor_n2 != 1:
            medidasN2.append(factor_n2)
        if factor_n3 != 1:
            medidasN3.append(factor_n3)
    if len(medidasN1) > 0:
        series.append({"name": "Cota 1", "data": medidasN1, "type": "line", "color": "#FF0000"})
    if len(medidasN2) > 0:
        series.append({"name": "Cota 2", "data": medidasN2, "type": "line", "color": "#FF0000"})
    if len(medidasN3) > 0:
        series.append({"name": "Cota 3", "data": medidasN3, "type": "line", "color": "#FF0000"})
    return series


# METODO QUE CALCULA LOS NIVELES DE ALERTA DE DOSIS
def calcularNivelesDosis(media, factor_n1, factor_n2, factor_n3, fechas):
    series, medidasN1, medidasN2, medidasN3 = [], [], [], []
    for fecha in fechas:
        medidasN1.append(round(media*factor_n1, 3))
        medidasN2.append(round(media + factor_n2, 3))
        medidasN3.append(round(media + factor_n3, 3))
    series.append({"name": "Nivel 1", "data": medidasN1, "type": "line", "color": "#FFCC00"})
    series.append({"name": "Nivel 2", "data": medidasN2, "type": "line", "color": "#FF7000"})
    series.append({"name": "Nivel 3", "data": medidasN3, "type": "line", "color": "#FF0000"})
    return series


# METODO QUE CALCULA LOS NIVELES DE ALERTA DE ESPECTROMETRIA
def calcularNivelesEspectrometria(media, factor_n1, factor_n2, factor_n3, fechas):
    series, medidasN1, medidasN2, medidasN3 = [], [], [], []
    for fecha in fechas:
        medidasN1.append(round(media*factor_n1, 3))
        medidasN2.append(round(media*factor_n2, 3))
        medidasN3.append(round(media*factor_n3, 3))

    series.append({"name": "Nivel 1", "data": medidasN1, "type": "line", "color": "#FFCC00"})
    series.append({"name": "Nivel 2", "data": medidasN2, "type": "line", "color": "#FF7000"})
    series.append({"name": "Nivel 3", "data": medidasN3, "type": "line", "color": "#FF0000"})
    return series

# METODO QUE OBTIENE LA SERIE TEMPORAL Y LOS DATOS DE UNA GRAFICA
def obtenerInfoChart(bd, serieConf, est, dias, configGrafica):
    fechasTemp, serie, diferencia = None, None, None
    if serieConf.tabla == "Gamma":
        fechasTemp, serie, diferencia = consultasGamYRadioyodos(bd, est.id, serieConf.canal, dias, serieConf)
    elif serieConf.tabla == "Espec":
        fechasTemp, serie, diferencia = consultasEspecGamma(bd, configGrafica.detector, serieConf.canal, dias,
                                                serieConf)
    elif serieConf.tabla == "EspecAcum":
        fechasTemp, serie = consultasEspecAcumGamma(bd, configGrafica.detector, serieConf.canal, dias,
                                                    serieConf)
    elif serieConf.tabla == "Param":
        fechasTemp, serie, diferencia = consultasParamControl(bd, est.id, serieConf.canal, dias, serieConf)
    elif serieConf.tabla == "Meteo":
        fechasTemp, serie, diferencia = consultasEstMeteoControl(bd, est.id, serieConf.canal, dias, serieConf)
    return fechasTemp, serie, diferencia

# CONSULTA DE LA TABLA ESPECGAMMA
def consultasEspecGamma(bd, id, canal, dias, serieConf):
    serie = {}
    fechas = None
    diferencia = None

    if serieConf.tipodato == "valor":
        fechas, serie, diferencia = consultaValorGraficaEspecGamma(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                       serieConf.color, serieConf.redondeo)
    elif serieConf.tipodato == "amd":
        serie = consultaAMDGraficaEspecGamma(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica, serieConf.color, serieConf.redondeo)
    elif "media" in serieConf.tipodato:
        fechas, serie, diferencia = consultaMediaEspecGamma(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                  serieConf.color,int(serieConf.tipodato.split("_")[1]), serieConf.redondeo)
    return fechas, serie, diferencia

# CONSULTA DEL PARAMETRO VALOR DE LA TABLA ESPECGAMMA
def consultaValorGraficaEspecGamma(bd, detector, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None
    difMaxima = 0.0

    estEspecGamma = EstEspecGamma.objects.using(bd).filter(relacion_detectores_estacion_id=detector).filter(
        isotopos_id=canal).filter(fecha_hora__gt=dias)
    for v in estEspecGamma:
        if diferencia == None:
            fechaPrevia = v.fecha_hora
        diferencia = v.fecha_hora - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
        if horas > difMaxima:
            difMaxima = horas
        if horas > 1.0:
            fechaAux = v.fecha_hora + timedelta(hours=1)
            fechas.append(fechaAux)
            medidas.append(None)
        if v.valido == 1:
            fechas.append(v.fecha_hora)
            medidas.append(round(v.actividad, redondeo))
        else:
            fechas.append(v.fecha_hora)
            medidas.append(None)
        fechaPrevia = v.fecha_hora
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie, round(difMaxima,2)

# CONSULTA DEL PARAMETRO AMD DE LA TABLA ESPECGAMMA
def consultaAMDGraficaEspecGamma(bd, detector, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    medidas = []

    estEspecGamma = EstEspecGamma.objects.using(bd).filter(relacion_detectores_estacion_id=detector).filter(
        isotopos_id=canal).filter(fecha_hora__gt=dias)
    for v in estEspecGamma:
        if v.valido == 1:
            medidas.append(round(v.amd, redondeo))
        else:
            medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return serie

# CONSULTA DEL PARAMETRO VALOR REALIZADA UNA MEDIA DE LA TABLA ESPECGAMMA
def consultaMediaEspecGamma(bd, detector, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    medidas = []

    estEspecGamma = EstEspecGamma.objects.using(bd).filter(relacion_detectores_estacion_id=detector).filter(
        isotopos_id=canal).filter(fecha_hora__gt=dias)
    for v in estEspecGamma:
        if v.valido == 1:
            medidas.append(round(v.amd, redondeo))
        else:
            medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return serie


# CONSULTA DE LA TABLA ESPECGAMMA
def consultasEspecAcumGamma(bd, id, canal, dias, serieConf):
    serie = {}
    fechas = None

    if serieConf.tipodato == "valor":
        fechas, serie = consultaValorGraficaEspecAcumGamma(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                           serieConf.color, serieConf.redondeo)
    elif serieConf.tipodato == "amd":
        serie = consultaAMDGraficaEspecAcumGamma(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                 serieConf.color, serieConf.redondeo)
    return fechas, serie


# CONSULTA DEL PARAMETRO VALOR DE LA TABLA ESPECGAMMAACUMULADOS
def consultaValorGraficaEspecAcumGamma(bd, detector, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    fechas = []
    medidas = []

    estEspecAcumGamma = EstEspecGammaAcumulados.objects.using(bd).filter(
        relacion_detectores_estacion_id=detector).filter(isotopos_id=canal).filter(fecha_hora__gt=dias)
    for v in estEspecAcumGamma:
        if (v.fecha_hora.hour == 0 and v.fecha_hora.minute ==0) or bd == 'csn':
            if v.valido == 1:
                fechas.append(v.fecha_hora)
                medidas.append(round(v.actividad, redondeo))
            else:
                fechas.append(v.fecha_hora)
                medidas.append(None)

    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie


# CONSULTA DEL PARAMETRO AMD DE LA TABLA ESPECGAMMAACUMULADOS
def consultaAMDGraficaEspecAcumGamma(bd, detector, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    medidas = []

    estEspecAcumGamma = EstEspecGammaAcumulados.objects.using(bd).filter(
        relacion_detectores_estacion_id=detector).filter(isotopos_id=canal).filter(fecha_hora__gt=dias)
    for v in estEspecAcumGamma:
        if (v.fecha_hora.hour == 0 and v.fecha_hora.minute ==0) or bd == 'csn':
            if v.valido == 1:
                medidas.append(round(v.amd, redondeo))
            else:
                medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return serie


# CONSULTA DE LA TABLA MEDIAS DIARIAS
def consultasMedias(bd, id, canal, dias, serieConf, nombre):
    serie = {}
    fechas = None

    if serieConf.tipodato == "valor":
        fechas, serie = consultaValorMedias(bd, id, canal, dias, nombre, serieConf.tipografica, serieConf.redondeo)
    return fechas, serie


# CONSULTA DEL PARAMETRO VALOR DE LA TABLA MEDIAS DIARIAS
def consultaValorMedias(bd, estacion, canal, dias, nombre, tipo, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None

    media = MediasDiarias.objects.using(bd).filter(id_estacion=estacion,id_detector=0,id_canal=canal,fecha__gte=dias.date())
    for v in media:
        fechas.append(v.fecha)
        if v.valor is None:
            medidas.append(None)
        else:
            medidas.append(round(v.valor, redondeo))
    fechas.append(datetime.now(tz.timezone("Europe/Madrid")))
    medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo}
    return fechas, serie


# CONSULTA DE LA TABLA PARAMETROSCONTROL
def consultasParamControl(bd, id, canal, dias, serieConf):
    serie = {}
    fechas = None
    diferencia = None

    if serieConf.tipodato == "valor":
        fechas, serie, diferencia = consultaValorParamControl(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                  serieConf.color, serieConf.redondeo)
    elif "media" in serieConf.tipodato:
        fechas, serie, diferencia = consultaMediaParamControl(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                  serieConf.color,int(serieConf.tipodato.split("_")[1]), serieConf.redondeo)

    return fechas, serie, diferencia

# CONSULTA DEL PARAMETRO VALOR DE LA TABLA PARAMETROSCONTROL
def consultaValorParamControl(bd, estacion, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None
    difMaxima = 0.0

    param = ParamControl.objects.using(bd).filter(estaciones=estacion).filter(canales=canal).filter(
        valido=1).filter(fecha_hora__gte=dias)
    for v in param:
        if diferencia == None:
            fechaPrevia = v.fecha_hora
        diferencia = v.fecha_hora - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
        if horas > difMaxima:
            difMaxima = horas
        if horas > 1.0:
            fechaAux = v.fecha_hora + timedelta(hours=1)
            fechas.append(fechaAux)
            medidas.append(None)
        fechas.append(v.fecha_hora)
        medidas.append(round(v.valor, redondeo))
        fechaPrevia = v.fecha_hora
    fechas.append(datetime.now(tz.timezone("Europe/Madrid")))
    medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie, round(difMaxima,2)

# CONSULTA DEL PARAMETRO VALOR DE LA TABLA PARAMETROSCONTROL APLICANDO UNA MEDIA DEFINIDA POR LA VARIABLE TIEMPO
def consultaMediaParamControl(bd, estacion, canal, dias, nombre, tipo, color, tiempo, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None
    difMaxima = 0.0

    param = ParamControl.objects.using(bd).filter(estaciones=estacion).filter(canales=canal).filter(valido=1).filter(fecha_hora__gte=dias)
    f_ini, valor = None, []
    for v in param:
        if diferencia == None:
            fechaPrevia = v.fecha_hora
        diferencia = v.fecha_hora - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
        if horas > difMaxima:
            difMaxima = horas
        if horas > 1.0:
            fechaAux = v.fecha_hora + timedelta(hours=1)
            fechas.append(fechaAux)
            medidas.append(None)
        if f_ini is None:
            f_ini = v.fecha_hora
        dif = (v.fecha_hora - f_ini).total_seconds() / 60
        if dif < tiempo:
            valor.append(v.valor)
        else:
            fechas.append(f_ini)
            medidas.append(round(sum(valor)/len(valor),redondeo))
            f_ini = v.fecha_hora
            valor = []
            valor.append(v.valor)
        fechaPrevia = v.fecha_hora
    fechas.append(datetime.now(tz.timezone("Europe/Madrid")))
    medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie, round(difMaxima,2)

# CONSULTA DE LA TABLA ESTMETEOCONTROL
def consultasEstMeteoControl(bd, id, canal, dias, serieConf):
    serie = {}
    fechas = None
    diferencia = None

    if serieConf.tipodato == "valor":
        fechas, serie, diferencia = consultaValorEstMeteoControl(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                     serieConf.color, serieConf.redondeo)
    elif "media" in serieConf.tipodato:
        fechas, serie, diferencia = consultaMediaEstMeteoControl(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,
                                                  serieConf.color,int(serieConf.tipodato.split("_")[1]), serieConf.redondeo)
    return fechas, serie, diferencia

# CONSULTA DEL PARAMETRO VALOR DE LA TABLA ESTMETEOCONTROL
def consultaValorEstMeteoControl(bd, estacion, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None
    difMaxima = 0.0

    meteo = EstMeteorologicas.objects.using(bd).filter(estaciones=estacion).filter(canales=canal).filter(
        valido=1).filter(fecha_hora__gte=dias)
    for v in meteo:
        if diferencia == None:
            fechaPrevia = v.fecha_hora
        diferencia = v.fecha_hora - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
        if horas > difMaxima:
            difMaxima = horas
        if horas > 1.0:
            fechaAux = v.fecha_hora + timedelta(hours=1)
            fechas.append(fechaAux)
            medidas.append(None)
        fechas.append(v.fecha_hora)
        medidas.append(round(v.valor, redondeo))
        fechaPrevia = v.fecha_hora
    fechas.append(datetime.now(tz.timezone("Europe/Madrid")))
    medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie, round(difMaxima,2)

# CONSULTA DEL PARAMETRO VALOR DE LA TABLA ESTMETEOCONTROL APLICANDO UNA MEDIA EN FUNCION DE LA VARIABLE TIEMPO
def consultaMediaEstMeteoControl(bd, estacion, canal, dias, nombre, tipo, color, tiempo, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None
    difMaxima = 0.0

    meteo = EstMeteorologicas.objects.using(bd).filter(estaciones=estacion).filter(canales=canal).filter(
        valido=1).filter(fecha_hora__gte=dias)
    f_ini, valor = None, []
    for v in meteo:
        if diferencia == None:
            fechaPrevia = v.fecha_hora
        diferencia = v.fecha_hora - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
        if horas > difMaxima:
            difMaxima = horas
        if horas > 1.0:
            fechaAux = v.fecha_hora + timedelta(hours=1)
            fechas.append(fechaAux)
            medidas.append(None)
        if f_ini is None:
            f_ini = v.fecha_hora
        dif = (v.fecha_hora - f_ini).total_seconds() / 60
        if dif < tiempo:
            valor.append(v.valor)
        else:
            fechas.append(f_ini)
            medidas.append(round(sum(valor)/len(valor),redondeo))
            f_ini = v.fecha_hora
            valor = []
            valor.append(v.valor)
        fechaPrevia = v.fecha_hora
    fechas.append(datetime.now(tz.timezone("Europe/Madrid")))
    medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie, round(difMaxima,2)

# CONSULTA DE LA TABLA GAMYRADIOYODOS
def consultasGamYRadioyodos(bd, id, canal, dias, serieConf):
    serie = {}
    fechas = None

    if serieConf.tipodato == "valor":
        fechas, serie, diferencia = consultaValorGraficaGamYRadioyodos(bd, id, canal, dias, serieConf.nombre, serieConf.tipografica,serieConf.color, serieConf.redondeo)
    return fechas, serie, diferencia

# CONSULTA DEL PARAMETRO VALOR DE LA TABLA GAMYRADIOYODOS
def consultaValorGraficaGamYRadioyodos(bd, estacion, canal, dias, nombre, tipo, color, redondeo):
    serie = {}
    fechas = []
    medidas = []
    fechaPrevia, diferencia = None, None
    difMaxima = 0.0
    estGYR = EstGamYRadioyodos.objects.using(bd).filter(estaciones=estacion).filter(canales=canal).filter(
        valido=1).filter(fecha_hora__gte=dias)
    for v in estGYR:
        if diferencia == None:
            fechaPrevia = v.fecha_hora 

        diferencia = v.fecha_hora - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
         
        if horas > difMaxima:
            difMaxima = horas
        if horas > 1.0:
            fechaAux = v.fecha_hora + timedelta(hours=1)
            fechas.append(fechaAux)
            medidas.append(None)
        if v.valido == 1:
            fechas.append(v.fecha_hora)
            medidas.append(round(v.valor, redondeo))
        else:
            fechas.append(v.fecha_hora)
            medidas.append(None)
        fechaPrevia = v.fecha_hora
    
    if fechaPrevia is not None:
        diferencia = datetime.now(tz.timezone("Europe/Madrid")) - fechaPrevia
        dias = diferencia.days * 24
        segundos = diferencia.seconds / 3600
        horas = float(dias) + segundos
        if horas > difMaxima:
            difMaxima = horas

    fechas.append(datetime.now(tz.timezone("Europe/Madrid")))
    medidas.append(None)
    serie = {"name": nombre, "data": medidas, "type": tipo, "color": "#" + color}
    return fechas, serie, round(difMaxima,2)

# METODO PARA INVALIDAR DATOS DE LAS GRAFICAS RARE
@permission_required('auth.guardia_rarex')
def invalidarDatos(request, id_chart, anio):
    idChart = id_chart.replace('chartid_','')
    config = ConfigGraficasRare.objects.using('rvra').filter(id=idChart)[0]
    bd = config.red
    dias = datetime.now(timezone.utc) - timedelta(days=config.dias)
    est = Estaciones.objects.using(bd).filter(id=config.id_estacion)[0]
    texto = est.nombre
    media = None

    if config.series.find(",") >= 0:
        idSerieConf = config.series.split(",")[0]
    else:
        idSerieConf = config.series
    valores = []
    serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=idSerieConf)[0]

    
    if serieConf.tabla == "Gamma":
        if anio == "0":
            consulta = EstGamYRadioyodos.objects.using(bd).filter(estaciones=config.id_estacion,canales=serieConf.canal,fecha_hora__gte=dias,valido=1)
        else:
            consulta = EstGamYRadioyodos.objects.using(bd+"_historico").filter(estaciones=config.id_estacion,canales=serieConf.canal,fecha_hora__year=anio,valido=1)
        media = {"valor": consulta.aggregate(Avg('valor'))}
        for c in consulta:
            auxValor = {}
            auxValor["fecha"] = c.fecha_hora
            auxValor["estacion"] = c.estaciones
            auxValor["canal"] = c.canales
            auxValor["valor"] = c.valor
            auxValor["valido"] = c.valido
            valores.append(auxValor)
        canal = Canales.objects.using('rvra').filter(id=serieConf.canal)[0]
        texto = texto + " - " + canal.nombre
    elif serieConf.tabla == "Espec":
        if anio == "0":
            consulta = EstEspecGamma.objects.using(bd).filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__gte=dias,valido=1)
        else:
            consulta = EstEspecGamma.objects.using(bd+"_historico").filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__year=anio,valido=1)
        media = {"actividad": consulta.aggregate(Avg('actividad')),"amd": consulta.aggregate(Avg('amd'))}
        for c in consulta:
            auxValor = {}
            auxValor["fecha"] = c.fecha_hora
            auxValor["detector"] = c.relacion_detectores_estacion_id
            auxValor["isotopo"] = c.isotopos_id
            auxValor["actividad"] = c.actividad
            auxValor["error"] = c.error
            auxValor["amd"] = c.amd
            auxValor["valido"] = c.valido
            valores.append(auxValor)
        isotopo = Isotopos.objects.using('rvra').filter(id=serieConf.canal)[0]
        texto = texto + " - " + isotopo.n_iso
    elif serieConf.tabla == "EspecAcum":
        if anio == "0":
            consulta = EstEspecGammaAcumulados.objects.using(bd).filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__gte=dias,valido=1)
        else:
            consulta = EstEspecGammaAcumulados.objects.using(bd+"_historico").filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__year=anio,valido=1)
        media = {"actividad": consulta.aggregate(Avg('actividad')),"amd": consulta.aggregate(Avg('amd'))}
        for c in consulta:
            auxValor = {}
            auxValor["fecha"] = c.fecha_hora
            auxValor["detector"] = c.relacion_detectores_estacion_id
            auxValor["isotopo"] = c.isotopos_id
            auxValor["actividad"] = c.actividad
            auxValor["error"] = c.error
            auxValor["amd"] = c.amd
            auxValor["valido"] = c.valido
            valores.append(auxValor)
        isotopo = Isotopos.objects.using('rvra').filter(id=serieConf.canal)[0]
        texto = texto + " - " + isotopo.n_iso

    valoresJSON = simplejson.dumps(valores, default=myconverter)
 
    if anio == "0":
        return render(request, 'correccionDatos.html', { "estacion":texto, "tabla": serieConf.tabla, "valores": valoresJSON, "media": media  })
    else:
        return render(request, 'correccionDatos.html', { "estacion":texto, "tabla": serieConf.tabla, "valores": valoresJSON, "historico": True, "media": media  })

# METODO PARA INVALIDAR DATOS DE LAS GRAFICAS CSN
@permission_required('auth.guardia_rarex')
def invalidarDatosCSN(request, id_chart, anio):
    idChart = id_chart.replace('chartid_','')
    config = ConfigGraficasRare.objects.using('rvra').filter(id=idChart)[0]
    bd = config.red
    dias = datetime.now(timezone.utc) - timedelta(days=config.dias)
    est = Estaciones.objects.using(bd).filter(id=config.id_estacion)[0]
    texto = est.nombre

    if config.series.find(",") >= 0:
        idSerieConf = config.series.split(",")[0]
    else:
        idSerieConf = config.series
    valores = []
    serieConf = ConfigSerieGrafica.objects.using('rvra').filter(id=idSerieConf)[0]

    if serieConf.tabla == "Gamma":
        if anio == "0":
            consulta = EstGamYRadioyodos.objects.using(bd).filter(estaciones=config.id_estacion,canales=serieConf.canal,fecha_hora__gte=dias,valido=1)
        else:
            consulta = EstGamYRadioyodos.objects.using(bd+"_historico").filter(estaciones=config.id_estacion,canales=serieConf.canal,fecha_hora__year=anio,valido=1)
        media = {"valor": consulta.aggregate(Avg('valor'))}
        for c in consulta:
            auxValor = {}
            auxValor["fecha"] = c.fecha_hora
            auxValor["estacion"] = c.estaciones
            auxValor["canal"] = c.canales
            auxValor["valor"] = c.valor
            auxValor["valido"] = c.valido
            valores.append(auxValor)
        canal = Canales.objects.using('rvra').filter(id=serieConf.canal)[0]
        texto = texto + " - " + canal.nombre
    elif serieConf.tabla == "Espec":
        if anio == "0":
            consulta = EstEspecGamma.objects.using(bd).filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__gte=dias,valido=1)
        else:
            consulta = EstEspecGamma.objects.using(bd+"_historico").filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__year=anio,valido=1)
        media = {"actividad": consulta.aggregate(Avg('actividad')),"amd": consulta.aggregate(Avg('amd'))}
        for c in consulta:
            auxValor = {}
            auxValor["fecha"] = c.fecha_hora
            auxValor["detector"] = c.relacion_detectores_estacion_id
            auxValor["isotopo"] = c.isotopos_id
            auxValor["actividad"] = c.actividad
            auxValor["error"] = c.error
            auxValor["amd"] = c.amd
            auxValor["valido"] = c.valido
            valores.append(auxValor)
        isotopo = Isotopos.objects.using('rvra').filter(id=serieConf.canal)[0]
        texto = texto + " - " + isotopo.n_iso
    elif serieConf.tabla == "EspecAcum":
        if anio == "0":
            consulta = EstEspecGammaAcumulados.objects.using(bd).filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__gte=dias,valido=1)
        else:
            consulta = EstEspecGamma.objects.using(bd+"_historico").filter(relacion_detectores_estacion_id=config.detector,isotopos_id=serieConf.canal,fecha_hora__year=anio,valido=1)
        media = {"actividad": consulta.aggregate(Avg('actividad')),"amd": consulta.aggregate(Avg('amd'))}
        for c in consulta:
            auxValor = {}
            auxValor["fecha"] = c.fecha_hora
            auxValor["detector"] = c.relacion_detectores_estacion_id
            auxValor["isotopo"] = c.isotopos_id
            auxValor["actividad"] = c.actividad
            auxValor["error"] = c.error
            auxValor["amd"] = c.amd
            auxValor["valido"] = c.valido
            valores.append(auxValor)
        isotopo = Isotopos.objects.using('rvra').filter(id=serieConf.canal)[0]
        texto = texto + " - " + isotopo.n_iso

    valoresJSON = simplejson.dumps(valores, default=myconverter)

    if anio == "0":
        return render(request, 'correccionDatosCSN.html', { "estacion":texto, "tabla": serieConf.tabla, "valores": valoresJSON , "media": media})
    else:
        return render(request, 'correccionDatosCSN.html', { "estacion":texto, "tabla": serieConf.tabla, "valores": valoresJSON, "historico": True, "media": media})

# METODO PARA INVALIDAR DATOS DE LA TABLA GAMMA DE LAS GRAFICAS RARE
@permission_required('auth.guardia_rarex')
def invalidarDatoGamma(request, estacion, canal, fecha, hora, historico):
    year = int(fecha.split("-")[0])
    month = int(fecha.split("-")[1])
    day = int(fecha.split("-")[2])
    hour = int(hora.split("-")[0])
    minute = int(hora.split("-")[1])
    second = int(hora.split("-")[2])
    fecha = datetime(year, month, day, hour, minute, second)
    resultado = 1
    bd = 'rvra'
    if historico == "1":
        bd = 'rvra_historico'
    valor = EstGamYRadioyodos.objects.using(bd).filter(fecha_hora=fecha).filter(canales=canal).filter(estaciones=estacion)[0]
    try:
        EstGamYRadioyodos.objects.using(bd).filter(fecha_hora=fecha).filter(canales=canal).filter(estaciones=estacion).update(valido=0)
    except ObjectDoesNotExist:
        resultado = 0
    try:
        EstGamYRadioyodos.objects.using('csn').filter(fecha_hora=fecha).filter(canales=canal).filter(estaciones=estacion).delete()
    except ObjectDoesNotExist:
        resultado = 0

    fechaAjustada = fecha.astimezone(pytz.utc)
    fechaAjustadaAntes = fechaAjustada - timedelta(hours=5)
    fechaAjustadaDespues = fechaAjustada + timedelta(hours=5)

    medidas = EstGamYRadioyodos.objects.using('csn').filter(fecha_hora__gte=fechaAjustadaAntes, fecha_hora__lte=fechaAjustadaDespues, canales=canal, estaciones=estacion)

    try:
        if valor.valor == 0.0:
            EstGamYRadioyodos.objects.using('csn').filter(fecha_hora__gte=fechaAjustadaAntes, fecha_hora__lte=fechaAjustadaDespues, canales=canal, estaciones=estacion, valor=0).delete()
        else:
            EstGamYRadioyodos.objects.using('csn').filter(fecha_hora__gte=fechaAjustadaAntes, fecha_hora__lte=fechaAjustadaDespues, canales=canal, estaciones=estacion, valor=valor.valor).delete()

    except ObjectDoesNotExist:
        resultado = 0

    elemento = "fecha:" + str(fecha) + " , canal:" + str(canal) + " , estacion:" + str(estacion)
    datoCorregido = DatosCorregidosGraficas(usuario=request.user, fecha=datetime.now(), tabla="EstGamYRadioyodos", elemento=elemento)
    datoCorregido.save(using='rvra')

    return JsonResponse({"valor":resultado}, safe=False)

# METODO PARA INVALIDAR DATOS DE LA TABLA ESPEC DE LAS GRAFICAS RARE
@permission_required('auth.guardia_rarex')
def invalidarDatoEspec(request, detector, isotopo, fecha, hora, todos, historico):
    year = int(fecha.split("-")[0])
    month = int(fecha.split("-")[1])
    day = int(fecha.split("-")[2])
    hour = int(hora.split("-")[0])
    minute = int(hora.split("-")[1])
    second = int(hora.split("-")[2])
    fecha = datetime(year, month, day, hour, minute, second)
    resultado = 1
    bd = 'rvra'
    if historico == "1":
        bd = 'rvra_historico'

    valor = EstEspecGamma.objects.using(bd).filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).filter(isotopos_id=isotopo)[0]

    try:
        if todos == "1":
            EstEspecGamma.objects.using(bd).filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).update(valido=0)
        else:
            EstEspecGamma.objects.using(bd).filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).filter(isotopos_id=isotopo).update(valido=0)
    except ObjectDoesNotExist:
        resultado = 0

    fechaAjustada = fecha.astimezone(pytz.utc)
    fechaAjustadaAntes = fechaAjustada - timedelta(hours=5)
    fechaAjustadaDespues = fechaAjustada + timedelta(hours=5)

    try:
        cons = EstEspecGamma.objects.using("csn").filter(fecha_hora__gte=fechaAjustadaAntes,fecha_hora__lte=fechaAjustadaDespues,relacion_detectores_estacion_id=detector,isotopos_id=isotopo)
        for c in cons:
            if c.actividad == valor.actividad and c.amd == valor.amd:
                try:
                    if todos == "1":
                        EstEspecGamma.objects.using("csn").filter(fecha_hora=c.fecha_hora,relacion_detectores_estacion_id=c.relacion_detectores_estacion_id).delete()
                    else:
                        EstEspecGamma.objects.using("csn").filter(fecha_hora=c.fecha_hora,relacion_detectores_estacion_id=c.relacion_detectores_estacion_id,isotopos_id=c.isotopos_id).delete()
                except ObjectDoesNotExist:
                    resultado = 0
    except ObjectDoesNotExist:
        resultado = 0

    if todos == "1":
        elemento = "fecha:" + str(fecha) + " , isotopo: todos , detector:" + str(detector)
    else:
        elemento = "fecha:" + str(fecha) + " , isotopo:" + str(isotopo) + " , detector:" + str(detector)
    datoCorregido = DatosCorregidosGraficas(usuario=request.user, fecha=datetime.now(), tabla="EstEspecGamma", elemento=elemento)
    datoCorregido.save(using='rvra')

    return JsonResponse({"valor":resultado}, safe=False)

# METODO PARA INVALIDAR DATOS DE LA TABLA ESPEC DE LAS GRAFICAS RARE
@permission_required('auth.guardia_rarex')
def invalidarDatoEspecAcum(request, detector, isotopo, fecha, hora, todos, historico):
    year = int(fecha.split("-")[0])
    month = int(fecha.split("-")[1])
    day = int(fecha.split("-")[2])
    hour = int(hora.split("-")[0])
    minute = int(hora.split("-")[1])
    second = int(hora.split("-")[2])
    fecha = datetime(year, month, day, hour, minute, second)
    resultado = 1
    bd = 'rvra'
    if historico == "1":
        bd = 'rvra_historico'

    valor = EstEspecGammaAcumulados.objects.using(bd).filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).filter(isotopos_id=isotopo)[0]

    try:
        if todos == "1":
            EstEspecGammaAcumulados.objects.using(bd).filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).update(valido=0)
        else:
            EstEspecGammaAcumulados.objects.using(bd).filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).filter(isotopos_id=isotopo).update(valido=0)
    except ObjectDoesNotExist:
        resultado = 0

    fechaAjustada = fecha.astimezone(pytz.utc)
    fechaAjustadaAntes = fechaAjustada - timedelta(hours=5)
    fechaAjustadaDespues = fechaAjustada + timedelta(hours=5)

    try:
        cons = EstEspecGammaAcumulados.objects.using("csn").filter(fecha_hora__gte=fechaAjustadaAntes,fecha_hora__lte=fechaAjustadaDespues,relacion_detectores_estacion_id=detector,isotopos_id=isotopo)
        for c in cons:
            if c.actividad == valor.actividad and c.amd == valor.amd:
                try:
                    if todos == "1":
                        EstEspecGammaAcumulados.objects.using("csn").filter(fecha_hora=c.fecha_hora,relacion_detectores_estacion_id=c.relacion_detectores_estacion_id).delete()
                    else:
                        EstEspecGammaAcumulados.objects.using("csn").filter(fecha_hora=c.fecha_hora,relacion_detectores_estacion_id=c.relacion_detectores_estacion_id,isotopos_id=c.isotopos_id).delete()
                except ObjectDoesNotExist:
                    resultado = 0
    except ObjectDoesNotExist:
        resultado = 0

    if todos == "1":
        elemento = "fecha:" + str(fecha) + " , isotopo: todos , detector:" + str(detector)
    else:
        elemento = "fecha:" + str(fecha) + " , isotopo:" + str(isotopo) + " , detector:" + str(detector)
    datoCorregido = DatosCorregidosGraficas(usuario=request.user, fecha=datetime.now(), tabla="EstEspecGamma", elemento=elemento)
    datoCorregido.save(using='rvra')

    return JsonResponse({"valor":resultado}, safe=False)


# METODO PARA INVALIDAR DATOS DE LA TABLA GAMMA DE LAS GRAFICAS CSN
@permission_required('auth.guardia_rarex')
def invalidarDatoGammaCSN(request, estacion, canal, fecha, hora, historico):
    year = int(fecha.split("-")[0])
    month = int(fecha.split("-")[1])
    day = int(fecha.split("-")[2])
    hour = int(hora.split("-")[0])
    minute = int(hora.split("-")[1])
    second = int(hora.split("-")[2])
    fecha = datetime(year, month, day, hour, minute, second)
    resultado = 1
    bd = 'rvra'
    if historico == "1":
        bd = 'rvra_historico'

    try:
        EstGamYRadioyodos.objects.using('csn').filter(fecha_hora=fecha).filter(canales=canal).filter(estaciones=estacion).delete()
    except ObjectDoesNotExist:
        resultado = 0

    elemento = "fecha:" + str(fecha) + " , canal:" + str(canal) + " , estacion:" + str(estacion)
    datoCorregido = DatosCorregidosGraficas(usuario=request.user, fecha=datetime.now(), tabla="EstGamYRadioyodos", elemento=elemento)
    datoCorregido.save(using='rvra')

    return JsonResponse({"valor":resultado}, safe=False)


# METODO PARA INVALIDAR DATOS DE LA TABLA ESPEC DE LAS GRAFICAS CSN
@permission_required('auth.guardia_rarex')
def invalidarDatoEspecCSN(request, detector, isotopo, fecha, hora, todos, historico):
    year = int(fecha.split("-")[0])
    month = int(fecha.split("-")[1])
    day = int(fecha.split("-")[2])
    hour = int(hora.split("-")[0])
    minute = int(hora.split("-")[1])
    second = int(hora.split("-")[2])
    fecha = datetime(year, month, day, hour, minute, second)
    resultado = 1
    bd = 'rvra'
    if historico == "1":
        bd = 'rvra_historico'

    try:
        if todos == "1":
            EstEspecGamma.objects.using("csn").filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).delete()
        else:
            EstEspecGamma.objects.using("csn").filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).filter(isotopos_id=isotopo).delete()
    except ObjectDoesNotExist:
        resultado = 0

    if todos == "1":
        elemento = "fecha:" + str(fecha) + " , isotopo: todos , detector:" + str(detector)
    else:
        elemento = "fecha:" + str(fecha) + " , isotopo:" + str(isotopo) + " , detector:" + str(detector)
    datoCorregido = DatosCorregidosGraficas(usuario=request.user, fecha=datetime.now(), tabla="EstEspecGamma_CSN", elemento=elemento)
    datoCorregido.save(using='rvra')

    return JsonResponse({"valor":resultado}, safe=False)


# METODO PARA INVALIDAR DATOS DE LA TABLA ESPEC DE LAS GRAFICAS CSN
@permission_required('auth.guardia_rarex')
def invalidarDatoEspecAcumCSN(request, detector, isotopo, fecha, hora, todos, historico):
    year = int(fecha.split("-")[0])
    month = int(fecha.split("-")[1])
    day = int(fecha.split("-")[2])
    hour = int(hora.split("-")[0])
    minute = int(hora.split("-")[1])
    second = int(hora.split("-")[2])
    fecha = datetime(year, month, day, hour, minute, second)
    resultado = 1
    bd = 'rvra'
    if historico == "1":
        bd = 'rvra_historico'

    try:
        if todos == "1":
            EstEspecGammaAcumulados.objects.using("csn").filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).delete()
        else:
            EstEspecGammaAcumulados.objects.using("csn").filter(fecha_hora=fecha).filter(relacion_detectores_estacion_id=detector).filter(isotopos_id=isotopo).delete()
    except ObjectDoesNotExist:
        resultado = 0

    if todos == "1":
        elemento = "fecha:" + str(fecha) + " , isotopo: todos , detector:" + str(detector)
    else:
        elemento = "fecha:" + str(fecha) + " , isotopo:" + str(isotopo) + " , detector:" + str(detector)
    datoCorregido = DatosCorregidosGraficas(usuario=request.user, fecha=datetime.now(), tabla="EstEspecGammaAcum_CSN", elemento=elemento)
    datoCorregido.save(using='rvra')

    return JsonResponse({"valor":resultado}, safe=False)



# METODO PARA OBTENER EL INFORME FINAL DE LAS GRAFICAS RARE
@permission_required('auth.guardia_rarex')
def informeGuardiaRare(request):
    valores = {}
    ayer = date.today() - timedelta(days=1)

    valores["Dia"] = ayer

    ayerInicio = datetime.today() - timedelta(days=1)
    ayerFin = datetime.today() - timedelta(days=1)
    ayerInicio = ayerInicio.replace(hour=0, minute=0, second=0)
    ayerFin = ayerFin.replace(hour=23, minute=59, second=59)

    numValoresTotales, totalOperatividad, operatividades = calcularOperatividad(datetime.today() - timedelta(days=1))
    valores["OperatividadEstaciones"] = operatividades
    valores["OperatividadTotalGamma"] = int(totalOperatividad)

    '''
    detectores = EstEspecGamma.objects.using('rvra').filter(isotopos_id=14,fecha_hora__gte=ayerInicio,fecha_hora__lte=ayerFin).values('relacion_detectores_estacion_id').distinct().count()
    numValoresYodo = EstEspecGamma.objects.using('rvra').filter(isotopos_id=14,fecha_hora__gte=ayerInicio,fecha_hora__lte=ayerFin).count()
    '''

    smsEnviados = MensajeHistoenvio.objects.using('rvra').filter(fecha=ayer).count()
    valores["SMSEnviados"] = smsEnviados

    datosRadio, erroresRadio, datosIntranet = calcularErrores(datetime.today() - timedelta(days=1))
    valores["datosRadio"] = datosRadio
    valores["erroresRadio"] = erroresRadio
    valores["datosIntranet"] = datosIntranet

    nivelesUno = MensajesTelegramHistorico.objects.using('spd').filter(fecha_hora_utc__gte=ayerInicio,fecha_hora_utc__lte=ayerFin,id_area=1,mensaje__contains='Nivel 1').exclude(mensaje__contains='MONITORIZA EN PRUEBAS').exclude(mensaje__contains='Fin de nivel').count()
    nivelesDos = MensajesTelegramHistorico.objects.using('spd').filter(fecha_hora_utc__gte=ayerInicio,fecha_hora_utc__lte=ayerFin,id_area=1,mensaje__contains='Nivel 2').exclude(mensaje__contains='MONITORIZA EN PRUEBAS').exclude(mensaje__contains='Fin de nivel').count()
    nivelesTres = MensajesTelegramHistorico.objects.using('spd').filter(fecha_hora_utc__gte=ayerInicio,fecha_hora_utc__lte=ayerFin,id_area=1,mensaje__contains='Nivel 3').exclude(mensaje__contains='MONITORIZA EN PRUEBAS').exclude(mensaje__contains='Fin de nivel').count()

    valores["Niveles1"] = nivelesUno
    valores["Niveles2"] = nivelesDos
    valores["Niveles3"] = nivelesTres

    listaBotones = ConfigGraficasRare.objects.using('rvra').filter(red='rvra').values('id_boton', 'nombre_boton').order_by(
        'id_boton').distinct()
    listaBotones2 = ConfigGraficasRare.objects.using('rvra').filter(red='rvra').values('id_boton', 'nombre_boton').order_by(
        'id_boton').distinct()
    checksum1, checksum2 = 0, 0
    for l in listaBotones:
        checksum1 += hash(frozenset(l))
    for l2 in listaBotones2:
        checksum2 += hash(frozenset(l2))
    check1 = hashlib.md5(str(checksum1).encode('utf-8')).hexdigest()
    check2 = hashlib.md5(str(checksum2).encode('utf-8')).hexdigest()
    if (check1 == check2):
        valores["checksum"] = 1
    else:
        valores["checksum"] = 0
    valores["checksum1"] = check1
    valores["checksum2"] = check2

    return JsonResponse(valores, safe=False)

@permission_required('auth.guardia_rarex')
def consultarImagenPapel(request):
    fechaHora = datetime.now().astimezone(pytz.timezone("Europe/Madrid"))
    estacionesPapel = [{"nombre":"azuaga", "ip":'http://172.20.36.19/videostream.cgi?user=rvra&pwd=rvra&resolution=32&rate=0'},{"nombre":"saucedilla", "ip":'http://172.20.36.30/videostream.cgi?user=rvra&pwd=rvra&resolution=32&rate=0'},{"nombre":"serrejon", "ip":'rtsp://rvra:rvra@172.20.36.68:554/live/ch0'},{"nombre":"fregenal", "ip":'http://172.20.36.11/videostream.cgi?user=rvra&pwd=rvra&resolution=32&rate=0'}]
    for estacion in estacionesPapel:
        try:
            vid = cv2.VideoCapture(estacion["ip"])
            ret, frame = vid.read()
            cv2.putText(frame,estacion["nombre"]+" "+fechaHora.strftime("%m/%d/%Y, %H:%M:%S"), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, 3)	
            print("CARGANDO CAMARA", estacion["nombre"], settings.STATIC_ROOT)
            cv2.imwrite(settings.STATIC_ROOT +"papel/"+estacion["nombre"]+'_papel.jpg', frame)
        except Exception as e:
            print("ERROR CARGANDO CAMARA", estacion["nombre"], e)
            
    return render(
        request,
        "consultaCamarasEstaciones.html",
        {}
    )

def calcularOperatividad(dia):
    inicio = dia.replace(hour=0, minute=0, second=0)
    fin = dia.replace(hour=23, minute=59, second=59)
    totalOperatividad = 0.0
    operatividades = []
    estaciones = InformacionesEstaciones.objects.using("rvra")
    numEstacionesTotales = len(estaciones)
    numValoresTotales = 0
    for est in estaciones:
        numValoresDosis = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__gte=inicio,fecha_hora__lte=fin).filter(canales=1).filter(estaciones=est.id_estacion.id).count()
        numValoresTotales += numValoresDosis
        valNecesarios = 24*60*60 / est.tiempo_consulta
        operatividadDosis = int((numValoresDosis/valNecesarios) *100)
        if operatividadDosis > 100:
            operatividadDosis = 100
        totalOperatividad += operatividadDosis
        datos_estacion = Estaciones.objects.using('rvra').filter(id=est.id_estacion.id)[0]
        operatividades.append({"Estacion":datos_estacion.nombre,"Frecuencia":est.tiempo_consulta, "Operatividad":operatividadDosis})
    return  numValoresTotales, totalOperatividad / numEstacionesTotales, operatividades

# METODO PARA SUBIR EL INFORME DE LAS GRAFICAS
@permission_required('auth.guardia_rarex')
def uploadResumenGuardia(request):
    ahora = datetime.now()
    RevisionGraficas(usuario=request.user, fecha=ahora, comentarios=request.POST.get('comentarios'), operatividad=request.POST.get('operatividad'), niveles=request.POST.get('niveles'), integridad=request.POST.get('integridad'), grafica=request.POST.get('red')).save(using='rvra')
    respuesta = str(request.user) + ", tu informe para las graficas de " + str(request.POST.get('grafica')) + " ha sido almacenado correctamente. Muchas gracias"
    return JsonResponse(respuesta, safe=False)

# METODO PARA FINALIZAR GRAFICAS RARE. FALTA GUARDAR LA INFO EN UNA TABLA
@permission_required('auth.guardia_rarex')
def finalizarInformeRare(request):
    user = request.user
    return render(
        request,
        "content/portada.html",
        {
            "user":user,
        }
    )

# METODO PARA MOSTRAR LA INFORMACION DE LAS GUARDIAS REALIZADAS
@permission_required('auth.guardia_rarex')
def infoGuardias(request):
    page = request.GET.get('page', 1)


    bdRevisiones = RevisionGraficas.objects.using('rvra').filter(grafica='rvra').order_by('-id')
    paginator = Paginator(bdRevisiones, 20)
    try:
        revisiones = paginator.page(page)
    except PageNotAnInteger:
        revisiones = paginator.page(1)
    except EmptyPage:
        revisiones = paginator.page(paginator.num_pages)

    valores = []
    for revision in revisiones:
        guardia = {"id":revision.id, "usuario":revision.usuario, "fecha":revision.fecha, "comentarios":revision.comentarios.strip().replace(" [","\n["), "operatividad":revision.operatividad, "niveles":revision.niveles, "integridad":revision.integridad}
        fecha_anterior =  revision.fecha.replace(hour=0, minute=0, second=0)
        fecha_siguiente = fecha_anterior + timedelta(days=1)
        revisionCSN = RevisionGraficas.objects.using('rvra').filter(fecha__gte=fecha_anterior, fecha__lte=fecha_siguiente, grafica='csn')
        if len(revisionCSN) > 0:
            guardia["csn"] = {"fechaCSN": revisionCSN[0].fecha, "comentarios":revisionCSN[0].comentarios.strip().replace(" [","\n[")}
        corregidos = DatosCorregidosGraficas.objects.using('rvra').filter(fecha__gte=fecha_anterior, fecha__lte=fecha_siguiente)
        correccionesBD = []
        for dato in corregidos:
            correccionesBD.append({"usuario":dato.usuario, "fecha":dato.fecha, "tabla":dato.tabla, "elemento":dato.elemento})
        guardia["corregidos"] = correccionesBD
        valores.append(guardia)
    return render(
        request,
        "historico_guardias.html",
        {"guardiasRealizadas": valores, "paginas": revisiones}
    )

# CONSULTA GRAFICAS CONSULTA RAREX
@permission_required('auth.consulta_rarex')
def getMonitoriza(request):
    
    return render(
        request,
        "monitoriza.html",
        {}
    )


@permission_required('auth.consulta_rarex')
def getMonitorizaDatos(request):
    monitorizaCanales = list(ConfigMonitorizaCanales.objects.using('rvra').filter(isotopo_id=0).values('estacion_id','can_det_est','isotopo_id','estacion_id__nombre', 'can_det_est__nombre','isotopo__n_iso','med_anio_ant','med_amd_anio_ant','sd_activo','minutos_sd','sd_sms_env','niveles_activo','sms_enviado','factor_n1','factor_n2','factor_n3'))
    monitorizaDetectores = list(ConfigMonitorizaDetectores.objects.using('rvra').exclude(isotopo_id=0).values('estacion_id','can_det_est','isotopo_id','estacion_id__nombre', 'can_det_est__dir_datos','isotopo__n_iso','med_anio_ant','med_amd_anio_ant','sd_activo','minutos_sd','sd_sms_env','niveles_activo','sms_enviado','factor_n1','factor_n2','factor_n3'))
    monitoriza = monitorizaCanales+monitorizaDetectores

    return JsonResponse(monitoriza, safe=False)

# GENERACION DE INFORMES PARA CSN
@permission_required('auth.consulta_rarex')
def generacionInforme(request):
    if request.method == "POST":
        form = FechasInforme(request.POST)
        initial_date = datetime.strptime(form.data["date_inicio"], '%Y-%m-%d')
        final_date = datetime.strptime(form.data["date_fin"], '%Y-%m-%d')

        while initial_date <= final_date:
            generarInforme(initial_date)
            initial_date = initial_date + timedelta(days=1)

        botones = consultarBotonesGraficas('rvra')
        return render(
            request,
            "guardia_rare.html",
            {"desbloqueo":0, "red":"rvra", "listaBotones": botones}
        )
    else:

        return render(
            request,
            "generacionInforme.html",
            {}
        )


# METODO PARA ENVIAR UN MENSAJE A LOS USUARIOS INFORMADOS
def enviarMensajeMonitoriza(request):
    usuariosInformados = consultarTelefonosInformados()
    if (request.POST.get("checkboxCanalTelegram") =="on"):
        MensajesTelegram(id_area=1,id_estacion=None,fecha_hora_utc=datetime.now(pytz.timezone("Europe/Madrid")),mensaje="Información adicional",descripcion=request.POST.get('TextAreaMensajeEnvio'),icono='38',estado=0,id_telegram=-1001749964853,silenciar=0, confirmar=0).save(using='spd')
    
    if (request.POST.get("checkboxCanalSMS") =="on"):
        for telefono in usuariosInformados:
            MensajesSms(fecha_hora_utc=datetime.now(pytz.timezone("Europe/Madrid")),mensaje="Información adicional",descripcion=request.POST.get('TextAreaMensajeEnvio'),icono='38',estado=0,telefono=telefono,confirmar=0).save(using='spd')
    return JsonResponse({"informados":usuariosInformados}, safe=False)


def modificarSeguimiento(request, parametro, valor, estacion, canal, isotopo):
    if parametro == "tiempo":
        ConfigMonitoriza.objects.using('rvra').filter(estacion_id=estacion, can_det_est=canal, isotopo_id=isotopo).update(sd_activo=valor)
    elif parametro == "nivel":
        ConfigMonitoriza.objects.using('rvra').filter(estacion_id=estacion, can_det_est=canal, isotopo_id=isotopo).update(niveles_activo=valor)
    return JsonResponse({"modificado":"ok"}, safe=False)

# CREA UN INFORME DE UNA FECHA DADA PARA CSN
def generarInforme(fecha):
    workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + "/informesCSN/" + fecha.strftime("%d") + fecha.strftime("%m") + fecha.strftime("%Y") + '_CSN.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    column = 0
    worksheet.write(row, column, "***ESTADO DE LA RED A:")
    column += 1
    worksheet.write(row, column, fecha.strftime("%d") + "/" + fecha.strftime("%m") + "/"  + fecha.strftime("%Y"))
    column = 0
    row += 1
    worksheet.write(row, column, "***DATOS CONTROL***")
    row += 1
    numValoresTotales, totalOperatividad, operatividades = calcularOperatividad(fecha)
    worksheet.write(row, column, "#PARAMETRO")
    column += 1
    worksheet.write(row, column, "DATOS RECIBIDOS")
    column += 1
    worksheet.write(row, column, "PORCENTAJE DATOS RECIBIDOS")
    column = 0
    row += 1
    worksheet.write(row, column, "DATOS TOTALES GAMMA Y RADIOYODOS")
    column += 1
    worksheet.write(row, column, numValoresTotales)
    column += 1
    worksheet.write(row, column, str(round(totalOperatividad,2))+"%")
    column =0
    row += 1
    datos, errores, intranet = calcularErrores(fecha)
    worksheet.write(row, column, "DATOS RADIO:")
    column += 1
    worksheet.write(row, column, datos)
    column =0
    row += 1
    worksheet.write(row, column, "ERRORES DE RADIO:")
    column += 1
    worksheet.write(row, column, errores)
    column =0
    row += 1
    worksheet.write(row, column, "DATOS INTRANET:")
    column += 1
    worksheet.write(row, column, intranet)
    column =0
    row += 1
    worksheet.write(row, column, "***TASA DE DOSIS***")
    column += 1
    worksheet.write(row, column, "VALOR (uSv/h)")
    column += 1
    worksheet.write(row, column, "ERROR (uSv/h)")
    column = 0
    row += 1
    estaciones = [2,1,3,4,5,7,8,10,11,12,13,40,53,54,55,56,57]
    for e in estaciones:
        estacion, media, error = calcularDosisEstacion(fecha, e)
        worksheet.write(row, column, estacion)
        column += 1
        worksheet.write(row, column, media)
        column += 1
        worksheet.write(row, column, error)
        column = 0
        row += 1

    worksheet.write(row, column, "***ESPECTROMETRIA GAMMA ARROCAMPO***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ISOTOPO")
    column =+ 1
    worksheet.write(row, column, "ACTIVIDAD (Bq/m3)")
    column += 1
    worksheet.write(row, column, "ERROR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "AMD (Bq/m3)")
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1011, 14)
    worksheet.write(row, column, "YODO")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1011, 12)
    worksheet.write(row, column, "CESIO")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1

    worksheet.write(row, column, "***ESPECTROMETRIA GAMMA SAUCEDILLA PILOTO***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ISOTOPO")
    column =+ 1
    worksheet.write(row, column, "ACTIVIDAD (Bq/m3)")
    column += 1
    worksheet.write(row, column, "ERROR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "AMD (Bq/m3)")
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1001, 6)
    worksheet.write(row, column, "Bi-214 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 6)
    worksheet.write(row, column, "Bi-214 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 9)
    worksheet.write(row, column, "Co-60 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1001, 12)
    worksheet.write(row, column, "Cs-137 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 12)
    worksheet.write(row, column, "Cs-137 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1001, 14)
    worksheet.write(row, column, "I-131 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 14)
    worksheet.write(row, column, "I-131 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1001, 20)
    worksheet.write(row, column, "Pb-214 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 20)
    worksheet.write(row, column, "Pb-214 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 27)
    worksheet.write(row, column, "Zn-65 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1002, 31)
    worksheet.write(row, column, "Am-241 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1

    worksheet.write(row, column, "***ESPECTROMETRIA GAMMA ATALAYA***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ISOTOPO")
    column =+ 1
    worksheet.write(row, column, "ACTIVIDAD (Bq/m3)")
    column += 1
    worksheet.write(row, column, "ERROR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "AMD (Bq/m3)")
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1006, 6)
    worksheet.write(row, column, "Bi-214 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1007, 9)
    worksheet.write(row, column, "Co-60 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1006, 12)
    worksheet.write(row, column, "Cs-137 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1007, 12)
    worksheet.write(row, column, "Cs-137 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1006, 14)
    worksheet.write(row, column, "I-131 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1007, 14)
    worksheet.write(row, column, "I-131 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1006, 20)
    worksheet.write(row, column, "Pb-214 (Gas)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1007, 20)
    worksheet.write(row, column, "Pb-214 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1007, 27)
    worksheet.write(row, column, "Zn-65 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1007, 31)
    worksheet.write(row, column, "Am-241 (Part.)")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1

    worksheet.write(row, column, "***ESPECTROMETRIA GAMMA VALDECANAS***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ISOTOPO")
    column =+ 1
    worksheet.write(row, column, "ACTIVIDAD (Bq/m3)")
    column += 1
    worksheet.write(row, column, "ERROR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "AMD (Bq/m3)")
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1000, 14)
    worksheet.write(row, column, "YODO")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1000, 12)
    worksheet.write(row, column, "CESIO")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1

    worksheet.write(row, column, "***ESPECTROMETRIA GAMMA BADAJOZ***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ISOTOPO")
    column =+ 1
    worksheet.write(row, column, "ACTIVIDAD (Bq/m3)")
    column += 1
    worksheet.write(row, column, "ERROR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "AMD (Bq/m3)")
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1010, 14)
    worksheet.write(row, column, "YODO")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1
    actividad, error, amd = obtenerEspect(fecha, 1010, 12)
    worksheet.write(row, column, "CESIO")
    column += 1
    worksheet.write(row, column, actividad)
    column += 1
    worksheet.write(row, column, error)
    column += 1
    worksheet.write(row, column, amd)
    column = 0
    row += 1

    worksheet.write(row, column, "***AEROSOLES: ALFA***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ESTACION")
    column =+ 1
    worksheet.write(row, column, "VALOR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "DESVIACION (Bq/m3)")
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 4, 14)
    worksheet.write(row, column, "FREGENAL DE LA SIERRA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 10, 14)
    worksheet.write(row, column, "SERREJON")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 40, 14)
    worksheet.write(row, column, "SAUCEDILLA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1

    worksheet.write(row, column, "***AEROSOLES: BETA***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ESTACION")
    column =+ 1
    worksheet.write(row, column, "VALOR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "DESVIACION (Bq/m3)")
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 4, 15)
    worksheet.write(row, column, "FREGENAL DE LA SIERRA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 10, 15)
    worksheet.write(row, column, "SERREJON")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 40, 15)
    worksheet.write(row, column, "SAUCEDILLA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1

    worksheet.write(row, column, "***RADON EQUIVALENTE***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ESTACION")
    column =+ 1
    worksheet.write(row, column, "VALOR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "DESVIACION (Bq/m3)")
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 4, 16)
    worksheet.write(row, column, "FREGENAL DE LA SIERRA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 10, 16)
    worksheet.write(row, column, "SERREJON")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 40, 16)
    worksheet.write(row, column, "SAUCEDILLA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1

    worksheet.write(row, column, "***RADIOYODOS: FRACCION GASEOSA***")
    column = 0
    row += 1
    worksheet.write(row, column, "#ESTACION")
    column =+ 1
    worksheet.write(row, column, "VALOR (Bq/m3)")
    column += 1
    worksheet.write(row, column, "DESVIACION (Bq/m3)")
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 4, 17)
    worksheet.write(row, column, "FREGENAL DE LA SIERRA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 10, 17)
    worksheet.write(row, column, "SERREJON")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1
    media, desviacion = obtenerGammayRad(fecha, 40, 17)
    worksheet.write(row, column, "SAUCEDILLA")
    column += 1
    worksheet.write(row, column, media)
    column += 1
    worksheet.write(row, column, desviacion)
    column = 0
    row += 1

    workbook.close()

def subirChurro(request):
    handle_uploaded_file('fichero.dat', request.FILES['fichero_churro'])

    # Using readlines()
    file = open('fichero.dat', 'r')
    Lines = file.readlines()
    
    count = 0
    # Strips the newline character
    for line in Lines:
        memoria=line[0:1]
        muestra=line[10:13]
        analisis=line[14:16] 
        isotopo=line[16:22]     
        fecha_recogida_inicial=datetime.strptime(line[22:30], '%d-%m-%y').strftime('%Y-%m-%d')
        fecha_recogida_final=datetime.strptime(line[31:39], '%d-%m-%y').strftime('%Y-%m-%d')
        fecha_analisis=datetime.strptime(line[40:48], '%d-%m-%y').strftime('%Y-%m-%d')
        compartida=line[39:40]  
        
        numero_muestras=int(line[79:81])

        churro = ModelGeslabChurros(
            memoria = ModelGeslabMemorias.objects.using('geslab_churros').filter(codigo_memoria=memoria).get(),
            muestra = ModelGeslabMuestras.objects.using('geslab_churros').filter(codigo=muestra).get(),
            analisis =ModelGeslabAnalisis.objects.using('geslab_churros').filter(churro=analisis).get(),
            isotopo = ModelGeslabIsotopos.objects.using('geslab_churros').filter(descripcion=isotopo).get(),
            f_rec_ini = fecha_recogida_inicial,
            f_rec_fin = fecha_recogida_final,
            dias = 0,
            f_analisis = fecha_analisis,
            muestra_compartida = compartida,
            submuestras = numero_muestras
        )
        try:
            churro.actividad=float(line[49:58])
        except:
            print("sin actividad")
        try:
            churro.error=float(line[59:68])
        except:
            print("sin error")
        try:
            churro.lid=float(line[69:78])
        except:
            print("sin amd")
        
        
        if not ModelGeslabChurros.objects.using('geslab_churros').filter(memoria = churro.memoria, muestra = churro.muestra, analisis = churro.analisis, isotopo = churro.isotopo, f_rec_ini = churro.f_rec_ini, f_rec_fin = churro.f_rec_fin, f_analisis = churro.f_analisis).exists():
            churro.save(using='geslab_churros')
    

    return JsonResponse({}, safe=False)

def calcularDosisEstacion(dia, estacion):
    inicio = dia.replace(hour=0, minute=0, second=0)
    fin = dia.replace(hour=23, minute=59, second=59)
    media = EstGamYRadioyodos.objects.using('rvra').filter(fecha_hora__gte=inicio,fecha_hora__lte=fin,canales=1,estaciones=estacion,valido=1).aggregate(Avg('valor'))
    estacion = Estaciones.objects.using('rvra').filter(id=estacion)[0]
    if media["valor__avg"] is None:
        return estacion.nombre, "-", "-"
    else:
        return estacion.nombre, round(media["valor__avg"],3), round(media["valor__avg"]*0.15,3)

def obtenerEspect(dia, detector, isotopo):
    inicio = dia.replace(hour=0, minute=0, second=0)
    fin = dia.replace(hour=23, minute=59, second=59)
    estEspecGamma = EstEspecGamma.objects.using("rvra").filter(fecha_hora__gte=inicio ,fecha_hora__lte=fin, relacion_detectores_estacion_id=detector, isotopos_id=isotopo, valido=1).aggregate(Avg('actividad'), Avg('error'), Avg('amd'))
    if estEspecGamma["actividad__avg"] is None:
        return "-", "-", "-"
    elif estEspecGamma["error__avg"] is None:
        return "-", "-", "-"
    elif estEspecGamma["amd__avg"] is None:
        return "-", "-", "-"
    else:
        return round(estEspecGamma["actividad__avg"],3), round(estEspecGamma["error__avg"],3), round(estEspecGamma["amd__avg"],3)

def obtenerGammayRad(dia, estacion, canal):
    inicio = dia.replace(hour=0, minute=0, second=0)
    fin = dia.replace(hour=23, minute=59, second=59)
    estGamYRad = EstGamYRadioyodos.objects.using("rvra").filter(fecha_hora__gte=inicio ,fecha_hora__lte=fin, estaciones=estacion, canales=canal, valido=1).aggregate(Avg('valor'),StdDev('valor'))
    if estGamYRad["valor__avg"] is None:
        return "-", "-"
    elif estGamYRad["valor__stddev"] is None:
        return "-", "-"
    else:
        return round(estGamYRad["valor__avg"],3), round(estGamYRad["valor__stddev"],3)

def calcularErrores(dia):
    errores = HistoricoTotalDatos.objects.using("rvra").filter(dia=dia, can_det_est=1).aggregate(Sum('datos_radio'),Sum('errores_radio'),Sum('intranet'))
    return errores["datos_radio__sum"], errores["errores_radio__sum"], errores["intranet__sum"]




''' Funciones recursos generales '''
@permission_required('auth.laruex')
def consultarConexionesRemotas(request):
    usuario = AuthUser.objects.filter(id = request.user.id)[0]
    password = InformacionVncExportar.objects.filter(id_usuario = usuario)[0]
    conexiones = RelacionPersonalPcsRemoto.objects.filter(usuario=request.user.id)
    return render(
        request,
        "conexionesRemotas.html",
        {"conexiones":conexiones, "usuario":usuario.username, "password":password}
    )

@permission_required('auth.laruex')
def devolverConexionVNC(request, pc):
    usuario = AuthUser.objects.filter(id = request.user.id)[0]
    password = InformacionVncExportar.objects.filter(id_usuario = usuario)[0]
    ordenador = RelacionIpOrdenadores.objects.filter(id=pc)[0]


    contenidoFile = '<?xml version="1.0"?>\n<!DOCTYPE vncaddressbook [\n<!ENTITY COMPANY "RealVNC Ltd.">\n<!ELEMENT vncaddressbook (folder*,file*)>\n<!ATTLIST vncaddressbook password CDATA #IMPLIED>\n<!ELEMENT folder (folder*,file*)>\n<!ATTLIST folder name CDATA #REQUIRED>\n<!ELEMENT file (section*)>\n<!ATTLIST file name CDATA #REQUIRED>\n<!ELEMENT section (param*)>\n<!ATTLIST section name CDATA #REQUIRED>\n<!ELEMENT param (#PCDATA)>\n<!ATTLIST param name CDATA #REQUIRED>\n<!ATTLIST param value CDATA #REQUIRED>\n]>\n<vncaddressbook>\n<file name="'+ordenador.equipo
    contenidoFile = contenidoFile + '">\n<section name="Connection">\n<param name="Host" value="'+ordenador.ip+":"+ordenador.puerto_vnc
    contenidoFile = contenidoFile + '" />\n<param name="UserName" value="'+request.user.username
    contenidoFile = contenidoFile + '" />\n<param name="Password" value="'+password.pass_vnc_exportar
    contenidoFile = contenidoFile + '" />\n<param name="Encryption" value="Server" />\n<param name="SecurityNotificationTimeout" value="2500" />\n<param name="SelectDesktop" value="" />\n<param name="ProxyServer" value="" />\n<param name="ProxyType" value="" />\n<param name="ProxyUserName" value="" />\n<param name="ProxyPassword" value="" />\n<param name="SingleSignOn" value="1" />\n</section>\n<section name="Options">\n<param name="UseLocalCursor" value="1" />\n<param name="FullScreen" value="0" />\n<param name="RelativePtr" value="0" />\n<param name="FullColor" value="0" />\n<param name="ColorLevel" value="pal8" />\n<param name="PreferredEncoding" value="ZRLE" />\n<param name="AutoSelect" value="1" />\n<param name="Shared" value="1" />\n<param name="SendPointerEvents" value="1" />\n<param name="SendKeyEvents" value="1" />\n<param name="ClientCutText" value="1" />\n<param name="ServerCutText" value="1" />\n<param name="ShareFiles" value="1" />\n<param name="EnableChat" value="1" />\n<param name="EnableRemotePrinting" value="1" />\n<param name="ChangeServerDefaultPrinter" value="1" />\n<param name="PointerEventInterval" value="0" />\n<param name="PointerCornerSnapThreshold" value="30" />\n<param name="Scaling" value="Fit" />\n<param name="MenuKey" value="F8" />\n<param name="EnableToolbar" value="1" />\n<param name="AutoReconnect" value="1" />\n<param name="ProtocolVersion" value="" />\n<param name="AcceptBell" value="1" />\n<param name="ScalePrintOutput" value="1" />\n<param name="PasswordFile" value="" />\n<param name="VerifyId" value="2" />\n<param name="IdHash" value="" />\n<param name="WarnUnencrypted" value="1" />\n<param name="DotWhenNoCursor" value="1" />\n<param name="FullScreenChangeResolution" value="0" />\n<param name="UseAllMonitors" value="0" />\n<param name="Emulate3" value="0" />\n<param name="SendSpecialKeys" value="1" />\n<param name="SuppressIME" value="1" />\n<param name="Monitor" value="" />\n<param name="ColourLevel" value="pal8" />\n<param name="DisableWinKeys" value="1" />\n<param name="FullColour" value="0" />\n<param name="Protocol3.3" value="0" />\n</section>\n</file>\n</vncaddressbook>'
    if os.path.exists(settings.MEDIA_ROOT+"/conexion.xml"):
        os.remove(settings.MEDIA_ROOT+"/conexion.xml")
    f = open(settings.MEDIA_ROOT+"/conexion.xml", "a")
    f.write(contenidoFile)
    f.close()
    return FileResponse(open(settings.MEDIA_ROOT+"/conexion.xml", 'rb'))



@user_passes_test(lambda u: u.is_superuser)
def conexionesPorUsuario(request):
    conexiones = RelacionPersonalPcsRemoto.objects.filter().order_by('usuario')
    ordenadores = RelacionIpOrdenadores.objects.order_by('equipo').values_list('equipo',flat=True).distinct()
    usuarios = AuthUser.objects.order_by('username').filter(is_active=True).values_list('username',flat=True).distinct()
    return render(
        request,
        "conexionesPorUsuario.html",
        {"conexiones":conexiones,"ordenadores":ordenadores,"usuarios":usuarios}
    )


@user_passes_test(lambda u: u.is_superuser)
def conexionesPorEquipo(request):
    conexiones = RelacionPersonalPcsRemoto.objects.order_by('id_ordenador')
    ordenadores = RelacionIpOrdenadores.objects.order_by('equipo').values_list('equipo',flat=True).distinct()
    usuarios = AuthUser.objects.order_by('username').filter(is_active=True).values_list('username',flat=True).distinct()
    return render(
        request,
        "conexionesPorEquipo.html",
        {"conexiones":conexiones,"ordenadores":ordenadores,"usuarios":usuarios}
    )

@user_passes_test(lambda u: u.is_superuser)
def nuevaRelacionEquiposRemotosParaEquipo(request):
    ordenador = RelacionIpOrdenadores.objects.filter(equipo=request.POST.get('selectEquipo'))[0]
    for valor in request.POST:
        if "checkUsuario" in valor:
            usuario = AuthUser.objects.filter(username=request.POST.get(valor))[0]
            if not RelacionPersonalPcsRemoto.objects.filter(id_ordenador=ordenador, usuario=usuario).exists():
                RelacionPersonalPcsRemoto(id_ordenador=ordenador, usuario=usuario).save()
    return JsonResponse({"valor":"a"}, safe=False)


@user_passes_test(lambda u: u.is_superuser)
def nuevaRelacionEquiposRemotosParaUser(request):
    usuario = AuthUser.objects.filter(username=request.POST.get('selectUsuario'))[0]
    for valor in request.POST:
        if "checkPC" in valor:
            ordenador = RelacionIpOrdenadores.objects.filter(equipo=request.POST.get(valor))[0]
            if not RelacionPersonalPcsRemoto.objects.filter(id_ordenador=ordenador, usuario=usuario).exists():
                RelacionPersonalPcsRemoto(id_ordenador=ordenador, usuario=usuario).save()
    return JsonResponse({"valor":"a"}, safe=False)


@permission_required('auth.guardia_rarex')
def simulacrosRealizados(request):
    simulacros = SimulacrosRarex.objects.using('rvra').exclude(estado=0).order_by('-id')
    proximo = SimulacrosRarex.objects.using('rvra').filter(estado=0).get()
    return render(
        request,
        "simulacrosRealizados.html",
        {"simulacros":simulacros, "proximoSimulacro":proximo}
    )

@permission_required('auth.guardia_rarex')
def desactivarSimulacro(request):
    simulacro = SimulacrosRarex.objects.using('rvra').filter(estado=1).get()
    if simulacro.inicio_nivel1:
        simulacro.minutos_nivel1 = compararFechasGMT2(simulacro.inicio_nivel1)
    if simulacro.inicio_nivel2:
        simulacro.minutos_nivel2 = compararFechasGMT2(simulacro.inicio_nivel2)
    if simulacro.inicio_nivel3:
        simulacro.minutos_nivel3 = compararFechasGMT2(simulacro.inicio_nivel3)
    simulacro.estado = 2
    simulacro.exitoso = 1
    simulacro.analista_confirmacion = request.user.id
    simulacro.save(using='rvra')
    nombreAnalistaGuardia = AuthUser.objects.filter(id=simulacro.analista_guardia)[0].first_name + " " + AuthUser.objects.filter(id=simulacro.analista_guardia)[0].last_name
    nombreAnalistaConfirmacion = AuthUser.objects.filter(id=simulacro.analista_confirmacion)[0].first_name + " " + AuthUser.objects.filter(id=simulacro.analista_confirmacion)[0].last_name
    return render(
        request,
        "informeSimulacro.html",
        {"simulacro":simulacro, "analista_guardia": nombreAnalistaGuardia, "analista_confirmacion": nombreAnalistaConfirmacion}
    )

@permission_required('auth.guardia_rarex')
def informeSimulacro(request, id):
    simulacro = SimulacrosRarex.objects.using('rvra').filter(id=id).get()
    nombreAnalistaGuardia = AuthUser.objects.filter(id=simulacro.analista_guardia)[0].first_name + " " + AuthUser.objects.filter(id=simulacro.analista_guardia)[0].last_name
    nombreAnalistaConfirmacion = AuthUser.objects.filter(id=simulacro.analista_confirmacion)[0].first_name + " " + AuthUser.objects.filter(id=simulacro.analista_confirmacion)[0].last_name
    return render(
        request,
        "informeSimulacro.html",
        {"simulacro":simulacro, "analista_guardia": nombreAnalistaGuardia, "analista_confirmacion": nombreAnalistaConfirmacion}
    )


def getPruebaGrafica(request):
    return render(
        request,
        "grafica.html",
        {}
    )

