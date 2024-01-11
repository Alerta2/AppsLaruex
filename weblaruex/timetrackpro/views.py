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
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse





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
        "alerta":alerta,
        "rutaActual": "Habilitaciones"
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

@login_required
def tarjetasAcceso(request):
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
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    tarjetasActivas = []
    if administrador or director:
        tarjetasActivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).order_by("nombre").values()
    return JsonResponse(list(tarjetasActivas), safe=False)

@login_required   
def datosTarjetasAccesoInactivas(request):
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
    administrador = esAdministrador(request.user.id)
    if administrador:
        empleados = AuthUserTimeTrackPro.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

        return JsonResponse(list(empleados), safe=False)
    else:
        return redirect('timetrackpro:sin-permiso')

@login_required
def agregarTarjetaAcceso(request):
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
        # guardo los datos en un diccionario
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los datos necesarios para la vista
    archivos = []
    if administrador or director:
        archivos = RegistrosJornadaInsertados.objects.using("timetrackpro").order_by('year', 'mes').all()
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "archivos":list(archivos), 
        "rutaActual": "Registros insertados"
    }
    return render(request,"registros-insertados.html",infoVista)



@login_required
def datosRegistrosInsertados(request):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registros = []
    if administrador or director:
        registros = RegistrosJornadaInsertados.objects.using("timetrackpro").values('id', 'seccion', 'mes', 'year', 'fecha_lectura', 'insertador__first_name', 'insertador__last_name', 'ruta')
    return JsonResponse(list(registros), safe=False)



def obtenerRegistro(request, year=None, mes=None, semana=None):
    #empleados de las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
    administrador = esAdministrador(request.user.id)
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
    }
    return render(request,"informeRegistro.html",infoVista)

def obtenerRegistroUsuario(request, id=None, year=None, mes=None, semana=None):
    administrador = esAdministrador(request.user.id)
    #empleados de las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()

    # current_url = request.path[1:]
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
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


@login_required
def verRegistro(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registro = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=id)[0]
    maquina = MaquinaControlAsistencia.objects.using("timetrackpro").filter(nombre__icontains=registro.seccion)[0]

    ruta = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_NUEVO + registro.ruta
    ruta_leido = settings.MEDIA_DESARROLLO_TIMETRACKPRO + settings.RUTA_REGISTROS_INSERTADOS + registro.ruta
    IdEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]

    if request.method == 'POST' and administrador:
        print("-- Entro en el post --")
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
                # Comprobar si en la base de datos existen registros con el mismo id_archivo_leido
                if Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).exists():
                    registrosYaInsertados = Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).values()
                    for r in registrosYaInsertados:
                        if r["id_empleado"] == empleado.id and r["hora"] == hora:
                            continue
                        else:
                            # Si no existe, crea un nuevo registro en la base de datos
                            nuevoRegistro = Registros(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                            nuevoRegistro.save()
                else:
                    # Si no existe, crea un nuevo registro en la base de datos
                    nuevoRegistro = Registros(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                    nuevoRegistro.save()
        # Mover el archivo a la nueva ruta después de procesarlo
        shutil.move(ruta, ruta_leido)

    if Registros.objects.using("timetrackpro").filter(id_archivo_leido=registro.id, id_empleado=IdEmpleado.id).exists() or administrador or director:
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "registro":registro,
            "rutaActual":"Registros insertados" + " / " + str(registro.seccion) + " / " + str(registro.mes) + " / " + str(registro.year),
        }
        return render(request,"verRegistro.html",infoVista)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para ver el registro seleccionado.")

    # guardo los datos en un diccionario



@login_required
def actulizarRegistro(request, id):
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
            print("-- Entro en el post --")
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
                    # Comprobar si en la base de datos existen registros con el mismo id_archivo_leido
                    if Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).exists():
                        registrosYaInsertados = Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).values()
                        for r in registrosYaInsertados:
                            if r["id_empleado"] == empleado.id and r["hora"] == hora:
                                continue
                            else:
                                # Si no existe, crea un nuevo registro en la base de datos
                                nuevoRegistro = Registros(id_empleado=empleado, nombre_empleado=nombre, hora=hora, maquina=maquina, remoto=0, id_archivo_leido=registro)
                                nuevoRegistro.save()
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
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para actualizar el registro seleccionado.")

