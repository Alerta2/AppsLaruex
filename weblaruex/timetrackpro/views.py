import datetime
import os
import shutil
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from timetrackpro.models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import *
from datetime import date, datetime
from django.core.exceptions import ObjectDoesNotExist
import unicodedata
from django.db.models import Q



excluidos = ["Prueba", "Pruebas", "prueba", "pruebas", "PRUEBA", "PRUEBAS", "Usuario Pruebas",  "test", "TEST", "Test" , " ", "", "root", "CSN", "PCivil Provisional", "Protección Civil", "JEx", "Admin", "admin"]


def home(request):
    navBar = NavBar.objects.using("timetrackpro").values()
    return render(request,"home.html",{"navBar":navBar})

def tarjetasAcceso(request):
    infoGeneralTarjeta = settings.INFO_GENERAL_TARJETA_CONTACTO 

    infoPersonalTarjeta = settings.INFO_PERSONAL_TARJETA_CONTACTO
    infoContactoTarjeta = settings.INFO_AVISO_TARJETA_CONTACTO
    # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
    tarjetasActivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=1).order_by("nombre").values()
    tarjetasInactivas = TarjetasAcceso.objects.using("timetrackpro").filter(activo=0).order_by("nombre").values()

    # paginación tarjetas activas
    paginatorActivas = Paginator(tarjetasActivas, 5)  # Divide en páginas de 10 elementos
    numeroPaginaActivas = request.GET.get('page')
    tarjetasAccesoActivas = paginatorActivas.get_page(numeroPaginaActivas)

    # paginación tarjetas inactivas
    paginatorInactivas = Paginator(tarjetasInactivas, 5)  # Divide en páginas de 10 elementos
    numeroPaginaInactivas = request.GET.get('page')
    tarjetasAccesoInactivas = paginatorInactivas.get_page(numeroPaginaInactivas)

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tarjetasAccesoActivas":tarjetasAccesoActivas,
        "tarjetasAccesoInactivas":tarjetasAccesoInactivas, 
        "infoGeneralTarjeta":infoGeneralTarjeta,
        "infoPersonalTarjeta":infoPersonalTarjeta,
        "infoContactoTarjeta":infoContactoTarjeta
    }

    return render(request,"tarjetasAcceso.html", infoVista)


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
            nuevaTarjeta= TarjetasAcceso(nombre=nombre, apellidos=apellidos, dni=dni, imagen=imagen,acceso_laboratorios=acceso_laboratorios, acceso_cpd=acceso_cpd, acceso_alerta2=acceso_alerta2, id_tarjeta=id_tarjeta,fecha_alta=fechaActual, fecha_baja=fecha_expiracion, activo=0)
        else:
            nuevaTarjeta = TarjetasAcceso(nombre=nombre, apellidos=apellidos, dni=dni, imagen=imagen,acceso_laboratorios=acceso_laboratorios, acceso_cpd=acceso_cpd, acceso_alerta2=acceso_alerta2, id_tarjeta=id_tarjeta,fecha_alta=fechaActual, activo=0)
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

    return tarjetasAcceso(request)  

def verTarjetaAcceso(request, id):
    # información tarjeta acceso reverso
    infoGeneralTarjeta = settings.INFO_GENERAL_TARJETA_CONTACTO 
    infoPersonalTarjeta = settings.INFO_PERSONAL_TARJETA_CONTACTO
    infoContactoTarjeta = settings.INFO_AVISO_TARJETA_CONTACTO

    # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
    tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=id).values()[0]

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"verTarjetaAcceso.html", infoVista)
 

