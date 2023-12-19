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
from timetrackpro.funciones.funcionesAuxiliares import *
from django.db.models.functions import TruncDate




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


# ? información tarjeta acceso reverso
infoGeneralTarjeta ="Este carné es propiedad del LARUEX y deberá devuelto al departamento de administración una vez acabada la relación contractual con el mismo."
infoPersonalTarjeta = "El carné es personal e intransferible, por lo que cederlo a cualquier otra persona supondrá una grave violación de las normas del laboratorio."
infoContactoTarjeta = "Se ruega a quien encuentre este carné se ponga en contacto en el teléfono +34 927 251 389."


excluidos = ["Prueba", "Pruebas", "prueba", "pruebas", "PRUEBA", "PRUEBAS", "Usuario Pruebas",  "test", "TEST", "Test" , " ", "", "root", "CSN", "PCivil Provisional", "Protección Civil", "JEx", "Admin", "admin"]

# Defino la barra de navegación
navBar = NavBar.objects.using("timetrackpro").values()


def home(request):
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
    }

    return render(request,"home.html",infoVista)

'''
    Vista que indica que no se ha encontrado la página
'''
def noEncontrado(request):
    
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
        "mensaje":msg
    }

    return render(request,"ups.html",infoVista)

def habilitaciones(request):     
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
        "alerta":alerta
    }
    if administrador:
        return render(request,"habilitaciones.html",infoVista)
    
    else:
        return redirect('timetrackpro:sin-permiso')
    
def agregarHabilitacion(request):
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
    

def asociarHabilitacion(request):
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


def modificarHabilitacion(request):
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            idHabilitacion = request.POST.get("idHabilitacion")
            habilitacion = Habilitaciones.objects.using("timetrackpro").filter(id=idHabilitacion)[0]
            nombreHabilitacion = request.POST.get("nombreHabilitacion")
            habilitacion.nombre = nombreHabilitacion
            habilitacion.save(using='timetrackpro')
        return redirect('timetrackpro:habilitaciones')
    else:
        return redirect('timetrackpro:sin-permiso')
    
def eliminarHabilitacion(request):
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            idHabilitacion = request.POST.get("idHabilitacion")
            habilitacion = Habilitaciones.objects.using("timetrackpro").filter(id=idHabilitacion)[0]
            habilitacion.delete(using='timetrackpro')
        return redirect('timetrackpro:habilitaciones')
    else:
        return redirect('timetrackpro:sin-permiso')

def tarjetasAcceso(request):
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los datos necesarios para la vista
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
        "infoContactoTarjeta":infoContactoTarjeta
    }

    return render(request,"tarjetasAcceso.html", infoVista)


def datosTarjetasAccesoActivas(request):
    tarjetasActivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).order_by("nombre").values()
    return JsonResponse(list(tarjetasActivas), safe=False)

def datosTarjetasAccesoInactivas(request):
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
def datosDjangoUsers(request):
    empleados = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

    return JsonResponse(list(empleados), safe=False)


def agregarTarjetaAcceso(request):
    # obtengo los datos necesarios para la vista    
    if request.method == 'POST':
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

def verTarjetaAcceso(request, id):
    # obtengo los datos necesarios para la vista
    tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=id).values()[0]

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
 

def editarTarjetaAcceso(request):
    if request.method == 'POST':
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
        return redirect('timetrackpro:tarjetas-de-acceso')