@login_required
def datosRegistro(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    registros = []
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id).values('id_empleado__id')
    if administrador or director:
        registros = Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    else:
        registros = Registros.objects.using("timetrackpro").filter(id_archivo_leido=id, id_empleado__id__in=empleado).values('id','id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name', 'remoto')
    return JsonResponse(list(registros), safe=False)

@login_required
def verLineaRegistro(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id).values('id_empleado__id')

    if Registros.objects.using("timetrackpro").filter(id=id, id_empleado__id__in=empleado).exists() or administrador or director:     
        registro = Registros.objects.using("timetrackpro").filter(id=id)[0]
   
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
def editarLineaRegistro(request, id):
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        registro = Registros.objects.using("timetrackpro").filter(id=id)[0]

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

def eliminarLineaRegistro(request, id):
    registro = Registros.objects.using("timetrackpro").filter(id=id)[0]
    archivoModificado = RegistrosJornadaInsertados.objects.using("timetrackpro").filter(id=registro.id_archivo_leido.id)[0]
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
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
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para eliminar el registro seleccionado.")

@login_required
def verMisErroresNotificados(request):
        
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": "Mis errores notificados",
    }
    return render(request,"mis-errores-notificados.html",infoVista)

@login_required
def datosMisErroresNotificados(request):
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
    idFilter = None
    
    if (id is None):
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").values()
    else:
        errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id_empleado=id).values()
        idFilter = id
    
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "errores":list(errores),
        "idFilter":idFilter,
        "rutaActual": "Errores notificados",
    }
    return render(request,"errores-registrados.html",infoVista)


@login_required
def verErroresNotificadosPendientes(request):
    administrador = esAdministrador(request.user.id)
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "rutaActual": "Errores notificados pendientes",
    }
    return render(request,"errores-registrados-pendientes.html",infoVista)

def datosErroresNotificadosPendientes(request):
    # obtengo los festivos registrados en la base de datos
    errores = ErroresRegistroNotificados.objects.using("timetrackpro").filter(estado=estadosErrores['Pendiente']).values('id','hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica', 'quien_notifica__id', 'quien_notifica__first_name','quien_notifica__last_name', 'id_empleado' , 'id_empleado__id_empleado', 'id_empleado__id_empleado__id', 'id_empleado__id_empleado__nombre') 
    # devuelvo la lista en formato json
    return JsonResponse(list(errores), safe=False)

@login_required
def notificarErrorEnFichaje(request):
    
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "empleados":list(empleados), 
        "rutaActual": "Notificar error en fichaje",
    }
    if request.method == 'POST':
        idEmpleadoMaquina = request.POST.get("idEmpleadoMaquina")

        empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=idEmpleadoMaquina)[0]

        idEmpleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=empleado)[0]
        motivo = request.POST.get("motivoError")
        estado = 1 # indico que aún esta pendiente de revisar
        hora = request.POST.get("hora")
        if idEmpleado in request.POST:
            registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.POST.get("idEmpleado"))[0]
        else:
            registrador = AuthUserTimeTrackPro.objects.using("timetrackpro").filter(id=request.user.id)[0]
        horaNotificacion = datetime.now()

        nuevoErrorRegistrado = ErroresRegistroNotificados(id_empleado=idEmpleado, hora=hora, motivo=motivo, estado=estado, quien_notifica=registrador, hora_notificacion=horaNotificacion)
        nuevoErrorRegistrado.save(using='timetrackpro')
        return redirect('timetrackpro:ver-errores-notificados', id=idEmpleadoMaquina)   
     
    return render(request,"notificar-error-registro.html", infoVista)



@login_required
def verErrorRegistroNotificado(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id).values('id','id_empleado','id_empleado__id','id_empleado__id', 'hora', 'motivo', 'estado', 'motivo_rechazo', 'quien_notifica')[0]
    # compruebo si el empleado que ha notificado el error es el mismo que el que lo ha registrado
    if administrador or director or error['id_empleado__id'] == empleado.id_empleado.id:
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
            "error":error,
            "empleado":empleado,
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
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    if administrador:
        if request.method == 'POST':
            motivo = None
            estado = request.POST.get("estado")
            if estado == estadosErrores['Rechazado']:
                motivo = request.POST.get("motivo")
            error.estado = estado
            error.motivo_rechazo = motivo
            error.save(using='timetrackpro')
    # guardo los datos en un diccionario
    return redirect('timetrackpro:ver-error-registro-notificado', id=id)

