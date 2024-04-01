import datetime
import os
import shutil
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from timetrackpro.models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import *
from datetime import date, datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
import unicodedata
from django.db.models import Q, F, Max, Min, Count, Sum, Avg
from timetrackpro.funciones.funcionesAuxiliaresTimetrackpro import *
from django.db.models.functions import TruncDate
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
import calendar
from django.db.models import Sum
from django.db.models.functions import ExtractWeek
import io
import pytz
from django.utils import timezone
from django.core.mail import send_mail

from calendario_guardias.models import MonitorizaApps
from rare.models import MensajesTelegram
from docLaruex.models import ReservasVehiculos, Equipo
from django.views.decorators.csrf import csrf_exempt


# ? Configuración de mensajes de 
iconosAviso ={
    "success":"fa-solid fa-circle-check",
    "danger":"fa-solid fa-triangle-exclamation",
    "warning":"fa-solid fa-triangle-exclamation",
    "info":"fa-solid fa-circle-exclamation"
}
alerta = {
    "activa": False,
    "icono": iconosAviso["success"],
    "tipo": "success",
    "mensaje": "Publicación editada correctamente."
    

}
estadosErrores = {
    "Pendiente":1,
    "Rechazado":2,
    "Aceptado":3
}

nombreMeses = {
    1:"Enero",
    2:"Febrero",
    3:"Marzo",
    4:"Abril",
    5:"Mayo",
    6:"Junio",
    7:"Julio",
    8:"Agosto",
    9:"Septiembre",
    10:"Octubre",
    11:"Noviembre",
    12:"Diciembre"
}


# ? información tarjeta acceso reverso
infoGeneralTarjeta ="Este carné es propiedad del LARUEX y deberá devuelto al departamento de administración una vez acabada la relación contractual con el mismo."
infoPersonalTarjeta = "El carné es personal e intransferible, por lo que cederlo a cualquier otra persona supondrá una grave violación de las normas del laboratorio."
infoContactoTarjeta = "Se ruega a quien encuentre este carné se ponga en contacto en el teléfono +34 927 251 389."


excluidos = ["Prueba", "Pruebas", "prueba", "pruebas", "PRUEBA", "PRUEBAS", "Usuario Pruebas",  "test", "TEST", "Test" , " ", "", "root", "CSN", "PCivil Provisional", "Protección Civil", "JEx", "Admin", "admin"]

# Defino la barra de navegación
navBar = NavBar.objects.using("timetrackpro").values()

def calcularVacacionesSolicitadas(idUsuario, year):
    '''
    La función se encarga de calcular los días de vacaciones solicitados por un usuario en un año concreto.
    :param idUsuario: Identificador del usuario del que se quieren calcular los días de vacaciones solicitados.
    :param year: Año en el que se quieren calcular los días de vacaciones solicitados.
    :return: Número de días de vacaciones solicitados por el usuario en el año concreto.
    '''
    vacacionesSolicitadas = 0
    vacacionesHabilesSolicitadas = 0
    estadoSolicitado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]

    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoSolicitado, tipo_vacaciones__in=[3,4]).values('dias_consumidos', 'dias_habiles_consumidos').exists():
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoSolicitado, tipo_vacaciones__in=[3,4]).values('dias_consumidos', 'dias_habiles_consumidos')
        for v in vacaciones:
            vacacionesSolicitadas = vacacionesSolicitadas + v['dias_consumidos']
            vacacionesHabilesSolicitadas = vacacionesHabilesSolicitadas + v['dias_habiles_consumidos']
    return vacacionesSolicitadas, vacacionesHabilesSolicitadas



def convertirDate(fecha):
    '''
    La función se encarga de convertir una fecha de tipo string a tipo datetime.
    :param fecha: Fecha en formato string que se quiere convertir a tipo datetime.
    :return: Fecha en formato datetime.
    '''
    return datetime.strptime(fecha, '%Y-%m-%d')


def convertirDateATimeDelta(fecha):
    '''
    La función se encarga de convertir una fecha de tipo datetime a tipo timedelta.
    :param fecha: Fecha en formato datetime que se quiere convertir a tipo timedelta.
    :return: Fecha en formato timedelta.
    '''
    return timedelta(days=fecha.day, hours=fecha.hour, minutes=fecha.minute, seconds=fecha.second)



def calcularDiasHabiles(fechaInicio, fechaFin):
    # devuelve el nuemero de días habiles entre dos fechas, tambien tiene en cuenta si en el medio hay festivos
    '''
    La función se encarga de calcular el número de días hábiles entre dos fechas, teniendo en cuenta si en el medio hay festivos.
    :param fechaInicio: Fecha de inicio del periodo en el que se quieren calcular los días hábiles.
    :param fechaFin: Fecha de fin del periodo en el que se quieren calcular los días hábiles.
    :return: Número de días hábiles entre las dos fechas.
    '''
    diasHabiles = 0
    festivos = []

    if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__range=[fechaInicio, fechaFin]).exists():
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__range=[fechaInicio, fechaFin]).values('fecha_inicio')

    fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d')
    fechaFin = datetime.strptime(fechaFin, '%Y-%m-%d')

    # recorro el periodo seleccionado 
    for i in range((fechaFin-fechaInicio).days + 1):
        dia = fechaInicio + timedelta(days=i)
        if festivos:
            if dia.weekday() < 5 and not FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio=dia).exists():
                diasHabiles = diasHabiles + 1
        else:
            if dia.weekday() < 5:
                diasHabiles = diasHabiles + 1
    return diasHabiles


def gastadasVacacionesSemanaSanta(idUsuario, year):
    '''
        0 - Disponibles
        1 - Solicitadas
        2 - No disponibles
    '''
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    estadoSolicitado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
    disfrutadas = 0
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado, tipo_vacaciones=2).exists():
        disfrutadas = 2
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoSolicitado, tipo_vacaciones=2).exists():
        disfrutadas = 1
    return disfrutadas


def gastadasVacacionesNavidad(idUsuario, year):
    '''
        0 - Disponibles
        1 - Solicitadas
        2 - No disponibles
    '''
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    estadoSolicitado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
    disfrutadas = 0
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado, tipo_vacaciones=1).exists():
        disfrutadas = 2
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoSolicitado, tipo_vacaciones=1).exists():
        disfrutadas = 1
    return disfrutadas


def calcularVacacionesConsumidas(idUsuario, year):
    '''
    La función se encarga de calcular los días hábiles de vacaciones consumidos por un usuario en un año concreto.
    :param idUsuario: Identificador del usuario del que se quieren calcular los días de vacaciones solicitados.
    :param year: Año en el que se quieren calcular los días de vacaciones solicitados.
    :return: Número de días de vacaciones consumidos por el usuario en el año concreto.
    '''
    vacacionesConsumidas = 0
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]

    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado, tipo_vacaciones__in=[3,4]).exists():
        # obtiene las vacaciones aceptadas del usuario y calcula todos los dias consumidos llamando a la funcion calcularDiasHabiles
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado, tipo_vacaciones__in=[3,4]).values('fecha_inicio', 'fecha_fin', 'dias_consumidos', 'dias_habiles_consumidos')
        for v in vacaciones:
            vacacionesConsumidas = vacacionesConsumidas + v['dias_habiles_consumidos']
    return vacacionesConsumidas

def calcularVacacionesNaturalesConsumidas(idUsuario, year):
    '''
    La función se encarga de calcular los días de vacaciones consumidos por un usuario en un año concreto.
    :param idUsuario: Identificador del usuario del que se quieren calcular los días de vacaciones solicitados.
    :param year: Año en el que se quieren calcular los días de vacaciones solicitados.
    :return: Número de días de vacaciones consumidos por el usuario en el año concreto.
    '''
    vacacionesConsumidas = 0
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado).exists():
        # obtiene las vacaciones aceptadas del usuario y calcula todos los dias consumidos llamando a la funcion calcularDiasHabiles
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado).values('fecha_inicio', 'fecha_fin', 'dias_consumidos', 'dias_habiles_consumidos')
        for v in vacaciones:
            vacacionesConsumidas = vacacionesConsumidas + v['dias_consumidos']
    return vacacionesConsumidas

def calcularAsuntosPropiosSolicitados(idUsuario, year):
    '''
    Función que se encarga de calcular los días de asuntos propios solicitados por un usuario en un año concreto.
    :param idUsuario: Identificador del usuario del que se quieren calcular los días de asuntos propios solicitados.
    :param year: Año en el que se quieren calcular los días de asuntos propios solicitados.
    :return: Número de días de asuntos propios solicitados por el usuario en el año concreto.
    '''
    asuntosSolicitados = 0
    estadoSolicitado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
    AsuntosPropiosSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoSolicitado).values('dias_consumidos')
    
    if AsuntosPropiosSolicitados.exists():
        for a in AsuntosPropiosSolicitados:
            asuntosSolicitados = asuntosSolicitados + a['dias_consumidos']
    return asuntosSolicitados

def calcularAsuntosPropiosConsumidos(idUsuario, year):
    # calcular dias de de asuntos propios consumidos
    '''
    Función que se encarga de calcular los días de asuntos propios consumidos por un usuario en un año concreto.
    :param idUsuario: Identificador del usuario del que se quieren calcular los días de asuntos propios consumidos.
    :param year: Año en el que se quieren calcular los días de asuntos propios consumidos.
    :return: Número de días de asuntos propios consumidos por el usuario en el año concreto.
    '''
    
    asuntosConsumidos = 0
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    AsuntosPropiosAceptados = AsuntosPropios.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado, recuperable=0 ).values('dias_consumidos')
    
    if AsuntosPropiosAceptados.exists():
        for asunto in AsuntosPropiosAceptados:
            asuntosConsumidos = asuntosConsumidos + asunto['dias_consumidos']
    
    return asuntosConsumidos

def calcularAsuntosPropiosRecuperablesConsumidos(idUsuario, year):
    # calcular dias de de asuntos propios consumidos
    '''
    Función que se encarga de calcular los días de asuntos propios consumidos por un usuario en un año concreto.
    :param idUsuario: Identificador del usuario del que se quieren calcular los días de asuntos propios consumidos.
    :param year: Año en el que se quieren calcular los días de asuntos propios consumidos.
    :return: Número de días de asuntos propios consumidos por el usuario en el año concreto.
    '''
    
    asuntosRecuperablesConsumidos = 0
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    AsuntosPropiosAceptados = AsuntosPropios.objects.using("timetrackpro").filter(empleado=idUsuario, year=year, estado = estadoAceptado, recuperable=1 ).values('dias_consumidos')
    
    if AsuntosPropiosAceptados.exists():
        for asunto in AsuntosPropiosAceptados:
            asuntosRecuperablesConsumidos = asuntosRecuperablesConsumidos + asunto['dias_consumidos']
    
    return asuntosRecuperablesConsumidos

@login_required
def home(request):

    # si el usario esta logueado y autenticado
    if request.user.is_authenticated:
        """
        The function `home` renders a specific HTML template based on the user's role and provides
        information about remaining and requested vacation days.
        
        :param request: The `request` parameter is an object that represents the HTTP request made by the
        client. It contains information such as the user making the request, the method used (GET, POST,
        etc.), and any data sent with the request
        :return: a rendered HTML template based on the user's role. If the user is an administrator, it
        returns the "home-admin.html" template. If the user is a director, it returns the "home.html"
        template. Otherwise, it also returns the "home.html" template.
        """
        administrador = esAdministrador(request.user.id)
        director = esDirector(request.user.id)
        # calcular cuantos dias de asuntos propios ha consumido durante el año en curso
        # calcular cuantos dias de vacaciones ha consumido durante el año en curso
        user = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.user.id)[0]
        empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=user)[0]
        diasPropiosConsumidos = calcularAsuntosPropiosConsumidos(empleado.id_usuario, datetime.now().year)
        diasPropiosRecuperablesConsumidos = calcularAsuntosPropiosRecuperablesConsumidos(empleado.id_usuario, datetime.now().year)
        diasPropiosSolicitados = calcularAsuntosPropiosSolicitados(empleado.id_usuario, datetime.now().year)
        diasPropiosRestantes= settings.DIAS_ASUNTOS_PROPIOS-diasPropiosConsumidos
        diasVacacionesConsumidos = calcularVacacionesConsumidas(empleado.id_usuario, datetime.now().year)
        diasVacacionesNaturalesConsumidos = calcularVacacionesNaturalesConsumidas(empleado.id_usuario, datetime.now().year)
        diasVacacionesNaturalesRestantes = 30-diasVacacionesNaturalesConsumidos
        diasVacacionesRestantes = 22-diasVacacionesConsumidos
        diasVacacionesSolicitados, diasHabilesVacacionesSolicitados  = calcularVacacionesSolicitadas(empleado.id_usuario, datetime.now().year)
        navidad = gastadasVacacionesNavidad(empleado.id_usuario, datetime.now().year)
        semanaSanta = gastadasVacacionesSemanaSanta(empleado.id_usuario, datetime.now().year)
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "director":director,
            "rutaActual": "Home",
            "diasPropiosRestantes":diasPropiosRestantes,
            "diasVacacionesNaturalesRestantes":diasVacacionesNaturalesRestantes,
            "diasVacacionesRestantes":diasVacacionesRestantes,
            "diasPropiosSolicitados":diasPropiosSolicitados,
            "diasVacacionesSolicitados":diasVacacionesSolicitados,
            "diasHabilesVacacionesSolicitados":diasHabilesVacacionesSolicitados,
            "diasPropiosRecuperablesConsumidos":diasPropiosRecuperablesConsumidos,
            "alerta":alerta,
            "navidad":navidad,
            "semanaSanta":semanaSanta
        }
        return render(request,"home.html",infoVista)
        # guardo los datos en un diccionario
    else:
        return redirect('timetrackpro:sin-permiso')


def noEncontrado(request):
    """
    The function "noEncontrado" renders a 404.html template with some additional information.
    
    :param request: The request object represents the HTTP request that the user made. It contains
    information about the user's request, such as the URL, headers, and any data sent with the request
    :return: a rendered HTML template called "404.html" with the dictionary "infoVista" as the context
    data.
    """
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
    }

    return render(request,"404.html",infoVista)


def sinPermiso(request):
    """
    Vista que se encarga de mostrar la página de "Sin permiso" cuando un usuario intenta acceder a una funcionalidad que no tiene permitida.
    :param request: HttpRequest que representa la solicitud HTTP que se está procesando.
    :return: HttpResponse que representa la respuesta HTTP resultante.
    """
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "TimeTrackProTittle":"TimeTrackPro - Sin permiso",
        "rutaActual": "Sin permiso"
    }

    return render(request,"sinPermiso.html",infoVista)


def ups(request, mensaje=None):
    """
    Vista que se encarga de mostrar la página de "Ups" cuando un usuario intenta insertar solicitudes con fechas que ya existen en la base de datos.
    :param request: HttpRequest que representa la solicitud HTTP que se está procesando.
    :return: HttpResponse que representa la respuesta HTTP resultante.
    """
    msg = "Ups, Parece que ya existe un registro con esas fechas en la base de datos."
    if mensaje is not None:
        msg = mensaje
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "TimeTrackProTittle":"TimeTrackPro - Ups permiso",
        "mensaje":msg,
        "rutaActual": "Ups"
    }

    return render(request,"ups.html",infoVista)

def correcto(request, mensaje=None):
    """
    Vista que se encarga de mostrar la página de "Correcto" cuando un usuario intenta insertar solicitudes con fechas que ya existen en la base de datos.
    :param request: HttpRequest que representa la solicitud HTTP que se está procesando.
    :return: HttpResponse que representa la respuesta HTTP resultante.
    """
    msg = "Acción realizada correctamente."
    if mensaje is not None:
        msg = mensaje
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "TimeTrackProTittle":"TimeTrackPro - Correcto",
        "mensaje":msg,
        "rutaActual": "Ok"
    }
    return render(request,"correcto.html",infoVista)

def habilitaciones(request):     
    """
    The function "habilitaciones" renders a template with data for displaying a list of enabled features
    and employees with enabled features, and also checks if the user is an administrator.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the requested URL, and any data
    sent with the request
    :return: The code is returning a response based on the user's permissions. If the user is an
    administrator, it will render the "HabilitacionesTimeTrackPro.html" template with the provided context data. If
    the user is not an administrator, it will redirect to the "sin-permiso" URL.
    """
    alerta = request.session.pop('alerta', None)
    # guardo los datos en un diccionario
    administrador = esAdministrador(request.user.id)

    habilitaciones = HabilitacionesTimeTrackPro.objects.using("timetrackpro").values('id', 'nombre')
    empleadosHabilitados = RelHabilitacionesUsuarioTimeTrackPro.objects.using("timetrackpro").values('id', 'id_auth_user', 'id_habilitacion', 'id_habilitacion__nombre', 'id_auth_user__first_name', 'id_auth_user__last_name')

    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "habilitaciones":list(habilitaciones),
        "empleadosHabilitados":list(empleadosHabilitados),
        "alerta":alerta,
        "rutaActual": "Habilitaciones"
    }
    if administrador:
        return render(request,"habilitaciones.html",infoVista)
    
    else:
        return redirect('timetrackpro:sin-permiso')
    
def agregarHabilitacion(request):
    """
    The function "agregarHabilitacion" adds a new "Habilitacion" object to the database if the user is
    an administrator and the "nombreHabilitacion" does not already exist.
    
    :param request: The "request" parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the method used (GET or POST),
    and any data sent with the request
    :return: a redirect to either the 'timetrackpro:habilitaciones' URL or the
    'timetrackpro:sin-permiso' URL.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            nombre = request.POST.get("nombreHabilitacion")
            if nombre in HabilitacionesTimeTrackPro.objects.using("timetrackpro").values_list('nombre', flat=True):
                alerta["activa"] = True
                alerta["icono"] = iconosAviso["danger"]
                alerta["tipo"] = "danger"
                alerta["mensaje"] = "La habilitación ya existe."
            else:
                nuevaHabilitacion = HabilitacionesTimeTrackPro(nombre=nombre)
                alerta["activa"] = True
                alerta["icono"] = iconosAviso["success"]
                alerta["tipo"] = "success"
                alerta["mensaje"] = "Habilitación agregada correctamente."
                nuevaHabilitacion.save(using='timetrackpro')

        request.session['alerta'] = alerta
        return redirect('timetrackpro:habilitaciones')
    else:
        return redirect('timetrackpro:sin-permiso')
    
@login_required
def asociarHabilitacion(request):
    
    """
    This function associates employees with a specific authorization in a time tracking system.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data submitted with the request
    :return: The code is returning a redirect to either the 'timetrackpro:habilitaciones' URL or the
    'timetrackpro:sin-permiso' URL.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            listEmpleados = []
            empleadosSeleccionados = request.POST.get("idEmpleadoSeleccionado")
            empleadosSeleccionados = empleadosSeleccionados.split("#")
            for e in empleadosSeleccionados:
                if e != "":
                    listEmpleados.append(e)   
            idHabilitacion = request.POST.get("habilitacionSeleccionada")

            habilitacion = HabilitacionesTimeTrackPro.objects.using("timetrackpro").filter(id=idHabilitacion)[0]
            for empleado in listEmpleados:
                empleado_obj = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=empleado)[0]  # Obtener el objeto 
                if empleado_obj and not RelHabilitacionesUsuarioTimeTrackPro.objects.using("timetrackpro").filter(id_habilitacion=habilitacion, id_auth_user=empleado_obj).exists():
                    nuevaRelacion = RelHabilitacionesUsuarioTimeTrackPro(id_auth_user=empleado_obj, id_habilitacion=habilitacion)
                    nuevaRelacion.save(using='timetrackpro')
                    alerta["activa"] = True
                    alerta["icono"] = iconosAviso["success"]
                    alerta["tipo"] = "success"
                    alerta["mensaje"] = "Usuarios asociados correctamente."
                    request.session['alerta'] = alerta
        return redirect('timetrackpro:habilitaciones')
    else:
        return redirect('timetrackpro:sin-permiso')

@login_required
def modificarHabilitacion(request):
    """
    The function `modificarHabilitacion` modifies the name of a habilitacion object if the user is an
    administrator.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the method used (GET or POST),
    and any data sent with the request
    :return: a redirect to either 'timetrackpro:habilitaciones' or 'timetrackpro:sin-permiso' depending
    on the conditions.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            idHabilitacion = request.POST.get("idHabilitacion")
            habilitacion = HabilitacionesTimeTrackPro.objects.using("timetrackpro").filter(id=idHabilitacion)[0]
            nombreHabilitacion = request.POST.get("nombreHabilitacion")
            habilitacion.nombre = nombreHabilitacion
            habilitacion.save(using='timetrackpro')
        return redirect('timetrackpro:habilitaciones')
    else:
        return redirect('timetrackpro:sin-permiso')


@login_required
def eliminarHabilitacion(request):
    """
    This function deletes a "Habilitacion" object if the user is an administrator.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    user. It contains information such as the user's session, the HTTP method used (GET, POST, etc.),
    and any data sent with the request
    :return: a redirect to either the 'timetrackpro:habilitaciones' URL or the
    'timetrackpro:sin-permiso' URL.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            idHabilitacion = request.POST.get("idHabilitacion")
            habilitacion = HabilitacionesTimeTrackPro.objects.using("timetrackpro").filter(id=idHabilitacion)[0]
            habilitacion.delete(using='timetrackpro')
        return redirect('timetrackpro:habilitaciones')
    else:
        return redirect('timetrackpro:sin-permiso')

@login_required
def tarjetasAcceso(request):
    """
    The function "tarjetasAcceso" checks if the user is an administrator or director, retrieves inactive
    access cards from the database, paginates the results, and returns the necessary data for the view.
    
    :param request: The request object represents the HTTP request that the user made. It contains
    information about the user, the requested URL, and any data that was sent with the request
    :return: a rendered HTML template called "tarjetasAcceso.html" along with a dictionary of data
    called "infoVista".
    """
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los datos necesarios para la vista
    if admin or director:
        tarjetasInactivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=0).order_by("nombre").values()
        # paginación tarjetas inactivas
        paginatorInactivas = Paginator(tarjetasInactivas, 5)  # Divide en páginas de 10 elementos
        numeroPaginaInactivas = request.GET.get('page')
        tarjetasAccesoInactivas = paginatorInactivas.get_page(numeroPaginaInactivas)

        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "admin":admin,
            "director":director,
            "tarjetasAccesoInactivas":tarjetasAccesoInactivas, 
            "infoGeneralTarjeta":infoGeneralTarjeta,
            "infoPersonalTarjeta":infoPersonalTarjeta,
            "infoContactoTarjeta":infoContactoTarjeta,
            "rutaActual": "Tarjetas de acceso"
        }

        return render(request,"tarjetasAcceso.html", infoVista)
    else:
        return redirect('timetrackpro:sin-permiso')

@login_required
def datosTarjetasAccesoActivas(request):
    """
    The function "datosTarjetasAccesoActivas" retrieves active access cards from the database and
    returns them as a JSON response.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a JSON response containing a list of active access cards.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    tarjetasActivas = []
    if administrador or director:
        tarjetasActivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).order_by("nombre").values()
    return JsonResponse(list(tarjetasActivas), safe=False)

@login_required   
def datosTarjetasAccesoInactivas(request):
    """
    The function "datosTarjetasAccesoInactivas" retrieves inactive access cards from the database and
    returns them as a JSON response.
    
    :param request: The "request" parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the requested URL, and any data
    sent with the request
    :return: a JSON response containing a list of inactive access cards.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    tarjetasInactivas = []
    if administrador or director:
        tarjetasInactivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=0).order_by("nombre").values()
    return JsonResponse(list(tarjetasInactivas), safe=False)