'''-------------------------------------------
                                Módulo: verPermiso

- Descripción: 
Muestra la información de cada uno de los permisos registrados en la base de datos

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def infoConfigTarjetasAcceso(request):
    

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"infoConfigTarjetasAcceso.html",infoVista)

def registrosInsertados(request):

    # obtengo los datos necesarios para la vista
    
    archivos = RegistrosJornadaInsertados.objects.using("timetrackpro").order_by('year', 'mes').all()

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "archivos":list(archivos)
    }
    return render(request,"registros-insertados.html",infoVista)


def datosRegistrosInsertados(request):
    registros = RegistrosJornadaInsertados.objects.using("timetrackpro").values('id', 'seccion', 'mes', 'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', 'ruta')
    return JsonResponse(list(registros), safe=False)



def obtenerRegistro(request, year=None, mes=None, semana=None):
    #empleados de las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"informeRegistro.html",infoVista)

def obtenerRegistroUsuario(request, id=None, year=None, mes=None, semana=None):
    #empleados de las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()

    # current_url = request.path[1:]
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"informeRegistroUsuario.html",infoVista)


def datosRegistroUsuario(request, id=None, year=None, mes=None, semana=None):
    #empleados de las máquinas de control de asistencia
    salida = []

    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
    #filter=models.Q(hora__date__gte=datetime.strptime(year + "-" + mes + "-01", '%Y-%m-%d').date()), distinct=True)
    if id is not  None:
        empleados = EmpleadosMaquina.objects.using("timetrackpro").filter(id__in=id).values()
    for e in empleados:
        #registros = Registros.objects.using("timetrackpro").filter(id_empleado=e["id"]).annotate(fecha=TruncDate('hora')).values('hora__date','hora__time','id_empleado','nombre_empleado', 'fecha').annotate(hora_entrada=Min('hora__time'), hora_salida=Max('hora__time')).order_by('fecha')
        registros= Registros.objects.using("timetrackpro").filter(id_empleado=e["id"]).annotate(fecha=TruncDate('hora')).values('fecha', 'id_empleado', 'nombre_empleado', 'hora__time').order_by('-fecha','hora__time')

        #.annotate(hora_entrada=Min('hora__time'), hora_salida=Max('hora__time'))
        for r in registros:


            salida.append(r)
    # current_url = request.path[1:]
    return JsonResponse(list(salida), safe=False)



def quitarAcentos(cadena):
    return ''.join((c for c in unicodedata.normalize('NFD', cadena) if unicodedata.category(c) != 'Mn'))



def convertirFormatoDateTime(datoFecha):
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



def verRegistro(request, id):
    registro = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=id)[0]
    
    maquina = MaquinaControlAsistencia.objects.using("timetrackpro").filter(nombre__icontains=registro.seccion)[0]
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
                empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=id_empleado)[0]
                nombre = campos[1]
                hora = convertirFormatoDateTime(campos[3])
                
                if Registros.objects.using("timetrackpro").filter(id_empleado=empleado, hora=hora).exists():
                    continue
                else:
                    # Si no existe, crea un nuevo registro en la base de datos
                    nuevoRegistro = Registros(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                    nuevoRegistro.save()

        # Mover el archivo a la nueva ruta después de procesarlo
        shutil.move(ruta, ruta_leido)
    registrosInsertados = Registros.objects.using("timetrackpro").filter(id_archivo_leido=registro.id).values()

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "registro":registro,
        "registrosInsertados":list(registrosInsertados)
    }
    return render(request,"verRegistro.html",infoVista)

def datosRegistro(request, id):
    registros = Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    empleados = AuthUserTimeTrackPro.objects.using("timetrackpro").values('id', 'first_name', 'last_name', 'is_active')
    
    
    '''
    procExistentes = []
    salida = []
    for p in registros:
        if not p["id_doc__nombre"] in procExistentes:
            p["responsable__first_name"] = p["responsable__first_name"] + \
                " / " + p["revisor__first_name"]
            salida.append(p)
            procExistentes.append(p["id_doc__nombre"])
    '''
    return JsonResponse(list(registros), safe=False)


def verLineaRegistro(request, id):
    registro = Registros.objects.using("timetrackpro").filter(id=id)[0]
    

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "registro":registro,
    }
    return render(request,"verLineaRegistro.html",infoVista)

def editarLineaRegistro(request, id):
    registro = Registros.objects.using("timetrackpro").filter(id=id)[0]
    
    if request.method == 'POST':
        registro.hora = request.POST.get("hora")
        registro.modificado = 1
        motivo = request.POST.get("motivo")
        if motivo != "":
            registro.motivo_modificacion = motivo
        else :
            registro.motivo_modificacion = None
        registro.save(using='timetrackpro')


    # guardo los datos en un diccionario

    return redirect('timetrackpro:ver-linea-registro', id=id)

def eliminarLineaRegistro(request, id):
    registro = Registros.objects.using("timetrackpro").filter(id=id)[0]
    archivoModificado = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=registro.id_archivo_leido.id)[0]

    if request.method == 'POST':
        idRegistroEliminado = registro.id
        idEmpleado = registro.id_empleado
        nombreEmpleado = registro.nombre_empleado
        hora = registro.hora
        maquina = registro.maquina
        remoto = registro.remoto
        idArchivoLeido = archivoModificado
        fechaEliminacion = datetime.now()
        motivo = request.POST.get("motivoEliminacion")
        registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=int(request.POST.get("registradorEliminacion")))[0]


        nuevoRegistroEliminado = RegistrosEliminados(id_registro_eliminado=idRegistroEliminado, id_empleado=idEmpleado, nombre_empleado=nombreEmpleado, hora=hora, maquina=maquina, remoto=remoto, id_archivo_leido=idArchivoLeido, fecha_eliminacion=fechaEliminacion, motivo=motivo, eliminado_por=registrador)

        nuevoRegistroEliminado.save(using='timetrackpro')
        registro.delete(using='timetrackpro')


    # guardo los datos en un diccionario
    return redirect('timetrackpro:ver-registro', id=archivoModificado.id)

def verMisErroresNotificados(request):
        
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"mis-errores-notificados.html",infoVista)


def datosMisErroresNotificados(request):
    # obtengo el id del usuario
    idUsuario = request.user.id
    # obtengo la relacion de ids del usuario con los empleados
    idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=idUsuario)[0]
    errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=idEmpleado).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre') 
    return JsonResponse(list(errores), safe=False)

def verErroresNotificados(request, id=None):
    idFilter = None
    
    if (id is None):
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").values()
    else:
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=id).values()
        idFilter = id
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "errores":list(errores),
        "idFilter":idFilter
    }
    return render(request,"errores-registrados.html",infoVista)



def verErroresNotificadosPendientes(request):
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"errores-registrados-pendientes.html",infoVista)

def datosErroresNotificadosPendientes(request):
    # obtengo los festivos registrados en la base de datos
    errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(estado=1).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre') 
    # devuelvo la lista en formato json
    return JsonResponse(list(errores), safe=False)

def notificarErrorEnFichaje(request):
    
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados)
    }
    if request.method == 'POST':
        idEmpleadoMaquina = request.POST.get("idEmpleadoMaquina")
        empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=idEmpleadoMaquina)[0]
        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=empleado)[0]
        motivo = request.POST.get("motivoError")
        estado = 1 # indico que aún esta pendiente de revisar
        hora = request.POST.get("hora")
        registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.POST.get("idEmpleado"))[0]
        horaNotificacion = datetime.now()

        nuevoErrorRegistrado = ErroresRegistroNotificados(id_empleado=idEmpleado, hora=hora, motivo=motivo, estado=estado, quien_notifica=registrador, hora_notificacion=horaNotificacion)
        nuevoErrorRegistrado.save(using='timetrackpro')
        return redirect('timetrackpro:ver-errores-notificados', id=idEmpleadoMaquina)   
     
    return render(request,"notificar-error-registro.html", infoVista)



def verErrorRegistroNotificado(request, id):
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id).values('id','id_empleado','id_empleado__id','id_empleado_id', 'hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica')[0]
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=error["id_empleado__id"])[0]
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "error":error,
        "empleado":empleado,
        "empleados":list(empleados),
    }
    return render(request,"verErrorNotificado.html",infoVista)

def modificarEstadoErrorRegistroNotificado(request, id):
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    if request.method == 'POST':
        motivo = None
        estado = request.POST.get("estado")

        if estado == "2":
           motivo = request.POST.get("motivo")

        error.estado = estado
        error.motivo_rechazo = motivo

        error.save(using='timetrackpro')

    # guardo los datos en un diccionario

    return redirect('timetrackpro:ver-error-registro-notificado', id=id)

def editarErrorRegistroNotificado(request, id):
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    if request.method == 'POST':
        error.hora = request.POST.get("hora")
        if request.POST.get("empleadoModificado") != "":
            empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=request.POST.get("empleadoModificado"))[0]
            error.id_empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=empleado)[0]
        error.save(using='timetrackpro')

    # guardo los datos en un diccionario
    return redirect('timetrackpro:ver-error-registro-notificado', id=id)

def eliminarErrorRegistroNotificado(request, id):
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    error.delete(using='timetrackpro')
    # guardo los datos en un diccionario
    return redirect('timetrackpro:ver-errores-registrados')

def datosErroresNotificados(request, id=None):
    # obtengo los festivos registrados en la base de datos
    errores = []
    if id == None:
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre')

    else:
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=id).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre') 
    # devuelvo la lista en formato json
    return JsonResponse(list(errores), safe=False)


def insertarRegistroManual(request):
    
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados)
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



def agregarRegistro(request):
    
    if request.method == 'POST':
        
        seccion = request.POST.get("seccion")
        mes = request.POST.get("mes")
        year = request.POST.get("year")
        fecha = datetime.now()
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
        nuevoRegistro = RegistrosJornadaInsertados(seccion=seccion, mes=mes, year=year, fecha_lectura=fecha, insertador=AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=int(request.POST.get("registrador")))[0], remoto=0)
        nuevoRegistro.save(using='timetrackpro')

        if request.FILES['archivoSeleccionado']:
            nombreArchivo = mes + "_" + year + "_" + seccion + '_Registro.' + request.FILES['archivoSeleccionado'].name.split('.')[-1]
            ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_NUEVO + nombreArchivo
            subirDocumento(request.FILES['archivoSeleccionado'], ruta)
            nuevoRegistro.ruta = nombreArchivo
            nuevoRegistro.save(using='timetrackpro')
        
        return redirect('timetrackpro:ver-registro', id=nuevoRegistro.id)
    else:
        # obtengo los datos necesarios para la vista
        infoVista = {
            "navBar":navBar,
            "administrador":True,
        }
        return render(request,"registros-insertados.html", infoVista)




def empleados(request):
    # obtengo los datos necesarios para la vista
    
    empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_auth_user__is_active', 'id_auth_user__is_superuser', 'id_auth_user__is_staff', 'id_auth_user__username', 'id_auth_user__password', 'id_auth_user__last_login', 'id_auth_user__date_joined')



    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados)
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
    empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id','id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_auth_user__is_active', 'id_auth_user__is_superuser', 'id_auth_user__is_staff', 'id_auth_user__username', 'id_auth_user__password', 'id_auth_user__last_login', 'id_auth_user__date_joined')

    return JsonResponse(list(empleados), safe=False)

def agregarUsuario(request):
    
    falta_tarjeta = True
    # obtengo los datos necesarios para la vista
    
    usuariosApp = AuthUserTimeTrackPro.objects.using("timetrackpro").values()
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "usuariosApp":list(usuariosApp),
        "falta_tarjeta":falta_tarjeta
    }

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
        if not Empleados.objects.using("timetrackpro").filter(dni__icontains=dniEmpleado).exists():
            nuevoUsuario = Empleados(nombre=nombreEmpleado, apellidos=apellidosEmpleado, puesto=puestoEmpleado, direccion=direccionEmpleado, telefono=telefonoEmpleado, telefono2=telefono2Empleado, email=emailEmpleado, email2=email2Empleado, dni=dniEmpleado, fecha_nacimiento=fechaNacimientoEmpleado, info_adicional=infoAdicionalEmpleado, extension=extensionEmpleado, fecha_alta_app=fechaAltaApp)
            nuevoUsuario.save(using='timetrackpro')

            if request.FILES['fotoEmpleadoSeleccionado']:
                nombreArchivo = str(nuevoUsuario.id) + '_usuario.' + request.FILES['fotoEmpleadoSeleccionado'].name.split('.')[-1]
                ruta = settings.STATIC_ROOT + settings.RUTA_USUARIOS_TIMETRACKPRO + nombreArchivo

                subirDocumento(request.FILES['fotoEmpleadoSeleccionado'], ruta)
                nuevoUsuario.img = nombreArchivo
                nuevoUsuario.save(using='timetrackpro')
        else:
            nuevoUsuario = Empleados.objects.using("timetrackpro").filter(dni__icontains=dniEmpleado)[0]
        return redirect('timetrackpro:ver-empleado', id=nuevoUsuario.id)

    
    else:
        return render(request,"agregar-usuario.html",infoVista)


def usuariosMaquina(request):
        # obtengo los datos necesarios para la vista
    
    usuariosMaquina = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "usuariosMaquina":list(usuariosMaquina)
    }
    return render(request,"usuariosMaquina.html",infoVista)

def datosUsuariosMaquina(request):
    usersMaquina = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

    return JsonResponse(list(usersMaquina), safe=False)


def agregarUsuarioMaquina(request):
    id, nombre, turno, horas_maxima_contrato, en_practicas, maquina_laboratorio, maquina_alerta2, maquina_departamento, numHuellas = None, None, None, None, None, None, None, None, None

    pin, esAdmin, ficharRemoto = 0, 0, 0

    if request.method == 'POST':
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
        
        if request.POST.get('permite_pin') == "on":
            pin = 1

       
        if request.POST.get('es_administrador') == "on":
            esAdmin = 1

               
        if request.POST.get('fichar_remoto') == "on":
            ficharRemoto = 1
        
        numHuellas = request.POST.get('huellas_registradas')

        if not EmpleadosMaquina.objects.using("timetrackpro").filter(id=request.POST.get("id_empleado_maquina")).exists():
            nuevoUser = EmpleadosMaquina(id=id, nombre=nombre, turno=turno, horas_maxima_contrato=horas_maxima_contrato, en_practicas=en_practicas, maquina_laboratorio=maquina_laboratorio, maquina_alerta2=maquina_alerta2, maquina_departamento=maquina_departamento, permite_pin=pin, es_administrador=esAdmin, huellas_registradas=numHuellas, fichar_remoto=ficharRemoto)
            nuevoUser.save(using='timetrackpro')
        

    return redirect('timetrackpro:usuarios-maquina')


def verUsuarioMaquina(request, id):
    # declaro las variables que voy a usar
    idUser, nombre, turno, horas_maxima_contrato, en_practicas, maquina_laboratorio, maquina_alerta2, maquina_departamento, relUser, huellas = None, None, None, None, None, None, None, None, None, None

    pin, esAdmin, ficharRemoto = 0, 0, 0

    # obtengo los datos necesarios para la vista
    
    usuarioMaquina = EmpleadosMaquina.objects.using("timetrackpro").filter(id=id)[0]
    relUser = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=usuarioMaquina)[0]
    



    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "usuarioMaquina":usuarioMaquina, 
        "relUser":relUser
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




'''-------------------------------------------
                                Módulo: verEmpleado

