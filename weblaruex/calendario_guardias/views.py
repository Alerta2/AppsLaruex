from email import message
from django.conf import settings
from matplotlib.pyplot import text
from telegram import *
from telegram.ext import *
from telegram.chat import *
from telegram.message import *
from distutils.log import info
from logging import exception
from unittest import result
from aiohttp_jinja2 import context_processors_middleware
from django.shortcuts import render
from ast import Return, While
from math import fabs
from aiohttp import request
from django.shortcuts import render
import numpy
from structure.models import Profile
from django.contrib.auth.models import User
from django.http import JsonResponse
from datetime import datetime, time, timedelta, tzinfo
import locale
import json
import random
import isoweek
import math
import collections
import pandas as pd
from django.db.models import F, Value, ExpressionWrapper, DateField,  Case, When, Q, Func, Sum
from django.db.models.functions import Concat, ExtractWeek,  ExtractMonth 
from django.db.models.fields import IntegerField, CharField
from .models import CalendarioAreas, CalendarioGuardiasGuardias, CalendarioTurnos, CalendarioPersonal, CalendarioFestivos, CalendarioCambiosGuardias, MensajesPendienteCorfirmacion, MensajesTelegram, MensajesTelegramHistorico, MonitorizaApps
from django.contrib.auth.decorators import permission_required
import re
import cryptocode
import pytz
from dateutil import tz
import yaml
import numpy as np



# Create your views here.

'''Return: HTML template (Visor del Calendario de guardias ALERTA2-LARUEX)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def VisorOperatividadApps(request):  
    return render(request,"operatividad_apps.html", {"user": request.user}) 


'''Return: HTML template (Visor del Calendario de guardias ALERTA2-LARUEX)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def VisorCalendarioGuardias(request): #Obtengo las guardias que estan activas en el día de hoy   
    tzInfo = pytz.timezone('Europe/Madrid')
    fecha_hora_actual = datetime.now().astimezone(tzInfo)
    today = fecha_hora_actual.strftime("%Y-%m-%d")
    current_time = fecha_hora_actual.strftime("%H:%M:%S")
    
    guardiasToday= CalendarioGuardiasGuardias.objects.using("guardias"
    ).filter( valido = 1, supervisado=1, fecha_local_start__lte=today, fecha_local_end__gte=today
    ).filter(id_turno__hora_local_comienzo__lte = current_time, id_turno__hora_local_fin__gte=current_time
    ).annotate(id_user=F('id_user_analista'), 
                area=F('id_turno__id_area__nombre'), 
                hora_entrada= F('id_turno__hora_local_comienzo'),
                hora_salida= F('id_turno__hora_local_fin'),
                icono = F('id_turno__id_area__icono')
    ).values('id_user','area', 'hora_entrada', 'hora_salida','icono').order_by('area', '-id_guardia')

    #Obtengo la informacion del personal que esta activo de guardia en estos momentos
    if guardiasToday.count()>0:
        df_personal = pd.DataFrame(guardiasToday)
        df_personal["nombre"] = df_personal.apply(lambda row : User.objects.get(id=row['id_user']).first_name, axis = 1)
        df_personal["telefono"] = df_personal.apply(lambda row : getNumberPhone(User.objects.get(id=row['id_user'])), axis = 1)
        df_personal['avatar'] = df_personal.apply(lambda row : getAvatar(User.objects.get(id=row['id_user'])), axis = 1)

        df_personal = df_personal.drop_duplicates(subset = ["area"])
    
        jsonPersonal = df_personal.to_json(orient="records")
        jsonPersonal = json.loads(jsonPersonal)
        jsonPersonal =  json.dumps(jsonPersonal)

    else:
        df_personal = pd.DataFrame()

    #Obtengo todas las areas de trabajo junto con su informacion 
    areas = CalendarioTurnos.objects.using('guardias'
    ).annotate(area= F('id_area__nombre'),
            icono = F('id_area__icono'),
            color = F('color_fondo'),
            info = Concat(F('descripcion'), Value(" (De "), F('hora_local_comienzo'), Value(' a '), F('hora_local_fin'), Value(")"), output_field=CharField())
    ).values('area','icono', 'color', 'info').order_by('area', 'hora_local_comienzo' ,'-hora_local_fin')
    
    return render(request,"cg_visor_calendario.html", {"user": request.user, "Personal":df_personal.to_dict('records'), "Areas": list(areas)}) 