@login_required
def editarErrorRegistroNotificado(request, id):
    error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if administrador or director:
        if request.method == 'POST' and administrador:
            error.hora = request.POST.get("hora")
            if request.POST.get("empleadoModificado") != "":
                empleado = EmpleadosMaquina.objects.using("timetrackpro").filter(id=request.POST.get("empleadoModificado"))[0]
                error.id_empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_empleado=empleado)[0]
            error.save(using='timetrackpro')

        # guardo los datos en un diccionario
        return redirect('timetrackpro:ver-error-registro-notificado', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar el error seleccionado.")

@login_required
def eliminarErrorRegistroNotificado(request, id):
    administrador = esAdministrador(request.user.id)
    if administrador:
        error = ErroresRegistroNotificados.objects.using("timetrackpro").filter(id=id)[0]
        error.delete(using='timetrackpro')
        # guardo los datos en un diccionario
        return redirect('timetrackpro:ver-errores-registrados')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para eliminar el error seleccionado.")

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
    administrador = esAdministrador(request.user.id)
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')

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
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    empleados = []
    if not administrador or director:
        empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id','id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_auth_user__is_active', 'id_auth_user__is_superuser', 'id_auth_user__is_staff', 'id_auth_user__username', 'id_auth_user__password', 'id_auth_user__last_login', 'id_auth_user__date_joined')
    return JsonResponse(list(empleados), safe=False)

def agregarUsuario(request):
    
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
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar un usuario.")

@login_required
def usuariosMaquina(request):
        # obtengo los datos necesarios para la vista
    administrador = esAdministrador(request.user.id)

    usuariosMaquina = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

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
    administrador = esAdministrador(request.user.id)
    director =  esDirector(request.user.id)
    usersMaquina=[]
    if administrador or director:
        usersMaquina = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

    return JsonResponse(list(usersMaquina), safe=False)

@login_required
def agregarUsuarioMaquina(request):
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
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para agregar un usuario.")



def verUsuarioMaquina(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # declaro las variables que voy a usar
    idUser, nombre, turno, horas_maxima_contrato, en_practicas, maquina_laboratorio, maquina_alerta2, maquina_departamento, relUser, huellas = None, None, None, None, None, None, None, None, None, None

    pin, esAdmin, ficharRemoto = 0, 0, 0

    # obtengo los datos necesarios para la vista
    
    usuarioMaquina = EmpleadosMaquina.objects.using("timetrackpro").filter(id=id)[0]
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
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    usuario = Empleados.objects.using("timetrackpro").filter(id=id)[0]
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
    usuariosApp = Empleados.objects.using("timetrackpro").values()
    administrador = esAdministrador(request.user.id)
    # datos de los empleados registrados en las máquinas de control de asistencia
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values()
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
    administrador = esAdministrador(request.user.id)
    if administrador:
        
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
            "rutaActual": "Editar asociación de usuario",
            "rutaPrevia": "Usuarios de la aplicación",
            "urlRutaPrevia": reverse('timetrackpro:empleados')
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
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para editar la asociación del usuario.")


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



@login_required
def datosFestivosVacacionesEmpleado(request):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)

    year = datetime.now().year
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    estadoAceptado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=11)[0]
    usuario = Empleados.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]
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

@login_required
def vacacionesSolicitadas(request):
    administrador = esAdministrador(request.user.id)
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
        "administrador":administrador,
        "initialDate":initialDate,
        "director":director
    }
    return render(request,"vacaciones-solicitadas.html",infoVista)

@login_required
def datosVacacionesSolicitadas(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if year == None:
        year = datetime.now().year
     # obtengo los datos necesarios para la vista
    salida = []
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    usuario = Empleados.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]

    if administrador or director:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(estado__in=[9,10,11],year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos')
    else:
        vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=usuario, estado__in=[9,10,11],year=year).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos')
    return JsonResponse(list(vacaciones),safe=False)