- Descripción: 
Obtener los datos de un empleado en concreto.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def verEmpleado(request, id):
    
        # obtengo los datos necesarios para la vista
    
    usuario = Empleados.objects.using("timetrackpro").filter(id=id)[0]
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

    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
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
        "tarjetas":list(tarjetasAcceso)
    }
    return render(request,"verEmpleado.html",infoVista)

'''-------------------------------------------
                                Módulo: asociarUsuario

- Descripción: 
Permite asociar las cuentas de los usuarios de la aplicación con los empleados registrados en las máquinas de control de asistencia, ademas de asociar la tarjeta de acceso y la información de la cuenta de django.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def asociarUsuario(request):
    
    usuariosApp = Empleados.objects.using("timetrackpro").values()
    # datos de los empleados registrados en las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
    # datos de los empleados registrados en django
    usuariosDjango = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

    tarjetasAcceso = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).values()

    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados),
        "usuariosApp":list(usuariosApp),
        "usuariosDjango":list(usuariosDjango),
        "tarjetas":list(tarjetasAcceso),
    }
    if request.method == 'POST':

        # obtenemos el identificador del usuario con la información que hay en la aplicación sobre el usuario, este contiene toda la info relevante del usuario
        idUser = request.POST.get("userApp")
        usuario = Empleados.objects.using("timetrackpro").filter(id=idUser)[0]

        # obtenemos el identificador del empleado, este contiene la información de la máquina de control de asistencia
        idEmpleado = request.POST.get("empleado_maquina")
        empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=idEmpleado)[0]

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


'''-------------------------------------------
                                Módulo: editarAsociarUsuario