'''Return: HTML (Configuración del Perfil del Usuario logueado)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def PerfilUsuario(request):
    return render(request,"cg_perfil_usuario.html",{"user": request.user})

@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def PersonalCalendarioGuardias(request):  
    
    personal = CalendarioPersonal.objects.using("guardias").filter(operativo=1)
    info_personal=[]
    for analista in personal:
        user = User.objects.get(id=analista.id_usuario)
        usuario={}
        usuario["id"]= user.id
        usuario["nombre"]=user.first_name
        usuario["apellidos"]=user.last_name
        usuario["id_area"]=analista.id_area.id_area
        usuario["area"]=analista.id_area.nombre
        usuario["icono"]=analista.id_area.icono
        usuario["avatar"] = getAvatar(user)
        info_personal.append(usuario)

    return render(request,"cg_personal.html", {"user": request.user, "Personal":info_personal})

'''Return: HTML template (Para crear un nuevo calendario anual de guardias)'''
@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def NuevoCalendarioGuardias(request):
    return render(request,"cg_nuevo_calendario.html", {"user": request.user})

'''Return: HTML template (Para mostrar las notificaciones, cambios solicitados, 
solicitudes pendientes de cambios, cambios realizados etc...'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def MiTablonGuardias(request):
    return render(request,"cg_tablon_personal.html", {"user": request.user})

'''Return: HTML template (Para aceptar/rechazar cambios solicitados, 
y sustituciones de los analistas. Apartado para el supervisor/Director del centro)'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def SupervisionGuardias(request):
    return render(request,"cg_supervision.html", {"user": request.user})

'''Return: HTML template (Para consultar el historico de cambios solicitados'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def HistoricoCambiosGuardia(request):
    return render(request,"cg_historico.html", {"user": request.user})

@permission_required('auth.calendario_guardias', login_url='/acceso/analista/')
def ConfirmacionTelegram(request):
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    id_area = None
    id_chat = None
    id_mensaje = None
    info = request.GET.get('i', None)

    try:
        if info!=None:
            json_info = yaml.safe_load(info)
            id_area = json_info.get('a', None)
            id_mensaje = json_info.get('m', None)
            id_chat = json_info.get('c', None) 

        print("AREA", id_area, "MENSAJE", id_mensaje, "CHAT", id_chat)
        df_analista = pd.DataFrame()
        autorizado = False
        if id_mensaje!=None and id_chat!=None and id_area!=None:
            tzInfo = pytz.timezone('Europe/Madrid')
            fecha_hora_actual = datetime.now().astimezone(tzInfo)
            today = fecha_hora_actual.strftime("%Y-%m-%d")
            current_time = fecha_hora_actual.strftime("%H:%M:%S")
        
            #Obtengo a los analistas que se encuentran de guardia para el area especificada
            analistas = CalendarioGuardiasGuardias.objects.using('guardias'
                    ).filter(id_turno__id_area=int(float(id_area)),
                            valido = 1, 
                            supervisado = 1,
                            fecha_local_start__lte = today,
                            fecha_local_end__gte = today
                    ).filter(id_turno__hora_local_comienzo__lte = current_time, 
                            id_turno__hora_local_fin__gte=current_time
                    ).annotate(id_user=F('id_user_analista'), 
                            area=F('id_turno__id_area__nombre'), 
                            hora_entrada= F('id_turno__hora_local_comienzo'),
                            hora_salida= F('id_turno__hora_local_fin'),
                            icono = F('id_turno__id_area__icono')
                    ).values('id_user','area', 'hora_entrada', 'hora_salida','icono').order_by('-id_guardia')
                
            #Obtengo la informacion del personal que esta activo de guardia en estos momentos
            if analistas.count()>0:
                df_analista = pd.DataFrame(analistas)
                df_analista = df_analista.drop_duplicates(subset = ["area"]) # Me quedo unicamente con el primer analista que debe encontrarse de guaardia
                df_analista["nombre"] = df_analista.apply(lambda row : User.objects.get(id=row['id_user']).first_name, axis = 1)

                if request.user.id == df_analista.iloc[0]['id_user']:
                    print("AUTORIZADO")
                    autorizado = True
                else:
                    print("NO AUTORIZADO")
                    #Compruebo si el analista que quiere confirmar ha recibido mensajes en la ultima hora de este area
                    autorizado = False
                
                bot = Bot(token=settings.TOKEN_TELEGRAM)

        if autorizado == True: # Analista de guardia autorizado para confirmar el mensaje
            men_telegram_confirm = MensajesPendienteCorfirmacion.objects.using("guardias").filter(id_mensaje_telegram = id_mensaje, id_telegram = id_chat, id_area = int(float(id_area)))
            if men_telegram_confirm.exists(): #Si el mensaje está aun por confirmar ...
                #Si aún existe el mensaje lo actualizo en el historico y lo elimino de los pendientes de confirmacion
                df_men_telegram_confirm = pd.DataFrame(men_telegram_confirm.values())
                print(df_men_telegram_confirm)
                for men in df_men_telegram_confirm.itertuples():
                    MensajesTelegramHistorico.objects.using('guardias'
                        ).filter(id_mensaje = men.id_mensaje
                        ).update(id_mensaje_telegram = men.id_mensaje_telegram,
                                fecha_hora_utc_confirmacion = fecha_hora_actual.astimezone(pytz.utc),
                                analista = request.user.id)
                men_telegram_confirm.delete()

                #Finalmente edito el mensaje de telegram con el Nombre del Analista que lo ha confirmado junto con la fecha/hora de confirmacion    
                buttonsMenu = [[InlineKeyboardButton("\U00002705 Confirmado", callback_data='<confirmado>'+ request.user.first_name + ' ' + request.user.last_name + ' ' + fecha_hora_actual.strftime("%d %b, %Y, a las %H:%M") +' h')]]
                keyboard_markup = InlineKeyboardMarkup(buttonsMenu)
                bot.edit_message_reply_markup(chat_id=id_chat,
                                        message_id=id_mensaje, 
                                        reply_markup=keyboard_markup) 
                mensaje = "El aviso notificado ha sido confirmado"
                icono = "success"
            else: #Si el mensaje ya ha sido confirmado le muestro un mensaje al analista
                men_telegram_histo = MensajesTelegramHistorico.objects.using("guardias").filter(id_mensaje_telegram = id_mensaje, id_telegram = id_chat, id_area = int(float(id_area))).exclude(fecha_hora_utc_confirmacion__isnull=True).exclude(analista__isnull=True) #.exclude(analista__exact='') (vacio)
                if men_telegram_histo.exists(): 
                    df_men_telegram_histo = pd.DataFrame(men_telegram_histo.values())
                    df_men_telegram_histo['nameAnalista'] = df_men_telegram_histo.apply(lambda row: User.objects.get(id=row['analista']).first_name, axis=1)
                    mensaje =  str(df_men_telegram_histo.iloc[0]['nameAnalista']) + " ha confirmando el aviso notificado con motivo de tu respuesta tardía al mismo"
                    icono = "warning"
                else:
                    mensaje = "El aviso notificado ya ha sido confirmado por otro analista pero se ha producido un error al intentar consultar su identidad."
                    icono = "error"

        else: # Analista no autorizado para confirmar el mensaje
            mensaje = "No estás autorizado para realizar la confirmación del aviso notificado"
            icono = "error"

            # Comprobar si el analista se encuentra entre los de respaldo
            '''
            buttonsMenu = [[InlineKeyboardButton("\U00002705 Confirmado", callback_data='<confirmado>'+ request.user.first_name + ' ' + request.user.last_name + ' ' + datetime.now().strftime("%d %b, %Y, a las %H:%M") +' h')]]
            keyboard_markup = InlineKeyboardMarkup(buttonsMenu)
            bot.edit_message_reply_markup(chat_id=id_chat,
                                    message_id=id_mensaje, 
                                    reply_markup=keyboard_markup) '''
            
            '''men_telegram_confirm = MensajesTelegramCorfirmacion.objects.using("guardias").filter(id_mensaje_telegram = id_mensaje, id_telegram = id_chat, id_area = int(float(id_area)))
            if men_telegram_confirm.exists(): #Si el mensaje está aun por confirmar ...
                #Si aún existe el mensaje lo añado al historico y lo elimino de los pendientes de confirmacion
                df_men_telegram_confirm = pd.DataFrame(men_telegram_confirm.values())
                for men in df_men_telegram_confirm.itertuples():
                    MensajesTelegramHistorico.objects.using('guardias'
                        ).create(id_mensaje = men.id_mensaje,
                                id_area = men.id_area,
                                id_estacion = men.id_estacion,
                                id_canal = men.id_canal,
                                fecha_hora_local = men.fecha_hora_local,
                                mensaje = men.mensaje,
                                descripcion = men.descripcion,
                                icono = men.icono,
                                estado = men.estado,
                                id_telegram = men.id_telegram,
                                silenciar = men.silenciar,
                                confirmar = men.confirmar,
                                tipo_mensaje_enviado = men.tipo_mensaje_enviado,
                                enviado = men.enviado,
                                id_mensaje_telegram = men.id_mensaje_telegram,
                                fecha_hora_local_confirmacion = datetime.now(),
                                analista = request.user.id)
                men_telegram_confirm.delete()

                #Finalmente edito el mensaje de telegram con el Nombre del Analista que lo ha confirmado junto con la fecha/hora de confirmacion    
                buttonsMenu = [[InlineKeyboardButton("\U00002705 Confirmado", callback_data='<confirmado>'+ request.user.first_name + ' ' + request.user.last_name + ' ' + datetime.now().strftime("%d %b, %Y, a las %H:%M") +' h')]]
                keyboard_markup = InlineKeyboardMarkup(buttonsMenu)
                bot.edit_message_reply_markup(chat_id=id_chat,
                                        message_id=id_mensaje, 
                                        reply_markup=keyboard_markup) 
                mensaje = "El aviso notificado ha sido confirmado"
                icono = "success"'''
            
    except Exception as e:
        print("ERROR", e)
        mensaje = "Se ha producido un error. Comunícaselo al responsable de informática."
        icono = "error"

      
    return render(request,"cg_confirmacion.html", {"user": request.user, "autorizado": autorizado, "mensaje":mensaje, "icono":icono})







'''DATOS: URL (Imagen del Profile del usuario)'''
def getAvatar(usuario):
    if hasattr(usuario, 'profile'): #Si existe profile para el usuario
        return usuario.profile.image.url
    else:
        return "../../../../media/profile/default.png"

'''DATOS: TELEFONO (Numero de telefono del analista)'''
def getNumberPhone(usuario):
    if hasattr(usuario, 'profile'): #Si existe profile para el usuario
        return usuario.profile.telefono
    else:
        return ""

'''DATOS: JSON (Listado de todo el pesonal operativo en el calendario de guardias
al cual le dacilita un color identificativo)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getColoresPersonal(request):
    area = request.GET.get('a','')

    ColoresPersonal=[]
    if area!= "":
        coloresUsers = ["#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144"]
        
        personal = CalendarioPersonal.objects.using('guardias').filter(id_area=int(area), operativo=1)

        idx=0
        for analista in personal:
            ColoresPersonal.append([analista.id_usuario, #id_usuario
                                    coloresUsers[idx]]) #color que representa al usuario
            idx +=1
        df_Colores_Personal = pd.DataFrame(ColoresPersonal, columns=['idUser', 'color'])
    
    return JsonResponse(df_Colores_Personal.to_dict('records'), safe=False)

'''DATOS: JSON (Listado de todos los turnos de trabajo y sus colores representativos)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getColoresTurnos(request):

    ColoresTurnos=[]   
    turnos = CalendarioTurnos.objects.using('guardias')

    idx=0
    for turno in turnos:
        ColoresTurnos.append([turno.id_turno, #id_usuario
                                turno.color_fondo]) #color que representa al usuario
        idx +=1
    df_Colores_Turno = pd.DataFrame(ColoresTurnos, columns=['idTurno', 'color'])
    
    return JsonResponse(df_Colores_Turno.to_dict('records'), safe=False)


'''DATOS: JSON (Listado de todo el pesonal operativo en el calendario de guardias
al cual le dacilita un color identificativo)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getColoresUsuarios(request):
    area = request.GET.get('a','')

    personal = CalendarioPersonal.objects.using('guardias').values('id_usuario')
    df_personal = pd.DataFrame(personal)
    df_personal = df_personal['id_usuario'].unique()

    print(df_personal)

    ColoresUsuarios=[]
    coloresUsers = ["#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144",
                    "#277da1", "#577590", "#4d908e", "#43aa8b", "#90be6d", "#f9c74f", "#f9844a", "#f8961e", "#f3722c", "#f94144"]
    idx=0
    for user in df_personal:
        ColoresUsuarios.append([user, #id_usuario
                                coloresUsers[idx]]) #color que representa al usuario
        idx +=1

    df_Colores_Usuarios = pd.DataFrame(ColoresUsuarios, columns=['idUser', 'color'])
 
    return JsonResponse(df_Colores_Usuarios.to_dict('records'), safe=False)

'''DATOS: JSON (Listado de los analistas que pueden ser datos de alta en el Calendario de guardias)
    Formato especifico para insertarlo en un input select de sweetalert'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getUsers(request):
    area = request.GET.get('area','')
    
    usuarios_area = CalendarioPersonal.objects.using('guardias').filter(id_area__id_area=area, operativo = 1).values('id_usuario')
    if usuarios_area.count()>0:
        usuarios_area = pd.DataFrame(list(usuarios_area))
    else:
        usuarios_area = pd.DataFrame(columns=['id_usuario'])

    usuarios = User.objects.all().values('id','username', 'first_name', 'last_name').order_by('first_name')
    usuarios = pd.DataFrame(list(usuarios))
    usuarios = usuarios.loc[~usuarios['id'].isin(usuarios_area['id_usuario'].tolist())]    
    #usuarios = usuarios.sort_values(by=['first_name'])

    dictUsuarios={}
    for index, row in usuarios.iterrows():
        if row['first_name']=="":
             dictUsuarios[row['id']]=row['username']
        else:
             dictUsuarios[row['id']]=row['first_name']+' '+row['last_name']+' ('+row['username']+')'

    print(dictUsuarios)
    
    resultjson = json.dumps(dictUsuarios)


    return JsonResponse(resultjson, safe=False)


'''DATOS: JSON (Listado con todos las areas y su personal)
Formato especial para la filtracion del Calendario'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getTreeViewAreasPersonal(request):
    
    areas = CalendarioAreas.objects.using("guardias").values('id_area', 'nombre','icono','descripcion')
    
    result=[]

    for area in areas:
        print(area)
        areaAux={}
        areaAux['id'] = None
        areaAux['id_area']=area['id_area']
        areaAux['text']=area['nombre']
        areaAux['checked']= False
        areaAux['faCssClass'] = area['icono']
          
        personal= CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = area['id_area'])
        usuarios=[]
        for analista in personal:
            user = User.objects.get(id=analista.id_usuario)
            usuario={}
            usuario["id"]= str(analista.id_area.id_area)+"-"+str(analista.id_usuario)
            usuario["id_user"]=analista.id_usuario
            usuario["id_area"]=area['id_area']
            usuario["nameUser"] = user.first_name+" "+user.last_name
            if analista.operativo == 1:
                usuario["text"]=user.first_name+" "+user.last_name
            else:
                usuario["text"]='<span style="color:#C0C0C0">'+user.first_name+" "+user.last_name +'</span>'
            usuario["avatar"]= getAvatar(user)
            areaAux['checked']= False
            usuario['imageHtml']='<img  src="' + getAvatar(user) + '" alt=""  style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;"/>'
            usuario['operativo']=analista.operativo
            usuarios.append(usuario)

        usuarios = sorted(usuarios, key=lambda d: d['nameUser']) 
        areaAux['children']=usuarios #Obtengo el listado del personal vigente para la realización de guardias del area estudiada
        
        result.append(areaAux)
   
    return JsonResponse(list(result), safe=False)

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

'''DATOS: JSON (Listado con todas las guardias que deben ser visualizadas
 en el Visor del Calendario de Guardias)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getGuardias(request):  
    guardias=CalendarioGuardiasGuardias.objects.using("guardias").filter(valido = 1, supervisado = 1
        ).annotate(
            start=F('fecha_local_start'),
            end=ExpressionWrapper(F('fecha_local_end')+ timedelta(days=1), output_field=DateField()),
            group =  Case( When(tipo_guardia=2, then=Value('sustitucion')),
                            output_field=CharField(),
                            default=Value('guardias'),
                    ), 
            idUser=F('id_user_analista'),
            idArea=F('id_turno__id_area__id_area'),
            icono =  F('id_turno__id_area__icono'),
            nameArea = F('id_turno__id_area__nombre'),
            hora_inicio = F('id_turno__hora_local_comienzo'),
            hora_fin = F('id_turno__hora_local_fin'),
            #backgroundColor = F('id_turno__color_fondo'),
            turno = F('id_turno__id_turno'),
            idUserMod = F('id_user_modificado'),
        ).values('start','end','icono', 'group', 'idUser','idArea', 'nameArea', 'id_guardia', 'semana', 'hora_inicio', 'hora_fin', 'turno', 'idUserMod'
        ).order_by('idArea', 'start', 'id_guardia')

    if guardias.count()>0:
        df=pd.DataFrame(guardias)
        df['avatar'] = df.apply(lambda row : getAvatar(User.objects.get(id=row['idUser'])), axis = 1)
        df['nameUser'] = df.apply(lambda row : User.objects.get(id=row['idUser']).first_name, axis = 1)
    else:
        df= pd.DataFrame()

    return JsonResponse(df.to_dict('records'), safe=False)


'''DATOS: JSON (Listado con los analistas pertenecientes a un area)
    Formato especifico para insertarlo en un input select de sweetalert'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getSustituto(request):

    area = request.GET.get('a','') #obtengo el id del area de trabajo
    user = request.GET.get('u','')

    dictPersonal={}

    if area!='':
        personal = CalendarioPersonal.objects.using("guardias").filter(id_area=int(area), operativo=1).exclude(id_usuario=user).values('id_usuario')
        for analista in personal:
            infoUser = User.objects.get(id=analista['id_usuario'])
            dictPersonal[analista['id_usuario']]=infoUser.first_name + ' '+infoUser.last_name +' ('+infoUser.username+')'

    resultjson = json.dumps(dictPersonal)
    return JsonResponse(resultjson, safe=False)



'''DATOS: JSON (Listado con todas las guardias con las que puedo realizar un cambio)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getGuardiasCambios(request):
    
    area = request.GET.get('a','')
    id_user = request.GET.get('u','')
    idTurno = request.GET.get('t','')

    if area !="":
        today = datetime.today()

        turno = CalendarioTurnos.objects.using("guardias").get(id_turno = int(idTurno))

        guardias=CalendarioGuardiasGuardias.objects.using("guardias"
            ).filter(tipo_guardia__in = [1,3], 
                        supervisado = 1, 
                        valido = 1, 
                        id_turno = turno,
                        fecha_local_start__gt=today, 
            ).exclude(id_user_analista=id_user
            ).annotate(
                start=F('fecha_local_start'),
                end=ExpressionWrapper(F('fecha_local_end')+ timedelta(days=1), output_field=DateField()),
                group = Value('guardias',output_field=CharField()),
                icon =  F('id_turno__id_area__icono'), 
                idUser=F('id_user_analista'),
                idArea=F('id_turno__id_area__id_area'),
                nameArea = F('id_turno__id_area__nombre'),
                backgroundColor = F('id_turno__color_fondo'),
            ).values('start','end','icon', 'group', 'idUser','idArea', 'nameArea', 'id_guardia', 'semana', 'backgroundColor')

        if guardias.count()>0:
            df=pd.DataFrame(guardias)
            df['avatar'] = df.apply(lambda row : getAvatar(User.objects.get(id=row['idUser'])), axis = 1)
            #df['title'] = df.apply(lambda row : User.objects.get(id=row['idUser']).first_name, axis = 1)
            df['nameUser'] =df.apply(lambda row: User.objects.get(id=row['idUser']).first_name, axis=1)
        else:
            df=pd.DataFrame()

    return JsonResponse(df.to_dict('records'), safe=False)


'''DATOS: JSON (Listado con el estado de mis sustituciones)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getSustituciones(request):
    
    sustituciones = CalendarioGuardiasGuardias.objects.using('guardias'
    ).filter(tipo_guardia=2
    ).filter(Q(id_user_modificado = request.user.id) | Q(id_user_analista = request.user.id)
    ).order_by('supervisado', 'fecha_local_start', 
    ).annotate(
        solicitante = F('id_user_modificado'),
        sustituto = F('id_user_analista'),
        fecha_sustitucion = F('fecha_local_start'),
        area = F('id_turno__id_area__nombre'),
        icono = F('id_turno__id_area__icono'),
        estado = Case( When(supervisado=0, then=Value('Pendiente')),
                        When(supervisado=1, then=Value('Aceptada')),
                        When(supervisado=2, then=Value('Rechazada')),
                        output_field=CharField(),
                        default=Value('Indefinido'),
                    ),
        color = Case(When(supervisado=0, then=Value('#A9A9A9')),
                        When(supervisado=1, then=Value('#3CB371')),
                        When(supervisado=2, then=Value('#8B0000')),
                        output_field=CharField(),
                        default=Value('#000000')
                    ),
        creador = F('id_user_modificado'),
        turno = Concat(F('id_turno__descripcion'), Value(' (De '), F('id_turno__hora_local_comienzo'), Value(' a '), F('id_turno__hora_local_fin'), Value(')'), output_field=CharField()), 
    ).order_by('supervisado'
    ).values('id_guardia', 'solicitante', 'sustituto', 'fecha_sustitucion', 'area', 'icono', 'turno', 'estado', 'color', 'creador')

    if sustituciones.count()>0:
        df_sustituciones = pd.DataFrame(sustituciones)
        df_sustituciones["avatar_solicitante"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['solicitante'])), axis = 1)
        df_sustituciones["avatar_sustituto"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['sustituto'])), axis = 1)
        df_sustituciones["solicitante"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['solicitante']).first_name, axis = 1)
        df_sustituciones["sustituto"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['sustituto']).first_name, axis = 1)
    else:
        df_sustituciones = pd.DataFrame()
    return JsonResponse(df_sustituciones.to_dict('records'), safe=False)


'''DATOS: JSON (Listado con el estado de mis cambios de guardia)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getCambiosGuardias(request):

    cambios = CalendarioCambiosGuardias.objects.using('guardias'
    ).filter( Q(id_user_emisor = request.user.id) | Q(id_user_receptor=request.user.id) 
    ).annotate(emisor = F("id_user_emisor"),
              receptor = F("id_user_receptor"),
              idArea=F('id_turno__id_area__id_area'),
              area =  F('id_turno__id_area__nombre'),
              icono = F('id_turno__id_area__icono'),
              turno = F('id_turno__id_turno'),
              semana_emisor = F("sem_guardia_emisor"),
              semana_receptor =F("sem_guardia_receptor"),
              year_emisor = F('year_sem_guardia_emisor'),
              year_receptor = F('year_sem_guardia_receptor'),
              estado = Case( When(supervisado=0, then=Value('Pendiente')),
                        When(supervisado=1, then=Value('Aceptada')),
                        When(supervisado=2, then=Value('Rechazada')),
                        output_field=CharField(),
                        default=Value('Indefinido'),
                    ),
              color = Case(When(supervisado=0, then=Value('#A9A9A9')),
                        When(supervisado=1, then=Value('#3CB371')),
                        When(supervisado=2, then=Value('#8B0000')),
                        output_field=CharField(),
                        default=Value('#000000')
                    )
    ).order_by('supervisado'
    ).values("id_cambio", "emisor", "receptor", "idArea", "area", "icono", "turno", "semana_emisor", "semana_receptor", "year_emisor", "year_receptor", "estado", "color")

    if cambios.count()>0:
        df_cambios = pd.DataFrame(cambios)
        df_cambios["avatar_emisor"]=  df_cambios.apply(lambda row : getAvatar(User.objects.get(id=row['emisor'])), axis = 1)
        df_cambios["avatar_receptor"]=  df_cambios.apply(lambda row : getAvatar(User.objects.get(id=row['receptor'])), axis = 1)
        df_cambios["nameEmisor"] = df_cambios.apply(lambda row : User.objects.get(id=row['emisor']).first_name, axis = 1)
        df_cambios["nameReceptor"] = df_cambios.apply(lambda row : User.objects.get(id=row['receptor']).first_name, axis = 1)
        df_cambios["infoEmisor"] = df_cambios.apply(lambda row : get_array_infoGuardias(row['year_emisor'], row['semana_emisor'], row['turno'], row['emisor']), axis = 1)
        df_cambios["infoReceptor"] = df_cambios.apply(lambda row : get_array_infoGuardias(row['year_receptor'], row['semana_receptor'], row['turno'], row['receptor']), axis = 1) 
            
    else:
        df_cambios = pd.DataFrame()

    return JsonResponse(df_cambios.to_dict("records"), safe=False)

def get_array_infoGuardias(year, semana, turno, idUser):
    rows = CalendarioGuardiasGuardias.objects.using("guardias"
    ).filter(year = int(year),
            semana = int(semana), 
            id_turno__id_turno = int(turno), 
            id_user_analista = int(idUser)
    ).annotate(infoDate = Concat(Value("Del "), 
                                Func(F('fecha_local_start'), Value('%d-%b-%Y'), function='DATE_FORMAT'), 
                                Value(" al "), 
                                Func(F('fecha_local_end'), Value('%d-%b-%Y'), function='DATE_FORMAT'), 
                                output_field=CharField())     
    ).values('infoDate').order_by('fecha_local_start')

    result = [row["infoDate"] for row in rows]
    result = list(set(result))
    return result

'''DATOS: JSON (Listado con todas mis guardias y las sustituciones que me hacen (pendientes o aceptadas))'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getMisGuardias(request):
    idUser = request.user.id

    guardias=CalendarioGuardiasGuardias.objects.using("guardias"
            ).filter((Q(id_user_analista = idUser) & Q(tipo_guardia__in = [1,3]) & Q(supervisado = 1) & Q(valido = 1)) | #mis guardias oficiales activas
                    (Q(id_user_analista = idUser) & Q(tipo_guardia = 2) & Q(supervisado__lt = 2) & Q(valido = 1)) #mis sustotuciones pendientes o aceptadas
            ).annotate(
                start=F('fecha_local_start'),
                end=ExpressionWrapper(F('fecha_local_end')+ timedelta(days=1), output_field=DateField()),
                backgroundColor = Case( When(tipo_guardia = 2, supervisado = 0, then=Value('#A9A9A9')), #Sustituciones Pendientes
                                        When(tipo_guardia = 2, supervisado = 1, then=Value('#00FA9A')), #Sustituciones Aceptadas
                                        When(id_user_analista = idUser, then=Value('#007bff')), #Guardias oficiales
                                        default=Value('#007bff'),
                                        output_field=CharField()),                
                borderColor = Value('#fff', output_field=CharField()),
                textColor=Case( When(Q(tipo_guardia = 2) | Q(supervisado=0), then=Value('#000000')),
                                        default=Value('#fff'),
                                        output_field=CharField()), 
                icon =  F('id_turno__id_area__icono'),
                group = Value('guardias',output_field=CharField()),
                id_user=F('id_user_analista'),
                id_area=F('id_turno__id_area__id_area'),
                area = F('id_turno__id_area__nombre'),
                hora_inicio = F('id_turno__hora_local_comienzo'),
                hora_fin = F('id_turno__hora_local_fin')
            ).values('start','end','backgroundColor','borderColor','textColor', 'icon', 'group', 'id_user','id_area', 'area', 'id_guardia', 'semana', 'hora_inicio', 'hora_fin')

    if guardias.count()>0:
        df=pd.DataFrame(guardias)
        df['avatar'] = df.apply(lambda row : getAvatar(User.objects.get(id=row['id_user'])), axis = 1)
        df['title'] = df.apply(lambda row : User.objects.get(id=row['id_user']).first_name, axis = 1)
    else:
        df= pd.DataFrame()

    return JsonResponse(df.to_dict('records'), safe=False)


'''DATOS: JSON (Listado con las sustituciones pendientes de ser supervisadas)'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def getSustitucionesPendientes(request):
    
    sustituciones = CalendarioGuardiasGuardias.objects.using('guardias'
    ).filter(tipo_guardia = 2, supervisado=0, valido = 1
    ).order_by('fecha_local_end'
    ).annotate(
        solicitante = F('id_user_modificado'),
        sustituto = F('id_user_analista'),
        fecha_sustitucion = F('fecha_local_start'),
        idArea = F('id_turno__id_area'),
        area = F('id_turno__id_area__nombre'),
        icono = F('id_turno__id_area__icono'),
        turno = Concat(F('id_turno__descripcion'), Value(' (De '), F('id_turno__hora_local_comienzo'), Value(' a '), F('id_turno__hora_local_fin'), Value(')'), output_field=CharField()), 
    ).values('id_guardia', 'solicitante', 'sustituto', 'fecha_sustitucion', 'idArea', 'area', 'icono', 'turno')

    if sustituciones.count()>0:
        df_sustituciones = pd.DataFrame(sustituciones)
        df_sustituciones["avatar_solicitante"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['solicitante'])), axis = 1)
        df_sustituciones["avatar_sustituto"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['sustituto'])), axis = 1)
        df_sustituciones["solicitante"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['solicitante']).first_name, axis = 1)
        df_sustituciones["sustituto"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['sustituto']).first_name, axis = 1)
    else:
        df_sustituciones = pd.DataFrame()

    return JsonResponse(df_sustituciones.to_dict('records'), safe=False)