'''-------------------------------------------
                                Módulo: datosDjangoUsers

- Descripción: 
Obtener los datos de cada uno de los empleados de Laruex, tanto los registrados en la maquina de control de asistencia como los que no.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def datosDjangoUsers(request):
    """
    The function "datosDjangoUsers" retrieves a list of employees from a database and returns it as a
    JSON response if the user is an administrator, otherwise it redirects to a permission denied page.
    
    :param request: The request object represents the HTTP request made by the client. It contains
    information such as the user making the request, the HTTP method used, and any data sent with the
    request
    :return: The function `datosDjangoUsers` returns a JSON response containing a list of employee data
    if the user is an administrator. If the user is not an administrator, it redirects to the
    'sin-permiso' URL.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        empleados = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

        return JsonResponse(list(empleados), safe=False)
    else:
        return redirect('timetrackpro:sin-permiso')

@login_required
def agregarTarjetaAcceso(request):
    """
    The function "agregarTarjetaAcceso" adds a new access card to the system, including the card details
    and an optional image.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request and any data sent with the request
    :return: a redirect to the 'timetrackpro:tarjetas-de-acceso' URL.
    """
    administrador = esAdministrador(request.user.id)
    # obtengo los datos necesarios para la vista    
    if request.method == 'POST' and administrador:
        nombre = request.POST.get("nombre")
        apellidos = request.POST.get("apellidos")
        dni = request.POST.get("dni") 
        imagen = request.POST.get("imagenTarjeta") 
        acceso_laboratorios = request.POST.get("accesoLaboratorios") 
        acceso_cpd = request.POST.get("accesoCPD") 
        acceso_alerta2 = request.POST.get("accesoAlerta2")
        id_tarjeta = request.POST.get("idTarjeta")
        fechaActual = request.POST.get("fechaActual")  # fecha actual
        
        fecha_expiracion = None
        if "fechaExpiracion" in request.POST and request.POST.get("fechaExpiracion") != "":
            fecha_expiracion = request.POST.get("fechaExpiracion")
            nuevaTarjeta= TarjetasAcceso(nombre=nombre, apellidos=apellidos, dni=dni, imagen=imagen,acceso_laboratorios=acceso_laboratorios, acceso_cpd=acceso_cpd, acceso_alerta2=acceso_alerta2, id_tarjeta=id_tarjeta,fecha_alta=fechaActual, fecha_expiracion=fecha_expiracion, activo=1)
        else:
            nuevaTarjeta = TarjetasAcceso(nombre=nombre, apellidos=apellidos, dni=dni, imagen=imagen,acceso_laboratorios=acceso_laboratorios, acceso_cpd=acceso_cpd, acceso_alerta2=acceso_alerta2, id_tarjeta=id_tarjeta,fecha_alta=fechaActual, activo=1)
        nuevaTarjeta.save(using='timetrackpro')

    try: 
        if request.FILES['imagenTarjeta']:
            nombreImagen = str(nuevaTarjeta.id) + '_tarjeta.' + request.FILES['imagenTarjeta'].name.split('.')[-1]
            rutaTarjetas = 'img/timetrackpro/tarjetas/'
            ruta = settings.STATIC_ROOT + rutaTarjetas + nombreImagen
            subirDocumento(request.FILES['imagenTarjeta'], ruta)
            nuevaTarjeta.imagen = nombreImagen
            nuevaTarjeta.save(using='timetrackpro')
    except:
        #cambiar
        print("Error al subir la foto del equipo")

    return redirect('timetrackpro:tarjetas-de-acceso') 

@login_required
def verTarjetaAcceso(request, id):
    """
    The function "verTarjetaAcceso" checks if the user is an administrator or director, and if so, it
    retrieves the necessary data for the view and renders the "tarjeta.html" template with the data. If
    the user is not an administrator or director, it redirects to the "sin-permiso" page.
    
    :param request: The request object represents the HTTP request that the user made to access the
    view. It contains information such as the user's session, the HTTP method used (GET, POST, etc.),
    and any data submitted with the request
    :param id: The "id" parameter is the unique identifier of a specific TarjetaAcceso (Access Card)
    object. It is used to retrieve the details of that particular access card from the database
    :return: either a rendered HTML template with the necessary data for the view, or it is redirecting
    to another page if the user does not have the necessary permissions.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    # obtengo los datos necesarios para la vista
    tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=id).values()[0]
    if  administrador or director:
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "admin":esAdministrador(request.user.id),
            "tarjeta":tarjeta,
            "infoGeneralTarjeta":infoGeneralTarjeta,
            "infoPersonalTarjeta":infoPersonalTarjeta,
            "infoContactoTarjeta":infoContactoTarjeta,
            "alerta":alerta
        }
        return render(request,"tarjeta.html", infoVista)
    else:
        return redirect('timetrackpro:sin-permiso')
 
@login_required
def editarTarjetaAcceso(request):
    """
    The function `editarTarjetaAcceso` is used to edit a card access record in a database, with various
    fields being updated based on the user's input.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data sent with the request
    :return: a redirect to different views depending on the conditions. If the request method is POST
    and the user is an administrator, it redirects to the 'ver-tarjeta-acceso' view with the edited
    tarjeta's ID as a parameter. If the user is not an administrator, it redirects to the 'ups' view
    with a message indicating that the user does not have permission to edit
    """
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST':
        if administrador:
            id = request.POST.get("idTarjeta")
            # obtengo los datos necesarios para la vista
            tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=id)[0]

            nombre = str(request.POST.get("nombre"))
            nombre = nombre.replace("  ", "")
            nombre = nombre.replace("-", "")
            nombre = nombre.upper()
            tarjeta.nombre = nombre

            apellidos = str(request.POST.get("apellidos"))
            apellidos = apellidos.replace("  ", "")
            apellidos = apellidos.replace("-", "")
            apellidos = apellidos.upper()
            tarjeta.apellidos = apellidos

            dni = str(request.POST.get("dni"))
            dni = dni.replace(" ", "")
            dni = dni.replace("-", "")
            dni = dni.upper()
            tarjeta.dni = dni

            idTarjeta = str(request.POST.get("numeroTarjeta"))
            idTarjeta.replace(" ", "").replace("-", "")
            tarjeta.id_tarjeta = idTarjeta

            
            fechaAlta = request.POST.get("fechaAlta")
            tarjeta.fecha_alta = fechaAlta

            fechaExpiracion = None
            if "fechaExpiracion" in request.POST and request.POST.get("fechaExpiracion") != "":
                fecha_expiracion = request.POST.get("fechaExpiracion")
                tarjeta.fecha_baja = fecha_expiracion

            tarjetaActiva = request.POST.get('tarjeta_activa')
            if tarjetaActiva == "on":
                tarjeta.activo = 1
            else:
                tarjeta.activo = 0

            accesoAlerta2 = request.POST.get('acceso_alerta2')
            if accesoAlerta2 == "on":
                tarjeta.acceso_alerta2 = 1
            else:
                tarjeta.acceso_alerta2 = 0

            accesoLaboratorios = request.POST.get('acceso_laboratorio')
            if accesoLaboratorios == "on":
                tarjeta.acceso_laboratorios = 1
            else:
                tarjeta.acceso_laboratorios = 0

            accesoCPD = request.POST.get('acceso_cpd')
            if accesoCPD == "on":
                tarjeta.acceso_cpd = 1
            else:
                tarjeta.acceso_cpd = 0
            
            alerta["activa"] = True
            alerta["tipo"] = "success"
            alerta["mensaje"] = "Tarjeta editada correctamente."
            alerta["icono"] = iconosAviso["success"]

            try: 
                if request.FILES['imagenTarjeta'] and request.FILES['imagenTarjeta'] is not None:
                    if tarjeta.imagen is not None:
                        rutaActual = settings.STATIC_ROOT + settings.RUTA_TARJETAS_TIMETRACKPRO + tarjeta.imagen
                        if os.path.isfile(rutaActual):
                            os.remove(rutaActual)         

                    nombreImagen = str(tarjeta.id) + '_tarjeta.' + request.FILES['imagenTarjeta'].name.split('.')[-1]
                    ruta = settings.STATIC_ROOT + settings.RUTA_TARJETAS_TIMETRACKPRO + nombreImagen
                    subirDocumento(request.FILES['imagenTarjeta'], ruta)
                    tarjeta.imagen = nombreImagen
                else:
                    alerta["tipo"] = "danger"   
                    alerta["mensaje"] = "Error al subir la foto"
                    alerta["icono"] = iconosAviso["danger"]
            except:
                #cambiar
                print("Error al subir la foto")
        

            tarjeta.save(using='timetrackpro')
            return redirect('timetrackpro:ver-tarjeta-acceso', id=id)
        else:
            return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar la tarjeta.")
    else:
        return redirect('timetrackpro:tarjetas-de-acceso')




def infoConfigTarjetasAcceso(request):
    """
    The function "infoConfigTarjetasAcceso" renders a template with information for configuring access
    cards, including the navigation bar, user role, and current route.
    
    :param request: The request object represents the HTTP request that the server receives from the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a rendered HTML template called "infoConfigTarjetasAcceso.html" with the data stored in the
    "infoVista" dictionary.
    """
    administrador = esAdministrador(request.user.id)

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "rutaActual": "Configuración para Impresión de Tarjetas de Acceso",

    }
    return render(request,"infoConfigTarjetasAcceso.html",infoVista)

@login_required
def registrosInsertados(request):
    """
    The function "registrosInsertados" retrieves and displays inserted records for administrators and
    directors.
    
    :param request: The request object represents the HTTP request that the server receives from the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a rendered HTML template with the data needed for the view. The data includes the
    navigation bar, a boolean value indicating if the user is an administrator, a list of inserted
    records, and the current route.
    """
        # guardo los datos en un diccionario
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los datos necesarios para la vista
    archivos = []
    archivos = RegistrosJornadaInsertados.objects.using("timetrackpro").order_by('year', 'mes').all()
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "archivos":list(archivos), 
        "rutaActual": "Registros insertados",
        "yearActual":datetime.now().year
    }
    return render(request,"registros-insertados.html",infoVista)

@login_required
def registrosRemotosInsertados(request):
    """
    The function "registrosInsertados" retrieves and displays inserted records for administrators and
    directors.    
    :param request: The request object represents the HTTP request that the server receives from the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a rendered HTML template with the data needed for the view. The data includes the
    navigation bar, a boolean value indicating if the user is an administrator, a list of inserted
    records, and the current route.
    """
    # guardo los datos en un diccionario
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    yearActual = datetime.now().year
    # obtengo los datos necesarios para la vista
    archivos = []
    archivos = RegistrosJornadaInsertados.objects.using("timetrackpro").order_by('year', 'mes').all()
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "archivos":list(archivos), 
        "yearActual":yearActual,
        "rutaActual": "Registros insertados desde la aplicación"
    }
    return render(request,"registros-remotos-insertados.html",infoVista)



@login_required
def datosRegistrosInsertados(request, seccion=None, year=None, mes=None):
    """
    The function "datosRegistrosInsertados" retrieves inserted records from a database and returns them
    as a JSON response.
    
    :param request: The "request" parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the requested URL, and any data
    sent with the request
    :return: a JSON response containing a list of dictionaries. Each dictionary represents a record of
    inserted journal entries and includes the following fields: 'id', 'seccion', 'mes', 'year',
    'fecha_lectura', 'insertador__first_name', 'insertador__last_name', and 'ruta'.
    """

    secciones = {
        1: "Todos",
        2: "Alerta2",
        3: "Departamento",
        4: "Laboratorios",
    }
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registros = []
    if seccion == 1 or seccion == None or seccion == "1" or seccion == "Todos":
        if mes == None:
            registros = RegistrosJornadaInsertados.objects.using("timetrackpro").values('id', 'seccion', 'mes', 'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', 'ruta')
        else:
            registros = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(year=year, mes=nombreMeses[int(mes)]).values('id', 'seccion', 'mes', 'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', 'ruta')
    else:
        if mes == None:
            registros = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(seccion=secciones[int(seccion)]).values('id', 'seccion', 'mes', 'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', 'ruta')
        else:
            registros = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(seccion=secciones[int(seccion)], year=year, mes=nombreMeses[int(mes)]).values('id', 'seccion', 'mes', 'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', 'ruta')
    return JsonResponse(list(registros), safe=False)


@login_required
def datosRegistrosRemotosInsertados(request, remoto=None, year=None, mes=None):
    """
    La función "datosRegistrosRemotosInsertados" recupera los registros insertados desde la aplicación
    y los devuelve como una respuesta JSON.
    :param request: El objeto "request" representa la solicitud HTTP que el usuario hizo para acceder a
    la vista. Contiene información como la sesión del usuario, el método HTTP utilizado (GET, POST, etc.)
    y cualquier dato enviado con la solicitud.
    :param remoto: El parámetro "remoto" es una cadena que indica si los registros insertados son
    remotos o no. Si el valor es "remoto", se devuelven los registros insertados desde la aplicación.
    Si el valor es "local", se devuelven los registros insertados localmente.
    :return: una respuesta JSON que contiene una lista de diccionarios. Cada diccionario representa un
    registro de entradas de diario insertadas y contiene los siguientes campos: 'id', 'seccion', 'mes',
    'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', y 'ruta'.
    """ 
    if remoto == "2" or remoto == 2:
        remoto = None

    if year == None:
        year = datetime.now().year

    if mes == None:
        #obtengo el ultimo mes
        if datetime.now().month == 1:
            mes = 12
            year = datetime.now().year - 1
        else:
            mes = datetime.now().month - 1

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registros = []
    
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id).values('id_empleado__id')
    if administrador or director:
        if remoto == None:
            registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido__isnull=True,hora__year=year, hora__month=mes).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
        else:
            registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido__isnull=True, remoto=remoto, hora__year=year, hora__month=mes).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    else:
        if remoto == None:
            registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_empleado__id__in=empleado, id_archivo_leido__isnull=True,hora__year=year, hora__month=mes).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
        else:
            registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_empleado__id__in=empleado, id_archivo_leido__isnull=True, remoto=remoto, hora__year=year, hora__month=mes).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    return JsonResponse(list(registros), safe=False)


@login_required
def diasTotalesEmpleados(request, year=None):
    """
    La función "diasTotalesEmpleados" comprueba si el usuario es un administrador o un director, y si es
    así, recupera los datos necesarios para la vista y renderiza la plantilla "relaciones-empleados.html"
    con los datos. Si el usuario no es un administrador o un director, redirige a la página "sin-permiso".
    :param request: El objeto "request" representa la solicitud HTTP que el usuario hizo para acceder a
    la vista. Contiene información como la sesión del usuario, el método HTTP utilizado (GET, POST, etc.)
    y cualquier dato enviado con la solicitud.
    :return: una plantilla HTML renderizada con los datos necesarios para la vista. Los datos incluyen la
    barra de navegación, un valor booleano que indica si el usuario es un administrador, una lista de
    registros insertados y la ruta actual.
    """

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        if year == None:
            year = datetime.now().year
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "rutaActual": "Dias totales solicitados por los empleados",
            "year":year
        }
        return render(request,"dias-totales-empleados.html",infoVista)
    else:
        return redirect('timetrackpro:sin-permiso')


@login_required
def datosDiasTotalesEmpleados(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    diasTotalesEmpleados = []
    if year == None:
        year = datetime.now().year
    
    if administrador or director:
        
        empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(fecha_baja_app__isnull = True).values('id', 'nombre', 'apellidos', 'fecha_baja_app')
        for e in empleados:
            vacaciones = calcularVacacionesConsumidas(e['id'], year)
            asuntosPropios = calcularAsuntosPropiosConsumidos(e['id'],year)
            asuntosPropiosRecuperables = calcularAsuntosPropiosRecuperablesConsumidos(e['id'],year)
            ausencias = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(empleado=e['id'], year=year).count()
            disfrutadasVacacionesSemanaSanta = gastadasVacacionesSemanaSanta(e['id'], year)
            disfrutadasVacacionesNavidad = gastadasVacacionesNavidad(e['id'], year)
            diasTotalesEmpleados.append({"empleado": e, "vacaciones": vacaciones, "asuntosPropios":asuntosPropios, "asuntosPropiosRecuperables":asuntosPropiosRecuperables, "ausencias":ausencias, "activo":e['fecha_baja_app'], "semanaSanta":disfrutadasVacacionesSemanaSanta, "navidad":disfrutadasVacacionesNavidad})


    return JsonResponse(list(diasTotalesEmpleados), safe=False)



@login_required
def relacionesEmpleados(request):
    """
    La función "relacionesEmpleados" comprueba si el usuario es un administrador o un director, y si es
    así, recupera los datos necesarios para la vista y renderiza la plantilla "relaciones-empleados.html"
    con los datos. Si el usuario no es un administrador o un director, redirige a la página "sin-permiso".
    :param request: El objeto "request" representa la solicitud HTTP que el usuario hizo para acceder a
    la vista. Contiene información como la sesión del usuario, el método HTTP utilizado (GET, POST, etc.)
    y cualquier dato enviado con la solicitud.
    :return: una plantilla HTML renderizada con los datos necesarios para la vista. Los datos incluyen la
    barra de navegación, un valor booleano que indica si el usuario es un administrador, una lista de
    registros insertados y la ruta actual.
    """

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "rutaActual": "Relación empleados",
        }
        return render(request,"relaciones-empleados.html",infoVista)
    else:
        return redirect('timetrackpro:sin-permiso')

@login_required
def datosRelacionesEmpleados(request):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleados = []
    if administrador or director:
        empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id','id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_tarjeta_acceso', 'id_tarjeta_acceso__nombre', 'id_tarjeta_acceso__apellidos', 'id_tarjeta_acceso__dni', 'id_tarjeta_acceso__id_tarjeta', 'id_tarjeta_acceso__fecha_alta', 'id_tarjeta_acceso__fecha_baja', 'id_tarjeta_acceso__imagen', 'id_tarjeta_acceso__acceso_laboratorios', 'id_tarjeta_acceso__acceso_cpd', 'id_tarjeta_acceso__acceso_alerta2', 'id_tarjeta_acceso__activo')
    return JsonResponse(list(empleados), safe=False)




@login_required
def obtenerRegistroEmpleados(request):
    """
    The function "obtenerRegistroEmpleados" retrieves employee records and renders them in a template
    for an attendance report.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data sent with the request
    :return: a rendered HTML template with the information needed to display the employee registration
    report.
    """

    administrador = esAdministrador(request.user.id)
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(activo=1).values()
    exEmpleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(activo=0).exclude(id__in=[100,101]).values()

    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados),
        "exEmpleados":list(exEmpleados),
        "rutaActual": "Informe de asistencia empleados",
    }
    return render(request,"informe-registro-usuario.html",infoVista)


@login_required
def obtenerRegistroSemanalEmpleados(request):
    """
    The function "obtenerRegistroSemanalEmpleados" renders a dashboard view with information about
    employee attendance.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data sent with the request
    :return: a rendered HTML template called "dashboard.html" with the context variable "infoVista".
    """

    administrador = esAdministrador(request.user.id)
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(activo=1).values()
    exEmpleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(activo=0).exclude(id__in=[100,101]).values()
    # current_url = request.path[1:]
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados),
        "exEmpleados":list(exEmpleados),
        "rutaActual": "Informe de asistencia empleados",
    }
    return render(request,"informe-registro-semanal-usuario.html",infoVista)

@login_required
def fichar(request):
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    registrosRemotosHoy = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_empleado=empleado.id_empleado, hora__date=datetime.now().date(), remoto=1)
    if empleado.id_empleado.fichar_remoto == 1:
        if request.method == 'POST':
            # obtener hora actual, hora utc    
            zona_horaria_espana = pytz.timezone('Europe/Madrid')
            hora = datetime.now(zona_horaria_espana).strftime("%Y-%m-%d %H:%M:%S")
            registro = RegistrosTimetrackpro(id_empleado=empleado.id_empleado, nombre_empleado=empleado.id_empleado.nombre, hora=hora, remoto=1)
            registro.save(using='timetrackpro')
            alerta["activa"] = True
            alerta["tipo"] = "success"
            alerta["mensaje"] = "Fichaje realizado correctamente."
            alerta["icono"] = iconosAviso["success"]

            return redirect('timetrackpro:correcto', mensaje='Has fichado correctamente.')

        infoVista = {
            "navBar":navBar,
            "rutaActual": "Fichar",
            "alerta": alerta,
            "registrosRemotosHoy": list(registrosRemotosHoy),
        }
        return render(request,"fichar.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para fichar.")

    


@login_required
def datosRegistroEmpleados(request):
    """
    La función "datosRegistroEmpleados" recupera los datos de registro de los empleados en función de
    los parámetros proporcionados.
    :param request: El objeto "request" es un objeto que representa la solicitud HTTP realizada por el
    cliente. Contiene información como el método de solicitud, las cabeceras y los parámetros de la
    consulta. En este código, se utiliza para recuperar los parámetros de la consulta utilizando el
    método "GET".
    :return: una respuesta JSON que contiene la variable "informe", que es el resultado de llamar a la  
    función "calcularHoras" con los parámetros "usuarios", "fechaInicio" y "fechaFin".

    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    mesPrevio = datetime.now().month
    yearActual = datetime.now().year
    if mesPrevio == 1:
        mesPrevio = 12
        yearActual = yearActual - 1

    usuarios = []
    informe = []
    if request.GET.get("fechaInicio") != None:
        fechaInicio = datetime.strptime(request.GET.get("fechaInicio"), '%d/%m/%Y')
    else:
        fechaInicio = str(yearActual) + "-" + str(mesPrevio) + "-01"
        fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d')

    if request.GET.get("fechaFin") != None:
        fechaFin = datetime.strptime(request.GET.get("fechaFin"), '%d/%m/%Y')
    else:
        ultimoDiaMes = calendar.monthrange(yearActual, mesPrevio)  
        fechaFin = str(yearActual) + "-" + str(mesPrevio) + "-"+str(ultimoDiaMes[1])
        fechaFin = datetime.strptime(fechaFin, '%Y-%m-%d')
    if administrador or director:
        if request.GET.get("listEmpleados") != None:
            usuarios = request.GET.get("listEmpleados").split("_")
        else: 
            usuarios = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values_list('id', flat=True)
    else:
        usuario = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        usuarios.append(usuario.id_empleado.id)

    informe = calcularHoras(usuarios, fechaInicio, fechaFin)
    return JsonResponse(list(informe), safe=False)


@login_required
def datosRegistroSemanalEmpleados(request):
    """
    La función "datosRegistroSemanalEmpleados" recupera los datos de registro de los empleados en función
    de los parámetros proporcionados.
    :param request: El objeto "request" es un objeto que representa la solicitud HTTP realizada por el
    cliente. Contiene información como el método de solicitud, las cabeceras y los parámetros de la
    consulta. En este código, se utiliza para recuperar los parámetros de la consulta utilizando el
    método "GET".
    :return: una respuesta JSON que contiene la variable "informe", que es el resultado de llamar a la
    función "calcularHorasSemanal" con los parámetros "usuarios", "fechaInicio" y "fechaFin".
    
    """

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    mesPrevio = datetime.now().month
    yearActual = datetime.now().year
    if mesPrevio == 1:
        mesPrevio = 12
        yearActual = yearActual - 1
    usuarios = []

    if request.GET.get("fechaInicio") != None:
        fechaInicio = datetime.strptime(request.GET.get("fechaInicio"), '%d/%m/%Y')
    else:
        fechaInicio = str(yearActual) + "-" + str(mesPrevio) + "-01"
        fechaInicio = datetime.strptime(fechaInicio, '%Y-%m-%d')


    if request.GET.get("fechaFin") != None:
        fechaFin = datetime.strptime(request.GET.get("fechaFin"), '%d/%m/%Y')
    else:
        ultimoDiaMes = calendar.monthrange(yearActual, mesPrevio)  
        fechaFin = str(yearActual) + "-" + str(mesPrevio) + "-"+str(ultimoDiaMes[1])
        fechaFin = datetime.strptime(fechaFin, '%Y-%m-%d')

    if administrador or director:

        if request.GET.get("listEmpleados") != None:
            usuarios = request.GET.get("listEmpleados").split("_")
        else: 
            usuarios = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values_list('id', flat=True)
    else:
        usuario = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        usuarios.append(usuario.id_empleado.id)            
    informe = calcularHorasSemanales(usuarios, fechaInicio, fechaFin)
    return JsonResponse(list(informe), safe=False)

def comprobarJornadaEmpleado(idUsuario,fechaInicio, fechaFin=None):
    """
    The function `comprobarJornadaEmpleado` checks the work schedule of an employee based on their ID
    and a given date range, and returns the number of weekly working hours.
    
    :param idUsuario: The id of the user or employee for whom you want to check the work schedule
    :param fechaInicio: The starting date for which you want to check the employee's work schedule
    :param fechaFin: The parameter "fechaFin" is an optional parameter that represents the end date of
    the period for which you want to check the employee's work schedule. If no end date is provided, it
    defaults to the same value as the start date (fechaInicio)
    :return: the value of the variable "jornadaLaboral", which represents the number of weekly working
    hours for the employee.
    """
    if fechaFin is None:
        fechaFin = fechaInicio
    jornadaLaboral = 37.5
    # compruebo si el usuario tiene una jornada definida
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idUsuario)[0]
    # comprubo si existe una jornada para el empleado donde la fecha de inicio sea mayor o igual que la fechaInicio y la fecha de fin sea null
    if RelJornadaEmpleados.objects.using("timetrackpro").order_by('-id').filter(id_empleado=empleado, fecha_inicio__lte=fechaInicio, fecha_fin__isnull=True).exists():
        jornada = RelJornadaEmpleados.objects.using("timetrackpro").order_by('id').filter(id_empleado=empleado, fecha_inicio__lte=fechaInicio, fecha_fin__isnull=True)[0]
        jornadaLaboral = jornada.horas_semanales
    elif RelJornadaEmpleados.objects.using("timetrackpro").order_by('-id').filter(id_empleado=empleado, fecha_inicio__lte=fechaInicio, fecha_fin__gte=fechaFin).exists():
        jornada = RelJornadaEmpleados.objects.using("timetrackpro").order_by('id').filter(id_empleado=empleado, fecha_inicio__lte=fechaInicio, fecha_fin__gte=fechaFin)[0]
        jornadaLaboral = jornada.horas_semanales
    else:
        jornadaLaboral = 37.5
    return jornadaLaboral

def comprobarPermisosEmpleado(idUsuario, fechaInicio, fechaFin=None):
    """
    The function `comprobarPermisosEmpleado` checks if an employee has requested any permissions,
    personal matters, or vacations for a given date range and returns the details along with the number
    of days for each category.
    
    :param idUsuario: The parameter "idUsuario" represents the ID of the user or employee for whom we
    want to check the permissions
    :param fechaInicio: The parameter "fechaInicio" represents the start date for which you want to
    check the employee's permissions
    :param fechaFin: The parameter "fechaFin" is an optional parameter that represents the end date for
    checking permissions. If it is not provided, the function will use the same value as "fechaInicio"
    (start date) for checking permissions
    :return: The function `comprobarPermisosEmpleado` returns a tuple containing the following values:
    """
    if fechaFin is None:
        fechaFin = fechaInicio    
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idUsuario)[0]
    estadosAceptadosPermisos = [18,20,21]
    diasPermisos = 0;
    diasAsuntosPropios = 0;
    diasVacaciones = 0;
    permisos = "No hay permisos ni ausencias solicitados para la fecha seleccionada"
    asuntosPropios = "No hay asuntos propios solicitados para la fecha seleccionada"
    vacaciones = "No hay vacaciones solicitadas para la fecha seleccionada"
    # compruebo si el usuario ha solicitado alguna ausencia para ese dia
    if PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin, estado__id__in=estadosAceptadosPermisos).exists():
        permisos = "El empleado tiene una ausencia solicitada para la fecha seleccionada"
        # cuento los dias de ausencia solicitados por el empleado
        diasPermisos = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin, estado__id__in=estadosAceptadosPermisos).count()
    if AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin, estado__id=11).exists():
        asuntosPropios = "El empleado tiene un asunto propio solicitado para la fecha seleccionada"
        # cuanto los dias de asuntos propios solicitados por el empleado
        diasAsuntosPropios = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin, estado__id=11).count()
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin, estado__id=11).exists():
        vacaciones = "El empleado tiene dias de vacaciones solicitados para la fecha seleccionada"
        # cuento los dias de vacaciones solicitados por el empleado
        diasVacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin, estado__id=11).count()
    return permisos, asuntosPropios, vacaciones, diasPermisos, diasAsuntosPropios, diasVacaciones

def comprobarFestivos(fechaInicio, fechaFin=None):
    """
    The function `comprobarFestivos` checks for holidays between two given dates.
    
    :param fechaInicio: The parameter "fechaInicio" represents the start date for which you want to
    check if it is a holiday or not
    :param fechaFin: The parameter "fechaFin" is an optional parameter that represents the end date for
    checking holidays. If no value is provided for "fechaFin", it defaults to the value of "fechaInicio"
    :return: the number of holidays between the given start and end dates.
    """
    if fechaFin is None:
        fechaFin = fechaInicio
    festivos = 0

    if fechaInicio == fechaFin:
        if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio=fechaInicio).exists():
            festivos = 1
    else:
        if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin).exists():  
            # cuento los dias de festivos restando la fecha fin a la fecha inicio
            # obtengo todos los festivos que hay entre la fecha de inicio y la fecha de fin

            festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__gte=fechaInicio)[0]

            if  festivo.fecha_fin <= fechaFin:
                
                festivos = (festivo.fecha_fin - festivo.fecha_inicio).days + 1
            else:
                festivos = (fechaFin - festivo.fecha_inicio).days + 1

    if festivos < 0:
        festivos = 0

    return festivos

def comprobarFestivosSemanas(fechaInicio, fechaFin=None):
    # si la fechaFin no existe le asigno la fechaInicio
    if fechaFin is None:
        fechaFin = fechaInicio
    festivos = 0
    # compruebo si hay algún festivo entre las dos fechas 
    if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin).exists():
        festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin)[0]
        # obtener diferencia dias entre las fechas
        # si la fecha de inicio es distinta de la fecha fin
        fInicio = date(festivo.fecha_inicio.year, festivo.fecha_inicio.month, festivo.fecha_inicio.day)
        fFin = date(festivo.fecha_fin.year, festivo.fecha_fin.month, festivo.fecha_fin.day)
        # comparo las fechas de inicio y fin
        
        if fFin != fInicio:
            # obtengo la diferencia de dias entre la fecha de inicio y la fecha de fin
            # me quedo unicamente con los dias de la fecha de inicio y la fecha de fin y los resto
            dias = (fFin - fInicio).days + 1
        else:
            dias = 1
        festivos = festivos + dias  
    return festivos


def pruebas(request):
    empleados = []
    idEmpleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=1)[0]
    empleados.append(idEmpleado.id)
    fechaInicio = date(2023, 10, 1)
    fechaFin =  date(2023, 10, 31)
    calcularHorasSemanales(empleados, fechaInicio, fechaFin)
        # Devuelve una respuesta HTTP adecuada, por ejemplo:
    #festivos = comprobarFestivos(fechaInicio, fechaFin)
    return HttpResponse("festivos: " + str(festivos))
    #return jornada

def calcularHoras(usuarios, fechaInicio, fechaFin):
    """
    The function "calcularHoras" calculates the number of hours worked by employees within a given date
    range and generates a report.
    
    :param usuarios: A list of user IDs for whom you want to calculate the hours
    :param fechaInicio: The starting date for calculating the hours
    :param fechaFin: The parameter "fechaFin" represents the end date for calculating the hours. It is
    the date until which the hours will be calculated
    :return: a list of dictionaries containing information about the calculated hours for each employee
    and day within the specified date range.
    """

    # linea de informe ejemplo
    # {"empleado": 1, "dia": dd/mm/yyyy, "horas": 7, "correcto": "si", "observaciones": "", fichajes: 2}
    informe = []
    jornadaLaboral = None
    # sumo un dia a la fecha fin
    fechaFin = fechaFin + timedelta(days=1)

    registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_empleado__id__in=usuarios, hora__range=(fechaInicio, fechaFin)).order_by("hora").all()

    
    for e in usuarios:
        dias = registros.filter(id_empleado__id=e).order_by("id_empleado", 'hora').values_list('hora__date').distinct()
        empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=e)[0]
        dias = list(set(dias))
        for d in dias:
            # obtener la jornada del empleado
            jornada = comprobarJornadaEmpleado(empleado.id_usuario.id, d[0])
            if isinstance(jornada, float):
                jornadaLaboral = jornada
            elif isinstance(jornada, dict) and 'get' in jornada:
                jornadaLaboral = jornada.get('get')('x')
            else:
                jornadaLaboral=jornada

            dia_siguiente = d[0]+timedelta(days=1)
            # hacer que registrosDiaEmpleado = registros.filter(id_empleado__id=e, hora__range=(d["hora__date"],dia_siguiente)).all() esté ordenado por hora

            registrosDiaEmpleado = registros.filter(id_empleado__id=e, hora__range=(d[0],dia_siguiente)).all()
            # aquí podríamos comprobar cuando el usuario no tienen ningun registro ese día si tiene alguna justificacion para ajustar
            permisos, asuntosPropios, vacaciones, diasPermisos, diasAsuntosPropios, diasVacaciones = comprobarPermisosEmpleado(empleado.id_usuario.id, d[0])
            festivo = comprobarFestivos(d[0])
            if len(registrosDiaEmpleado)%2 == 0:
                horas = 0
                tramo = 0
                auxHoras = 0
                for r in registrosDiaEmpleado:
                    if tramo == 0:
                        auxHoras = r.hora
                        tramo = 1
                    else:
                        horas = horas + (r.hora - auxHoras).total_seconds()/3600
                        tramo = 0
                # comprobar justificaciones para ajustar las horas del dia
                informe.append({"empleado": e, "dia": d[0], "horas": horas, "correcto": "si", "observaciones": "", "fichajes": len(registrosDiaEmpleado), "nombreEmpleado": empleado.id_usuario.nombre + " " + empleado.id_usuario.apellidos, "jornada": jornadaLaboral, "permisos": permisos, "asuntosPropios": asuntosPropios, "vacaciones": vacaciones, "diasPermisos": diasPermisos, "diasAsuntosPropios": diasAsuntosPropios, "diasVacaciones": diasVacaciones, "festivo": festivo})
            else:
                fichajesHechos = registrosDiaEmpleado.values_list('hora__time', flat=True)
                informe.append({"empleado": e, "dia": d[0], "horas": 0, "correcto": "no", "observaciones": "No se puede hacer el cálculo por fichaje impar", "fichajes": len(registrosDiaEmpleado), "horas_fichadas":list(fichajesHechos), "nombreEmpleado": empleado.id_usuario.nombre + " " + empleado.id_usuario.apellidos, "jornada": jornadaLaboral, "permisos": permisos, "asuntosPropios": asuntosPropios, "vacaciones": vacaciones, "diasPermisos": diasPermisos, "diasAsuntosPropios": diasAsuntosPropios, "diasVacaciones": diasVacaciones, "festivo": festivo})
    return informe

def calcularHorasSemanales (usuarios, fechaInicio, fechaFin):
    """
    The function "calcularHorasSemanales" calculates the weekly working hours for a list of employees
    within a specified date range.
    
    :param usuarios: A list of user IDs for which you want to calculate the weekly hours
    :param fechaInicio: The starting date for calculating the weekly hours
    :param fechaFin: The parameter "fechaFin" represents the end date of the time period for which you
    want to calculate the weekly hours
    :return: a list of dictionaries, where each dictionary represents a report for a specific employee
    and week. The dictionary contains information such as the employee ID, week, total hours worked,
    whether the calculation is correct or not, any observations, number of recorded shifts, and
    additional details about the employee and week.
    """
    # linea de informe ejemplo
    # {"empleado": 1, "semana": dd al dd MM de YYYY, "horas": 37.5, "correcto": "si", "observaciones": "", fichajes: 2}
    informe = []
    # sumo un dia a la fecha fin
    fechaFin = fechaFin + timedelta(days=1)
    registros = RegistrosTimetrackpro.objects.using("timetrackpro").order_by("hora").filter(id_empleado__id__in=usuarios, hora__range=(fechaInicio, fechaFin)).all()
    for e in usuarios:
        semanas = registros.filter(id_empleado__id=e).annotate(semana=ExtractWeek('hora')).values_list('semana').distinct()
        empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=e)[0]
        semanas = list(set(semanas))
        #obtengo las horas por dias y las agrupo por semana.
        for s in semanas:
            dias = registros.filter(id_empleado__id=e, hora__week=s[0]).values_list('hora__date').distinct()
            dias = list(set(dias))
            year = dias[0][0].year
            # obtengo todos los dias de esa semana 
            inicioSemana, finSemana = obtenerFechaSemana(year, s[0])    
            horas = 0
            diasErrores = []
            diasFichados = 0
            jornada = comprobarJornadaEmpleado(empleado.id_usuario.id, inicioSemana, finSemana)
            if isinstance(jornada, float):
                jornadaLaboral = jornada
            elif isinstance(jornada, dict) and 'get' in jornada:
                jornadaLaboral = jornada.get('get')('x')
            else:
                jornadaLaboral=jornada
            permisos, asuntosPropios, vacaciones, diasPermisos, diasAsuntosPropios, diasVacaciones = comprobarPermisosEmpleado(empleado.id_usuario.id, inicioSemana, finSemana)
            #festivos = comprobarFestivos(inicioSemana, finSemana)
            festivos = comprobarFestivosSemanas(inicioSemana, finSemana)
        
            for d in dias:
                # comprubeo si el dia tiene un numero par de registros
                dia_siguiente = d[0]+timedelta(days=1)
                registrosDiaEmpleado = registros.filter(id_empleado__id=e, hora__range=(d[0],dia_siguiente)).all()

                if len(registrosDiaEmpleado)%2 == 0:
                    tramo = 0
                    auxHoras = 0
                    for r in registrosDiaEmpleado:
                        if tramo == 0:
                            auxHoras = r.hora
                            tramo = 1
                        else:
                            horas = horas + (r.hora - auxHoras).total_seconds()/3600
                            tramo = 0
                    diasFichados = diasFichados + 1
                else:
                    diasErrores.append(d[0])
            # si hay dias con errores, los añado al informe
            if len(diasErrores) > 0:                
                informe.append({"empleado": e, "semana": s[0], "horas": horas, "correcto": "no", "observaciones": "No se puede hacer el cálculo por fichaje impar", "fichajes": diasFichados, "diasErrores": diasErrores, "nombreEmpleado": empleado.id_usuario.nombre + " " + empleado.id_usuario.apellidos, "inicioSemana": inicioSemana, "finSemana": finSemana, "jornada": jornadaLaboral, "permisos": permisos, "asuntosPropios": asuntosPropios, "vacaciones": vacaciones, "diasPermisos": diasPermisos, "diasAsuntosPropios": diasAsuntosPropios, "diasVacaciones": diasVacaciones, "festivos": festivos})
            else:
                informe.append({"empleado": e, "semana": s[0], "horas": horas, "correcto": "si", "observaciones": "", "fichajes": diasFichados, "nombreEmpleado": empleado.id_usuario.nombre + " " + empleado.id_usuario.apellidos, "inicioSemana": inicioSemana, "finSemana": finSemana, "jornada": jornadaLaboral, "permisos": permisos, "asuntosPropios": asuntosPropios, "vacaciones": vacaciones, "diasPermisos": diasPermisos, "diasAsuntosPropios": diasAsuntosPropios, "diasVacaciones": diasVacaciones, "festivos": festivos})
    return informe


def obtenerFechaSemana(year, week):
    """
    The function `obtenerFechaSemana` takes a year and week number as input and returns the start and
    end dates of that week.
    
    :param year: The year parameter represents the year for which you want to obtain the date range of a
    specific week
    :param week: The week parameter represents the week number within the year. It can be any integer
    value from 1 to 52 (or 53 in some cases)
    :return: The function `obtenerFechaSemana` returns a tuple containing the start and end dates of a
    given week in a given year.
    """
    # Assuming ISO week starts from Monday
    start_of_week = datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w").date()
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week, end_of_week

def quitarAcentos(cadena):
    """
    The function "quitarAcentos" removes accents from a given string.
    :param cadena: The parameter "cadena" represents a string that may contain accented characters
    :return: a string with all the accents removed from the input string.
    """
    return ''.join((c for c in unicodedata.normalize('NFD', cadena) if unicodedata.category(c) != 'Mn'))



def convertirFormatoDateTime(datoFecha):
    """
    The function `convertirFormatoDateTime` takes a date and time string in either the format
    'YYYY-MM-DD HH:MM:SS' or 'DD/MM/YYYY HH:MM:SS' and converts it to the format 'YYYY-MM-DD HH:MM:SS'.
    
    :param datoFecha: The parameter "datoFecha" is a string representing a date and time in either the
    format "YYYY-MM-DD HH:MM:SS" or "DD/MM/YYYY HH:MM:SS"
    :return: a string in the format '%Y-%m-%d %H:%M:%S'.
    """
    try:
        # Intenta convertir la fecha y hora al formato deseado
        fechaHora = datetime.strptime(datoFecha, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            # Si la conversión falla, intenta otro formato
            fechaHora = datetime.strptime(datoFecha, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            # Si ambos formatos fallan, regresa None
            return None
    
    return fechaHora.strftime('%Y-%m-%d %H:%M:%S')


@login_required
def verRegistro(request, id):
    """
    The function "verRegistro" checks if the user is an administrator or director, retrieves a record
    from the database, processes a file, and renders a template with the record information if the user
    has permission.
    
    :param request: The request object represents the HTTP request that the server receives from the
    client. It contains information about the request, such as the method (GET or POST), headers, and
    user session
    :param id: The "id" parameter is the ID of the record that you want to retrieve and display. It is
    used to filter the RegistrosJornadaInsertados objects and retrieve the specific record with that ID
    :return: either a rendered HTML template or a redirect to another view, depending on the conditions.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registro = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=id)[0]
    maquina = MaquinaControlAsistencia.objects.using("timetrackpro").filter(nombre__icontains=registro.seccion)[0]
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values()

    ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_NUEVO + registro.ruta
    ruta_leido = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + registro.ruta
    IdEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]

    '''
    <url> - url de la aplicacion
    <mes> - mes del fichero de registro
    <year> - año del fichero de registro
    <seccion> - seccion del fichero de registro
    '''

    '''
    ASUNTO 
    Nuevo fichero de registro de jornada insertado.       

    MENSAJE PARA EL DESTINATARIO

    Se ha insertado un nuevo fichero de registro de jornada en la aplicación.
    Los datos del fichero son los siguientes:
    - Mes y año: <mes> de <year>
    - Sección: <seccion>
    Puede consultar más información en el siguiente enlace.
    <url>
    '''

    if request.method == 'POST' and administrador:
        if not os.path.isfile(ruta):
            return "El archivo no existe"
        with io.open(ruta, "r", encoding="utf-8") as archivo:
            primeraLinea = True
            for linea in archivo:
                if primeraLinea:
                    primeraLinea = False
                    continue
                linea = linea.strip()
                # Comprobar si la línea está vacía
                if not linea:
                    continue
                # Dividir la línea en campos (supongamos que los campos están separados por comas)
                campos = linea.split('\t')
                # Obtener los valores de los campos (reemplaza con los nombres correctos)
                id_empleado = campos[0].lstrip('0')
                nombre = campos[1]
                # reemplazo los espacios por guiones bajos y lo pongo en mayusculas
                nombre = nombre.replace(" ", "_").upper()
                empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(nombre=nombre)[0]
                hora = convertirFormatoDateTime(campos[3])
                # Comprobar si en la base de datos existen registros con el mismo id_archivo_leido
                if not RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=id, id_empleado=empleado.id, hora=hora).exists():
                    # Si no existe, crea un nuevo registro en la base de datos
                    nuevoRegistro = RegistrosTimetrackpro(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                    nuevoRegistro.save()
        # Mover el archivo a la nueva ruta después de procesarlo
        shutil.move(ruta, ruta_leido)
        url = 'http://alerta2.es/private/timetrackpro/registros-insertados'

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=49)[0]
        subject = mensajeTipoDestinatario.mensaje.replace('\n', '').replace('\r', '')
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<mes>", registro.mes).replace("<year>", str(registro.year)).replace("<url>", url).replace("<seccion>", registro.seccion)

        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]

        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        enviarTelegram(subject, mensajeDestinatario)



    if RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=registro.id, id_empleado=IdEmpleado.id).exists() or administrador or director:
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "registro":registro,
            "rutaPrevia":"Registros insertados",
            "urlRutaPrevia":reverse('timetrackpro:registros-insertados'),
            "rutaActual":str(registro.seccion) + " / " + str(registro.mes) + " / " + str(registro.year),
            "empleados":empleados,
        }
        return render(request,"verRegistro.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver el registro seleccionado.")

    # guardo los datos en un diccionario

@login_required
def actualizarRegistro(request, id):
    """
    The function `actulizarRegistro` updates a record in a database based on a request and ID, and
    renders a view with the updated record and related data.
    
    :param request: The request object represents the HTTP request that the user made to the server. It
    contains information such as the user's session, the HTTP method used (GET, POST, etc.), and any
    data submitted with the request
    :param id: The `id` parameter is the identifier of the record that needs to be updated. It is used
    to retrieve the specific record from the database
    :return: a rendered HTML template with the context data "infoVista" if the user is an administrator.
    If the user is not an administrator, it redirects to another view with a "mensaje" parameter.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        registro = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=id)[0]
        maquina = MaquinaControlAsistencia.objects.using("timetrackpro").filter(nombre__icontains=registro.seccion)[0]

        # cambiamos el nombre al registro antiguo en la ruta de insertados
        ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + registro.ruta
        # comprobamos si hay un registro que acabe con _old.txt
        if os.path.isfile(ruta):
            nombreNuevo = registro.ruta.replace(".txt", "_old.txt")
            # si ya existe un registro con ese nombre, lo borramos
            if os.path.isfile(settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + nombreNuevo):
                os.remove(settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + nombreNuevo)
            shutil.move(ruta, settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + nombreNuevo)
            registro.ruta = nombreNuevo
            registro.save(using='timetrackpro')

        #insertamos el nuevo registro
        # leemos el fichero que acabamos de insertar, linea a linea y comprobamos si ya existe en la base de datos
        ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_NUEVO + registro.ruta
        ruta_leido = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + registro.ruta

        if request.method == 'POST':
            if not os.path.isfile(ruta):
                return "El archivo no existe"
            with open(ruta, "r") as archivo:
                archivo.readline()
                for linea in archivo:
                    linea = linea.strip()
                    # Comprobar si la línea está vacía
                    if not linea:
                        continue
                    # Dividir la línea en campos (supongamos que los campos están separados por comas)
                    campos = linea.split('\t')
                    # Obtener los valores de los campos (reemplaza con los nombres correctos)
                    id_empleado = campos[0].lstrip('0')
                    empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=id_empleado)[0]
                    nombre = campos[1]
                    hora = convertirFormatoDateTime(campos[3])
                    # Comprobar si en la base de datos existen registros con el mismo id_archivo_leido
                    if RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=id).exists():
                        registrosYaInsertados = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=id).values()
                        for r in registrosYaInsertados:
                            if r["id_empleado"] == empleado.id and r["hora"] == hora:
                                continue
                            else:
                                # Si no existe, crea un nuevo registro en la base de datos
                                nuevoRegistro = RegistrosTimetrackpro(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                                nuevoRegistro.save()
                    else:
                        # Si no existe, crea un nuevo registro en la base de datos
                        nuevoRegistro = RegistrosTimetrackpro(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                        nuevoRegistro.save()
            # Mover el archivo a la nueva ruta después de procesarlo
            shutil.move(ruta, ruta_leido)
        registrosInsertados = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=registro.id).values()

        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "registro":registro,
            "registrosInsertados":list(registrosInsertados)
        }
        return render(request,"verRegistro.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para actualizar el registro seleccionado.")

@login_required
def datosRegistro(request, id):
    """
    The function "datosRegistro" retrieves data from the "Registros" table based on the user's role and
    filters.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the method used (GET, POST,
    etc.), and any data sent with the request
    :param id: The "id" parameter is the identifier of the file being requested. It is used to filter
    the records in the "Registros" table based on the "id_archivo_leido" field
    :return: a JSON response containing a list of records. The records include various fields such as
    'id', 'id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes',
    'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registros = []
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id).values('id_empleado__id')
    if administrador or director:
        registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=id).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    else:
        registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=id, id_empleado__id__in=empleado).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    return JsonResponse(list(registros), safe=False)

@login_required
def verLineaRegistro(request, id):
    """
    The function `verLineaRegistro` checks if the user has permission to view a specific record and
    renders the record details if they have permission, otherwise it redirects to an error page.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the requested URL, and any data
    sent with the request
    :param id: The "id" parameter is the identifier of the specific record or entry in the database that
    you want to view. It is used to retrieve the corresponding record from the "Registros" table in the
    "timetrackpro" database
    :return: either a rendered HTML template with the information of a specific record, or it is
    redirecting to another page with an error message if the user does not have permission to view the
    selected record.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id).values('id_empleado__id')

    if RegistrosTimetrackpro.objects.using("timetrackpro").filter(id=id, id_empleado__id__in=empleado).exists() or administrador or director:     
        registro = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
   
        rutaActual = "Registro " + registro.nombre_empleado +" / " + registro.hora.strftime("%d de %m de %Y") + " / " + registro.hora.strftime("%H:%M:%S") 
        rutaPrevia = "Registros insertados"
        urlRutaPrevia = reverse('timetrackpro:registros-insertados')

        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "registro":registro,
            "rutaActual":rutaActual,
            "rutaPrevia":rutaPrevia,
            "urlRutaPrevia":urlRutaPrevia,
        }
        return render(request,"verLineaRegistro.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver el registro seleccionado.")

@login_required
def agregarLineaRegistro(request):
    '''
    La función `agregarLineaRegistro` permite a un administrador agregar una línea de registro a un
    registro en una aplicación TimeTrackPro.
    
    :param request: El objeto `request` contiene información sobre la solicitud HTTP actual, como el
    usuario que realiza la solicitud, el método utilizado (GET o POST) y cualquier dato enviado con la
    solicitud
    :return: una redirección a la vista 'ver-registro' con el parámetro 'id' establecido en el id del
    objeto 'archivoModificado', o una redirección a la vista 'ups' con el parámetro 'mensaje' establecido
    en "No tienes permiso para agregar un registro."
    '''
    administrador = esAdministrador(request.user.id)
    if administrador and request.method == 'POST':
            registro = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=request.POST.get("registro"))[0]
            maquina = MaquinaControlAsistencia.objects.using("timetrackpro").filter(nombre__icontains=registro.seccion)[0]
            empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=request.POST.get("empleado"))[0]
            nombre = empleado.nombre
            hora = request.POST.get("hora_registro")
            remoto = 0
            modificado = 1
            id_archivo_leido = registro
            nuevoRegistro = RegistrosTimetrackpro(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=remoto, modificado=modificado, id_archivo_leido=id_archivo_leido)
            nuevoRegistro.save(using='timetrackpro')
            return redirect('timetrackpro:ver-registro', id=registro.id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar un registro.")


@login_required
def editarLineaRegistro(request, id):
    """
    The function `editarLineaRegistro` allows an administrator to edit a specific line of a record in a
    TimeTrackPro application.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data submitted with the request
    :param id: The `id` parameter is the identifier of the record that needs to be edited. It is used to
    retrieve the specific record from the database
    :return: a redirect to either the 'ver-linea-registro' view with the specified id parameter or the
    'ups' view with a specified error message if the user does not have permission to edit the selected
    record.
    """
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        registro = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]

        registro.hora = request.POST.get("hora")
        registro.modificado = 1
        motivo = request.POST.get("motivo")
        if motivo != "":
            registro.motivo_modificacion = motivo
        else :
            registro.motivo_modificacion = None
        registro.save(using='timetrackpro')
        return redirect('timetrackpro:ver-linea-registro', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar el registro seleccionado.")

@login_required
def eliminarArchivoRegistro(request, id):
    """
    la función `eliminarArchivoRegistro` elimina un archivo de la base de datos y guarda el registro
    eliminado en otra tabla.
    :param request: El objeto `request` es un objeto que representa la solicitud HTTP realizada por el
    cliente. Contiene información como el usuario que realiza la solicitud, el método utilizado (GET o
    POST) y cualquier dato enviado con la solicitud
    :param id: El parámetro `id` es el identificador del registro que necesita ser eliminado de la base
    de datos
    :return: una redirección a la vista 'timetrackpro:registros-insertados' si el usuario tiene
    permisos de administrador, de lo contrario, una redirección a la vista 'timetrackpro:ups' con el
    parámetro 'mensaje' establecido en "No tienes permiso para eliminar el registro seleccionado."
    """

    administrador = esAdministrador(request.user.id)
    if administrador:
        archivoModificado = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=id)[0]
        registros = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id_archivo_leido=archivoModificado)
        # eliminar el fichero de la carpeta de registros insertados
        ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + archivoModificado.ruta
        if os.path.isfile(ruta):
            os.remove(ruta)
        for r in registros:
            r.delete(using='timetrackpro')
        archivoModificado.delete(using='timetrackpro')
        
        return redirect('timetrackpro:registros-insertados')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para eliminar el registro seleccionado.")


@login_required
def eliminarLineaRegistro(request, id):
    """
    The function `eliminarLineaRegistro` deletes a record from a database table and saves the deleted
    record in another table.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the method used (GET or POST),
    and any data sent with the request
    :param id: The `id` parameter is the identifier of the record that needs to be deleted from the
    database
    :return: a redirect to either the 'timetrackpro:ver-registro' view with the 'id' parameter set to
    the id of the 'archivoModificado' object, or a redirect to the 'timetrackpro:ups' view with the
    'mensaje' parameter set to "No tienes permiso para eliminar el registro seleccionado."
    """
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        registro = RegistrosTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
        idRegistroEliminado = registro.id
        idEmpleado = registro.id_empleado
        nombreEmpleado = registro.nombre_empleado
        hora = registro.hora
        maquina = registro.maquina
        remoto = registro.remoto
            
        if registro.id_archivo_leido != None:
            idArchivoLeido = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=registro.id_archivo_leido.id)[0]
        else:
            idArchivoLeido = None
        fechaEliminacion = datetime.now()
        motivo = request.POST.get("motivoEliminacion")
        registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=int(request.POST.get("registradorEliminacion")))[0]

        

        # agrego el registro eliminado a la tabla de registros eliminados
        nuevoRegistroEliminado = RegistrosEliminados(id_registro_eliminado=idRegistroEliminado, id_empleado=idEmpleado, nombre_empleado=nombreEmpleado, hora=hora, maquina=maquina, remoto=remoto, id_archivo_leido=idArchivoLeido, fecha_eliminacion=fechaEliminacion, motivo=motivo, eliminado_por=registrador)
        nuevoRegistroEliminado.save(using='timetrackpro')
        # elimino el registro de la tabla de registros
        registro.delete(using='timetrackpro')

        

        if idArchivoLeido == None:
            return redirect('timetrackpro:registros-remotos-insertados')
        # guardo los datos en un diccionario
        else:
            return redirect('timetrackpro:ver-registro', id=idArchivoLeido.id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para eliminar el registro seleccionado.")

@login_required
def verMisErroresNotificados(request):
    """
    The function "verMisErroresNotificados" renders a template called "mis-errores-notificados.html"
    with some additional information.
    
    :param request: The "request" parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a rendered HTML template called "mis-errores-notificados.html" with the context data
    "infoVista".
    """
        
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": "Mis errores notificados",
    }
    return render(request,"mis-errores-notificados.html",infoVista)

@login_required
def datosMisErroresNotificados(request):
    """
    The function `datosMisErroresNotificados` retrieves error data based on the user's role and returns
    it as a JSON response.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the requested URL, and any data
    sent with the request
    :return: a JSON response containing a list of errors.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    idUsuario = request.user.id
    if administrador or director:
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre')
    else:
        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=idUsuario)[0]
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=idEmpleado).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre')
    
    return JsonResponse(list(errores), safe=False)

@login_required
def verErroresNotificados(request, id=None):
    """
    The function `verErroresNotificados` retrieves a list of notified errors from a database and renders
    them in a template.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :param id: The "id" parameter is an optional parameter that represents the ID of an employee. If the
    "id" parameter is provided, the function will filter the errors based on that employee's ID. If the
    "id" parameter is not provided, the function will retrieve all errors
    :return: a rendered HTML template with the context data "infoVista".
    """
    administrador = esAdministrador(request.user.id)
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "rutaActual": "Errores al fichar notificados",
    }
    return render(request,"errores-registrados.html",infoVista)


@login_required
def verErroresNotificadosPendientes(request):
    """
    The function "verErroresNotificadosPendientes" renders a template called
    "errores-registrados-pendientes.html" with some additional information.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request and any data sent with the request
    :return: a rendered HTML template called "errores-registrados-pendientes.html" with the context
    variable "infoVista".
    """
    administrador = esAdministrador(request.user.id)
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "rutaActual": "Errores notificados pendientes",
    }
    return render(request,"errores-registrados-pendientes.html",infoVista)

@login_required
def datosErroresNotificadosPendientes(request):
    """
    La función `datosErroresNotificadosPendientes` recupera los datos de los errores notificados
    pendientes de revisión y los devuelve como una respuesta JSON.
    :param request: La variable `request` es un objeto que representa la solicitud HTTP realizada por
    el cliente. Contiene información como el usuario que realiza la solicitud, la URL solicitada y
    cualquier dato enviado con la solicitud.
    :return: una respuesta JSON que contiene una lista de errores.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    errores = []
    if administrador or director:
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(estado=estadosErrores['Pendiente']).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado', 'id_empleado__id', 'id_empleado__nombre') 
    else:
        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=idEmpleado, estado=estadosErrores['Pendiente']).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado', 'id_empleado__id', 'id_empleado__nombre')

    # obtengo los festivos registrados en la base de datos

    # devuelvo la lista en formato json
    return JsonResponse(list(errores), safe=False)

@login_required
def notificarErrorEnFichaje(request):
    """
    The function `notificarErrorEnFichaje` is a view function in Django that handles the notification of
    errors in employee time tracking.
    
    :param request: The request object represents the HTTP request that the server receives from the
    client
    :return: a redirect to the 'timetrackpro:ver-errores-notificados' view with the parameter
    'id=idEmpleadoMaquina'.
    """
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(activo=1).values('id', 'nombre')
    administrador = esAdministrador(request.user.id)
    empleadoActual = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados), 
        "empleadoActual": empleadoActual,
        "rutaActual": "Notificar error en fichaje",
    }
    if request.method == 'POST':
        idEmpleadoMaquina = request.POST.get("empleado_maquina")
        empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleadoMaquina)[0]
        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=empleado.id)[0]
        solicitante = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleado.id_usuario.id)[0]

        motivo = request.POST.get("motivoError")
        estado = 1 # indico que aún esta pendiente de revisar
        hora = request.POST.get("hora")
        registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.user.id)[0]
        horaNotificacion = datetime.now()

        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaRegistro> - fecha de registro del problema
        <fechaIncidencia> - fecha en la que se produjo el problema
        <motivo> - motivo del problema
        '''

        '''
        ASUNTO 
        Error en el fichaje manual de <nombreSolicitante> <apellidosSolicitante>

        MENSAJE PARA EL REMITENTE
        Se ha notificado un error en el fichaje manual con fecha <fechaIncidencia>.
        Puede consultar el estado en el siguiente enlace:
        <url>        

        MENSAJE PARA EL DESTINATARIO

        <nombreSolicitante> <apellidosSolicitante> ha notificado un error al fichar manualmente.
        Los detalles del error son los siguientes:

        Empleado: <nombreSolicitante> <apellidosSolicitante>
        Fecha de notificación: <fechaRegistro>
        -------------------------   
        Fecha del error: <fechaIncidencia>
        Motivo: <motivo>
        -------------------------

        Puede consultar más información en el siguiente enlace.
        <url>
        '''

        url = 'http://alerta2.es/private/timetrackpro/ver-errores-notificados/'
        fechaNotificacion = horaNotificacion.strftime("%d-%m-%Y a las %H:%M:%S")
        horaFecha = hora.split("T")[0]
        fechaIncidencia = horaFecha + " " + hora.split("T")[1]

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=47)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace('\n', '').replace('\r', '')
        
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace("<url>", url).replace("<fechaIncidencia>", fechaIncidencia)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=48)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace("<url>", url).replace("<fechaRegistro>", fechaIncidencia).replace("<fechaIncidencia>", fechaNotificacion).replace("<motivo>", motivo)

        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]

        # convertir a direcciones de correo
        if solicitante.email != "" and solicitante.email != None:
            correoEmpleado = convertirAMail(solicitante.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)
        mailSolicitante = [correoEmpleado,]

        nuevoErrorRegistrado = ErroresRegistroNotificados(id_empleado=idEmpleado.id_usuario, hora=hora, motivo=motivo, estado=estado, quien_notifica=registrador, hora_notificacion=horaNotificacion)
        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        enviarTelegram(subject, mensajeDestinatario)
        
        nuevoErrorRegistrado.save(using='timetrackpro')
        return redirect('timetrackpro:ver-errores-notificados', id=idEmpleadoMaquina)   
     
    return render(request,"notificar-error-registro.html", infoVista)