def editarTarjetaAcceso(request, id):
        # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
    tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(id=id)[0]


    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tarjeta":tarjeta
    }
    if request.method == 'POST':
        
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

        idTarjeta = str(request.POST.get("idTarjeta"))
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

        tarjeta.save(using='timetrackpro')


        if 'fotoSeleccionada' in request.FILES:
            print("--- imagen", request.FILES['fotoSeleccionada'])
            print("--- --------- ------ ----")
            if tarjeta.imagen is not None:
                rutaActual = settings.STATIC_ROOT + settings.RUTA_TARJETAS_TIMETRACKPRO + tarjeta.imagen
                if os.path.isfile(rutaActual):
                    os.remove(rutaActual)
            nombreArchivo = str(tarjeta.id) + '_tarjeta.' + request.FILES['fotoSeleccionada'].name.split('.')[-1]
            ruta = settings.STATIC_ROOT + settings.RUTA_TARJETAS_TIMETRACKPRO + nombreArchivo
            subirDocumento(request.FILES['fotoSeleccionada'], ruta)
            tarjeta.imagen = nombreArchivo
            tarjeta.save(using='timetrackpro')
        
        return render(request,"verTarjetaAcceso.html", infoVista)
    
    return render(request,"editar-tarjetaAcceso.html", infoVista)


def registrosInsertados(request):

    # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
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
    navBar = NavBar.objects.using("timetrackpro").values()
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
                empleado = Empleados.objects.using("timetrackpro").filter(id=id_empleado)[0]
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
    registros = Registros.objects.using("timetrackpro").filter(id_archivo_leido=id).values('id_empleado__nombre', 'hora', 'maquina__id', 'maquina__nombre', 'id_archivo_leido__mes', 'id_archivo_leido__year', 'id_archivo_leido__seccion', 'id_archivo_leido__fecha_lectura', 'id_archivo_leido__insertador__first_name', 'id_archivo_leido__insertador__last_name')
    empleados = AuthUser.objects.using("timetrackpro").values('id', 'first_name', 'last_name', 'is_active')
    
    
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



def agregarRegistro(request):
    navBar = NavBar.objects.using("timetrackpro").values()
    if request.method == 'POST':
        
        seccion = request.POST.get("seccion")
        mes = request.POST.get("mes")
        year = request.POST.get("year")
        fecha = datetime.now()
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
        nuevoRegistro = RegistrosJornadaInsertados(seccion=seccion, mes=mes, year=year, fecha_lectura=fecha, insertador=AuthUser.objects.using("timetrackpro").filter(id=int(request.POST.get("registrador")))[0], remoto=0)
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
    navBar = NavBar.objects.using("timetrackpro").values()
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
    navBar = NavBar.objects.using("timetrackpro").values()
    usuariosApp = AuthUser.objects.using("timetrackpro").values()
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
        if not Usuarios.objects.using("timetrackpro").filter(dni__icontains=dniEmpleado).exists():
            nuevoUsuario = Usuarios(nombre=nombreEmpleado, apellidos=apellidosEmpleado, puesto=puestoEmpleado, direccion=direccionEmpleado, telefono=telefonoEmpleado, telefono2=telefono2Empleado, email=emailEmpleado, email2=email2Empleado, dni=dniEmpleado, fecha_nacimiento=fechaNacimientoEmpleado, info_adicional=infoAdicionalEmpleado, extension=extensionEmpleado, fecha_alta_app=fechaAltaApp)
            nuevoUsuario.save(using='timetrackpro')

            if request.FILES['fotoEmpleadoSeleccionado']:
                nombreArchivo = str(nuevoUsuario.id) + '_usuario.' + request.FILES['fotoEmpleadoSeleccionado'].name.split('.')[-1]
                ruta = settings.STATIC_ROOT + settings.RUTA_USUARIOS_TIMETRACKPRO + nombreArchivo

                subirDocumento(request.FILES['fotoEmpleadoSeleccionado'], ruta)
                nuevoUsuario.img = nombreArchivo
                nuevoUsuario.save(using='timetrackpro')
        else:
            nuevoUsuario = Usuarios.objects.using("timetrackpro").filter(dni__icontains=dniEmpleado)[0]
        return redirect('timetrackpro:ver-empleado', id=nuevoUsuario.id)

    
    else:
        return render(request,"agregar-usuario.html",infoVista)


def usuariosMaquina(request):
        # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
    usuariosMaquina = Empleados.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "usuariosMaquina":list(usuariosMaquina)
    }
    return render(request,"usuariosMaquina.html",infoVista)

