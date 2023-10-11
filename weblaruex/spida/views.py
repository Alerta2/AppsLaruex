from django.db.models.expressions import Value
from django.db.models.fields import IntegerField
from os import name
from typing import Text
from django.db.models import query
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.models import CharField, Value
from django.conf import settings
from django.http import FileResponse

from .models import Estaciones, Eventos, UmbralesRios, UltimosValores, UltimasImagenes, SucesosInundacion, InformesTrimestrales, Canales, AdjuntosEventos,  DocumentacionAdjunto
import locale
from datetime import datetime, timedelta
from dateutil import tz


import simplejson, json
from django.http import JsonResponse
import base64

from .forms import subidaInforme, FormFechaIniFinEvento
from django.apps import apps

import requests

import cv2
import pytz



def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

def presentacionSpida(request):
    user=request.user
    return render(request,"presentacionSpida.html",{"user":user})


'''Pagina de inicio (Portada Web)'''
def inicioSpida(request):
    user=request.user
    return render(request,"portadaSpida.html",{"user": user})


'''Mapa principal publico SPIDA'''
#@permission_required('auth.spida_documentacion')
def getMapaSpida(request):
    permissions = request.user.get_user_permissions()
    if 'auth.spida_documentacion' in permissions:
        print("Usuario logueado y con permiso spida documentacion")
    else:
        print("Usuario no logueado o sin permisos")
    user = request.user
    
   

    return render(request,"mapaSpida.html",{"user": user})

def getHorariosSol(request):
     #Utilizo esto para calcular los tiempos de amanecer, atardecer, amanecer y anochecer.
    peticionHttp = requests.get('http://api.sunrise-sunset.org/json?lat=39.16667&lng=-6.16667&formatted=0')
    result = peticionHttp.json()
    return JsonResponse(result, safe=False)


def getCieloAemet(request):
    now = datetime.now()
    cont=0
    #print("URL CIELO AEMET: ",'http://www.aemet.es/es/api-eltiempo/variables/eCielo/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+02:00/01/D+'+str(cont)+'/70')
    peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/variables/eCielo/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+02:00/01/D+'+str(cont)+'/70')
    while len(peticionHttpAemet.text)==0 and cont<10:
        cont=cont+1
        peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/variables/eCielo/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+02:00/01/D+'+str(cont)+'/70')

    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)


def getImagenesPreAcumAemet(request):
    peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/modelo-harmonie/timeline/61/PB/1%20hora')
    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)

def getImagenesRadar(request):
    peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/radar/timeline/RN1/PB')
    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)


'''Login Usuarios Spida'''
def getLoginSpida(request):
    user = request.user
    return render(request,"registration/login.html",{"user": user})

'''Documentcion Eventos Spida'''
''' 1. Compruebo si se trata de un metodo POST
    2. Si es Correcto: 
        2.1 Compruebo si se trata de un formulario de tipo fecha del Evento (bien para crear un nuevo evento o para darlo por concluido)
        - Si se trata de un nuevo evento, realizo las comprobaciones necesarias para asegurarme de que no existe un evento de inundación 
          con la misma fecha de inicio
        - Si de lo contrario es para dar por terminado un evento ya existente, compruebo que la fecha final del evento es mayor o igual
          que la fecha de inicio del mismo
        2.2 Compruebo si se trata de un formulario de ficheros adjuntos
        - Recorremos los ficheros adjuntados y los almacenamos en la carpeta media/SPIDA así como en la base de datos
    3. Si no se trata de un metodo POST:
        3.1 Cargo simplemente el HTML
        '''