@login_required
def verErrorRegistroNotificado(request, id):
    """
    The function `verErrorRegistroNotificado` checks if the user is an administrator, director, or the
    employee who registered the error, and then renders a template with the error details if they have
    permission, otherwise it redirects to an error page.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the requested URL, and any data
    sent with the request
    :param id: The "id" parameter is the ID of the error notification that you want to view
    :return: either a rendered HTML template with the necessary data or a redirect to another page with
    an error message.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id).values('id','id_empleado','id_empleado__id','id_empleado__id','id_empleado__nombre','id_empleado__apellidos', 'hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica')[0]
    empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").values('id', 'nombre', 'apellidos')
    # compruebo si el empleado que ha notificado el error es el mismo que el que lo ha registrado
    if administrador or director or error['id_empleado__id'] == empleado.id_empleado.id:
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "error":error,
            "empleado":empleado,
            "empleados":empleados,
            "rutaActual": "Error notificado " + str(error['hora'].strftime("%d-%m-%Y")),
            "rutaPrevia": "Errores notificados",
            "urlRutaPrevia": reverse('timetrackpro:ver-errores-notificados')
            #"rutaPreviaUrl": reverse('timetrackpro:ver-errores-notificados', kwargs={'id': error['id_empleado__id']}),
        }
        return render(request,"verErrorNotificado.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver el error seleccionado.")

@login_required
def modificarEstadoErrorRegistroNotificado(request, id):
    """
    The function modifies the error state and rejection reason of a notified registration error, and
    redirects to view the updated error.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data sent with the request
    :param id: The `id` parameter is the unique identifier of the `ErroresRegistroNotificados` object
    that needs to be modified
    :return: a redirect to the 'ver-error-registro-notificado' view with the specified id as a
    parameter.
    """
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    empleadosLaruex  = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=error.id_empleado)[0]
    empleadoMaquina = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=empleadosLaruex.id_empleado.id)[0]
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            motivo = None
            estado = request.POST.get("estado")

            if int(estado) == estadosErrores['Rechazado']:
                motivo = request.POST.get("motivo")
            error.estado = estado
            error.motivo_rechazo = motivo
            error.save(using='timetrackpro')
            
            if int(estado) == estadosErrores['Aceptado']:
                # inserto el registro en la tabla de registros
                motivoModificacion = "Error en el fichaje manual"
                nuevoRegistro = RegistrosTimetrackpro(id_empleado=empleadoMaquina, nombre_empleado=empleadoMaquina.nombre, hora=error.hora, maquina=None, remoto=0, modificado=1, id_archivo_leido=None, motivo_modificacion=motivoModificacion)
                nuevoRegistro.save(using='timetrackpro')
    # guardo los datos en un diccionario
    return redirect('timetrackpro:ver-error-registro-notificado', id=id)

@login_required
def editarErrorRegistroNotificado(request, id):
    """
    The function `editarErrorRegistroNotificado` allows an administrator or director to edit an error in
    the notified registry.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data sent with the request
    :param id: The `id` parameter is the identifier of the error record that needs to be edited
    :return: a redirect to either the 'timetrackpro:ver-error-registro-notificado' view with the
    specified id, or to the 'timetrackpro:ups' view with a message indicating that the user does not
    have permission to edit the selected error.
    """
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        if request.method == 'POST' and administrador:
            error.hora = request.POST.get("hora")
            if request.POST.get("empleadoModificado") != "":

                empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=request.POST.get("empleadoModificado"))[0]
                error.id_empleado = empleado
                error.motivo = request.POST.get("nuevoMotivoError")
            error.save(using='timetrackpro')

        # guardo los datos en un diccionario
        return redirect('timetrackpro:ver-error-registro-notificado', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar el error seleccionado.")

@login_required
def eliminarErrorRegistroNotificado(request, id):
    """
    The function `eliminarErrorRegistroNotificado` deletes an error from the database if the user is an
    administrator, otherwise it redirects to an error page.
    
    :param request: The request object represents the HTTP request that the user made. It contains
    information about the user, the requested URL, and any data that was sent with the request
    :param id: The "id" parameter is the unique identifier of the error to be deleted from the
    "ErroresRegistroNotificados" table in the "timetrackpro" database
    :return: a redirect response. If the user is an administrator, it redirects to the
    'timetrackpro:ver-errores-notificados' URL. If the user is not an administrator, it redirects to the
    'timetrackpro:ups' URL with a message indicating that the user does not have permission to delete
    the selected error.
    """
    administrador = esAdministrador(request.user.id)
    if administrador:
        error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
        error.delete(using='timetrackpro')
        # guardo los datos en un diccionario
        return redirect('timetrackpro:ver-errores-notificados')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para eliminar el error seleccionado.")

def datosErroresNotificados(request, id=None):
    """
    La función `datosErroresNotificados` recupera los datos de los errores notificados de una base de
    datos y los devuelve como una respuesta JSON.

    :param request: El parámetro `request` es un objeto que representa la solicitud HTTP realizada por
    el cliente. Contiene información como el usuario que realiza la solicitud, el método utilizado
    (GET, POST, etc.) y cualquier dato enviado con la solicitud
    :param id: El parámetro "id" es un parámetro opcional que representa el ID de un empleado. Si se
    proporciona el parámetro "id", la función filtrará los errores en función del ID de ese empleado. Si
    no se proporciona el parámetro "id", la función recuperará todos los errores
    :return: una respuesta JSON que contiene una lista de errores.

    """
    # obtengo los festivos registrados en la base de datos
    errores = []
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    if administrador or director:
        if id == None:
            errores = ErroresRegistroNotificados.objects.using("timetrackpro").values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id', 'id_empleado__nombre', 'hora_notificacion', 'hora_modificacion_o_rechazo')
        else:
            errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=id).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado', 'id_empleado__id', 'id_empleado__nombre', 'hora_notificacion', 'hora_modificacion_o_rechazo') 
    else:
        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=idEmpleado.id_usuario).values('id', 'id_empleado', 'hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'id_empleado', 'id_empleado__id', 'id_empleado__nombre', 'quien_notifica__first_name', 'quien_notifica__last_name', 'hora_notificacion', 'hora_modificacion_o_rechazo')
    return JsonResponse(list(errores), safe=False)


def insertarRegistroManual(request):
    """
    The function `insertarRegistroManual` is used to insert a manual record into a database and redirect
    to a specific page.
    
    :param request: The request object represents the HTTP request that the server receives from the
    client. It contains information such as the user making the request, the method used (GET or POST),
    and any data sent with the request
    :return: The code is returning a rendered HTML template with the context data "infoVista".
    """
    administrador = esAdministrador(request.user.id)
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados), 
        "rutaActual": "Insertar registro manual",

    }
    if request.method == 'POST':
        idEmpleado = request.POST.get("idEmpleado")
        hora = request.POST.get("hora")
        maquina = None
        remoto = 0
        idArchivoLeido = None
        fechaLectura = datetime.now()
        insertador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=int(request.POST.get("registrador")))[0]

        nuevoErrorRegistrado = ErroresRegistroNotificados
        nuevoErrorRegistrado.save(using='timetrackpro')
        return redirect('timetrackpro:errores-registrados', id=idEmpleado)   
     
    return render(request,"insertar-registro-diario.html", infoVista)


@login_required
def agregarRegistro(request):
    """
    The function `agregarRegistro` adds a new record to a database table if the user is an administrator
    and redirects to the appropriate page based on the user's role.
    
    :param request: The request object contains information about the current HTTP request, such as the
    user making the request, the method used (GET or POST), and any data submitted with the request
    :return: a redirect response to different views based on the user's role and the request method. If
    the user is an administrator and the request method is POST, it redirects to the 'verRegistro' view
    with the newly created record's ID. If the user is an administrator and the request method is not
    POST, it redirects to the 'registros-insertados' view. If the user
    """
    administrador = esAdministrador(request.user.id)
    director= esDirector(request.user.id)
    if administrador:
        if request.method == 'POST':
            seccion = request.POST.get("seccion")
            mes = request.POST.get("mes")
            year = request.POST.get("year")
            fecha = datetime.now()
            fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
            # compruebo si hay un registro para esa seccion, mes y año
            if RegistrosJornadaInsertados.objects.using("timetrackpro").filter(seccion=seccion, mes=mes, year=year).exists():
                return redirect('timetrackpro:ups', mensaje="Ya existe un registro para esa sección, mes y año.")
            
            nuevoRegistro = RegistrosJornadaInsertados(seccion=seccion, mes=mes, year=year, fecha_lectura=fecha, insertador=AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=int(request.POST.get("registrador")))[0], remoto=0)
            nuevoRegistro.save(using='timetrackpro')

            if request.FILES['archivoSeleccionado']:
                nombreArchivo = mes + "_" + year + "_" + seccion + '_Registro.' + request.FILES['archivoSeleccionado'].name.split('.')[-1]
                ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_NUEVO + nombreArchivo
                subirDocumento(request.FILES['archivoSeleccionado'], ruta)
                nuevoRegistro.ruta = nombreArchivo
                nuevoRegistro.save(using='timetrackpro')
            
            return verRegistro(request, nuevoRegistro.id)
        else:
            return redirect('timetrackpro:registros-insertados')
    elif director:
        return redirect('timetrackpro:registros-insertados')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar un registro.")
        
    


@login_required
def empleados(request):
    """
    The function "empleados" retrieves employee data from a database and renders it in a template for
    display.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a rendered HTML template called "empleados.html" with the data stored in the "infoVista"
    dictionary.
    """
    # obtengo los datos necesarios para la vista
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleados =[]
    if administrador or director:
        empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_auth_user__is_active', 'id_auth_user__is_superuser', 'id_auth_user__is_staff', 'id_auth_user__username', 'id_auth_user__password', 'id_auth_user__last_login', 'id_auth_user__date_joined')
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados),
        "rutaActual": "Usuarios de la aplicación",
    }
    return render(request,"empleados.html",infoVista)


#! AUN NO SE USA datosEmpleados
'''-------------------------------------------
                                Módulo: datosEmpleados

- Descripción: 
Obtener los datos de cada uno de los empleados de Laruex, tanto los registrados en la maquina de control de asistencia como los que no.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def datosEmpleados(request):
    """
    The function "datosEmpleados" retrieves employee data from a database and returns it as a JSON
    response.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a JSON response containing a list of employee data.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleados = []
    if administrador or director:
        empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id','id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_auth_user__is_active', 'id_auth_user__is_superuser', 'id_auth_user__is_staff', 'id_auth_user__username', 'id_auth_user__password', 'id_auth_user__last_login', 'id_auth_user__date_joined')
    return JsonResponse(list(empleados), safe=False)

