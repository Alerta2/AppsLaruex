from datetime import datetime, timedelta
from dateutil import tz
import locale
import requests
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.fields import CharField, DateTimeField, FloatField, IntegerField
from django.shortcuts import render, resolve_url
from django.apps import apps
import pandas as pd
from pandas_geojson import to_geojson
from .forms import FormCrearEvento, FormCerrarEvento
from .models import  AvisosMeteorologicosAemet, Estaciones, InformesTrimestrales, SucesosInundacion, Eventos, ContactosMunicipios, DocumentacionAdjunto, AdjuntosEventos,Canales, UltimasImagenes, ZonaMeteoalertaAemet, UltimosValores, RelacionEstacionesMeteo, CamarasSaih, ValoresVisualizados10D, ValoresPrecipitacion10D
from django.http import JsonResponse
from django.db.models import F, Q, Func, Case, When, Value,Sum, CharField
from django.db.models.functions import Concat
from django.http import FileResponse
from django.conf import settings
import base64
import json
import pytz
import numpy as np
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.clickjacking import xframe_options_sameorigin
from structure.models import Profile

def InformesSemestrales(request):
    user=request.user
    return render(request,"informes.html",{"user":user})

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

'''Pagina unica (Spida)'''
def Spida(request):
    user=request.user
    return render(request,"spida.html",{"user": user})

def Prueba(request):
    user=request.user
    return render(request,"pruebaprintmap.html",{"user": user})

'''Pagina de inicio (Home Spida)'''
def HomeSpida(request):
    user=request.user
    return render(request,"home_spd.html",{"user": user})

'''Pagina de datos en tiempo real (Mapa Spida)'''
def MapaSpida(request):
    user=request.user
    
    if user.is_authenticated:
        filters = {
            'visualizar': 1,
            'monitorizar': 1,
        }
    else:
        filters = {
            'visualizar': 1,
            'monitorizar': 1,
            #'estaciones_ultimos_valores__id_canal':100,
            'id_red': 1
        }

    estaciones= Estaciones.objects.using('spd'
    ).select_related(
    ).filter(**filters, id_tipo__in=[1,2,5] # Solo estaciones con monitorizacion de nivel de rio
    ).annotate(
        Id=F('id_estacion'),
        Nombre=F('nombre'),
        Tipo= Case( When(id_tipo=2, then=Value('E')),
                    default=Value('AR'),
                    output_field=CharField()
                    ),
        Red=Case(When(id_red=1, then=Value('SPD/')),
                When(id_red=2, then=Value('CHT/')),
                When(id_red=3, then=Value('CHG/')),
                default=Value(''),
                output_field=CharField())
    ).values('Id','Nombre','Tipo', 'Red').order_by('Nombre')
    
    return render(request,"mapa_spd.html",{"user": user, "listaEstaciones":estaciones})

'''Pagina no encontrada 404'''
def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

'''Pagina error 500'''
def custom_error_view(request, exception=None):
    return render(request, "errors/500.html", {})

'''Pagina de sucesos de inundacion'''
def SucesosSpida(request):
    user = request.user
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    sucesos=SucesosInundacion.objects.using('spd').order_by('-fecha_hora_local')

    listaSucesos=[]
    for suceso in sucesos:
        sucesoAuxiliar={}
        sucesoAuxiliar['id']=suceso.id_suceso
        sucesoAuxiliar['titulo']=suceso.rotulo
        sucesoAuxiliar['descripcion']=suceso.descripcion
        sucesoAuxiliar['fecha']=(suceso.fecha_hora_local).strftime("%d %B, %Y")
        sucesoAuxiliar['imagen']=base64.b64encode(suceso.imagen).decode()
        listaSucesos.append(sucesoAuxiliar)

    return render(request,"sucesos_spd.html",{"user": user, "Sucesos":listaSucesos})

'''Pagina de documentacion privada'''
def DocumentacionSpida(request):
    user=request.user
    return render(request,"documentacion_spd.html",{"user": user})

'''Pagina de Alerta2 privada'''
def Alerta2(request):
    user=request.user
    return render(request,"alerta2_spd.html",{"user": user})

''' POST (Evento Submit del Formulario existente en el template Configuración 
del Perfil del Usuario para modificar los datos personales (nombre, apellidos, 
email, telefono, avatar)'''
def updatePerfilUsuario(request):
    user=request.user

    mensaje={}
    mensaje["text"]=""
    mensaje["timer"]=5000

    if request.method == 'POST':
        info=request.POST # get info del POST 
        avatar=request.FILES #get avatar (imagen del Perfil del Usuario)

        #Si se resuelve de forma satisfactoria....
        mensaje["title"]='El perfil del usuario ha sido actualizado'
        mensaje["icon"]="success"

        #Actualizo la info del usuario (nombre, apellidos y email)  
        try:      
            user.first_name=info.get("first_name")
            user.last_name=info.get("last_name")
            user.email=info.get("email")
            user.save()

        except:
            mensaje["title"]="No ha sido posible actualizar la información del usuario"
            mensaje["text"]="Intentelo de nuevo en unos minutos"
            mensaje["icon"]="warning"

        #Actualizo el profile del usuario (avatar y telefono)  
        try: 
            if hasattr(request.user, 'profile'): #existe profile para el usuario
                user.profile.telefono=info.get("phonenumberCompleto")
                if avatar.get("avatar") is not None: #Filtro el que la imagen del avatar no sea obligatoria ponerla
                    user.profile.image=avatar.get("avatar")
                user.profile.save()

            else: #no existe profile para el usuario
                if avatar.get("avatar") is not None: #Filtro el que la imagen del avatar no sea obligatoria ponerla
                    newProfile = Profile(user=User.objects.get(username=user), telefono = info.get("phonenumberCompleto"),image = avatar.get("avatar"))
                else:
                    newProfile = Profile(user=User.objects.get(username=user), telefono = info.get("phonenumberCompleto"))
                newProfile.save()
        except:
            mensaje["title"]="No ha sido posible actualizar el perfil del usuario"
            mensaje["text"]="Intentelo de nuevo en unos minutos"
            mensaje["icon"]="warning"
        
        return JsonResponse(mensaje, safe=False)
    else:
        mensaje["title"]="Se ha producido un error"
        mensaje["text"]="Intentelo de nuevo"
        mensaje["icon"]="error" 
        return JsonResponse(mensaje, safe=False)