def getDocumentsEventos(request):
    user = request.user

    if request.method == 'POST': # 1.       
        #print("METHOD POST", request.POST, request.FILES) # 2.   
        form = FormFechaIniFinEvento(request.POST) 
        if form.is_valid(): # 2.1
            info=request.POST # get info del POST
            idEvento = int(info.get("idEvento")) # get id del evento
            tipoFechaEvento = info.get("tipoFecha") # get tipo de fecha del evento (inicio: para crear un nuevo evento, fin: para cerrar el evento)
            tituloEvento = info.get("titulo") # get titulo del evento
            fechaEvento =datetime.strptime(info.get("fecha"),'%d/%m/%Y')  # get fecha (inicio o fin) del evento

            if tipoFechaEvento=="inicio": # Si tipo de fecha = inicio ... se quiere crear un nuevo evento
                if Eventos.objects.using('spida_web').filter(fecha_hora_inicio=fechaEvento).exists(): # Compruebo si ya existe un evento con la misma fecha de inicio. Si existe ...
                    print("Ya existe un evento con fecha de inicio", fechaEvento)
                    
                    eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio') #obtengo la lista de eventos actualizados
                    return render(request,"docu-eventos.html", {"user": user,"Eventos":eventos, "form": FormFechaIniFinEvento(), "MensajeError": "Ya existe un evento con fecha "+info.get("fecha")})
                
                else: # Si no existe ....
                    print("Se va a crear un nuevo evento con fecha de inicio", fechaEvento)
                    new_entry = Eventos(titulo=tituloEvento, fecha_hora_inicio=fechaEvento, estado='0') # Creo la query para almacenarlo en la base de datos
                    new_entry.save(using='spida_web') # Guardo el nuevo evento en la base de datos
                    print("El nuevo evento ha sido cargado en la base de datos de forma satisfactoria")
                    
                    eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio') #obtengo la lista de eventos actualizados
                    return render(request,"docu-eventos.html", {"user": user, "Eventos":eventos, "form": FormFechaIniFinEvento(), "MensajeSuccess": 'Ha sido creado un nuevo evento con fecha ' + info.get("fecha")})
            
            elif tipoFechaEvento=="fin": # Si tipo de fecha = fin ... se quiere dar por terminado un evento ya existente
                
                query=Eventos.objects.using('spida_web').filter(id_evento=idEvento)  
                if query.exists(): # Si el evento existe en la base de datos 
                    if (query.first().fecha_hora_inicio).replace(tzinfo=None)<=fechaEvento: # Y ademas la fecha de finalizacion del evento es mayor o igual a la fecha de inicio
                        Eventos.objects.using('spida_web').filter(id_evento=idEvento).update(titulo=tituloEvento, fecha_hora_fin=fechaEvento, estado='1') # Le añado la fecha fin del evento y cambio su estado ('0': Abierto, '1':Cerrado)
                        
                        eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio') #obtengo la lista de eventos actualizados
                        return render(request,"docu-eventos.html", {"user": user, "Eventos":eventos, "form": FormFechaIniFinEvento(),"MensajeSuccess": 'Evento de inundación concluido'})
                    
                    else: # Si la fecha de finalizacion del evento no es mayor o igual a la fecha de inicio del mismo
                        eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio') #obtengo la lista de eventos actualizados
                        return render(request,"docu-eventos.html", {"user": user, "Eventos":eventos, "form": FormFechaIniFinEvento(), "MensajeError": "La Fecha de finalización del evento de inundación no puede ser menor que la fecha de comienzo de éste"})
                else:
                    eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio') #obtengo la lista de eventos actualizados
                    return render(request,"docu-eventos.html", {"user": user,  "Eventos":eventos, "form": FormFechaIniFinEvento(),"MensajeError": "No se puede cerrar el evento con ID "+idEvento+" porque no se encuentra registrado en la base de datos"})
        
        elif 'docspida' in request.FILES: # 2.2
            print("Se ha adjuntado nueva documentación")

            info=request.POST # get info del POST
            idEvento = info.get("idEvento") # get id del evento
            tituloAdjunto = info.get("titulo") # get titulo del adjunto
            descripcionAdjunto =info.get("descripcion") # get descripcion del adjunto 
            fecha_hora = datetime.now()

            #Añado el nuevo adjunto
            Evento = Eventos.objects.using('spida_web').filter(id_evento=int(idEvento)).first()
            new_entry = AdjuntosEventos(id_evento=Evento, titulo_adjunto=tituloAdjunto, id_usuario=user.id, fecha_hora_local=fecha_hora, descripcion=descripcionAdjunto) # Creo la query para almacenarlo en la base de datos
            new_entry.save(using='spida_web') # Guardo el nuevo evento en la base de datos
            idAdjunto = new_entry.id_adjunto
        
            listFicherosAdjuntos = request.FILES.getlist('docspida') # get ficheros adjuntados
            
            for fichero in listFicherosAdjuntos: # recorro los ficheros adjuntos 
                print("Fichero: ",fichero.name.split('.')[0], fichero.name.split('.')[-1], "Size:", fichero.size)
                nombrefichero=(fichero.name.split('.')[0]).replace(" ", "_") # nombre del fichero
                extfichero=fichero.name.split('.')[-1] # extension del fichero (tipo: Ejemplo pdf, doc, jpg etc.)
                sizefichero=fichero.size # tamaño del fichero (En bytes)
                CargarFicheroAdjuntado(fichero,idEvento,idAdjunto,nombrefichero,extfichero,sizefichero) # Almaceno cada fichero en media/SPIDA y en la base de datos

            eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio')
            return render(request,"docu-eventos.html", {"user": user, "Eventos":eventos, "form": FormFechaIniFinEvento(), "MensajeSuccess": 'Se ha adjuntado nueva documentación'}) 
        
        else:
            print("No se encuentra ningun metodo POST de los conocidos")
            
            eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio')
            return render(request,"docu-eventos.html", {"user": user, "Eventos":eventos, "form": FormFechaIniFinEvento()}) 
                
    else:
        eventos=Eventos.objects.using('spida_web').order_by('estado','-fecha_hora_inicio')
        return render(request,"docu-eventos.html", {"user": user, "Eventos":eventos, "form": FormFechaIniFinEvento()})    