def agregarUsuario(request):
    """
    The function "agregarUsuario" is used to add a new user to the application, with various fields such
    as name, email, phone number, etc.
    
    :param request: The request object represents the HTTP request that the browser sends to the server.
    It contains information such as the user's session, the HTTP method used (GET or POST), and any data
    submitted with the request
    :return: either a redirect to the "ver-empleado" page with the ID of the newly created user, or a
    redirect to the "ups" page with a message indicating that the user does not have permission to add a
    user.
    """
    
    falta_tarjeta = True
    # obtengo los datos necesarios para la vista
    
    usuariosApp = AuthUserTimeTrackPro.objects.using("timetrackpro").values()
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "usuariosApp":list(usuariosApp),
        "falta_tarjeta":falta_tarjeta, 
        "rutaActual": "Agregar usuario",
        "rutaPrevia": "Usuarios de la aplicación",
        "urlRutaPrevia": reverse('timetrackpro:empleados')
    }
    if administrador:
        if request.method == 'POST':
            idEmpleadoMaquina, nombreEmpleadoMaquina, dniEmpleado, fechaNacimientoEmpleado, nombreEmpleado, apellidosEmpleado, puestoEmpleado, extensionEmpleado, direccionEmpleado, telefonoEmpleado, telefono2Empleado, emailEmpleado, email2Empleado, infoAdicionalEmpleado, userApp, tarjeta= None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            

            idEmpleadoMaquina = request.POST.get("id_empleado_maquina")

            nombreEmpleadoMaquina = request.POST.get("nombre_empleado_maquina")
            nombreEmpleadoMaquina = quitarAcentos(nombreEmpleadoMaquina).upper()
            nombreEmpleadoMaquina = nombreEmpleadoMaquina.replace(" ", "_")

            dniEmpleado = request.POST.get("dni_empleado")
            dniEmpleado = dniEmpleado.upper()
            dniEmpleado = dniEmpleado.replace(" ", "")
            dniEmpleado = dniEmpleado.replace("-", "")
            fechaNacimientoEmpleado = request.POST.get("fechaNacimiento_empleado")
            
            fechaAltaApp = datetime.now()
            fechaAltaApp = fechaAltaApp.strftime("%Y-%m-%d")

            nombreEmpleado = request.POST.get("nombre_empleado")


            apellidosEmpleado = request.POST.get("apellidos_empleado")
            
            puestoEmpleado = request.POST.get("puesto_empleado")
            extensionEmpleado = request.POST.get("extension_empleado")

            direccionEmpleado = request.POST.get("direccion_empleado")
            telefonoEmpleado = request.POST.get("telefono")
            telefono2Empleado = request.POST.get("telefono2")
            emailEmpleado = request.POST.get("email")

            if not "" in request.POST.get("email2"):
                email2Empleado = request.POST.get("email2")

            
            # crear objeto en la tabla Formatos
            infoAdicionalEmpleado = ""
            if request.POST.get("infoAdicional_empleado") is not None:
                infoAdicionalEmpleado = request.POST.get("infoAdicional_empleado")

            nuevoUsuario = None
            if not EmpleadosTimetrackpro.objects.using("timetrackpro").filter(dni__icontains=dniEmpleado).exists():
                nuevoUsuario = EmpleadosTimetrackpro(nombre=nombreEmpleado, apellidos=apellidosEmpleado, puesto=puestoEmpleado, direccion=direccionEmpleado, telefono=telefonoEmpleado, telefono2=telefono2Empleado, email=emailEmpleado, email2=email2Empleado, dni=dniEmpleado, fecha_nacimiento=fechaNacimientoEmpleado, info_adicional=infoAdicionalEmpleado, extension=extensionEmpleado, fecha_alta_app=fechaAltaApp)
                nuevoUsuario.save(using='timetrackpro')

                if request.FILES['fotoEmpleadoSeleccionado']:
                    nombreArchivo = str(nuevoUsuario.id) + '_usuario.' + request.FILES['fotoEmpleadoSeleccionado'].name.split('.')[-1]
                    ruta = settings.STATIC_ROOT + settings.RUTA_USUARIOS_TIMETRACKPRO + nombreArchivo

                    subirDocumento(request.FILES['fotoEmpleadoSeleccionado'], ruta)
                    nuevoUsuario.img = nombreArchivo
                    nuevoUsuario.save(using='timetrackpro')
            else:
                nuevoUsuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(dni__icontains=dniEmpleado)[0]
            return redirect('timetrackpro:ver-empleado', id=nuevoUsuario.id)
        
        else:
            return render(request,"agregar-usuario.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar un usuario.")

@login_required
def usuariosMaquina(request):
    """
    The function "usuariosMaquina" retrieves data about machine users and renders it in a template for
    display.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a rendered HTML template called "usuariosMaquina.html" with the data stored in the
    "infoVista" dictionary.
    """
        # obtengo los datos necesarios para la vista
    administrador = esAdministrador(request.user.id)

    usuariosMaquina = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "usuariosMaquina":list(usuariosMaquina), 
        "rutaActual": "Usuarios de la máquina",
        "rutaPrevia": "Usuarios de la aplicación",
    }
    return render(request,"usuariosMaquina.html",infoVista)

def datosUsuariosMaquina(request):
    """
    The function "datosUsuariosMaquina" retrieves data of users from a machine and returns it as a JSON
    response.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a JSON response containing a list of user data for the "EmpleadosMaquina" model. The user
    data includes fields such as "id", "nombre", "turno", "horas_maxima_contrato", "en_practicas",
    "maquina_laboratorio", "maquina_alerta2", and "maquina_departamento".
    """
    administrador = esAdministrador(request.user.id)
    director =  esDirector(request.user.id)
    usersMaquina=[]
    if administrador or director:
        usersMaquina = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

    return JsonResponse(list(usersMaquina), safe=False)

@login_required
def agregarUsuarioMaquina(request):
    """
    The function "agregarUsuarioMaquina" adds a new user to the system if the current user is an
    administrator or director.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    user. It contains information such as the user's session, the HTTP method used (GET or POST), and
    any data submitted with the request
    :return: a redirect to either the 'timetrackpro:usuarios-maquina' URL or the 'timetrackpro:ups' URL
    with a message if the user does not have permission to add a user.
    """
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        id, nombre, turno, horas_maxima_contrato, en_practicas, maquina_laboratorio, maquina_alerta2, maquina_departamento, numHuellas = None, None, None, None, None, None, None, None, None

        pin, esAdmin, ficharRemoto = 0, 0, 0

        if request.method == 'POST' and administrador:
            id = request.POST.get("id_empleado_maquina")
            nombre = request.POST.get("nombre_empleado_maquina")
            nombre = quitarAcentos(nombre).upper()
            nombre = nombre.replace(" ", "_")
            turno = request.POST.get("turno_empleado_maquina")
            horas_maxima_contrato = request.POST.get("jornada_maxima_empleado")

            en_practicas = request.POST.get('en_practicas')
            if en_practicas == "on":
                en_practicas = 1
            else:
                en_practicas = 0

            maquina_alerta2 = request.POST.get('maquina_alerta2')
            if maquina_alerta2 == "on":
                maquina_alerta2 = 1
            else:
                maquina_alerta2 = 0

            maquina_departamento = request.POST.get('maquina_departamento')
            if maquina_departamento == "on":
                maquina_departamento = 1
            else:
                maquina_departamento = 0

            maquina_laboratorio = request.POST.get('maquina_laboratorio')
            if maquina_laboratorio == "on":
                maquina_laboratorio = 1
            else:
                maquina_laboratorio = 0
            
            pin = 0 
            if request.POST.get('permite_pin') == "on":
                pin = 1

        
            esAdmin=0
            if request.POST.get('es_administrador') == "on":
                esAdmin = 1

            ficharRemoto = 0 
            if request.POST.get('fichar_remoto') == "on":
                ficharRemoto = 1
            
            numHuellas = request.POST.get('huellas_registradas')

            if not EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=request.POST.get("id_empleado_maquina")).exists():
                nuevoUser = EmpleadosMaquinaTimetrackpro(id=id, nombre=nombre, turno=turno, horas_maxima_contrato=horas_maxima_contrato, en_practicas=en_practicas, maquina_laboratorio=maquina_laboratorio, maquina_alerta2=maquina_alerta2, maquina_departamento=maquina_departamento, codigo_fichar=pin, admin_dispositivo=esAdmin, huellas_registradas=numHuellas, fichar_remoto=ficharRemoto, activo=1)
                nuevoUser.save(using='timetrackpro')
            

        return redirect('timetrackpro:usuarios-maquina')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar un usuario.")



def verUsuarioMaquina(request, id):
    '''
    La funcion "verUsuarioMaquina" obtiene los datos de un usuario de la maquina de control de asistencia y los muestra en una plantilla para su visualizacion.

    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del usuario de la maquina que se desea ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verUsuarioMaquina.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # declaro las variables que voy a usar
    idUser, nombre, turno, horas_maxima_contrato, en_practicas, maquina_laboratorio, maquina_alerta2, maquina_departamento, relUser, huellas = None, None, None, None, None, None, None, None, None, None

    pin, esAdmin, ficharRemoto = 0, 0, 0

    # obtengo los datos necesarios para la vista
    
    usuarioMaquina = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    relUser = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=usuarioMaquina)[0]
    
    userLogin = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]

    if administrador or director or (usuarioMaquina.id == userLogin.id_empleado.id):

        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "usuarioMaquina":usuarioMaquina, 
            "relUser":relUser,
            "rutaActual": str(usuarioMaquina.nombre),
            "rutaPrevia": "Usuarios de la máquina",
            "urlRutaPrevia": reverse('timetrackpro:usuarios-maquina')
        }
        if request.method == 'POST':
            idUser = request.POST.get("id_empleado_maquina")
            nombre = request.POST.get("nombre_empleado_maquina")
            nombre = quitarAcentos(nombre).upper()
            nombre = nombre.replace(" ", "_")

            turno = request.POST.get("turno_empleado")
            horas_maxima_contrato = request.POST.get("jornada_maxima_empleado")

            en_practicas = request.POST.get('en_practicas')
            if en_practicas == "on":
                en_practicas = 1
            else:
                en_practicas = 0

            maquina_alerta2 = request.POST.get('maquina_alerta2')
            if maquina_alerta2 == "on":
                maquina_alerta2 = 1
            else:
                maquina_alerta2 = 0

            maquina_departamento = request.POST.get('maquina_departamento')
            if maquina_departamento == "on":
                maquina_departamento = 1
            else:
                maquina_departamento = 0

            maquina_laboratorio = request.POST.get('maquina_laboratorio')
            if maquina_laboratorio == "on":
                maquina_laboratorio = 1
            else:
                maquina_laboratorio = 0
            
            if request.POST.get('permite_pin') == "on":
                pin = 1
            
            if request.POST.get('es_administrador') == "on":
                esAdmin = 1
            
            if request.POST.get('fichar_remoto') == "on":
                ficharRemoto = 1
            
            huellas = request.POST.get('huellas_registradas')


            usuarioMaquina.id = idUser
            usuarioMaquina.nombre = nombre
            usuarioMaquina.turno = turno
            usuarioMaquina.horas_maxima_contrato = horas_maxima_contrato
            usuarioMaquina.en_practicas = en_practicas
            usuarioMaquina.maquina_alerta2 = maquina_alerta2
            usuarioMaquina.maquina_departamento = maquina_departamento
            usuarioMaquina.maquina_laboratorio = maquina_laboratorio
            usuarioMaquina.codigo_fichar = pin
            usuarioMaquina.admin_dispositivo = esAdmin
            usuarioMaquina.fichar_remoto = ficharRemoto
            usuarioMaquina.huellas_registradas = huellas
            
            usuarioMaquina.save(using='timetrackpro')

            return redirect('timetrackpro:ver-usuario-maquina', id=idUser)

        return render(request,"verUsuarioMaquina.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver el usuario de la maquina seleccionado.")




'''-------------------------------------------
                                Módulo: verEmpleado

- Descripción: 
Obtener los datos de un empleado en concreto.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def verEmpleado(request, id):
    '''
    La funcion "verEmpleado" obtiene los datos de un empleado y los muestra en una plantilla para su visualizacion.
    
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del empleado que se desea ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verEmpleado.html" con los datos necesarios para la vista

    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    usuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    idUser = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    if administrador or director or idUser.id_usuario.id == usuario.id:
            # obtengo los datos necesarios para la vista
        
        empleado = None 
        userDjango = None

        usuariosApp = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

        tarjetasAcceso = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).values()


        if RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario).exists():
            empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario)[0]
            if (empleado.id_auth_user != None) and AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=empleado.id_auth_user.id).exists():
                userDjango = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=empleado.id_auth_user.id)[0]

        tarjeta = None
        if TarjetasAcceso.objects.using("timetrackpro").filter(dni=usuario.dni).exists():
            tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(dni=usuario.dni)[0]

        empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre')
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":True, 
            "empleado":empleado,
            "tarjeta":tarjeta,
            "userDjango":userDjango,
            "usuario":usuario,
            "empleados":list(empleados),
            "usuariosApp":list(usuariosApp),
            "tarjetas":list(tarjetasAcceso), 
            "rutaActual": str(usuario.nombre) + " " + str(usuario.apellidos),
            "rutaPrevia": "Usuarios de la aplicación",
            "urlRutaPrevia": reverse('timetrackpro:empleados')
        }
        return render(request,"verEmpleado.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver el empleado seleccionado.")

'''-------------------------------------------
                                Módulo: asociarUsuario

- Descripción: 
Permite asociar las cuentas de los usuarios de la aplicación con los empleados registrados en las máquinas de control de asistencia, ademas de asociar la tarjeta de acceso y la información de la cuenta de django.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def asociarUsuario(request):
    '''
    La funcion "asociarUsuario" permite asociar las cuentas de los usuarios de la aplicacion con los empleados registrados en las maquinas de control de asistencia, ademas de asociar la tarjeta de acceso y la informacion de la cuenta de django.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "asociar-empleados.html" con los datos necesarios para la vista    
    '''
    usuariosApp = EmpleadosTimetrackpro.objects.using("timetrackpro").values()
    administrador = esAdministrador(request.user.id)
    # datos de los empleados registrados en las máquinas de control de asistencia
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values()
    # datos de los empleados registrados en django
    usuariosDjango = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

    tarjetasAcceso = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).values()
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados),
        "usuariosApp":list(usuariosApp),
        "usuariosDjango":list(usuariosDjango),
        "tarjetas":list(tarjetasAcceso),
        "rutaActual": "Asociar usuario",
        "rutaPrevia": "Usuarios de la aplicación",
        "urlRutaPrevia": reverse('timetrackpro:empleados')
    }
    if administrador:
        if request.method == 'POST':
            # obtenemos el identificador del usuario con la información que hay en la aplicación sobre el usuario, este contiene toda la info relevante del usuario
            idUser = request.POST.get("userApp")
            usuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idUser)[0]

            # obtenemos el identificador del empleado, este contiene la información de la máquina de control de asistencia
            idEmpleado = request.POST.get("empleado_maquina")
            empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleado)[0]

            # obtenemos el identificador del usuario de django
            idUserDjango = request.POST.get("usuariosDjango")
            userDjango = None
            if idUserDjango != "0":
                userDjango = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=idUserDjango)[0]

            # obtenemos el identificador de la tarjeta de acceso
            idTarjeta = request.POST.get("tarjeta_empleado")        
            tarjeta = None
            if idTarjeta != "0":
                tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=idTarjeta)[0]
            
            #comprobamos si existe el registro en la tabla RelEmpleadosUsuarios
            if not RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario).exists():
                # creamos el registro en la tabla RelEmpleadosUsuarios
                nuevoRelEmpleadoUsuario = RelEmpleadosUsuarios(id_usuario=usuario, id_empleado=empleado, id_auth_user=userDjango, id_tarjeta_acceso=tarjeta)
                nuevoRelEmpleadoUsuario.save(using='timetrackpro')
            else:
                # si existe, actualizamos el registro
                relEmpleadoUsuario = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario)[0]
                relEmpleadoUsuario.id_empleado = empleado
                relEmpleadoUsuario.id_auth_user = userDjango
                relEmpleadoUsuario.id_tarjeta_acceso = tarjeta
                relEmpleadoUsuario.save(using='timetrackpro')


            return redirect('timetrackpro:ver-empleado', id=idUser)
        else:
            return render(request,"asociar-empleados.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para asociar un usuario.")



'''-------------------------------------------
                                Módulo: editarAsociarUsuario
- Descripción: 
Permite editar las relacion de usario en maquinas de registro, tarjeta de acceso, usuario de django y usuario de la aplicación (datos de contacto del usuario). 
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
-------------------------------------------'''
@login_required
def editarAsociarUsuario(request, id):
    '''
    La funcion "editarAsociarUsuario" permite editar las relacion de usario en maquinas de registro, tarjeta de acceso, usuario de django y usuario de la aplicación (datos de contacto del usuario).
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del usuario de la aplicacion que se desea editar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "editar-asociar-empleados.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if administrador:
        
        relacionActual = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=id).values('id', 'id_usuario', 'id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos','id_empleado', 'id_empleado__id','id_empleado__nombre','id_auth_user', 'id_auth_user__id','id_auth_user__first_name','id_auth_user__last_name', 'id_tarjeta_acceso', 'id_tarjeta_acceso__id', 'id_tarjeta_acceso__nombre', 'id_tarjeta_acceso__apellidos', 'id_tarjeta_acceso__id_tarjeta')[0]
        usuariosApp = EmpleadosTimetrackpro.objects.using("timetrackpro").values()
        # datos de los empleados registrados en las máquinas de control de asistencia
        empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values()
        # datos de los empleados registrados en django
        usuariosDjango = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

        tarjetasAcceso = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).values()

        infoVista = {
            "relacionActual":relacionActual,
            "navBar":navBar,
            "administrador":True,
            "empleados":list(empleados),
            "usuariosApp":list(usuariosApp),
            "usuariosDjango":list(usuariosDjango),
            "tarjetas":list(tarjetasAcceso),
            "rutaActual": "Editar asociación de usuario",
            "rutaPrevia": "Usuarios de la aplicación",
            "urlRutaPrevia": reverse('timetrackpro:empleados')
        }
        if request.method == 'POST':

            # obtenemos el identificador del usuario con la información que hay en la aplicación sobre el usuario, este contiene toda la info relevante del usuario
            idUser = request.POST.get("userApp")
            usuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idUser)[0]

            # obtenemos el identificador del empleado, este contiene la información de la máquina de control de asistencia
            idEmpleado = request.POST.get("empleado_maquina")
            empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleado)[0]

            # obtenemos el identificador del usuario de django
            idUserDjango = request.POST.get("usuariosDjango")
            userDjango = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=idUserDjango)[0]

            # obtenemos el identificador de la tarjeta de acceso
            idTarjeta = request.POST.get("idTarjeta")
            tarjeta = None
            if idTarjeta != "0":
                tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=idTarjeta)[0]
            
            #comprobamos si existe el registro en la tabla RelEmpleadosUsuarios
            if not RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario).exists():
                # creamos el registro en la tabla RelEmpleadosUsuarios
                nuevoRelEmpleadoUsuario = RelEmpleadosUsuarios(id_usuario=usuario, id_empleado=empleado, id_auth_user=userDjango, id_tarjeta_acceso=tarjeta)
                nuevoRelEmpleadoUsuario.save(using='timetrackpro')
            else:
                # si existe, actualizamos el registro
                relEmpleadoUsuario = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario)[0]
                relEmpleadoUsuario.id_empleado = empleado
                relEmpleadoUsuario.id_auth_user = userDjango
                relEmpleadoUsuario.id_tarjeta_acceso = tarjeta
                relEmpleadoUsuario.save(using='timetrackpro')


            return redirect('timetrackpro:ver-empleado', id=idUser)
        else:
            return render(request,"editar-asociar-empleados.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar la asociación del usuario.")


@login_required
def editarEmpleado(request, id):
    '''
    La funcion "editarEmpleado" permite editar los datos de un empleado en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del empleado que se desea editar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "editar-empleado.html" con los datos necesarios para la vista
    '''
    
    usuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario)[0]
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True, 
        "empleado":empleado,
        "rutaActual": "Editar " + str(usuario.nombre) + " " + str(usuario.apellidos),
        "rutaPrevia": "Usuarios de la aplicación",
        "urlRutaPrevia": reverse('timetrackpro:empleados')
    }
    if administrador:
        if request.method == 'POST':
            # EDITAMOS LOS DATOS DEL REGISTRO DE JORNADA 
            empleado.id_empleado.id = request.POST.get("id_empleado_maquina")
            empleado.id_empleado.nombre = request.POST.get("nombre_empleado_maquina")
            empleado.id_empleado.nombre = quitarAcentos(empleado.id_empleado.nombre).upper()
            empleado.id_empleado.nombre = empleado.id_empleado.nombre.replace(" ", "_")
            empleado.id_empleado.turno = request.POST.get("turno_empleado")
            empleado.id_empleado.horas_maxima_contrato = request.POST.get("jornada_maxima_empleado")
            
            en_practicas = request.POST.get('en_practicas')
            if en_practicas == "on":
                empleado.id_empleado.en_practicas = 1
            else:
                empleado.id_empleado.en_practicas = 0

            maquina_alerta2 = request.POST.get('maquina_alerta2')
            if maquina_alerta2 == "on":
                empleado.id_empleado.maquina_alerta2 = 1
            else:
                empleado.id_empleado.maquina_alerta2 = 0

            maquina_departamento = request.POST.get('maquina_departamento')
            if maquina_departamento == "on":
                empleado.id_empleado.maquina_departamento = 1
            else:
                empleado.id_empleado.maquina_departamento = 0

            maquina_laboratorio = request.POST.get('maquina_laboratorio')
            if maquina_laboratorio == "on":
                empleado.id_empleado.maquina_laboratorio = 1
            else:
                empleado.id_empleado.maquina_laboratorio = 0

            empleado.id_empleado.save(using='timetrackpro')

            # EDITAMOS LOS DATOS PERSONALES 
            dniEmpleado = request.POST.get("dni_empleado")
            if dniEmpleado:
                empleado.id_usuario.dni = dniEmpleado

            fechaNacimientoEmpleado = request.POST.get("fechaNacimiento_empleado")
            if fechaNacimientoEmpleado:
                empleado.id_usuario.fecha_nacimiento = fechaNacimientoEmpleado
        
            fechaAltaEmpleado = request.POST.get("fecha_alta_app")
            if fechaAltaEmpleado:
                empleado.id_usuario.fecha_alta_app = fechaAltaEmpleado

        
            nombreEmpleado = request.POST.get("nombre_empleado")
            if nombreEmpleado:
                empleado.id_usuario.nombre = nombreEmpleado
            
            apellidosEmpleado = request.POST.get("apellidos_empleado")
            if apellidosEmpleado:
                empleado.id_usuario.apellidos = apellidosEmpleado

            puestoEmpleado = request.POST.get("puesto_empleado")
            if puestoEmpleado:
                empleado.id_usuario.puesto = puestoEmpleado
            
            extensionEmpleado = request.POST.get("extension_empleado")
            if extensionEmpleado:
                empleado.id_usuario.extension = extensionEmpleado

            direccionEmpleado = request.POST.get("direccion_empleado")
            if direccionEmpleado:
                empleado.id_usuario.direccion = direccionEmpleado
            
            telefonoEmpleado = request.POST.get("telefono")
            if telefonoEmpleado:
                empleado.id_usuario.telefono = telefonoEmpleado

            telefono2Empleado = request.POST.get("telefono2")
            if telefono2Empleado:
                empleado.id_usuario.telefono2 = telefono2Empleado
                
            emailEmpleado = request.POST.get("email")
            if emailEmpleado:
                empleado.id_usuario.email = emailEmpleado
            
            email2Empleado = request.POST.get("email2")
            if email2Empleado:
                empleado.id_usuario.email2 = email2Empleado
            
            infoAdicional = request.POST.get("infoAdicional_empleado")
            if infoAdicional:
                empleado.id_usuario.info_adicional = infoAdicional

            empleado.id_usuario.save(using='timetrackpro')

            # EDITAMOS LOS DATOS DE LA TARJETA DE ACCESO
            idTarjeta = request.POST.get("id_tarjeta")
            if idTarjeta:
                empleado.id_tarjeta_acceso.id_tarjeta = idTarjeta

            fechaAltaTarjeta = request.POST.get("fecha_alta_tarjeta")
            if fechaAltaTarjeta:
                empleado.id_tarjeta_acceso.fecha_alta = fechaAltaTarjeta

            fechaBajaTarjeta = request.POST.get("fecha_baja_tarjeta")
            if fechaBajaTarjeta:
                empleado.id_tarjeta_acceso.fecha_baja = fechaBajaTarjeta

            if dniEmpleado:
                empleado.id_tarjeta_acceso.dni = dniEmpleado

            nombreEmpleadoTarjeta = request.POST.get("nombre_empleado_tarjeta")
            if nombreEmpleadoTarjeta:
                nombreEmpleadoTarjeta.upper()
                empleado.id_tarjeta_acceso.nombre = nombreEmpleadoTarjeta

            apellidosEmpleadoTarjeta = request.POST.get("apellidos_empleado_tarjeta")
            if apellidosEmpleadoTarjeta:
                apellidosEmpleadoTarjeta.upper()
                empleado.id_tarjeta_acceso.apellidos = apellidosEmpleadoTarjeta


            tarjetaActiva = request.POST.get('tarjeta_activa')
            if tarjetaActiva == "on":
                empleado.id_tarjeta_acceso.activo = 1
            else:
                empleado.id_tarjeta_acceso.activo = 0

            acceso_alerta2 = request.POST.get('acceso_alerta2')
            if acceso_alerta2 == "on":
                empleado.id_tarjeta_acceso.acceso_alerta2 = 1
            else:
                empleado.id_tarjeta_acceso.acceso_alerta2 = 0

            acceso_laboratorios = request.POST.get('acceso_laboratorio')
            if acceso_laboratorios == "on":
                empleado.id_tarjeta_acceso.acceso_laboratorios = 1
            else:
                empleado.id_tarjeta_acceso.acceso_laboratorios = 0

            acceso_cpd = request.POST.get('acceso_cpd')
            if acceso_cpd == "on":
                empleado.id_tarjeta_acceso.acceso_cpd = 1
            else:
                empleado.id_tarjeta_acceso.acceso_cpd = 0
            
            return verEmpleado(request, id)

        return render(request,"editar-empleado.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar el empleado seleccionado.")




@login_required
def festivos(request, year=None):
    '''
    La funcion "festivos" obtiene los festivos registrados en la base de datos y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los festivos
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "festivos.html" con los datos necesarios para la vista
    '''
    festivos = None
    administrador = esAdministrador(request.user.id)
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    if year == None:
        year = datetime.now().year

    festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "festivos":list(festivos),
        "year":year, 
        "tipoFestivos":list(tipoFestivos), 
        "rutaActual": "Festivos",
    }
    return render(request,"festivos.html",infoVista)

def datosFestivos(request, year=None):
    """
    The function "datosUsuariosMaquina" retrieves data of users from a machine and returns it as a JSON
    response.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a JSON response containing a list of user data for the "EmpleadosMaquina" model. The user
    data includes fields such as "id", "nombre", "turno", "horas_maxima_contrato", "en_practicas",
    "maquina_laboratorio", "maquina_alerta2", and "maquina_departamento".
    """

    if year == None:
        year = datetime.now().year  
    festivos=[]
    festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')

    return JsonResponse(list(festivos), safe=False)


def datosFestivosCalendario(request, year=None):
    '''
    La funcion "datosFestivosCalendario" obtiene los festivos registrados en la base de datos y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los festivos
    :return: un objeto "JsonResponse" que contiene los datos de los festivos en formato json    
    '''
    # obtengo los festivos registrados en la base de datos
    festivos = []
    if year == None:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
    else:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
    # creo una lista vacía para guardar los datos de los festivos
    salida = []

    # recorro los festivos y los guardo en la lista
    for festivo in festivos:
        # inserto los datos en la lista siguiendo la estructura que requiere el calendario
        salida.append({
            'id':festivo['id'],
            'title':festivo['nombre'],
            'start':festivo['fecha_inicio'],
            'end':festivo['fecha_fin'],
            'color':festivo['tipo_festividad__color_calendario']
        })
    # devuelvo la lista en formato json
    return JsonResponse(salida, safe=False)



@login_required
def agregarJornada(request, year=None):
    '''
    La funcion "agregarJornada" permite agregar una jornada laboral a un empleado en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los festivos
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "jornadas.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        if request.method == 'POST':
            fechaFin = None
            if request.POST.get("fecha_fin") != "":
                fechaFin = request.POST.get("fecha_fin")
            fechaInicio = None
            if request.POST.get("fecha_inicio") != "":
                fechaInicio = request.POST.get("fecha_inicio")
            else:
                fechaInicio = datetime.now().date()
            id_empleado = request.POST.get("empleadoSeleccionado")
            horas = request.POST.get("horas")

            if id_empleado == "0":
                # obtengo todos los empleados
                empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(fecha_baja_app__isnull=True).values()
                for e in empleados:
                    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=e['id'])[0]
                    nuevaJornada = RelJornadaEmpleados(id_empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, horas_semanales=horas)
                    nuevaJornada.save(using='timetrackpro')
            else:
                empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=id_empleado)[0]
                nuevaJornada = RelJornadaEmpleados(id_empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, horas_semanales=horas)
                nuevaJornada.save(using='timetrackpro')
            
            alerta["activa"] = True
            alerta["icono"] = iconosAviso["success"]
            alerta["tipo"] = "success"
            alerta["mensaje"] = "Nueva jornada agregada correctamente."
        return redirect('timetrackpro:jornadas')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar una jornada.")