def datosCambioVacacionesSolicitadas(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if year == None:
        year = datetime.now().year
     # obtengo los datos necesarios para la vista
    empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    usuario = Empleados.objects.using("timetrackpro").filter(id=empleado.id_usuario.id)[0]
    cambiosVacaciones = []
    if administrador or director:
        cambiosVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(fecha_inicio_actual__year=year).values('id', 'solicitante', 'solicitante__nombre', 'solicitante__apellidos', 'id_periodo_cambio', 'id_periodo_cambio__tipo_vacaciones', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__tipo_vacaciones__color', 'id_periodo_cambio__tipo_vacaciones__color_calendario', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado', 'motivo_rechazo', 'fecha_solicitud')
    else:
        cambiosVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(empleado=usuario, fecha_inicio_actual__year=year).values('id', 'solicitante', 'solicitante__nombre', 'solicitante__apellidos', 'id_periodo_cambio', 'id_periodo_cambio__tipo_vacaciones', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__tipo_vacaciones__color', 'id_periodo_cambio__tipo_vacaciones__color_calendario', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado', 'motivo_rechazo', 'fecha_solicitud')

    # creo una lista vacía para guardar los datos de los festivos
    # devuelvo la lista en formato json
    return JsonResponse(list(cambiosVacaciones),safe=False)


@login_required
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
@login_required
def calendarioFestivos(request, mes=None, year=None):
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
    administrador = esAdministrador(request.user.id)
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

    return redirect('timetrackpro:festivos-year', year=datetime.now().year)

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

    

@login_required
def editarFestivo(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(id=id)[0]
    # current_url = request.path[1:]
    
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    if request.method == 'POST' and (administrador or director):
        festivo.nombre = request.POST.get("nombre_festividad_editar")
        idTipo = request.POST.get("tipo_festividad_editar")
        tipo = TipoFestivos.objects.using("timetrackpro").filter(id=idTipo)[0]
        festivo.tipo_festividad = tipo
        festivo.fecha_inicio = request.POST.get("fecha_inicio_editar")
        festivo.year = request.POST.get("year_editar")
        festivo.fecha_fin = request.POST.get("fecha_fin_editar")  
        festivo.save(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=festivo.year)    

    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "tipoFestivos":list(tipoFestivos),
        "festivo":festivo, 
        "rutaActual": "Editar festivo",
        "rutaPrevia": "Festivos",
        "urlRutaPrevia": reverse('timetrackpro:festivos-year', year=festivo.year)
    }
    return render(request,"editarFestivo.html", infoVista)

@login_required
def eliminarFestivo(request, id):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # current_url = request.path[1:]
    festivo = FestivosTimetrackPro.objects.using("timetrackpro").filter(id=id)[0]
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
        "urlRutaPrevia": reverse('timetrackpro:festivos-year', year=festivo.year)
    }
    return render(request,"eliminarFestivo.html",{})