def datosUsuariosMaquina(request):
    usersMaquina = Empleados.objects.using("timetrackpro").values('id', 'nombre', 'turno', 'horas_maxima_contrato', 'en_practicas', 'maquina_laboratorio', 'maquina_alerta2', 'maquina_departamento')

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

        if not Empleados.objects.using("timetrackpro").filter(id=request.POST.get("id_empleado_maquina")).exists():
            nuevoUser = Empleados(id=id, nombre=nombre, turno=turno, horas_maxima_contrato=horas_maxima_contrato, en_practicas=en_practicas, maquina_laboratorio=maquina_laboratorio, maquina_alerta2=maquina_alerta2, maquina_departamento=maquina_departamento, permite_pin=pin, es_administrador=esAdmin, huellas_registradas=numHuellas, fichar_remoto=ficharRemoto)
            nuevoUser.save(using='timetrackpro')
        

    return redirect('timetrackpro:usuarios-maquina')


def verUsuarioMaquina(request, id):
    # declaro las variables que voy a usar
    idUser, nombre, turno, horas_maxima_contrato, en_practicas, maquina_laboratorio, maquina_alerta2, maquina_departamento, relUser, huellas = None, None, None, None, None, None, None, None, None, None

    pin, esAdmin, ficharRemoto = 0, 0, 0

    # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
    usuarioMaquina = Empleados.objects.using("timetrackpro").filter(id=id)[0]
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
    navBar = NavBar.objects.using("timetrackpro").values()
    usuario = Usuarios.objects.using("timetrackpro").filter(id=id)[0]
    empleado = None 
    userDjango = None

    usuariosApp = AuthUser.objects.using("timetrackpro").exclude(first_name__in=excluidos).exclude(last_name__in=excluidos).exclude(username__in=excluidos).order_by('first_name').values('id', 'first_name', 'last_name', 'is_active')

    tarjetasAcceso = TarjetasAcceso.objects.using("timetrackpro").values()


    if RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario).exists():
        empleado = RelEmpleadosUsuarios.objects.using("timetrackpro").filter(id_usuario=usuario)[0]
        if AuthUser.objects.using("timetrackpro").filter(id=empleado.id_auth_user.id).exists():
            userDjango = AuthUser.objects.using("timetrackpro").filter(id=empleado.id_auth_user.id)[0]

    tarjeta = None
    if TarjetasAcceso.objects.using("timetrackpro").filter(dni=usuario.dni).exists():
        tarjeta = TarjetasAcceso.objects.using("timetrackpro").filter(dni=usuario.dni)[0]

    empleados = Empleados.objects.using("timetrackpro").values('id', 'nombre')
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


def asociarUsuario(request):
    if request.method == 'POST':

        # obtenemos el identificador del usuario, este contiene toda la info relevante del usuario
        idUser = request.POST.get("idUsuario")
        usuario = Usuarios.objects.using("timetrackpro").filter(id=idUser)[0]

        # obtenemos el identificador del empleado, este contiene la información de la máquina de control de asistencia
        idEmpleado = request.POST.get("idEmpleado")
        empleado = Empleados.objects.using("timetrackpro").filter(id=idEmpleado)[0]

        # obtenemos el identificador del usuario de django
        idUserDjango = request.POST.get("idUserApp")
        userDjango = AuthUser.objects.using("timetrackpro").filter(id=idUserDjango)[0]

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
        return redirect('timetrackpro:empleados')