@login_required
def verJornada(request, id):
    '''
    La funcion "verJornada" obtiene los datos de una jornada laboral en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la jornada laboral que se desea ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-jornada.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    jornada = RelJornadaEmpleados.objects.using("timetrackpro").filter(id=id)[0]
    
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": jornada.id_empleado.nombre + " " + jornada.id_empleado.apellidos,
        "rutaPrevia": "Jornadas",
        "urlRutaPrevia": reverse('timetrackpro:jornadas'),
        "jornada":jornada,
        "administrador":administrador,
    }
    return render(request,"ver-jornada.html",infoVista)

@login_required
def eliminarJornada(request, id):
    '''
    La funcion "eliminarJornada" permite eliminar una jornada laboral en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la jornada laboral que se desea eliminar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "jornadas.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        jornada = RelJornadaEmpleados.objects.using("timetrackpro").filter(id=id)[0]
        jornada.delete(using='timetrackpro')
        return redirect('timetrackpro:jornadas')
    return redirect('timetrackpro:ups', mensaje="No se ha podido eliminar la jornada indicada")


@login_required
def editarJornada(request, id):
    '''
    La funcion "editarJornada" permite editar los datos de una jornada laboral en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la jornada laboral que se desea editar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "editar-jornada.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        jornada = RelJornadaEmpleados.objects.using("timetrackpro").filter(id=id)[0]
        jornada.fecha_inicio = request.POST.get("fecha_inicio")
        if request.POST.get("fecha_fin") != "":
            jornada.fecha_fin = request.POST.get("fecha_fin")
        jornada.horas_semanales = request.POST.get("horas")
        jornada.save(using='timetrackpro')
        return redirect('timetrackpro:ver-jornada', id=id)
    return redirect('timetrackpro:ups', mensaje="No se ha podido modificar la jornada indicada")


@login_required
def datosFestivosVacacionesEmpleado(request):
    '''
    La funcion "datosFestivosVacacionesEmpleado" obtiene los festivos y las vacaciones de un empleado en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :return: un objeto "JsonResponse" que contiene los datos de los festivos y las vacaciones en formato json
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    year = datetime.now().year
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    usuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]
    # obtengo los festivos registrados en la base de datos
    festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
    
    if administrador or director:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado','empleado__nombre','empleado__apellidos', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud')
    else:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=usuario, year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado','empleado__nombre','empleado__apellidos', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud')

    # creo una lista vacía para guardar los datos de los festivos
    salidaFestivos = []

    # recorro los festivos y los guardo en la lista
    for festivo in festivos:
        # inserto los datos en la lista siguiendo la estructura que requiere el calendario
        salidaFestivos.append({
            'id':festivo['id'],
            'title':festivo['nombre'],
            'start':festivo['fecha_inicio'],
            'end':festivo['fecha_fin'],
            'color':festivo['tipo_festividad__color_calendario']
        })
    salidaVacaciones = [] 
    for vacacion in vacaciones:
        salidaVacaciones.append({
            'id':vacacion['id'],
            'title':vacacion['empleado__nombre'] + " " +vacacion['empleado__apellidos'],
            'start':vacacion['fecha_inicio'],
            'end':vacacion['fecha_fin'] + timedelta(days=1),
            'color':vacacion['tipo_vacaciones__color_calendario']
        })

    salida = salidaFestivos + salidaVacaciones
    # devuelvo la lista en formato json
    return JsonResponse(salida, safe=False)

@login_required
def vacacionesSolicitadas(request):
    '''
    La funcion "vacacionesSolicitadas" obtiene las vacaciones solicitadas por un empleado en concreto y las muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "vacaciones-solicitadas.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    mes = str(datetime.now().month)
    year = str(datetime.now().year)
    
    if len(mes) == 1:
        mes = "0" + str(mes)

    diaInicial = "01"
    initialDate = year + "-" + mes + "-" + diaInicial
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "initialDate":initialDate,
        "director":director
    }
    return render(request,"vacaciones-solicitadas.html",infoVista)

@login_required
def datosVacacionesSolicitadas(request, year=None):
    '''
    La funcion "datosVacacionesSolicitadas" obtiene las vacaciones solicitadas por un empleado en concreto y las muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :return: un objeto "JsonResponse" que contiene los datos de las vacaciones en formato json
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if year == None:
        year = datetime.now().year
     # obtengo los datos necesarios para la vista
    vacaciones = []
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]

    if administrador or director:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(estado__in=[9,10,11], year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos', 'dias_habiles_consumidos')
    else:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado.id, estado__in=[9,10,11],year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos', 'dias_habiles_consumidos')
    return JsonResponse(list(vacaciones),safe=False)

def datosCambioVacacionesSolicitadas(request, year=None):
    '''
    La funcion "datosCambioVacacionesSolicitadas" obtiene los cambios de vacaciones solicitados por un empleado en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :return: un objeto "JsonResponse" que contiene los datos de los cambios de vacaciones en formato json
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if year == None:
        year = datetime.now().year
     # obtengo los datos necesarios para la vista
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    usuario = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]

    cambiosVacaciones = []
    if administrador or director:
        cambiosVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(fecha_inicio_actual__year=year, estado__in=[9,10,12]).values('id', 'solicitante', 'solicitante__nombre', 'solicitante__apellidos', 'id_periodo_cambio', 'id_periodo_cambio__tipo_vacaciones', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__tipo_vacaciones__color', 'id_periodo_cambio__tipo_vacaciones__color_calendario', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado', 'motivo_rechazo', 'fecha_solicitud', 'dias_habiles_actuales_consumidos', 'dias_habiles_nuevos_consumidos')
    else:
        cambiosVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(solicitante=usuario, fecha_inicio_actual__year=year, estado__in=[9,10,12]).values('id', 'solicitante', 'solicitante__nombre', 'solicitante__apellidos', 'id_periodo_cambio', 'id_periodo_cambio__tipo_vacaciones', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__tipo_vacaciones__color', 'id_periodo_cambio__tipo_vacaciones__color_calendario', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado', 'motivo_rechazo', 'fecha_solicitud', 'dias_habiles_actuales_consumidos', 'dias_habiles_nuevos_consumidos')
    # creo una lista vacía para guardar los datos de los festivos
    # devuelvo la lista en formato json
    return JsonResponse(list(cambiosVacaciones),safe=False)


@login_required
def datosCalendarioVacacionesSolicitadas(request):
    '''
    La funcion "datosCalendarioVacacionesSolicitadas" obtiene las vacaciones solicitadas por un empleado en concreto y las muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :return: un objeto "JsonResponse" que contiene los datos de las vacaciones en formato json
    '''
    # obtengo los festivos registrados en la base de datos
    festivos = FestivosTimetrackPro.objects.using("timetrackpro").values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')

    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(estado__in=[9,11,12]).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado','empleado__nombre', 'empleado__apellidos','fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud')
    # creo una lista vacía para guardar los datos de los festivos
    salidaFestivos = []

    # recorro los festivos y los guardo en la lista
    for festivo in festivos:
        # inserto los datos en la lista siguiendo la estructura que requiere el calendario
        salidaFestivos.append({
            'id':festivo['id'],
            'title':festivo['nombre'],
            'start':festivo['fecha_inicio'],
            'end':festivo['fecha_fin'],
            'color':festivo['tipo_festividad__color_calendario']
        })
    salidaVacaciones = [] 

    for vacacion in vacaciones:
        salidaVacaciones.append({
            'id':vacacion['id'],
            'title':vacacion['empleado__nombre'] + " " +vacacion['empleado__apellidos'],
            'start':vacacion['fecha_inicio'],
            'end':vacacion['fecha_fin'] + timedelta(days=1),
            'color':vacacion['tipo_vacaciones__color_calendario']
        })
    

    salida = salidaFestivos + salidaVacaciones
    # devuelvo la lista en formato json
    return JsonResponse(salida,safe=False)




'''-------------------------------------------
                                Módulo: calendarioFestivos

- Descripción: 
Permite visualizar el calendario dado un mes y un año concretos, el año es opcional.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Devuelve un listado festivos para ese año y mes concretros

-------------------------------------------'''
@login_required
def calendarioFestivos(request, mes=None, year=None):
    '''
    La funcion "calendarioFestivos" obtiene los festivos registrados en la base de datos y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param mes: El parametro "mes" es el mes del que se quieren obtener los festivos
    :param year: El parametro "year" es el año del que se quieren obtener los festivos
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "calendarioFestivos.html" con los datos necesarios para la vista
    '''
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    administrador = esAdministrador(request.user.id)
    # current_url = request.path[1:]
    if mes == None:
        mes = str(datetime.now().month)
    mesInicial = str(mes)
    if len(mes) == 1:
        mesInicial = "0" + mesInicial
    
    if year == None:
        yearInicial = str(datetime.now().year)
    else:
        yearInicial = str(year)
    diaInicial = "01"

    festivos = []
    if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).exists():
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    
    initialDate = yearInicial + "-" + mesInicial + "-" + diaInicial
    nombreMeses = {
        "01":"Enero",
        "02":"Febrero",
        "03":"Marzo",
        "04":"Abril",
        "05":"Mayo",
        "06":"Junio",
        "07":"Julio",
        "08":"Agosto",
        "09":"Septiembre",
        "10":"Octubre",
        "11":"Noviembre",
        "12":"Diciembre"
    }
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "festivos":list(festivos),
        "initialDate":initialDate,
        "tipoFestivos":list(tipoFestivos), 
        "rutaActual": "Calendario festivos" + " / " + str(yearInicial)  + " / " + nombreMeses[mesInicial],

    }
    return render(request,"calendarioFestivos.html",infoVista)


@login_required
def agregarFestivo(request):
    '''
    La funcion "agregarFestivo" permite agregar un festivo en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "festivos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST':
        nombre = request.POST.get("nombre_festividad")
        idTipo = request.POST.get("tipo_festividad")
        tipo = TipoFestivos.objects.using("timetrackpro").filter(id=idTipo)[0]
        fecha = request.POST.get("fecha_inicio")
        year = request.POST.get("year")

        nuevoFestivo = FestivosTimetrackPro(nombre=nombre, tipo_festividad=tipo, fecha_inicio=fecha, fecha_fin=fecha,year=year)
        nuevoFestivo.save(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=year)    
    # current_url = request.path[1:]

    return redirect('timetrackpro:festivos-year', year=datetime.now().year)

def agregarFestivoCalendario(request):
    '''
    La funcion "agregarFestivoCalendario" permite agregar un festivo en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion,el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "festivos.html" con los datos necesarios para la vista
    '''
    if request.method == 'POST':
        nombre = request.POST.get("nombre_festividad_seleccionada")
        idTipo = request.POST.get("tipo_festividad_seleccionada")
        tipo = TipoFestivos.objects.using("timetrackpro").filter(id=idTipo)[0]
        fecha = request.POST.get("fecha_inicio_seleccionada")
        mes = fecha.split("-")[1]
        year = request.POST.get("year_actual")
        nuevoFestivo = FestivosTimetrackPro(nombre=nombre, tipo_festividad=tipo, fecha_inicio=fecha, fecha_fin=fecha, year=year)
        nuevoFestivo.save(using='timetrackpro')
        return redirect('timetrackpro:calendario-festivos', mes=mes)    
    
    return festivos(request)

    

@login_required
def editarFestivo(request, id):
    '''
    La funcion "editarFestivo" permite editar los datos de un festivo en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion,el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del festivo que se desea editar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "editarFestivo.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(id=id)[0]
    year = str(festivo.year)
    # current_url = request.path[1:]
    
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    if request.method == 'POST' and (administrador or director):
        festivo.nombre = request.POST.get("nombre_festividad_editar")
        idTipo = request.POST.get("tipo_festividad_editar")
        tipo = TipoFestivos.objects.using("timetrackpro").filter(id=idTipo)[0]
        festivo.tipo_festividad = tipo
        festivo.fecha_inicio = request.POST.get("fecha_inicio_editar")
        festivo.fecha_fin = request.POST.get("fecha_inicio_editar")
        if "year_editar" in request.POST and request.POST.get("year_editar") != "":
            festivo.year = request.POST.get("year_editar")
        festivo.save(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=festivo.year)    

    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "tipoFestivos":list(tipoFestivos),
        "festivo":festivo, 
        "rutaActual": "Editar festivo",
        "rutaPrevia": "Festivos",
        "urlRutaPrevia": reverse('timetrackpro:festivos-year', kwargs={'year': year})
    }
    return render(request,"editarFestivo.html", infoVista)

@login_required
def eliminarFestivo(request, id):
    '''
    La funcion "eliminarFestivo" permite eliminar un festivo en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticionel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del festivo que se desea eliminar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "eliminarFestivo.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # current_url = request.path[1:]
    festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(id=id)[0]
    year = festivo.year
    if request.method == 'POST' and (administrador or director):
        year = festivo.year
        festivo.delete(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=year)
    
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "festivo":festivo,
        "tipoFestivos":list(tipoFestivos),
        "rutaActual": "Eliminar festivo",
        "rutaPrevia": "Festivos",
        
        "urlRutaPrevia": reverse('timetrackpro:festivos-year', kwargs={'year': year})
    }
    return render(request,"eliminarFestivo.html",{})



def verVacacionesSeleccionadas(request, id):
    '''
    La funcion "verVacacionesSeleccionadas" obtiene las vacaciones seleccionadas por un empleado en concreto y las muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de las vacaciones que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verVacacionesSeleccionadas.html" con los datos necesarios para la vista

    '''
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'empleado__id','fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos', 'estado__id','estado__nombre','estado')[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=vacaciones["empleado__id"])[0]

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    
    if not administrador and not director and empleado.id != request.user.id:
        return redirect('timetrackpro:sin-permiso')
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "vacaciones":vacaciones,
        "empleado":empleado,
        "rutaActual": "Vacaciones "  + str(vacaciones["empleado__nombre"]) + " " + str(vacaciones["empleado__apellidos"]),
        "rutaPrevia": "Vacaciones solicitadas",
        "urlRutaPrevia": reverse('timetrackpro:solicitar-vacaciones')
    }
    return render(request,"verVacacionesSeleccionadas.html", infoVista)


@login_required
def verVacacionesSeleccionadas(request, id):
    '''
    La funcion "verVacacionesSeleccionadas" obtiene las vacaciones seleccionadas por un empleado en concreto y las muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de las vacaciones que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verVacacionesSeleccionadas.html" con los datos necesarios para la vista
    '''
    
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'empleado__id','fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos', 'estado__id','estado__nombre','estado', 'dias_habiles_consumidos')[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=vacaciones["empleado__id"])[0]

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    
    if not administrador and not director and empleado.id != request.user.id:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver las vacaciones seleccionadas.")
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "vacaciones":vacaciones,
        "empleado":empleado,
        "rutaActual": "Cambio de Vacaciones "  + str(vacaciones["empleado__nombre"]) + " " + str(vacaciones["empleado__apellidos"]),
        "rutaPrevia": "Vacaciones solicitadas",
        "urlRutaPrevia": reverse('timetrackpro:solicitar-vacaciones')
    }
    return render(request,"verVacacionesSeleccionadas.html", infoVista)


@login_required
def verCambioVacacionesSeleccionadas(request, id):
    '''
    La funcion "verCambioVacacionesSeleccionadas" obtiene los cambios de vacaciones seleccionados por un empleado en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de los cambios de vacaciones que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verCambioVacacionesSeleccionadas.html" con los datos necesarios para la vista
    '''
    vacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id).values('id','solicitante', 'solicitante__id', 'solicitante__nombre', 'solicitante__apellidos', 'id_periodo_cambio', 'fecha_inicio_actual' , 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos','motivo_solicitud', 'estado', 'estado__id','motivo_rechazo', 'fecha_solicitud','id_periodo_cambio__tipo_vacaciones__nombre' , 'dias_habiles_actuales_consumidos', 'dias_habiles_nuevos_consumidos', 'id_periodo_cambio__motivo_rechazo')[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=vacaciones["solicitante__id"])[0]

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    
    if not administrador and not director and empleado.id != request.user.id:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver las cambio de vacaciones seleccionado.")
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "vacaciones":vacaciones,
        "empleado":empleado,
        "rutaActual": "Cambio de Vacaciones "  + str(vacaciones["solicitante__nombre"]) + " " + str(vacaciones["solicitante__apellidos"]),
        "rutaPrevia": "Vacaciones solicitadas",
        "urlRutaPrevia": reverse('timetrackpro:solicitar-vacaciones')
    }
    return render(request,"verCambioVacacionesSeleccionadas.html", infoVista)

@login_required
def modificarVacaciones(request, id):
    '''
    La funcion "modificarVacaciones" permite modificar los datos de unas vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de las vacaciones que se desean modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "modificarVacaciones.html" con los datos necesarios para la vista
    '''
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    
    if request.method == 'POST' and administrador:
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        vacaciones.fecha_inicio = fechaInicio
        vacaciones.fecha_fin = fechaFin
        vacaciones.dias_consumidos = request.POST.get("dias_consumidos")
        diasHabilesConsumidos = calcularDiasHabiles(fechaInicio, fechaFin)

        vacaciones.dias_habiles_consumidos = diasHabilesConsumidos
        vacaciones.save(using='timetrackpro')

        return redirect('timetrackpro:ver-vacaciones-seleccionadas', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para modificar las vacaciones seleccionadas.")

@login_required
def cambiarEstadoVacaciones(request, id):
    '''
    La funcion "cambiarEstadoVacaciones" permite cambiar el estado de unas vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de las vacaciones que se desean modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verVacacionesSeleccionadas.html" con los datos necesarios para la vista
    '''

    '''
    <url> - url de la aplicacion
    <fechaInicio> - fecha de inicio del periodo actual
    <fechaFin> - fecha de fin del periodo actual
    <estado> - estado de la solicitud

    ASUNTO 
    Solicitud de vacaciones <estado>.

    MENSAJE PARA EL DESTINATARIO
    Su solicitud de vacaciones para el periodo comprendido entre el <fechaInicio> y el <fechaFin> ha sido <estado>.
    Puede consultar el estado de su solicitud en el siguiente enlace:
    <url>
    '''

    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if request.method == 'POST' and (administrador or director):
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1,id=estado)[0]
        vacaciones.estado = nuevoEstado
        if vacaciones.estado.id == 10:
            motivo = request.POST.get("motivo")
            vacaciones.motivo_estado_solicitud = motivo
        vacaciones.save(using='timetrackpro')
        mailEmpleado = vacaciones.empleado.email
        estadoSolicitud = vacaciones.estado.nombre
        if mailEmpleado != "" and mailEmpleado != None:
            correoEmpleado = convertirAMail(mailEmpleado)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)
        mailSolicitante = [correoEmpleado,]
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=53)[0]
        url = 'http://alerta2.es/private/timetrackpro/ver-vacaciones-seleccionadas/' + str(vacaciones.id) + '/'
        fechaInicio = str(vacaciones.fecha_inicio)
        fechaFin = str(vacaciones.fecha_fin)
        subject = mensajeTipoDestinatario.mensaje.replace("<estado>", estadoSolicitud).replace('\n', '').replace('\r', '')
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<estado>", estadoSolicitud).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)

        send_mail(subject, mensajeDestinatario, email_from, mailSolicitante)

        return redirect('timetrackpro:solicitar-vacaciones')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para cambiar el estado de las vacaciones seleccionadas.")
    
@login_required
def eliminarVacaciones(request):
    '''
    La funcion "eliminarVacaciones" permite eliminar unas vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion 
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitarVacaciones.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            id = request.POST.get("id_vacaciones")
            vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
            vacaciones.delete(using='timetrackpro')
        return redirect('timetrackpro:solicitar-vacaciones')
    else:
        return redirect('timertackpro:ups', mensaje="No tienes permiso para eliminar las vacaciones seleccionadas.")

@login_required
def modificarCambioVacaciones(request, id):
    '''
    La funcion "modificarCambioVacaciones" permite modificar los datos de un cambio de vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del cambio de vacaciones que se desean modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "modificarCambioVacaciones.html" con los datos necesarios para la vista

    '''
    cambioVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    
    if request.method == 'POST' and administrador:
        cambioVacaciones.fecha_inicio_nueva = request.POST.get("fecha_inicio")
        cambioVacaciones.fecha_fin_nueva = request.POST.get("fecha_fin")
        cambioVacaciones.dias_nuevos_consumidos = request.POST.get("dias_consumidos")
        cambioVacaciones.save(using='timetrackpro')

        return redirect('timetrackpro:ver-cambio-vacaciones-seleccionadas', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para modificar el cambio de vacaciones seleccionado.")

@login_required
def cambiarEstadoCambioVacaciones(request, id):
    '''
    La funcion "cambiarEstadoCambioVacaciones" permite cambiar el estado de un cambio de vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del cambio de vacaciones que se desean modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verCambioVacacionesSeleccionadas.html" con los datos necesarios para la vista

    <nombreSolicitante> - nombre del usuario que solicita el cambio
    <apellidosSolicitante> - apellidos del usuario que solicita el cambio
    <url> - url de la aplicacion
    <fechaInicio> - fecha de inicio del periodo actual
    <fechaFin> - fecha de fin del periodo actual
    <estado> - estado de la solicitud

    ASUNTO 
    Solicitud de cambio de vacaciones <estado>.

    MENSAJE PARA EL DESTINATARIO
    Su solicitud de cambio de vacaciones para el periodo comprendido entre el <fechaInicio> y el <fechaFin> ha sido <estado>.
    Puede consultar el estado de la solicitud en el siguiente enlace.
    <url>
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    cambioVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=cambioVacaciones.id_periodo_cambio.id)[0]
    
    estadoPendiente = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1,id=9)[0]

    if request.method == 'POST' and (administrador or director):
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1,id=estado)[0]
        cambioVacaciones.estado = nuevoEstado
        if cambioVacaciones.estado.id == 11:
            vacaciones.fecha_inicio = cambioVacaciones.fecha_inicio_nueva
            vacaciones.fecha_fin = cambioVacaciones.fecha_fin_nueva
            vacaciones.dias_consumidos = cambioVacaciones.dias_nuevos_consumidos
            vacaciones.dias_habiles_consumidos = cambioVacaciones.dias_habiles_nuevos_consumidos
            vacaciones.estado = nuevoEstado
        if cambioVacaciones.estado.id == 10:
            vacaciones.estado = estadoPendiente
            motivo = request.POST.get("motivo")
            cambioVacaciones.motivo_rechazo = motivo
            cambioVacaciones.estado = nuevoEstado
            vacaciones.motivo_rechazo = motivo
        vacaciones.save(using='timetrackpro')

        cambioVacaciones.save(using='timetrackpro')
        mailEmpleado = cambioVacaciones.solicitante.email
        estadoSolicitud = cambioVacaciones.estado.nombre
        if mailEmpleado != "" and mailEmpleado != None:
            correoEmpleado = convertirAMail(mailEmpleado)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)
        mailSolicitante = [correoEmpleado,]
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=55)[0]
        url = 'http://alerta2.es/private/timetrackpro/ver-cambio-vacaciones-seleccionadas/' + str(cambioVacaciones.id) + '/'
        fechaInicio = str(cambioVacaciones.fecha_inicio_nueva)
        fechaFin = str(cambioVacaciones.fecha_fin_nueva)
        subject = mensajeTipoDestinatario.mensaje.replace("<estado>", estadoSolicitud).replace('\n', '').replace('\r', '')
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<estado>", estadoSolicitud).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)

        send_mail(subject, mensajeDestinatario, email_from, mailSolicitante)
        return redirect('timetrackpro:ver-cambio-vacaciones-seleccionadas', id=id)
    else:
        return redirect('timetrackpro:sin-permiso')
    
@login_required
def eliminarCambioVacaciones(request):
    '''
    La funcion "eliminarCambioVacaciones" permite eliminar un cambio de vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitarVacaciones.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            id = request.POST.get("id_vacaciones")
            cambioVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
            cambioVacaciones.delete(using='timetrackpro')
        return redirect('timetrackpro:solicitar-vacaciones')
    else:
        return redirect('timertackpro:ups', mensaje="No tienes permiso para eliminar las vacaciones seleccionadas.")

 
@login_required
def modificarAsuntosPropios(request):
    '''
    La funcion "modificarAsuntosPropios" permite modificar los datos de un asunto propio en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "modificarAsuntosPropios.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        id = request.POST.get("id_asunto")
        asunto = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]
        asunto.fecha_inicio = request.POST.get("fecha_inicio")
        asunto.fecha_fin = request.POST.get("fecha_fin")
        asunto.dias_consumidos = request.POST.get("dias_consumidos")
        sustituto = Sustitutos.objects.using("timetrackpro").filter(id=request.POST.get("sustituto"))[0]         
        asunto.sustituto = sustituto
        asunto.tareas_a_sustituir= request.POST.get("tareas_a_sustituir")
        recuperable = request.POST.get("recuperable")
        asunto.recuperable = recuperable
        if recuperable == "1": 
            asunto.descripcion = request.POST.get("descripcion")
        else:
            asunto.descripcion = None
        asunto.save(using='timetrackpro')

        return redirect('timetrackpro:ver-solicitud-asuntos-propios', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para modificar el asunto propio seleccionado.")
    
@login_required
def cambiarEstadoAsuntosPropios(request, id=None):
    '''
    La funcion "cambiarEstadoAsuntosPropios" permite cambiar el estado de un asunto propio en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verAsuntosPropiosSeleccionados.html" con los datos necesarios para la vista
    '''
    
    '''
    <url> - url de la aplicacion
    <fechaInicio> - fecha de inicio del periodo actual
    <fechaFin> - fecha de fin del periodo actual
    <estado> - estado de la solicitud

    ASUNTO 
    Solicitud de <tipoAsunto> <estado>.

    MENSAJE PARA EL DESTINATARIO
    Su solicitud de <tipoAsunto> para el periodo <fechaInicio> al <fechaFin> ha sido <estado>.
    Puede consultar el estado de la solicitud en el siguiente enlace.
    <url>
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if request.method == 'POST' and (administrador or director):
        if id == None:
            id = request.POST.get("id_asunto")
        asunto = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1, id=estado)[0]
        asunto.estado = nuevoEstado
        if asunto.estado.id == 10:
            motivo = request.POST.get("motivo")
            asunto.motivo_estado_solicitud = motivo
        asunto.save(using='timetrackpro')
        mailEmpleado = asunto.empleado.email
        tipo = "asuntos propios"
        if asunto.recuperable == 1:
            tipo = "asuntos propios recuperables"
        estadoSolicitud = asunto.estado.nombre
        if mailEmpleado != "" and mailEmpleado != None:
            correoEmpleado = convertirAMail(mailEmpleado)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=54)[0]
        url = 'http://alerta2.es/private/timetrackpro/ver-solicitud-asuntos-propios/' + str(asunto.id) + '/'
        fechaInicio = str(asunto.fecha_inicio)
        fechaFin = str(asunto.fecha_fin)
        subject = mensajeTipoDestinatario.mensaje.replace("<estado>", estadoSolicitud).replace("<tipoAsunto>", tipo).replace('\n', '').replace('\r', '')
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<tipoAsunto>", tipo).replace("<estado>", estadoSolicitud)
        send_mail(subject, mensajeDestinatario, email_from, mailSolicitante)

        return redirect('timetrackpro:solicitar-asuntos-propios')
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido cambiar el estado del asunto propio")

@login_required
def eliminarAsuntosPropios(request, id=None):
    '''
    La funcion "eliminarAsuntosPropios" permite eliminar un asunto propio en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitarAsuntosPropios.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if request.method == 'POST' and (administrador or director):
        if id == None:
            id = request.POST.get("id_asunto_eliminar")
        asunto = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]
        asunto.delete(using='timetrackpro')
        return redirect('timetrackpro:solicitar-asuntos-propios')
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido eliminar la solicitud de asuntos propios")