@login_required
def erroresRegistro(request, mes=None):
    administrador = esAdministrador(request.user.id)
    festivos = None
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    if mes == None:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    else:
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(year=mes).order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    # current_url = request.path[1:]
    
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
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
    
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id).values('id', 'tipo_vacaciones', 'tipo_vacaciones__nombre', 'tipo_vacaciones__color', 'tipo_vacaciones__color_calendario',  'year', 'empleado', 'empleado__id','fecha_inicio', 'fecha_fin', 'dias_consumidos', 'estado', 'fecha_solicitud', 'empleado__nombre','empleado__apellidos', 'estado__id','estado__nombre','estado')[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=vacaciones["empleado__id"])[0]

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

    vacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id).values('id','solicitante', 'solicitante__id', 'solicitante__nombre', 'solicitante__apellidos', 'id_periodo_cambio', 'fecha_inicio_actual' , 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos','motivo_solicitud', 'estado', 'estado__id','motivo_rechazo', 'fecha_solicitud','id_periodo_cambio__tipo_vacaciones__nombre' )[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=vacaciones["solicitante__id"])[0]

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
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    
    if request.method == 'POST' and administrador:
        vacaciones.fecha_inicio = request.POST.get("fecha_inicio")
        vacaciones.fecha_fin = request.POST.get("fecha_fin")
        vacaciones.dias_consumidos = request.POST.get("dias_consumidos")
        vacaciones.save(using='timetrackpro')

        return redirect('timetrackpro:ver-vacaciones-seleccionadas', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para modificar las vacaciones seleccionadas.")

@login_required
def cambiarEstadoVacaciones(request, id):
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
        return redirect('timetrackpro:solicitar-vacaciones')
    else:
        return redirect('timetrackpro:ups', mensaje="No tienes permiso para cambiar el estado de las vacaciones seleccionadas.")
    
@login_required
def eliminarVacaciones(request):
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
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    cambioVacaciones = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(id=id)[0]
    vacaciones = VacacionesTimetrackpro.objects.using("timetrackpro").filter(id=cambioVacaciones.id_periodo_cambio.id)[0]

    if request.method == 'POST' and (administrador or director):
        estado = request.POST.get("estado")
        nuevoEstado = EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1,id=estado)[0]
        cambioVacaciones.estado = nuevoEstado
        if cambioVacaciones.estado.id == 11:
            vacaciones.fecha_inicio = cambioVacaciones.fecha_inicio_nueva
            vacaciones.fecha_fin = cambioVacaciones.fecha_fin_nueva
            vacaciones.dias_consumidos = cambioVacaciones.dias_nuevos_consumidos
            vacaciones.save(using='timetrackpro')
        if cambioVacaciones.estado.id == 10:
            motivo = request.POST.get("motivo")
            cambioVacaciones.motivo_rechazo = motivo
        cambioVacaciones.save(using='timetrackpro')
        return redirect('timetrackpro:ver-cambio-vacaciones-seleccionadas', id=id)
    else:
        return redirect('timetrackpro:sin-permiso')
    
@login_required
def eliminarCambioVacaciones(request):
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
        return redirect('timetrackpro:solicitar-asuntos-propios')
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido cambiar el estado del asunto propio")

@login_required
def eliminarAsuntosPropios(request, id=None):
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
    # guardo los datos en un diccionario
    if request.method == 'POST':
        # obtenemos los datos del empleado
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        idEmpleado = user.id_empleado.id
        solicitante = Empleados.objects.using("timetrackpro").filter(id=idEmpleado)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=1)[0]
        # obtenemos los datos del formulario
        idAsuntosPropios = request.POST.get("asunto_modificar")
        asuntoPropio = AsuntosPropios.objects.using("timetrackpro").filter(id=idAsuntosPropios)[0]
        estadoPendiente = EstadosSolicitudes.objects.using("timetrackpro").filter(id=17)[0]
        asuntoPropio.estado = estadoPendiente
        asuntoPropio.save(using='timetrackpro')
        fechaInicioActual = request.POST.get("fechaActualInicio")
        fechaFinActual = request.POST.get("fechaActualFin")
        diasConsumidosActual = request.POST.get("dias_actuales_consumidos")
        fechaSolicitud = datetime.now()
        fechaNuevaInicio = request.POST.get("fechaInicioNueva")
        fechaNuevaFin = request.POST.get("fechaFinNueva")
        diasConsumidosNuevos = request.POST.get("dias_nuevos_consumidos")
        motivoCambio = request.POST.get("motivo_cambio")
        solicitudModificacionAsuntosPropios = CambiosAsuntosPropios(id_periodo_cambio=asuntoPropio, solicitante=solicitante, fecha_inicio_actual=fechaInicioActual, fecha_fin_actual=fechaFinActual, dias_actuales_consumidos=diasConsumidosActual, fecha_solicitud=fechaSolicitud, fecha_inicio_nueva=fechaNuevaInicio, fecha_fin_nueva=fechaNuevaFin, dias_nuevos_consumidos=diasConsumidosNuevos, motivo_solicitud=motivoCambio, estado=estado)
        solicitudModificacionAsuntosPropios.save(using='timetrackpro')
    return redirect('timetrackpro:solicitar-vacaciones')


def documentacion(request):
    return render(request,"documentation.html",{})

def perfil(request):
    # current_url = request.path[1:]
    
    return render(request,"profile.html",{"navBar":navBar, })

def dashBoard(request):
    
    return render(request,"dashboard.html",{"navBar":navBar})

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
    # obtengo los datos necesarios para la vista
    if year == None:
        year = datetime.now().year
    permisos = PermisosVacaciones.objects.using("timetrackpro").filter(year=year).values('id','nombre', 'duracion', 'naturales_o_habiles', 'periodo_antelacion', 'fecha_maxima_solicitud', 'acreditar', 'doc_necesaria', 'legislacion_aplicable', 'bonificable_por_antiguedad', 'bonificacion_por_15_years', 'bonificacion_por_20_years', 'bonificacion_por_25_years', 'bonificacion_por_30_years', 'year', 'es_permiso_retribuido', 'pas', 'pdi')

    # devuelvo la lista en formato json
    return JsonResponse(list(permisos), safe=False)