'''DATOS: JSON (Listado con los cambios de guardia pendientes de ser supervisadas)'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def getCambiosGuardiasPendientes(request):

    user=request.user

    cambios = CalendarioCambiosGuardias.objects.using('guardias'
    ).filter(supervisado = 0
    ).annotate(emisor = F("id_user_emisor"),
              receptor = F("id_user_receptor"),
              idArea=F('id_turno__id_area__id_area'),
              area =  F('id_turno__id_area__nombre'),
              icono = F('id_turno__id_area__icono'),
              turno = F('id_turno__id_turno'),
              semana_emisor = F("sem_guardia_emisor"),
              semana_receptor =F("sem_guardia_receptor"),
              year_emisor = F('year_sem_guardia_emisor'),
              year_receptor = F('year_sem_guardia_receptor'),
    ).values("id_cambio", "emisor", "receptor", "idArea", "area", "icono", "turno", "semana_emisor", "semana_receptor", "year_emisor", "year_receptor")

    if cambios.count()>0:
        df_cambios = pd.DataFrame(cambios)
        df_cambios["avatar_emisor"]=  df_cambios.apply(lambda row : getAvatar(User.objects.get(id=row['emisor'])), axis = 1)
        df_cambios["avatar_receptor"]=  df_cambios.apply(lambda row : getAvatar(User.objects.get(id=row['receptor'])), axis = 1)
        df_cambios["nameEmisor"] = df_cambios.apply(lambda row : User.objects.get(id=row['emisor']).first_name, axis = 1)
        df_cambios["nameReceptor"] = df_cambios.apply(lambda row : User.objects.get(id=row['receptor']).first_name, axis = 1)
        #df_cambios["array_guardias_emisor"] = df_cambios.apply(lambda row : get_array_idGuardias(row['year_emisor'], row["semana_emisor"], row['turno'], row["emisor"]), axis = 1)
        #df_cambios["array_guardias_receptor"] = df_cambios.apply(lambda row : get_array_idGuardias(row['year_receptor'], row["semana_receptor"], row['turno'], row["receptor"]), axis = 1)
        df_cambios["infoEmisor"] = df_cambios.apply(lambda row : get_array_infoGuardias(row['year_emisor'], row['semana_emisor'], row['turno'], row['emisor']), axis = 1)
        df_cambios["infoReceptor"] = df_cambios.apply(lambda row : get_array_infoGuardias(row['year_receptor'], row['semana_receptor'], row['turno'], row['receptor']), axis = 1) 
            
    else:
        df_cambios = pd.DataFrame()

    

    return JsonResponse(df_cambios.to_dict("records"), safe=False)


'''DATOS: JSON (Listado con los cambios de guardia pendientes de ser supervisadas)'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def getHistoricoCambiosGuardias(request):

    user=request.user

    cambios = CalendarioCambiosGuardias.objects.using('guardias'
    #).filter(supervisado = 0
    ).annotate(emisor = F("id_user_emisor"),
              receptor = F("id_user_receptor"),
              idArea=F('id_turno__id_area__id_area'),
              area =  F('id_turno__id_area__nombre'),
              icono = F('id_turno__id_area__icono'),
              turno = F('id_turno__id_turno'),
              permanencia = Concat(F('id_turno__descripcion'), Value(' (De '), F('id_turno__hora_local_comienzo'), Value(' a '), F('id_turno__hora_local_fin'), Value(')'), output_field=CharField()), 
              semana_emisor = F("sem_guardia_emisor"),
              semana_receptor =F("sem_guardia_receptor"),
              year_emisor = F('year_sem_guardia_emisor'),
              year_receptor = F('year_sem_guardia_receptor'),
              estado = Case( When(supervisado=0, then=Value('Pendiente')),
                        When(supervisado=1, then=Value('Aceptada')),
                        When(supervisado=2, then=Value('Rechazada')),
                        output_field=CharField(),
                        default=Value('Indefinido'),
                    ),
              color = Case(When(supervisado=0, then=Value('#A9A9A9')),
                        When(supervisado=1, then=Value('#3CB371')),
                        When(supervisado=2, then=Value('#8B0000')),
                        output_field=CharField(),
                        default=Value('#000000')
                    )              
    ).values("id_cambio", "emisor", "receptor", "idArea", "area", "icono", "turno", "permanencia", "semana_emisor", "semana_receptor", "year_emisor", "year_receptor", "estado", "color")

    if cambios.count()>0:
        df_cambios = pd.DataFrame(cambios)
        df_cambios["avatar_emisor"]=  df_cambios.apply(lambda row : getAvatar(User.objects.get(id=row['emisor'])), axis = 1)
        df_cambios["avatar_receptor"]=  df_cambios.apply(lambda row : getAvatar(User.objects.get(id=row['receptor'])), axis = 1)
        df_cambios["nameEmisor"] = df_cambios.apply(lambda row : User.objects.get(id=row['emisor']).first_name, axis = 1)
        df_cambios["nameReceptor"] = df_cambios.apply(lambda row : User.objects.get(id=row['receptor']).first_name, axis = 1)
        #df_cambios["array_guardias_emisor"] = df_cambios.apply(lambda row : get_array_idGuardias(row['year_emisor'], row["semana_emisor"], row['turno'], row["emisor"]), axis = 1)
        #df_cambios["array_guardias_receptor"] = df_cambios.apply(lambda row : get_array_idGuardias(row['year_receptor'], row["semana_receptor"], row['turno'], row["receptor"]), axis = 1)
        df_cambios["infoEmisor"] = df_cambios.apply(lambda row : get_array_infoGuardias(row['year_emisor'], row['semana_emisor'], row['turno'], row['emisor']), axis = 1)
        df_cambios["infoReceptor"] = df_cambios.apply(lambda row : get_array_infoGuardias(row['year_receptor'], row['semana_receptor'], row['turno'], row['receptor']), axis = 1) 
        df_cambios["tipo"] = "Completo"
        df_cambios = df_cambios.filter(['nameEmisor', 'nameReceptor', 'avatar_emisor', 'avatar_receptor', 'infoEmisor', 'infoReceptor', 'permanencia', 'area', 'icono', 'tipo', 'estado', 'color'])
    else:
        df_cambios = pd.DataFrame(columns=['nameEmisor', 'nameReceptor', 'avatar_emisor', 'avatar_receptor', 'infoEmisor', 'infoReceptor', 'permanencia', 'area', 'icono', 'tipo', 'estado', 'color'])

    
    sustituciones = CalendarioGuardiasGuardias.objects.using('guardias'
    ).filter(tipo_guardia=2
    #).filter(Q(id_user_modificado = request.user.id) | Q(id_user_analista = request.user.id)
    ).order_by('supervisado', 'fecha_local_start', 
    ).annotate(
        emisor = F('id_user_modificado'),
        receptor = F('id_user_analista'),
        fecha_sustitucion = Func(F('fecha_local_start'), Value('%d-%b-%Y'), function='DATE_FORMAT'),
        area = F('id_turno__id_area__nombre'),
        icono = F('id_turno__id_area__icono'),
        permanencia = Concat(F('id_turno__descripcion'), Value(' (De '), F('id_turno__hora_local_comienzo'), Value(' a '), F('id_turno__hora_local_fin'), Value(')'), output_field=CharField()), 
        estado = Case( When(supervisado=0, then=Value('Pendiente')),
                        When(supervisado=1, then=Value('Aceptada')),
                        When(supervisado=2, then=Value('Rechazada')),
                        output_field=CharField(),
                        default=Value('Indefinido'),
                    ),
        color = Case(When(supervisado=0, then=Value('#A9A9A9')),
                        When(supervisado=1, then=Value('#3CB371')),
                        When(supervisado=2, then=Value('#8B0000')),
                        output_field=CharField(),
                        default=Value('#000000')
                    )
    ).order_by('supervisado'
    ).values('emisor', 'receptor', 'fecha_sustitucion', 'area', 'icono', 'permanencia', 'estado', 'color')

    if sustituciones.count()>0:
        df_sustituciones = pd.DataFrame(sustituciones)
        df_sustituciones["avatar_emisor"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['emisor'])), axis = 1)
        df_sustituciones["avatar_receptor"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['receptor'])), axis = 1)
        df_sustituciones["nameEmisor"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['emisor']).first_name, axis = 1)
        df_sustituciones["nameReceptor"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['receptor']).first_name, axis = 1)
        df_sustituciones["infoEmisor"] = df_sustituciones.apply(lambda row : [row['fecha_sustitucion']], axis = 1)
        df_sustituciones["infoReceptor"] = df_sustituciones.apply(lambda row : [], axis = 1)
        df_sustituciones["tipo"] = "Puntual"
        df_sustituciones = df_sustituciones.filter(['nameEmisor', 'nameReceptor', 'avatar_emisor', 'avatar_receptor', 'infoEmisor', 'infoReceptor', 'permanencia', 'area', 'icono', 'tipo', 'estado', 'color'])
    else:
        df_sustituciones = pd.DataFrame(columns=['nameEmisor', 'nameReceptor', 'avatar_emisor', 'avatar_receptor', 'infoEmisor', 'infoReceptor', 'permanencia', 'area', 'icono', 'tipo', 'estado', 'color'])

    sustituciones_voluntarias = CalendarioGuardiasGuardias.objects.using('guardias'
    ).filter(tipo_guardia=4
    #).filter(Q(id_user_modificado = request.user.id) | Q(id_user_analista = request.user.id)
    ).order_by('supervisado', 'fecha_local_start', 
    ).annotate(
        emisor = F('id_user_modificado'),
        fecha_sustitucion = Func(F('fecha_local_start'), Value('%d-%b-%Y'), function='DATE_FORMAT'),
        area = F('id_turno__id_area__nombre'),
        icono = F('id_turno__id_area__icono'),
        permanencia = Concat(F('id_turno__descripcion'), Value(' (De '), F('id_turno__hora_local_comienzo'), Value(' a '), F('id_turno__hora_local_fin'), Value(')'), output_field=CharField()), 
        estado = Case( When(supervisado=0, then=Value('Pendiente')),
                        When(supervisado=1, then=Value('Aceptada')),
                        When(supervisado=2, then=Value('Rechazada')),
                        output_field=CharField(),
                        default=Value('Indefinido'),
                    ),
        color = Case(When(supervisado=0, then=Value('#A9A9A9')),
                        When(supervisado=1, then=Value('#3CB371')),
                        When(supervisado=2, then=Value('#8B0000')),
                        output_field=CharField(),
                        default=Value('#000000')
                    )
    ).order_by('supervisado'
    ).values('emisor', 'fecha_sustitucion', 'area', 'icono', 'permanencia', 'estado', 'color')

    if sustituciones_voluntarias.count()>0:
        df_sustituciones_voluntarias = pd.DataFrame(sustituciones_voluntarias)
        df_sustituciones_voluntarias["avatar_emisor"]=  df_sustituciones_voluntarias.apply(lambda row : getAvatar(User.objects.get(id=row['emisor'])), axis = 1)
        df_sustituciones_voluntarias["nameEmisor"] = df_sustituciones_voluntarias.apply(lambda row : User.objects.get(id=row['emisor']).first_name, axis = 1)
        df_sustituciones_voluntarias["infoEmisor"] = df_sustituciones_voluntarias.apply(lambda row : [row['fecha_sustitucion']], axis = 1)
        df_sustituciones_voluntarias["infoReceptor"] = df_sustituciones_voluntarias.apply(lambda row : [], axis = 1)
        df_sustituciones_voluntarias["tipo"] = "Voluntario"
        df_sustituciones_voluntarias = df_sustituciones_voluntarias.filter(['nameEmisor', 'nameReceptor', 'avatar_emisor', 'avatar_receptor', 'infoEmisor', 'infoReceptor', 'permanencia', 'area', 'icono', 'tipo', 'estado', 'color'])
        print(df_sustituciones_voluntarias)
    else:
        df_sustituciones_voluntarias = pd.DataFrame(columns=['nameEmisor', 'nameReceptor', 'avatar_emisor', 'avatar_receptor', 'infoEmisor', 'infoReceptor', 'permanencia', 'area', 'icono', 'tipo', 'estado', 'color'])
    
    frames = [df_cambios, df_sustituciones, df_sustituciones_voluntarias]
    df_cambios_calendario = pd.concat(frames).sort_values(by=["estado"])
    df_cambios_calendario.reset_index(drop=True, inplace=True)


    return JsonResponse(df_cambios_calendario.to_dict("records"), safe=False)



'''DATOS: SET - MENSAJE (Inserta una nueva peticion de sustitucion)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def setSustitucion(request):

    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 
        
    idGuardia = request.GET.get('g','') #Obtengo el id de la guardia titular en la que deseo realizar la petición de una sustitución
    fechaSustitucion = request.GET.get('f','') #Obtengo el día en el que deseo que me sustituyan
    idSustituto = request.GET.get('u', '')#Obtengo el usuario/analista que quiero que me sustituya
    newTurno = request.GET.get('t','') #Obtengo el turno en el que quiero que me sustituya

    if idGuardia!="" and fechaSustitucion!="" and idSustituto!="" and newTurno!="":
        try:
            #Información de la guardia titular en la que quiero que me sustituyan
            guardiaTitular = CalendarioGuardiasGuardias.objects.using("guardias").values().filter(id_guardia = int(idGuardia))
            df_guardiaTitular = pd.DataFrame(guardiaTitular)
            df_guardiaTitular = df_guardiaTitular.iloc[0]

            #Obtengo el turno de trabajo en el que deseo establecer una sustitucion
            turno = CalendarioTurnos.objects.using("guardias").filter(id_turno = int(newTurno)).first()

            #Compruebo si ya hay una sustitucion registrada para este dia en el mismo turno
            print("PRUEBA", df_guardiaTitular.get('year'), df_guardiaTitular.get('semana'), datetime.strptime(fechaSustitucion, '%Y-%m-%d'), datetime.strptime(fechaSustitucion, '%Y-%m-%d').date())
            if CalendarioGuardiasGuardias.objects.using("guardias"
                ).filter(year= df_guardiaTitular.get('year'), 
                        semana = df_guardiaTitular.get('semana'),
                        tipo_semana = df_guardiaTitular.get('tipo_semana'),
                        tipo_guardia = 2,
                        id_turno = turno,
                        fecha_local_start = datetime.strptime(fechaSustitucion, '%Y-%m-%d').date(),  
                        supervisado__lt=2,
                        valido = 1
                        ).exists():
                mensaje["title"]="Sustitución ya solicitada!"
                mensaje["text"]="No puede realizar la misma petición de sustitución por duplicado."
                mensaje["icon"]="warning" 
                return JsonResponse(mensaje, safe=False)
            else:
                #Añado la nueva petición de sustitución a la base de datos
                CalendarioGuardiasGuardias.objects.using("guardias"
                ).create(year = df_guardiaTitular.get('year'), 
                        semana = df_guardiaTitular.get('semana'),
                        id_user_analista = int(idSustituto),
                        id_turno_id = int(newTurno),
                        fecha_local_start = datetime.strptime(fechaSustitucion, '%Y-%m-%d'),
                        fecha_local_end = datetime.strptime(fechaSustitucion, '%Y-%m-%d'),
                        id_user_modificado = df_guardiaTitular.get('id_user_analista'),
                        tipo_semana = df_guardiaTitular.get('tipo_semana'),
                        tipo_guardia = 2,
                        supervisado = 0,
                        valido = 1) # Creo la query para almacenarlo en la base de datos
            
                mensaje["title"]="Petición de sustitución aceptada"
                mensaje["text"]="La solicitud será notificada al director del centro, responsable de aceptar o no la propuesta realizada. Hasta que no sea verificada dicha sustitución, no podrá visualizar los cambios en el calendario. Para conocer su estado dirijase al apartado Mi Tablón."
                mensaje["icon"]="success" 

        except Exception as e:
            print("ERROR en setSustitucion", e)
            mensaje["title"]="Opps! ..."
            mensaje["text"]="No ha sido posible registrar la sustitución requerida en la base de datos. Vuelve a intentarlo en unos minutos."
            mensaje["icon"]="error" 

    return JsonResponse(mensaje, safe=False)

'''DATOS: SET - MENSAJE (Inserta una nueva peticion de sustitucion)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def setSustitucionSupervisor(request):

    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 
        
    idGuardia = request.GET.get('g','') #Obtengo el id de la guardia titular en la que deseo realizar la petición de una sustitución
    fechaSustitucion = request.GET.get('f','') #Obtengo el día en el que deseo que me sustituyan
    print("DATOS", idGuardia, fechaSustitucion)

    if idGuardia!="" and fechaSustitucion!="":
        try:
            #Información de la guardia titular en la que quiero sustituir un dia
            print("Guardia")
            guardiaTitular = CalendarioGuardiasGuardias.objects.using("guardias").filter(id_guardia = int(idGuardia)).values()
            print(guardiaTitular)
            df_guardiaTitular = pd.DataFrame(guardiaTitular)
            print("DATAFRAME")
            print(df_guardiaTitular)
            df_guardiaTitular = df_guardiaTitular.iloc[0]
            print("FIN DATAFRAME")
            
            print("ID TURNO", int(df_guardiaTitular.get('id_turno_id')))
            #Obtengo el turno de trabajo en el que deseo establecer una sustitucion
            turno = CalendarioTurnos.objects.using("guardias").filter(id_turno = int(df_guardiaTitular.get('id_turno_id'))).first()

            #Compruebo si ya hay una sustitucion registrada para este dia en el mismo turno
            if CalendarioGuardiasGuardias.objects.using("guardias"
                ).filter(year= df_guardiaTitular.get('year'), 
                        semana = df_guardiaTitular.get('semana'),
                        tipo_semana = df_guardiaTitular.get('tipo_semana'),
                        tipo_guardia = 2,
                        id_turno = turno,
                        fecha_local_start = datetime.strptime(fechaSustitucion, '%Y-%m-%d').date(), 
                        supervisado__lt=2,
                        valido = 1
                        ).exists():
                mensaje["title"]="Sustitución ya solicitada!"
                mensaje["text"]="No puede realizar la misma petición de sustitución por duplicado."
                mensaje["icon"]="warning" 
                return JsonResponse(mensaje, safe=False)
            else:
                #Añado la nueva petición de sustitución a la base de datos
                CalendarioGuardiasGuardias.objects.using("guardias"
                ).create(year = df_guardiaTitular.get('year'), 
                        semana = df_guardiaTitular.get('semana'),
                        id_user_analista = request.user.id,
                        id_turno = turno,
                        fecha_local_start = datetime.strptime(fechaSustitucion, '%Y-%m-%d'),
                        fecha_local_end = datetime.strptime(fechaSustitucion, '%Y-%m-%d'),
                        id_user_modificado = request.user.id,
                        tipo_semana = df_guardiaTitular.get('tipo_semana'),
                        tipo_guardia = 4,
                        supervisado = 1,
                        valido = 1) # Creo la query para almacenarlo en la base de datos
            
                mensaje["title"]="Petición de sustitución aceptada"
                mensaje["text"]="Ya puede visualizar los cambios en el calendario."
                mensaje["icon"]="success" 

        except Exception as e:
            print("ERROR en setSustitucionSupervisor", e)
            mensaje["title"]="Opps! ..."
            mensaje["text"]="No ha sido posible registrar la sustitución requerida por el supervisor en la base de datos. Vuelve a intentarlo en unos minutos."
            mensaje["icon"]="error" 

    return JsonResponse(mensaje, safe=False)