@login_required
def solicitarModificarAsuntosPropios(request):
    '''
    La funcion "solicitarModificarAsuntosPropios" permite solicitar la modificacion de un asunto propio en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitarModificarAsuntosPropios.html" con los datos necesarios para la vista
    '''

    # guardo los datos en un diccionario
    if request.method == 'POST':
        # obtenemos los datos del empleado
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        idEmpleado = user.id_empleado.id
        solicitante = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleado)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
        # obtenemos los datos del formulario
        idAsuntosPropios = request.POST.get("asunto_modificar")
        asuntoPropio = AsuntosPropios.objects.using("timetrackpro").filter(id=idAsuntosPropios)[0]
        estadoPendiente = EstadosSolicitudes.objects.using("timetrackpro").filter(id=12)[0]
        asuntoPropio.estado = estadoPendiente
        asuntoPropio.save(using='timetrackpro')
        fechaInicioActual = asuntoPropio.fecha_inicio
        fechaFinActual = asuntoPropio.fecha_fin
        diasConsumidosActual = asuntoPropio.dias_consumidos
        fechaSolicitud = datetime.now()
        fechaNuevaInicio = request.POST.get("fechaInicioNueva")
        fechaNuevaFin = request.POST.get("fechaFinNueva")
        diasConsumidosNuevos = request.POST.get("dias_nuevos_consumidos")
        motivoCambio = request.POST.get("motivo_cambio")

        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaInicioActual> - fecha de inicio del periodo actual
        <fechaFinActual> - fecha de fin del periodo actual
        <diasConsumidosActual> - dias consumidos en el periodo actual
        <fechaNuevaInicio> - fecha de inicio del nuevo periodo
        <fechaNuevaFin> - fecha de fin del nuevo periodo
        <diasConsumidosNuevos> - dias consumidos en el nuevo periodo
        '''

        '''
        ASUNTO 
        Solicitud de cambio día de asuntos propios <nombreSolicitante> <apellidosSolicitante>.
        
        MENSAJE PARA EL REMITENTE

        Su solicitud de cambio de asuntos propios ha sido registrada con éxito.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>        

        MENSAJE PARA EL DESTINATARIO

        <nombreSolicitante> <apellidosSolicitante> ha solicitado un cambio de asuntos propios cambiado el perido del <fechaInicioActual> al <fechaFinActual> que abarcaba <diasConsumidosActual> día/s por el periodo del <fechaNuevaInicio> al <fechaNuevaFin> que abarca <diasConsumidosNuevos> día/s.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        '''

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=35)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace('\n', '').replace('\r', '')
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace("<url>", "http://alerta2.es/private/timetrackpro/solicitar-asuntos-propios/").replace("<fechaInicioActual>", fechaInicioActual.strftime("%Y-%m-%d")).replace("<fechaFinActual>", fechaFinActual.strftime("%Y-%m-%d")).replace("<diasConsumidosActual>", str(diasConsumidosActual)).replace("<fechaNuevaInicio>", fechaNuevaInicio).replace("<fechaNuevaFin>", fechaNuevaFin).replace("<diasConsumidosNuevos>", diasConsumidosNuevos)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=36)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace("<url>", "http://alerta2.es/private/timetrackpro/solicitar-asuntos-propios/").replace("<fechaInicioActual>", fechaInicioActual.strftime("%Y-%m-%d")).replace("<fechaFinActual>", fechaFinActual.strftime("%Y-%m-%d")).replace("<diasConsumidosActual>", str(diasConsumidosActual)).replace("<fechaNuevaInicio>", fechaNuevaInicio).replace("<fechaNuevaFin>", fechaNuevaFin).replace("<diasConsumidosNuevos>", diasConsumidosNuevos)
        
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]
        # convertir a direcciones de correo
        if solicitante.email != "" and solicitante.email != None:
            correoEmpleado = convertirAMail(solicitante.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]

        solicitudModificacionAsuntosPropios = CambiosAsuntosPropios(id_periodo_cambio=asuntoPropio, solicitante=solicitante, fecha_inicio_actual=fechaInicioActual, fecha_fin_actual=fechaFinActual, dias_actuales_consumidos=diasConsumidosActual, fecha_solicitud=fechaSolicitud, fecha_inicio_nueva=fechaNuevaInicio, fecha_fin_nueva=fechaNuevaFin, dias_nuevos_consumidos=diasConsumidosNuevos, motivo_solicitud=motivoCambio, estado=estado)
        solicitudModificacionAsuntosPropios.save(using='timetrackpro')
        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        enviarTelegram(subject, mensajeDestinatario)
    return redirect('timetrackpro:solicitar-asuntos-propios')


def documentacion(request):
    return render(request,"documentation.html",{})

def perfil(request):
    # current_url = request.path[1:]
    
    return render(request,"profile.html",{"navBar":navBar, })

def dashBoard(request):

    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": "Dashboard Mensual",
        "fechaInicio": datetime.now().strftime("%Y-%m-%d"),
        "fechaFin": datetime.now().strftime("%Y-%m-%d"),
    }
    
    return render(request,"dashboard.html",infoVista)

def tablas(request):        
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"registros-insertados.html",infoVista)


def facturacion(request):
    
    return render(request,"billing.html",{"navBar":navBar})

def realidadVirtual(request):
    
    return render(request,"virtual-reality.html",{"navBar":navBar})

def signIn(request):
    return render(request,"profile.html",{})

def signUp(request):
    return render(request,"sign-up.html",{})

@login_required
def datosListaPermisos(request, year=None):
    '''
    La funcion "datosListaPermisos" obtiene los datos de los permisos de vacaciones de un año en concreto y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos de vacaciones
    :return: un objeto "JsonResponse" que contiene los datos de los permisos de vacaciones en formato json
    '''
    # obtengo los datos necesarios para la vista
    if year == None:
        year = datetime.now().year
    permisos = PermisosVacaciones.objects.using("timetrackpro").filter(year=year).values('id','nombre', 'duracion', 'naturales_o_habiles', 'periodo_antelacion', 'fecha_maxima_solicitud', 'acreditar', 'doc_necesaria', 'legislacion_aplicable', 'bonificable_por_antiguedad', 'bonificacion_por_15_years', 'bonificacion_por_20_years', 'bonificacion_por_25_years', 'bonificacion_por_30_years', 'year', 'es_permiso_retribuido', 'pas', 'pdi')

    # devuelvo la lista en formato json
    return JsonResponse(list(permisos), safe=False)

@login_required
def listaPermisos(request, year=None):
    '''
    La funcion "listaPermisos" obtiene los permisos de vacaciones de un año en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos de vacaciones
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "permisos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if year == None:
        year = datetime.now().year
    # obtengo los datos necesarios para la vista

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "alerta":alerta,
        "rutaActual": "Permisos remunerados "  + str(year),
        "year":year,
    }
    return render(request,"permisos.html", infoVista)

@login_required
def agregarPermiso(request, year=None):
    '''
    La funcion "agregarPermiso" permite agregar un permiso de vacaciones a la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos de vacaciones
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "agregar-permisos.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    # obtengo los datos necesarios para la vista
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
    }
    if administrador or director:
        if request.method == 'POST':
            # obtenemos los datos del formulario
            nombre = request.POST.get("nombre_permiso")
            duracion = request.POST.get("duracion_permiso")
            tipoDias = request.POST.get("tipo_dias")
            fechaLimite = None
            if "fecha_limite_solicitud" in request.POST and request.POST.get("fecha_limite_solicitud") != "":
                fechaLimite = request.POST.get("fecha_limite_solicitud")

            year = None
            if "year_permiso" in request.POST:
                year = request.POST.get("year_permiso")
            
            periodoAntelacion = None
            if "periodo_antelacion" in request.POST:
                periodoAntelacion = request.POST.get("periodo_antelacion")
            
            documentacionJustificativa = None
            if "documentacion_permiso" in request.POST:
                documentacionJustificativa = request.POST.get("documentacion_permiso")
            
            legislacionAplicable = None
            if "legilacion_aplicable" in request.POST:
                legislacionAplicable = request.POST.get("legilacion_aplicable")

            bonificable = request.POST.get("bonificable")
            if bonificable == "on":
                bonificable = 1
            else:
                bonificable = 0

            retribuido = request.POST.get("bonificable")
            if retribuido == "on":
                retribuido = 1
            else:
                retribuido = 0

            pas = request.POST.get("pas")
            if pas == "on":
                pas = 1
            else:
                pas = 0
            
            pdi = request.POST.get("pdi")
            if pdi == "on":
                pdi = 1
            else:
                pdi = 0

            acreditable = request.POST.get("acreditable")
            if acreditable == "on":
                acreditable = 1
            else:
                acreditable = 0

            bonificacion_15, bonificacion_20, bonificacion_25, bonificacion_30 = 0, 0, 0, 0
            if bonificable == 1:
                bonificacion_15 = request.POST.get("bonificacion_15_year")
                bonificacion_20 = request.POST.get("bonificacion_20_year")
                bonificacion_25 = request.POST.get("bonificacion_25_year")
                bonificacion_30 = request.POST.get("bonificacion_30_year")

            # registramos el permiso en la base de datos
            nuevoPermiso = PermisosVacaciones(nombre=nombre, duracion=duracion, naturales_o_habiles=tipoDias, periodo_antelacion=periodoAntelacion, fecha_maxima_solicitud=fechaLimite, acreditar=acreditable, doc_necesaria=documentacionJustificativa, legislacion_aplicable=legislacionAplicable, bonificable_por_antiguedad=bonificable, bonificacion_por_15_years=bonificacion_15, bonificacion_por_20_years=bonificacion_20, bonificacion_por_25_years=bonificacion_25, bonificacion_por_30_years=bonificacion_30, year=year, es_permiso_retribuido=retribuido, pdi=pdi, pas=pas)
            nuevoPermiso.save(using='timetrackpro')
            alerta["activa"] = True
            alerta["icono"] = iconosAviso["success"]
            alerta["tipo"] = "success"
            alerta["mensaje"] = "Permiso agregado correctamente."
            return redirect('timetrackpro:lista-permisos', year=year)
                # return redirect('timetrackpro:permisos', id=nuevoRegistro.id)
        else:
            return render(request,"agregar-permisos.html", infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permisos para agregar un permiso remunerado")

@login_required        
def verPermiso(request, id):
    '''
    La funcion "verPermiso" obtiene los datos de un permiso de vacaciones en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso de vacaciones que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verPermiso.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    permiso = PermisosVacaciones.objects.using("timetrackpro").filter(id=id)[0]
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "permiso":permiso,
    }
    return render(request,"verPermiso.html",infoVista)



def editarPermiso(request):
    '''
    La funcion "editarPermiso" permite editar los datos de un permiso de vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "editarPermiso.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        id = request.POST.get("id_permiso")

        permiso = PermisosVacaciones.objects.using("timetrackpro").filter(id=id)[0]

        # obtenemos los datos del formulario
        permiso.nombre = request.POST.get("nombre_permiso")
        permiso.duracion = request.POST.get("duracion_permiso")
        permiso.naturales_o_habiles = request.POST.get("tipo_dias")
        if "fecha_limite_solicitud" in request.POST and request.POST.get("fecha_limite_solicitud") != "":
            permiso.fecha_maxima_solicitud = request.POST.get("fecha_limite_solicitud")
        
        if "year_permiso" in request.POST:
            permiso.year = request.POST.get("year_permiso")
        
        if "periodo_antelacion" in request.POST:
            permiso.periodo_antelacion = request.POST.get("periodo_antelacion")

        acreditable = request.POST.get("acreditable")
        if acreditable == "on":
            permiso.acreditar = 1
            docPermiso = request.POST.get("documentacion_permiso")
            if docPermiso != "":
                permiso.doc_necesaria = docPermiso
            else:
                permiso.doc_necesaria = "Ninguna"
        else:
            permiso.acreditar = 0
            permiso.doc_necesaria = "Ninguna"       
        
        if "legilacion_aplicable" in request.POST:
            permiso.legislacion_aplicable = request.POST.get("legilacion_aplicable")

        bonificable = request.POST.get("bonificable")
        if bonificable == "on":
            permiso.bonificable_por_antiguedad = 1
            permiso.bonificacion_por_15_years = request.POST.get("bonificacion_15_year")
            permiso.bonificacion_por_20_years = request.POST.get("bonificacion_20_year")
            permiso.bonificacion_por_25_years = request.POST.get("bonificacion_25_year")
            permiso.bonificacion_por_30_years = request.POST.get("bonificacion_30_year")
        else:
            permiso.bonificable_por_antiguedad = 0
            permiso.bonificacion_por_15_years = 0
            permiso.bonificacion_por_20_years = 0
            permiso.bonificacion_por_25_years = 0
            permiso.bonificacion_por_30_years = 0

        retribuido = request.POST.get("retribuido")
        if retribuido == "on":
            permiso.es_permiso_retribuido = 1
        else:
            permiso.es_permiso_retribuido = 0

        pas = request.POST.get("pas")
        if pas == "on":
            permiso.pas = 1
        else:
            permiso.pas = 0

        pdi = request.POST.get("pdi")
        if pdi == "on":
            permiso.pdi = 1
        else:
            permiso.pdi = 0

        permiso.save(using='timetrackpro')
        return redirect('timetrackpro:ver-permiso', id=permiso.id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permisos para editar un permiso remunerado")

@login_required
def eliminarPermiso(request):
    '''
    La funcion "eliminarPermiso" permite eliminar un permiso de vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "permisos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        id = request.POST.get("id_permiso_eliminar")
        permiso = PermisosVacaciones.objects.using("timetrackpro").filter(id=id)[0]
        alerta["activa"] = True
        alerta["icono"] = iconosAviso["success"]
        alerta["tipo"] = "success"
        alerta["mensaje"] = "Permiso con código " + permiso.nombre + " eliminado con éxito."
        permiso.delete(using='timetrackpro')
        return redirect('timetrackpro:lista-permisos')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permisos para eliminar un permiso remunerado")


'''-------------------------------------------
        Permisos retribuidos de empleados
-------------------------------------------'''
@login_required
def datosListaPermisosRetribuidos(request):
    '''
    La funcion "datosListaPermisosRetribuidos" obtiene los datos de los permisos retribuidos de vacaciones y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "JsonResponse" que contiene los datos de los permisos retribuidos de vacaciones en formato json
    '''
    # obtengo los datos necesarios para la vista
    permisos = PermisosRetribuidos.objects.using("timetrackpro").values('id', 'cod_uex', 'nombre', 'tipo__id', 'tipo__nombre', 'dias', 'habiles_o_naturales', 'solicitud_dias_naturales_antelacion', 'pas', 'pdi')

    # devuelvo la lista en formato json
    return JsonResponse(list(permisos), safe=False)

@login_required
def listaPermisosRetribuidos(request):
    '''
    La funcion "listaPermisosRetribuidos" obtiene los permisos retribuidos de vacaciones y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "alerta":alerta,
        "rutaActual": "Permisos reconocidos por la Uex",
    }
    return render(request,"permisos-retribuidos.html", infoVista)

@login_required
def agregarPermisoRetribuido(request, year=None):
    '''
    La funcion "agregarPermisoRetribuido" permite agregar un permiso retribuido a la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos retribuidos de vacaciones
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "agregar-permisos-retribuidos.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        if request.method == 'POST':
            codUex = request.POST.get("cod_uex")
            nombre = request.POST.get("nombre_permiso")
            tipoPermiso = TipoPermisosYAusencias.objects.using("timetrackpro").filter(id=request.POST.get("tipo_permiso"))[0]
            diasConcedidos = request.POST.get("dias_concedidos")
            diasAntelacion = request.POST.get("dias_antelacion")
            
            habiles_o_naturales = "Hábiles"
            if request.POST.get("naturales") == "on":
                habiles_o_naturales = "Naturales"
                

            pas = request.POST.get("pas")
            if pas == "on":
                pas = 1
            else:
                pas = 0
            
            pdi = request.POST.get("pdi")
            if pdi == "on":
                pdi = 1
            else:
                pdi = 0

            # registramos el permiso en la base de datos
            nuevoPermiso = PermisosRetribuidos(cod_uex=codUex, nombre=nombre, tipo=tipoPermiso, dias=diasConcedidos, habiles_o_naturales=habiles_o_naturales, solicitud_dias_naturales_antelacion=diasAntelacion, pas=pas, pdi=pdi)
            nuevoPermiso.save(using='timetrackpro')
            # activar alerta
            alerta["activa"] = True
            alerta["icono"] = iconosAviso["success"]
            alerta["tipo"] = "success"
            alerta["mensaje"] = "Permiso agregado correctamente."
            return redirect('timetrackpro:lista-permisos-retribuidos')
                # return redirect('timetrackpro:permisos', id=nuevoRegistro.id)
        else:
            return redirect('timetrackpro:lista-permisos-retribuidos')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permisos para agregar un permiso retribuido")
   
@login_required
def verPermisoRetribuido(request, id):
    '''
    La funcion "verPermisoRetribuido" obtiene los datos de un permiso retribuido en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-permiso-retribuido.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    permiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=id)[0]
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "permiso":permiso,
        "rutaActual": "Permiso retribuido "  + str(permiso.cod_uex),
        "rutaPrevia": "Permisos reconocidos por la Uex",
        "urlRutaPrevia": reverse('timetrackpro:lista-permisos-retribuidos')
    }
    return render(request,"ver-permiso-retribuido.html",infoVista)

@login_required
def eliminarPermisoRetribuido(request):
    '''
    La funcion "eliminarPermisoRetribuido" permite eliminar un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "permisos-retribuidos.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        id = request.POST.get("id_permiso_eliminar")
        permiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=id)[0]
        solicitudesAsociadas = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id).values()
        for s in solicitudesAsociadas:
            s.delete(using='timetrackpro')
        alerta["activa"] = True
        alerta["icono"] = iconosAviso["success"]
        alerta["tipo"] = "success"
        alerta["mensaje"] = "Permiso con código " + permiso.cod_uex + " eliminado con éxito."
        permiso.delete(using='timetrackpro')

    return redirect('timetrackpro:lista-permisos-retribuidos')



@login_required
def editarPermisoRetribuido(request):
    '''
    La funcion "editarPermisoRetribuido" permite editar los datos de un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "editarPermisoRetribuido.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    
    if request.method == 'POST' and administrador:
        id = request.POST.get("id_permiso")
        permiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=id)[0]
        permiso.cod_uex = request.POST.get("cod_uex")

        tipoPermiso = TipoPermisosYAusencias.objects.using("timetrackpro").filter(id=request.POST.get("tipo_permiso"))[0]
        permiso.tipo = tipoPermiso

        permiso.solicitud_dias_naturales_antelacion = request.POST.get("dias_antelacion")

        permiso.dias = request.POST.get("dias_concedidos")
        naturales = request.POST.get("naturales")
        if naturales == "on":
            permiso.habiles_o_naturales = "Naturales"
        else:
            permiso.habiles_o_naturales = "Hábiles"
 
        if request.POST.get("pas") == "on":
            permiso.pas = 1
        else:
            permiso.pas = 0
        
        if request.POST.get("pdi") == "on":
            permiso.pdi = 1
        else:
            permiso.pdi = 0

        if request.POST.get("nombre_permiso") != "":
            permiso.nombre = request.POST.get("nombre_permiso")

        permiso.save(using='timetrackpro')
        return redirect('timetrackpro:ver-permiso-retribuido', id=permiso.id)
    else:
        return redirect('timetrackpro:lista-permisos-retribuidos')
'''-------------------------------------------
                                Módulo: registroManualControlHorario

- Descripción: 
Permite agregar información necesaria para el registro manual de la jornada laboral de un empleado
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def insertarRegistroManualMensual(request):
    '''
    La funcion "insertarRegistroManualMensual" permite agregar un registro manual de la jornada laboral de un empleado a la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "insertar-registro-mensual.html" con los datos necesarios para la vista
    '''
    festivos = FestivosTimetrackPro.objects.using("timetrackpro").values()
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "festivos":list(festivos), 
        "rutaActual": "Insertar registro mesual",
    }
    return render(request,"insertar-registro-mensual.html",infoVista)

@login_required
def solicitarAsuntosPropios(request, year=None):
    '''
    La funcion "solicitarAsuntosPropios" permite solicitar un asunto propio a la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los asuntos propios
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-asuntos-propios.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").values()
    sustitutos = Sustitutos.objects.using("timetrackpro").values()
    asuntos=[]
    asuntosPropiosEmpleados = []
    diasConsumidos = 0
    if year is None:
        year = str(datetime.now().year)
        yearActual = datetime.now().year

    if administrador or director:
        asuntosPropiosEmpleados = AsuntosPropios.objects.using("timetrackpro").filter(year=yearActual).values()

    asuntos = AsuntosPropios.objects.using("timetrackpro").filter(year=yearActual,empleado=empleado, estado__id=9).values()
    for a in asuntos:
        diasConsumidos += a['dias_consumidos']

    mes = str(datetime.now().month)
    if len(mes) == 1:
        mes = "0" + mes
    initialDate = str(year) + "-" + mes + "-01"
    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        diasConsumidos = request.POST.get("dias_consumidos")
        
        recuperable = 0 
        if request.POST.get("recuperable") == "1":
            recuperable = 1

        tareasASustituir = None
        funciones = ""
        if request.POST.get("tareas_a_sustituir") != "":
            tareasASustituir = request.POST.get("tareas_a_sustituir")
            funciones = tareasASustituir

        descripcion = None
        if request.POST.get("descripcion") != "":
            descripcion = request.POST.get("descripcion")

        empleadoSustituto = request.POST.get("sustituto")

        if empleadoSustituto != "0" and empleadoSustituto != 0:        
            sustituto = Sustitutos.objects.using("timetrackpro").filter(id=empleadoSustituto)[0]
            nombreSustituto = sustituto.nombre + " " + sustituto.apellidos 
    
        else:
            sustituto = None
            nombreSustituto = "Ninguno"    

        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <tipo> - tipo de solicitud asunto propios o asuntos propios recuperables
        <url> - url de la aplicacion
        <fechaInicio> - fecha de inicio del periodo actual
        <fechaFin> - fecha de fin del periodo actual
        <diasConsumidos> - dias consumidos en el periodo actual
        <funciones> - funciones a realizar por el sustituto 
        <sustituto> - nombre del sustituto
        <recuperacion> - si el asunto propio es recuperable o no    
        '''

        '''
        ASUNTO 
        Solicitud de día de <tipo> <nombreSolicitante> <apellidosSolicitante>.
        
        MENSAJE PARA EL REMITENTE
        Su solicitud de <tipo> ha sido registrada con éxito.
        Periodo del <fechaInicio> al <fechaFin> que abarcaba <diasConsumidos> día/s.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        

        MENSAJE PARA EL DESTINATARIO
        <nombreSolicitante> <apellidosSolicitante> ha solicitado <diasConsumidos> día/s de <tipo> desde <fechaInicio> al <fechaFin>.
        <recuperacion>.
        Las funciones a cubir son:
        <funciones>
        La persona que asume la sustitución es:
        <sustituto>
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
               
        '''
        
        url = 'http://alerta2.es/private/timetrackpro/solicitar-asuntos-propios/'
        recuperacion = ""
        tipoAsuntos = "asuntos propios"
        # correo enviado al usuario

        if recuperable == 1:
            tipoAsuntos = "asuntos propios recuperables"
            if descripcion != None:
                recuperacion = "Las horas se recuperarán de la siguiente manera: " + descripcion


        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=37)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<tipo>", tipoAsuntos).replace('\n', '').replace('\r', '')
        
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<diasConsumidos>", diasConsumidos).replace("<tipo>", tipoAsuntos)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=38)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<diasConsumidos>", diasConsumidos).replace("<funciones>", funciones).replace("<sustituto>", nombreSustituto).replace("<recuperacion>", recuperacion).replace("<tipo>", tipoAsuntos)

        # adjuntar el enlace a la aplicacion web


        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]
        # convertir a direcciones de correo
        if empleado.email != "" and empleado.email != None:
            correoEmpleado = convertirAMail(empleado.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]

        if AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin).exists():
            return redirect('timetrackpro:solicitar-asuntos-propios')
        else:
            estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
            fechaSolicitud = datetime.now()
            year = fechaInicio.split("-")[0]
            nuevoAsuntoPropio = AsuntosPropios(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_consumidos=diasConsumidos, estado=estado, fecha_solicitud=fechaSolicitud, year=year, recuperable=recuperable, descripcion=descripcion, tareas_a_sustituir=tareasASustituir, sustituto=sustituto)
            nuevoAsuntoPropio.save(using='timetrackpro')
            send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
            send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
            enviarTelegram(subject, mensajeDestinatario)

            return redirect('timetrackpro:solicitar-asuntos-propios', year=year)
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "empleados":list(empleados),
        "asuntosPropiosEmpleados":list(asuntosPropiosEmpleados),
        "asuntos":list(asuntos),
        "diasConsumidos":diasConsumidos,
        "initialDate":initialDate,
        "currentYear":year,
        "sustitutos":list(sustitutos),
        "rutaActual": "Asuntos propios "  + str(year),
        "rutaPrevia": "Solicitudes",
        "urlRutaPrevia": reverse('timetrackpro:solicitudes'),
    }
    return render(request,"solicitar-asuntos-propios.html",infoVista)

@login_required
def solicitarPermisosRetribuidos(request, year=None):
    '''
    La funcion "solicitarPermisosRetribuidos" permite solicitar un permiso retribuido a la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos retribuidos
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").values()
    sustitutos = Sustitutos.objects.using("timetrackpro").values()
    asuntosPropiosEmpleados = []
    asuntos=[]
    permisosSolicitadosEmpleados = []
    permisosSolicitados = []
    permisos = PermisosRetribuidos.objects.using("timetrackpro").values('id', 'cod_uex', 'nombre', 'tipo__id', 'tipo__nombre', 'dias', 'habiles_o_naturales', 'solicitud_dias_naturales_antelacion', 'pas', 'pdi')
    diasConsumidos = 0
    if year is None:
        year = str(datetime.now().year)
    if administrador or director:
        asuntosPropiosEmpleados = AsuntosPropios.objects.using("timetrackpro").filter(year=year).values()
        permisosSolicitadosEmpleados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year).values()
    if not director:
        asuntos = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado).values()
        permisosSolicitados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year,empleado=empleado).values()
        
        for a in asuntos:
            diasConsumidos += a['dias_consumidos']
    mes = str(datetime.now().month)
    if len(mes) == 1:
        mes = "0" + mes
    initialDate = year + "-" + mes + "-01"
    irDocumentacionUex = settings.IR_DOCUMENTACION_UEX

    
    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        idPermiso = None
        if "id_permiso" in request.POST:
            idPermiso = request.POST.get("id_permiso")
        codigoPermiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=idPermiso)[0]
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        if fechaFin == "":
            fechaFin = fechaInicio
        diasSolicitados = request.POST.get("dias_solicitados")
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=18)[0]
        fechaSolicitud = datetime.now()

        motivoSolicitud = None
        if "motivo_solicitud" in request.POST:
            motivoSolicitud = request.POST.get("motivo_solicitud")

        for p in permisosSolicitados:
            if p['fecha_inicio'] == fechaInicio:
                return redirect('timetrackpro:ups', mensaje='Ya existe un permiso retribuido para el día ' + fechaInicio + '')
            

        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaInicio> - fecha de inicio del periodo actual
        <fechaFin> - fecha de fin del periodo actual
        <diasSolicitados> - dias consumidos en el periodo actual
        <motivo> - motivo de la solicitud
        '''

        '''
        ASUNTO 
        Nueva solicitud de permiso de ausencias <nombreSolicitante> <apellidosSolicitante>.

        MENSAJE PARA EL REMITENTE

        Su solicitud de permisos de ausencias sido registrada con éxito.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>        

        MENSAJE PARA EL DESTINATARIO

        <nombreSolicitante> <apellidosSolicitante> ha solicitado un nuevo permiso de ausencias.
        El motivo de la solicitud es
        <motivo>
        <motivoSolicitud>
        La duración máxima de la solicitud es de <diasDisponibles>.
        El perido solicitado abarca <diasSolicitados> día/s comenzando desde el  <fechaInicio> al <fechaFin>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        '''

        url = 'http://alerta2.es/private/timetrackpro/solicitar-asuntos-propios/'
        motivo = codigoPermiso.nombre
        diasDisponibles = "indefinida"
        if codigoPermiso.dias != None and codigoPermiso.dias != 999:
            diasDisponibles = str(codigoPermiso.dias)  + " día/s " + codigoPermiso.habiles_o_naturales

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=43)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace('\n', '').replace('\r', '')
        
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<diasSolicitados>", diasSolicitados).replace("<motivo>", motivo).replace("<motivoSolicitud>", motivoSolicitud)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=44)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<diasSolicitados>", diasSolicitados).replace("<motivo>", motivo).replace("<motivoSolicitud>", motivoSolicitud).replace("<diasDisponibles>", diasDisponibles)
        
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]

        # convertir a direcciones de correo
        if empleado.email != "" and empleado.email != None:
            correoEmpleado = convertirAMail(empleado.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]

        nuevoPermiso = PermisosYAusenciasSolicitados(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_solicitados=diasSolicitados, estado=estado, fecha_solicitud=fechaSolicitud, year=year, codigo_permiso=codigoPermiso, motivo_solicitud=motivoSolicitud)
        nuevoPermiso.save(using='timetrackpro')
        
        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        enviarTelegram(subject, mensajeDestinatario)
        alerta["activa"] = True
        alerta["icono"] = iconosAviso["success"]
        alerta["tipo"] = "success"
        alerta["mensaje"] = "Permiso agregado correctamente."


        return redirect('timetrackpro:solicitar-permisos-retribuidos', year=year)

    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "empleados":list(empleados),
        "asuntosPropiosEmpleados":list(asuntosPropiosEmpleados),
        "asuntos":list(asuntos),
        "permisosSolicitadosEmpleados":list(permisosSolicitadosEmpleados),
        "permisosSolicitados":list(permisosSolicitados),
        "permisos":list(permisos),
        "diasConsumidos":diasConsumidos,
        "initialDate":initialDate,
        "currentYear":year,
        "sustitutos":list(sustitutos),
        "rutaActual": "Permisos solicitados "  + str(year),
        "rutaPrevia": "Solicitudes",
        "urlRutaPrevia": reverse('timetrackpro:solicitudes'),
        "irDocumentacionUex" : irDocumentacionUex
    }
    return render(request,"solicitar-permisos-retribuidos.html",infoVista)

@login_required
def solicitarPermisoRetribuidoCalendario(request, year=None):
    '''
    La funcion "solicitarPermisoRetribuidoCalendario" permite solicitar un permiso retribuido a la base de datos desde el calendario de la vista "solicitar-permisos-retribuidos.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos retribuidos
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    if request.method == 'POST':
        permisos = PermisosYAusenciasSolicitados.objects.using("timetrackpro").values()
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        idPermiso = request.POST.get("id_permiso")
        codigoPermiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=idPermiso)[0]
        fechaInicio = request.POST.get("fecha_inicio_calendario")
        fechaFin = request.POST.get("fecha_fin_calendario")
        if fechaFin == "":
            fechaFin = fechaInicio
        diasSolicitados = request.POST.get("dias_solicitados_seleccionados")
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=18)[0]
        fechaSolicitud = datetime.now()
        year = fechaInicio.split("-")[0]
        
        for p in permisos:
            if p['fecha_inicio'] == fechaInicio:
                return redirect('timetrackpro:ups', mensaje='Ya existe un permiso retribuido para el día ' + fechaInicio + '')

        motivoSolicitud = None
        if "motivo_solicitud" in request.POST:
            motivoSolicitud = request.POST.get("motivo_solicitud")

        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaInicio> - fecha de inicio del periodo actual
        <fechaFin> - fecha de fin del periodo actual
        <diasSolicitados> - dias consumidos en el periodo actual
        <motivo> - motivo de la solicitud
        '''

        '''
        ASUNTO 
        Nueva solicitud de permiso de ausencias <nombreSolicitante> <apellidosSolicitante>.

        MENSAJE PARA EL REMITENTE

        Su solicitud de permisos de ausencias sido registrada con éxito.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>        

        MENSAJE PARA EL DESTINATARIO

        <nombreSolicitante> <apellidosSolicitante> ha solicitado un nuevo permiso de ausencias.
        El motivo de la solicitud es
        <motivo>
        <motivoSolicitud>
        La duración máxima de la solicitud es de <diasDisponibles>.
        El perido solicitado abarca <diasSolicitados> día/s comenzando desde el  <fechaInicio> al <fechaFin>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        '''

        url = 'http://alerta2.es/private/timetrackpro/solicitar-asuntos-propios/'
        motivo = codigoPermiso.nombre
        diasDisponibles = "indefinida"
        if codigoPermiso.dias != None and codigoPermiso.dias != 999:
            diasDisponibles = str(codigoPermiso.dias)  + " día/s " + codigoPermiso.habiles_o_naturales

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=43)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace('\n', '').replace('\r', '')
        
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<diasSolicitados>", diasSolicitados).replace("<motivo>", motivo).replace("<motivoSolicitud>", motivoSolicitud)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=44)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin).replace("<diasSolicitados>", diasSolicitados).replace("<motivo>", motivo).replace("<motivoSolicitud>", motivoSolicitud).replace("<diasDisponibles>", diasDisponibles)
        
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]

        # convertir a direcciones de correo
        if empleado.email != "" and empleado.email != None:
            correoEmpleado = convertirAMail(empleado.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]


        nuevoPermiso = PermisosYAusenciasSolicitados(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_solicitados=diasSolicitados, estado=estado, fecha_solicitud=fechaSolicitud, year=year, codigo_permiso=codigoPermiso, motivo_solicitud=motivoSolicitud)
        nuevoPermiso.save(using='timetrackpro')
        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        enviarTelegram(subject, mensajeDestinatario)
        alerta["activa"] = True
        alerta["icono"] = iconosAviso["success"]
        alerta["tipo"] = "success"
        alerta["mensaje"] = "Permiso agregado correctamente."
    return redirect('timetrackpro:solicitar-permisos-retribuidos', year=year)