@login_required
def listaPermisos(request, year=None):
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
    # obtengo los datos necesarios para la vista
    permisos = PermisosRetribuidos.objects.using("timetrackpro").values('id', 'cod_uex', 'nombre', 'tipo__id', 'tipo__nombre', 'dias', 'habiles_o_naturales', 'solicitud_dias_naturales_antelacion', 'pas', 'pdi')

    # devuelvo la lista en formato json
    return JsonResponse(list(permisos), safe=False)

@login_required
def listaPermisosRetribuidos(request):
    administrador = esAdministrador(request.user.id)
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
        "alerta":alerta,
        "rutaActual": "Permisos reconocidos por la Uex",
    }
    return render(request,"permisos-retribuidos.html", infoVista)

@login_required
def agregarPermisoRetribuido(request, year=None):
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
        mes = "0" + mes
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
        "currentYear":year,
        "sustitutos":list(sustitutos),
        "rutaActual": "Asuntos propios "  + str(year),
        "rutaPrevia": "Solicitudes",
        "urlRutaPrevia": reverse('timetrackpro:solicitudes'),
    }
    return render(request,"solicitar-asuntos-propios.html",infoVista)

@login_required
def solicitarPermisosRetribuidos(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    empleados = Empleados.objects.using("timetrackpro").values()
    sustitutos = Sustitutos.objects.using("timetrackpro").values()
    asuntosPropiosEmpleados = []
    permisosSolicitadosEmpleados = []
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
    
    if request.method == 'POST':
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        idPermiso = request.POST.get("id_permiso")
        codigoPermiso = PermisosRetribuidos.objects.using("timetrackpro").filter(id=idPermiso)[0]
        fechaInicio = request.POST.get("fecha_inicio")
        fechaFin = request.POST.get("fecha_fin")
        if fechaFin == "":
            fechaFin = fechaInicio
        diasSolicitados = request.POST.get("dias_solicitados")
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(id=18)[0]
        fechaSolicitud = datetime.now()
        
        for p in permisosSolicitados:
            if p['fecha_inicio'] == fechaInicio:
                return redirect('timetrackpro:ups', mensaje='Ya existe un permiso retribuido para el día ' + fechaInicio + '')
        nuevoPermiso = PermisosYAusenciasSolicitados(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_solicitados=diasSolicitados, estado=estado, fecha_solicitud=fechaSolicitud, year=year, codigo_permiso=codigoPermiso)
        nuevoPermiso.save(using='timetrackpro')
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
    }
    return render(request,"solicitar-permisos-retribuidos.html",infoVista)

@login_required
def solicitarPermisoRetribuidoCalendario(request, year=None):
    if request.method == 'POST':
        permisos = PermisosYAusenciasSolicitados.objects.using("timetrackpro").values()
        user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
        empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0] 
        idPermiso = request.POST.get("id_permiso_calendario")
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
        nuevoPermiso = PermisosYAusenciasSolicitados(empleado=empleado, fecha_inicio=fechaInicio, fecha_fin=fechaFin, dias_solicitados=diasSolicitados, estado=estado, fecha_solicitud=fechaSolicitud, year=year, codigo_permiso=codigoPermiso)
        nuevoPermiso.save(using='timetrackpro')
        alerta["activa"] = True
        alerta["icono"] = iconosAviso["success"]
        alerta["tipo"] = "success"
        alerta["mensaje"] = "Permiso agregado correctamente."
    return redirect('timetrackpro:solicitar-permisos-retribuidos', year=year)

@login_required
def datosAsuntosPropiosEmpleados(request, year=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    idUser = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=idUser.id_usuario.id)[0]
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
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    diasSolicitados = []
    if year is None:
        year = datetime.now().year
    diasSolicitados = AsuntosPropios.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id','empleado__nombre','empleado__apellidos','empleado','year','dias_consumidos','fecha_solicitud','estado__nombre','estado__id','estado','fecha_inicio','fecha_fin', 'recuperable', 'descripcion', 'tareas_a_sustituir', 'sustituto__nombre', 'sustituto__apellidos', 'sustituto')
    
    return JsonResponse(list(diasSolicitados), safe=False)