- Descripción: 
Permite editar las relacion de usario en maquinas de registro, tarjeta de acceso, usuario de django y usuario de la aplicación (datos de contacto del usuario). 
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def editarAsociarUsuario(request, id):
    
    relacionActual = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=id).values('id', 'id_usuario', 'id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos','id_empleado', 'id_empleado__id','id_empleado__nombre','id_auth_user', 'id_auth_user__id','id_auth_user__first_name','id_auth_user__last_name', 'id_tarjeta_acceso', 'id_tarjeta_acceso__id', 'id_tarjeta_acceso__nombre', 'id_tarjeta_acceso__apellidos', 'id_tarjeta_acceso__id_tarjeta')[0]
    usuariosApp = Empleados.objects.using("timetrackpro").values()
    # datos de los empleados registrados en las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
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
    }
    if request.method == 'POST':

        # obtenemos el identificador del usuario con la información que hay en la aplicación sobre el usuario, este contiene toda la info relevante del usuario
        idUser = request.POST.get("userApp")
        usuario = Empleados.objects.using("timetrackpro").filter(id=idUser)[0]

        # obtenemos el identificador del empleado, este contiene la información de la máquina de control de asistencia
        idEmpleado = request.POST.get("empleado_maquina")
        empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=idEmpleado)[0]

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