@login_required
def datosAsuntosPropiosEmpleados(request, year=None):
    '''
    La funcion "datosAsuntosPropiosEmpleados" obtiene los datos de los asuntos propios de los empleados y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los asuntos propios
    :return: un objeto "JsonResponse" que contiene los datos de los asuntos propios de los empleados en formato json
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    idUser = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idUser.id_usuario.id)[0]
    diasSolicitados = []
    if year is None:
        year = datetime.now().year

    if administrador or director:
            diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(year=year).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
    else:
        diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(year=year, empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')

    return JsonResponse(list(diasSolicitados), safe=False)


@login_required
def datosAsuntosPropiosSolicitados(request, year=None):
    '''
    La funcion "datosAsuntosPropiosSolicitados" obtiene los datos de los asuntos propios solicitados por un empleado en concreto y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los asuntos propios
    :return: un objeto "JsonResponse" que contiene los datos de los asuntos propios solicitados por un empleado en concreto en formato json
    '''
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    diasSolicitados = []
    if year is None:
        year = datetime.now().year
    diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
    
    return JsonResponse(list(diasSolicitados), safe=False)

@login_required   
def datosPermisosRetribuidosEmpleados(request, year=None):
    '''
    La funcion "datosPermisosRetribuidosEmpleados" obtiene los datos de los permisos retribuidos de vacaciones de los empleados y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos retribuidos de vacaciones
    :return: un objeto "JsonResponse" que contiene los datos de los permisos retribuidos de vacaciones de los empleados en formato json
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    permisosEmpleados = []
    if year is None:
        year = datetime.now().year
    if administrador or director:
        permisosEmpleados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year).values('id', 'empleado__nombre', 'empleado__apellidos', 'empleado', 'year', 'dias_solicitados', 'fecha_solicitud', 'estado__nombre', 'estado__id', 'estado', 'fecha_inicio', 'fecha_fin', 'justificante', 'codigo_permiso__nombre', 'codigo_permiso__id', 'codigo_permiso')
    return JsonResponse(list(permisosEmpleados), safe=False)


@login_required
def datosPermisosRetribuidosSolicitados(request, year=None):
    '''
    La funcion "datosPermisosRetribuidosSolicitados" obtiene los datos de los permisos retribuidos de vacaciones solicitados por un empleado en concreto y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los permisos retribuidos de vacaciones
    :return: un objeto "JsonResponse" que contiene los datos de los permisos retribuidos de vacaciones solicitados por un empleado en concreto en formato json
    '''
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    permisosSolicitados = []
    if year is None:
        year = datetime.now().year

    permisosSolicitados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id', 'empleado__nombre', 'empleado__apellidos', 'empleado', 'year', 'dias_solicitados', 'fecha_solicitud', 'estado__nombre', 'estado__id', 'estado', 'fecha_inicio', 'fecha_fin', 'justificante', 'codigo_permiso__nombre', 'codigo_permiso__id', 'codigo_permiso')
    
    return JsonResponse(list(permisosSolicitados), safe=False)

@login_required
def verSolicitudPermisosRetribuidos(request, id=None):
    '''
    La funcion "verSolicitudPermisosRetribuidos" obtiene los datos de un permiso retribuido en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-solicitud-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if not request.POST:
        alerta['activa'] = False

    if id is not None:
        solicitud = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]    
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=solicitud.empleado.id)[0]
        diasConsumidos = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(empleado=empleado, year=solicitud.year).aggregate(Sum('dias_solicitados'))['dias_solicitados__sum']
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre')
    sustitutos = Sustitutos.objects.using("timetrackpro").values('id', 'nombre', 'apellidos')
    permisos = PermisosRetribuidos.objects.using("timetrackpro").values('id', 'cod_uex', 'nombre', 'tipo__id', 'tipo__nombre', 'dias', 'habiles_o_naturales', 'solicitud_dias_naturales_antelacion', 'pas', 'pdi')
    solicitante = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]

    if solicitud.empleado.id == solicitante.id_usuario.id or director or administrador:
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "director":director,
            "empleados":list(empleados),
            "permisos":list(permisos),
            "solicitud":solicitud, 
            "diasConsumidos":diasConsumidos,
            "sustitutos":list(sustitutos),
            "alerta":alerta,
            "rutaActual":"Solictud de permiso " + str(solicitud.codigo_permiso.cod_uex) + " - " + str(solicitud.codigo_permiso.nombre) ,
            "rutaPrevia":"Permisos solicitados",
            "rutaPrevia2":"Solicitudes",
            "urlRutaPrevia":reverse('timetrackpro:solicitar-permisos-retribuidos'),
            "urlRutaPrevia2":reverse('timetrackpro:solicitudes'),
        }

        return render(request,"ver-solicitud-permisos-retribuidos.html", infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tiene permisos para ver esta solicitud")

@login_required
def cambiarEstadoSolicitudPermisoRetribuido(request, id=None):
    '''
    La funcion "cambiarEstadoSolicitudPermisoRetribuido" permite cambiar el estado de un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido que se desean cambiar el estado
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-solicitud-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if request.method == 'POST' and (administrador or director):
        if id == None:
            id = request.POST.get("id_permiso")
        permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(permisos_retribuidos=1, id=estado)[0]
        permiso.estado = nuevoEstado
        motivo = None
        if permiso.estado.id == 19:
            motivo = request.POST.get("motivo")
        permiso.motivo_estado_solicitud = motivo
        permiso.save(using='timetrackpro')
        nombreEmpleado = permiso.empleado.nombre
        apellidosEmpleado = permiso.empleado.apellidos
        emailEmpleado = permiso.empleado.email
        estado = permiso.estado.nombre
        if emailEmpleado != "" and emailEmpleado != None:
            correoEmpleado = convertirAMail(emailEmpleado)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=52)[0]
        url = 'http://alerta2.es/private/timetrackpro/ver-solicitud-permisos-retribuidos/' + str(permiso.id) + '/'
        fechaInicio = str(permiso.fecha_inicio)
        fechaFin = str(permiso.fecha_fin)
        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaInicio> - fecha de inicio del periodo actual
        <fechaFin> - fecha de fin del periodo actual
        <estado> - estado de la solicitud

        ASUNTO 
        Solicitud de persimos <estado>.

        MENSAJE PARA EL DESTINATARIO
        Su solicitud de permisos de ausencias para el periodo <fechaInicio> al <fechaFin> ha sido <estado>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        '''
        subject = mensajeTipoDestinatario.mensaje.replace("<estado>", estado).replace('\n', '').replace('\r', '')
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", nombreEmpleado).replace("<estado>", estado).replace("<apellidosSolicitante>", apellidosEmpleado).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)

        send_mail(subject, mensajeDestinatario, email_from, mailSolicitante)

        return redirect('timetrackpro:ver-solicitud-permisos-retribuidos', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido cambiar el estado del permiso retribuido")

@login_required
def eliminarSolicitudPermisoRetribuido(request, id=None):
    '''
    La funcion "eliminarSolicitudPermisoRetribuido" permite eliminar un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido que se desean eliminar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        if id == None:
            id = request.POST.get("id_permiso_eliminar")
        permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
        if permiso.justificante != None:
            ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_JUSTIFICANTES + permiso.justificante
            os.remove(ruta)
        permiso.delete(using='timetrackpro')
        return redirect('timetrackpro:solicitar-permisos-retribuidos')
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido eliminar el asunto propio")

@login_required
def justicarSolicitudPermisosRetribuidos(request, id=None):
    '''
    La funcion "justicarSolicitudPermisosRetribuidos" permite justificar un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido que se desean justificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-solicitud-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los datos necesarios para la vista    
    if request.method == 'POST':
        if id == None:
            id = request.POST.get("id_permiso_justificar")

        permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(permisos_retribuidos=1, id=21)[0]
        empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        
        if permiso.empleado.id == empleado.id_usuario.id or director or administrador:
            try: 
                if request.FILES['justificante']:
                    nombreJustificante = str(permiso.id) + '_justificante.' + request.FILES['justificante'].name.split('.')[-1]
                    ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_JUSTIFICANTES + nombreJustificante
                    permiso.justificante = nombreJustificante
                    permiso.save(using='timetrackpro')
                    subirDocumento(request.FILES['justificante'], ruta)
            except:
                print("Error al subir la foto del equipo")
            
            permiso.estado = estado
            permiso.save(using='timetrackpro')

            return redirect('timetrackpro:ver-solicitud-permisos-retribuidos', id=id) 
        else:
            return redirect('timetrackpro:ups', mensaje="No tiene permisos para justificar esta solicitud")

@login_required
def descargarSolicitudPermisosRetribuidos(request, id):
    '''
    La funcion "descargarSolicitudPermisosRetribuidos" permite descargar el justificante de un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido del que se desean descargar el justificante
    :return: un objeto "FileResponse" que contiene el justificante del permiso retribuido en concreto
    '''

    permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
        
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id)

    ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_JUSTIFICANTES + permiso.justificante

    # compruebo si la ruta devuelve algo 
    if os.path.exists(ruta) and (administrador or direccion or request.user.id == permiso.empleado.id):
        return FileResponse(open(ruta, 'rb'))
    else:
        return JsonResponse({'status': 'error', 'message': 'El archivo no esta disponible, compruebe que la ruta y el archivo tengan la misma extensión'})


@login_required
def descargarFicheroMaquina(request, id):
    '''
    La funcion "descargarSolicitudPermisosRetribuidos" permite descargar el justificante de un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido del que se desean descargar el justificante
    :return: un objeto "FileResponse" que contiene el justificante del permiso retribuido en concreto
    '''

    fichero = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=id)[0]
        
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id)

    ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + fichero.ruta

    # compruebo si la ruta devuelve algo 
    if os.path.exists(ruta) and (administrador or direccion):
        return FileResponse(open(ruta, 'rb'))
    else:
        return JsonResponse({'status': 'error', 'message': 'El archivo no esta disponible, compruebe que la ruta y el archivo tengan la misma extensión'})



@login_required
def actualizarJustificanteSolicitudPermisosRetribuidos(request, id):
    '''
    La funcion "actualizarJustificanteSolicitudPermisosRetribuidos" permite actualizar el justificante de un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del permiso retribuido del que se desean actualizar el justificante
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-solicitud-permisos-retribuidos.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id)
    if administrador or direccion:
        permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
        ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_JUSTIFICANTES + permiso.justificante
        rutaOld = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_JUSTIFICANTES + permiso.justificante.split('.')[0] + '_old.' + permiso.justificante.split('.')[-1]

        # si existe el archivo lo renombro 
        if os.path.exists(rutaOld):
            os.remove(rutaOld)
        if os.path.exists(ruta):
            os.rename(ruta, rutaOld)
        permiso.justificante = str(permiso.id) + '_justificante.' + request.FILES["justificante_actualizar"].name.split('.')[-1]
        permiso.save(using='timetrackpro')
        ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_JUSTIFICANTES + permiso.justificante
        subirDocumento(request.FILES["justificante_actualizar"], ruta)

    # compruebo si la ruta devuelve algo 
    if os.path.exists(ruta) and (administrador or direccion or request.user.id == permiso.empleado.id):
        return redirect('timetrackpro:ver-solicitud-permisos-retribuidos', id=id)
    else:
        return JsonResponse({'status': 'error', 'message': 'El archivo no esta disponible, compruebe que la ruta y el archivo tengan la misma extensión'})


@login_required
def modificarSolicitudPermisoRetribuido(request):
    '''
    La funcion "modificarSolicitudPermisoRetribuido" permite modificar un permiso retribuido en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-solicitud-permisos-retribuidos.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    
    if administrador:
        if request.method == 'POST':
            id = request.POST.get("id_solicitu_modificar")
            codigoPermiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=request.POST.get("id_permiso_modificar"))[0]
            permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
            permiso.fecha_inicio = request.POST.get("fecha_inicio")
            permiso.fecha_fin = request.POST.get("fecha_fin")
            permiso.dias_solicitados = request.POST.get("dias_solicitados")
            permiso.codigo_permiso = codigoPermiso
            if request.POST.get("motivoEditar") != "" and request.POST.get("motivoEditar") != None:
                permiso.motivo_estado_solicitud = request.POST.get("motivoEditar")
            if request.POST.get("motivoSolicitud") != "" and request.POST.get("motivoSolicitud") != None:
                permiso.motivo_solicitud = request.POST.get("motivoSolicitud")
            permiso.save(using='timetrackpro')

            return redirect('timetrackpro:ver-solicitud-permisos-retribuidos', id=id)
        return redirect('timetrackpro:solicitar-permisos-retribuidos')
    else:
        return redirect('timetrackpro:sin-permiso')
    

def convertirAMail(correo):
    '''
    La funcion "convertirAMail" permite convertir un correo electronico en un formato valido para enviar un correo electronico.
    :param correo: El parametro "correo" es el correo electronico que se desean convertir
    :return: un objeto "str" que contiene el correo electronico convertido
    '''
    mail = ""
    if correo != "":
        mail = "<" + correo + ">"
    return mail

@login_required
def solicitarVacaciones(request):
    '''
    La funcion "solicitarVacaciones" permite solicitar vacaciones a la base de datos desde la vista "solicitar-vacaciones.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-vacaciones.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    estados = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1).values()
    # obtengo los datos necesarios para la vista
    
    usuario = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=usuario.id_usuario.id)[0]
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    # current_url = request.path[1:]
    mes = str(datetime.now().month)
    if len(mes) == 1:
        mes = "0" + mes
    # The above code is not doing anything. It appears to be incomplete or missing some code.
    year = str(datetime.now().year)
    diaInicial = "01"

    cambios = []
    vacaciones = []
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado, year=int(datetime.now().year)).exists():
        vacacionesEncontradas = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado, year=int(datetime.now().year)).values('id','tipo_vacaciones__nombre', 'year', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'dias_habiles_consumidos', 'estado__nombre', 'estado__id','fecha_solicitud', 'tipo_vacaciones__color')
        for v in vacacionesEncontradas:
            vacaciones.append(v)

    if CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(solicitante=empleado,estado__in=EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1, id__in=(9, 10))).exists():

        cambiosEncontrados = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(solicitante=empleado,estado__in=EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1, id__in=(9, 10)), fecha_inicio_actual__contains=str(datetime.now().year)).values('id', 'solicitante', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__year', 'id_periodo_cambio__fecha_inicio', 'id_periodo_cambio__fecha_fin', 'id_periodo_cambio__dias_consumidos', 'id_periodo_cambio__estado__nombre', 'id_periodo_cambio__estado__id', 'id_periodo_cambio__fecha_solicitud', 'id_periodo_cambio__tipo_vacaciones__color', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado__nombre', 'estado__id', 'motivo_rechazo', 'fecha_solicitud', 'id_periodo_cambio__id')
        for c in cambiosEncontrados:
            cambios.append(c)

    festivos = []
    if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).exists():
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'year')
    
    initialDate = year + "-" + mes + "-" + diaInicial
    navidad = False
    vacacionesExcluidos = []
    periodosVacaciones = []
    if gastadasVacacionesNavidad(empleado, year) != 0:
        navidad = True
        vacacionesExcluidos.append(1)
    semanaSanta = False
    if gastadasVacacionesSemanaSanta(empleado, year) != 0:
        semanaSanta = True
        vacacionesExcluidos.append(2)

    periodosVacaciones = TipoVacaciones.objects.using("timetrackpro").exclude(id__in=vacacionesExcluidos).values()


    
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "festivos":list(festivos),
        "initialDate":initialDate,
        "tipoFestivos":list(tipoFestivos),
        "usuario":usuario,
        "estados":list(estados),
        "periodosVacaciones":list(periodosVacaciones),
        "vacaciones":vacaciones,
        "cambios":cambios, 
        "rutaActual":"Solicitud de Vacaciones" + " " + str(datetime.now().year),
        "rutaPrevia":"Solicitudes",
        "urlRutaPrevia":reverse('timetrackpro:solicitudes'),
        "navidad":navidad,
        "semanaSanta":semanaSanta,
        "director":director,
    }

    if request.method == 'POST':

        # obtenemos los datos del empleado
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]

        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]

        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
        # obtenemos los datos del formulario
        tipoVacaciones = TipoVacaciones.objects.using("timetrackpro").filter(id=request.POST.get("tipo_dias"))[0]
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        diasConsumidos = request.POST.get("dias_consumidos")
        diasHabilesConsumidos = calcularDiasHabiles(fechaInicio, fechaFin)
        fechaSolicitud = datetime.now()
    
        year = fechaInicio.split("-")[0]

        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaInicio> - fecha de inicio del periodo actual
        <fechaFin> - fecha de fin del periodo actual
        '''

        '''
        ASUNTO 
        Solicitud de vacaciones <nombreSolicitante> <apellidosSolicitante>.

        MENSAJE PARA EL REMITENTE
        Su solicitud de vacaciones ha sido registrada con éxito.
        El periodo seleccionado comienza el <fechaInicio> y finaliza el <fechaFin>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        

        MENSAJE PARA EL DESTINATARIO
        <nombreSolicitante> <apellidosSolicitante> ha registrado una solicitud de vacaciones para el periodo del <fechaInicio> al <fechaFin>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
               
        '''
        url = 'http://alerta2.es/private/timetrackpro/solicitar-vacaciones/'
        # correo enviado al usuario

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=39)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace('\n', '').replace('\r', '')


        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=40)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)

        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]
        # convertir a direcciones de correo
        if empleado.email != "" and empleado.email != None:
            correoEmpleado = convertirAMail(empleado.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]
        # compruebo si ya existe un registro de vacaciones para ese periodo 
        if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio=fechaInicio).exists():
            return redirect('timetrackpro:ups', mensaje="Parece que ya existe una solicitud de vacaciones para esas fechas.")
        else:
            nuevoRegistroVacaciones = VacacionesTimetrackpro(empleado=empleado, tipo_vacaciones=tipoVacaciones, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_consumidos=diasConsumidos, fecha_solicitud=fechaSolicitud, year=year, estado=estado,dias_habiles_consumidos=diasHabilesConsumidos)
            nuevoRegistroVacaciones.save(using='timetrackpro')

            send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
            send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
            enviarTelegram(subject, mensajeDestinatario)
            
            return redirect('timetrackpro:solicitar-vacaciones')   
    
    return render(request,"solicitarVacaciones.html", infoVista)



@login_required
def solicitarModificarVacaciones(request):
    '''
    La funcion "solicitarModificarVacaciones" permite solicitar modificar un periodo de vacaciones a la base de datos desde la vista "solicitar-vacaciones.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-vacaciones.html" con los datos necesarios para la vista
    '''
    # guardo los datos en un diccionario
    if request.method == 'POST':
        #obtengo el id del usuario autenticado 
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        idEmpleado = user.id_usuario.id
        solicitante = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleado)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
        # obtenemos los datos del formulario
        idVacaciones = request.POST.get("vacaciones_modificar")
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=idVacaciones)[0]
        estadoPendiente = EstadosSolicitudes.objects.using("timetrackpro").filter(id=12)[0]
        vacaciones.estado = estadoPendiente
        vacaciones.save(using='timetrackpro')
        fechaInicioActual = request.POST.get("fechaActualInicio")
        fechaFinActual = request.POST.get("fechaActualFin")
        diasConsumidosActual = vacaciones.dias_consumidos
        diasHabilesConsumidosActual = vacaciones.dias_habiles_consumidos

        fechaSolicitud = datetime.now()
        fechaNuevaInicio = request.POST.get("fechaInicioNueva")
        fechaNuevaFin = request.POST.get("fechaFinNueva")
        diasConsumidosNuevos = request.POST.get("dias_nuevos_consumidos")
        diasHabilesConsumidosNuevos = calcularDiasHabiles(fechaNuevaInicio, fechaNuevaFin)
        motivoCambio = request.POST.get("motivo_cambio")


        '''
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaInicioActual> - fecha de inicio del periodo actual
        <fechaFinActual> - fecha de fin del periodo actual
        <fechaNuevaInicio> - fecha de inicio del periodo nuevo
        <fechaNuevaFin> - fecha de fin del periodo nuevo
        '''

        '''
        ASUNTO 
        Solicitud de cambio periodo de vacaciones <nombreSolicitante> <apellidosSolicitante>.

        MENSAJE PARA EL REMITENTE
        Su solicitud de cambio del periodo de vacaciones ha sido registrada con éxito.
        El periodo actual comienza el <fechaInicioActual> y finaliza el <fechaFinActual>.
        El nuevo periodo comienza el <fechaNuevaInicio> y finaliza el <fechaNuevaFin>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>

        MENSAJE PARA EL DESTINATARIO
        <nombreSolicitante> <apellidosSolicitante> ha registrado una solicitud de cambio de vacaciones modificando el periodo actual del <fechaInicioActual> al <fechaFinActual> por el perido desde el <fechaNuevaInicio> al <fechaNuevaFin>.
        Puede consultar el estado de la solicitud en el siguiente enlace.
        <url>
        '''


        url = 'http://alerta2.es/private/timetrackpro/solicitar-vacaciones/'

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=41)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace('\n', '').replace('\r', '')


        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace("<url>", url).replace("<fechaInicioActual>", fechaInicioActual).replace("<fechaFinActual>", fechaFinActual).replace("<fechaNuevaInicio>", fechaNuevaInicio).replace("<fechaNuevaFin>", fechaNuevaFin)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=42)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", solicitante.nombre).replace("<apellidosSolicitante>", solicitante.apellidos).replace("<url>", url).replace("<fechaInicioActual>", fechaInicioActual).replace("<fechaFinActual>", fechaFinActual).replace("<fechaNuevaInicio>", fechaNuevaInicio).replace("<fechaNuevaFin>", fechaNuevaFin)

        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]
        # convertir a direcciones de correo

        if solicitante.email != "" and solicitante.email != None:
            correoEmpleado = convertirAMail(solicitante.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]

        solicitudModificacionVacaciones = CambiosVacacionesTimetrackpro(id_periodo_cambio=vacaciones, solicitante=solicitante, fecha_inicio_actual=fechaInicioActual, fecha_fin_actual=fechaFinActual, dias_actuales_consumidos=diasConsumidosActual, dias_habiles_actuales_consumidos=diasHabilesConsumidosActual, fecha_solicitud=fechaSolicitud, fecha_inicio_nueva=fechaNuevaInicio, fecha_fin_nueva=fechaNuevaFin, dias_nuevos_consumidos=diasConsumidosNuevos, motivo_solicitud=motivoCambio, estado=estado, dias_habiles_nuevos_consumidos=diasHabilesConsumidosNuevos)
        solicitudModificacionVacaciones.save(using='timetrackpro')

        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        enviarTelegram(subject, mensajeDestinatario)
    return redirect('timetrackpro:solicitar-vacaciones')

@login_required
def solicitudes(request):
    '''
    La funcion "solicitudes" permite mostrar las solicitudes de vacaciones, asuntos propios y permisos retribuidos de un empleado en concreto en la vista "solicitudes.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitudes.html" con los datos necesarios para la vista
    '''
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "rutaActual":"Solicitudes",
        "administrador":esAdministrador(request.user.id),
        "director":esDirector(request.user.id),
    }
    return render(request,"solicitudes.html", infoVista)


@login_required
def verSolicitudAsuntosPropios(request, id=None):
    '''
    La funcion "verSolicitudAsuntosPropios" obtiene los datos de un asunto propio en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del asunto propio que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-solicitud-asuntos-propios.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if id is not None:
        solicitud = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]    
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=solicitud.empleado.id)[0]
        diasConsumidos = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, year=solicitud.year).aggregate(Sum('dias_consumidos'))['dias_consumidos__sum']
        empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre')
        sustitutos = Sustitutos.objects.using("timetrackpro").values('id', 'nombre', 'apellidos')
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "director":director,
            "empleados":list(empleados),
            "solicitud":solicitud, 
            "diasConsumidos":diasConsumidos,
            "sustitutos":list(sustitutos),
            "rutaActual":"Solicitud de Asuntos Propios " + solicitud.fecha_inicio.strftime("%d") + " al " + solicitud.fecha_fin.strftime("%d de %m de %Y"),
            "rutaPrevia":"Asuntos Propios",
            "urlRutaPrevia":reverse('timetrackpro:solicitar-asuntos-propios'),
            "rutaPrevia2":"Solicitudes",
            "urlRutaPrevia2":reverse('timetrackpro:solicitudes'),
        }

        return render(request,"ver-solicitud-asuntos-propios.html", infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="Ups. Algo no se ha podido acceder a la solicitud de asuntos propios")


@login_required
def datosCalendarioAsuntosPropios(request, year=None):
    '''
    La funcion "datosCalendarioAsuntosPropios" obtiene los datos de los asuntos propios de un empleado en concreto y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los asuntos propios
    :return: un objeto "JsonResponse" que contiene los datos de los asuntos propios de un empleado en concreto en formato json
    '''

    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los festivos registrados en la base de datos
    festivos = []
    salidaFestivos = []
    if year == None:
        year = datetime.now().year

    festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'year', 'tipo_festividad__color_calendario')
    # recorro los festivos y los guardo en la lista
    for festivo in festivos:
        # inserto los datos en la lista siguiendo la estructura que requiere el calendario
        salidaFestivos.append({
            'id':festivo['id'],
            'title':festivo['nombre'],
            'start':festivo['fecha_inicio'],
            'end':festivo['fecha_inicio'],
            'color':festivo['tipo_festividad__color_calendario']
        })
    asuntosPropios = []
    salidaAsuntosPropios = []
    salidaPermisos = []
    estadosAsuntos = [9,11,12]
    if not admin and not director:
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
        asuntosPropios = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado,estado__in=estadosAsuntos).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
        permisosSocilicitados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_solicitados','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'codigo_permiso__nombre', 'codigo_permiso__cod_uex', 'justificante')
        # recorro los festivos y los guardo en la lista
        for asunto in asuntosPropios:
            # inserto los datos en la lista siguiendo la estructura que requiere el calendario
            salidaAsuntosPropios.append({
                'id':asunto['id'],
                'title':asunto['empleado__nombre'] + " " + asunto['empleado__apellidos'],
                'start':asunto['fecha_inicio'],
                'end':asunto['fecha_fin'] + timedelta(days=1),
                'color':'#555555',
                'textColor':'#fff', 
                'borderColor':'#555555'
            })
        for p in permisosSocilicitados:
            # inserto los datos en la lista siguiendo la estructura que requiere el calendario

            salidaPermisos.append({
                'id':p['id'],
                'title':p['empleado__nombre'] + " " + p['empleado__apellidos'],
                'start':p['fecha_inicio'],
                'end':p['fecha_fin'] + timedelta(days=1),
                'textColor':'#555555', 
                'borderColor':'#555555',
                'color':'#fff',
            })
    else:
        asuntosPropios = AsuntosPropios.objects.using("timetrackpro").filter(year=year, estado__in=estadosAsuntos).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin')
        permisosSolicitados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_solicitados','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'codigo_permiso__nombre', 'codigo_permiso__cod_uex', 'justificante')
        # recorro los festivos y los guardo en la lista
        for asunto in asuntosPropios:
            # sumar un día a la fecha de fin
            # inserto los datos en la lista siguiendo la estructura que requiere el calendario
            salidaAsuntosPropios.append({
                'id':asunto['id'],
                'title':asunto['empleado__nombre'] + " " + asunto['empleado__apellidos'],
                'start':asunto['fecha_inicio'],
                'end':asunto['fecha_fin'] + timedelta(days=1),
                'color':'#555555',
                'textColor':'#fff', 
                'borderColor':'#555555'
            })
        for p in permisosSolicitados:
            # inserto los datos en la lista siguiendo la estructura que requiere el calendario
            salidaPermisos.append({
                'id':p['id'],
                'title':p['empleado__nombre'] + " " + p['empleado__apellidos'],
                'start':p['fecha_inicio'],
                'end':p['fecha_fin'] + timedelta(days=1),
                'textColor':'#555555', 
                'borderColor':'#555555',
                'color':'#fff',
            })
    
    # creo una lista vacía para guardar los datos de los festivos
    salida = salidaFestivos + salidaAsuntosPropios + salidaPermisos
    # devuelvo la lista en formato json
    return JsonResponse(salida, safe=False)


@login_required
def agregarAsuntosPropiosCalendario(request):
    '''
    La funcion "agregarAsuntosPropiosCalendario" permite agregar un asunto propio a la base de datos desde la vista "solicitar-asuntos-propios.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-asuntos-propios.html" con los datos necesarios para la vista
    '''

    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        fechaInicio = request.POST.get("fecha_inicio_seleccionada")
        fechaFin = request.POST.get("fecha_fin_seleccionada")
        diasConsumidos = request.POST.get("dias_seleccionados_consumidos")
        
        recuperable = 0 
        if request.POST.get("recuperable_calendario") == 1:
            recuperable = 1

        tareasASustituir = None
        if request.POST.get("tareas_a_sustituir_calendario") != "":
            tareasASustituir = request.POST.get("tareas_a_sustituir_calendario")

        descripcion = None
        if request.POST.get("descripcion_calendario") != "":
            descripcion = request.POST.get("descripcion_calendario")

        empleadoSustituto = request.POST.get("sustituto_calendario")
        if empleadoSustituto != "0" and empleadoSustituto != 0:       
            sustituto = Sustitutos.objects.using("timetrackpro").filter(id=empleadoSustituto)[0] 
        else:
            sustituto = None

        if AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin).exists():
            return redirect('timetrackpro:solicitar-asuntos-propios')
        else:
            estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
            fechaSolicitud = datetime.now()
            year = request.POST.get("year_actual")
            nuevoAsuntoPropio = AsuntosPropios(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_consumidos=diasConsumidos, estado=estado, fecha_solicitud=fechaSolicitud, year=year, recuperable=recuperable, descripcion=descripcion, tareas_a_sustituir=tareasASustituir, sustituto=sustituto)
            nuevoAsuntoPropio.save(using='timetrackpro')
            return redirect('timetrackpro:solicitar-asuntos-propios', year=year)
 
    return solicitarAsuntosPropios(request)