@login_required   
def datosPermisosRetribuidosEmpleados(request, year=None):
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
    user = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_auth_user=request.user.id)[0]
    empleado = Empleados.objects.using("timetrackpro").filter(id=user.id_usuario.id)[0]
    permisosSolicitados = []
    if year is None:
        year = datetime.now().year

    permisosSolicitados = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(year=year,empleado=empleado).values('id', 'empleado__nombre', 'empleado__apellidos', 'empleado', 'year', 'dias_solicitados', 'fecha_solicitud', 'estado__nombre', 'estado__id', 'estado', 'fecha_inicio', 'fecha_fin', 'justificante', 'codigo_permiso__nombre', 'codigo_permiso__id', 'codigo_permiso')
    
    return JsonResponse(list(permisosSolicitados), safe=False)

@login_required
def verSolicitudPermisosRetribuidos(request, id=None):
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    if not request.POST:
        alerta['activa'] = False

    if id is not None:
        solicitud = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]    
        empleado = Empleados.objects.using("timetrackpro").filter(id=solicitud.empleado.id)[0]
        diasConsumidos = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(empleado=empleado, year=solicitud.year).aggregate(Sum('dias_solicitados'))['dias_solicitados__sum']
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
    sustitutos = Sustitutos.objects.using("timetrackpro").values('id', 'nombre', 'apellidos')
    permisos = PermisosRetribuidos.objects.using("timetrackpro").values('id', 'cod_uex', 'nombre', 'tipo__id', 'tipo__nombre', 'dias', 'habiles_o_naturales', 'solicitud_dias_naturales_antelacion', 'pas', 'pdi')
    if solicitud.empleado.id == request.user.id or director or administrador:
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
        return redirect('timetrackpro:ver-solicitud-permisos-retribuidos', id=id)
    else:
        return redirect('timetrackpro:ups', mensaje="No se ha podido cambiar el estado del permiso retribuido")

@login_required
def eliminarSolicitudPermisoRetribuido(request, id=None):
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
    administrador = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los datos necesarios para la vista    
    if request.method == 'POST':
        if id == None:
            id = request.POST.get("id_permiso_justificar")

        permiso = PermisosYAusenciasSolicitados.objects.using("timetrackpro").filter(id=id)[0]
        estado = EstadosSolicitudes.objects.using("timetrackpro").filter(permisos_retribuidos=1, id=21)[0]
        if permiso.empleado.id == request.user.id or director or administrador:
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
def actualizarJustificanteSolicitudPermisosRetribuidos(request, id):
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
            if request.POST.get("motivoEditar") != "":
                permiso.motivo = request.POST.get("motivoEditar")
            permiso.save(using='timetrackpro')

            return redirect('timetrackpro:ver-solicitud-permisos-retribuidos', id=id)
        return redirect('timetrackpro:solicitar-permisos-retribuidos')
    else:
        return redirect('timetrackpro:sin-permiso')
    

@login_required
def solicitarVacaciones(request):
    administrador = esAdministrador(request.user.id)
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

        cambiosEncontrados = CambiosVacacionesTimetrackpro.objects.using("timetrackpro").filter(solicitante=usuario.id_usuario,estado__in=EstadosSolicitudes.objects.using("timetrackpro").filter(vacaciones=1, id__in=(9, 10)), fecha_inicio_actual__contains=str(datetime.now().year)).values('id', 'solicitante', 'id_periodo_cambio__tipo_vacaciones__nombre', 'id_periodo_cambio__year', 'id_periodo_cambio__fecha_inicio', 'id_periodo_cambio__fecha_fin', 'id_periodo_cambio__dias_consumidos', 'id_periodo_cambio__estado__nombre', 'id_periodo_cambio__estado__id', 'id_periodo_cambio__fecha_solicitud', 'id_periodo_cambio__tipo_vacaciones__color', 'fecha_inicio_actual', 'fecha_fin_actual', 'dias_actuales_consumidos', 'fecha_inicio_nueva', 'fecha_fin_nueva', 'dias_nuevos_consumidos', 'motivo_solicitud', 'estado__nombre', 'estado__id', 'motivo_rechazo', 'fecha_solicitud', 'id_periodo_cambio__id')
        for c in cambiosEncontrados:
            cambios.append(c)

    festivos = []
    if FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).exists():
        festivos = FestivosTimetrackPro.objects.using("timetrackpro").filter(fecha_inicio__month=mes).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    
    initialDate = year + "-" + mes + "-" + diaInicial
    
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
    }

    if request.method == 'POST':
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