'''-------------------------------------------
                                Módulo: verEmpleado

- Descripción: 
Obtener los datos de un empleado en concreto.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def editarEmpleado(request, id):
    
    usuario = Empleados.objects.using("timetrackpro").filter(id=id)[0]
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario)[0]
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True, 
        "empleado":empleado,
    }

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





def festivos(request, year=None):
    festivos = None
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    if year == None:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    else:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "year":year, 
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"festivos.html",infoVista)

def datosFestivosCalendario(request, year=None):
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




def datosFestivosVacacionesEmpleado(request):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    year = datetime.now().year
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    print('\033[91m'+'estadoAceptado: ' + '\033[92m', estadoAceptado)
    usuario = Empleados.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]
    print('\033[91m'+'usuario: ' + '\033[92m', usuario)
    # obtengo los festivos registrados en la base de datos
    festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
    
    if administrador or director:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado','empleado__nombre','empleado__apellidos', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud')
    else:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(estado=estadoAceptado, empleado=usuario, year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado','empleado__nombre','empleado__apellidos', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud')

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


def vacacionesSolicitadas(request):
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    mes = str(datetime.now().month)
    year = str(datetime.now().year)
    
    print (year, type(year))
    if len(mes) == 1:
        mes = "0" + str(mes)

    diaInicial = "01"
    initialDate = year + "-" + mes + "-" + diaInicial
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "initialDate":initialDate,
        "admin":admin,
        "director":director
    }
    return render(request,"vacaciones-solicitadas.html",infoVista)

def datosVacacionesSolicitadas(request):
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
     # obtengo los datos necesarios para la vista
    salida = []
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    usuario = Empleados.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]

    if admin or director:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(estado__in=[9,11,12]).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos')
    else:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=usuario, estado__in=[9,11,12]).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos')
    # creo una lista vacía para guardar los datos de los festivos
    # devuelvo la lista en formato json
    return JsonResponse(list(vacaciones),safe=False)




def datosCalendarioVacacionesSolicitadas(request):
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
            'end':vacacion['fecha_fin'],
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
def calendarioFestivos(request, mes, year=None):
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    # current_url = request.path[1:]
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
    
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "initialDate":initialDate,
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"calendarioFestivos.html",infoVista)



def agregarFestivo(request):
    if request.method == 'POST':
        nombre = request.POST.get("nombre_festividad")
        idTipo = request.POST.get("tipo_festividad")
        tipo = TipoFestivos.objects.using("timetrackpro").filter(id=idTipo)[0]
        fecha = request.POST.get("fecha_inicio")
        year = request.POST.get("year")

        fechaFin = None
        if "fecha_fin" in request.POST and request.POST.get("fecha_fin") != "":
            fechaFin = request.POST.get("fecha_fin")  
        else:
            fechaFin = fecha
        
        nuevoFestivo = FestivosTimetrackPro(nombre=nombre, tipo_festividad=tipo, fecha_inicio=fecha, fecha_fin=fechaFin, year=year)
        nuevoFestivo.save(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=year)    
    # current_url = request.path[1:]
    
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tipoFestivos":list(tipoFestivos)
    }

    return render(request,"agregarFestivos.html", infoVista)

def agregarFestivoCalendario(request):
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

    


def editarFestivo(request, id):
    festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(id=id)[0]
    # current_url = request.path[1:]
    
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tipoFestivos":list(tipoFestivos),
        "festivo":festivo
    }

    if request.method == 'POST':
        festivo.nombre = request.POST.get("nombre_festividad_editar")
        idTipo = request.POST.get("tipo_festividad_editar")
        tipo = TipoFestivos.objects.using("timetrackpro").filter(id=idTipo)[0]
        festivo.tipo_festividad = tipo
        festivo.fecha_inicio = request.POST.get("fecha_inicio_editar")
        festivo.year = request.POST.get("year_editar")
        festivo.fecha_fin = request.POST.get("fecha_fin_editar")  
        festivo.save(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=festivo.year)    

    return render(request,"editarFestivo.html", infoVista)


def eliminarFestivo(request, id):
    # current_url = request.path[1:]
    
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"eliminarFestivo.html",{})

def erroresRegistro(request, mes=None):
    festivos = None
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    if mes == None:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    else:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=mes).order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "mes":mes, 
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"festivos.html",infoVista)


'''-------------------------------------------
                                Módulo: erroresRegistroEmpleado

- Descripción: 
Permite visualizar a los empleados que han tenido algún error en el registro de su jornada laboral.

- Precondiciones:
El usuario debe estar autenticado.
Puede filtrar por año, mes y empleado.

- Postcondiciones:
Devuelve un listado de errores de registro de jornada laboral en función del filtro que se ha introducido por la url.

-------------------------------------------'''
def erroresRegistroEmpleado(request, idEmpleado, year=None, mes=None):
    id = idEmpleado
    festivos = None
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    if mes == None:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    else:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=mes).order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "mes":mes, 
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"festivos.html",infoVista)


def verVacacionesSeleccionadas(request, id):
    
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'empleado__id','fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos', 'estado__id','estado__nombre','estado')[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=vacaciones["empleado__id"])[0]

    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    
    if not admin and not director and empleado.id != request.user.id:
        return redirect('timetrackpro:sin-permiso')
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "admin":admin,
        "director":director,
        "vacaciones":vacaciones,
        "empleado":empleado,
    }
    return render(request,"verVacacionesSeleccionadas.html", infoVista)


def modificarVacaciones(request, id):
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    admin = esAdministrador(request.user.id)
    
    if request.method == 'POST' and admin:
        vacaciones.fecha_inicio = request.POST.get("fecha_inicio")
        vacaciones.fecha_fin = request.POST.get("fecha_fin")
        vacaciones.dias_consumidos = request.POST.get("dias_consumidos")
        vacaciones.save(using='timetrackpro')

        return redirect('timetrackpro:vacaciones-solicitadas')
    else:
        return redirect('timetrackpro:sin-permiso')
    
def cambiarEstadoVacaciones(request, id):
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]

    if request.method == 'POST':
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1,id=estado)[0]
        vacaciones.estado = nuevoEstado
        vacaciones.save(using='timetrackpro')
        return redirect('timetrackpro:vacaciones-solicitadas')
    else:
        return redirect('timetrackpro:sin-permiso')

def eliminarVacaciones(request):
    if request.method == 'POST':
        id = request.POST.get("id_vacaciones")
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
        vacaciones.delete(using='timetrackpro')
        return redirect('timetrackpro:vacaciones-solicitadas')
    else:
        return redirect('timetrackpro:vacaciones-solicitadas')

def modificarAsuntosPropios(request):
    admin = esAdministrador(request.user.id)
    
    if request.method == 'POST' and admin:
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
        return redirect('timetrackpro:sin-permiso')
    
def cambiarEstadoAsuntosPropios(request, id=None):

    if request.method == 'POST':
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
        return redirect('timetrackpro:solicitar-asuntos-propios')
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido cambiar el estado del asunto propio")

def eliminarAsuntosPropios(request, id=None):
    if request.method == 'POST':
        if id == None:
            id = request.POST.get("id_asunto_eliminar")
        asunto = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]
        asunto.delete(using='timetrackpro')
        return redirect('timetrackpro:solicitar-asuntos-propios')
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido eliminar el asunto propio")

def solicitarModificarAsuntosPropios(request):
    # guardo los datos en un diccionario
    if request.method == 'POST':
        # obtenemos los datos del empleado
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        idEmpleado = user.id_empleado.id
        solicitante = Empleados.objects.using("timetrackpro").filter(id=idEmpleado)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
        # obtenemos los datos del formulario
        idVacaciones = request.POST.get("vacaciones_modificar")
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=idVacaciones)[0]
        estadoPendiente = EstadosSolicitudes.objects.using("timetrackpro").filter(id=12)[0]
        vacaciones.estado = estadoPendiente
        vacaciones.save(using='timetrackpro')
        fechaInicioActual = request.POST.get("fechaActualInicio")
        fechaFinActual = request.POST.get("fechaActualFin")
        diasConsumidosActual = request.POST.get("dias_actuales_consumidos")
        fechaSolicitud = datetime.now()
        fechaNuevaInicio = request.POST.get("fechaInicioNueva")
        fechaNuevaFin = request.POST.get("fechaFinNueva")
        diasConsumidosNuevos = request.POST.get("dias_nuevos_consumidos")
        motivoCambio = request.POST.get("motivo_cambio")
        solicitudModificacionVacaciones = CambiosVacacionesTimetrackpro(id_periodo_cambio=vacaciones, solicitante=solicitante, fecha_inicio_actual=fechaInicioActual, fecha_fin_actual=fechaFinActual, dias_actuales_consumidos=diasConsumidosActual, fecha_solicitud=fechaSolicitud, fecha_inicio_nueva=fechaNuevaInicio, fecha_fin_nueva=fechaNuevaFin, dias_nuevos_consumidos=diasConsumidosNuevos, motivo_solicitud=motivoCambio, estado=estado)
        solicitudModificacionVacaciones.save(using='timetrackpro')
    return redirect('timetrackpro:solicitar-vacaciones')


def documentacion(request):
    return render(request,"documentation.html",{})

def perfil(request):
    # current_url = request.path[1:]
    
    return render(request,"profile.html",{"navBar":navBar, })

def dashBoard(request):
    
    return render(request,"dashboard.html",{"navBar":navBar})

def tablas(request):        
    # obtengo los datos necesarios para la vista
    

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


'''-------------------------------------------
        Permisos de empleados