'''DATOS: SET - MENSAJE (El analista elimina directamente de la base de datos
una peticion de sustitucion si aun esta se encuentra pendiente de chequear por 
el supervisor)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def setEliminarSustitucion(request):
    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error"

    idGuardia= request.GET.get('g', '')

    if idGuardia!="":
        try:
            CalendarioGuardiasGuardias.objects.using('guardias').filter(id_guardia = int(idGuardia)).delete()
            mensaje["title"]="Correcto!"
            mensaje["text"]="La petición de sustitución ha sido eliminada"
            mensaje["icon"]="success" 
        except Exception as e:
            print("ERROR setDeleteGuardia: ", e)
            mensaje["title"]="Se ha producido un error"
            mensaje["text"]="La petición de sustitucion no ha podido ser eliminada. Vuelva a intentarlo en unos minutos."
            mensaje["icon"]="error" 
    
    return JsonResponse(mensaje, safe=False)


'''DATOS: SET - MENSAJE (El supervisor acepta una peticion de sustitucion)'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def setAceptarSustitucion(request):

    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    idGuardia = request.GET.get('g','') #Obtengo el id de la guardia que deseo aceptar/validar

    if idGuardia!="":
        infoGuardia = CalendarioGuardiasGuardias.objects.using('guardias').filter(id_guardia = int(idGuardia)).first()

        try:
            CalendarioGuardiasGuardias.objects.using('guardias').filter(id_guardia = int(idGuardia)).update(supervisado = 1)
            mensaje["title"]="Sustitución aceptada!"
            mensaje["text"]="A continuación dicho cambio se hará visible en el calendario y será notificado a los respectivos analistas." #+ User.objects.get(id=infoGuardia.creador).first_name + ' y a '+User.objects.get(id=infoGuardia.id_usuario.id_usuario).first_name +' respectivamente.'
            mensaje["icon"]="success" 
        except Exception as e:
            print("ERROR setAceptarSustitucion: ", e)
            mensaje["title"]="Se ha producido un error"
            mensaje["text"]="No ha sido posible registrar en la base de datos la aceptación de dicha sustitución."
            mensaje["icon"]="error"

    return JsonResponse(mensaje, safe=False)

'''DATOS: SET - MENSAJE (El supervisor rechaza una peticion de sustitucion)'''
@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def setRechazarSustitucion(request):

    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    idGuardia = request.GET.get('g','') #Obtengo el id de la guardia que deseo aceptar/validar

    if idGuardia!="":
        infoGuardia = CalendarioGuardiasGuardias.objects.using('guardias').filter(id_guardia = int(idGuardia)).first()

        try:
            CalendarioGuardiasGuardias.objects.using('guardias').filter(id_guardia = int(idGuardia)).update(supervisado = 2, valido = 0)
            mensaje["title"]="Sustitución rechazada!"
            #mensaje["text"]="A continuación dicho cambio será notificado a los respectivos analistas."#+ User.objects.get(id=infoGuardia.creador).first_name + ' y a '+User.objects.get(id=infoGuardia.id_usuario.id_usuario).first_name +' respectivamente.'
            mensaje["icon"]="success" 
        except Exception as e:
            print("ERROR setRechazarSustitucion: ", e)
            mensaje["title"]="Se ha producido un error"
            mensaje["text"]="No ha sido posible registrar en la base de datos el rechazo de dicha sustitución."
            mensaje["icon"]="error"

    return JsonResponse(mensaje, safe=False)


'''DATOS: SET - MENSAJE (Inserta una nueva peticion de cambio de guardia)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def setCambioGuardia(request):

    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    idGuardia_emisor= request.GET.get('e', '') #Obtengo el id de la guardia que quiero cambiar
    idGuardia_receptor= request.GET.get('r', '') #Obtengo el id de la guardia por la que la quiero guardar

    try:
        if idGuardia_emisor!="" and idGuardia_emisor!="":
            guardia_emisor = CalendarioGuardiasGuardias.objects.using("guardias").filter(id_guardia=int(idGuardia_emisor)).first()
            guardia_receptor = CalendarioGuardiasGuardias.objects.using("guardias").filter(id_guardia = int(idGuardia_receptor)).first()

            if CalendarioCambiosGuardias.objects.using("guardias"
                ).filter(supervisado = 0
                ).filter( (Q(year_sem_guardia_emisor = guardia_emisor.year) & Q(sem_guardia_emisor = guardia_emisor.semana)) |
                        (Q(year_sem_guardia_receptor = guardia_receptor.year) & Q(sem_guardia_receptor = guardia_receptor.semana)) |
                        (Q(year_sem_guardia_emisor = guardia_receptor.year) & Q(sem_guardia_emisor = guardia_receptor.semana)) |
                        (Q(year_sem_guardia_receptor = guardia_emisor.year) & Q(sem_guardia_receptor = guardia_emisor.semana))  
                ).exists():

                mensaje["title"]="Cambio de guardia ya solicitado!"
                mensaje["text"]="Para una de las guardias ya se ha solicitado un cambio que aún se encuentra pendiente de aceptar o no por el director del centro, por lo que no es posible solicitar dicho cambio en estos momentos."
                mensaje["icon"]="warning" 
                return JsonResponse(mensaje, safe=False)

            else:
                CalendarioCambiosGuardias.objects.using("guardias"
                    ).create( year_sem_guardia_emisor =  guardia_emisor.year,
                            sem_guardia_emisor = guardia_emisor.semana,
                            id_user_emisor = guardia_emisor.id_user_analista,
                            year_sem_guardia_receptor = guardia_receptor.year,
                            sem_guardia_receptor = guardia_receptor.semana,
                            id_user_receptor = guardia_receptor.id_user_analista,
                            id_turno = guardia_emisor.id_turno, 
                            supervisado = 0
                    )
                                    
                mensaje["title"]="Petición de cambio de guardia aceptado"
                mensaje["text"]="La solicitud será notificada al director del centro, responsable de aceptar o no la propuesta realizada. Hasta que no sea verificado dicho cambio de guardia, no podrá ser visualizado en el calendario. Para conocer su estado dirijase al apartado Mi Tablón."
                mensaje["icon"]="success" 
         
    except Exception as e:
        print("ERROR en setCambioGuardias", e)
        mensaje["title"]="Opps! ..."
        mensaje["text"]="No ha sido posible registrar el cambio de guardia requerido en la base de datos. Vuelve a intentarlo en unos minutos."
        mensaje["icon"]="error" 


    return JsonResponse(mensaje, safe=False)


@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def setCambioGuardiaDirecto(request):
    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    idGuardia_emisor= request.GET.get('e', '') #Obtengo el id de la guardia que quiero cambiar
    idGuardia_receptor= request.GET.get('r', '') #Obtengo el id de la guardia por la que la quiero guardar

    try:
        if idGuardia_emisor!="" and idGuardia_emisor!="":
            guardia_emisor = CalendarioGuardiasGuardias.objects.using("guardias").filter(id_guardia=int(idGuardia_emisor)).first()
            guardia_receptor = CalendarioGuardiasGuardias.objects.using("guardias").filter(id_guardia = int(idGuardia_receptor)).first()

            if CalendarioCambiosGuardias.objects.using("guardias"
                ).filter(supervisado = 0
                ).filter( (Q(year_sem_guardia_emisor = guardia_emisor.year) & Q(sem_guardia_emisor = guardia_emisor.semana) & Q(id_user_emisor = guardia_emisor.id_user_analista)) |
                        (Q(year_sem_guardia_receptor = guardia_receptor.year) & Q(sem_guardia_receptor = guardia_receptor.semana) & Q(id_user_receptor = guardia_receptor.id_user_analista)) |
                        (Q(year_sem_guardia_emisor = guardia_receptor.year) & Q(sem_guardia_emisor = guardia_receptor.semana) & Q(id_user_emisor = guardia_receptor.id_user_analista)) |
                        (Q(year_sem_guardia_receptor = guardia_emisor.year) & Q(sem_guardia_receptor = guardia_emisor.semana) & Q(id_user_receptor = guardia_emisor.id_user_analista))  
                ).exists():

                mensaje["title"]="Cambio de guardia ya solicitado!"
                mensaje["text"]="Para una de las guardias ya se ha solicitado un cambio que aún se encuentra pendiente de aceptar o no por el director del centro, por lo que no es posible tramitar este cambio hasta que no revise anteriormente las perticiones realizadas por los analistas en el tablón de notificaciones."
                mensaje["icon"]="warning" 
                return JsonResponse(mensaje, safe=False)

            else:

                guardias_emisor = CalendarioGuardiasGuardias.objects.using("guardias"
                ).filter(year = guardia_emisor.year,
                    semana = guardia_emisor.semana,
                    id_user_analista = guardia_emisor.id_user_analista,
                    tipo_guardia__in = [1,3],
                    supervisado = 1,
                    valido = 1
                )

                guardias_receptor = CalendarioGuardiasGuardias.objects.using("guardias"
                ).filter(year = guardia_receptor.year,
                    semana = guardia_receptor.semana,
                    id_user_analista = guardia_receptor.id_user_analista,
                    tipo_guardia__in = [1,3],
                    supervisado = 1,
                    valido = 1
                )

                guardias_emisor_historico = guardias_emisor.values_list('id_guardia', flat=True)
                guardias_receptor_historico = guardias_receptor.values_list('id_guardia', flat=True)  

                df_guardias_emisor = pd.DataFrame(guardias_emisor.values())
                df_guardias_receptor = pd.DataFrame(guardias_receptor.values())

                id_user_emisor = guardias_emisor.first().id_user_analista
                id_user_receptor = guardias_receptor.first().id_user_analista

                df_guardias_emisor['id_user_analista']=id_user_receptor
                df_guardias_receptor["id_user_analista"]= id_user_emisor

                #Obtengo el listado completo de nuevas guardias
                frames = [df_guardias_emisor, df_guardias_receptor]
                df_new_guardias = pd.concat(frames).sort_values(by=["semana"])
                df_new_guardias.reset_index(drop=True, inplace=True)
                df_new_guardias = df_new_guardias.drop(columns=['id_guardia'])

                df_new_guardias["id_user_modificado"] = request.user.id
                df_new_guardias["tipo_guardia"] = 3 #indico que es un cambio de guardia

                #Actualizo las guardias historicas
                guardias_emisor.update(valido = 0)
                guardias_receptor.update(valido = 0)

                try:
                    #Cargo de forma masiva a través de un json las nuevas guardias
                    CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                        CalendarioGuardiasGuardias(**vals) for vals in df_new_guardias.to_dict('records')
                    )
                    mensaje["title"]="Cambio de guardia aceptado!"
                    mensaje["text"]="A continuación dicho cambio se hará visible en el calendario!"# y será notificado a "+ User.objects.get(id = int(id_user_emisor)).first_name + " y a " +  User.objects.get(id=int(id_user_receptor)).first_name +" respectivamente."
                    mensaje["icon"]="success"
                except Exception as e :
                    print("Error ", e)
                    #Actualizo las guardias historicas si se ha producido un error
                    guardias_emisor = CalendarioGuardiasGuardias.objects.using("guardias"
                        ).filter(id_guardia__in = guardias_emisor_historico).update(valido = 1)
                
                    guardias_receptor = CalendarioGuardiasGuardias.objects.using("guardias"
                        ).filter(id_guardia__in = guardias_receptor_historico).update(valido = 1)
                    
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="No ha sido posible registrar en la base de datos dicho cambio de guardia."
                    mensaje["icon"]="error"
         
    except Exception as e:
        print("ERROR en setCambioGuardias", e)
        mensaje["title"]="Opps! ..."
        mensaje["text"]="No ha sido posible registrar el cambio de guardia requerido en la base de datos. Vuelve a intentarlo en unos minutos."
        mensaje["icon"]="error" 


    return JsonResponse(mensaje, safe=False)


@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def setEliminarCambioGuardia(request):
    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error"

    idCambio= request.GET.get('c', '')

    if idCambio!="":
        try:
            print("ELIMINAR CAMBIO", idCambio)
            CalendarioCambiosGuardias.objects.using('guardias').filter(id_cambio = int(idCambio)).delete()
            mensaje["title"]="Correcto!"
            mensaje["text"]="La petición de cambio de guardia ha sido eliminada"
            mensaje["icon"]="success" 
        except Exception as e:
            print("ERROR setDeleteGuardia: ", e)
            mensaje["title"]="Se ha producido un error"
            mensaje["text"]="La petición de cambio de guardia no ha podido ser eliminada. Vuelva a intentarlo en unos minutos."
            mensaje["icon"]="error" 
    
    return JsonResponse(mensaje, safe=False)

@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def setAceptarCambioGuardia(request):
    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    idCambio = request.GET.get('c','')

    if idCambio!="":
        try:
            infoCambio = CalendarioCambiosGuardias.objects.using("guardias").filter(id_cambio = int(idCambio)).first()

            guardias_emisor = CalendarioGuardiasGuardias.objects.using("guardias"
                ).filter(year = infoCambio.year_sem_guardia_emisor,
                    semana = infoCambio.sem_guardia_emisor,
                    id_user_analista = infoCambio.id_user_emisor,
                    tipo_guardia__in = [1,3],
                    supervisado = 1,
                    valido = 1
                )
            guardias_receptor = CalendarioGuardiasGuardias.objects.using("guardias"
                ).filter(year = infoCambio.year_sem_guardia_receptor,
                    semana = infoCambio.sem_guardia_receptor,
                    id_user_analista = infoCambio.id_user_receptor,
                    tipo_guardia__in = [1,3],
                    supervisado = 1,
                    valido = 1
                )

            guardias_emisor_historico = guardias_emisor.values_list('id_guardia', flat=True)
            guardias_receptor_historico = guardias_receptor.values_list('id_guardia', flat=True)            

            df_guardias_emisor = pd.DataFrame(guardias_emisor.values())
            df_guardias_receptor = pd.DataFrame(guardias_receptor.values())

            id_user_emisor = guardias_emisor.first().id_user_analista
            id_user_receptor = guardias_receptor.first().id_user_analista

            df_guardias_emisor['id_user_analista']=id_user_receptor
            df_guardias_receptor["id_user_analista"]= id_user_emisor

            #Obtengo el listado completo de nuevas guardias
            frames = [df_guardias_emisor, df_guardias_receptor]
            df_new_guardias = pd.concat(frames).sort_values(by=["semana"])
            df_new_guardias.reset_index(drop=True, inplace=True)
            df_new_guardias = df_new_guardias.drop(columns=['id_guardia'])

            df_new_guardias["id_user_modificado"] = request.user.id
            df_new_guardias["tipo_guardia"] = 3 #indico que es un cambio de guardia

            #Actualizo las guardias historicas
            guardias_emisor.update(valido = 0)
            guardias_receptor.update(valido = 0)

            try:
                #Cargo de forma masiva a través de un json las nuevas guardias
                CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                    CalendarioGuardiasGuardias(**vals) for vals in df_new_guardias.to_dict('records')
                )

                CalendarioCambiosGuardias.objects.using("guardias").filter(id_cambio = int(idCambio)).update(supervisado = 1)

                mensaje["title"]="Cambio de guardia aceptado!"
                mensaje["text"]="A continuación dicho cambio se hará visible en el calendario y será notificado a "+ User.objects.get(id = int(id_user_emisor)).first_name + " y a " +  User.objects.get(id=int(id_user_receptor)).first_name +" respectivamente."
                mensaje["icon"]="success"
            except Exception as e :
                print("Error ", e)
                #Actualizo las guardias historicas si se ha producido un error
                guardias_emisor = CalendarioGuardiasGuardias.objects.using("guardias"
                    ).filter(id_guardia__in = guardias_emisor_historico).update(valido = 1)
            
                guardias_receptor = CalendarioGuardiasGuardias.objects.using("guardias"
                    ).filter(id_guardia__in = guardias_receptor_historico).update(valido = 1)
                
                CalendarioCambiosGuardias.objects.using("guardias").filter(id_cambio = int(idCambio)).update(supervisado = 0)
                mensaje["title"]="Se ha producido un error"
                mensaje["text"]="No ha sido posible registrar en la base de datos dicho cambio de guardia."
                mensaje["icon"]="error"
    
        except Exception as e:
            print("ERROR setAceptarCambioGuardia: ", e)
            mensaje["title"]="Se ha producido un error"
            mensaje["text"]="No ha sido posible registrar en la base de datos la aceptación de dicho cambio de guardia."
            mensaje["icon"]="error"

    return JsonResponse(mensaje, safe=False)

@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def setRechazarCambioGuardia(request):
    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    idCambio = request.GET.get('c','') #Obtengo el id de la guardia que deseo aceptar/validar

    if idCambio!="":
        try:
            CalendarioCambiosGuardias.objects.using('guardias').filter(id_cambio = int(idCambio)).update(supervisado = 2)
            mensaje["title"]="Sustitución rechazada!"
            mensaje["text"]="A continuación dicho cambio será notificado a los respectivos analistas."#+ User.objects.get(id=infoGuardia.creador).first_name + ' y a '+User.objects.get(id=infoGuardia.id_usuario.id_usuario).first_name +' respectivamente.'
            mensaje["icon"]="success" 
        except Exception as e:
            print("ERROR setRechazarSustitucion: ", e)
            mensaje["title"]="Se ha producido un error"
            mensaje["text"]="No ha sido posible registrar en la base de datos el rechazo de dicha sustitución."
            mensaje["icon"]="error"

    return JsonResponse(mensaje, safe=False)


def setNuevoMensaje(request):

    result = False

    mensaje = request.GET.get('m', None)
    icono = request.GET.get('i',None)
    descripcion = request.GET.get('d',None)
    area = request.GET.get('a', None)

    #tzInfo = pytz.timezone('Europe/Madrid')
    tzInfo = pytz.utc
    
    try:
        if mensaje!=None:
            #\\U0001F539
   
            MensajesTelegram.objects.using("guardias").create(  id_area = area,
                                                                fecha_hora_utc = datetime.now().astimezone(tzInfo).strftime("%Y-%m-%d %H:%M:%S"), 
                                                                mensaje = mensaje, 
                                                                descripcion = descripcion,
                                                                icono = icono, 
                                                                estado = 0,
                                                                id_telegram = settings.ID_CHAT_GUARDIAS,
                                                                silenciar = 1,
                                                                confirmar = 0,
                                                                enviado = 0)#-1001729943644)#-674425144)
            result = True

    except Exception as e:
        print("ERROR enviar mensaje telegram", e)
        result = False
    return JsonResponse(result, safe=False)




'''DATOS: MENSAJE (Inserta los dias festivos señalados en la base de datos)'''
@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def updateFestivos(request):
    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    year = request.GET.get('y','') #obtengo el año en el que quiero actualizar los festivos
    jsonFestivos = request.GET.get('f', '') #objengo el json con los festivos

    if year!="" and jsonFestivos!="":
        df_festivos = pd.read_json(jsonFestivos)
        if len(df_festivos.index) > 0:
            try:
                #Obtengo los festivos que ya hay registrados en la base de datos para el año en cuestión y los elimino
                festivos_historicos= CalendarioFestivos.objects.using('guardias').filter(fecha_local__year=int(year))
                df_festivos_historicos = pd.DataFrame(festivos_historicos.values())
                festivos_historicos.delete()
                try:
                    #Cargo de forma masiva a través de un json los nuevos festivos en la base de datos  
                    CalendarioFestivos.objects.using('guardias').bulk_create(
                        CalendarioFestivos(**vals) for vals in df_festivos.to_dict('records')
                    )                
                    mensaje["title"]=""
                    mensaje["text"]="Se han añadido a la base de datos todos los días festivos pertenecientes al calendario de guardias "+year+'.'
                    mensaje["icon"]="success" 
                except:
                    #Cargo de forma masiva a través de un json los festivos historicos si se ha producido un problema
                    CalendarioFestivos.objects.using('guardias').bulk_create(
                        CalendarioFestivos(**vals) for vals in df_festivos_historicos.to_dict('records')
                    ) 
            
            except Exception as e:
                print("ERROR updateFestivos", e)
                mensaje["title"]="Opps! ..."
                mensaje["text"]="Se ha producido un error al insertar los días festivos para el año "+year+" en la base de datos."
                mensaje["icon"]="error"
        
        else:
            mensaje["title"]="Opps! ..."
            mensaje["text"]="No se ha recibido ningún día festivo para proceder a generar el nuevo calendario de guardias."
            mensaje["icon"]="error"

    return JsonResponse(mensaje, safe=False)


'''DATOS: JSON (Listado de las áreas de trabajo)
    Formato especifico para insertarlo en un input select de sweetalert'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getAreas(request):
    areas = CalendarioAreas.objects.using("guardias").annotate(value=F('id_area'), text=F('nombre')).values('value', 'text')
    dictAreas={}
    for area in areas:
        dictAreas[area['value']]=area['text']

    resultjson = json.dumps(dictAreas)
    return JsonResponse(resultjson, safe=False)