@login_required
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

@login_required
def solicitudes(request):
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
    administrador = esAdministrador(request.user.id)
    if id is not None:
        solicitud = AsuntosPropios.objects.using("timetrackpro").filter(id=id)[0]    
        empleado = Empleados.objects.using("timetrackpro").filter(id=solicitud.empleado.id)[0]
        diasConsumidos = AsuntosPropios.objects.using("timetrackpro").filter(empleado=empleado, year=solicitud.year).aggregate(Sum('dias_consumidos'))['dias_consumidos__sum']
        empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
        sustitutos = Sustitutos.objects.using("timetrackpro").values('id', 'nombre', 'apellidos')
        # guardo los datos en un diccionario
        infoVista = {
            "navBar":navBar,
            "administrador":administrador,
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
    admin = esAdministrador(request.user.id)
    director = esDirector(request.user.id)
    # obtengo los festivos registrados en la base de datos
    festivos = []
    salidaFestivos = []
    if year == None:
        year = datetime.now().year

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


@login_required
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
    administrador = esAdministrador(request.user.id)
    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":administrador,
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





@login_required
def notificarProblemas(request):
    
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
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
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
        estado = estadosErrores["Pendiente"]
        fechaRegistro = datetime.now()
        motivo = request.POST.get("motivoError")
        tipo = "2"
        error = ProblemasDetectadosTimeTrackPro(usuario=usuario, estado=estado, fecha_registro=fechaRegistro, problema_detectado=motivo, tipo=tipo)
        error.save(using='timetrackpro')

        return redirect('timetrackpro:ver-errores-notificados', id=error.id)   
     
    return render(request,"notificar-incidencia.html", infoVista)



@login_required
def notificarErroresApp(request):
    
    empleados = EmpleadosMaquina.objects.using("timetrackpro").values('id', 'nombre')
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
        estado = estadosErrores["Pendiente"]
        fechaRegistro = datetime.now()
        motivo = request.POST.get("motivoError")
        tipo = "1"
        error = ProblemasDetectadosTimeTrackPro(usuario=usuario, estado=estado, fecha_registro=fechaRegistro, problema_detectado=motivo, tipo=tipo)
        error.save(using='timetrackpro')

        return redirect('timetrackpro:ver-errores-notificados', id=error.id)    
     
    return render(request,"notificar-incidencia.html", infoVista)


@login_required
def problemasNotificados(request):
    infoVista = {
        "navBar":navBar,
        "administrador":esAdministrador(request.user.id),
        "rutaActual": "Incidencias notificadas",

    }
    return render(request,"listado-incidencias.html",infoVista)


@login_required   
def datosProblemasNotificados(request, tipo=None, estado=None):
    print('\033[91m'+'estado: ' + '\033[92m', estado)
    print('\033[91m'+'tipo: ' + '\033[92m', tipo)
    if tipo is None or tipo == "Todos":
        tipo = ["1", "2"]
    if estado is None or estado == "0":
        estado = ["1", "2", "3"]
    incidencias = ProblemasDetectadosTimeTrackPro.objects.using("timetrackpro").filter(tipo__in=tipo, estado__in=estado).values('id', 'usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario', 'fecha_registro', 'estado', 'problema_detectado', 'tipo')

    return JsonResponse(list(incidencias), safe=False)



@login_required
def verIncidencia(request, id):
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
    administrador = esAdministrador(request.user.id)
    if request.method == 'POST' and administrador:
        incidencia = ProblemasDetectadosTimeTrackPro.objects.using("timetrackpro").filter(id=id)[0]
        incidencia.delete(using='timetrackpro')
        return redirect('timetrackpro:listado-incidencias')
    return redirect('timetrackpro:ups', mensaje="No se ha podido eliminar la incidencia")
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