-------------------------------------------'''
'''-------------------------------------------
                                Módulo: permisos

- Descripción: 
listado de permisos reconocidos que cualquier empleado puede disfrutar

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def datosPermisos(request, year=None):
    # obtengo los datos necesarios para la vista
    if year == None:
        permisos = Permisos.objects.using("timetrackpro").values('id','nombre', 'duracion', 'naturales_o_habiles', 'periodo_antelacion', 'fecha_maxima_solicitud', 'acreditar', 'doc_necesaria', 'legislacion_aplicable', 'bonificable_por_antiguedad', 'bonificacion_por_15_years', 'bonificacion_por_20_years', 'bonificacion_por_25_years', 'bonificacion_por_30_years', 'year', 'es_permiso_retribuido', 'pas', 'pdi')
    else:
        permisos = Permisos.objects.using("timetrackpro").filter(year=year).values('id','nombre', 'duracion', 'naturales_o_habiles', 'periodo_antelacion', 'fecha_maxima_solicitud', 'acreditar', 'doc_necesaria', 'legislacion_aplicable', 'bonificable_por_antiguedad', 'bonificacion_por_15_years', 'bonificacion_por_20_years', 'bonificacion_por_25_years', 'bonificacion_por_30_years', 'year', 'es_permiso_retribuido', 'pas', 'pdi')

    # devuelvo la lista en formato json
    return JsonResponse(list(permisos), safe=False)

'''-------------------------------------------
                                Módulo: permisos

- Descripción: 
listado de permisos reconocidos que cualquier empleado puede disfrutar

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def permisos(request, year=None):
    # obtengo los datos necesarios para la vista

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "alerta":alerta,
    }
    return render(request,"permisos.html", infoVista)


'''-------------------------------------------
                         Módulo: agregarPermiso

- Descripción: 
vista que permite agregar un permiso a la base de datos

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Agregar un permiso a la base de datos y redirigir a la vista de permisos

-------------------------------------------'''
def agregarPermiso(request, year=None):
    # obtengo los datos necesarios para la vista
    
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
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
        nuevoPermiso = Permisos(nombre=nombre, duracion=duracion, naturales_o_habiles=tipoDias, periodo_antelacion=periodoAntelacion, fecha_maxima_solicitud=fechaLimite, acreditar=acreditable, doc_necesaria=documentacionJustificativa, legislacion_aplicable=legislacionAplicable, bonificable_por_antiguedad=bonificable, bonificacion_por_15_years=bonificacion_15, bonificacion_por_20_years=bonificacion_20, bonificacion_por_25_years=bonificacion_25, bonificacion_por_30_years=bonificacion_30, year=year, es_permiso_retribuido=retribuido, pdi=pdi, pas=pas)
        nuevoPermiso.save(using='timetrackpro')
        alerta.activa = True
        alerta.icono = iconosAviso["success"]
        alerta.tipo = "success"
        alerta.mensaje = "Permiso agregado correctamente."
        return redirect('timetrackpro:permisos', year=year)
            # return redirect('timetrackpro:permisos', id=nuevoRegistro.id)
    else:
        return render(request,"agregar-permisos.html", infoVista)
    
'''-------------------------------------------
                                Módulo: verPermiso

- Descripción: 
Muestra la información de cada uno de los permisos registrados en la base de datos

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def verPermiso(request, id):
    permiso = Permisos.objects.using("timetrackpro").filter(id=id)[0]
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "permiso":permiso,
    }
    return render(request,"verPermiso.html",infoVista)


'''-------------------------------------------
                                Módulo: editarPermiso

- Descripción: 
edita la informacion de un permiso en la base de datos

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def editarPermiso(request):
    id = request.POST.get("id_permiso")

    permiso = Permisos.objects.using("timetrackpro").filter(id=id)[0]

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


'''-------------------------------------------
                                Módulo: registroManualControlHorario