'''Guardar Documentacion Adjuntada de los Eventos Spida'''
def CargarFicheroAdjuntado(fichero, idEvento, idAdjunto, nombreFichero, extensionFichero, sizeFichero):
    fecha_hora=datetime.now()
    rutaFichero= '/SPIDA/EIS_'+ str(idEvento).zfill(4)+'_'+fecha_hora.strftime("%Y%m%d%H%M%S")+nombreFichero+'.'+str(extensionFichero) # ruta donde va a ser guardado el fichero adjuntado
    print("Solicito escribir fichero ", fichero)
    
    with open(settings.MEDIA_ROOT +rutaFichero, 'wb+') as destination:
        print("Escribiendo fichero")
        for chunk in fichero.chunks():
            destination.write(chunk)
        
        Adjunto = AdjuntosEventos.objects.using('spida_web').filter(id_adjunto=int(idAdjunto)).first()
        new_entry = DocumentacionAdjunto(id_adjunto=Adjunto,nombre=nombreFichero, extension=extensionFichero, ruta=rutaFichero, size = sizeFichero) # Creo la query para almacenarlo en la base de datos
        new_entry.save(using='spida_web') # Guardo el nuevo evento en la base de datos
        
        

'''Sucesos Spida'''
def getSucesosSpida(request):
    user = request.user
    sucesos=SucesosInundacion.objects.using('spida_web').order_by('-fecha_hora_local')

    listaSucesos=[]
    for suceso in sucesos:
        sucesoAuxiliar={}
        sucesoAuxiliar['id']=suceso.id_suceso
        sucesoAuxiliar['titulo']=suceso.rotulo
        sucesoAuxiliar['descripcion']=suceso.descripcion
        sucesoAuxiliar['fecha']=(suceso.fecha_hora_local).strftime("%d %B, %Y")
        sucesoAuxiliar['imagen']=base64.b64encode(suceso.imagen).decode()
        listaSucesos.append(sucesoAuxiliar)

    return render(request,"sucesosSpida.html",{"user": user, "Sucesos":listaSucesos})
    #return JsonResponse(jsonSucesosSpida, safe=False)

'''Documentacion privada Spida'''
@permission_required('auth.spida_documentacion', login_url='/spida/login/')
def getDocumentacionSpida(request):
    user = request.user
    return render(request,"documentsSpida.html",{"user": user})

