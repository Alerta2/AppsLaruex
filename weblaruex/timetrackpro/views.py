import datetime
from django.conf import settings
from django.shortcuts import redirect, render
from timetrackpro.models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import *
from datetime import date, datetime



def home(request):
    navBar = NavBar.objects.using("timetrackpro").values()
    print(navBar)
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
 

def registrosInsertados(request):

        # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"registros-insertados.html",infoVista)

def VerRegistro(request, id):
    print("-----------------------")
    print("visualizo registro nº: ", id)
    print("-----------------------")

    # obtengo los datos necesarios para la vista
    navBar = NavBar.objects.using("timetrackpro").values()

    # guardo los datos en un diccionario
    infoVista = {
        "navBar":navBar,
        "administrador":True,
    }
    return render(request,"registros-insertados.html",infoVista)


def agregarRegistro(request):
    print("agregar registro --------")

    navBar = NavBar.objects.using("timetrackpro").values()
    if request.method == 'POST':
        
        print("agregar registro ---- 2 ----")
        seccion = request.POST.get("seccion")
        mes = request.POST.get("mes")
        year = request.POST.get("year")
        fecha = datetime.now()
        fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
        nuevoRegistro = RegistrosJornadaInsertados(seccion=seccion, mes=mes, year=year, fecha_lectura=fecha, insertador=AuthUser.objects.using("timetrackpro").filter(id=int(request.POST.get("registrador")))[0])
        nuevoRegistro.save(using='timetrackpro')

        if request.FILES['archivoSeleccionado']:
            print("agregar registro ---- 3 ----")
            nombreArchivo = mes + "_" + year + "_" + seccion + '_registro.' + request.FILES['archivoSeleccionado'].name.split('.')[-1]
            rutaArchivo = '/timetrackpro/registros_insertados/'
            ruta = settings.MEDIA_PRODUCCION + rutaArchivo + nombreArchivo
            subirDocumento(request.FILES['archivoSeleccionado'], ruta)
            nuevoRegistro.ruta = ruta
            nuevoRegistro.save(using='timetrackpro')
            print("agregar registro ---- 4 ----")
        return VerRegistro(request, nuevoRegistro.id)
    else:
        # obtengo los datos necesarios para la vista
        infoVista = {
            "navBar":navBar,
            "administrador":True,
        }
        return render(request,"registros-insertados.html",infoVista)




def documentacion(request):
    return render(request,"documentation.html",{})

def perfil(request):
    # current_url = request.path[1:]
    navBar = NavBar.objects.using("timetrackpro").values()
    print(navBar)
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
    return render(request,"sign-in.html",{})

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