- Descripción: 
Permite agregar información necesaria para el registro manual de la jornada laboral de un empleado
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def insertarRegistroManualMensual(request):
    festivos = FestivosTimetrackPro.objects.using("timetrackpro").values()
    admin = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "admin":admin,
        "festivos":list(festivos)
    }
    return render(request,"insertar-registro-mensual.html",infoVista)

def solicitarAsuntosPropios(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    empleados = Empleados.objects.using("timetrackpro").values()
    sustitutos = Sustitutos.objects.using("timetrackpro").values()
    asuntosPropiosEmpleados = []
    diasConsumidos = 0
    if administrador or director:
        if year is None:
            asuntosPropiosEmpleados = AsuntosPropios.objects.using("timetrackpro").values()
        else:
            asuntosPropiosEmpleados = AsuntosPropios.objects.using("timetrackpro").filter(year=year).values()

    if not director:
        if year is None:
            asuntos = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado).values()
        else:
            asuntos = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado).values()
        
        for a in asuntos:
            diasConsumidos += a['dias_consumidos']

    if year is None:
        year = str(datetime.now().year)
    mes = str(datetime.now().month)
    if len(mes) == 1:
        mesInicial = "0" + mesInicial
    initialDate = year + "-" + mes + "-01"
    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        diasConsumidos = request.POST.get("dias_consumidos")
        
        recuperable = 0 
        if request.POST.get("recuperable") == 1:
            recuperable = 1

        tareasASustituir = None
        if request.POST.get("tareas_a_sustituir") != "":
            tareasASustituir = request.POST.get("tareas_a_sustituir")

        descripcion = None
        if request.POST.get("descripcion") != "":
            descripcion = request.POST.get("descripcion")

        empleadoSustituto = request.POST.get("sustituto")
        if empleadoSustituto != 0:        
            sustituto = Sustitutos.objects.using("timetrackpro").filter(id=empleadoSustituto)[0] 
        else:
            sustituto = None

        if AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin).exists():
            return redirect('timetrackpro:solicitar-asuntos-propios')
        else:
            estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
            fechaSolicitud = datetime.now()
            year = fechaInicio.split("-")[0]
            nuevoAsuntoPropio = AsuntosPropios(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_consumidos=diasConsumidos, estado=estado, fecha_solicitud=fechaSolicitud, year=year, recuperable=recuperable, descripcion=descripcion, tareas_a_sustituir=tareasASustituir, sustituto=sustituto)
            nuevoAsuntoPropio.save(using='timetrackpro')

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
        "sustitutos":list(sustitutos),
    }
    return render(request,"solicitar-asuntos-propios.html",infoVista)

def datosAsuntosPropiosEmpleados(request, year=None):
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    diasSolicitados = []

    if admin or director:
        if year is None:
            diasSolicitados = AsuntosPropios.objects.using("timetrackpro").values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
        else:
            diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(year=year).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')

        return JsonResponse(list(diasSolicitados), safe=False)
    else:
        return JsonResponse([], safe=False)


def datosAsuntosPropiosSolicitados(request, year=None):
    admin = esAdministrador(request.user.id)
    if admin:
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
        diasSolicitados = []
        if year is None:
            diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
        else:
            diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
        
        return JsonResponse(list(diasSolicitados), safe=False)
    else:
        return JsonResponse([], safe=False)


def solicitarVacaciones(request):
    estados = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1).values()
    periodosVacaciones = TipoVacaciones.objects.using("timetrackpro").values()
    # obtengo los datos necesarios para la vista
    authUser = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.user.id)[0]
    usuario = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=authUser)[0]
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
    if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=usuario.id_usuario, year=int(datetime.now().year)).exists():
        vacacionesEncontradas = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=usuario.id_usuario, year=int(datetime.now().year)).values('id','tipo_vacaciones__nombre', 'year', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado__nombre', 'estado__id','fecha_solicitud', 'tipo_vacaciones__color')
        for v in vacacionesEncontradas:
            print(v)
            vacaciones.append(v)


    if CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(solicitante=usuario.id_usuario,estado__in=EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1, id__in=(9, 10))).exists():

        cambiosEncontrados = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(solicitante=usuario.id_usuario,estado__in=EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1, id__in=(9, 10))).values('id', 'solicitante', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__year', 'id_periodo_cambio__fecha_inicio', 'id_periodo_cambio__fecha_fin', 'id_periodo_cambio__dias_consumidos', 'id_periodo_cambio__estado__nombre', 'id_periodo_cambio__estado__id', 'id_periodo_cambio__fecha_solicitud', 'id_periodo_cambio__tipo_vacaciones__color', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado__nombre', 'estado__id', 'motivo_rechazo', 'fecha_solicitud', 'id_periodo_cambio__id')
        for c in cambiosEncontrados:
            cambios.append(c)


    festivos = []
    if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).exists():
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    
    initialDate = year + "-" + mes + "-" + diaInicial
    
    
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "initialDate":initialDate,
        "tipoFestivos":list(tipoFestivos),
        "usuario":usuario,
        "estados":list(estados),
        "periodosVacaciones":list(periodosVacaciones),
        "vacaciones":vacaciones, 
        "cambios":cambios
    }

    if request.method == 'POST':
        print("------------------------------------")
        print(request.POST)
        print("------------------------------------")
        # obtenemos los datos del empleado
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        idEmpleado = user.id_empleado.id
        empleado = Empleados.objects.using("timetrackpro").filter(id=idEmpleado)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
        # obtenemos los datos del formulario
        tipoVacaciones = TipoVacaciones.objects.using("timetrackpro").filter(id=request.POST.get("tipo_dias"))[0]
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        diasConsumidos = request.POST.get("dias_consumidos")
        fechaSolicitud = datetime.now()
    
        year = fechaInicio.split("-")[0]
        # compruebo si ya existe un registro de vacaciones para ese periodo 
        if VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=empleado, fecha_inicio=fechaInicio).exists():
            return redirect('timetrackpro:ups', mensaje="Parece que ya existe una solicitud de vacaciones para esas fechas.")
        else:
            nuevoRegistroVacaciones = VacacionesTimetrackpro(empleado=empleado, tipo_vacaciones=tipoVacaciones, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_consumidos=diasConsumidos, fecha_solicitud=fechaSolicitud, year=year, estado=estado)
            nuevoRegistroVacaciones.save(using='timetrackpro')
            return redirect('timetrackpro:solicitar-vacaciones')   
    
    return render(request,"solicitarVacaciones.html", infoVista)