'''Informes trimestrales Spida'''
@permission_required('auth.spida_inf_trimestrales')
def getInformesTrimestrales(request):
    user = request.user
    if request.method == 'POST':        
        #print("METHOD POST", request.POST, request.FILES) # 2.          
        if 'docInformeTrimestral' in request.FILES: # 2.2
            print("Se ha adjuntado nueva documentación")

            info=request.POST # get info del POST
            numCuatrimentre=int(info.get("cuatrimentre")) # get cuatrimentre del informe valorado (1 (Enero a Marzo), 2 (Abril a Junio), 3 (Julio a Septiembre) o 4 (Octubre a Diciembre))
            yearCuatrimestre=int(info.get("year"))
            first_date = datetime(yearCuatrimestre, 3 * numCuatrimentre - 2, 1)
            last_date = datetime(yearCuatrimestre + 3 * numCuatrimentre // 12, 3 * numCuatrimentre % 12  + 1, 1) + timedelta(days=-1)
            print("Cuatrimentre: ",numCuatrimentre,"Fecha Ini: ",first_date,"Fecha fin: ",last_date)

            #Añado el nuevo informe trimestral a la base de datos
            if InformesTrimestrales.objects.using('spida_web').filter(fecha_hora_local_inicio=first_date, fecha_hora_local_fin=last_date).exists():
                print("Ya existe un informe para este cuatrimestre")
                return render(request,"informesSpida.html",{"user": user})
            else:
                InformeTrimestral = request.FILES.getlist('docInformeTrimestral')[0] # get pdf adjuntado
                nombreInformeTrimestral=(InformeTrimestral.name).replace(" ", "_") # nombre del fichero
                sizeInformeTrimestral=InformeTrimestral.size # tamaño del pdf (En bytes)
                rutaInformeTrimestral = '\SPIDA\INFORMES_TRIMESTRALES\ITS_'+str(yearCuatrimestre)+'_'+str(numCuatrimentre)+'C'+'.pdf'

                print(InformeTrimestral, nombreInformeTrimestral, sizeInformeTrimestral, rutaInformeTrimestral)
                
                with open(settings.MEDIA_ROOT+rutaInformeTrimestral, 'wb+') as destination:
                    print("Escribiendo fichero")
                    for chunk in InformeTrimestral.chunks():
                        destination.write(chunk)
                
                new_entry = InformesTrimestrales(id_cuatrimestre=numCuatrimentre, year=yearCuatrimestre, fecha_hora_local_inicio=first_date, fecha_hora_local_fin=last_date, nombre=nombreInformeTrimestral, size=sizeInformeTrimestral, ruta=rutaInformeTrimestral, fecha_hora_subida=datetime.now()) # Creo la query para almacenarlo en la base de datos
                new_entry.save(using='spida_web') # Guardo el nuevo evento en la base de datos
      
    return render(request,"informesSpida.html",{"user": user})

def getListadoInformesTrimestrales(request):
    user = request.user

    listInformesTrimestrales = InformesTrimestrales.objects.using('spida_web').order_by('-fecha_hora_subida').extra(
    select={
        'id':'id_informe',
        'cuatrimestre' : 'id_cuatrimestre',
        'year' : 'year',
        'fecha_ini' : 'fecha_hora_local_inicio',
        'fecha_fin' : 'fecha_hora_local_fin',
        'size' : 'size',
        'path' :'ruta',
        'fecha_subida':'fecha_hora_subida'
    }
    ).values('id', 'cuatrimestre', 'year', 'fecha_ini', 'fecha_fin', 'size', 'path', 'fecha_subida')

    return JsonResponse(list(listInformesTrimestrales), safe=False)

'''Abre automaticamente en una nueva ventana un informe trimestral'''
@permission_required('auth.spida_inf_trimestrales')
def OpenInformeTrimestral(request):
    user = request.user
    idInformeTrimestral = request.GET.get('informe','')
    contenido = InformesTrimestrales.objects.using('spida_web').filter(id_informe=idInformeTrimestral)[0]
    return FileResponse(open(settings.MEDIA_ROOT + contenido.ruta, 'rb'), content_type='application/pdf')#force-download

'''Descarga automaticamente un informe trimestral'''
@permission_required('auth.spida_inf_trimestrales')
def DownloadInformeTrimestral(request):
    user = request.user
    idInformeTrimestral = request.GET.get('informe','')
    contenido = InformesTrimestrales.objects.using('spida_web').filter(id_informe=idInformeTrimestral)[0]
    return FileResponse(open(settings.MEDIA_ROOT + contenido.ruta, 'rb'), content_type='application/force-download')

@permission_required('auth.spida_documentacion')
def DownloadDocuEventos(request, idDoc):
    user=request.user 
    documento=DocumentacionAdjunto.objects.using('spida_web').filter(id_documento=idDoc)[0]

    return FileResponse(open(settings.MEDIA_ROOT + documento.ruta , 'rb'),  as_attachment = True, filename = documento.nombre +"."+ documento.extension, content_type='application/force-download')

''''Abre automaticamente en una nueva ventana el Protocolo de Actuación SPIDA-INUNCAEX'''
@permission_required('auth.spida_protocolo')
def OpenProcoloto(request):
    user = request.user
    urlProtocolo = '/SPIDA/PROTOCOLO/PROTOCOLO_SPIDA_INUNCAEX.pdf'
    return FileResponse(open(settings.MEDIA_ROOT + urlProtocolo, 'rb'), content_type='application/pdf')

'''Protocolo de Actuación Spida'''
def getProtocoloActuacion(request):
    user = request.user
    return render(request,"protocoloSpida.html",{"user": user})

'''def prueba(request):
    user = request.user
    if request.method == 'POST':
        #print("PRUEBA FILE",request.POST)
        #print("FILES", request.FILES)     
        LISTFILES=request.FILES.getlist('docspida')
        #if form.is_valid():
        #    handle_uploaded_file(request.FILES['file'])
        for fichero in LISTFILES:
            #print("prueba",fichero.name.split('.')[0], fichero.name.split('.')[-1], type(fichero))
            nombrefichero=fichero.name.split('.')[0]
            extfichero=fichero.name.split('.')[-1]
            handle_uploaded_file(fichero, '0', extfichero)
    return render(request,"prueba.html",{"user": user, "form":FileFieldForm()})'''


'''Datos: Estaciones Spida Monitorizadas y Visualizadas'''
def getEstaciones(request):
    user = request.user
    permissions = user.get_user_permissions()

    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    #if 'auth.spida_documentacion' in permissions:
    if user.is_anonymous:
        estaciones=UmbralesRios.objects.using('spida_web').filter(id_estacion__visualizar=1).filter(id_estacion__monitorizar=1).filter(id_estacion__id_red=1)
        ultimos_valores = UltimosValores.objects.using('spida_web').filter(id_canal=100).filter(id_estacion__visualizar=1).filter(id_estacion__monitorizar=1).filter(id_estacion__id_red=1)
    else:
        estaciones=UmbralesRios.objects.using('spida_web').filter(id_estacion__visualizar=1).filter(id_estacion__monitorizar=1)
        ultimos_valores = UltimosValores.objects.using('spida_web').filter(id_canal=100).filter(id_estacion__visualizar=1).filter(id_estacion__monitorizar=1)
        #print("HOLA TIENE PERMISOS")
        #for est in estaciones:
        #    print(est)
    
    listaEstaciones=[]
    for estacion in estaciones:
        estacionAuxiliar={}
        estacionAuxiliar["id"]=estacion.id_estacion.id_estacion
        estacionAuxiliar["nombre"]=estacion.id_estacion.nombre
        estacionAuxiliar["red"]=estacion.id_estacion.id_red.id_red
        estacionAuxiliar["map_lat"]=estacion.id_estacion.sensor_lat
        estacionAuxiliar["map_lon"]=estacion.id_estacion.sensor_lon
        estacionAuxiliar["widget"]=estacion.id_estacion.widget_aemet
        estacionAuxiliar["N1"]=round(estacion.limite_n1*(estacion.limite_desbordamiento/100),2)
        estacionAuxiliar["N2"]=round(estacion.limite_n2*(estacion.limite_desbordamiento/100),2)
        estacionAuxiliar["N3"]=round(estacion.limite_n3*(estacion.limite_desbordamiento/100),2)
        estacionAuxiliar["valor"]=None
        estacionAuxiliar["fecha_utc"]=None
        estacionAuxiliar["fecha_local"]=None
        estacionAuxiliar["estado"]=None

        for valor in ultimos_valores:
            if valor.id_estacion.id_estacion==estacion.id_estacion.id_estacion:
                estacionAuxiliar["valor"]=valor.valor
                locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
                estacionAuxiliar["fecha_utc"]=valor.fecha_hora_utc.strftime("%d %B a las %H:%M h")
                estacionAuxiliar["fecha_local"]=valor.fecha_hora_local.strftime("%Y-%m-%d %H:%M:%S") #.strftime("%d %B a las %H:%M h")
                break

        fechaActual=(datetime.now()+timedelta(hours=-2)).strftime("%Y-%m-%d %H:%M:%S")
         
        if estacionAuxiliar["fecha_local"] != None and estacionAuxiliar["valor"]!=None and estacionAuxiliar["N1"]>0 and estacionAuxiliar["N2"]>0 and estacionAuxiliar["N3"]>0:
            #if estacionAuxiliar["fecha_local"]<(datetime.now()+timedelta(hours=-2)).strftime("%d %B a las %H:%M h"):
            if  datetime.strptime(estacionAuxiliar["fecha_local"], "%Y-%m-%d %H:%M:%S")< datetime.strptime(fechaActual, "%Y-%m-%d %H:%M:%S"):
                estacionAuxiliar["estado"]=-1
            else:
                if estacionAuxiliar["valor"] >= estacionAuxiliar["N3"]:
                    estacionAuxiliar["estado"]=3
                else:
                    if estacionAuxiliar["valor"]>=estacionAuxiliar["N2"]:
                        estacionAuxiliar["estado"]=2
                    elif estacionAuxiliar["valor"]>=estacionAuxiliar["N1"]:
                        estacionAuxiliar["estado"]=1
                    else:
                        estacionAuxiliar["estado"]=0
            estacionAuxiliar["fecha_local"]= (datetime.strptime(estacionAuxiliar["fecha_local"], "%Y-%m-%d %H:%M:%S")).strftime("%d %B a las %H:%M h")
        


        listaEstaciones.append(estacionAuxiliar)
        #print(estacionAuxiliar["id"],estacionAuxiliar["nombre"],estacionAuxiliar["N1"], estacionAuxiliar["N2"],estacionAuxiliar["N3"],estacionAuxiliar["estado"], estacionAuxiliar["fecha_local"], )

    cols=['id','nombre','red','widget','N1','N2', 'N3','valor','fecha_utc','fecha_local','estado']
    datosGeoJson = list_to_geojson(listaEstaciones,cols)
    return  JsonResponse(datosGeoJson, safe=False)

'''Recibe una lista de estaciones y la convierte en un json'''
def list_to_geojson(list, properties,lat='map_lat',lon='map_lon'):
    geojson={
        'type':'FeatureCollection',
        'features':[]
    }
    for estacion in list:
        feature={
            'type':'Feature',
            'properties':{},
            'geometry':{
                'type' : 'Point',
                'coordinates' : []
            }
        }
        feature['geometry']['coordinates']=[estacion[lon],estacion[lat]]
        for propiedad in properties:
            feature['properties'][propiedad]=estacion[propiedad]
        geojson['features'].append(feature)
    return geojson


def getMiniaturasSpida(request):
    user = request.user
    imagenes = UltimasImagenes.objects.using('spida_web')

    listaImagenes=[]
    for imagen in imagenes:
        imagenAuxiliar={}
        imagenAuxiliar['id']=imagen.id_estacion.id_estacion
        imagenAuxiliar['nombre']=imagen.id_estacion.nombre
        imagenAuxiliar['lat']=imagen.id_estacion.sensor_lat
        imagenAuxiliar['lng']=imagen.id_estacion.sensor_lon
        imagenAuxiliar['fecha_hora']=imagen.fecha_hora_local.strftime("%d %B a las %H:%M h")
        imagenAuxiliar['camara']=imagen.id_camara
        imagenAuxiliar['imagen']=base64.b64encode(imagen.miniatura).decode()
        
        listaImagenes.append(imagenAuxiliar)

    jsonImagenesSpida = json.dumps(listaImagenes, default=myconverter)
    return JsonResponse(jsonImagenesSpida, safe=False)

'''Devuelve una imagen concreta'''
def getImagenSpida(request):
    user = request.user
    result = {}
    
    idEstacion = request.GET.get('estacion','')
    idCamara = request.GET.get('camara','')

    if idEstacion == '' or idCamara == '':
        return JsonResponse(result, safe=False)
    
    idEstacion = int(idEstacion)
    idCamara = int(idCamara)

    imagen = UltimasImagenes.objects.using('spida_web').filter(id_estacion=idEstacion,id_camara=idCamara).first()
    if imagen is not None:
        result['estacion']=imagen.id_estacion.nombre
        result['camara']=imagen.id_camara
        result['fecha_hora']=imagen.fecha_hora_local.strftime("%d %B a las %H:%M h")
        result['imagen']=base64.b64encode(imagen.imagen).decode()
         
    return JsonResponse(result, safe=False)

def getListadoDocEvento(request):
    user = request.user
    listaAdjutoEvento = []
    #print(type(listaDocEvento))
    idEvento=request.GET.get('evento','')

    listAdjuntos = AdjuntosEventos.objects.using('spida_web').filter(id_evento=idEvento).order_by('-fecha_hora_local')
    for adjunto in listAdjuntos:
        docAuxiliar={}
        docAuxiliar['id']=str(adjunto.id_adjunto)
        docAuxiliar['evento']=str(adjunto.id_evento.id_evento)

        docAuxiliar['doc']=adjunto.nombre
        docAuxiliar['ext']=adjunto.extension
        docAuxiliar['fecha_subida']=adjunto.fecha_hora_local#doc.fecha_hora_local.strftime('%d-%m-%Y %H:%M')
        if adjunto.id_estacion==None:
            docAuxiliar['estacion']=""
        else:
            docAuxiliar['estacion']=str(adjunto.id_estacion.nombre)

        if adjunto.descripcion==None:
            docAuxiliar['descripcion']=""
        else:
            docAuxiliar['descripcion']=str(adjunto.descripcion)

        #print( docAuxiliar['id'],  docAuxiliar['evento'],  docAuxiliar['doc'],  docAuxiliar['ext'],  docAuxiliar['estacion'],  docAuxiliar['descripcion'], type(doc.fecha_hora_local))
        
        listAdjuntos.append(docAuxiliar)
    
    #print(type(listaDocEvento))

    #jsonDocs = json.dumps(listaDocEvento, default=myconverter)
    #jsonDocs = json.dumps(listaDocEvento,default=myconverter)
    return JsonResponse(listaAdjutoEvento, safe=False)

def getListadoAdjuntosEvento(request):
    user = request.user
    listaAdjutoEvento = []
    idEvento=request.GET.get('evento','')

    listAdjuntos = AdjuntosEventos.objects.using('spida_web').filter(id_evento=idEvento).order_by('-fecha_hora_local')

    for adjunto in listAdjuntos:
        adjuntAuxiliar={}
        adjuntAuxiliar['id']=str(adjunto.id_adjunto)
        adjuntAuxiliar['evento']=str(adjunto.id_evento.id_evento)
        adjuntAuxiliar['titulo']=str(adjunto.titulo_adjunto)
        adjuntAuxiliar['usuario']=(get_user_model().objects.get(id=adjunto.id_usuario)).get_full_name()
        adjuntAuxiliar['fecha_subida']=adjunto.fecha_hora_local # doc.fecha_hora_local.strftime('%d-%m-%Y %H:%M')
        adjuntAuxiliar['descripcion']=adjunto.descripcion
        listaAdjutoEvento.append(adjuntAuxiliar)

    return JsonResponse(listaAdjutoEvento, safe=False)

def pruebauser(usuario):
    print("HA ENTRADO AQUI",usuario, print(usuario))
    #print((get_user_model().objects.get(id=usuario)).get_full_name())
    return (get_user_model().objects.get(id=usuario)).get_full_name()
'''Obtiene el listado de Documentos de un Adjunto'''
def getListadoDocumentosAdjuntoEvento(request):
    user = request.user
    idAdjunto=request.GET.get('adjunto','')

    listDocs = DocumentacionAdjunto.objects.using('spida_web').filter(id_adjunto=idAdjunto).order_by('extension').extra(
    select={
        'id':'id_documento',
        'adjunto' : 'id_adjunto',
        'doc' : 'nombre',
        'ext' : 'extension',
        'size' : 'size',
        'path' : 'ruta'
    }
    ).values('id', 'adjunto', 'doc', 'ext', 'size', 'path')

    return JsonResponse(list(listDocs), safe=False)

'''Datos: Valores del canal las anteriores 24 horas'''
def getValores24h(request):
    
    user = request.user
    result = {}
    
    Estacion = request.GET.get('estacion','')
    Canal = request.GET.get('canal','')

    if Estacion == '' or Canal == '':
        return JsonResponse(result, safe=False)
    
    IdEst = int(Estacion)
    IdCan = int(Canal)

    # Parche estacion Badajoz
    if IdEst == 8010 and IdCan == 301:
        IdEst = 7010
        IdCan = 301
    
    # Parche precipitacion Caceres
    if IdEst == 7013 and IdCan == 301:
        IdEst = 1110
        IdCan = 301
        estacion = Estaciones.objects.using('spida_web').filter(id_estacion=IdEst,
                                                            monitorizar=1).first()
    else:
        # Obtenemos el dict con la info de la estacion
        estacion = Estaciones.objects.using('spida_web').filter(id_estacion=IdEst,
                                                            monitorizar=1,
                                                            visualizar=1).first()
    
    if estacion is None:
        return JsonResponse(result, safe=False)
    else:
        result['estacion'] = estacion.nombre
        result['tipo'] = estacion.id_tipo.nombre
        result['red'] = estacion.id_red.nombre
        result['subcuenca'] = estacion.id_subcuenca.nombre
        # result['codigo'] = estacion['cod_externo']
        # result['subcuenca'] = estacion['id_subcuenca']
        
    # Obtenemos el dict con la tabla a la que debemos acceder
    canales = Canales.objects.using('spida_web').filter(id_canal=IdCan).values().first()
    if not canales:
        return JsonResponse(result, safe=False)
    else:
        result['nombre'] = canales['nombre']
        result['unidades'] = canales['unidades']

    # Obtenenmos el model donde estan valores
    Valores = getModelbyDbtable(canales['tabla_bd'])
    if Valores == None:
        return JsonResponse(result, safe=False)


    fechahoraUTC_lim = datetime.utcnow() - timedelta(hours=24)
    UTCzone = tz.tzutc()
    fechahoraUTC_lim = fechahoraUTC_lim.replace(tzinfo=UTCzone)

    # Descargamaos las anteriores 24h
    data = Valores.objects.using('spida_web').filter(id_estacion=IdEst,
                                                     id_canal=IdCan,
                                                     fecha_hora_utc__gt=fechahoraUTC_lim)
    data = data.values('fecha_hora_local',
                       'valor',
                       'valido')
    # si no hay datos valores es una lista vacía []
    result['valores'] = list(data)
    
    return JsonResponse(result, safe=False)

'''Datos: Prediccion del canal para las próximas 24 horas'''
def getPrediccion24h(request):
    
    user = request.user
    result = {}
    
    Estacion = request.GET.get('estacion','')
    Canal = request.GET.get('canal','')

    if Estacion == '' or Canal == '':
        return JsonResponse(result, safe=False)
    
    IdEst = int(Estacion)
    IdCan = int(Canal)

    # Obtenemos el dict con la info de la estacion
    estacion = Estaciones.objects.using('spida_web').filter(id_estacion=IdEst,
                                                            monitorizar=1,
                                                            visualizar=1).first()
    
    if estacion is None:
        return JsonResponse(result, safe=False)
    else:
        result['estacion'] = estacion.nombre
        result['tipo'] = estacion.id_tipo.nombre
        result['red'] = estacion.id_red.nombre
        result['subcuenca'] = estacion.id_subcuenca.nombre
        # result['codigo'] = estacion['cod_externo']
        # result['subcuenca'] = estacion['id_subcuenca']

    # VALORES
    # Obtenemos el dict con la tabla a la que debemos acceder
    canales = Canales.objects.using('spida_web').filter(id_canal=IdCan).values().first()
    if not canales:
        return JsonResponse(result, safe=False)
    else:
        result['nombre'] = canales['nombre']
        result['unidades'] = canales['unidades']

    # Obtenenmos el model donde estan valores
    Valores = getModelbyDbtable(canales['tabla_bd'])
    if Valores == None:
        return JsonResponse(result, safe=False)


    fechahoraUTC = datetime.utcnow()
    fechahoraUTC_pastlim = fechahoraUTC - timedelta(hours=24)
    # UTCzone = tz.tzutc()
    # fechahoraUTC_lim = fechahoraUTC_lim.replace(tzinfo=UTCzone)

    # Descargamaos las anteriores 24h
    data = Valores.objects.using('spida_web').filter(id_estacion=IdEst,
                                                     id_canal=IdCan,
                                                     fecha_hora_utc__gt=fechahoraUTC_pastlim)
    data = data.values('fecha_hora_local',
                       'valor')

    # si no hay datos valores es una lista vacía []
    result['valores'] = list(data)

    # PREDICCION
    # Obtenemos el dict con la tabla a la que debemos acceder

    IdCanPred = IdCan + 1000
    
    canales = Canales.objects.using('spida_web').filter(id_canal=IdCanPred).values().first()
    if not canales:
        return JsonResponse(result, safe=False)

    # Obtenenmos el model donde estan valores
    Valores = getModelbyDbtable(canales['tabla_bd'])
    if Valores == None:
        return JsonResponse(result, safe=False)

    fechahoraUTC_futlim = fechahoraUTC + timedelta(hours=24)
    
    # Descargamaos las anteriores 24h
    data = Valores.objects.using('spida_web').filter(id_estacion=IdEst,
                                                     id_canal=IdCanPred,
                                                     fecha_hora_utc__gt=fechahoraUTC,
                                                     fecha_hora_utc__lt=fechahoraUTC_futlim)
    data = data.values('fecha_hora_local',
                       'valor')

    # si no hay datos valores es una lista vacía []
    result['prediccion'] = list(data)

    return JsonResponse(result, safe=False)

def getModelbyDbtable(db_table):
    for model in apps.get_models():
        if model._meta.db_table == db_table:
            return model
    else:
        return None


'''Devuelve los colores de la leyenda de la Precipitacion Acum 1 hora de los modelos numericos de Aemet'''
def getLegendaModelosNumericos(request):
    peticionLegendModelosNumericos = requests.get('http://www.aemet.es/es/api-eltiempo/modelo-harmonie/leyenda/61/PB')
    result = peticionLegendModelosNumericos.json()
    return JsonResponse(result, safe=False)


'''Devuelve los colores de la leyenda de la Precipitacion Acum 1 hora del Radar de Aemet'''
def getLegendaRadar(request):
    peticionLegendModelosNumericos = requests.get('http://www.aemet.es/es/api-eltiempo/radar/leyenda-radar/RN1')
    result = peticionLegendModelosNumericos.json()
    return JsonResponse(result, safe=False)



''' Consulta las cámaras de las estaciones de la red SPIDA '''
@permission_required('auth.spida_documentacion')
def getCamarasEstaciones(request):
    # si viene desde el formulario entra por aquí
    if request.method == 'POST':
        print(request.POST)
        '''
        # como consultar camara ejemplo
        fechaHora = datetime.now().astimezone(pytz.timezone("Europe/Madrid"))
        # en la ip tendrás que poner la url con la que consultas la camara con vlc
        camara = {"nombre":"spida01", "ip":'http://172.20.36.19/videostream.cgi?user=&pwd=&resolution=32&rate=0'}
        try:
            vid = cv2.VideoCapture(camara["ip"])
            ret, frame = vid.read()
            cv2.putText(frame,camara["nombre"]+" "+fechaHora.strftime("%m/%d/%Y, %H:%M:%S"), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, 3)	
            cv2.imwrite(camara["nombre"]+'.jpg', frame)
        except Exception as e:
            print("ERROR CARGANDO CAMARA", camara["nombre"], e)
            '''
    
        # aquí habrá que consultar la imagen y mandarla a la web

        return render(request, "camarasSpida.html",{})
    
    # si no viene desde el formulario entra por aquí y entrega la web sin nada
    else:
        # aquí falta obtener los nombre de las estaciones para rellenar el select del formulario
        return render(request, "camarasSpida.html",{})