def notificarIncidencias(request):
    '''
    La funcion "notificarIncidencias" permite notificar una incidencia a la base de datos desde la vista "notificar-incidencias.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "notificar-incidencias.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
    }
    if request.method == 'POST':
        idEmpleadoMaquina = request.POST.get("idEmpleadoMaquina")
        empleado = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").filter(id=idEmpleadoMaquina)[0]
        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=empleado)[0]
        motivo = request.POST.get("motivoError")
        estado = 1 # indico que aún esta pendiente de revisar
        hora = request.POST.get("hora")
        registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.POST.get("idEmpleado"))[0]
        horaNotificacion = datetime.now()
        nuevoErrorRegistrado = ErroresRegistroNotificados(id_empleado=idEmpleado, hora=hora, motivo=motivo, estado=estado, quien_notifica=registrador, hora_notificacion=horaNotificacion)
        nuevoErrorRegistrado.save(using='timetrackpro')
        return redirect('timetrackpro:ver-errores-notificados', id=idEmpleadoMaquina)   
     
    return render(request,"notificar-incidencia.html", infoVista)





@login_required
def notificarProblemas(request):
    '''
    La funcion "notificarProblemas" permite notificar un problema a la base de datos desde la vista "notificar-problemas.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "notificar-problemas.html" con los datos necesarios para la vista
    '''    
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "rutaActual": "Notificar problemas",
    }
     
    return render(request,"notificar-problemas.html", infoVista)



@login_required
def notificarDatosErroneos(request):  
    '''
    La funcion "notificarDatosErroneos" permite notificar datos erroneos a la base de datos desde la vista "notificar-incidencias.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "notificar-incidencias.html" con los datos necesarios para la vista
    '''  
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre')
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados), 
        "rutaActual": "Notificar datos erroneos",
        "rutaPrevia": "Notificar problemas",
        "urlRutaPrevia": reverse('timetrackpro:notificar-problemas'),
        "formulario": reverse('timetrackpro:notificar-datos-erroneos'),
    }
    if request.method == 'POST':
        usuario = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.user.id)[0]
        refEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=usuario)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=refEmpleado.id_usuario.id)[0]
        estado = estadosErrores["Pendiente"]
        fechaRegistro = datetime.now()
        motivo = request.POST.get("motivoError")
        tipo = "2"

        '''
        tipo = 2 -> Corrección de datos erróneos
        tipo = 1 -> Fallos en la aplicación
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaRegistro> - fecha de registro del problema
        <motivo> - motivo del problema
        '''

        '''
        ASUNTO 
        Nueva solicitud de <tipo> en timetrackpro.

        MENSAJE PARA EL REMITENTE

        Su incidencia ha quedado registrada. Puede consultar el estado en el siguiente enlace:
        <url>        

        MENSAJE PARA EL DESTINATARIO

        <nombreSolicitante> <apellidosSolicitante> ha registrado una incidencia de <tipo> con fecha <fechaRegistro>.
        El motivo de la solicitud es:
        <motivo>
        Puede consultar más información en el siguiente enlace.
        <url>
        '''

        url = 'http://alerta2.es/private/timetrackpro/listado-incidencias'
        stringFecha = fechaRegistro.strftime("%d-%m-%Y a las %H:%M:%S")

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=45)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<tipo>", "Corrección de datos erróneos").replace('\n', '').replace('\r', '')
        
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=46)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaRegistro>", stringFecha).replace("<motivo>", motivo).replace("<tipo>", "Corrección de datos erróneos")

        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO]

        # convertir a direcciones de correo
        if empleado.email != "" and empleado.email != None:
            correoEmpleado = convertirAMail(empleado.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]
        error = ProblemasDetectadosTimeTrackPro(usuario=usuario, estado=estado, fecha_registro=fechaRegistro, problema_detectado=motivo, tipo=tipo)

        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        error.save(using='timetrackpro')

        return redirect('timetrackpro:ver-incidencia', id=error.id)   
     
    return render(request,"notificar-incidencia.html", infoVista)



@login_required
def notificarErroresApp(request):
    '''
    La funcion "notificarErroresApp" permite notificar errores en la aplicación a la base de datos desde la vista "notificar-incidencias.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "notificar-incidencias.html" con los datos necesarios para la vista
    '''    
    empleados = EmpleadosMaquinaTimetrackpro.objects.using("timetrackpro").values('id', 'nombre')
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados), 
        "rutaActual": "Notificar error en la aplicación",
        "rutaPrevia": "Notificar problemas",
        "urlRutaPrevia": reverse('timetrackpro:notificar-problemas'),
        "formulario": reverse('timetrackpro:notificar-errores-app'),

    }
    if request.method == 'POST':
        usuario = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.user.id)[0]
        refEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=usuario)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=refEmpleado.id_usuario.id)[0]
        estado = estadosErrores["Pendiente"]
        fechaRegistro = datetime.now()
        motivo = request.POST.get("motivoError")
        tipo = "1"

        '''
        tipo = 2 -> Corrección de datos erróneos
        tipo = 1 -> Fallos en la aplicación
        <nombreSolicitante> - nombre del usuario que solicita el cambio
        <apellidosSolicitante> - apellidos del usuario que solicita el cambio
        <url> - url de la aplicacion
        <fechaRegistro> - fecha de registro del problema
        <motivo> - motivo del problema
        '''

        '''
        ASUNTO 
        Nueva solicitud de <tipo> en timetrackpro.

        MENSAJE PARA EL REMITENTE

        Su incidencia ha quedado registrada. Puede consultar el estado en el siguiente enlace:
        <url>        

        MENSAJE PARA EL DESTINATARIO

        <nombreSolicitante> <apellidosSolicitante> ha registrado una incidencia de <tipo> con fecha <fechaRegistro>.
        El motivo de la solicitud es:
        <motivo>
        Puede consultar más información en el siguiente enlace.
        <url>
        '''

        url = 'http://alerta2.es/private/timetrackpro/listado-incidencias'
        stringFecha = fechaRegistro.strftime("%d-%m-%Y a las %H:%M:%S")

        mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=45)[0]
        subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<tipo>","Fallos en la aplicación" ).replace("<apellidosSolicitante>", empleado.apellidos).replace('\n', '').replace('\r', '')
        
        mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url)

        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=46)[0]
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaRegistro>", stringFecha).replace("<motivo>", motivo).replace("<tipo>", "Fallos en la aplicación")

        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO]

        # convertir a direcciones de correo
        if empleado.email != "" and empleado.email != None:
            correoEmpleado = convertirAMail(empleado.email)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)

        mailSolicitante = [correoEmpleado,]

        error = ProblemasDetectadosTimeTrackPro(usuario=usuario, estado=estado, fecha_registro=fechaRegistro, problema_detectado=motivo, tipo=tipo)
        error.save(using='timetrackpro')
        send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
        send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
        return redirect('timetrackpro:ver-incidencia', id=error.id)    
     
    return render(request,"notificar-incidencia.html", infoVista)


@login_required
def problemasNotificados(request):
    '''
    La funcion "problemasNotificados" permite mostrar los problemas notificados por los empleados en la vista "problemas-notificados.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "problemas-notificados.html" con los datos necesarios para la vista
    '''

    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": "Incidencias notificadas",

    }
    return render(request,"listado-incidencias.html",infoVista)


@login_required   
def datosProblemasNotificados(request, tipo=None, estado=None):
    '''
    La funcion "datosProblemasNotificados" obtiene los datos de los problemas notificados por los empleados y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param tipo: El parametro "tipo" es el tipo de problema que se desea obtener
    :param estado: El parametro "estado" es el estado del problema que se desea obtener
    :return: un objeto "JsonResponse" que contiene los datos de los problemas notificados por los empleados en formato json
    '''
    if tipo is None or tipo == "Todos":
        tipo = ["1", "2"]
    if estado is None or estado == "0":
        estado = ["1", "2", "3"]
    incidencias = ProblemasDetectadosTimeTrackPro.objects.using("timetrackpro").filter(tipo__in=tipo, estado__in=estado).values('id', 'usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario', 'fecha_registro', 'estado', 'problema_detectado', 'tipo')

    return JsonResponse(list(incidencias), safe=False)



@login_required
def verIncidencia(request, id):
    '''
    La funcion "verIncidencia" obtiene los datos de una incidencia en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la incidencia que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-incidencia.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    incidencia = ProblemasDetectadosTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": "Incidencia nº " + str(incidencia.id),
        "rutaPrevia": "Incidencias notificadas",
        "urlRutaPrevia": reverse('timetrackpro:listado-incidencias'),
        "incidencia":incidencia,
        "administrador":administrador,
    }
    return render(request,"ver-incidencia.html",infoVista)

@login_required
def cambiarEstadoIncidencia(request, id):
    '''
    La funcion "cambiarEstadoIncidencia" permite cambiar el estado de una incidencia en concreto en la base de datos desde la vista "ver-incidencia.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la incidencia que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-incidencia.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            incidencia = ProblemasDetectadosTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
            incidencia.estado = request.POST.get("estado")
            incidencia.fecha_resolucion = datetime.now()
            if request.POST.get("estado") == "2":
                incidencia.observaciones = request.POST.get("motivo")
            else:
                incidencia.observaciones = None
            incidencia.save(using='timetrackpro')
            return redirect('timetrackpro:ver-incidencia', id=id)
        return redirect('timetrackpro:listado-incidencias')
    return redirect('timetrackpro:ups', mensaje="No se ha podido modificar el estado de la incidencia")


@login_required
def eliminarIncidencia(request, id):
    '''
    La funcion "eliminarIncidencia" permite eliminar una incidencia en concreto de la base de datos desde la vista "ver-incidencia.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la incidencia que se desean ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-incidencia.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        incidencia = ProblemasDetectadosTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
        incidencia.delete(using='timetrackpro')
        return redirect('timetrackpro:listado-incidencias')
    return redirect('timetrackpro:ups', mensaje="No se ha podido eliminar la incidencia")

@login_required
def jornadas(request):
    '''
    La funcion "jornadas" permite mostrar las jornadas de los empleados en la vista "jornadas-empleados.html".
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "jornadas-empleados.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    if administrador or director:
        empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").values()
        jornadas = RelJornadaEmpleados.objects.using("timetrackpro").values()

        # current_url = request.path[1:]
        
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "director":director,
            "jornadas":list(jornadas),
            "alerta":alerta, 
            "empleados":list(empleados), 
            "rutaActual": "Jornadas de los empleados",
        }
        return render(request,"jornada-empleados.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tiene permisos para ver esta página")


@login_required
def datosJornadas(request):
    '''
    La funcion "datosJornadas" obtiene los datos de las jornadas de los empleados y los devuelve en formato json.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :return: un objeto "JsonResponse" que contiene los datos de las jornadas de los empleados en formato json
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    jornadas=[]
    if administrador or director:
        auxJornadas = RelJornadaEmpleados.objects.using("timetrackpro").values()
        for j in auxJornadas:

            empleado_id = j.get('id_empleado_id')
            if empleado_id is not None:
                empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=empleado_id).first()
                if empleado:
                    j['empleado'] = empleado.nombre + " " + empleado.apellidos
                else:
                    j['empleado'] = "Empleado no encontrado"
            else:
                j['empleado'] = "ID de empleado no proporcionado"
            jornadas.append(j)

        return JsonResponse(list(jornadas), safe=False)
    else:
        return redirect('timetrackpro:ups', mensaje="No tiene permisos para ver esta página")


def subirDocumento(f, destino):
    '''
    La funcion "subirDocumento" permite subir un documento a la base de datos desde la vista "subir-documento.html".
    :param f: El parametro "f" es el documento que se desea subir
    :param destino: El parametro "destino" es el destino donde se desea guardar el documento
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "subir-documento.html" con los datos necesarios para la vista
    '''
    with open(destino, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def enviarTelegram(asunto, mensaje, icono=None):
    '''
    La funcion "enviarTelegram" permite enviar un mensaje a traves de Telegram.
    '''
    if icono is None:
        icono = '19'
    MensajesTelegram(id_area=4,id_estacion=None,fecha_hora_utc=datetime.now(pytz.timezone("Europe/Madrid")),mensaje=asunto,descripcion=mensaje,icono=icono,estado=0,id_telegram=settings.ID_CHAT_TIMETRACK,silenciar=0, confirmar=0).save(using='spd')

@login_required
def datosViajes(request, year=None):
    """
    The function "datosUsuariosMaquina" retrieves data of users from a machine and returns it as a JSON
    response.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the user making the request, the HTTP method used (GET,
    POST, etc.), and any data sent with the request
    :return: a JSON response containing a list of user data for the "EmpleadosMaquina" model. The user
    data includes fields such as "id", "nombre", "turno", "horas_maxima_contrato", "en_practicas",
    "maquina_laboratorio", "maquina_alerta2", and "maquina_departamento".
    """

    if year == None:
        year = datetime.now().year  
    viajes=[]
    viajes = ViajesTimeTrackPro.objects.using("timetrackpro").filter(fecha_inicio__year=year).values('id', 'solicitante__nombre', 'solicitante__id', 'solicitante', 'solicitante__apellidos', 'lugar', 'fecha_solicitud', 'fecha_inicio', 'fecha_fin', 'motivo_viaje', 'estado','estado__id','estado__nombre', 'motivo_rechazo', 'vehiculo')
    return JsonResponse(list(viajes), safe=False)

@login_required
def datosViajesCalendario(request, year=None):
    '''
    La funcion "datosFestivosCalendario" obtiene los festivos registrados en la base de datos y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los festivos
    :return: un objeto "JsonResponse" que contiene los datos de los festivos en formato json    
    '''
    # obtengo los festivos registrados en la base de datos
    festivos = []
    if year == None:
        viajes = ViajesTimeTrackPro.objects.using("timetrackpro").exclude(estado__id=24).values('id', 'solicitante__nombre', 'solicitante__id', 'solicitante', 'solicitante__apellidos', 'lugar', 'fecha_solicitud', 'fecha_inicio', 'fecha_fin', 'motivo_viaje', 'estado__nombre', 'motivo_rechazo', 'vehiculo')
    else:
        viajes = ViajesTimeTrackPro.objects.using("timetrackpro").filter(fecha_inicio__year=year).exclude(estado__id=24).values('id', 'solicitante__nombre', 'solicitante__id', 'solicitante', 'solicitante__apellidos', 'lugar', 'fecha_solicitud', 'fecha_inicio', 'fecha_fin', 'motivo_viaje', 'estado__nombre', 'motivo_rechazo', 'vehiculo')
    # creo una lista vacía para guardar los datos de los festivos
    salida = []

    # recorro los festivos y los guardo en la lista
    for viaje in viajes:
        # inserto los datos en la lista siguiendo la estructura que requiere el calendario
        salida.append({
            'id':viaje['id'],
            'title':viaje['lugar'],
            'start':viaje['fecha_inicio'],
            'end':viaje['fecha_fin'] + timedelta(days=1),
            'color': '#63465a',
            'textColor': '#FFFFFF'
        })
    # devuelvo la lista en formato json
    return JsonResponse(salida, safe=False)
    
@csrf_exempt
def obtenerVehiculosDisponibles(request):
    vehiculosList = []
    fechaInicio = request.POST.get("fecha_inicio")
    fechaFin = request.POST.get("fecha_fin")
    vehiculos = Equipo.objects.using("docLaruex").filter(tipo_equipo=21).values('id', 'cod_laruex', 'cod_uex', 'num_serie', 'descripcion', 'fecha_alta', 'fecha_baja', 'precio', 'modelo', 'motivo_baja', 'proyecto', 'cod_spida', 'propietario', 'proveedor', 'ubicacion_actual', 'grupo', 'alta_uex', 'id__nombre')
    for vehiculo in vehiculos:
        # obten la tabla donde se encuentran localizadas todas las reservas del vehiculo
        reservas = ReservasVehiculos.objects.using("docLaruex").filter(id_equipo=vehiculo['id']) 
        reservado = False
        if reservas.filter(fecha_inicio__lte=fechaInicio, fecha_fin__gte=fechaInicio).exists() or reservas.filter(fecha_inicio__gte=fechaInicio, fecha_fin__gte=fechaFin, fecha_inicio__lte=fechaFin).exists() or reservas.filter(fecha_inicio__lte=fechaInicio, fecha_fin__gte=fechaInicio, fecha_fin__lte=fechaFin).exists() or reservas.filter(fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin).exists():
            reservado = True
        if not reservado:
            vehiculosList.append(vehiculo)
    return render(request,"relleno-combo-vehiculos.html",{"vehiculos":vehiculosList})
    


@login_required
def viajes(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)    
    vehiculos = Equipo.objects.using("docLaruex").filter(tipo_equipo=21).values('id', 'cod_laruex', 'cod_uex', 'num_serie', 'descripcion', 'fecha_alta', 'fecha_baja', 'precio', 'modelo', 'motivo_baja', 'proyecto', 'cod_spida', 'propietario', 'proveedor', 'ubicacion_actual', 'grupo', 'alta_uex', 'id__nombre')
    if year is None:
        year = str(datetime.now().year)

    mes = str(datetime.now().month)
    if len(mes) == 1:
        mes = "0" + mes
    initialDate = str(year) + "-" + mes + "-01"
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "director":director,
        "initialDate":initialDate,
        "currentYear":year,
        "rutaActual": "Viajes "  + str(year),
        "rutaPrevia": "Solicitudes",
        "vehiculos": vehiculos,
        "urlRutaPrevia": reverse('timetrackpro:solicitudes'),
    }
    return render(request,"solicitar-viajes.html",infoVista)

def enviarMensajeViaje(request, empleado, viaje):
    '''
    <nombreSolicitante> - nombre del usuario que solicita el cambio
    <apellidosSolicitante> - apellidos del usuario que solicita el cambio
    <url> - url de la aplicacion
    <fechaInicio> - fecha de inicio del periodo actual
    <fechaFin> - fecha de fin del periodo actual
    <motivo> - motivo de la solicitud
    <lugar> - lugar del viaje

    ASUNTO 
    <nombreSolicitante> <apellidosSolicitante> ha solicitado un viaje.

    MENSAJE PARA EL REMITENTE
    Su solicitud de viaje ha sido registrada con éxito.
    Fecha: <fechaInicio> al <fechaFin>
    Lugar: <lugar>
    Motivo: <motivo>
    Puede consultar el estado de la solicitud en el siguiente enlace.
    <url>


    MENSAJE PARA EL DESTINATARIO
    <nombreSolicitante> <apellidosSolicitante> ha solicita un viaje a <lugar> por el motivo de <motivo> desde el <fechaInicio> al <fechaFin>.
    Puede consultar el estado de la solicitud en el siguiente enlace.
    <url>
        
    '''
    url = 'http://alerta2.es/private/timetrackpro/solicitud-viaje/' + str(viaje.id) + '/'
    # convertir a direcciones de correo
    if empleado.email != "" and empleado.email != None:
        correoEmpleado = convertirAMail(empleado.email)
    else:
        correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)
    
    email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
    destinatariosList = [settings.EMAIL_ADMIN_TIMETRACKPRO, settings.EMAIL_DIRECTOR_TIMETRACKPRO]
    mailSolicitante = [correoEmpleado,]

    mensajeTipoRemitente = MonitorizaMensajesTipo.objects.using("spd").filter(id=56)[0]
    subject = mensajeTipoRemitente.mensaje.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace('\n', '').replace('\r', '')
    
    mensajeSolicitante = mensajeTipoRemitente.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", viaje.fecha_inicio).replace("<fechaFin>", viaje.fecha_fin).replace("<lugar>", viaje.lugar).replace("<motivo>", viaje.motivo_viaje)

    mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=57)[0]
    mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<nombreSolicitante>", empleado.nombre).replace("<apellidosSolicitante>", empleado.apellidos).replace("<url>", url).replace("<fechaInicio>", viaje.fecha_inicio).replace("<fechaFin>", viaje.fecha_fin).replace("<lugar>", viaje.lugar).replace("<motivo>", viaje.motivo_viaje)
    send_mail(subject, mensajeSolicitante, email_from, mailSolicitante)
    send_mail(subject, mensajeDestinatario, email_from, destinatariosList)
    enviarTelegram(subject, mensajeDestinatario, '42')

    return redirect('timetrackpro:viajes')



@login_required
def solicitarViaje(request):
    '''
    La funcion "solicitarAsuntosPropios" permite solicitar un asunto propio a la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param year: El parametro "year" es el año del que se quieren obtener los asuntos propios
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "solicitar-asuntos-propios.html" con los datos necesarios para la vista
    '''
    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        motivo = ""
        if request.POST.get("motivo") != "" or request.POST.get("motivo") != None:
            motivo = request.POST.get("motivo")
        
        lugar = ""
        if request.POST.get("lugar") != "" or request.POST.get("lugar") != None:
            lugar = request.POST.get("lugar") 

        viajes = ViajesTimeTrackPro.objects.using("timetrackpro").filter(solicitante=empleado) 
        if viajes.filter(fecha_inicio__lte=fechaInicio, fecha_fin__gte=fechaInicio).exists() or viajes.filter(fecha_inicio__gte=fechaInicio, fecha_fin__gte=fechaFin, fecha_inicio__lte=fechaFin).exists() or viajes.filter(fecha_inicio__lte=fechaInicio, fecha_fin__gte=fechaInicio, fecha_fin__lte=fechaFin).exists() or viajes.filter(fecha_inicio__gte=fechaInicio, fecha_fin__lte=fechaFin).exists():
            return redirect('timetrackpro:ups', mensaje='Ya tienes un viaje solicitado en esas fechas.')
        else:
            # estado viaje pendiente
            estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=22)[0]
            fechaSolicitud = datetime.now()
            vehiculoSeleccionado = request.POST.get("vehiculo")
            print('\033[91m'+'vehiculoSeleccionado: ' + '\033[92m', vehiculoSeleccionado)
            vehiculo = None
            if vehiculoSeleccionado != "" and vehiculoSeleccionado != None: 
                vehiculoEquipo = Equipo.objects.using("docLaruex").filter(id=vehiculoSeleccionado)[0]
                vehiculo = vehiculoSeleccionado
                nuevaReservaVehiculo = ReservasVehiculos(id_equipo=vehiculoEquipo, fecha_inicio=fechaInicio, fecha_fin=fechaFin)
                nuevaReservaVehiculo.save(using='docLaruex')
            nuevoViaje = ViajesTimeTrackPro(solicitante=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, estado=estado, fecha_solicitud=fechaSolicitud, motivo_viaje=motivo, lugar=lugar, vehiculo=vehiculo)
            nuevoViaje.save(using='timetrackpro')
            enviarMensajeViaje(request, empleado, nuevoViaje)
        return redirect('timetrackpro:viajes')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar la tarjeta.")

        

@login_required
def verViaje(request, id):
    '''
    La funcion "verJornada" obtiene los datos de una jornada laboral en concreto y los muestra en una plantilla para su visualizacion.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de la jornada laboral que se desea ver
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-jornada.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    viaje = ViajesTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
    empleados = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(fecha_baja_app__isnull=True).values('id', 'nombre', 'apellidos')
    vehiculo = None
    if viaje.vehiculo != None:
        vehiculo = Equipo.objects.using("docLaruex").filter(id=viaje.vehiculo)[0]
    
    estados = EstadosSolicitudes.objects.using("timetrackpro").filter(viajes=1).values()
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": viaje.lugar,
        "rutaPrevia": "Viajes",
        "urlRutaPrevia": reverse('timetrackpro:viajes'),
        "vehiculo":vehiculo,
        "viaje":viaje,
        "empleados":list(empleados),
        "estados":list(estados),
        "administrador":administrador,
    }
    return render(request,"ver-viaje.html",infoVista)

@login_required
def modificarViaje(request, id=None):
    '''
    La funcion "modificarViaje" permite modificar un viaje en concreto de la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente. Contiene informacion como el usuario que realiza la peticion, el metodo HTTP utilizado (GET, POST, etc.), y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del viaje que se desea modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-viaje.html" con los datos necesarios para la vista
    '''
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        if request.POST.get("id_viaje") and not id:
            id = request.POST.get("id_viaje")

        viaje = ViajesTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
        retirarVehiculo = request.POST.get("retirar_vehiculo")
        if int(retirarVehiculo) == 0:
            nuevoVehiculo = Equipo.objects.using("docLaruex").filter(id=request.POST.get("vehiculo"))[0]
            if viaje.vehiculo:
                vehiculo = Equipo.objects.using("docLaruex").filter(id=viaje.vehiculo)[0]
                reservas = ReservasVehiculos.objects.using("docLaruex").filter(id_equipo=vehiculo, fecha_inicio=viaje.fecha_inicio, fecha_fin=viaje.fecha_fin)
                for reserva in reservas:
                    reserva.id_equipo = nuevoVehiculo
                    reserva.fecha_inicio = request.POST.get("fecha_inicio")
                    reserva.fecha_fin= request.POST.get("fecha_fin")
                    reserva.save(using='docLaruex')
            else:
                nuevaReservaVehiculo = ReservasVehiculos(id_equipo=nuevoVehiculo, fecha_inicio=request.POST.get("fecha_inicio"), fecha_fin=request.POST.get("fecha_fin"))
                nuevaReservaVehiculo.save(using='docLaruex')
            idNuevoVehiculo = nuevoVehiculo.id.id
        else:
            if viaje.vehiculo:
                vehiculo = Equipo.objects.using("docLaruex").filter(id=viaje.vehiculo)[0]
                reservas = ReservasVehiculos.objects.using("docLaruex").filter(id_equipo=vehiculo, fecha_inicio=viaje.fecha_inicio, fecha_fin=viaje.fecha_fin)
                for reserva in reservas:
                    reserva.delete(using='docLaruex')
            idNuevoVehiculo = None

                
        viaje.fecha_inicio = request.POST.get("fecha_inicio")
        viaje.fecha_fin = request.POST.get("fecha_fin")
        solicitante = EmpleadosTimetrackpro.objects.using("timetrackpro").filter(id=request.POST.get("solicitante"))[0]         
        viaje.solicitante = solicitante
        viaje.lugar = request.POST.get("lugar")
        viaje.motivo_viaje= request.POST.get("motivo_viaje")
        viaje.vehiculo = idNuevoVehiculo    
        viaje.save(using='timetrackpro')


        return redirect('timetrackpro:ver-viaje', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para modificar el asunto propio seleccionado.")
    



@login_required
def eliminarViaje(request, id=None):
    '''
    La función "eliminarViaje" permite eliminar un viaje en concreto de la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del viaje que se desea eliminar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "viajes.html" con los datos necesarios para la vista
    '''

    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            if request.POST.get("idViaje") and not id:
                id = request.POST.get("idViaje")
            viaje = ViajesTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
            if viaje.vehiculo:
                vehiculo = Equipo.objects.using("docLaruex").filter(id=viaje.vehiculo)[0]
                reservas = ReservasVehiculos.objects.using("docLaruex").filter(id_equipo=vehiculo, fecha_inicio=viaje.fecha_inicio, fecha_fin=viaje.fecha_fin)
                for reserva in reservas:
                    reserva.delete(using='docLaruex')
            viaje.delete(using='timetrackpro')
        return redirect('timetrackpro:viajes')
    else:
        return redirect('timetrackpro:sin-permiso')
    

@login_required
def cambiarEstadoViaje(request, id=None):

    '''
    La función cambiarEstadoViaje permite cambiar el estado de un viaje en concreto de la base de datos.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el cliente, el metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador del viaje que se desea modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "ver-viaje.html" con los datos necesarios para la vista
    '''

    '''
    <url> - url de la aplicacion
    <fechaInicio> - fecha de inicio del periodo actual
    <fechaFin> - fecha de fin del periodo actual
    <estado> - estado de la solicitud

    ASUNTO 
    Cambios en solicitud de viaje

    MENSAJE PARA EL DESTINATARIO
    Su solicitud de viaje para el periodo comprendido entre el <fechaInicio> y el <fechaFin> ha sido <estado>.
    Puede consultar el estado de su solicitud en el siguiente enlace:
    <url>
    '''

    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        if request.method == 'POST':
            if request.POST.get("idViaje") and not id:
                id = request.POST.get("idViaje")
            viaje = ViajesTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
            estadoSeleccionado = request.POST.get("estado")
            estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=estadoSeleccionado)[0]
            if int(estadoSeleccionado) == 24:
                motivoRechazo = request.POST.get("motivo_rechazo")
                viaje.motivo_rechazo = motivoRechazo
                if viaje.vehiculo:
                    vehiculo = Equipo.objects.using("docLaruex").filter(id=viaje.vehiculo)[0]
                    reservas = ReservasVehiculos.objects.using("docLaruex").filter(id_equipo=vehiculo, fecha_inicio=viaje.fecha_inicio, fecha_fin=viaje.fecha_fin)
                    for reserva in reservas:
                        reserva.delete(using='docLaruex')
            viaje.estado = estado   
            viaje.save(using='timetrackpro')

            mailEmpleado = viaje.solicitante.email
            estadoSolicitud = viaje.estado.nombre
            if mailEmpleado != "" and mailEmpleado != None:
                correoEmpleado = convertirAMail(mailEmpleado)
            else:
                correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)
            mailSolicitante = [correoEmpleado,]
            email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
            mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=58)[0]
            url = 'http://alerta2.es/private/timetrackpro/ver-viaje/' + str(viaje.id) + '/'
            fechaInicio = str(viaje.fecha_inicio)
            fechaFin = str(viaje.fecha_fin)
            subject = mensajeTipoDestinatario.mensaje.replace('\n', '').replace('\r', '')
            mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<estado>", estadoSolicitud).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)
            send_mail(subject, mensajeDestinatario, email_from, mailSolicitante)

        return redirect('timetrackpro:ver-viaje', id=viaje.id)
    else:
        return redirect('timetrackpro:sin-permiso')
    

    
@login_required
def cambiarEstadoVacacionesPruebas(request, id):
    '''
    La funcion "cambiarEstadoVacaciones" permite cambiar el estado de unas vacaciones en concreto.
    :param request: El parametro "request" es un objeto que representa la peticion HTTP realizada por el clienteel metodo HTTP utilizado (GET, POST, etc.) y cualquier dato enviado con la peticion
    :param id: El parametro "id" es el identificador de las vacaciones que se desean modificar
    :return: un objeto "HttpResponseRedirect" que redirige a la pagina "verVacacionesSeleccionadas.html" con los datos necesarios para la vista
    '''

    '''
    <url> - url de la aplicacion
    <fechaInicio> - fecha de inicio del periodo actual
    <fechaFin> - fecha de fin del periodo actual
    <estado> - estado de la solicitud

    ASUNTO 
    Solicitud de vacaciones <estado>.

    MENSAJE PARA EL DESTINATARIO
    Su solicitud de vacaciones para el periodo comprendido entre el <fechaInicio> y el <fechaFin> ha sido <estado>.
    Puede consultar el estado de su solicitud en el siguiente enlace:
    <url>
    '''

    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if request.method == 'POST' and (administrador or director):
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1,id=estado)[0]
        vacaciones.estado = nuevoEstado
        if vacaciones.estado.id == 10:
            motivo = request.POST.get("motivo")
            vacaciones.motivo_estado_solicitud = motivo
        vacaciones.save(using='timetrackpro')
        mailEmpleado = vacaciones.empleado.email
        estadoSolicitud = vacaciones.estado.nombre
        if mailEmpleado != "" and mailEmpleado != None:
            correoEmpleado = convertirAMail(mailEmpleado)
        else:
            correoEmpleado = convertirAMail(settings.EMAIL_DEFAULT_TIMETRACKPRO)
        mailSolicitante = [correoEmpleado,]
        email_from = settings.EMAIL_HOST_USER_TIMETRACKPRO
        mensajeTipoDestinatario = MonitorizaMensajesTipo.objects.using("spd").filter(id=53)[0]
        url = 'http://alerta2.es/private/timetrackpro/ver-vacaciones-seleccionadas/' + str(vacaciones.id) + '/'
        fechaInicio = str(vacaciones.fecha_inicio)
        fechaFin = str(vacaciones.fecha_fin)
        subject = mensajeTipoDestinatario.mensaje.replace("<estado>", estadoSolicitud).replace('\n', '').replace('\r', '')
        mensajeDestinatario = mensajeTipoDestinatario.descripcion.replace("<estado>", estadoSolicitud).replace("<url>", url).replace("<fechaInicio>", fechaInicio).replace("<fechaFin>", fechaFin)

        send_mail(subject, mensajeDestinatario, email_from, mailSolicitante)

        return redirect('timetrackpro:solicitar-vacaciones')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para cambiar el estado de las vacaciones seleccionadas.")