def solicitarModificarVacaciones(request):
    # guardo los datos en un diccionario
    if request.method == 'POST':
        # obtenemos los datos del empleado
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        idEmpleado = user.id_empleado.id
        solicitante = Empleados.objects.using("timetrackpro").filter(id=idEmpleado)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=9)[0]
        # obtenemos los datos del formulario
        idVacaciones = request.POST.get("vacaciones_modificar")
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=idVacaciones)[0]
        estadoPendiente = EstadosSolicitudes.objects.using("timetrackpro").filter(id=12)[0]
        vacaciones.estado = estadoPendiente
        vacaciones.save(using='timetrackpro')
        fechaInicioActual = request.POST.get("fechaActualInicio")
        fechaFinActual = request.POST.get("fechaActualFin")
        diasConsumidosActual = request.POST.get("dias_actuales_consumidos")
        fechaSolicitud = datetime.now()
        fechaNuevaInicio = request.POST.get("fechaInicioNueva")
        fechaNuevaFin = request.POST.get("fechaFinNueva")
        diasConsumidosNuevos = request.POST.get("dias_nuevos_consumidos")
        motivoCambio = request.POST.get("motivo_cambio")
        solicitudModificacionVacaciones = CambiosVacacionesTimetrackpro(id_periodo_cambio=vacaciones, solicitante=solicitante, fecha_inicio_actual=fechaInicioActual, fecha_fin_actual=fechaFinActual, dias_actuales_consumidos=diasConsumidosActual, fecha_solicitud=fechaSolicitud, fecha_inicio_nueva=fechaNuevaInicio, fecha_fin_nueva=fechaNuevaFin, dias_nuevos_consumidos=diasConsumidosNuevos, motivo_solicitud=motivoCambio, estado=estado)
        solicitudModificacionVacaciones.save(using='timetrackpro')
    return redirect('timetrackpro:solicitar-vacaciones')

def solicitudes(request):
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "director":esDirector(request.user.id),
    }
    return render(request,"solicitudes.html", infoVista)

def verSolicitudesVacaciones(request):
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "admin":admin,
        "director":director,
        "empleados":list(empleados)
    }

    return render(request,"notificar-error-registro.html", infoVista)

def verSolicitudesVacaciones(request, id=None):
    
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados)
    }

    return render(request,"notificar-error-registro.html", infoVista)

def verSolicitudAsuntosPropios(request, id=None):
    if id is not None:
        solicitud = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]    
        empleado = Empleados.objects.using("timetrackpro").filter(id=solicitud.empleado.id)[0]
        diasConsumidos = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, year=solicitud.year).aggregate(Sum('dias_consumidos'))['dias_consumidos__sum']
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
    sustitutos = Sustitutos.objects.using("timetrackpro").values('id', 'nombre', 'apellidos')
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados),
        "solicitud":solicitud, 
        "diasConsumidos":diasConsumidos,
        "sustitutos":list(sustitutos),
    }

    return render(request,"ver-solicitud-asuntos-propios.html", infoVista)


def datosCalendarioAsuntosPropios(request, year=None):
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los festivos registrados en la base de datos
    festivos = []
    salidaFestivos = []
    if year == None:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
    else:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=year).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
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
    asuntosPropios = []
    salidaAsuntosPropios = []
    if not admin and not director:
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
        if year == None:
            asuntosPropios = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
        else:
            asuntosPropios = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
        # recorro los festivos y los guardo en la lista
        for asunto in asuntosPropios:
            # inserto los datos en la lista siguiendo la estructura que requiere el calendario
            salidaAsuntosPropios.append({
                'id':asunto['id'],
                'title':asunto['empleado__nombre'] + " " + asunto['empleado__apellidos'],
                'start':asunto['fecha_inicio'],
                'end':asunto['fecha_fin'],
                'color':'#555555',
                'textColor':'#fff', 
                'borderColor':'#555555'
            })
    else:
        if year == None:
            asuntosPropios = AsuntosPropios.objects.using("timetrackpro").values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin')
        else:
            asuntosPropios = AsuntosPropios.objects.using("timetrackpro").filter(year=year).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin')
        # recorro los festivos y los guardo en la lista
        for asunto in asuntosPropios:
            # sumar un día a la fecha de fin
            asunto['fecha_fin'] = asunto['fecha_fin'] + timedelta(days=1)
            # inserto los datos en la lista siguiendo la estructura que requiere el calendario
            salidaAsuntosPropios.append({
                'id':asunto['id'],
                'title':asunto['empleado__nombre'] + " " + asunto['empleado__apellidos'],
                'start':asunto['fecha_inicio'],
                'end':asunto['fecha_fin'],
                'color':'#555555',
                'textColor':'#fff', 
                'borderColor':'#555555'
            })
    
    # creo una lista vacía para guardar los datos de los festivos
    salida = salidaFestivos + salidaAsuntosPropios
    # devuelvo la lista en formato json
    return JsonResponse(salida, safe=False)


def agregarAsuntosPropiosCalendario(request):
    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
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
        if empleadoSustituto != 0:        
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
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    if request.method == 'POST':
        idEmpleadoMaquina = request.POST.get("idEmpleadoMaquina")
        empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=idEmpleadoMaquina)[0]
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



'''-------------------------------------------
                                Módulo: subirDocumento

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def subirDocumento(f, destino):
    with open(destino, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