'''DATOS: JSON (Listado con los turnos de trabajo pertenecientes a un área de trabajo)
    Formato especifico para insertarlo en un input select de sweetalert'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getTurnosArea(request):
    area = request.GET.get('a','') #obtengo el id del area de trabajo
    dictTurnos={}
    if area!='':
        turnos = CalendarioTurnos.objects.using("guardias").filter(id_area=int(area)).values('id_turno', 'descripcion', 'hora_local_comienzo', 'hora_local_fin')
        for turno in turnos:
            dictTurnos[turno['id_turno']]=turno['descripcion']+' (Permanencia de '+ turno['hora_local_comienzo'].strftime("%H:%M") +' a '+ turno['hora_local_fin'].strftime("%H:%M")+')'

    resultjson = json.dumps(dictTurnos)
    return JsonResponse(resultjson, safe=False)

'''DATOS: JSON (1. Información de un area de trabajo, 2. Personal vigente en ese area de trabajo)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getPersonalArea(request):
    area = request.GET.get('a','') #obtengo el id del area de trabajo
    
    result={}
    result['area']=[]
    result['personal']=[]

    if area!="":
        infoArea = CalendarioAreas.objects.using("guardias").filter(id_area= int(area)).values()
        #Obtengo la información del area de trabajo seleccionada
        result['area']=list(infoArea)

        #Obtengo el personal dado de alta en el calendario de guardias para el area especificada
        personal = CalendarioPersonal.objects.using("guardias").filter(id_area=int(area), operativo=1)
        
        usuarios=[]
        for analista in personal:
            user = User.objects.get(id=analista.id_usuario) #Obtengo la informacion del usuario
            usuario={}
            usuario["id"]=user.id
            usuario["nombre"]=user.first_name
            usuario["apellidos"]=user.last_name
            usuario["avatar"]= getAvatar(user)
            usuarios.append(usuario)

        #Obtengo el listado con la informacion basica del personal dado de alta en el calendario de guardias para el area especificada
        result['personal']=usuarios

    return JsonResponse(result, safe=False)

'''DATOS: JSON (Listado con todas las guardias registradas en la 
base de datos para un año y un area especificada)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getGuardiasYearArea(request):
    year = request.GET.get('y','')
    area = request.GET.get('a','')

    guardias=[]
    if year!="" and area!="":
        guardias = CalendarioGuardiasGuardias.objects.using('guardias').filter(id_turno__id_area__id_area = 1, year=int(year)).values()

    return JsonResponse(list(guardias), safe=False)

'''DATOS: JSON (Listado con los analistas dados de alta pertenecientes a un área de trabajo)
    Formato especifico para insertarlo en un input select de sweetalert'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getAnalistasArea(request):
    area = request.GET.get('a','') #obtengo el id del area de trabajo
    dictAnalistas={}
    if area!='':
        personal = CalendarioPersonal.objects.using("guardias").filter(id_area=int(area), operativo=1)
        for analista in personal:
            user = User.objects.get(id=analista.id_usuario)
            dictAnalistas[analista.id_usuario]=user.first_name+" "+user.last_name

    resultjson = json.dumps(dictAnalistas)
    return JsonResponse(resultjson, safe=False)