'''Pagina de Alerta2 privada'''
def GraficosNivelRio(request):
    user=request.user

    filters = {
        'monitorizar': 1,
        'id_red': 1
    }

    estaciones= Estaciones.objects.using('spd'
    ).select_related(
    ).filter(**filters
    ).annotate(
        Id=F('id_estacion'),
        Nombre=F('nombre'),
        T = F('id_tipo'),
        N1=Sum(F('estaciones_umbrales__limite_n1') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
        N2=Sum(F('estaciones_umbrales__limite_n2') * (F('estaciones_umbrales__limite_desbordamiento') /100),output_field=FloatField()),
        N3=Sum(F('estaciones_umbrales__limite_n3') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
    ).values('Id','Nombre','N1','N2','N3')
    #jsonEstaciones = json.dumps(list(estaciones), default=myconverter)
    return render(request,"graficos_nivel_rio_spd.html",{"user": user, "Estaciones":list(estaciones)})

#def prueba(request):
#    user=request.user
#    filters = {
#    'monitorizar': 1,
#    'estaciones_ultimos_valores__id_canal':100,
#    'id_red': 1
#    }

#    estaciones= Estaciones.objects.using('spd'
#    ).select_related(
#    ).annotate(
#    ).filter(**filters
#        Id=F('id_estacion'),
#        Nombre=F('nombre'),
#        N1=Sum(F('estaciones_umbrales__limite_n1') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
#        N2=Sum(F('estaciones_umbrales__limite_n2') * (F('estaciones_umbrales__limite_desbordamiento') /100),output_field=FloatField()),
#        N3=Sum(F('estaciones_umbrales__limite_n3') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
#        NivelRio=F('estaciones_ultimos_valores__valor'),
#        FechaHora=F('estaciones_ultimos_valores__fecha_hora_local'),
#    ).values('Id','Nombre','N1','N2','N3','NivelRio','FechaHora')

#    return render(request,"graficos_nivel_rio_spd.html",{"user": user, "Estaciones":list(estaciones)})

'''Pagina de acceso a la parte privada (Login Spida)'''
def LoginSpida(request):
    user=request.user
    return render(request,"login_spd.html",{"user": user})

'''Pagina de edición de la información del usuario'''
def PerfilSpida(request):
    user=request.user

    if request.method == 'POST':
        #print("POST")
        info=request.POST # get info del POST 
        #print("REQWUEST", info)
        user.first_name=info.get("first_name")
        user.last_name=info.get("last_name")
        user.email=info.get("email")
        user.save()
      
        mensaje={}
        mensaje["title"]='El perfil del usuario ha sido actualizado'
        mensaje["text"]=""
        mensaje["icon"]="success"
        mensaje["timer"]=2000

        return render(request,"editperfil_spd.html",{"user": user, "mensaje": mensaje})
    
    else:
        return render(request,"editperfil_spd.html",{"user": user})


'''Pagina de consulta de los informes trimestrales de spida'''
def InformesTrimestralesSpida(request):
    user = request.user

    if request.method == 'POST':    
        mensaje={}    
        try:
            #print("METHOD POST", request.POST, request.FILES)                
            if 'docInformeTrimestral' in request.FILES:
                info=request.POST # get info del POST
                numCuatrimentre=int(info.get("cuatrimestre")) # get cuatrimentre del informe valorado (1 (Enero a Marzo), 2 (Abril a Junio), 3 (Julio a Septiembre) o 4 (Octubre a Diciembre))
                yearCuatrimestre=int(info.get("year"))
                first_date = datetime(yearCuatrimestre, 3 * numCuatrimentre - 2, 1)
                last_date = datetime(yearCuatrimestre + 3 * numCuatrimentre // 12, 3 * numCuatrimentre % 12  + 1, 1) + timedelta(days=-1)

                InformeTrimestral = request.FILES.getlist('docInformeTrimestral')[0] # get pdf adjuntado
                nombreInformeTrimestral=(InformeTrimestral.name).replace(" ", "_") # nombre del fichero
                sizeInformeTrimestral=InformeTrimestral.size # tamaño del pdf (En bytes)
                rutaInformeTrimestral = '/SPIDA/INFORMES_TRIMESTRALES/ITS_'+str(yearCuatrimestre)+'_'+str(numCuatrimentre)+'C'+'.pdf'
                
                with open(settings.MEDIA_ROOT+rutaInformeTrimestral, 'wb+') as destination:
                    print("Escribiendo fichero")
                    for chunk in InformeTrimestral.chunks():
                        destination.write(chunk)
                
                # Create or update new values 
                new_values={"id_cuatrimestre":numCuatrimentre, "year":yearCuatrimestre, "fecha_hora_local_inicio":first_date, "fecha_hora_local_fin":last_date, "nombre":nombreInformeTrimestral, "size":sizeInformeTrimestral, "ruta":rutaInformeTrimestral, "fecha_hora_subida":datetime.now()}
                obj, created = InformesTrimestrales.objects.using('spd').update_or_create(fecha_hora_local_inicio=first_date, fecha_hora_local_fin=last_date, defaults=new_values)
            
            
                mensaje["title"]='Se ha adjuntado un nuevo informe trimestral'
                mensaje["text"]=nombreInformeTrimestral
                mensaje["icon"]="success"
                return render(request,"informes_trimestrales_spd.html",{"user": user, "mensaje": mensaje})
        
        except:
            mensaje["title"]='¡Se ha producido un error!'
            mensaje["text"]="Inténtelo de nuevo en unos minutos"
            mensaje["icon"]="error"
            return render(request,"informes_trimestrales_spd.html",{"user": user, "mensaje": mensaje})

    return render(request,"informes_trimestrales_spd.html",{"user": user})

''''Comprobacion (ajax): si existe un informe trimestral '''
def ExitsInformeTrimestral(request):
    numCuatrimentre = int(request.GET.get('c',''))
    yearCuatrimestre= int(request.GET.get('y',''))
    first_date = datetime(yearCuatrimestre, 3 * numCuatrimentre - 2, 1)
    last_date = datetime(yearCuatrimestre + 3 * numCuatrimentre // 12, 3 * numCuatrimentre % 12  + 1, 1) + timedelta(days=-1)

    if InformesTrimestrales.objects.using('spd').filter(fecha_hora_local_inicio=first_date, fecha_hora_local_fin=last_date).exists():
        return JsonResponse(True, safe=False)
    else:
        return JsonResponse(False,safe=False)

'''Pagina de documentacion de interes de un evento de inundacion'''
def EventosInundacion(request):
    user=request.user
    mensaje={}
    DocumentacionErronea = ""
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    try:
        if request.method == 'POST': # 1.       
            #print("METHOD POST", request.POST, request.FILES) # 2.  
            formCreateNewEvento = FormCrearEvento(request.POST) 
            if formCreateNewEvento.is_valid(): # 2.1
                info=request.POST # get info del POST
                tituloNewEvento = info.get("tituloNewEvento") # get titulo del nuevo evento
                fechaNewEvento =datetime.strptime(info.get("fechaInicial"),'%d/%m/%Y')  # get fecha (inicio) del evento

                if Eventos.objects.using('spd').filter(fecha_hora_inicio=fechaNewEvento).exists(): # Compruebo si ya existe un evento con la misma fecha de inicio. Si existe ...
                    mensaje["title"]='No se puede crear el evento de inundación'
                    mensaje["text"]='Ya existe un evento de inundación con fecha de inicio '+ fechaNewEvento.strftime('%d de %B de %Y')
                    mensaje["icon"]="warning"
                    
                else: # Si no existe ....
                    mensaje["title"]='Se ha creado un nuevo evento'
                    mensaje["text"]=tituloNewEvento +' con fecha '+ fechaNewEvento.strftime('%d de %B de %Y')
                    mensaje["icon"]="success"

                    new_entry = Eventos(titulo=tituloNewEvento, fecha_hora_inicio=fechaNewEvento, estado='0') # Creo la query para almacenarlo en la base de datos
                    new_entry.save(using='spd') # Guardo el nuevo evento en la base de datos
            
            else:
                formCloseEvento = FormCerrarEvento(request.POST) 
                if formCloseEvento.is_valid():
                    info=request.POST # get info del POST
                    idEvento = int(info.get("idEventoInundacion")) # get id del evento
                    tituloEvento = info.get("tituloFinalEvento") # get titulo del evento
                    fecha_hora=datetime.strptime(info.get("fechaFinal"),'%d/%m/%Y')
                    query=Eventos.objects.using('spd').filter(id_evento=idEvento)  
                    
                    if query.exists(): # Si el evento existe en la base de datos 
                        Eventos.objects.using('spd').filter(id_evento=idEvento).update(titulo=tituloEvento, fecha_hora_fin=fecha_hora, estado='1') # Le añado la fecha fin del evento y cambio su estado ('0': Abierto, '1':Cerrado)
                        mensaje["title"]='¡Concluido el evento de inundación!'
                        mensaje["text"]= ""
                        mensaje["icon"]="success"
                    else:
                        mensaje["title"]='¡Se ha producido un error!'
                        mensaje["text"]= "No existe ningun evento con titulo " + tituloEvento 
                        mensaje["icon"]="error"
                    
                elif 'docsEvento' in request.FILES: # 2.2
                    info=request.POST # get info del POST
                    idEvento = info.get("idEvento") # get id del evento
                    tituloAdjunto = info.get("titulo") # get titulo del adjunto
                    descripcionAdjunto =info.get("descripcion") # get descripcion del adjunto 
                    fecha_hora = datetime.now()

                    #Añado el nuevo adjunto
                    Evento = Eventos.objects.using('spd').filter(id_evento=int(idEvento)).first()
                    new_entry = AdjuntosEventos(id_evento=Evento, titulo_adjunto=tituloAdjunto, id_usuario=user.id, fecha_hora_local=fecha_hora, descripcion=descripcionAdjunto) # Creo la query para almacenarlo en la base de datos
                    new_entry.save(using='spd') # Guardo el nuevo evento en la base de datos
                    idAdjunto = new_entry.id_adjunto
            
                    listFicherosAdjuntos = request.FILES.getlist('docsEvento') # get ficheros adjuntados
                    
                    for fichero in listFicherosAdjuntos: # recorro los ficheros adjuntos 
                        print("Fichero: ",fichero.name.split('.')[0], fichero.name.split('.')[-1], "Size:", fichero.size)
                        #nombrefichero=(fichero.name.split('.')[0]).replace(" ", "_") # nombre del fichero
                        nombrefichero=(fichero.name).replace(" ", "_") # nombre del fichero
                        extfichero=fichero.name.split('.')[-1] # extension del fichero (tipo: Ejemplo pdf, doc, jpg etc.)
                        sizefichero=fichero.size # tamaño del fichero (En bytes)
                        resultUpload = CargarFicheroAdjuntado(fichero,idEvento,idAdjunto,nombrefichero,extfichero,sizefichero) # Almaceno cada fichero en media/SPIDA y en la base de datos
                        if resultUpload==False:
                            DocumentacionErronea= DocumentacionErronea + fichero.name + ", "

                    if DocumentacionErronea!="":
                        mensaje["title"]='¡Se ha producido un error!'
                        mensaje["text"]="No se han podido subir los documentos: "+DocumentacionErronea+"inténtelo de nuevo en unos minutos"
                        mensaje["icon"]="error"
                    else:
                        mensaje["title"]='¡Nueva documentación adjuntada!'
                        mensaje["text"]= str(user.get_full_name())+" has adjuntado un total de "+ str(len(request.FILES.getlist('docsEvento')))+" nuevos archivos"
                        mensaje["icon"]="success"
               
    except NameError:
        mensaje["title"]='¡Se ha producido un error!'
        mensaje["text"]="Inténtelo de nuevo en unos minutos"
        mensaje["icon"]="error"

    finally:
        eventos=Eventos.objects.using('spd').order_by('estado','-fecha_hora_inicio')
        return render(request,"informes_eventos_spd.html",{"user": user,"Eventos":eventos , "formNewEvento": FormCrearEvento(), "formCloseEvento": FormCerrarEvento(), "Mensaje": mensaje})


'''Guardar Documentacion Adjuntada de los Eventos Spida'''
def CargarFicheroAdjuntado(fichero, idEvento, idAdjunto, nombreFichero, extensionFichero, sizeFichero):
    fecha_hora=datetime.now()
    rutaFichero= '/SPIDA/EIS_'+ str(idEvento).zfill(4)+'_'+fecha_hora.strftime("%Y%m%d%H%M%S")+nombreFichero # ruta donde va a ser guardado el fichero adjuntado
    #print("Solicito escribir fichero ", fichero)
    result = False
    try:
        with open(settings.MEDIA_ROOT +rutaFichero, 'wb+') as destination:
            print("Escribiendo fichero")
            for chunk in fichero.chunks():
                destination.write(chunk)
            
            Adjunto = AdjuntosEventos.objects.using('spd').filter(id_adjunto=int(idAdjunto)).first()
            new_entry = DocumentacionAdjunto(id_adjunto=Adjunto,nombre=nombreFichero, extension=extensionFichero, ruta=rutaFichero, size = sizeFichero) # Creo la query para almacenarlo en la base de datos
            new_entry.save(using='spd') # Guardo el nuevo evento en la base de datos
            result = True
    except:
        result=False
    finally:
        return result

'''Pagina con acceso a los telefonos de contacto de los municipios Spida'''
def Contactos(request):
    user=request.user
    return render(request,"contactos_spd.html",{"user": user})


'''Datos: Informacion concreta de una estacion'''
def getInfoEstacion(request):

    result={}
    result['info']=pd.DataFrame().to_dict('records')
    result['data']=pd.DataFrame().to_dict('records')

    user = request.user

    idEstacion=request.GET.get('i','')

    # Si no obtuve respuesta 
    if idEstacion == '' or idEstacion is None:
        return JsonResponse(list(), safe=False)
    
    # Obtengo el id de la estacion que quiero consultar
    idEstacion= int(idEstacion)

    # Extraigo la informacion de la estacion
    infoEstacion= Estaciones.objects.using('spd'
        ).select_related(
        ).filter(id_estacion= idEstacion
        ).annotate(
            Id=F('id_estacion'),
            Nombre=F('nombre'),
            R=F('id_red'),
            T = F('id_tipo'),
            Latitud=F('sensor_lat'),
            Longitud=F('sensor_lon'),
            CodA=F('widget_aemet'),
            N1=Sum(F('estaciones_umbrales__limite_n1') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
            N2=Sum(F('estaciones_umbrales__limite_n2') * (F('estaciones_umbrales__limite_desbordamiento') /100),output_field=FloatField()),
            N3=Sum(F('estaciones_umbrales__limite_n3') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
        ).values('Id','Nombre','R','T','Latitud','Longitud','CodA','N1','N2','N3')

    if len(infoEstacion)>0:
        df_infoEstacion = pd.DataFrame(infoEstacion)
        result['info']=df_infoEstacion.to_dict('records')

        # Si se trata de un embalse...
        if str(df_infoEstacion['T'].iloc[0]) == '2':
            canales = [501]
        # Si se trata de cualquier otra estacion...
        else:
            canales = [100]

        print(df_infoEstacion['Id'].iloc[0], canales)
        dataEstacion  = UltimosValores.objects.using('spd'
                    ).filter(id_estacion = df_infoEstacion['Id'].iloc[0] , id_canal__in = canales
                    ).annotate(
                        C=F('id_canal__id_canal'),
                        V = F('valor'),
                        DTL = F('fecha_hora_local'),
                        E = Case( When(Q(id_canal = 100) & Q(fecha_hora_utc__lte=Value((datetime.utcnow()-timedelta(minutes=80)),DateTimeField())), then=Value('-1')),
                                When(Q(id_canal = 100) & Q(valor__gte=Value(df_infoEstacion['N3'].iloc[0])), then=Value('3')),
                                When(Q(id_canal = 100) & Q(valor__gte=Value(df_infoEstacion['N2'].iloc[0])), then=Value('2')),
                                When(Q(id_canal = 100) & Q(valor__gte=Value(df_infoEstacion['N1'].iloc[0])), then=Value('1')),
                                When(Q(id_canal = 100) & Q(valor__lt=Value(df_infoEstacion['N1'].iloc[0])), then=Value('0')),
                                default=Value('10'),
                                output_field=IntegerField()
                                )
                    ).values('C', 'V', 'DTL', 'E')
                
        if len(dataEstacion)>0:
            df_dataEstacion= pd.DataFrame(dataEstacion)
            df_dataEstacion['DTL']=df_dataEstacion['DTL'].dt.strftime("%d %B a las %H:%M h")
            result['data']=df_dataEstacion.to_dict('records')

    return JsonResponse(result, safe=False)

    #filters = {
    #        'estaciones_ultimos_valores__id_canal':100,
    #        'estaciones_ultimos_valores__id_estacion':idEstacion
    #    }
    
    #locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    #infoEstacion= Estaciones.objects.using('spd'
    #).select_related(
    #).filter(**filters, estaciones_ultimos_valores__id_canal__in =[100,500,201]
    #).annotate(
     #   Id=F('id_estacion'),
     #   Nombre=F('nombre'),
     #   Red=F('id_red'),
     #   Tipo = F('id_tipo'),
     #   Latitud=F('sensor_lat'),
     #   Longitud=F('sensor_lon'),
     #   CodAemet=F('widget_aemet'),
     #   N1=Sum(F('estaciones_umbrales__limite_n1') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
     #   N2=Sum(F('estaciones_umbrales__limite_n2') * (F('estaciones_umbrales__limite_desbordamiento') /100),output_field=FloatField()),
     ##   N3=Sum(F('estaciones_umbrales__limite_n3') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
      #  NivelRio=F('estaciones_ultimos_valores__valor'),
      #  FechaHora=F('estaciones_ultimos_valores__fecha_hora_utc'),
      #  Estado= Case( When(estaciones_ultimos_valores__fecha_hora_local__lte=Value((datetime.now()-timedelta(minutes=80)),DateTimeField()), then=Value('-1')),
      #              When(estaciones_ultimos_valores__valor__gte=F('N3'), then=Value('3')),
      #              When(estaciones_ultimos_valores__valor__gte=F('N2'), then=Value('2')),
      #              When(estaciones_ultimos_valores__valor__gte=F('N1'), then=Value('1')),
      #              When(estaciones_ultimos_valores__valor__lt=F('N1'), then=Value('0')),
      #              default=Value('10'),
      #              output_field=IntegerField()
      #              )
    #).values('Id','Nombre','Red','Latitud','Longitud','CodAemet','N1','N2','N3','NivelRio','FechaHora','Estado')

    #return  JsonResponse(list(infoEstacion), safe=False)
from requests.auth import HTTPBasicAuth
def getCapturaImagen(request):
    idEstacion = request.GET.get('i','')
    idCamara = request.GET.get('c','')

    if idEstacion!="" and idCamara!="":

        camara = CamarasSaih.objects.using('spd').filter(id_estacion = idEstacion, data = idCamara).values('url').first()

        if camara!=None:
            return JsonResponse(camara['url'], safe=False)

    return JsonResponse([], safe=False)

def getStreamingImagen(request):

    idEstacion = request.GET.get('i','')
    idCamara = request.GET.get('c','')
    print("CAMARA", idEstacion, idCamara)

    if idEstacion!="":

        camara = CamarasSaih.objects.using('spd').filter(id_estacion = idEstacion).exclude(streaming__isnull=True).values('data','streaming')

        if len(camara)>0:
            df_camara = pd.DataFrame(camara)
            #df_camara['data'] = [str(x) for x in df_camara['data'] if x.isdigit()]
            df_camara['data'] =  df_camara.apply(lambda row :  "".join([str(x) for x in row['data'] if x.isdigit()]), axis = 1)
            df_camara['data'] =  df_camara.apply(lambda row :  "" if row["data"]=="" else str(int(row['data'])), axis = 1)
            print(df_camara)
            df_camara = df_camara[df_camara['data'] == idCamara] 
            if len(df_camara)>0:
                return JsonResponse(df_camara.iloc[0]['streaming'], safe=False)

    return JsonResponse([], safe=False)



'''Datos: Ultima imagen de la cámara principal de una estacion'''
def getUltimaImagen(request):

    df_imagenes = pd.DataFrame()

    user = request.user
    
    idEstacion = request.GET.get('i','')
    tipoEstacion = request.GET.get('t','')

    if idEstacion == '' or idEstacion is None:
        return JsonResponse([], safe=False)
    
    idEstacion = int(idEstacion)
    order = 'id_camara'

    # Excepcion para segundos sensores (Ej: Badajoz)
    if idEstacion>=8000:  
        idEstacion = idEstacion-1000
        order ='-id_camara'

    imagenes = UltimasImagenes.objects.using('spd'
            ).filter(id_estacion=idEstacion, fecha_hora_utc__gte=datetime.utcnow()-timedelta(days=1)
            ).values(
            ).order_by(order)
    
    if len(imagenes)>0:
        df_imagenes = pd.DataFrame(imagenes)
        df_imagenes['fecha_hora_utc']=df_imagenes['fecha_hora_utc'].dt.strftime("%d %B a las %H:%M h (UTC)")
        df_imagenes['fecha_hora_local']=df_imagenes['fecha_hora_local'].dt.strftime("%d %B a las %H:%M h")
        df_imagenes['imagen']=df_imagenes.apply(lambda x :  base64.b64encode(x['imagen']).decode(), axis = 1)
        df_imagenes['miniatura']=df_imagenes.apply(lambda x :  base64.b64encode(x['miniatura']).decode(), axis = 1)
         
    return JsonResponse(df_imagenes.to_dict('records'), safe=False)


'''Datos: Imagen concreta de una estacion'''
def getImagenSpida(request):
    user = request.user
    
    idEstacion = request.GET.get('id','')
    idCamara = request.GET.get('c','')
    ultimaImagen={}

    if idEstacion == '' or idCamara== '':
        return JsonResponse(list(ultimaImagen), safe=False)
      
    idEstacion = int(idEstacion)
    idCamara = int(idCamara)

    Imagen = UltimasImagenes.objects.using('spd').filter(id_estacion=idEstacion,id_camara=idCamara)

    for imagen in Imagen:
        ultimaImagen['FechaHora']=imagen.fecha_hora_local.strftime("%d %B a las %H:%M h")
        ultimaImagen['imagen']=base64.b64encode(imagen.imagen).decode()
         
    return JsonResponse(ultimaImagen, safe=False)

def getImagenesCamaras(request):
    user = request.user
    df_imagenes = pd.DataFrame()
    Imagenes = UltimasImagenes.objects.using('spd').filter(id_estacion__id_red=1).values('imagen', 'fecha_hora_local')

    if len(Imagenes)>0:
        df_imagenes = pd.DataFrame(Imagenes)
        df_imagenes['fecha_hora_local']=   df_imagenes.apply(lambda row :  row['fecha_hora_local'].strftime("%d %B a las %H:%M h"), axis = 1)
        df_imagenes['imagen']= df_imagenes.apply(lambda row :  base64.b64encode(row['imagen']).decode(), axis = 1)

    return JsonResponse(df_imagenes.to_dict('records'), safe=False)


'''Datos: Listado de miniaturas de las ultimas imagenes tomadas de todas las estaciones Spida'''
def getMiniaturasSpida(request):
    user = request.user
    imagenes = UltimasImagenes.objects.using('spd').filter(id_estacion__id_red = 1)

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


'''Datos: Estaciones Monitorizadas y Visualizadas (SAIH y SPIDA)'''
def getEstaciones(request):
    user = request.user

    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    if user.is_authenticated:
        filters = {
            'visualizar': 1,
            'monitorizar': 1,
            'estaciones_ultimos_valores__id_canal':100
        }
    else:
        filters = {
            'visualizar': 1,
            'monitorizar': 1,
            'estaciones_ultimos_valores__id_canal':100,
            'id_red': 1
        }

    estaciones= Estaciones.objects.using('spd'
    ).select_related(
    ).filter(**filters
    ).annotate(
        Id=F('id_estacion'),
        Nombre=F('nombre'),
        Red=F('id_red'),
        Latitud=F('sensor_lat'),
        Longitud=F('sensor_lon'),
        CodAemet=F('widget_aemet'),
        N1=Sum(F('estaciones_umbrales__limite_n1') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
        N2=Sum(F('estaciones_umbrales__limite_n2') * (F('estaciones_umbrales__limite_desbordamiento') /100),output_field=FloatField()),
        N3=Sum(F('estaciones_umbrales__limite_n3') * (F('estaciones_umbrales__limite_desbordamiento') / 100),output_field=FloatField()),
        NivelRio=F('estaciones_ultimos_valores__valor'),
        FechaHora=F('estaciones_ultimos_valores__fecha_hora_utc'),
        Estado= Case( When(estaciones_ultimos_valores__fecha_hora_local__lte=Value((datetime.now()+timedelta(minutes=-80)),DateTimeField()), then=Value('-1')),
                    When(estaciones_ultimos_valores__valor__gte=F('N3'), then=Value('3')),
                    When(estaciones_ultimos_valores__valor__gte=F('N2'), then=Value('2')),
                    When(estaciones_ultimos_valores__valor__gte=F('N1'), then=Value('1')),
                    When(estaciones_ultimos_valores__valor__lt=F('N1'), then=Value('0')),
                    default=Value('10'),
                    output_field=IntegerField()
                    )
    ).values('Id','Nombre','Red','Latitud','Longitud','CodAemet','N1','N2','N3','NivelRio','FechaHora','Estado')

    properties=['Id','Nombre','Red','CodAemet','N1','N2','N3','NivelRio','FechaHora','Estado']
    datosGeoJson = list_to_geojson(list(estaciones), properties, 'Latitud', 'Longitud')

    return  JsonResponse(datosGeoJson, safe=False)

'''Datos: Estaciones Monitorizadas y Visualizadas (SAIH y SPIDA)'''
def getEstacionesPluvio(request):
    df_relEstaciones = pd.DataFrame()

    user = request.user

    idEstacion = request.GET.get('id','')

    if user.is_authenticated and idEstacion!='':
        
        estaciones= RelacionEstacionesMeteo.objects.using('spd'
                    ).filter(id_estacion_hidro_id = int(idEstacion)
                    ).values('id_estacion_pluvio')
                
        if len(estaciones)>0:
            df_estaciones = pd.DataFrame(estaciones)

            estPluvio = df_estaciones['id_estacion_pluvio'].unique().tolist()
            estPluvio.append(int(idEstacion)) 

            relEstaciones = Estaciones.objects.using('spd'
                        ).filter(id_estacion__in = estPluvio, monitorizar = 1, visualizar = 1
                        ).annotate(
                                    Id=F('id_estacion'),
                                    Nombre=F('nombre'),
                                    R=F('id_red'),
                                    Red = F('id_red__nombre'),
                                    T=F('id_tipo'),
                                    Tipo=F('id_tipo__nombre'),
                                    lat=F('sensor_lat'),
                                    lon=F('sensor_lon')
                        ).values('Id','Nombre', 'Red', 'Tipo', 'R', 'T', 'lat', 'lon')
            
            if len(relEstaciones)>0:
                df_relEstaciones = pd.DataFrame(relEstaciones)

    return  JsonResponse(df_relEstaciones.to_dict('records'), safe=False)

'''Datos: Embalses Monitorizados y Visualizados'''
def getEmbalses(request):
    user = request.user

    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    filters = {
        'visualizar': 1,
        'monitorizar': 1,
        'estaciones_ultimos_valores__id_canal__in':[501,201]
    }
    filters2 = {
        'id_estacion__visualizar': 1,
        'id_estacion__monitorizar': 1,
        'id_canal__in':[501,201]
    }


    embalses = UltimosValores.objects.using('spd'
            ).filter(**filters2
            ).annotate(
                Id=F('id_estacion'),
                Codigo=F('id_estacion__cod_externo'),
                Nombre=F('id_estacion__nombre'),
                Red=F('id_estacion__id_red'),
                Latitud=F('id_estacion__sensor_lat'),
                Longitud=F('id_estacion__sensor_lon'),
                CaudalSalida=Case( When(id_canal=201, then=F('valor')),
                                        default=Value(None),
                                        output_field=FloatField()
                                ),
                Estado = Case( When(id_canal=201, then=Value(4)),
                                        default=Value(None),
                                        output_field=IntegerField()
                                ),
                FechaHoraCS=Case( When(id_canal=201, then=F('fecha_hora_utc')),
                                        default=Value(None),
                                        output_field=DateTimeField()
                                ),  
                VolumenPorcentual=Case( When(id_canal=501, then=F('valor')),
                                        default=Value(None),
                                        output_field=IntegerField()
                                ),
                FechaHoraVP=Case( When(id_canal=501, then=F('fecha_hora_utc')),
                                        default=Value(None),
                                        output_field=DateTimeField()
                                )
            ).values('Id','Codigo','Nombre','Red','Latitud','Longitud','CaudalSalida','FechaHoraCS','VolumenPorcentual','FechaHoraVP', 'Estado')
 
    df = pd.DataFrame(embalses)
    df = df.replace({np.nan: None})
    df = df.groupby(['Id','Codigo', 'Nombre', 'Red', 'Latitud', 'Longitud'], as_index=False)#.agg({'CaudalSalida':'first', 'FechaHoraCS':'first','VolumenPorcentual':'first', 'FechaHoraVP':'first'})
    df_embalses = df.mean()
    df_embalses = df_embalses.replace({np.nan: None})

    datosGeoJson = to_geojson(df=df_embalses, lat='Latitud', lon='Longitud',
                 properties=['Id', 'Codigo', 'Nombre', 'Red', 'CaudalSalida', 'FechaHoraCS', 'VolumenPorcentual', 'FechaHoraVP','Estado'])
    
    
    #embalses= Estaciones.objects.using('spd'
    #).select_related(
    #).filter(**filters
    #).annotate(
    #    Codigo=F('cod_externo'),
    #    Nombre=F('nombre'),
    #    Red=F('id_red'),
    #    Latitud=F('sensor_lat'),
    #    Longitud=F('sensor_lon'),
    #    VolumenPorcentual=F('estaciones_ultimos_valores__valor'),
    #    FechaHora=F('estaciones_ultimos_valores__fecha_hora_local'),
    #    Estado= Case( When(estaciones_ultimos_valores__fecha_hora_local__lte=Value((datetime.now()+timedelta(hours=-2)),DateTimeField()), then=Value('-1')),
    #                When(estaciones_ultimos_valores__fecha_hora_local__gte=Value((datetime.now()+timedelta(hours=-2)),DateTimeField()), then=Value('0')),
    #                default=Value('10'),
    #                output_field=IntegerField()
    #                )
    #).values('Codigo','Nombre','Red','Latitud','Longitud','VolumenPorcentual','FechaHora','Estado')

    #properties=['Codigo','Nombre','Red','VolumenPorcentual','FechaHora','Estado']
    #datosGeoJson = list_to_geojson(list(embalses), properties, 'Latitud', 'Longitud')
    return  JsonResponse(datosGeoJson, safe=False)
   

'''Datos: Listado Informes Trimestrales Spida'''
def getInformesTrimestrales(request):
    user = request.user

    informes = InformesTrimestrales.objects.using('spd').order_by('-fecha_hora_subida'
    ).extra(
        select={
            'id':'id_informe',
            'cuatrimestre' : 'id_cuatrimestre',
            'year' : 'year',
            'fecha_ini' : 'fecha_hora_local_inicio',
            'fecha_fin' : 'fecha_hora_local_fin',
            'size' : 'size',
            #'path' :'ruta',
            'fecha_subida':'fecha_hora_subida'
        }
    ).values('id', 'nombre', 'cuatrimestre', 'year', 'fecha_ini', 'fecha_fin', 'size', 'fecha_subida')

    return JsonResponse(list(informes), safe=False)

'''Datos: Listado de Contactos de los Municipios Spida'''
def getContactos(request):
    user= request.user
    contactos = ContactosMunicipios.objects.using('spd').order_by('id_estacion'
    ).annotate(
        id=F('id_contacto'),
        Estacion=F('id_estacion__nombre')
    ).values('id', 'nombre', 'apellidos', 'Estacion', 'telefono', 'oficio')

    return JsonResponse(list(contactos), safe=False)

'''Datos: Listado de documentos de un adjunto de un evento'''
def getDocumentosAdjunto(request):
    user = request.user
    idAdjunto=request.GET.get('adjunto','')

    listDocs = DocumentacionAdjunto.objects.using('spd').filter(id_adjunto=idAdjunto).order_by('extension').extra(
    select={
        'id':'id_documento',
        'adjunto' : 'id_adjunto',
        'doc' : 'nombre',
        'ext' : 'extension',
        'size' : 'size',
        #'path' : 'ruta'
    }
    ).values('id','nombre', 'adjunto', 'doc', 'ext', 'size') 

    return JsonResponse(list(listDocs), safe=False)

'''Datos: Listado de adjuntos de un evento'''
def getAdjuntos(request):
    user = request.user
    listaAdjutoEvento = []
    idEvento=request.GET.get('evento','')

    listAdjuntos = AdjuntosEventos.objects.using('spd').filter(id_evento=idEvento).order_by('-fecha_hora_local')

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

'''Datos: Valores del canal las anteriores 24 horas'''
def getValores24h(request):
    
    df_final = pd.DataFrame(columns=['fecha_hora_local', 'valor'])

    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    user = request.user
    result = {}
    
    estacion = request.GET.get('estacion','')
    canal = request.GET.get('canal','')

    if estacion == '' or canal == '':
        return JsonResponse(list(result), safe=False)
    
    idEst = int(estacion)
    idCan = int(canal)

    # Parche precipitacion Badajoz
    if idEst == 8010 and idCan == 301:
        idEst = 7010
        idCan = 301
    
    # Parche precipitacion Caceres
    if idEst == 7013 and idCan == 301:
        idEst = 1110
        idCan = 301


    tablaBD = Canales.objects.using('spd').filter(id_canal=idCan).values('tabla_bd')[0]
    modelDjango=getModelbyDbtable(tablaBD['tabla_bd'])

    if modelDjango!=None:
        fechahoraUTC_lim = datetime.utcnow() - timedelta(days=1)
        UTCzone = tz.tzutc()
        fechahoraUTC_lim = fechahoraUTC_lim.replace(tzinfo=UTCzone)
        #print("Fecha UTC", fechahoraUTC_lim)

        # Descargamaos las anteriores 24h
        result = modelDjango.objects.using('spd'
        ).filter(id_estacion=idEst, id_canal=idCan, fecha_hora_utc__gt=fechahoraUTC_lim
        ).values('fecha_hora_local', 'valor')

        if len(result)>0:
            df = pd.DataFrame()
            tzInfo = pytz.timezone('Europe/Madrid')
            df['fecha_hora_local'] = pd.date_range(datetime.today().date()+timedelta(days=-1), datetime.today(), freq='10min')
            df = df.loc[(df['fecha_hora_local'] >= datetime.today()+timedelta(days=-1))]
            #df['fecha_hora_local'] = df['fecha_hora_local'].dt.tz_convert('UTC').dt.tz_convert('Europe/Madrid')
            #df['fecha_hora_local'] = pd.date_range((datetime.now().astimezone(tz=pytz.timezone('Europe/Madrid')) - timedelta(days=1)).date(), datetime.now().astimezone(tz=pytz.timezone('Europe/Madrid')), freq='10min')
            #df['fecha_hora_local'] = pd.date_range((datetime.now().astimezone(tz=pytz.utc) - timedelta(days=1)).date(), datetime.now().astimezone(tz=pytz.utc), freq='10min')
            #df = df.loc[(df['fecha_hora_local'] >= datetime.now().astimezone(tz=pytz.utc) - timedelta(days=1))]
            #df['fecha_hora_local'] = df['fecha_hora_local'].dt.tz_convert('UTC').dt.tz_convert('Europe/Madrid')

            df1 = df
            df1['fecha_hora_local'] = df1['fecha_hora_local'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            df2 = pd.DataFrame(result)
            df2['fecha_hora_local'] = df2['fecha_hora_local'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

            df_final = pd.merge(df1, df2, on = ['fecha_hora_local'], how='left')
            df_final = df_final.groupby(['fecha_hora_local'], as_index=False)
            df_final = df_final.mean()
            df_final = df_final.replace({np.nan: None})

    return JsonResponse(df_final.to_dict('records'), safe=False)


def getDatosEmbalse(request):
    
    user = request.user
    result = {}
    
    estacion = request.GET.get('estacion','')

    if estacion == '':
        return JsonResponse(list(result), safe=False)
    
    idEst = int(estacion)
    idCan_VolPorcentual = 501
    idCan_CauAliviado = 201
    idCan_Precipitacion = 301

    fechahoraUTC_lim = datetime.utcnow() - timedelta(days=1)
    UTCzone = tz.tzutc()
    fechahoraUTC_lim = fechahoraUTC_lim.replace(tzinfo=UTCzone)

    volPorcentual = ValoresVisualizados10D.objects.using('spd').filter(id_estacion=idEst, id_canal=idCan_VolPorcentual, fecha_hora_utc__gt=fechahoraUTC_lim).values('fecha_hora_local', 'valor')
    CauAliviado = ValoresVisualizados10D.objects.using('spd').filter(id_estacion=idEst, id_canal=idCan_CauAliviado, fecha_hora_utc__gt=fechahoraUTC_lim).values('fecha_hora_local', 'valor')
    Precipitacion = ValoresPrecipitacion10D.objects.using('spd').filter(id_estacion=idEst, id_canal=idCan_Precipitacion, fecha_hora_utc__gt=fechahoraUTC_lim).values('fecha_hora_local', 'valor')
    
    result["volumen"] = list(volPorcentual)
    result["caudal"] = list(CauAliviado)
    result["precipitacion"] = list(Precipitacion)

    return JsonResponse(result, safe=False)


'''Datos: Valores del canal las anteriores 24 horas y futuras 24 horas'''
def getValoresPrediccion24h(request):
    
    user = request.user
    result = {}
    
    estacion = request.GET.get('estacion','')
    canal = request.GET.get('canal','')

    if estacion == '' or canal == '':
        return JsonResponse(list(result), safe=False)
    
    idEst = int(estacion)
    idCan_Datos_Registrados = int(canal)
    idCan_Datos_Predichos = idCan_Datos_Registrados + 1000

    # Parche precipitacion Badajoz
    if idEst == 8010 and idCan_Datos_Registrados == 301:
        idEst = 7010
        idCan_Datos_Registrados = 301
    
    # Parche precipitacion Caceres
    if idEst == 7013 and idCan_Datos_Registrados == 301:
        idEst = 1110
        idCan_Datos_Registrados = 301


    tablaBD_Datos_Registrados = Canales.objects.using('spd').filter(id_canal=idCan_Datos_Registrados).values('tabla_bd')[0]
    tablaBD_Datos_Predichos = Canales.objects.using('spd').filter(id_canal=idCan_Datos_Predichos).values('tabla_bd')[0]
  
    if tablaBD_Datos_Registrados!=None and tablaBD_Datos_Predichos!=None:
        modelDjango_Datos_Registrados=getModelbyDbtable(tablaBD_Datos_Registrados['tabla_bd'])
        modelDjango_Datos_Predichos=getModelbyDbtable(tablaBD_Datos_Predichos['tabla_bd'])
        
        fechahoraUTC_lim = datetime.utcnow() - timedelta(days=1)
        UTCzone = tz.tzutc()
        fechahoraUTC_lim = fechahoraUTC_lim.replace(tzinfo=UTCzone)
        print("Fecha UTC", fechahoraUTC_lim)

        # Descargamaos las anteriores 24h
        datos_registrados = modelDjango_Datos_Registrados.objects.using('spd'
        ).filter(id_estacion=idEst, id_canal=idCan_Datos_Registrados, fecha_hora_utc__gt=fechahoraUTC_lim
        ).values('fecha_hora_local', 'valor')

        if user.is_anonymous:
            datos_predichos=list()
        else:
            print("UTC PRUEBA", datetime.utcnow())
            datos_predichos = modelDjango_Datos_Predichos.objects.using('spd'
            ).filter(id_estacion=idEst, id_canal=idCan_Datos_Predichos, fecha_hora_utc__gte=datetime.utcnow(), fecha_hora_utc__lte=datetime.utcnow() + timedelta(hours=24)
            ).values('fecha_hora_local', 'valor')

            print("PREDICHOS", estacion)
            print(pd.DataFrame(datos_predichos))
        result["valores"] = list(datos_registrados)
        result["prediccion"] = list(datos_predichos)
    return JsonResponse(result, safe=False)

'''Datos: Valores del canal las anteriores 24 horas y futuras 24 horas'''
def getValoresRutinaEstacion(request):
    
    user = request.user
    result = {}
    
    estacion = request.GET.get('e','')

    if estacion == '':
        return JsonResponse(list(result), safe=False)
    
    idEst = int(estacion)
    fechahoraUTC_lim = datetime.utcnow() - timedelta(days=1)
    UTCzone = tz.tzutc()
    fechahoraUTC_lim = fechahoraUTC_lim.replace(tzinfo=UTCzone)

    val_nivel_rio = ValoresVisualizados10D.objects.using('spd'
                ).filter(id_canal=100, id_estacion = idEst, fecha_hora_utc__gte=fechahoraUTC_lim
                ).values('fecha_hora_local', 'valor') 
    val_pre_1h = ValoresPrecipitacion10D.objects.using('spd'
            ).filter(id_canal=301, id_estacion = idEst, fecha_hora_utc__gte=fechahoraUTC_lim, fecha_hora_utc__minute="00"
            ).values('fecha_hora_local', 'valor') 
    val_pre_1h_cuenca = ValoresPrecipitacion10D.objects.using('spd'
        ).filter(id_canal=302, id_estacion = idEst, fecha_hora_utc__gte=fechahoraUTC_lim
        ).values('fecha_hora_local', 'valor')
    
       
    result["nivel"] = list(val_nivel_rio)
    result["pre1h"] = list(val_pre_1h)
    result["pre1hcuenca"] = list(val_pre_1h_cuenca)

    return JsonResponse(result, safe=False)

''' Obtiene el nombre del model a partir del nombre de la tabla'''
def getModelbyDbtable(db_table):
    app_models = apps.get_app_config('spd').get_models()
    for model in app_models:
        if model._meta.db_table == db_table:
            return model
    
    return None

def get_diff(now, tzname):
    tz = pytz.timezone(tzname)
    utc = pytz.timezone('UTC')
    utc.localize(datetime.now())
    delta =  utc.localize(now) - tz.localize(now)
    print("DELTA", type(delta), delta.seconds/60/60)
    return delta

''' Obtiene el estado del cielo de las estaciones de pluviometria de Aemet'''
from django.http import HttpResponse
def getEstadoCieloAemet(request):
    
    diff = int(get_diff(datetime.utcnow(), 'Europe/Madrid').seconds/3600)
    now = datetime.now().astimezone(tz=pytz.timezone('Europe/Madrid'))
    cont=0

    url = 'http://www.aemet.es/es/api-eltiempo/variables/eCielo/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+0'+str(diff)+':00/01/D+'+str(cont)+'/70'
    peticionHttpAemet = requests.get(url)
    while len(peticionHttpAemet.text)==0 and cont<10:
        cont+=1
        url = 'http://www.aemet.es/es/api-eltiempo/variables/eCielo/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+0'+str(diff)+':00/01/D+'+str(cont)+'/70'
        peticionHttpAemet = requests.get(url)

    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)


def getTemperaturaAemet(request):
    
    diff = int(get_diff(datetime.utcnow(), 'Europe/Madrid').seconds/3600)
    now = datetime.now().astimezone(tz=pytz.timezone('Europe/Madrid'))
    cont=0

    peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/variables/Tempta/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+0'+str(diff)+':00/01/D+'+str(cont)+'/70')
    
    while len(peticionHttpAemet.text)==0 and cont<10:
        cont=cont+1
        peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/variables/Tempta/PB/7/'+now.strftime('%Y-%m-%dT%H')+':00:00+0'+str(diff)+':00/01/D+'+str(cont)+'/70')
        #peticionHttpAemet = requests.get('https://www.aemet.es/es/api-eltiempo/variables/Tempta/PB/7/2022-09-28T08:00:00+02:00/01/D+0/70')

    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)

'''Obtiene las imagenes de precipitacion acumulada 1 hora del modelo harmonie de Aemet'''
def getImagenesPreAcumAemet(request):
    hora = request.GET.get('h','')
    if int(hora)>1:
        hora=hora+'%20horas'
    else: 
        hora=hora+'%20hora'
    peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/modelo-harmonie/timeline/61/PB/'+hora)
    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)

'''Obtiene la ultima imagen del satelite radar de Aemet'''
def getImagenesRadar(request):
    peticionHttpAemet = requests.get('http://www.aemet.es/es/api-eltiempo/radar/timeline/RN1/PB')
    result = peticionHttpAemet.json()
    return JsonResponse(result, safe=False)

'''Devuelve los colores de la leyenda de la Precipitacion Acum 1 hora del Radar de Aemet'''
def getLegendaRadar(request):
    peticionLegendModelosNumericos = requests.get('http://www.aemet.es/es/api-eltiempo/radar/leyenda-radar/RN1')
    result = peticionLegendModelosNumericos.json()
    return JsonResponse(result, safe=False)

'''Obtiene las zonas meteorologicas de aemet'''
def getAvisosMeteorologicos(request):
    avisos = ZonaMeteoalertaAemet.objects.using('spida').values()
    return JsonResponse(list(avisos), safe=False)

'''Obtiene el listado con información detallada de los avisos meteorologicos'''
def getAvisosMeteorologicosInformacion(request):
    print("DATETIME AVISOS", datetime.now())
    #df=pd.DataFrame(columns=['nivel', 'zona_aemet', 'infoDate', 'descripcion', 'instruccion', 'probabilidad'])
    df=pd.DataFrame()
    info_avisos = AvisosMeteorologicosAemet.objects.using('spd'
    ).filter(valido_actual=1, fecha_fin__gte=datetime.now()
    ).values().order_by('-fecha_emision','fecha_comienzo', 'fecha_fin')
    
    #info_avisos = AvisosMeteorologicosAemet.objects.using('spida'
    #).filter(valido_actual=1, fecha_fin__gte=datetime.now()
    ##).annotate(infoDate = Concat(
    ##                    Func(F('fecha_comienzo'), Value('%d %b %Y %H:%m'), function='DATE_FORMAT'), 
    ##                    Value(" a "), 
    ##                    Func(F('fecha_fin'), Value('%d %b %Y %H:%m'), function='DATE_FORMAT'), 
    ##                    output_field=CharField())  
    ##).filter(fecha_comienzo__gte=datetime(2022, 9, 12)
    ##).values('nivel', 'zona_aemet', 'infoDate', 'descripcion', 'instruccion', 'probabilidad').order_by('fecha_comienzo', 'fecha_fin')
    #).values('nivel', 'zona_aemet', 'fecha_comienzo','fecha_fin', 'descripcion', 'instruccion', 'probabilidad').order_by('fecha_comienzo', 'fecha_fin')
    
    if len(info_avisos)>0:
        df= pd.DataFrame(info_avisos)
        df['fecha_comienzo']= pd.to_datetime(df.fecha_comienzo).dt.strftime('%d %b %Y %H:%M')
        df['fecha_fin']= pd.to_datetime(df.fecha_fin).dt.strftime('%d %b %Y %H:%M')
        df['infoDate']=df['fecha_comienzo']+" a "+df['fecha_fin']


    return JsonResponse(df.to_dict('records'), safe=False)   

'''Devuelve los colores de la leyenda de la Precipitacion Acum 1 hora de los modelos numericos de Aemet'''
def getLegendaModelosNumericos(request):
    peticionLegendModelosNumericos = requests.get('http://www.aemet.es/es/api-eltiempo/modelo-harmonie/leyenda/61/PB')
    result = peticionLegendModelosNumericos.json()
    return JsonResponse(result, safe=False)

'''Descargar: Documento Adjunto de un Evento'''
def DownloadDocumento(request):
    user = request.user
    nameDocumento = request.GET.get('doc','')
    documento = DocumentacionAdjunto.objects.using('spd').filter(nombre=nameDocumento)[0]
    return FileResponse(open(settings.MEDIA_ROOT + documento.ruta, 'rb'), content_type='application/force-download')


'''Descargar: Informe Trimestral Spida'''
def DownloadInformeTrimestral(request):
    user = request.user
    nameInforme = request.GET.get('i','')
    informe = InformesTrimestrales.objects.using('spd').filter(nombre=nameInforme)[0]
    return FileResponse(open(settings.MEDIA_ROOT + informe.ruta, 'rb'), content_type='application/force-download')


'''Abrir (ver): de la documentacion adjuntada de un evento solo los archivos con formato pdf, jpg, jpeg, png y gif'''
def ViewDocumento(request):
    user=request.user
    nameDocumento = request.GET.get('doc','')
    contenido = DocumentacionAdjunto.objects.using('spd').filter(nombre=nameDocumento)[0]
    return FileResponse(open(settings.MEDIA_ROOT + contenido.ruta, 'rb'))


'''Abrir (ver): Informe Trimestral Spida'''
def ViewInformeTrimestral(request):
    user = request.user
    nameInforme = request.GET.get('i','')
    contenido = InformesTrimestrales.objects.using('spd').filter(nombre=nameInforme)[0]
    return FileResponse(open(settings.MEDIA_ROOT + contenido.ruta, 'rb'), content_type='application/pdf')

'''Abrir (ver): Protocolo de Actuación SPIDA/INUNCAEX'''
def ViewProtocolo(request):
    user = request.user
    urlProtocolo = '/SPIDA/PROTOCOLO/PROTOCOLO_SPIDA_INUNCAEX.pdf'
    return FileResponse(open(settings.MEDIA_ROOT + urlProtocolo, 'rb'), content_type='application/pdf')

'''Recibe una lista de estaciones y la convierte en un json'''
def list_to_geojson(list, properties,lat,lon):
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