'''-------------------------------------------
                                Módulo: verEmpleado

- Descripción: 
Obtener los datos de un empleado en concreto.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def editarEmpleado(request, id):
    navBar = NavBar.objects.using("timetrackpro").values()
    usuario = Usuarios.objects.using("timetrackpro").filter(id=id)[0]
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





def solicitudes(request):

        # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()
    empleados = RelEmpleadosUsuarios.objects.using("timetrackpro").values('id_usuario__id', 'id_usuario__nombre', 'id_usuario__apellidos', 'id_usuario__img', 'id_usuario__dni', 'id_usuario__fecha_nacimiento', 'id_usuario__telefono', 'id_usuario__telefono2', 'id_usuario__email','id_usuario__email2', 'id_usuario__extension', 'id_usuario__puesto', 'id_usuario__direccion', 'id_usuario__info_adicional', 'id_usuario__fecha_alta_app', 'id_usuario__fecha_baja_app', 'id_empleado__id', 'id_empleado__nombre', 'id_empleado__turno', 'id_empleado__horas_maxima_contrato', 'id_empleado__en_practicas', 'id_empleado__maquina_laboratorio', 'id_empleado__maquina_alerta2', 'id_empleado__maquina_departamento', 'id_auth_user__id', 'id_auth_user__first_name', 'id_auth_user__last_name', 'id_auth_user__is_active', 'id_auth_user__is_superuser', 'id_auth_user__is_staff', 'id_auth_user__username', 'id_auth_user__password', 'id_auth_user__last_login', 'id_auth_user__date_joined')


    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "empleados":list(empleados)
    }
    return render(request,"solicitudes.html",infoVista)

def festivos(request, year=None):
    festivos = None
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    if year == None:
        festivos = FestivosYVacaciones.objects.using("timetrackpro").order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    else:
        festivos = FestivosYVacaciones.objects.using("timetrackpro").filter(year=year).order_by('-fecha_inicio').values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "year":year, 
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"festivos.html",infoVista)

def calendarioAnualFestivos(request):
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
    
    festivos = FestivosYVacaciones.objects.using("timetrackpro").values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"calendarioAnualFestivos.html",infoVista)



def datosFestivosCalendario(request):
    # obtengo los festivos registrados en la base de datos
    festivos = FestivosYVacaciones.objects.using("timetrackpro").values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year', 'tipo_festividad__color_calendario')
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


def calendarioFestivos(request, mes):
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
    festivos = FestivosYVacaciones.objects.using("timetrackpro").filter(fecha_inicio__month=mes).values('id', 'nombre', 'tipo_festividad__id', 'tipo_festividad__nombre', 'tipo_festividad__color', 'fecha_inicio', 'fecha_fin', 'year')
    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "festivos":list(festivos),
        "mes":mes,
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
        
        nuevoFestivo = FestivosYVacaciones(nombre=nombre, tipo_festividad=tipo, fecha_inicio=fecha, fecha_fin=fechaFin, year=year)
        nuevoFestivo.save(using='timetrackpro')
        return redirect('timetrackpro:festivos-year', year=year)

        return festivos(request)
    
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tipoFestivos":list(tipoFestivos)
    }

    return render(request,"agregarFestivos.html", infoVista)

def editarFestivo(request, id):
    festivo = FestivosYVacaciones.objects.using("timetrackpro").filter(id=id)[0]
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
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
    navBar = NavBar.objects.using("timetrackpro").values()
    tipoFestivos = TipoFestivos.objects.using("timetrackpro").values()

    infoVista = {
        "navBar":navBar,
        "administrador":True,
        "tipoFestivos":list(tipoFestivos)
    }
    return render(request,"eliminarFestivo.html",{})

def documentacion(request):
    return render(request,"documentation.html",{})

def perfil(request):
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
    return render(request,"profile.html",{"navBar":navBar, })

def dashBoard(request):
    navBar = NavBar.objects.using("timetrackpro").values()
    return render(request,"dashboard.html",{"navBar":navBar})

def tablas(request):        
    # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"registros-insertados.html",infoVista)


def facturacion(request):
    navBar = NavBar.objects.using("timetrackpro").values()
    return render(request,"billing.html",{"navBar":navBar})

def realidadVirtual(request):
    navBar = NavBar.objects.using("timetrackpro").values()
    return render(request,"virtual-reality.html",{"navBar":navBar})

def signIn(request):
    return render(request,"profile.html",{})

def signUp(request):
    return render(request,"sign-up.html",{})


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