'''DATOS: JSON (Listado con todos los dias festivos dado un año o no)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getFestivos(request):
    year = request.GET.get('y','')

    festivos=[]
    if year!="": #Si pido un año especifico...
        festivos =  CalendarioFestivos.objects.using('guardias').filter(fecha_local__year=int(year)).annotate(title=F('nombre'), start=F('fecha_local')).values('title', 'start')
    else: #Si pido todos los festivos...
        festivos =  CalendarioFestivos.objects.using('guardias').annotate(title=F('nombre'), start=F('fecha_local')).values('title', 'start')

    return JsonResponse(list(festivos), safe=False)














@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def createGuardia(request):

    idUser = request.GET.get('u','') #Id del analista
    fechaIni = request.GET.get('s','') #fecha_local_start (start)
    fechaFin = request.GET.get('e','') #fecha_local_end (end)

    guardia = []
    if idUser!="" and fechaIni!="" and fechaFin!="":
        analista = User.objects.get(id=int(idUser)) #Informacion completa del analista
        guardia.append([analista.id, #id_usuario
                        analista.first_name, #nombre analista
                        getAvatar(analista), #avatar
                        datetime.strptime(fechaIni, '%Y-%m-%d'), #fecha_local_start (start)
                        datetime.strptime(fechaFin, '%Y-%m-%d') + timedelta(days=1), #fecha_local_end (end)
                        True, #allDay (para poder ajustar la duracion de los eventos)
                        'guardias'])
    
    df_guardia = pd.DataFrame(guardia, columns=['idUser', 'nameUser', 'avatar', 'start', 'end', 'allDay', 'group'])
    
    return JsonResponse(df_guardia.to_dict('records'), safe=False)


'''DATOS: Elabora un calendario rotatorio en funcion de un área y un año especificado '''
@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def createCalendarRotatorio(request):
    
    area = request.GET.get('a','')
    year = request.GET.get('y','')

    try:
        UltimoUsuario= CalendarioGuardiasGuardias.objects.using("guardias"
                    ).filter(id_turno__id_area__id_area = int(area), year= int(year)-1
                    ).order_by('-semana','id_guardia').values('id_user_analista').first() 

        #Obtengo al personal implicado en las guardias del area seleccionada con el nuevo orden rotacional
        personal= CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = int(area), operativo = 1).values('id_usuario').order_by('id_usuario')
        personal = ListadoPersonal(personal, UltimoUsuario, area)

        #Obtengo el listado de semanas completo (num semana, fecha inicio, fecha fin)
        df_semanas = getListadoSemanas(int(year))

        #Genero el listado de guardias automáticamente
        df_guardias=RotacionGuardias(personal, df_semanas, 0)
        df_guardias['nameUser'] =df_guardias.apply(lambda row: User.objects.get(id=row['idUser']).first_name, axis=1)
        df_guardias['avatar'] =df_guardias.apply(lambda row: getAvatar(User.objects.get(id=row['idUser'])), axis=1)

    except Exception as e:
        print("ERROR createCalendarRotatorio: ", e)
        df_guardias = pd.DataFrame()

    return JsonResponse(df_guardias.to_dict('records'), safe=False)


'''DATOS: Elabora un calendario RAREX en funcion de un año especificado '''
@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def createCalendarRarex(request):
    
    area = request.GET.get('a','')
    year = request.GET.get('y','')

    try:
        #Obtengo...
        #1. UltimoUsuarioVerde: Ultimo usuario en realizar la ultima guardia Verde o de tipo 0
        #2. UltimoUsuarioNaranja: Ultimo usuario en realizar la ultima guardia Naranja o de tipo 1
        #3. UltimoUsuarioRojo: Ultimo usuario en realizar la ultima guardia Rosa o de Tipo 2 (siempre va a ser el de la ultima semana de Navidad)
        UltimoUsuarioVerde= CalendarioGuardiasGuardias.objects.using("guardias").filter(id_turno__id_area__id_area = int(area), year=int(year)-1, tipo_semana=0).order_by('-semana','id_guardia').values('id_user_analista').first() 
        UltimoUsuarioNaranja= CalendarioGuardiasGuardias.objects.using("guardias").filter(id_turno__id_area__id_area = int(area), year=int(year)-1, tipo_semana =1).order_by('-semana','id_guardia').values('id_user_analista').first() 
        UltimoUsuarioRojo= CalendarioGuardiasGuardias.objects.using("guardias").filter(id_turno__id_area__id_area = int(area), year=int(year)-1, tipo_semana=2).order_by('-semana','id_guardia').values('id_user_analista').first() 

        #Obtengo al personal implicado en las guardias del area seleccionada
        personal = CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = int(area), operativo = 1).exclude(supervisor=1).values('id_usuario').order_by('id_usuario')

        #Obtengo el orden del personal para realizar las semanas verdes o de tipo 0
        personal_verde = ListadoPersonal(personal, UltimoUsuarioVerde, area)
        #Obtengo el orden del personal para realizar las semanas naranjas o de tipo 1
        personal_naranja = ListadoPersonal(personal, UltimoUsuarioNaranja, area)
        #Obtengo el orden del personal para realizar las semanas rojas o de tipo 2
        personal_vacaciones = CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = int(area), operativo = 1).values('id_usuario').order_by('id_usuario')
        num_analistas = personal_vacaciones.count() #numero de analistas datos de alta
        personal_rojo = ListadoPersonal(personal_vacaciones, UltimoUsuarioRojo, area)

        #Obtengo el listado de semanas completo (num semana, fecha inicio, fecha fin)
        df_semanas = getListadoSemanas(int(year))

        #Obtengo el listado de semanas festivas (num semana) 
        df_festivos = getListadoAnualSemFestivas(int(year))

        #Obtengo un array con las semanas rojas (Semana Santa, Puente Diciembre, Navidad 1, Navidad 2)
        df_semanas_rojas = getSemanasRojas(int(year))
        df_semanas_rojas = df_semanas.loc[df_semanas['semana'].isin(df_semanas_rojas)]

        #Obtengo un array con las semanas verdes
        df_semanas_verdes = df_semanas.loc[~df_semanas['semana'].isin(df_festivos['semana'].tolist())]
        df_semanas_verdes = df_semanas_verdes.loc[~df_semanas_verdes['semana'].isin(df_semanas_rojas['semana'].tolist())]

        #Obtengo un array con las semanas naranjas
        df_semanas_naranjas = df_semanas.loc[df_semanas['semana'].isin(df_festivos['semana'].tolist())]
        df_semanas_naranjas = df_semanas_naranjas.loc[~df_semanas_naranjas['semana'].isin(df_semanas_rojas['semana'].tolist())]

        #Genero el listado de guardias verdes automáticamente
        df_guardias_verdes=RotacionGuardias(personal_verde, df_semanas_verdes, 0)
        #Genero el listado de guardias naranjas automáticamente
        df_guardias_naranjas=RotacionGuardias(personal_naranja, df_semanas_naranjas, 1)
        #Genero el listado de guardias rojas automáticamente
        num_rot = NumRot(num_analistas)
        if UltimoUsuarioRojo!=None:
            personal_rojo = [RotatePersonal(personal_rojo, num_rot*3)[0],
                            RotatePersonal(personal_rojo, num_rot*2)[0],
                            RotatePersonal(personal_rojo, num_rot*1)[0],
                            RotatePersonal(personal_rojo, num_rot*0)[0]]
        else:
            personal_rojo = [RotatePersonal(personal_rojo, -(num_rot*0))[0], 
                                RotatePersonal(personal_rojo, -(num_rot*1))[0],
                                RotatePersonal(personal_rojo, -(num_rot*2))[0],
                                RotatePersonal(personal_rojo, -(num_rot*3))[0]]
                                    
        df_guardias_rojas=RotacionGuardias(personal_rojo, df_semanas_rojas, 2)
        print("Personal Rojo")
        print(df_guardias_rojas)

        #Obtengo el listado completo de guardias
        frames = [df_guardias_verdes, df_guardias_naranjas, df_guardias_rojas]
        df_guardias = pd.concat(frames).sort_values(by=["start"])
        df_guardias.reset_index(drop=True, inplace=True)

        #Hago los cambios oportunos en el caso de que haya semanas de guardias continuas para un analista
        cambios = CambioSemanasContinuas(df_guardias)
        df_guardias = cambios['guardias']
        cambios_pendientes = cambios['cambios']

        #Hago los cambios oportunos en el caso de que haya festivos que caen en lunes o martes y que por tanto afecten a dos analistas
        df_guardias = CambioPuentes(df_guardias, int(year), df_semanas_naranjas)
        df_guardias['nameUser'] =df_guardias.apply(lambda row: User.objects.get(id=row['idUser']).first_name, axis=1)
        df_guardias['avatar'] =df_guardias.apply(lambda row: getAvatar(User.objects.get(id=row['idUser'])), axis=1)

        print("GUARDIAS RAREX")
        print(df_guardias)
            
    except Exception as e:
        print("ERROR setCalendarRarex: ", e)
        df_guardias = pd.DataFrame()
        cambios_pendientes = []
    
    result={}
    result["guardias"]=df_guardias.to_dict('records')
    result["cambios"]=cambios_pendientes
    return JsonResponse(result, safe=False)

@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def modificarCalendarioRotatorio(request):
    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error"
    mensaje["sms"] = ""
    mensaje["descripcion"] = ""

    result={}
    result["mensaje"]=mensaje

    idAreaAltaBaja = request.GET.get('a','') #Obtengo el area
    idUserAltaBaja = request.GET.get('u','') #Obtengo el usuario que quiero dar de Alta o de Baja
    fechaAltaBaja = request.GET.get('f','') #Obtengo la fecha de alta/baja
    estadoAltaBaja = request.GET.get('e', '') #Obtengo si deseo dar de alta o de baja al analista (1: Alta, 0: Baja)

    if idAreaAltaBaja!="" and idUserAltaBaja!="" and fechaAltaBaja!="" and estadoAltaBaja!="":

        fechaAltaBaja = datetime.strptime(fechaAltaBaja, '%Y-%m-%d') # fecha
        year = fechaAltaBaja.year #año 
        semana = fechaAltaBaja.isocalendar()[1] #numero de semana
        infoAnalista = User.objects.get(id=int(idUserAltaBaja)) #informacion completa del analista
        
        try:
            if int(estadoAltaBaja)==1: #Alta usuario
                supervisorUser = request.GET.get('s', '') 
                textAltaBaja = "alta"
                
                #Obtengo la guardia de la semana seleccionada a partir de la cual debo dar de alta al nuevo analista (sin incluir esta)
                guardia = CalendarioGuardiasGuardias.objects.using("guardias"
                        ).filter(id_turno__id_area__id_area = int(idAreaAltaBaja), 
                                year = int(year),
                                semana__gte = int(semana)
                        ).annotate(turno = F('id_turno__id_turno')
                        ).order_by('id_guardia').values('id_guardia', 'id_user_analista', 'turno').first()
               
                #Obtengo el objeto del area seleccionada
                area = CalendarioAreas.objects.using('guardias').get(id_area = int(idAreaAltaBaja))

                #Doy de alta al nuevo analista
                new_values = {"id_usuario": int(idUserAltaBaja), 
                            "id_area": area, 
                            "operativo": 1,
                            "supervisor": int(supervisorUser),
                            "superinformado" : 0} 
                
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=1, supervisor = int(supervisorUser))
                if not update_analista:
                    # if not exists, create new
                    CalendarioPersonal.objects.using("guardias").create(**new_values)
                
                if guardia!=None:
                    idGuardia = guardia.get('id_guardia') #Obtengo el id de la guardia anterior a partir de la cual tengo que establecer los cambios
                    UltimoUsuario = guardia #Obtengo el id del usuario de la siguiente guardia a partir de la cual tengo que establecer los cambios
                    turno = CalendarioTurnos.objects.using("guardias" #Obtengo el turno de trabajo que debo asignar a los cambios de guardia
                        ).get(id_turno = guardia.get('turno'))

                else:
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="No se han encontrado guardias registradas por lo que no se ha actualizado ningún Calendario de Guardias tras haber dado de "+textAltaBaja+" al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre
                    mensaje["icon"]="warning"
                    return JsonResponse(mensaje, safe=False)
            
            elif int(estadoAltaBaja)==0:#Baja usuario
                textAltaBaja = "baja"

                #Obtengo la primera guardia (igual o mayor a la semana seleccionada) del usuario que deseo dar de baja
                proximaGuardia = CalendarioGuardiasGuardias.objects.using("guardias"
                        ).filter(id_turno__id_area__id_area = int(idAreaAltaBaja), 
                                year = int(year),
                                semana__gte = int(semana),
                                id_user_analista = int(idUserAltaBaja)
                        ).order_by('id_guardia').values('semana').first()

                #Doy de baja al analista
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=0)
                if not update_analista: #Si se ha producido un error al dar de baja al analista seleccionado...
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="Error al intentar dar de baja al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +". Vuelve a intentarlo en unos minutos."
                    mensaje["icon"]="error"
                    return JsonResponse(mensaje, safe=False)
                
                if proximaGuardia!=None:      
                    #Obtengo la guardia de la semana a partir de la cual debo dar de baja al nuevo analista (sin incluir esta)
                    guardia = CalendarioGuardiasGuardias.objects.using("guardias"
                            ).filter(id_turno__id_area__id_area = int(idAreaAltaBaja), 
                                    year = int(year),
                                    semana__lt = proximaGuardia.get('semana')
                            ).annotate(turno = F('id_turno__id_turno')       
                            ).order_by('-semana', 'id_guardia').values('id_guardia', 'id_user_analista', 'semana', 'turno').first()
                   
                    if guardia!=None:
                        idGuardia = guardia.get('id_guardia') #Obtengo el id de la siguiente guardia a partir de la cual tengo que establecer los cambios
                        UltimoUsuario = guardia #Obtengo el id del usuario de la siguiente guardia a partir de la cual tengo que establecer los cambios
                        turno = CalendarioTurnos.objects.using("guardias" #Obtengo el turno de trabajo que debo asignar a los cambios de guardia
                        ).get(id_turno = guardia.get('turno'))
                        semana = guardia.get('semana') #Obtengo el numero de semana a partir de la cual debo realizar los cambios
                        
                    else:
                        mensaje["title"]="Opps! ..."
                        mensaje["text"]="No se han encontrado guardias registradas por lo que no se ha actualizado ningún Calendario de Guardias tras haber dado de "+textAltaBaja+" al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre
                        mensaje["icon"]="warning"
                        return JsonResponse(mensaje, safe=False)
                else:
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="No se han encontrado guardias registradas por lo que no se ha actualizado ningún Calendario de Guardias tras haber dado de "+textAltaBaja+" al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre
                    mensaje["icon"]="warning"
                    return JsonResponse(mensaje, safe=False)
            
            #Obtengo al personal implicado en las guardias del area seleccionada con el nuevo orden rotacional
            personal= CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = int(idAreaAltaBaja), operativo = 1).values('id_usuario').order_by('id_usuario') 
            personal = ListadoPersonal(personal, UltimoUsuario, idAreaAltaBaja)

            #Obtengo el listado de semanas completo (num semana, fecha inicio, fecha fin)
            df_semanas = getListadoSemanas(int(year))
            df_semanas = df_semanas.loc[(df_semanas['semana'] > semana)] #Solo obtengo las semanas que tengo que modificar (a partir de la siguiente a la seleccionada)

            #Genero el listado de guardias automáticamente
            df_guardias=RotacionGuardias(personal, df_semanas, 0)
            
            #Obtengo las nuevas guardias del nuevo calendario creado para ser insertadas en la base de datos
            df_guardias['fecha_local_start'] = df_guardias.apply(lambda row : row['start'], axis = 1)
            df_guardias['fecha_local_end'] = df_guardias.apply(lambda row :row['end'] + timedelta(days=-1), axis = 1)
            df_guardias['year'] = int(year)
            df_guardias['semana'] = df_guardias.apply(lambda row : isoweek.Week.withdate(row['fecha_local_end']).week, axis = 1)
            df_guardias['id_user_analista'] = df_guardias.apply(lambda row : row['idUser'], axis = 1)
            df_guardias['id_turno'] = turno
            df_guardias['tipo_semana'] = 0 #PENDIENTE DE ACTUALIZARLO PARA PODER HACER ESTUDIO COMPARATIVO
            df_guardias['id_user_modificado'] = request.user.id
            df_guardias['tipo_guardia'] = 1
            df_guardias['supervisado'] = 1
            df_guardias['valido'] = 1

            df_guardias = df_guardias.drop(columns=['idUser', 'start', 'end', 'allDay', 'group']) #Elimino las columnas que no me interesan
            df_guardias = df_guardias.sort_values(by=['semana', 'fecha_local_start'])

            #Guardo una copia por si acaso se produce un error
            guardias_historicas =   CalendarioGuardiasGuardias.objects.using('guardias').filter(year=int(year), id_turno__id_area__id_area=int(idAreaAltaBaja), semana__gt=int(semana)).order_by('id_guardia') #id_guardia__gt=int(idGuardia),
            df_guardias_historicas = pd.DataFrame(guardias_historicas.values())
            guardias_historicas.delete()  #Borro los registros que ya existían para este año y los cuales voy a modificar

            try:
                #Cargo de forma masiva a través de un json las nuevas guardias
                CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                    CalendarioGuardiasGuardias(**vals) for vals in df_guardias.to_dict('records')
                )
                mensaje["title"]=""
                mensaje["text"]="Ha sido moficado el calendario de guardias "+str(year)+" tras haber dado de "+textAltaBaja+" a "+infoAnalista.first_name+" "+infoAnalista.last_name+" en el área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +"."
                mensaje["icon"]="success" 
                mensaje["sms"] = "Se ha dado de "+textAltaBaja+" a "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +" a fecha "+ datetime.strftime(fechaAltaBaja, "%d %b, %Y")
                mensaje["descripcion"] = "El resto de analistas deberá comprobar los cambios efectuados en el calendario a partir de la fecha de "+ textAltaBaja +" señalada anteriormente. Posdata: enorabuena a los premiados, os quiere Paula"
            except:
                #Si se produce un error doy de alta/baja temporal al nuevo analista hasta que se resuelva el problema
                if int(estadoAltaBaja)==1:
                    update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=0)
                elif int(estadoAltaBaja)==0:
                    update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=1)
                
                #Cargo de forma masiva a través de un json las nuevas guardias
                CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                    CalendarioGuardiasGuardias(**vals) for vals in df_guardias_historicas.to_dict('records')
                )

                mensaje["title"]="Opps! ..."
                mensaje["text"]="Se ha producido un error al intentar actualizar los cambios de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +". Vuelve a intentarlo en unos minutos."
                mensaje["icon"]="error"

        except Exception as e:
            print("ERROR", e)
            #Si se produce un error doy de alta/baja temporal al nuevo analista hasta que se resuelva el problema
            if int(estadoAltaBaja)==1:
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=0)
            elif int(estadoAltaBaja)==0:
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=1)
            mensaje["title"]="Opps! ..."
            mensaje["text"]="Se ha producido un error al intentar dar de "+textAltaBaja+" a "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +". Vuelve a intentarlo en unos minutos."
            mensaje["icon"]="error"

    result["mensaje"]=mensaje
    return JsonResponse(result, safe=False)

@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def modificarCalendarioRarex(request):
    mensaje={}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error"
    mensaje["sms"] = ""
    mensaje["descripcion"] = ""

    result={}
    result["mensaje"]=mensaje
    result["cambios"]=[]

    idAreaAltaBaja = request.GET.get('a','') #Obtengo el area
    idUserAltaBaja = request.GET.get('u','') #Obtengo el usuario que quiero dar de Alta o de Baja
    fechaAltaBaja = request.GET.get('f','') #Obtengo la fecha de alta/baja
    estadoAltaBaja = request.GET.get('e', '') #Obtengo si deseo dar de alta o de baja al analista (1: Alta, 0: Baja)
    supervisorUser = request.GET.get('s', '') 

    if idAreaAltaBaja!="" and idUserAltaBaja!="" and fechaAltaBaja!="" and estadoAltaBaja!="":
        fechaAltaBaja = datetime.strptime(fechaAltaBaja, '%Y-%m-%d')
        year = fechaAltaBaja.year
        semana = fechaAltaBaja.isocalendar()[1]
        infoAnalista = User.objects.get(id=int(idUserAltaBaja))
        
        try:
            if int(estadoAltaBaja)==1: #Alta usuario
                supervisorUser = request.GET.get('s', '') 
                textAltaBaja = "alta"

                #Obtengo la guardia de la semana seleccionada a partir de la cual debo dar de alta al nuevo analista (sin incluir esta)
                guardia = CalendarioGuardiasGuardias.objects.using("guardias"
                        ).filter(id_turno__id_area__id_area = int(idAreaAltaBaja), 
                                year = int(year),
                                semana__gte = int(semana)
                        ).annotate(turno = F('id_turno__id_turno')
                        ).order_by('id_guardia').values('id_guardia', 'id_user_analista', 'turno').first()

                print("PRIMERA GUARDIA A PARTIR DE LA CUAL APLICAR CAMBIOS", guardia)

                #Obtengo el objeto del area seleccionada
                area = CalendarioAreas.objects.using('guardias').get(id_area = int(idAreaAltaBaja))

                #Doy de alta al nuevo analista
                new_values = {"id_usuario": int(idUserAltaBaja), 
                            "id_area": area, 
                            "operativo": 1,
                            "supervisor":int(supervisorUser),
                            "superinformado": 0} 
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=1, supervisor=int(supervisorUser))
                if not update_analista:
                    # if not exists, create new
                    CalendarioPersonal.objects.using("guardias").create(**new_values)
       
                if guardia!=None:
                    idGuardia = guardia.get('id_guardia') #Obtengo el id de la siguiente guardia a partir de la cual tengo que establecer los cambios
                    turno = CalendarioTurnos.objects.using("guardias" #Obtengo el turno de trabajo que debo asignar a los cambios de guardia
                            ).get(id_turno = guardia.get('turno')) 

                else:
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="No se han encontrado guardias registradas por lo que no se ha actualizado ningún Calendario de Guardias tras haber dado de "+textAltaBaja+" al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre
                    mensaje["icon"]="warning"
                    result["mensaje"]=mensaje
                    return JsonResponse(result, safe=False)
                

            elif int(estadoAltaBaja)==0:#Baja usuario
                textAltaBaja = "baja"

                #Obtengo la primera guardia (igual o mayor a la semana seleccionada) del usuario que deseo dar de baja
                proximaGuardia = CalendarioGuardiasGuardias.objects.using("guardias"
                        ).filter(id_turno__id_area__id_area = int(idAreaAltaBaja), 
                                year = int(year),
                                semana__gte = int(semana),
                                id_user_analista = int(idUserAltaBaja)
                        ).order_by('id_guardia').values('semana').first()

                #Doy de baja al analista
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=0)

                if not update_analista: #Si se ha producido un error al dar de baja al analista seleccionado...
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="Error al intentar dar de baja al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +". Vuelve a intentarlo en unos minutos."
                    mensaje["icon"]="error"
                    result["mensaje"]=mensaje
                    return JsonResponse(result, safe=False)
                
                if proximaGuardia!=None:      
                    #Obtengo la guardia de la semana a partir de la cual debo dar de alta al nuevo analista (sin incluir esta)
                    guardia = CalendarioGuardiasGuardias.objects.using("guardias"
                            ).filter(id_turno__id_area__id_area = int(idAreaAltaBaja), 
                                    year = int(year),
                                    semana__lt = proximaGuardia.get('semana')
                            ).annotate(turno = F('id_turno__id_turno')
                            ).order_by('-semana', 'id_guardia').values('id_guardia', 'id_user_analista', 'semana', 'turno').first()

                    if guardia!=None:
                        idGuardia = guardia.get('id_guardia') #Obtengo el id de la siguiente guardia a partir de la cual tengo que establecer los cambios
                        turno = CalendarioTurnos.objects.using("guardias" #Obtengo el turno de trabajo que debo asignar a los cambios de guardia
                        ).get(id_turno = guardia.get('turno'))
                        semana = guardia.get('semana') #Obtengo el numero de semana a partir de la cual debo realizar los cambios

                    else:
                        mensaje["title"]="Opps! ..."
                        mensaje["text"]="No se han encontrado guardias registradas por lo que no se ha actualizado ningún Calendario de Guardias tras haber dado de "+textAltaBaja+" al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre
                        mensaje["icon"]="warning"
                        result["mensaje"]=mensaje
                        return JsonResponse(result, safe=False)
                else:
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="No se han encontrado guardias registradas por lo que no se ha actualizado ningún Calendario de Guardias tras haber dado de "+textAltaBaja+" al analista "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre
                    mensaje["icon"]="warning"
                    result["mensaje"]=mensaje
                    return JsonResponse(result, safe=False)

            #Obtengo el personal implicado en las guardias del area seleccionada
            personal= CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = int(idAreaAltaBaja), operativo = 1).exclude(supervisor = 1).values('id_usuario').order_by('id_usuario')

            #1.1. Si hubo guardias el año anterior para el area especificada...
            #if count>0:
            #Obtengo...
            #1. UltimoUsuarioVerde: Ultimo usuario en realizar la ultima guardia Verde o de tipo 0
            #2. UltimoUsuarioNaranja: Ultimo usuario en realizar la ultima guardia Naranja o de tipo 1
            #3. UltimoUsuarioRojo: Ultimo usuario en realizar la ultima guardia Rosa o de Tipo 2 (siempre va a ser el de la ultima semana de Navidad)
            UltimoUsuarioVerde= CalendarioGuardiasGuardias.objects.using("guardias").filter(id_turno__id_area__id_area = int(idAreaAltaBaja), tipo_semana=0, semana__lte=semana).order_by('-year','-semana','id_guardia').values('id_user_analista').first() 
            UltimoUsuarioNaranja= CalendarioGuardiasGuardias.objects.using("guardias").filter(id_turno__id_area__id_area = int(idAreaAltaBaja), tipo_semana=1, semana__lte=semana).order_by('-year','-semana','id_guardia').values('id_user_analista').first() 
            UltimoUsuarioRojo= CalendarioGuardiasGuardias.objects.using("guardias").filter(id_turno__id_area__id_area = int(idAreaAltaBaja), tipo_semana=2, year=int(year)-1).order_by('-semana','id_guardia').values('id_user_analista').first() 
            
            #Obtengo el orden del personal para realizar las semanas verdes o de tipo 0
            personal_verde = ListadoPersonal(personal, UltimoUsuarioVerde, idAreaAltaBaja)
            #Obtengo el orden del personal para realizar las semanas naranjas o de tipo 1
            personal_naranja = ListadoPersonal(personal, UltimoUsuarioNaranja, idAreaAltaBaja)
            #Obtengo el orden del personal para realizar las semanas rojas o de tipo 2
            personal_vacaciones= CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = int(idAreaAltaBaja), operativo = 1).values('id_usuario').order_by('id_usuario')
            num_analistas = personal_vacaciones.count() #numero de analistas datos de alta
            personal_rojo = ListadoPersonal(personal_vacaciones, UltimoUsuarioRojo, idAreaAltaBaja)

            #Obtengo el listado de semanas completo (num semana, fecha inicio, fecha fin)
            df_semanas_year = getListadoSemanas(int(year))
            df_semanas = df_semanas_year.loc[(df_semanas_year['semana'] > semana)] #Solo obtengo las semanas que tengo que modificar (a partir de la siguiente a la seleccionada)

            #Obtengo el listado de semanas festivas (num semana) 
            df_festivos = getListadoAnualSemFestivas(int(year))
            df_festivos = df_festivos.loc[(df_festivos['semana'] > semana)] #Solo obtengo las semanas que tengo que modificar (a partir de la siguiente a la seleccionada)

            #Obtengo un array con las semanas rojas (Semana Santa, Puente Diciembre, Navidad 1, Navidad 2)
            df_semanas_rojas = getSemanasRojas(int(year))
            df_semanas_rojas = df_semanas_year.loc[df_semanas_year['semana'].isin(df_semanas_rojas)]
            #df_semanas_rojas = df_semanas_rojas.loc[(df_semanas_rojas['semana'] > semana)] #Solo obtengo las semanas que tengo que modificar (a partir de la siguiente a la seleccionada)

            #Obtengo un array con las semanas verdes
            df_semanas_verdes = df_semanas.loc[~df_semanas['semana'].isin(df_festivos['semana'].tolist())]
            df_semanas_verdes = df_semanas_verdes.loc[~df_semanas_verdes['semana'].isin(df_semanas_rojas['semana'].tolist())]
            df_semanas_verdes = df_semanas_verdes.loc[(df_semanas_verdes['semana'] > semana)] #Solo obtengo las semanas que tengo que modificar (a partir de la siguiente a la seleccionada)

            #Obtengo un array con las semanas naranjas
            df_semanas_naranjas = df_semanas.loc[df_semanas['semana'].isin(df_festivos['semana'].tolist())]
            df_semanas_naranjas = df_semanas_naranjas.loc[~df_semanas_naranjas['semana'].isin(df_semanas_rojas['semana'].tolist())]
            df_semanas_naranjas = df_semanas_naranjas.loc[(df_semanas_naranjas['semana'] > semana)] #Solo obtengo las semanas que tengo que modificar (a partir de la siguiente a la seleccionada)

            #Genero el listado de guardias verdes automáticamente
            df_guardias_verdes=RotacionGuardias(personal_verde, df_semanas_verdes, 0)
            #Genero el listado de guardias naranjas automáticamente
            df_guardias_naranjas=RotacionGuardias(personal_naranja, df_semanas_naranjas, 1)
            #Genero el listado de guardias rojas automáticamente
            num_rot = NumRot(num_analistas)                        
            if UltimoUsuarioRojo!=None:
                personal_rojo = [#RotatePersonal(aux_personal, num_rot*4)[0], 
                                RotatePersonal(personal_rojo, num_rot*3)[0],
                                RotatePersonal(personal_rojo, num_rot*2)[0],
                                RotatePersonal(personal_rojo, num_rot*1)[0],
                                RotatePersonal(personal_rojo, num_rot*0)[0]]
            else:
                personal_rojo = [RotatePersonal(personal_rojo, -(num_rot*0))[0], 
                                    RotatePersonal(personal_rojo, -(num_rot*1))[0],
                                    RotatePersonal(personal_rojo, -(num_rot*2))[0],
                                    RotatePersonal(personal_rojo, -(num_rot*3))[0]]
                                #RotatePersonal(personal, -(num_rot*4))[0]]  

            #personal_rojo = personal_rojo[-len((df_semanas_rojas.loc[(df_semanas_rojas['semana'] > semana)]).index):]
            df_guardias_rojas=RotacionGuardias(personal_rojo, df_semanas_rojas, 2)
            df_guardias_rojas = df_guardias_rojas.loc[(df_guardias_rojas['semana'] > semana)]

            #Obtengo el listado completo de guardias
            frames = [df_guardias_verdes, df_guardias_naranjas, df_guardias_rojas]
            df_guardias = pd.concat(frames).sort_values(by=["start"])
            df_guardias.reset_index(drop=True, inplace=True)

            #Hago los cambios oportunos en el caso de que haya semanas de guardias continuas para un analista
            cambios = CambioSemanasContinuas(df_guardias)
            df_guardias = cambios['guardias']
            cambios_pendientes = cambios['cambios']

            #Hago los cambios oportunos en el caso de que haya festivos que caen en lunes o martes y que por tanto afecten a dos analistas
            df_guardias = CambioPuentes(df_guardias, int(year), df_semanas_naranjas)

            #Obtengo las nuevas guardias del nuevo calendario creado para ser insertadas en la base de datos
            df_guardias['fecha_local_start'] = df_guardias.apply(lambda row : row['start'], axis = 1)
            df_guardias['fecha_local_end'] = df_guardias.apply(lambda row :row['end'] + timedelta(days=-1), axis = 1)
            df_guardias['year'] = int(year)
            df_guardias['semana'] = df_guardias.apply(lambda row :  getNumSemanaGuardiaRarex(row["fecha_local_start"],row['fecha_local_end']), axis = 1)
            df_guardias['id_user_analista'] = df_guardias.apply(lambda row : row['idUser'], axis = 1)
            df_guardias['id_turno'] = turno
            df_guardias['id_user_modificado'] = request.user.id
            df_guardias['tipo_semana'] = df_guardias.apply(lambda row : getTipoSemana(int(year), row['semana']), axis = 1)
            df_guardias['tipo_guardia'] = 1
            df_guardias['supervisado'] = 1
            df_guardias['valido'] = 1

            df_guardias = df_guardias.drop(columns=['idUser', 'start', 'end', 'allDay', 'group']) #Elimino las columnas que no me interesan
            df_guardias = df_guardias.sort_values(by=['semana', 'fecha_local_start'])
            result["cambios"]=cambios_pendientes

            print("GUARDIAS RAREX FIN")
            print(df_guardias) 

            #Guardo una copia por si acaso se produce un error
            guardias_historicas =  CalendarioGuardiasGuardias.objects.using('guardias').filter(year=int(year), id_turno__id_area__id_area=int(idAreaAltaBaja), semana__gt=int(semana)).order_by('id_guardia') #id_guardia__gt=int(idGuardia),
            df_guardias_historicas = pd.DataFrame(guardias_historicas.values())
            guardias_historicas.delete() #Borro los registros que ya existían para este año y los cuales voy a modificar

            try:                 
                #Cargo de forma masiva a través de un json las nuevas guardias
                CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                    CalendarioGuardiasGuardias(**vals) for vals in df_guardias.to_dict('records')
                )
                mensaje["title"]=""
                mensaje["text"]="Ha sido moficado el calendario de guardias "+str(year)+" tras haber dado de "+textAltaBaja+" a "+infoAnalista.first_name+" "+infoAnalista.last_name+" en el área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +"."
                mensaje["icon"]="success" 
                mensaje["sms"] = "Se ha dado de "+textAltaBaja+" a "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +" a fecha "+ datetime.strftime(fechaAltaBaja, "%d %b, %Y")
                mensaje["descripcion"] = "El resto de analistas deberá comprobar los cambios efectuados en el calendario a partir de la fecha de "+ textAltaBaja +" señalada anteriormente. Posdata: enorabuena a los premiados, os quiere Paula"
            except:
                #Si se produce un error doy de alta/baja temporal al nuevo analista hasta que se resuelva el problema
                if int(estadoAltaBaja)==1:
                    update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=0)
                elif int(estadoAltaBaja)==0:
                    update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=1)
                
                #Cargo de forma masiva a través de un json las nuevas guardias
                CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                    CalendarioGuardiasGuardias(**vals) for vals in df_guardias_historicas.to_dict('records')
                )

                mensaje["title"]="Opps! ..."
                mensaje["text"]="Se ha producido un error al intentar actualizar los cambios de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +". Vuelve a intentarlo en unos minutos."
                mensaje["icon"]="error"
                    
        except Exception as e:
            print("Error: modificarCalendarioRarex", e)
            #Si se produce un error doy de alta/baja temporal al nuevo analista hasta que se resuelva el problema
            if int(estadoAltaBaja)==1:
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=0)
            elif int(estadoAltaBaja)==0:
                update_analista = CalendarioPersonal.objects.using('guardias').filter(id_usuario = int(idUserAltaBaja), id_area__id_area=int(idAreaAltaBaja)).update(operativo=1)
            mensaje["title"]="Opps! ..."
            mensaje["text"]="Se ha producido un error al intentar dar de "+textAltaBaja+" a "+infoAnalista.first_name+" "+infoAnalista.last_name+ " en el calendario de guardias perteneciente al área de "+ CalendarioAreas.objects.using("guardias").get(id_area=int(idAreaAltaBaja)).nombre +". Vuelve a intentarlo en unos minutos."
            mensaje["icon"]="error"
    
    result["mensaje"]=mensaje

    return JsonResponse(result, safe=False)



def NumRot(numAnalistas):
    if numAnalistas % 2 == 0: #Num analistas par...
        num_rot = numAnalistas/2
        if num_rot % 2 == 0: #Num rot par     
            num_rot = num_rot - 1
        else:
            num_rot = num_rot + 2
    else: #Num analistas impar
        num_rot = math.floor(numAnalistas/2)
    return int(num_rot)

def CambioSemanasContinuas(df_guardias):
    result={}
    cambios_no_realizados = []

    for index, row in df_guardias.iterrows():
        if row['tipo_semana']>0: #Busco las semanas donde puede haber conflicto (semanas festivas, de tipo 1 y 2)      

                user_1 = UserCambio(df_guardias, index-2)
                user_2 = UserCambio(df_guardias, index-1)
                user = row["idUser"]
                user_3 = UserCambio(df_guardias, index+1)
                user_4 = UserCambio(df_guardias, index+2)

                if user_2==user:
                    if index+2 in df_guardias.index:
                        if user_1!=None:
                            df_guardias_cambios = df_guardias[(df_guardias.index>index+2) & (df_guardias['idUser']!=user_1) & (df_guardias['tipo_semana']==0)]
                        else:
                            df_guardias_cambios = df_guardias[(df_guardias.index>index+2) & (df_guardias['tipo_semana']==0)]

                        if len(df_guardias_cambios.index)>0:
                            index_inicial =  index-1
                            index_cambio = df_guardias_cambios.first_valid_index()
                            user_inicial =  df_guardias.iloc[index_inicial]['idUser']
                            user_cambio = df_guardias.iloc[index_cambio]['idUser']
                            df_guardias.at[index_inicial, 'idUser'] = user_cambio
                            df_guardias.at[index_cambio, 'idUser'] = user_inicial
                        else:
                            cambios_no_realizados.append(row["semana"]-1)
                        
                    else:
                        cambios_no_realizados.append(row["semana"]-1)
                            
                
                if user_3==user:
                    if index+3 in df_guardias.index:
                        if user_4!=None:
                            df_guardias_cambios = df_guardias[(df_guardias.index>index+3) & (df_guardias['idUser']!=user_4) & (df_guardias['tipo_semana']==0)]
                        else:
                            df_guardias_cambios = df_guardias[(df_guardias.index>index+3) & (df_guardias['tipo_semana']==0)]

                        if len(df_guardias_cambios.index)>0:
                            index_inicial =  index+1
                            index_cambio = df_guardias_cambios.first_valid_index()
                            user_inicial =  df_guardias.iloc[index_inicial]['idUser']
                            user_cambio = df_guardias.iloc[index_cambio]['idUser']
                            df_guardias.at[index_inicial, 'idUser'] = user_cambio
                            df_guardias.at[index_cambio, 'idUser'] = user_inicial
                        else:
                            cambios_no_realizados.append(row["semana"]+1)
                    else:
                        cambios_no_realizados.append(row["semana"]+1)

    print("GUARDIAS CAMBIOS PAULA")
    print(df_guardias)
    df_guardias = df_guardias.sort_values(by="start")
    
    result['guardias']=df_guardias
    result['cambios']=cambios_no_realizados
    #df_guardias['idUser']=  df_guardias.apply(lambda row : int(row['idUser']), axis = 1)   
    return result

def UserCambio(df_guardias, index):
    if index in df_guardias.index:
        user = (df_guardias.iloc[index]['idUser'])
    else:
        user = None
    return user


def CambioPuentes(df_guardias, year, semanas_naranjas):
    #Obtengo las semanas festivas (naranjas tipo 1) que tienen festivos en Lunes y por tanto afectan a dos analistas
    semanas = CalendarioFestivos.objects.using('guardias'
    ).filter(fecha_local__year=int(year), 
            fecha_local__week__in=semanas_naranjas['semana'].tolist(), 
            fecha_local__week__gt=1,
            fecha_local__week_day__in=[2] #,3]
    ).annotate(week=ExtractWeek('fecha_local')).values('week') 
    
    if semanas.count()>0: #Si se han encontrado semanas naranjas con festivo en lunes...
        df_semanas = pd.DataFrame(semanas)
        df_semanas = df_semanas['week'].tolist()
        print("SEMANAS PUENTES", df_semanas)

        for semana in df_semanas:

            #Obtengo la semana en la que tengo que modificar las fecha de inicio y fin
            indexAnalista = df_guardias.index[df_guardias['semana']==semana].tolist()[0]
            tiposembefore = df_guardias.at[indexAnalista-1,'tipo_semana']

            print("INFO", indexAnalista, tiposembefore)

            if tiposembefore==0:
                #En primer lugar modifico la fecha de inicio y fin del analista que le ha tocado la semana con festivo
                #Comienzo la semana de guardias en sabado
                df_guardias.loc[indexAnalista,'start'] =  df_guardias.loc[indexAnalista,'start'] + timedelta(days=-2)
                #Termino la semana de guardias en viernes
                df_guardias.loc[indexAnalista,'end'] =  df_guardias.loc[indexAnalista,'end'] + timedelta(days=-2)
                

                #Añado un nuevo registro para que el analista de la semana anterior haga el fin de semana posterior
                new_guardia={}
                new_guardia['idUser'] = df_guardias.at[indexAnalista-1,'idUser']
                new_guardia['start'] = df_guardias.at[indexAnalista-1,'end'] + timedelta(days=5)
                new_guardia['end'] = df_guardias.at[indexAnalista-1,'end'] + timedelta(days=7)
                new_guardia['allDay'] = True
                new_guardia['group'] = 'guardias'
                new_guardia['semana'] = df_guardias.at[indexAnalista-1,'semana']
                new_guardia['tipo_semana'] = df_guardias.at[indexAnalista-1,'tipo_semana']

                df_new_guardia=pd.DataFrame([new_guardia])
                print("NUEVO REGISTRO", df_new_guardia)
                
                #Por ultimo modifico la fecha de fin del analista que le toco la semana anterior a la del festivo ya que hará el fin de semana de la siguiente semana
                #Para el analista de la semana anterior a la del festivo modifico la fecha de finalización al viernes
                df_guardias.loc[indexAnalista-1,'end'] =  df_guardias.loc[indexAnalista-1,'end'] + timedelta(days=-2)

                df_guardias = pd.concat([df_guardias, df_new_guardia]).sort_values(by=["semana"])
                df_guardias.reset_index(drop=True, inplace=True)
    
    return df_guardias

@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def updateCalendarioRotatorio(request):
    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    year= request.GET.get('y', '')
    turno = request.GET.get('t', '')
    area = request.GET.get('a','')
    jsonGuardias = request.GET.get('g', '')

    if jsonGuardias!="" and year!="" and turno!="" and area!="":
        df_guardias = pd.read_json(jsonGuardias)
        if len(df_guardias.index) > 0:
            try:
                #Obtengo el objeto del turno seleccionado
                turno = CalendarioTurnos.objects.using("guardias").get(id_turno=int(turno))
                
                #Obtengo las nuevas guardias del nuevo calendario creado para ser insertadas en la base de datos
                df_guardias['fecha_local_start'] = df_guardias.apply(lambda row : datetime.strptime(row['fecha_local_start'],'%Y-%m-%d'), axis = 1)
                df_guardias['fecha_local_end'] = df_guardias.apply(lambda row : datetime.strptime(row['fecha_local_end'],'%Y-%m-%d')+timedelta(days=-1), axis = 1)
                df_guardias['year'] = int(year)
                df_guardias['semana'] = df_guardias.apply(lambda row : isoweek.Week.withdate(row['fecha_local_start']).week, axis = 1)
                df_guardias['id_user_analista'] = df_guardias.apply(lambda row : row['id_user_analista'], axis = 1)
                df_guardias['id_turno'] = turno
                df_guardias['tipo_semana'] = 0 #PENDIENTE DE ACTUALIZARLO PARA PODER HACER ESTUDIO COMPARATIVO
                df_guardias['id_user_modificado'] = request.user.id
                df_guardias['tipo_guardia'] = 1
                df_guardias['supervisado'] = 1
                df_guardias['valido'] = 1

                #Nuevo! Para que se inserten en orden
                df_guardias = df_guardias.sort_values(by=['semana', 'fecha_local_start'])

                print(df_guardias)
                
                #Borro los registros que ya existían para este año
                guardias_historicas = CalendarioGuardiasGuardias.objects.using('guardias').filter(year=int(year), id_turno__id_area__id_area=int(area))
                df_guardias_historicas = pd.DataFrame(guardias_historicas.values())
                guardias_historicas.delete()
    
                try:
                    #Cargo de forma masiva a través de un json las nuevas guardias
                    CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                        CalendarioGuardiasGuardias(**vals) for vals in df_guardias.to_dict('records')
                    )      
     
                    mensaje["title"]=""
                    mensaje["text"]="Ha sido creado un nuevo Calendario de Guardias para el año "+year+" perteneciente al area de "+ turno.id_area.nombre +' pudiendo ser ya visualizado.'
                    mensaje["icon"]="success" 
                
                except:
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="Se ha producido un error al registrar en la base de datos las nuevas guardias para el año "+year+" perteneciente al area de "+ turno.id_area.nombre
                    mensaje["icon"]="error"
                    #Cargo de forma masiva a través de un json las guardias historicas por que se ha producido un error
                    CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                        CalendarioGuardiasGuardias(**vals) for vals in df_guardias_historicas.to_dict('records')
                    )  
 
            except Exception as e:
                print("ERROR updateCalendarioRotatorio", e)
                mensaje["title"]="Opps! ..."
                mensaje["text"]="Se ha producido un error al crear un nuevo Calendario de Guardias para el año "+year+" perteneciente al area de "+ turno.id_area.nombre
                mensaje["icon"]="error"
        
        else:
            mensaje["title"]="Opps! ..."
            mensaje["text"]="No se ha recibido ninguna guardia para crear un nuevo calendario de guardias."
            mensaje["icon"]="warning"
    
    return JsonResponse(mensaje, safe=False) 

@permission_required('auth.calendario_guardias_nuevo', login_url='/private/calendario/guardias/acceso/')
def updateCalendarioRarex(request):
    mensaje = {}
    mensaje["title"]="Error"
    mensaje["text"]=""
    mensaje["icon"]="error" 

    year= request.GET.get('y', '')
    turno = request.GET.get('t', '')
    area = request.GET.get('a','')
    jsonGuardias = request.GET.get('g', '')

    if jsonGuardias!="" and year!="" and turno!="" and area!="":
        df_guardias = pd.read_json(jsonGuardias)
        if len(df_guardias.index) > 0:

            try:
                #Obtengo el objeto del turno seleccionado
                turno = CalendarioTurnos.objects.using("guardias").get(id_turno=int(turno))

                #Obtengo las nuevas guardias del nuevo calendario creado para ser insertadas en la base de datos
                df_guardias['fecha_local_start'] = df_guardias.apply(lambda row : datetime.strptime(row['fecha_local_start'],'%Y-%m-%d'), axis = 1)
                df_guardias['fecha_local_end'] = df_guardias.apply(lambda row : datetime.strptime(row['fecha_local_end'],'%Y-%m-%d')+timedelta(days=-1), axis = 1)
                df_guardias['year'] = int(year)
                df_guardias['semana'] = df_guardias.apply(lambda row :  getNumSemanaGuardiaRarex(row["fecha_local_start"],row['fecha_local_end']), axis = 1)
                df_guardias['id_user_analista'] = df_guardias.apply(lambda row : row['id_user_analista'], axis = 1)
                df_guardias['id_turno'] = turno
                df_guardias['tipo_semana'] = df_guardias.apply(lambda row : getTipoSemana(int(year), row['semana']), axis = 1)
                df_guardias['id_user_modificado'] = request.user.id
                df_guardias['tipo_guardia'] = 1
                df_guardias['supervisado'] = 1
                df_guardias['valido'] = 1

                #Nuevo! Para que se inserten en orden
                df_guardias = df_guardias.sort_values(by=['semana', 'fecha_local_start'])

                #Borro los registros que ya existían para este año
                guardias_historicas = CalendarioGuardiasGuardias.objects.using('guardias').filter(year=int(year), id_turno__id_area__id_area=int(area))
                df_guardias_historicas = pd.DataFrame(guardias_historicas.values())
                guardias_historicas.delete()
    
                try:
                    #Cargo de forma masiva a través de un json las nuevas guardias
                    CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                        CalendarioGuardiasGuardias(**vals) for vals in df_guardias.to_dict('records')
                    )           
                    mensaje["title"]=""
                    mensaje["text"]="Ha sido creado un nuevo Calendario de Guardias para el año "+year+" perteneciente al area de "+ turno.id_area.nombre +' pudiendo ser ya visualizado.'
                    mensaje["icon"]="success" 
                
                except:
                    mensaje["title"]="Opps! ..."
                    mensaje["text"]="Se ha producido un error al registrar en la base de datos las nuevas guardias para el año "+year+" perteneciente al area de "+ turno.id_area.nombre
                    mensaje["icon"]="error"
                    #Cargo de forma masiva a través de un json las guardias historicas por que se ha producido un error
                    CalendarioGuardiasGuardias.objects.using('guardias').bulk_create(
                        CalendarioGuardiasGuardias(**vals) for vals in df_guardias_historicas.to_dict('records')
                    )                
            
            except Exception as e:
                print("ERROR updateCalendarioRarex: ", e)
                mensaje["title"]="Opps! ..."
                mensaje["text"]="Se ha producido un error al crear un nuevo Calendario de Guardias para el año "+year+" perteneciente al area de "+ turno.id_area.nombre
                mensaje["icon"]="error"
        
        else:
            mensaje["title"]="Opps! ..."
            mensaje["text"]="No se ha recibido ninguna guardia para crear un nuevo calendario de guardias."
            mensaje["icon"]="warning"
    
    return JsonResponse(mensaje, safe=False) 

'''Para los cambios de puentes mantengo la semana anterior a las guardias del analista que tiene que hacer el fin de semana anterior'''
def getNumSemanaGuardiaRarex(fecha_inicio,fecha_fin):
    if (fecha_fin-fecha_inicio).days==1:
        return int(isoweek.Week.withdate(fecha_fin).week) -1
    else:
        return int(isoweek.Week.withdate(fecha_fin).week)

'''Devuelve dado una semana y un año el tipo de semana (0: Normal 1:Festivo 2:Vacaciones)'''
def getTipoSemana(year, semana):
    
    #Obtengo el listado de semanas completo (num semana, fecha inicio, fecha fin)
    df_semanas = getListadoSemanas(int(year))

    #Obtengo el listado de semanas festivas (num semana) 
    df_festivos = getListadoAnualSemFestivas(int(year))
    
    #Obtengo un array con las semanas rojas (Semana Santa, Puente Diciembre, Navidad 1, Navidad 2)
    df_semanas_rojas = getSemanasRojas(int(year))
    df_semanas_rojas = df_semanas.loc[df_semanas['semana'].isin(df_semanas_rojas)]
    if semana in df_semanas_rojas['semana'].to_numpy():
        return int(2)

    #Obtengo un array con las semanas verdes
    df_semanas_verdes = df_semanas.loc[~df_semanas['semana'].isin(df_festivos['semana'].tolist())]
    df_semanas_verdes = df_semanas_verdes.loc[~df_semanas_verdes['semana'].isin(df_semanas_rojas['semana'].tolist())]
    if semana in df_semanas_verdes['semana'].to_numpy():
        return int(0)

    #Obtengo un array con las semanas naranjas
    df_semanas_naranjas = df_semanas.loc[df_semanas['semana'].isin(df_festivos['semana'].tolist())]
    df_semanas_naranjas = df_semanas_naranjas.loc[~df_semanas_naranjas['semana'].isin(df_semanas_rojas['semana'].tolist())]
    if semana in df_semanas_naranjas['semana'].to_numpy():
        return int(1)


'''DATOS: DATAFRAME (Listado de Semanas Festivas dado un año)'''
def getListadoAnualSemFestivas(year):
    festivos =  CalendarioFestivos.objects.using('guardias'
    ).filter(fecha_local__year=year).order_by('fecha_local'
    ).annotate(  
        month=ExtractMonth('fecha_local'),
        week=ExtractWeek('fecha_local'),
    ).values('month', 'week'
    ).annotate(semana=Case( When( Q(month=1) & Q(week__gt=10), then=Value('0')),
                When( Q(month=12) & Q(week=1), then=Value('0')),
                default=ExtractWeek('fecha_local'),
                output_field=IntegerField()),
    ).filter(semana__gt=0
    ).values('semana'
    ).order_by()

    if festivos.count()>0:
        df_semanas_festivas= pd.DataFrame (list(festivos)).sort_values('semana')
    else:
        df_semanas_festivas = pd.DataFrame()

    return df_semanas_festivas


'''DATOS: ARRAY (Vector con los numeros de las semanas rojas o de tipo 2 dado un año)'''
def getSemanasRojas(year):
    semana_santa = CalendarioFestivos.objects.using("guardias"
    ).filter(fecha_local__year=year, nombre ="Jueves Santo"
    ).annotate(week=ExtractWeek('fecha_local')).values('week')
    print("SEMANA SANTA", year)
    print(semana_santa)
    puente_diciembre = CalendarioFestivos.objects.using("guardias"
    ).filter(fecha_local__year=year, fecha_local__month=12, fecha_local__day=6
    ).annotate(week=ExtractWeek('fecha_local')).values('week')
    navidad = CalendarioFestivos.objects.using("guardias"
    ).filter(fecha_local__year=year, fecha_local__month=12, fecha_local__day=24
    ).annotate(week=ExtractWeek('fecha_local')).values('week')

    if semana_santa.count()>0 and puente_diciembre.count()>0 and navidad.count()>0:
        semanas_rojas = [semana_santa.first().get('week'), 
                        puente_diciembre.first().get('week'), 
                        navidad.first().get('week'), 
                        navidad.first().get('week')+1]
    else:
        semanas_rojas=[]
    print("GET SEMANAS ROJAS", semanas_rojas)
        
    return semanas_rojas


def NumeroRotacionPersonal(ultimoUsuario, df_personal, area):
    #Obtengo a todo el personal que ha sido adscrito al calendario de guardias en el area especificada (Este dado de alta (operativo = 1) o dado de baja (operativo = 0))
    personal_completo = CalendarioPersonal.objects.using("guardias").filter(id_area__id_area = area).values('id_usuario').order_by('id_usuario')
    df_personal_completo = pd.DataFrame(personal_completo)

    #Obtengo el numero de rotacion del personal
    if ultimoUsuario not in df_personal['id_usuario'].unique(): 
        aux_personal_completo = personal_completo
        index = df_personal_completo.index[df_personal_completo['id_usuario'] ==  ultimoUsuario].tolist()[0]
        while ultimoUsuario not in df_personal['id_usuario'].unique():
            aux_personal_completo = RotatePersonal(aux_personal_completo, -1)
            df_aux_personal_completo = pd.DataFrame(aux_personal_completo)
            ultimoUsuario = df_aux_personal_completo.at[index, 'id_usuario']
    
    index_lastUser=df_personal.index[df_personal['id_usuario'] ==  ultimoUsuario].tolist()[0]
    index_firstUser= index_lastUser+1 #numero de rotacion que debo realizar

    return index_firstUser


def RotatePersonal(personal, num_rotacion):
    orden_lista = collections.deque(personal)
    orden_lista.rotate(-num_rotacion)
    list_personal = list(orden_lista)
    return list_personal


def ListadoPersonal(personal, UltimoUsuario, area):
    try:
        num_rotacion_personal = NumeroRotacionPersonal(UltimoUsuario.get('id_user_analista'), pd.DataFrame(list(personal)), int(area))
        list_personal = RotatePersonal(personal, num_rotacion_personal)
    except:
        list_personal = personal
    return list_personal


'''DATOS: DATAFRAME (Listado de Semanas completas dado un año)'''
def getListadoSemanas(year):
    numsemanas= isoweek.Week.last_week_of_year(year).week 
    idsemana=0
    semanas=[]
    while idsemana < numsemanas:
        idsemana +=1
        semanas.append([idsemana,year, 0])
    df_semanas = pd.DataFrame(semanas, columns=["semana", "año", "tipo"])
    df_semanas['fecha_ini'] =df_semanas.apply(lambda row: isoweek.Week(year, int(row.semana)).monday(), axis=1)
    df_semanas['fecha_fin'] =df_semanas.apply(lambda row: isoweek.Week(year, int(row.semana)).sunday(), axis=1)
    return df_semanas


'''DATOS: DATAFRAME (Genera el reparto de semanas en funcion de los usuarios y devuelve el listado de guardias)'''
def RotacionGuardias(personal, semanas, tipo_semana):    
    i=0
    idx=0
    rotacion = []
    while i< len(semanas):
        for usuario in personal:     
            if i >= len(semanas):
                break
            rotacion.append([usuario['id_usuario'], #id_usuario
                             semanas.iloc[i]['fecha_ini'], #fecha_local_start
                             semanas.iloc[i]['fecha_fin']+timedelta(days=1), #fecha_local_end
                             True, #allDay (para poder ajustar la duracion de los eventos)
                             'guardias', #nombre del grupo
                             semanas.iloc[i]['semana'], #numero que identifica la semana
                             tipo_semana]) #tipo de semana
            i +=1
            idx +=1
        idx=0

    df_guardia = pd.DataFrame(rotacion, columns=['idUser', 'start', 'end', 'allDay', 'group', 'semana', 'tipo_semana'])
   
    return df_guardia

''' POST (Evento Submit del Formulario existente en el template Configuración 
del Perfil del Usuario para modificar los datos personales (nombre, apellidos, 
email, telefono, avatar)'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def updatePerfilUsuarioGuardias(request):
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

'''Datos: Listado de aplicaciones en funcionamiento'''
@permission_required('auth.calendario_guardias', login_url='/private/calendario/guardias/acceso/')
def getEstadoApps(request):
    user = request.user

    apps = MonitorizaApps.objects.using('guardias').order_by('nombre'
            ).annotate(proxima_ejecucion = F('proxima_ejecucion_utc'), 
                       ultima_ejecucion = F('ultima_ejecucion_utc')
            ).values('nombre','descripcion', 'nombre_proceso', 'proxima_ejecucion', 'ultima_ejecucion', 'segundos_ejecucion', 'num_periodos_alarma', 'ejecutar')
   
    if len(apps)>0:
        df_apps = pd.DataFrame(apps)
        df_apps['nombre_proceso'] = df_apps.apply(lambda row: row['nombre_proceso'].replace('__', ' '), axis =1) 
        df_apps['time_seconds'] = df_apps.apply(lambda row: (10*60) if int(row['segundos_ejecucion']) < (10*60) else int(row['segundos_ejecucion'])*int(row['num_periodos_alarma']), axis =1)
        df_apps['fecha_hora_utc'] = df_apps.apply(lambda row: datetime.now().astimezone(tz=pytz.utc) - timedelta(seconds=row['time_seconds']), axis =1)
        df_apps['estado'] = df_apps.apply(lambda row: 1 if row['ultima_ejecucion']!=None 
                                                    and row['ultima_ejecucion']<row['fecha_hora_utc'] 
                                                    and (row['proxima_ejecucion']-row['ultima_ejecucion']).total_seconds()==row['segundos_ejecucion'] 
                                                    and row['ejecutar']!=0
                                                    else 2 if row['ejecutar']==0
                                                    else 3, axis =1)

        df_apps['proxima_ejecucion'] = df_apps['proxima_ejecucion'].dt.tz_convert('UTC').dt.tz_convert('Europe/Madrid')
        df_apps['proxima_ejecucion'] = df_apps['proxima_ejecucion'].dt.strftime('%d %b, %Y %H:%M:%S h')
        df_apps['ultima_ejecucion'] = df_apps['ultima_ejecucion'].dt.tz_convert('UTC').dt.tz_convert('Europe/Madrid')
        df_apps['ultima_ejecucion'] = df_apps['ultima_ejecucion'].dt.strftime('%d %b, %Y %H:%M:%S h')

        df_apps.drop(['time_seconds', 'fecha_hora_utc', 'num_periodos_alarma', 'ejecutar'], axis=1, inplace=True)
        df_apps = df_apps.replace({np.nan: None})
        df_apps = df_apps.sort_values(by=['estado', 'nombre', 'nombre_proceso'])

     
    else:
        df_apps = pd.DataFrame(columns=['nombre', 'descripcion', 'nombre_proceso', 'ultima_ejecucion', 'proxima_ejecucion', 'estado'])


    return JsonResponse(df_apps.to_dict('records'), safe=False)

@permission_required('auth.calendario_guardias_supervisor', login_url='/private/calendario/guardias/acceso/')
def getHistorioContadorGuardias(request):

    df_guardias = pd.DataFrame(columns=['analista', 'area', 'icono', 'avatar', 'num_guardias'])
    df_sustituciones = pd.DataFrame(columns=['analista', 'area', 'icono', 'avatar', 'num_sustituciones'])

    # Obtengo las guardias semanales de todo el calendario
    guardias = CalendarioGuardiasGuardias.objects.using('guardias'
                ).annotate(area = F('id_turno__id_area__nombre'), icono = F('id_turno__id_area__icono'),
                ).filter(valido = 1, supervisado = 1, tipo_guardia__in = [1,3]
                ).values('semana', 'id_turno', 'area', 'icono', 'id_user_analista')
    
    if len(guardias)>0:

        df_guardias = pd.DataFrame(guardias)
        df_guardias["analista"] = df_guardias.apply(lambda row : User.objects.get(id=row['id_user_analista']).first_name, axis = 1)
        df_guardias["avatar"]=  df_guardias.apply(lambda row : getAvatar(User.objects.get(id=row['id_user_analista'])), axis = 1)

        #Elimino las semanas duplicadas de una misma guardia (ejemplo: cuando a un analista le toca el fin de semana por un festivo)
        df_guardias = df_guardias.drop_duplicates(['id_user_analista', 'semana', 'id_turno'], keep= 'last')

        #Elimino las columnas que no me interesan
        df_guardias = df_guardias.drop(columns=['semana', 'id_turno', 'id_user_analista'], axis=1)
        df_guardias['num_guardias'] = 1
        # Agrupo las guardias por analista-area-año y sumo la cantidad de guardias realizadas
        df_guardias = df_guardias.groupby(['analista', 'area'], as_index=False).agg({'area':'first', 'icono':'first', 'avatar': 'first', 'num_guardias':'sum'})
        df_guardias = df_guardias.sort_values(by=['area', 'analista'])
        df_guardias.reset_index(drop=True, inplace=True)

   
    # Obtengo las sustituciones aprovadas de todo el calendario
    sustituciones = CalendarioGuardiasGuardias.objects.using('guardias'
                ).annotate(area = F('id_turno__id_area__nombre'), icono = F('id_turno__id_area__icono'),
                ).filter(valido = 1, supervisado = 1, tipo_guardia = 2
                ).values( 'semana', 'id_turno', 'area', 'icono', 'id_user_analista')

    if len(sustituciones)>0:

        df_sustituciones = pd.DataFrame(sustituciones)
        df_sustituciones["analista"] = df_sustituciones.apply(lambda row : User.objects.get(id=row['id_user_analista']).first_name, axis = 1)
        df_sustituciones["avatar"]=  df_sustituciones.apply(lambda row : getAvatar(User.objects.get(id=row['id_user_analista'])), axis = 1)

        #Elimino las semanas duplicadas de una misma guardia (ejemplo: cuando a un analista le toca el fin de semana por un festivo)
        #df_sustituciones = df_sustituciones.drop_duplicates(['id_user_analista', 'semana', 'id_turno'], keep= 'last')

        #Elimino las columnas que no me interesan
        df_sustituciones = df_sustituciones.drop(columns=['semana', 'id_turno', 'id_user_analista'], axis=1)
        df_sustituciones['num_sustituciones'] = 1
        # Agrupo las guardias por analista-area-año y sumo la cantidad de guardias realizadas
        df_sustituciones = df_sustituciones.groupby(['analista', 'area'], as_index=False).agg({'area':'first', 'icono':'first', 'avatar': 'first', 'num_sustituciones':'sum'})
        df_sustituciones = df_sustituciones.sort_values(by=['area', 'analista'])
        df_sustituciones.reset_index(drop=True, inplace=True)
        

    df_final = pd.merge(df_guardias, df_sustituciones, on = ['analista', 'area', 'icono', 'avatar'], how='left')
    df_final = df_final.replace({np.nan: None})
    print(df_final)


    return JsonResponse(df_final.to_dict('records'), safe=False)


