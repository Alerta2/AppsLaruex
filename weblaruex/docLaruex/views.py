'''-----------------------------------------------------------
LIBRERIAS IMPORTADAS PARA EL FUNCIONAMIENTO DE LA APLICACIÓN
-----------------------------------------------------------'''
#libreria para comprobacion de ficheros
import glob
import os
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

#importaciones para generar pdf con  wkhtmltopdf
import pdfkit
from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
#importaciones para generar un pdf con css
# # importaciones para generar un pdf
from django.http import FileResponse, HttpResponse, HttpResponseRedirect

from django.http.response import JsonResponse

from django.shortcuts import redirect, render
from docLaruex.funciones.funcionesAuxiliares import *
from docLaruex.models import *
from django.db.models import F
from django.db.models import Max, OuterRef, Subquery
from django.db.models import Q
from django.forms.models import model_to_dict


# crear archivo ZIP
import stat
from django.utils.http import urlquote
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import zipfile
from time import sleep
import shutil

# comparar dos urls
from django.urls import resolve
import re

# generar QR
import qrcode
import io
from PIL import Image, ImageDraw, ImageFont

#include json library
import json

# permite formatear los elementos json en elementos de un formulario
from django import forms



# =========================================================================
#                   MÓDULOS QUE PERMITEN EDITAR OBJETOS
# =========================================================================

'''------------------------------------------
La función accesoDenegado, renderiza la plantilla "docLaruex/accesoDenegado.html" cuando el usuario no tiene los permisos necesarios para acceder a una determinada funcionalidad.

- Precondiciones:
    Debe haber recibido una solicitud de "request"

- Postcondiciones:
    devuelve una respuesta renderizada utilizando la función "render" de Django.
-------------------------------------------'''
def accesoDenegado(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Renderiza la plantilla accesoDenegado.html con los elementos del menú
    return render(request, 'docLaruex/accesoDenegado.html', {"itemsMenu": itemsMenu})



'''------------------------------------------
La función accesoDenegado, renderiza la plantilla "docLaruex/accesoDenegado.html" cuando el usuario no tiene los permisos necesarios para acceder a una determinada funcionalidad.

- Precondiciones:
    Debe haber recibido una solicitud de "request"

- Postcondiciones:
    devuelve una respuesta renderizada utilizando la función "render" de Django.
-------------------------------------------'''
def noEncontrado(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Renderiza la plantilla accesoDenegado.html con los elementos del menú
    return render(request, 'docLaruex/noEncontrado.html', {"itemsMenu": itemsMenu})



'''------------------------------------------
La función home, renderiza la plantilla "docLaruex/home.html" 

- Precondiciones:
    Debe haber recibido una solicitud de "request"

- Postcondiciones:
    Devuelve una respuesta renderizada utilizando la función "render" de Django.
-------------------------------------------'''
def home(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Renderiza la plantilla accesoDenegado.html con los elementos del menú
    return render(request, 'docLaruex/home.html', {"itemsMenu": itemsMenu, "tareas":tareas})

'''------------------------------------------
La función portada está decorado con el decorador "@login_required" que asegura que el usuario deba iniciar sesión antes de acceder a la vista "portada". El módulo verifica si el usuario tiene los permisos necesarios para acceder a la funcionalidad.

- Precondiciones:
    Debe haber recibido una solicitud de "request"
    El usuario debe estar autenticado.

- Postcondiciones:
    Devuelve una respuesta renderizada utilizando la función "render" de Django.
    Si el usuario tiene los permisos necesarios, se renderiza la plantilla "docLaruex/portada.html", de lo contrario se renderiza la plantilla "docLaruex/accesoDenegado.html". Los datos necesarios para la plantilla son "itemsMenu", "administrador" y "habilitacionesUsuario".
-------------------------------------------'''
@login_required
def portada(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Obtiene las habilitaciones del usuario actual
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    # Verifica si el usuario actual es administrador
    administrador = esAdministrador(request.user.id)

    # Si el usuario tiene habilitaciones o es administrador, renderiza la plantilla portada.html
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return render(request, 'docLaruex/portada.html', {"itemsMenu": itemsMenu, "administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario)})

    # De lo contrario, renderiza la plantilla accesoDenegado.html
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})



'''------------------------------------------
afdskhfdaskjf

- Precondiciones:

- Postcondiciones:

- Comentarios:.
-------------------------------------------'''

@login_required
def eliminadoExito(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    return render(request, 'docLaruex/eliminadoExito.html', {"itemsMenu": itemsMenu})

'''------------------------------------------
La función listadoUsuarios carga la vista de todos los usuarios en la base de datos de la aplicación "docLaruex". Esta vista incluye una tabla que muestra información de cada usuario, como su nombre, correo electrónico y estado de actividad. El módulo primero verifica si el usuario que solicita la vista es un administrador, obteniendo esta información de la función "esAdministrador". Si el usuario es un administrador, se muestra la vista de todos los usuarios, incluyendo la información obtenida de la base de datos de la aplicación "docLaruex". De lo contrario, se muestra una página de acceso denegado.

- Precondiciones:
    El usuario debe haber iniciado sesión.

- Postcondiciones:
    Se carga la vista de todos los usuarios o se muestra una página de acceso denegado.

- Comentarios:
    Este módulo carga la vista de todos los usuarios y comprueba si el usuario que ha iniciado sesión es un administrador.
-------------------------------------------'''


@login_required
def listadoUsuarios(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    administrador = esAdministrador(request.user.id)
    usuarios = AuthUser.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser','last_login')
    
    if administrador:
        return render(request, 'docLaruex/listaUsuarios.html', {"itemsMenu": itemsMenu, "usuarios": list(usuarios),"administrador": administrador})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
La función "DatosUsuarios" carga la información de la tabla que muestra todos los usuarios. Este módulo obtiene la misma información que el primer módulo, pero en formato JSON y la devuelve como respuesta HTTP.

- Precondiciones:
    El usuario debe haber iniciado sesión.

- Postcondiciones:
    Devuelven la información solicitada de la base de datos de la aplicación "docLaruex". La información se muestra en vistas HTML o como formato JSON en respuesta HTTP.

-------------------------------------------'''
@login_required
def DatosUsuarios(request):
    usuarios = AuthUser.objects.using(
        "docLaruex").order_by('first_name').values('id','username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser','last_login')
    return JsonResponse(list(usuarios), safe=False)



'''------------------------------------------
La función "verUsuario" permite ver la vista particular de un usuario. Este módulo obtiene la información del usuario con un "id" especificado y muestra la vista particular de este usuario. La vista particular incluye información del usuario, como su nombre, correo electrónico, fecha de inicio de sesión y la información de contacto del usuario. También se muestra la información de las habilitaciones del usuario, que incluye el título de la habilitación y su fecha de obtención.

- Precondiciones:
    El usuario debe haber iniciado sesión.

- Postcondiciones:
    Devuelven la información solicitada de la base de datos de la aplicación "docLaruex". La información se muestra en vistas HTML o como formato JSON en respuesta HTTP.
-------------------------------------------'''
@login_required
def verUsuario (request, id):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    usuario = AuthUser.objects.using("docLaruex").get(id=id)
    nombreyApellidos = str(usuario.first_name) +" "+ str(usuario.last_name)
    print ("-------------------")
    print (nombreyApellidos)
    print ("-------------------")
    contactoUsuario = Curriculum.objects.using("docLaruex").filter(id_usuario=id).values('id_usuario','id_usuario','id_usuario__first_name','id_usuario__last_name','id_usuario__email','id_usuario__is_active','id_usuario__is_staff','id_usuario__is_superuser','id_usuario__last_login','id_usuario__date_joined','id_usuario__username','id_usuario__password','id_usuario__is_superuser','id_usuario__is_staff','id_usuario__is_active','id_usuario__date_joined','id_usuario__last_login', 'id_contacto', 'id_contacto__id', 'id_contacto__nombre', 'id_contacto__telefono', 'id_contacto__telefono_fijo','id_contacto__email','id_contacto__direccion','id_contacto__info_adicional','id_contacto__puesto','id_contacto__extension', 'id__id_habilitacion',).first()
    
    habilitacionesUsuario = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id).values('id','tipo','fecha','id_habilitacion','id_habilitacion__id', 'id_habilitacion__titulo')

    contactoUserNombre = Contacto.objects.using("docLaruex").filter(nombre__icontains=nombreyApellidos).values('id','nombre','telefono','telefono_fijo','email','info_adicional','id_habilitacion','puesto','direccion','empresa','extension','img','dni','fecha_nacimiento','tipo_contacto').first()
    
    print ("-------------------")
    print (contactoUserNombre)
    print ("-------------------")
    administrador = esAdministrador(request.user.id)
    if (request.user.id == usuario.id) or administrador:
        return render(request, 'docLaruex/usuario.html', {"itemsMenu": itemsMenu, "usuario": usuario, "contactoUsuario": contactoUsuario, "administrador": administrador, "habilitacionesUsuario": list(habilitacionesUsuario), "contactoUserNombre":contactoUserNombre})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

'''------------------------------------------
La módulo "verMiPerfil" permite al usuario ver su propia vista particular. El módulo primero obtiene la información del usuario que ha iniciado sesión y muestra la vista particular correspondiente. Al igual que en el módulo "verUsuario", la vista particular incluye información del usuario, información de contacto y habilitaciones del usuario.

- Precondiciones:
    El usuario debe haber iniciado sesión.

- Postcondiciones:
    Se carga la vista del perfil del usuario o se muestra una página de acceso denegado.
-------------------------------------------'''
@login_required
def verMiPerfil (request):    
    id = request.user.id
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    usuario = AuthUser.objects.using("docLaruex").get(id=id)
    contactoUsuario = Curriculum.objects.using("docLaruex").filter(id_usuario=id).values('id','id_usuario','id_usuario__first_name','id_usuario__last_name','id_usuario__email','id_usuario__is_active','id_usuario__is_staff','id_usuario__is_superuser','id_usuario__last_login','id_usuario__date_joined','id_usuario__username','id_usuario__password','id_usuario__is_superuser','id_usuario__is_staff','id_usuario__is_active','id_usuario__date_joined','id_usuario__last_login', 'id_contacto', 'id_contacto__id', 'id_contacto__nombre', 'id_contacto__telefono', 'id_contacto__telefono_fijo','id_contacto__email','id_contacto__direccion','id_contacto__info_adicional','id_contacto__puesto','id_contacto__extension', 'id__id_habilitacion',).first()
    
    habilitacionesUsuario = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id).values('id','tipo','fecha','id_habilitacion','id_habilitacion__id', 'id_habilitacion__titulo')

    administrador = esAdministrador(request.user.id)
    if (request.user.id != usuario.id) or administrador:
        return render(request, 'docLaruex/usuario.html', {"itemsMenu": itemsMenu, "usuario": usuario, "contactoUsuario": contactoUsuario, "administrador": administrador, "habilitacionesUsuario": list(habilitacionesUsuario)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
Este módulo se encarga de inhabilitar un usuario específico. La función obtiene el usuario de la base de datos y su lista de habilitaciones. Luego, se verifica si el usuario tiene los permisos necesarios para llevar a cabo la operación y si el método de la solicitud HTTP es POST. Si se cumplen ambas condiciones, se cambia el estado de las variables is_superuser, is_staff e is_active del usuario a 0 y se eliminan todas sus habilitaciones. Finalmente, se renderiza la plantilla correspondiente con los parámetros correspondientes.

- Precondiciones:
    El usuario que realiza la solicitud debe estar autenticado.
    El usuario que se va a inhabilitar debe existir en la base de datos.

- Postcondiciones:
    El usuario seleccionado se inhabilita, lo que significa que ya no puede iniciar sesión en el sistema.
    Todas las habilitaciones del usuario se eliminan.
-------------------------------------------'''
# elimina los permisos y las habilitaciones de un usuario, pero no lo elimina de la base de datos
@login_required
def inhabilitarUsuario (request, id):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    usuario = AuthUser.objects.using("docLaruex").filter(id=id)[0]
    habilitacionesUsuario = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id)
    administrador = esAdministrador(request.user.id)
    
    if request.method == 'POST':
        usuario.is_superuser = 0;
        usuario.is_staff = 0;
        usuario.is_active = 0;
        usuario.save(using="docLaruex")
        for habilitacion in habilitacionesUsuario:
            habilitacion.delete()
        return render(
            request,
            "docLaruex/usuario.html",
            {"itemsMenu": itemsMenu, "usuario": usuario, "administrador": administrador, "habilitacionesUsuario": list(habilitacionesUsuario)})


'''------------------------------------------
Este módulo se encarga de editar los datos de un usuario específico. La función obtiene el usuario de la base de datos y se verifica si el usuario tiene los permisos necesarios para llevar a cabo la operación. Si el método de la solicitud HTTP es POST, se actualizan los datos del usuario con los valores recibidos en la solicitud. Finalmente, se renderiza la plantilla correspondiente con los parámetros correspondientes.

- Precondiciones:
    El usuario que realiza la solicitud debe estar autenticado.
    El usuario que se va a editar debe existir en la base de datos.

- Postcondiciones:
    Los datos del usuario seleccionado se actualizan con los valores recibidos en la solicitud.
-------------------------------------------'''
@login_required
def editarUsuario (request, id):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    usuario = AuthUser.objects.using("docLaruex").filter(id=id)[0]
    administrador = esAdministrador(request.user.id)
    
    if request.method == 'POST':
        usuario.username = request.POST['nuevoUsername'];
        usuario.first_name = request.POST['nuevoNombreUsuario'];
        usuario.last_name = request.POST['nuevoApellidoUsuario'];
        usuario.email = request.POST['nuevoEmail'];
        usuario.is_superuser = request.POST['nuevoSuperUser'];
        usuario.is_staff = request.POST['nuevoStaff'];
        usuario.is_active = request.POST['nuevoActive'];
        usuario.save(using="docLaruex")

    return render(
        request,
        "docLaruex/editarUsuario.html",
        {"itemsMenu": itemsMenu, "usuario": usuario, "administrador": administrador})


'''------------------------------------------
Este módulo se encarga de cargar la vista de todos los objetos disponibles. La función obtiene los diferentes tipos de datos necesarios para mostrar la información en la vista, como responsables, revisores, editores, propietarios, financiadores, colaboradores, habilitaciones, estados, contactos y procedimientos existentes. Luego, se verifica si el usuario tiene los permisos necesarios para acceder a la vista. Si se cumplen las condiciones, se renderiza la plantilla correspondiente con los parámetros correspondientes.

- Precondiciones:    
    El usuario que realiza la solicitud debe estar autenticado.
- Postcondiciones:
    Se carga la vista de todos los objetos disponibles en el sistema.
-------------------------------------------'''
@login_required
def ListadoObjetos(request):
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    revisores = Revisores.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    editores = Editores.objects.using("docLaruex").order_by('first_name').values(
        'id', 'first_name', 'last_name')

    propietarios = UserCurriculum.objects.using("docLaruex").order_by('first_name').values(
        'id', 'first_name', 'last_name')
    financiadores = EntidadesFinanciadoras.objects.using("docLaruex").order_by('nombre').values(
        'id', 'nombre', 'imagen')
    colaboradores = Entidades.objects.using("docLaruex").order_by('nombre').values(
        'id', 'nombre', 'imagen')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    estados = Estado.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
    
    contactos = Contacto.objects.using(
        "docLaruex").order_by('nombre').values('id','nombre')

    procedimientosExistentes = Procedimiento.objects.using(
        "docLaruex").values_list('id_doc__nombre', flat=True).distinct()
     
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

        return render(request, 'docLaruex/ListaObjetos.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "editores": list(editores), "revisores": list(revisores), "financiadores": list(financiadores),"colaboradores": list(colaboradores), "estados": list(estados),"contactos": list(contactos),"propietarios":list(propietarios),"procedimientosExistentes": list(procedimientosExistentes), "habilitaciones": list(habilitaciones), "administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario)})
    else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
Este módulo se encarga de cargar la información de la tabla que muestra todos los objetos disponibles. La función obtiene los objetos de la base de datos que corresponden a las habilitaciones del usuario y que no son de tipo Equipo o Ubicación. Luego, se construye un JSON con los datos obtenidos y se devuelve como respuesta.

- Precondiciones:
    El usuario que realiza la solicitud debe estar autenticado.
- Postcondiciones:
    Se devuelve un JSON con la información de la tabla que muestra todos los objetos disponibles en el sistema que corresponden a las habilitaciones del usuario y que no son de tipo Equipo o Ubicación.
-------------------------------------------'''
def DatosObjetos(request):
    objetos = Objeto.objects.using('docLaruex').filter(id_habilitacion__in=comprobarHabilitaciones(request.user.id)).exclude(tipo__in = ['Equipo', 'Ubicacion']).order_by('-fecha_subida').values('id', 'padre__id', 'padre__nombre',
                                                                                 'nombre', 'fecha_subida', 'ruta', 'tipo', 'creador__first_name', 'creador__last_name', 'visible', 'icono', 'id_estado__nombre','id_estado__id',  'ruta_editable')
    return JsonResponse(list(objetos), safe=False)

    


'''------------------------------------------
- Descripción:

- Precondiciones:
    Deben existir objetos de tipo Objeto, Procedimiento y Formatos en la base de datos de docLaruex.
- Postcondiciones:
    Devolverá una respuesta JsonResponse que contendrá un listado con los objetos consultados.
-------------------------------------------'''
def DatosObjetosAsociar(request):
    objetos = Objeto.objects.using('docLaruex').exclude(tipo='Formato').exclude(
        tipo='Procedimiento').order_by('-fecha_subida').values('id', 'nombre', 'tipo')

    procedimientos = Procedimiento.objects.using('docLaruex').order_by(
        '-id_doc__fecha_subida').values('id_doc__id', 'id_doc__nombre', 'id_doc__tipo', 'version')

    formato = Formatos.objects.using('docLaruex').order_by(
        '-id_doc__fecha_subida').values('id_doc__id', 'id_doc__nombre', 'id_doc__tipo', 'version')

    listado = list(objetos) + list(procedimientos) + list(formato)
    return JsonResponse(listado, safe=False)



'''------------------------------------------
- Descripción:
Este módulo se encarga de cargar la información de la tabla que muestra todos los objetos disponibles. La función obtiene los objetos de la base de datos que corresponden a las habilitaciones del usuario y que no son de tipo Equipo o Ubicación. Luego, se construye un JSON con los datos obtenidos y se devuelve como respuesta.

- Precondiciones:
Deben existir objetos de tipo Objeto, Procedimiento y Formatos en la base de datos de docLaruex
Usuario debe estar logueados

- Postcondiciones:
Devolverá una respuesta JsonResponse que contendrá un listado con los objetos consultados.
-------------------------------------------'''
@login_required
def DatosObjetosSeleccionados(request, id):
    objetosSeleccionados = Objeto.objects.using('docLaruex').order_by(
        '-nombre').values('id', 'nombre', 'tipo')
    salida = []
    return JsonResponse(list(salida), safe=False)

'''------------------------------------------
- Descripción:
Este módulo se encarga de listar los objetos de la base de datos en función del tipo del objeto.

- Precondiciones:
Debe haber conexión con la base de datos de docLaruex
El usuario debe estar logueado 

- Postcondiciones:
Creará un nuevo objeto en la base de datos y devolverá una respuesta JsonResponse que indicará si la operación fue exitosa o no.
-------------------------------------------'''
@login_required
def ListadoObjetosPorTipo(request, tipo):
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id) 
    secretaria = esSecretaria(request.user.id)

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    estados = Estado.objects.using("docLaruex").values()
    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    revisores = Revisores.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    editores = Editores.objects.using("docLaruex").order_by('first_name').values(
        'id')
    
    propietarios = UserCurriculum.objects.using("docLaruex").order_by('first_name').values(
        'id', 'first_name', 'last_name')
    financiadores = EntidadesFinanciadoras.objects.using("docLaruex").order_by('nombre').values(
        'id', 'nombre', 'imagen')
    colaboradores = Entidades.objects.using("docLaruex").order_by('nombre').values(
        'id','nombre', 'imagen')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    
    contactos = Contacto.objects.using("docLaruex").order_by('nombre').values(
        'id', 'nombre')

    if (tipo == "Procedimiento"):

        procedimientosExistentes = Procedimiento.objects.using("docLaruex").filter(
            id_doc__tipo=tipo).values_list('id_doc__nombre', flat=True).distinct()
     
        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

            return render(request, 'docLaruex/listaProcedimientos.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "editores": list(editores), "revisores": list(revisores), "procedimientosExistentes": list(procedimientosExistentes), "habilitaciones": list(habilitaciones), "administrador": administrador, "habilitacionesUsuario": list(habilitacionesUsuario),"estados":list(estados)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif (tipo == "Documento"):

        documentosExistentes = Documento.objects.using("docLaruex").filter(
            id_doc__tipo=tipo).values_list('id_doc__nombre', flat=True).distinct()
        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
            return render(request, 'docLaruex/listaDocumentos.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "editores": list(editores), "revisores": list(revisores), "procedimientosExistentes": list(documentosExistentes), "habilitaciones": list(habilitaciones), "administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario),"estados":list(estados)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif (tipo == "Curriculum"):

        curriculumsExistentes = Curriculum.objects.using("docLaruex").filter(
            id__tipo=tipo).values_list('id__nombre', flat=True).distinct()
        
        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

            return render(request, 'docLaruex/listaCurriculums.html', {"itemsMenu": itemsMenu, "curriculumsExistentes": list(curriculumsExistentes), "habilitaciones": list(habilitaciones), "contactos":list(contactos),"propietarios": list(propietarios),"estados":list(estados),"administrador": administrador, "direccion": direccion, "habilitacionesUsuario":list(habilitacionesUsuario)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif (tipo == "Proyecto"):

        proyectoExistentes = Proyecto.objects.using("docLaruex").filter(
            id__tipo=tipo).values_list('id__nombre', flat=True).distinct()
        
        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

            return render(request, 'docLaruex/listaProyectos.html', {"itemsMenu": itemsMenu, "financiadores": list(financiadores), "colaboradores": list(colaboradores), "proyectoExistentes": list(proyectoExistentes), "habilitaciones": list(habilitaciones), "estados":list(estados), "administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif (tipo == "Acta"):   
        actas = Acta.objects.using("docLaruex").filter(
            id__tipo=tipo).values_list('id__nombre', flat=True).distinct()
        convocantes = Convocantes.objects.using("docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
        secretarios = Secretarios.objects.using("docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
        miembros = Miembros.objects.using("docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
        
        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

            # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
            return render(request, 'docLaruex/listaActas.html', {"itemsMenu": itemsMenu, "proyectos":list(actas), "convocantes":list(convocantes), "secretarios":list(secretarios), "miembros":list(miembros), "estados":list(estados),"habilitaciones": list(habilitaciones),"administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario), "range":range(20)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
    elif (tipo == "Curso"):   
        patrocinadores = Entidades.objects.using("docLaruex").order_by('nombre').values(
            'id', 'nombre', 'imagen')
        tipoCursos = TipoCurso.objects.using("docLaruex").values(
            'id', 'nombre')
        cursos = Cursos.objects.using("docLaruex").values('id','fecha_inicio', 'fecha_fin', 'id__nombre', 'id__ruta','id__ruta_editable','id__id_estado__id', 'id__id_estado__nombre', 'id__id_habilitacion__id', 'id__id_habilitacion__titulo', 'imagen', 'patrocinadores__nombre', 'tipo_curso__id', 'tipo_curso__nombre', 'horas')
    
        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

            return render(request, 'docLaruex/listaCursos.html', {"itemsMenu": itemsMenu,"cursos":list(cursos), "responsables": list(responsables), "habilitaciones": list(habilitaciones), "patrocinadores":list(patrocinadores), "administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario), "tipoCursos":list(tipoCursos), "range":range(20)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif (tipo == "Ubicacion"):
        tipoUbicacionesExistentes = TipoUbicacion.objects.using(
            "docLaruex").values('id', 'nombre')
        ubicacionesExistentes = Ubicaciones.objects.using(
            "docLaruex").order_by('id__nombre').values('id', 'id__nombre', 'id__padre')

        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:    
            return render(request, 'docLaruex/ListaUbicaciones.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicacionesExistentes": list(ubicacionesExistentes), "administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario), "habilitaciones": list(habilitaciones), "tipoUbicacionesExistentes": list(tipoUbicacionesExistentes)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
    
    elif (tipo == "Equipo"):

        #genera un código_laruex consecutivo
        # por el momento busca en un rango, para localizar el último valor
        # pues para agilizar la gestión se igualaron alguno cod_uex con cod_laruex
        ultimoCodigoLaruex = Equipo.objects.using("docLaruex").filter(cod_laruex__range =[2320,68000]).order_by('-cod_laruex').values('cod_laruex')[0]
        ultimoCodigo=ultimoCodigoLaruex['cod_laruex'] + 1

        itemsMenu = MenuBar.objects.using("docLaruex").values()
        fabricantes = Fabricante.objects.using(
            "docLaruex").order_by('nombre').values('id', 'nombre')
        proveedores = Proveedor.objects.using(
            "docLaruex").order_by('nombre').values('id', 'nombre')
        tipoEquipoExistentes = TipoEquipo.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
        equiposExistentes = Equipo.objects.using(
            "docLaruex").values('id')
        
        equipos = Equipo.objects.using(
            "docLaruex").values('id', 'cod_laruex')
        ubicaciones = Ubicaciones.objects.using(
        "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'latitud', 'longitud', 'id__padre', 'id__padre__nombre')
        gruposEquipos = GrupoEquipos.objects.using("docLaruex").values('id', 'nombre')

        if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador or secretaria or direccion:
            return render(request, 'docLaruex/ListaEquipos.html', {"ultimoCodigo": ultimoCodigo,"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicaciones": list(ubicaciones), "habilitaciones": list(habilitaciones), "fabricantes": list(fabricantes),"proveedores": list(proveedores), "tipoEquipo": list(tipoEquipoExistentes),"equiposExistentes":list(equiposExistentes),"administrador": administrador, "secretaria":secretaria, "direccion":direccion,"habilitacionesUsuario":list(habilitacionesUsuario), "equipos":list(equipos), "gruposEquipos":list(gruposEquipos)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    else:
        return(request)

'''
############## Carga la vista de todos los procedimientos ¿¿¿¿¿BORRAR????? ##############
@login_required
def ListadoProcedimientos(request):
    itemsMenu = MenuBar.objects.using("docLaruex").order_by('-padre').values()
    return render(request, 'docLaruex/listaProcedimientos.html', {"itemsMenu": itemsMenu})
'''


'''------------------------------------------
                                Módulo: DatosProcedimientos
- Descripción:
Este módulo se encarga de cargar la información de la tabla que muestra todos los procedimientos disponibles en la plataforma. La función obtiene los procedimientos de la base de datos que corresponden a las habilitaciones del usuario y que no son de tipo Equipo o Ubicación. Luego, se construye un JSON con los datos obtenidos y se devuelve como respuesta.

- Precondiciones:
Deben existir objetos de tipo Procedimiento en la base de datos de docLaruex.
El usuario debe estar logueado

- Postcondiciones:
Devolverá una respuesta JsonResponse que contendrá un listado con los procedimientos consultados.-------------------------------------------'''
@login_required
def DatosProcedimientos(request):
    procedimientos = Procedimiento.objects.using('docLaruex').filter(id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('-version').values('id_doc', 'id_doc__ruta_editable','id_doc__nombre', 'titulo', 'version','id_doc__id_estado__id','id_doc__id_estado__nombre', 'responsable__first_name', 'revisor__first_name', 'fecha_verificacion', 'modificaciones', 'id_doc__id_habilitacion__titulo')
    procExistentes = []
    salida = []
    for p in procedimientos:
        if not p["id_doc__nombre"] in procExistentes:
            p["responsable__first_name"] = p["responsable__first_name"] + \
                " / " + p["revisor__first_name"]
            salida.append(p)
            procExistentes.append(p["id_doc__nombre"])
    return JsonResponse(list(salida), safe=False)



'''------------------------------------------
                                Módulo: ListadoProcedimientosTipo

- Descripción:
Este módulo se encarga de mostrar una página con un listado de los diferentes tipos de procedimientos que se pueden consultar en la plataforma, según las habilitaciones del usuario. La función obtiene los datos necesarios de la base de datos y los utiliza para construir la página que se mostrará al usuario.

- Precondiciones:
Deben existir objetos de tipo MenuBar y Habilitaciones en la base de datos de docLaruex.
El usuario debe estar logueado

- Postcondiciones:
Si el usuario tiene habilitaciones asociadas a su cuenta o es administrador, se mostrará una página con un listado de los tipos de procedimientos disponibles, en caso contrario, se mostrará una página de acceso denegado.-------------------------------------------'''
@login_required
def ListadoProcedimientosTipo (request):
    itemsMenu = MenuBar.objects.using("docLaruex").order_by('-padre').values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    TipoProcedimientos = ["MC","PGC","PL", "PR", "OD", "PS", "Anexo"]
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return render(request, 'docLaruex/listaProcedimientosTipo.html', {"itemsMenu": itemsMenu, "TipoProcedimientos": list(TipoProcedimientos),"administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario) })
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: DatosProcedimientosTipo

- Descripción:
Este módulo recibe como parámetro el tipo de procedimiento y retorna una lista de los procedimientos que pertenecen a ese tipo. El usuario debe estar autenticado.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
El módulo devuelve una lista de los procedimientos del tipo indicado que pertenecen al usuario autenticado.
-------------------------------------------'''
@login_required
def DatosProcedimientosTipo(request, tipo):
    
    procedimientos = Procedimiento.objects.using('docLaruex').filter(id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id_doc__nombre__contains=tipo).order_by('-version').values('id_doc', 'id_doc__ruta_editable','id_doc__nombre', 'titulo', 'version','id_doc__id_estado__id','id_doc__id_estado__nombre', 'responsable__first_name', 'revisor__first_name', 'fecha_verificacion', 'modificaciones', 'id_doc__id_habilitacion__titulo')
    procExistentes = []
    salida = []
    for p in procedimientos:
        if not p["id_doc__nombre"] in procExistentes:
            p["responsable__first_name"] = p["responsable__first_name"] + \
                " / " + p["revisor__first_name"]
            salida.append(p)
            procExistentes.append(p["id_doc__nombre"])
    return JsonResponse(list(salida), safe=False)



'''------------------------------------------
                                Módulo: ListadoReservaProcedimientos

- Descripción:
Este módulo muestra una lista de procedimientos reservados por los usuarios. El usuario debe estar autenticado y tener habilitaciones asignadas o ser un administrador.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
El módulo muestra una lista de los procedimientos reservados y de los responsables que los reservaron, así como la opción de reservar o liberar procedimientos.
-------------------------------------------'''
@login_required
def ListadoReservaProcedimientos(request):
    itemsMenu = MenuBar.objects.using("docLaruex").order_by('-padre').values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return render(request, 'docLaruex/listaReservaProcedimientos.html', {"itemsMenu": itemsMenu, "responsables": list(responsables),"administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: ReservaDatosProcedimientos

- Descripción: 
Este módulo muestra una lista de los procedimientos reservados por los usuarios. El usuario debe estar autenticado.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
El módulo devuelve una lista de los procedimientos reservados por los usuarios y de los responsables que los reservaron.
-------------------------------------------'''
@login_required
def ReservaDatosProcedimientos(request):
    reservas = ReservasProcedimiento.objects.using('docLaruex').order_by('-procedimiento_reservado').values('id', 'procedimiento_reservado', 'titulo', 'fecha', 'responsable__first_name', 'responsable__last_name','responsable')
    reservasExistentes = []
    salida = []
    for r in reservas:
        if not r["procedimiento_reservado"] in reservasExistentes:
            salida.append(r)
            reservasExistentes.append(r["procedimiento_reservado"])
    return JsonResponse(list(salida), safe=False)


'''------------------------------------------
                                Módulo: eliminarReservaProcedimiento

- Descripción: 
Este módulo se encarga de eliminar la reserva de un procedimiento de la base de datos.

- Precondiciones:
El usuario debe estar autenticado y ser un administrador.

- Postcondiciones:
Se elimina la reserva de un procedimiento de la base de datos y se muestra la lista actualizada de habilitaciones.
-------------------------------------------'''
@login_required
def eliminarReservaProcedimiento(request,id):
    if esAdministrador(request.user.id):
        ReservasProcedimiento.objects.using("docLaruex").filter(id=id).delete()
        return ListadoReservaProcedimientos(request)
    else:
        return accesoDenegado(request)


'''------------------------------------------
                                Módulo: BuscarCodigoProcedimiento

- Descripción: 
Este módulo busca un código de procedimiento disponible. Recibe como parámetro el código base del procedimiento y devuelve un código de procedimiento disponible. El usuario debe estar autenticado.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
El módulo devuelve un código de procedimiento disponible que se puede asignar a un nuevo procedimiento.-------------------------------------------'''
@login_required
def BuscarCodigoProcedimiento(request, codigo):
    procedimientos = Objeto.objects.using('docLaruex').filter(tipo="Procedimiento", nombre__contains=codigo+"-").values_list('nombre', flat=True).distinct()
    reservas = ReservasProcedimiento.objects.using('docLaruex').filter(procedimiento_reservado__contains=codigo+"-").values_list('procedimiento_reservado', flat=True)

    procedimientos = list(procedimientos) + list(reservas)
    print (procedimientos)
    
    if procedimientos:
        numeroProcedimiento = 1
        encontrado = False
        while not encontrado:
            if numeroProcedimiento < 10:
                posibleCodigo = codigo + "-0" + str(numeroProcedimiento)
            else:
                posibleCodigo = codigo + "-" + str(numeroProcedimiento)

            if posibleCodigo in procedimientos:
                numeroProcedimiento+=1
            else:
                encontrado=True
                return JsonResponse({"codigoProcedimiento":posibleCodigo}, safe=False)
    else:
        codigo_libre = codigo + "-01"
        return JsonResponse({"codigoProcedimiento":codigo_libre}, safe=False)



'''------------------------------------------
                                Módulo: agregarAnexo

- Descripción: 
Este módulo permite agregar un anexo a un curriculum existente y actualizar la base de datos de formaciones asociadas al mismo.

- Precondiciones:
El usuario debe estar autenticado.
El id del curriculum debe ser válido.
Se debe haber completado el formulario de datos de formación y haber adjuntado un archivo.

- Postcondiciones:

Se crea una carpeta para almacenar los archivos adjuntos asociados al curriculum, si esta no existe previamente.
Se guarda en la base de datos la formación asociada al curriculum con los datos proporcionados por el usuario.
Se guarda el archivo adjunto en la carpeta correspondiente y se actualiza la ruta en la base de datos.
Se redirige al usuario a la página de procedimiento correspondiente con los datos actualizados.
-------------------------------------------'''
@login_required
def agregarAnexo(request, id_curriculum):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    curriculum = Curriculum.objects.using('docLaruex').filter(id=id_curriculum)[0]
    datosProcedimiento = Procedimiento.objects.using('docLaruex').filter(id_doc=id).values()
    directorio = settings.MEDIA_ROOT +"archivos/Documento/" + str(id_curriculum)

    if not os.path.exists(directorio):
        print("--- Creo la carpeta ---")
        os.makedirs(directorio)
    
    ficheroAdjunto = request.FILES["ficheroAdjuntoFormacionCurriculum"]  

    #actualizamos la base de datos de formaciones asociadas a curriculums   
    print("--- cargo formaciones ---")  
    formaciones = FormacionCurriculum(id_curriculum=curriculum, titulo=request.POST.get("tituloFormacion"), descripcion=request.POST.get("descripcionFormacion"), horas=request.POST.get("horasFormacion"),  fecha_inicio=request.POST.get("fechaInicioFormacion"), fecha_fin=request.POST.get("fechaFinFormacion"))
    formaciones.save(using='docLaruex')  
    print("--- guardo formaciones ---")  

    formaciones.ruta = str(formaciones.id) + '.' + ficheroAdjunto.name.split('.')[-1]
    formaciones.save(using='docLaruex')

    rutaFormacion = settings.MEDIA_ROOT + 'archivos/Curriculum/' + str(id_curriculum) +"/"+ formaciones.ruta 

    #subimos el documento a la carpeta
    subirDocumento(ficheroAdjunto, rutaFormacion)
    
    return render(request, 'docLaruex/procedimiento.html', {'datosProcedimiento': datosProcedimiento, "administrador":esAdministrador(request.user.id),'itemsMenu': itemsMenu})

'''------------------------------------------
                                Módulo: DatosCurriculums

- Descripción: 
Este módulo obtiene los datos de todos los currículums en la base de datos.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Retorna una respuesta JSON con los datos de todos los currículums en la base de datos.
-------------------------------------------'''
@login_required
def DatosCurriculums(request):
    curriculums = Curriculum.objects.using('docLaruex').order_by('id').values('id','id_usuario__id', 'id_usuario__first_name', 'id_usuario__last_name', 'id_contacto__id','id_contacto__telefono','id_contacto__telefono_fijo','id_contacto__email','id_contacto__direccion','id_contacto__info_adicional','id_contacto__puesto','id_contacto__extension', 'id__id_habilitacion','id__tipo', 'id__nombre')
    
    return JsonResponse(list(curriculums), safe=False)


'''------------------------------------------
                                Módulo: agregarFormacionCurriculum

- Descripción: 
Este módulo permite agregar una formación al currículum del usuario

- Precondiciones:
El usuario debe estar autenticado y tener un currículum previamente creado.

- Postcondiciones:
Se agrega una formación al currículum del usuario y se guarda en la base de datos y en el sistema de archivos.

-------------------------------------------'''
@login_required
def agregarFormacionCurriculum(request, id_curriculum):
    
    print("********************************")
    print("Entro en agregar Formacion asociadas")

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    curriculum = Curriculum.objects.using('docLaruex').filter(id=id_curriculum)[0]
    datosCurriculum = Curriculum.objects.using('docLaruex').filter(id=id_curriculum).values()
    directorio = settings.MEDIA_ROOT +"archivos/Curriculum/" + str(id_curriculum)

    if not os.path.exists(directorio):
        print("--- Creo la carpeta ---")
        os.makedirs(directorio)
    
    ficheroAdjunto = request.FILES["ficheroAdjuntoFormacionCurriculum"]  

    #actualizamos la base de datos de formaciones asociadas a curriculums   
    print("--- cargo formaciones ---")  
    formaciones = FormacionCurriculum(id_curriculum=curriculum, titulo=request.POST.get("tituloFormacion"), descripcion=request.POST.get("descripcionFormacion"), horas=request.POST.get("horasFormacion"),  fecha_inicio=request.POST.get("fechaInicioFormacion"), fecha_fin=request.POST.get("fechaFinFormacion"))
    formaciones.save(using='docLaruex')  
    print("--- guardo formaciones ---")  

    formaciones.ruta = str(formaciones.id) + '.' + ficheroAdjunto.name.split('.')[-1]
    formaciones.save(using='docLaruex')

    rutaFormacion = settings.MEDIA_ROOT + 'archivos/Curriculum/' + str(id_curriculum) +"/"+ formaciones.ruta 

    #subimos el documento a la carpeta
    subirDocumento(ficheroAdjunto, rutaFormacion)
    
    print("--- subo formaciones ---")  
    return render(request, 'docLaruex/curriculum.html', {'datosCurriculum': datosCurriculum, "administrador":esAdministrador(request.user.id),'itemsMenu': itemsMenu})

'''------------------------------------------
                                Módulo: consultarFormacionCurriculum

- Descripción: 
Este módulo permite descargar el archivo adjunto de una formación en un currículum.

- Precondiciones:
El usuario debe estar autenticado y la formación debe existir en el currículum.

- Postcondiciones:
 Se descarga el archivo adjunto de la formación.
-------------------------------------------'''
@login_required
def consultarFormacionCurriculum(request, id_curriculum, id):
    formacion = FormacionCurriculum.objects.using('docLaruex').filter(id=id)[0]
    ruta = settings.MEDIA_ROOT + 'archivos/Curriculum/' + id_curriculum + '/' + id + '.' + formacion.ruta.split('.')[-1]
    return FileResponse(open(ruta, 'rb'))




'''------------------------------------------
                                Módulo: DatosDocumentos

- Descripción: 
Este módulo se encarga de obtener los documentos relacionados con las habilitaciones del usuario que realiza la petición y devolverlos en formato JSON.

- Precondiciones:
El usuario debe estar autenticado y haber iniciado sesión en el sistema. Además, el usuario debe tener habilitaciones asignadas en el sistema.

- Postcondiciones:
El sistema devolverá una respuesta en formato JSON con la información de los documentos relacionados con las habilitaciones del usuario que realizó la petición.
-------------------------------------------'''
@login_required
def DatosDocumentos(request):
    documentos = Documento.objects.using('docLaruex').filter(id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('-id_doc').values('id_doc', 'id_doc__nombre', 'id_doc__fecha_subida', 'editable',
                                                                                 'fecha_actualizacion', 'num_modificaciones', 'id_doc__tipo', 'id_doc__creador__first_name',  'id_doc__creador__last_name', 'id_doc__ruta')
    docsExistentes = []
    salida = []
    for d in documentos:
        if not d["id_doc"] in docsExistentes:
            salida.append(d)
            docsExistentes.append(d["id_doc"])
    return JsonResponse(list(salida), safe=False)



'''------------------------------------------
                                Módulo: DatosDocumentos

- Descripción: 
Este módulo se encarga de obtener una lista de todas las habilitaciones existentes en el sistema y mostrarla en una vista HTML.

- Precondiciones:
El usuario debe estar autenticado y haber iniciado sesión en el sistema. Además, el usuario debe tener permisos de administrador en el sistema.

- Postcondiciones:
El sistema devolverá una vista HTML con la lista de todas las habilitaciones existentes en el sistema. Si el usuario no tiene permisos de administrador, se le mostrará una vista HTML de acceso denegado.
-------------------------------------------'''
@login_required
def ListadoHabilitaciones(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    usuarios = AuthUser.objects.using("docLaruex").order_by('first_name').values()
    administrador = esAdministrador(request.user.id)

    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values()
    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    if administrador:
        return render(request, 'docLaruex/listaHabilitaciones.html', {"itemsMenu": itemsMenu,  "administrador": administrador,"usuarios":usuarios, "habilitaciones":habilitaciones})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: eliminarHabilitacion

- Descripción: 
Este módulo se encarga de eliminar una habilitación específica de la base de datos.

- Precondiciones:
El usuario debe estar autenticado y ser un administrador.

- Postcondiciones:
Se elimina la habilitación especificada de la base de datos y se muestra la lista actualizada de habilitaciones.
-------------------------------------------'''
@login_required
def eliminarHabilitacion(request,id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    
    Habilitaciones.objects.using("docLaruex").filter(id=id).delete()
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values()
    usuarios = AuthUser.objects.using("docLaruex").order_by('first_name').values()
    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    return render(request, 'docLaruex/listaHabilitaciones.html', {"itemsMenu": itemsMenu,  "administrador": esAdministrador(request.user.id),"usuarios":usuarios, "habilitaciones":habilitaciones})


'''------------------------------------------
                                Módulo: eliminarHabilitacionUsuario

- Descripción: 
Este módulo se encarga de eliminar una relación entre un usuario y una habilitación específicos de la base de datos.

- Precondiciones:
 El usuario debe estar autenticado y ser un administrador.

- Postcondiciones:
Se elimina la relación especificada de la base de datos y se muestra la lista actualizada de habilitaciones y usuarios.
-------------------------------------------'''
@login_required
def eliminarHabilitacionUsuario(request,id,id_usuario):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    
    RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_habilitacion=id,id_usuario=id_usuario).delete()

    usuarios = AuthUser.objects.using("docLaruex").order_by('first_name').values()
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values()

    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    return render(request, 'docLaruex/listaHabilitaciones.html', {"itemsMenu": itemsMenu,  "administrador": esAdministrador(request.user.id),"usuarios":usuarios, "habilitaciones":habilitaciones})


'''------------------------------------------
                                Módulo: ListadoFabricantes

- Descripción: 
Este módulo se encarga de mostrar una lista de fabricantes y sus equipos asociados de la base de datos.

- Precondiciones:
El usuario debe estar autenticado y tener al menos una habilitación para ver la lista de fabricantes.

- Postcondiciones:
Se muestra la lista de fabricantes y sus equipos asociados de la base de datos.
-------------------------------------------'''
@login_required
def ListadoFabricantes(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()    
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    fabricantes = Fabricante.objects.using("docLaruex").values()
    equipos = Equipo.objects.using("docLaruex").values()
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
        return render(request, 'docLaruex/listaFabricantes.html', {"itemsMenu": itemsMenu, "administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario),"fabricantes":fabricantes, "equipos":equipos})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: DatosFabricantes

- Descripción: 
Este módulo devuelve los datos de los fabricantes de equipos ordenados por ID en formato JSON.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.

- Postcondiciones:
Devuelve los datos de los fabricantes de equipos en formato JSON.
-------------------------------------------'''
@login_required
def DatosFabricantes(request):
    fabricantes = Fabricante.objects.using('docLaruex').order_by('id').values(
        'id','nombre', 'fijo', 'movil', 'correo', 'direccion', 'comentarios')
    return JsonResponse(list(fabricantes), safe=False)


'''------------------------------------------
                                Módulo: agregarFabricante

- Descripción: 
Este módulo agrega un nuevo fabricante a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.

- Postcondiciones:
La página de lista de fabricantes se renderiza de nuevo.
Se agrega un nuevo registro de fabricante a la base de datos.
-------------------------------------------'''
@login_required
def agregarFabricante(request):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    fijo = request.POST.get("prefijoFijo") + request.POST.get("fijo")
    movil = request.POST.get("prefijoMovil") + request.POST.get("movil")


    nuevoFabricante = Fabricante(nombre=request.POST.get("nombre"), fijo=fijo, movil=movil, correo=request.POST.get("correo"), direccion=request.POST.get("direccion"), comentarios=request.POST.get("comentarios"), web=request.POST.get("web"))
    nuevoFabricante.save(using='docLaruex')
    
    return render(request, 'docLaruex/listaFabricantes.html', {"itemsMenu": itemsMenu})

'''------------------------------------------
                                Módulo: ListadoProveedores

- Descripción: 

Este módulo muestra una lista de proveedores.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.

- Postcondiciones:
Renderiza la página que muestra la lista de proveedores.

-------------------------------------------'''
@login_required
def ListadoProveedores(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    proveedores = Proveedor.objects.using("docLaruex").values()
    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return render(request, 'docLaruex/listaProveedores.html', {"itemsMenu": itemsMenu,"administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario),"proveedores":proveedores})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})



'''------------------------------------------
                                Módulo: DatosProveedores

- Descripción: 
Este módulo devuelve los datos de los proveedores ordenados por ID  en formato JSON.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.

- Postcondiciones:
Devuelve los datos de los proveedores en formato JSON.
-------------------------------------------'''
@login_required
def DatosProveedores(request):
    proveedores = Proveedor.objects.using('docLaruex').order_by('id').values(
        'id','nombre', 'cif', 'direccion', 'telefono', 'telefono_2', 'fax', 'correo', 'correo_2', 'web', 'comentarios')
    return JsonResponse(list(proveedores), safe=False)
    
'''------------------------------------------
                                Módulo: agregarProveedor

- Descripción: 
Este módulo agrega un nuevo proveedor a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.

- Postcondiciones:
La página de lista de proveedores se renderiza de nuevo.
Se agrega un nuevo registro de proveedor a la base de datos.
-------------------------------------------'''    
@login_required
def agregarProveedor(request):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    telefono = request.POST.get("prefijoTelefono") + request.POST.get("telefono")
    telefono2 = request.POST.get("prefijoTelefono2") + request.POST.get("telefono2")
    fax = request.POST.get("prefijoFax") + request.POST.get("fax")


    nuevoProveedor = Proveedor(nombre=request.POST.get("nombre"),cif=request.POST.get("cif"), telefono=telefono, telefono_2=telefono2, fax=fax, correo=request.POST.get("correo"),correo_2=request.POST.get("correo2"), web=request.POST.get("web"), direccion=request.POST.get("direccion"), comentarios=request.POST.get("comentarios"))
    nuevoProveedor.save(using='docLaruex')
    
    return render(request, 'docLaruex/listaProveedores.html', {"itemsMenu": itemsMenu})

'''------------------------------------------
                                Módulo: verProveedor

- Descripción: 
Este módulo se encarga de mostrar la información detallada de un proveedor seleccionado por el usuario. Se utiliza para ver los datos del proveedor en pantalla.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un proveedor existente en la base de datos para visualizar su información.

- Postcondiciones:
Se debe mostrar la información detallada del proveedor seleccionado.
El proveedor debe existir en la base de datos.

-------------------------------------------'''   
@login_required
def verProveedor(request, id):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    proveedor = Proveedor.objects.using('docLaruex').values('id','nombre', 'cif', 'direccion', 'telefono', 'telefono_2', 'fax', 'correo', 'correo_2', 'web', 'comentarios').filter(id=id)[0]

    return render(
            request,
            "docLaruex/proveedor.html",
            {"itemsMenu": itemsMenu, "proveedor": proveedor, "administrador": esAdministrador(request.user.id)})



'''------------------------------------------
                                Módulo: editarProveedor

- Descripción:  
Este módulo permite al usuario editar la información de un proveedor existente en la base de datos. Se utiliza para actualizar los datos del proveedor.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un proveedor existente en la base de datos para editar su información.

- Postcondiciones:
Los datos del proveedor deben ser actualizados en la base de datos.
Se debe mostrar la información actualizada del proveedor en pantalla.

-------------------------------------------'''   
@login_required
def editarProveedor(request, id):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    proveedor = Proveedor.objects.using('docLaruex').filter(id=id)[0]

    if request.method == 'POST':
        print("POST", request.POST)
        proveedor.nombre = request.POST['nuevoNombre']
        proveedor.cif = request.POST['nuevoCif']
        proveedor.direccion = request.POST['nuevaDireccion']
        proveedor.telefono = request.POST['nuevoPrefijoTelefono'] + request.POST['nuevoTelefono']
        proveedor.telefono_2 = request.POST['nuevoPrefijoTelefono2'] + request.POST['nuevoTelefono2']
        proveedor.fax = request.POST['nuevoPrefijoFax'] + request.POST['nuevoFax']
        proveedor.correo = request.POST['nuevoCorreo']
        proveedor.correo_2 = request.POST['nuevoCorreo2']
        
        proveedor.web = request.POST['nuevaWeb']
        proveedor.comentarios = request.POST['nuevosComentarios']
        proveedor.save(using="docLaruex")
        return render(
            request,
            "docLaruex/proveedor.html",
            {"itemsMenu": itemsMenu, "proveedor": proveedor})
    else:
        return render(
            request,
            "docLaruex/editarProveedor.html",
            {"itemsMenu": itemsMenu, "proveedor": proveedor})



'''------------------------------------------
                                Módulo: eliminarProveedor

- Descripción:  
Este módulo se encarga de eliminar un proveedor existente en la base de datos. Se utiliza para borrar los datos de un proveedor que ya no es necesario.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un proveedor existente en la base de datos para eliminar.

- Postcondiciones:
El proveedor debe ser eliminado de la base de datos.
Se debe mostrar la página de listado de proveedores sin el proveedor eliminado.

-------------------------------------------''' 
@login_required
def eliminarProveedor(request, id):

    proveedor = Proveedor.objects.using('docLaruex').filter(id=id)[0]
    proveedor.delete(using="docLaruex")

    # volver a página Listado de Proveedores

    return ListadoProveedores(request)


'''------------------------------------------
                                Módulo: agregarNotificacion

- Descripción:  
Este módulo es responsable de agregar una nueva notificación a un documento específico. Los datos de la notificación son recibidos por medio de una solicitud POST y son guardados en la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en el sistema.
La solicitud recibida debe ser de tipo POST.
Los datos necesarios para crear una nueva notificación (id_doc, tituloNotificacion, resumenNotificacion, estadoNotificacion) deben estar incluidos en la solicitud.

- Postcondiciones:
Una nueva notificación es creada y almacenada en la base de datos.

-------------------------------------------''' 
@login_required
def agregarNotificacion(request):

    nuevaNotificacion = Notificacion(id_doc=Objeto.objects.using("docLaruex").filter(id=request.POST.get("id_doc")).get(),
    titulo=request.POST.get("tituloNotificacion"), resumen=request.POST.get("resumenNotificacion"), estado_notificacion=EstadosNotificaciones.objects.using("docLaruex").filter(id=request.POST.get("estadoNotificacion")).get(), creador=AuthUser.objects.using("docLaruex").filter(id=request.user.id).get(), fecha=date.today())
    nuevaNotificacion.save(using='docLaruex')

    return JsonResponse({"Notificacion": "ok"}, safe=False)



'''------------------------------------------
                                Módulo: datosNotificaciones

- Descripción:  
Este módulo es responsable de obtener los datos de las notificaciones asociadas a un documento específico y devolverlos en formato JSON.

- Precondiciones:
El usuario debe haber iniciado sesión en el sistema.
La solicitud recibida debe contener el id del documento para el cual se quieren obtener las notificaciones.

- Postcondiciones:
Los datos de las notificaciones asociadas al documento son devueltos en formato JSON.

-------------------------------------------''' 
@login_required
def datosNotificaciones(request, id_doc):
    notificaciones = Notificacion.objects.using('docLaruex').filter(id_doc=Objeto.objects.using("docLaruex").filter(id=id_doc).first()).values('id', 'titulo', 'resumen', 'estado_notificacion__id','estado_notificacion__nombre', 'creador__first_name', 'creador__last_name','fecha')
    return JsonResponse(list(notificaciones), safe=False)



'''------------------------------------------
                                Módulo: consultarNotificaciones

- Descripción:  
Este módulo es responsable de obtener las últimas cinco notificaciones creadas y devolverlas en formato JSON.

- Precondiciones:
El usuario debe haber iniciado sesión en el sistema.

- Postcondiciones:
Si el usuario tiene habilitaciones para ver notificaciones o es administrador, las últimas cinco notificaciones creadas son devueltas en formato JSON.
Si el usuario no tiene habilitaciones para ver notificaciones y no es administrador, se devuelve un mensaje indicando que no hay notificaciones disponibles.

-------------------------------------------''' 
@login_required
def consultarNotificaciones(request):
    notificaciones = Notificacion.objects.using('docLaruex').order_by('-id').values('id', 'id_doc__nombre','id_doc__id', 'titulo', 'resumen', 'creador__first_name', 'creador__last_name', 'fecha')[:5]
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return JsonResponse(list(notificaciones), safe=False)
    else:
        return JsonResponse({"sinNotificaciones":" Sin Notificaciones"}, safe=False)


'''------------------------------------------
                                Módulo: consultarNotificacionesNuevas

- Descripción:  
Este módulo permite al usuario consultar las nuevas notificaciones que se han generado desde su última consulta. Para ello, se le proporciona el id de la última notificación que consultó. Se consultan las notificaciones que tienen un id mayor a este número y se devuelven las 5 más recientes en un formato JSON.

- Precondiciones:
El usuario debe estar autenticado.
id_ultima_notificacion es un entero que indica el id de la última notificación consultada por el usuario.

- Postcondiciones:
Si el usuario tiene habilitaciones o es administrador, se devuelve un JsonResponse con las notificaciones más recientes que tienen un id mayor a id_ultima_notificacion, en un formato JSON que incluye el id de la notificación, el id del objeto asociado a la notificación, el título, el resumen, el nombre y apellido del creador y la fecha de creación.
Si el usuario no tiene habilitaciones ni es administrador, se devuelve un JsonResponse con el mensaje "Sin Notificaciones", en un formato JSON.

-------------------------------------------''' 
@login_required
def consultarNotificacionesNuevas(request, id_ultima_notificacion):
    notificaciones = Notificacion.objects.using('docLaruex').filter(id__gt=id_ultima_notificacion).order_by('-id').values('id', 'id_doc__id', 'titulo', 'resumen', 'creador__first_name', 'creador__last_name', 'fecha')[:5]
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return JsonResponse(list(notificaciones), safe=False)
    else:
        return JsonResponse({"sinNotificaciones":" Sin Notificaciones"}, safe=False)


'''------------------------------------------
                                Módulo: verNotificacion

- Descripción:  
Este módulo permite al usuario ver una notificación en particular. Se le proporciona el id de la notificación y se consulta la información de la misma en la base de datos. Luego se renderiza la plantilla "docLaruex/notificacion.html" con los datos de la notificación y otros datos necesarios, como la lista de objetos MenuBar, la lista de estados de las notificaciones y una variable que indica si el usuario autenticado es un administrador o no.

- Precondiciones:
El usuario debe estar autenticado.
id es un entero que indica el id de la notificación que se quiere ver.

- Postcondiciones:
Se renderiza la plantilla "docLaruex/notificacion.html" con los siguientes parámetros:
itemsMenu: lista de objetos MenuBar.
notificacion: objeto Notificacion con el id especificado en id.
administrador: booleano que indica si el usuario autenticado es un administrador o no.
estados: lista de objetos EstadosNotificaciones.

-------------------------------------------''' 
@login_required
def verNotificacion(request, id):
        itemsMenu = MenuBar.objects.using("docLaruex").values()
        
        habilitacionesUsuario = comprobarHabilitaciones(request.user.id)
        estados = EstadosNotificaciones.objects.using("docLaruex").values()
        notificacion = Notificacion.objects.using("docLaruex").filter(id=id).first()
        
        return render(
                request,
                "docLaruex/notificacion.html",
                {"itemsMenu": itemsMenu, "notificacion": notificacion ,"administrador": esAdministrador(request.user.id), "estados":estados})



'''------------------------------------------
                                Módulo: editarNotificacion

- Descripción:  
Este módulo permite al usuario editar una notificación en particular. Se le proporciona el id de la notificación y se consulta la información de la misma en la base de datos.

- Precondiciones:
El usuario debe estar autenticado.
id es un entero que indica el id de la notificación que se quiere editar.

- Postcondiciones:
Si la petición es un POST, se actualiza el título y el resumen de la notificación en la base de datos y se renderiza la plantilla "docLaruex/notificacion.html" con los siguientes parámetros:
itemsMenu: lista de objetos MenuBar.
notificacion: objeto Notificacion con el id especificado en id.
Si la petición no es un POST, se renderiza la plantilla "docLaruex/editarNotificacion.html" con los siguientes parámetros:
itemsMenu: lista de objetos MenuBar.
notificacion: objeto Notificacion con el id especificado en id.

-------------------------------------------''' 
@login_required
def editarNotificacion(request, id):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    notificacion = Notificacion.objects.using('docLaruex').filter(id=id)[0]

    if request.method == 'POST':
        print("POST", request.POST)
        notificacion.titulo = request.POST['nuevoTitulo']
        print("------------------", request.POST['nuevoResumen'])
        notificacion.resumen = request.POST['nuevoResumen']
        notificacion.save(using="docLaruex")

        return render(
            request,
            "docLaruex/notificacion.html",
            {"itemsMenu": itemsMenu, "notificacion": notificacion})
    else:
        return render(
            request,
            "docLaruex/editarNotificacion.html",
            {"itemsMenu": itemsMenu, "notificacion": notificacion})

'''------------------------------------------
                                Módulo: eliminarNotificacion

- Descripción:  
Este módulo permite al usuario eliminar una notificación en particular. Se le proporciona el id de la notificación y se consulta la información de la misma en la base de datos.

- Precondiciones:
El usuario debe estar autenticado.
id es un entero que indica el id de la notificación que se quiere editar.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def eliminarNotificacion(request,id):
    if esAdministrador(request.user.id):
        Notificacion.objects.using("docLaruex").filter(id=id).delete()
        return listaNotificaciones(request)
    else:
        return accesoDenegado(request)

'''------------------------------------------
                                Módulo: listaNotificaciones

- Descripción:  
Este módulo devuelve una lista de notificaciones que están disponibles para el usuario actual. Si el usuario tiene permisos especiales, se le mostrarán todas las notificaciones disponibles, de lo contrario, solo se le mostrarán las notificaciones que correspondan a sus permisos. La información devuelta incluye el título, resumen, estado, creador, fecha y documento relacionado de cada notificación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Se muestra una lista de notificaciones disponibles para el usuario actual.
-------------------------------------------''' 

@login_required
def listaNotificaciones(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return render(request, 'docLaruex/listaNotificaciones.html', {"itemsMenu": itemsMenu,"administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})



'''------------------------------------------
                                Módulo: listaNotificacionesDatos

- Descripción:  
Este módulo devuelve una lista de notificaciones en formato JSON. La información devuelta incluye el título, resumen, estado, creador, fecha y documento relacionado de cada notificación.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
Se devuelve una lista de notificaciones en formato JSON.
-------------------------------------------''' 
@login_required
def listaNotificacionesDatos(request):
    notificaciones = Notificacion.objects.using('docLaruex').order_by('-fecha','-id').values('id', 'titulo', 'resumen', 'estado_notificacion__id','estado_notificacion__nombre', 'creador__first_name', 'creador__last_name','fecha','id_doc__id', 'id_doc__nombre')
    return JsonResponse(list(notificaciones), safe=False)





'''------------------------------------------
                                Módulo: listaNotificaciones

- Descripción:  
Este módulo devuelve una lista de notificaciones que están disponibles para el usuario actual. Si el usuario tiene permisos especiales, se le mostrarán todas las notificaciones disponibles, de lo contrario, solo se le mostrarán las notificaciones que correspondan a sus permisos. La información devuelta incluye el título, resumen, estado, creador, fecha y documento relacionado de cada notificación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Se muestra una lista de notificaciones disponibles para el usuario actual.
-------------------------------------------''' 

@login_required
def listaNotificacionesUsuario(request):
    id_usuario = request.user.id
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    if Notificacion.objects.using('docLaruex').filter(creador__id=id_usuario) or administrador:
        return render(request, 'docLaruex/listaNotificacionesUsuario.html', {"itemsMenu": itemsMenu,"administrador": administrador, "habilitacionesUsuario":list(habilitacionesUsuario)})
    else:
        return noEncontrado(request)



'''------------------------------------------
                                Módulo: listaNotificacionesDatos

- Descripción:  
Este módulo devuelve una lista de notificaciones en formato JSON. La información devuelta incluye el título, resumen, estado, creador, fecha y documento relacionado de cada notificación.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
Se devuelve una lista de notificaciones en formato JSON.
-------------------------------------------''' 

@login_required
def listaNotificacionesUsuarioDatos(request):
    id_usuario = request.user.id
    notificaciones = Notificacion.objects.using('docLaruex').filter(creador__id=id_usuario).order_by('-fecha','-id').values('id', 'titulo', 'resumen', 'estado_notificacion__id','estado_notificacion__nombre','creador__id', 'creador__first_name', 'creador__last_name','fecha','id_doc__id', 'id_doc__nombre')
    return JsonResponse(list(notificaciones), safe=False)

'''------------------------------------------
                                Módulo: listaNotificacionesDatos

- Descripción:  
Este módulo devuelve una lista de proyectos disponibles para el usuario actual. Si el usuario tiene permisos especiales, se le mostrarán todos los proyectos disponibles, de lo contrario, solo se le mostrarán los proyectos que correspondan a sus permisos. La información devuelta incluye el nombre, estado y entidad financiadora de cada proyecto, así como una lista de colaboradores asociados.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
Se muestra una lista de proyectos disponibles para el usuario actual.
-------------------------------------------''' 
@login_required
def ListadoProyectos(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    proyectos = Proyecto.objects.using("docLaruex").values()
    habilitaciones = Habilitaciones.objects.using("docLaruex").values()
    estados = Estado.objects.using("docLaruex").values()
    
    financiadores = EntidadesFinanciadoras.objects.using("docLaruex").order_by('nombre').values(
        'id', 'nombre', 'imagen')
    colaboradores = Entidades.objects.using("docLaruex").order_by('nombre').values(
        'id','nombre', 'imagen')

    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    return render(request, 'docLaruex/listaProyectos.html', {"itemsMenu": itemsMenu,"administrador": esAdministrador(request.user.id), "proyectos":list(proyectos), "habilitaciones":list(habilitaciones), "estados":list(estados), "colaboradores":list(colaboradores), "financiadores":list(financiadores)})


'''------------------------------------------
                                Módulo: DatosProyectos

- Descripción:  
Esta función se encarga de obtener los datos de los proyectos y devolverlos en formato JSON.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la función.
La base de datos "docLaruex" debe estar correctamente configurada y accesible.

- Postcondiciones:
Se devuelve un objeto JSON que contiene la lista de proyectos almacenados en la base de datos "docLaruex" ordenados por ID.-------------------------------------------''' 
@login_required
def DatosProyectos(request):

    proyectos = Proyecto.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('id').values('id','codigo', 'expediente','fecha_inicio', 'fecha_fin', 'presupuesto','objetivo', 'id__nombre', 'id__ruta','id__ruta_editable','id__id_estado__id', 'id__id_estado__nombre', 'id__id_habilitacion__id', 'id__id_habilitacion__titulo')
    return JsonResponse(list(proyectos), safe=False)


'''------------------------------------------
                                Módulo: ListadoActas

- Descripción:  
Esta función se encarga de obtener los datos de las actas y los convocantes, secretarios y miembros asociados a ellas, y pasarlos a la plantilla correspondiente.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la función.
La base de datos "docLaruex" debe estar correctamente configurada y accesible.

- Postcondiciones:
Se devuelve la plantilla correspondiente con la información de las actas y los convocantes, secretarios y miembros asociados a ellas.
-------------------------------------------''' 
@login_required
def ListadoActas(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    actas = Acta.objects.using("docLaruex").values()
    convocantes = Convocantes.objects.using("docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    secretarios = Secretarios.objects.using("docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    miembros = Miembros.objects.using("docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')

    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    return render(request, 'docLaruex/listaActas.html', {"itemsMenu": itemsMenu,"administrador": esAdministrador(request.user.id), "proyectos":list(actas), "convocantes":list(convocantes), "secretarios":list(secretarios), "miembros":list(miembros)})


'''------------------------------------------
                                Módulo: DatosActas

- Descripción:  
Esta función se encarga de obtener los datos de las actas y devolverlos en formato JSON. Si el usuario no es administrador, solo se muestran las actas de las habilitaciones a las que tiene acceso.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la función.
La base de datos "docLaruex" debe estar correctamente configurada y accesible.

- Postcondiciones:
Si el usuario es administrador, se devuelve un objeto JSON que contiene la lista de actas almacenadas en la base de datos "docLaruex" ordenados por ID.
Si el usuario no es administrador, se devuelve un objeto JSON que contiene la lista de actas almacenadas en la base de datos "docLaruex" ordenados por ID y filtrados por las habilitaciones a las que tiene acceso.
-------------------------------------------'''

@login_required
def DatosActas(request):
    if esAdministrador(request.user.id):
        actas = Acta.objects.using('docLaruex').order_by('id').values('id','fecha_inicio', 'fecha_cierre', 'convocante','ubicacion', 'secretario', 'sesion','consejo', 'id__ruta', 'id__ruta_editable')
        return JsonResponse(list(actas), safe=False)
    else:
        actas = Acta.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('id').values('id','fecha_inicio', 'fecha_cierre', 'convocante','ubicacion', 'secretario', 'sesion','consejo', 'id__ruta', 'id__ruta_editable')
        return JsonResponse(list(actas), safe=False)



'''------------------------------------------
                                Módulo: agregarActa

- Descripción:  
Este módulo se encarga de agregar una nueva acta al sistema. Se espera que el usuario proporcione ciertos datos a través de un formulario, como la fecha de inicio, la ubicación de la sesión, el número de sesión, el consejo al que se refiere la sesión, la información del convocante y del secretario, y los miembros presentes en la sesión. También se pueden agregar puntos y acuerdos a la acta.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
El usuario debe tener los permisos necesarios para agregar una nueva acta.
El formulario de datos de la nueva acta debe ser enviado con los campos requeridos.

- Postcondiciones:
Una nueva acta es agregada al sistema con los datos proporcionados por el usuario.
Los miembros presentes en la sesión son asociados con la nueva acta.
Los puntos y acuerdos relacionados con la sesión son asociados con la nueva acta.
-------------------------------------------'''
@login_required
def agregarActa(request, nuevoObjeto):
    
    
    print ("---------ENTRO ACTA----------")
    # Obtenemos los datos del formulario
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    convocante = Convocantes.objects.using("docLaruex").filter(id=request.POST.get("convocante")).get()
    secretario = Secretarios.objects.using("docLaruex").filter(id=request.POST.get("secretario")).get()


    print(request.POST.get("fecha_inicio"))
    if request.POST.get("fecha_cierre") == "":
        fechaCierre = None;
    else:
        fechaCierre = request.POST.get("fecha_cierre")

    # Creamos el objeto acta
    print ("---------ACTA CREAR----------")
    nuevaActa = Acta(id=nuevoObjeto, fecha_inicio=request.POST.get("fecha_inicio"), fecha_cierre=fechaCierre, convocante= convocante, ubicacion=request.POST.get("ubicacion"), secretario=secretario, sesion=request.POST.get("numSesion"), consejo=request.POST.get("nombreConsejo"))
    nuevaActa.save(using='docLaruex')
    print ("---------ACTA CREADA----------")

   # Creamos la relación entre el acta y los miembros
    miembros = Miembros.objects.using("docLaruex").filter(id__in=request.POST.getlist("miembros"))
    for m in miembros:
        nuevaRelActaMiembros = RelActaMiembros(id_acta=nuevaActa, id_miembro=m)
        nuevaRelActaMiembros.save(using='docLaruex')
    # Creamos la relación entre el acta y los puntos y acuerdos
    banderaHayPuntos = True
    i = 0
    while banderaHayPuntos: 

        numeroDePunto = "punto" + str(i)
        ordenNumeroPunto = "ordenPunto" + str(i)

        if (request.POST.get(numeroDePunto) ): 
            puntos_y_acuerdos=PuntosYAcuerdos(orden=request.POST.get(ordenNumeroPunto), tipo="Punto", descripcion=request.POST.get(numeroDePunto), acta_relacionada=nuevaActa)
            puntos_y_acuerdos.save(using='docLaruex')

        else:
            banderaHayPuntos=False

        i += 1 
        
        print ("---------MIEMBROS----------")

    return render(request, 'docLaruex/listaActas.html', {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: agregarAcuerdos

- Descripción:  
Este módulo se encarga de agregar nuevos acuerdos a una acta existente en el sistema. Se espera que el usuario proporcione los acuerdos a través de un formulario.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
El usuario debe tener los permisos necesarios para agregar nuevos acuerdos a una acta existente.
El formulario de datos de los nuevos acuerdos debe ser enviado con los campos requeridos.

- Postcondiciones:
Los nuevos acuerdos son agregados a la acta existente en el sistema.
Los nuevos acuerdos están asociados con la acta existente.
-------------------------------------------'''
@login_required
def agregarAcuerdos(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Buscamos el acta 
    acta = Acta.objects.using("docLaruex").filter(id=id).get()
    print("--- Datos del Request ---")
    print(request.POST)
    print("--- (((()))) ---")

    banderaHayAcuerdos = True
    i = 0
    while banderaHayAcuerdos: 
        numeroDeAcuerdo = "acuerdo" + str(i)
        ordenNumeroAcuerdo = "ordenAcuerdo" + str(i)

        if request.POST.get(numeroDeAcuerdo): 
            puntos_y_acuerdos=PuntosYAcuerdos(orden=request.POST.get(ordenNumeroAcuerdo), tipo="Acuerdo", descripcion=request.POST.get(numeroDeAcuerdo), acta_relacionada=acta)
            puntos_y_acuerdos.save(using='docLaruex')

        else:
            banderaHayAcuerdos=False

        i += 1 
    return render(request, 'docLaruex/acta.html', {"itemsMenu": itemsMenu, "acta":acta})



'''------------------------------------------
                                Módulo: agregarTipoEquipo

- Descripción:  
Este módulo se encarga de agregar un nuevo tipo de equipo al sistema. Se espera que el usuario proporcione el nombre del nuevo tipo de equipo a través de un formulario.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
El usuario debe tener los permisos necesarios para agregar un nuevo tipo de equipo.
El formulario de datos del nuevo tipo de equipo debe ser enviado con los campos requeridos.

- Postcondiciones:
Un nuevo tipo de equipo es agregado al sistema con el nombre proporcionado por el usuario.
-------------------------------------------'''
@login_required
def agregarTipoEquipo(request):
    CategoriaEquipo = TipoEquipo(nombre=request.POST.get("nombreTipoEquipo"))
    CategoriaEquipo.save(using='docLaruex')
    
    return JsonResponse({"TipoEquipo": "ok"}, safe=False)



'''------------------------------------------
                                Módulo: agregarReservaProcedimiento

- Descripción: 
Este módulo es utilizado para agregar una reserva de procedimiento en el sistema. Recibe una petición HTTP POST con información necesaria para crear una nueva reserva de procedimiento, la cual es almacenada en la base de datos.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
Se debe recibir una petición HTTP POST con la información necesaria para crear la reserva de procedimiento.

- Postcondiciones:
Se crea una nueva reserva de procedimiento en la base de datos.
Se retorna una respuesta HTTP JsonResponse indicando si la operación fue exitosa o no.

-------------------------------------------'''
@login_required
def agregarReservaProcedimiento(request):
    
    reserva =ReservasProcedimiento(procedimiento_reservado=request.POST['procedimientoReservado'], titulo=request.POST['tituloProcedimiento'], fecha=date.today(), responsable=AuthUser.objects.using("docLaruex").filter(id=request.POST.get("responsable")).get())
    reserva.save(using='docLaruex')
    
    return JsonResponse({"Reserva": "ok"}, safe=False)

'''------------------------------------------
                                Módulo: DatosHabilitacionesRelacionadas

- Descripción: 
Este módulo es utilizado para obtener información sobre las habilitaciones relacionadas con los usuarios en el sistema. Retorna una lista de objetos JSON con la información de las habilitaciones relacionadas con los usuarios, ordenada por el id de la habilitación de forma descendente.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:
Se retorna una lista de objetos JSON con la información de las habilitaciones relacionadas con los usuarios.

-------------------------------------------'''
@login_required
def DatosHabilitacionesRelacionadas(request):
    relacionHabilitacionesUsuarios = RelUsuarioHabilitaciones.objects.using('docLaruex').order_by('-id_habilitacion').values(
        'id_habilitacion', 'id_usuario', 'id_usuario__first_name', 'id_usuario__last_name', 'id_usuario__id', 'id_habilitacion__titulo', 'id_habilitacion__id', 'tipo', 'fecha')

    habilitacionesExistentes = []
    salida = []
    for h in relacionHabilitacionesUsuarios:
        if not h["id_habilitacion"] in habilitacionesExistentes:
            h["id_usuario"] = h["id_usuario__first_name"] + \
                " / " + h["id_usuario__first_name"]
            salida.append(h)
            habilitacionesExistentes.append(h["id_habilitacion"])
    return JsonResponse(list(relacionHabilitacionesUsuarios), safe=False)



'''------------------------------------------
                                Módulo: DatosHabilitacionesRelacionadas (RECARGADO)

- Descripción: 
Este módulo es utilizado para obtener información sobre las habilitaciones relacionadas con un usuario específico en el sistema. Retorna una lista de objetos JSON con la información de las habilitaciones relacionadas con el usuario, ordenada por el id de la habilitación de forma descendente.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
Se debe recibir el id del usuario para el cual se desean obtener las habilitaciones relacionadas.

- Postcondiciones:
Se retorna una lista de objetos JSON con la información de las habilitaciones relacionadas con el usuario especificado.

-------------------------------------------'''
@login_required
def DatosHabilitacionesRelacionadas(request, id):   
    if esAdministrador(request.user.id):
        relacionHabilitacionesUsuarios = RelUsuarioHabilitaciones.objects.using('docLaruex').filter(id_usuario=id).order_by('-id_habilitacion').values(
            'id_habilitacion', 'id_usuario', 'id_usuario__first_name', 'id_usuario__last_name', 'id_usuario__id', 'id_habilitacion__titulo', 'id_habilitacion__id', 'tipo', 'fecha')

        habilitacionesExistentes = []
        salida = []
        for h in relacionHabilitacionesUsuarios:
            if not h["id_habilitacion"] in habilitacionesExistentes:
                h["id_usuario"] = h["id_usuario__first_name"] + \
                    " / " + h["id_usuario__first_name"]
                salida.append(h)
                habilitacionesExistentes.append(h["id_habilitacion"])
        return JsonResponse(list(relacionHabilitacionesUsuarios), safe=False)


'''------------------------------------------
                                Módulo: DatosHabilitaciones (RECARGADO)

- Descripción: 
Este módulo es utilizado para obtener información sobre las habilitaciones relacionadas con un usuario específico en el sistema. Retorna una lista de objetos JSON con la información de las habilitaciones relacionadas con el usuario, ordenada por el id de la habilitación de forma descendente.

- Precondiciones:
El usuario debe estar autenticado en el sistema como administrador.

- Postcondiciones:
Se retorna una lista de objetos JSON con la información de las habilitaciones relacionadas con el usuario especificado.
-------------------------------------------'''

@login_required
def DatosHabilitaciones(request):
    if esAdministrador(request.user.id):
        habilitaciones = Habilitaciones.objects.using('docLaruex').order_by('id').values(
            'id','titulo')
        return JsonResponse(list(habilitaciones), safe=False)

'''------------------------------------------
                                Módulo: agregarHabilitacion

- Descripción: 
Este módulo es utilizado para agregar una nueva habilitación al sistema. Recibe el título de la habilitación como parámetro y la agrega a la base de datos.

- Precondiciones:
El usuario debe estar autenticado en el sistema como administrador.

- Postcondiciones:
Se agrega una nueva habilitación con el título especificado en la base de datos.
-------------------------------------------'''
@login_required
def agregarHabilitacion(request):
    if esAdministrador(request.user.id):
        nuevaHabilitacion = Habilitaciones(titulo=request.POST.get("titulo"))
        nuevaHabilitacion.save(using='docLaruex')
        
        return JsonResponse({"documento": "ok"}, safe=False)

'''------------------------------------------
                                Módulo: datosHabilitacionesAsociar

- Descripción: 
Este módulo es utilizado para obtener una lista de usuarios en el sistema que pueden ser asociados a una habilitación específica. Retorna una lista de objetos JSON con la información de los usuarios.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
El usuario debe ser un administrador.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosHabilitacionesAsociar(request):
    
    if esAdministrador(request.user.id):
        usuarios =  AuthUser.objects.using("docLaruex").values()
        return JsonResponse(list(usuarios), safe=False)


'''------------------------------------------
                                Módulo: datosHabilitacionesAsociar

- Descripción: 
Este módulo es utilizado para asociar una habilitación a uno o varios usuarios del sistema.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
El usuario debe ser un administrador.
Se debe recibir el id de la habilitación que se desea asociar.
Se deben recibir los ids de los usuarios a los que se desea asociar la habilitación, separados por "#".

- Postcondiciones:

Se crea una relación entre la habilitación y los usuarios especificados.

-------------------------------------------'''
@login_required
def asociarHabilitacion(request):
    # crear objeto en la tabla Objetos
    if esAdministrador(request.user.id):
        usuarios=request.POST.get("idUsuariosSeleccionados").split('#')
        for u in usuarios:
            usuario = u.split('@')
            if u != "":
                auxHabi= Habilitaciones.objects.using("docLaruex").filter(id=request.POST.get("habilitacion")).get() 
                auxUser =  AuthUser.objects.using("docLaruex").filter(id= usuario[0]).get()
                nuevaRelacion = RelUsuarioHabilitaciones(id_habilitacion=auxHabi, id_usuario=auxUser, fecha=datetime.now(
                ), tipo=usuario[1])
                nuevaRelacion.save(using='docLaruex')
        # return ListadoObjetos(request)
        return JsonResponse({"documento": "ok"}, safe=False)

'''------------------------------------------
                                Módulo: asociarHabilitacionTodosUsuarios

- Descripción: 
Este módulo es utilizado para asociar una habilitación a todos los usuarios del sistema.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
El usuario debe ser un administrador.
Se debe recibir el id de la habilitación que se desea asociar.

- Postcondiciones:

Se crea una relación entre la habilitación y todos los usuarios del sistema.

-------------------------------------------'''
@login_required
def asociarHabilitacionTodosUsuarios(request):
    if esAdministrador(request.user.id):
        usuarios=AuthUser.objects.using("docLaruex").values('id')

        for u in usuarios: 
            habilitacion= Habilitaciones.objects.using("docLaruex").filter(id=request.POST.get("habilitacion")).get() 
            auxUser =  AuthUser.objects.using("docLaruex").filter(id=u['id']).get() 
            nuevaRelacion = RelUsuarioHabilitaciones(id_habilitacion=habilitacion, id_usuario=auxUser, fecha=datetime.now(
            ), tipo="Técnico") 
            nuevaRelacion.save(using='docLaruex')
            # return ListadoObjetos(request)
        return JsonResponse({"documento": "ok"}, safe=False)


'''------------------------------------------
                                Módulo: InfoVerObjeto

- Descripción: 
Se encarga de mostrar información detallada sobre un objeto en particular. Se utiliza la función decoradora "@login_required" para asegurar que solo los usuarios autenticados puedan acceder a esta vista.

- Precondiciones:
 
El usuario debe estar autenticado en la aplicación.
El objeto debe existir en la base de datos y tener un ID válido.

- Postcondiciones:

Se muestra información detallada sobre el objeto en función del tipo de este, incluyendo los responsables, revisores y editores asignados, las habilitaciones necesarias para acceder al objeto, el estado actual, entre otros datos.
Si el usuario no tiene las habilitaciones necesarias para acceder al objeto, se muestra una página de acceso denegado.
Si el objeto no existe en la base de datos o el ID no es válido, se muestra una página de error.
-------------------------------------------'''
@login_required
def InfoVerObjeto(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    administrador = esAdministrador(request.user.id)
    secretaria = esSecretaria(request.user.id)
    direccion = esDirector(request.user.id)

    objeto = Objeto.objects.using("docLaruex").filter(id=id)[0]
    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    revisores = Revisores.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    editores = Editores.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
        
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    estados = Estado.objects.using("docLaruex").values('id', 'nombre')
    
    procedimientosExistentes = Procedimiento.objects.using(
        "docLaruex").values_list('id_doc__nombre', flat=True).distinct()


    #habilitacionNecesaria = comprobarHabilitacionObjeto(id)
    
    if objeto.tipo == "Procedimiento":
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)

        procedimiento = Procedimiento.objects.using("docLaruex").filter(id_doc=id,id_doc__id_habilitacion__in=habilitacionesUsuario)[0]
        
        if procedimiento is not None:
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/procedimiento.html",
                {"itemsMenu": itemsMenu, "procedimiento": procedimiento, "responsables": list(
                    responsables), "revisores": list(revisores), "editores": list(editores), "habilitaciones": list(habilitaciones), "habilitacionesUsuario": list(habilitacionesUsuario), "administrador":administrador,  "media":media, "cargo":cargo, "estados":list(estados)},
            )
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif objeto.tipo == "Formato":
        
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)
        #formato = Formatos.objects.using("docLaruex").filter(id_doc=id)[0]

        procedimientos = Procedimiento.objects.using("docLaruex").order_by('id_doc__nombre').values('id_doc__nombre','titulo', 'version')
        formato = Formatos.objects.using("docLaruex").filter(id_doc=id,id_doc__id_habilitacion__in=habilitacionesUsuario).first()

        procedimiento = Procedimiento.objects.using("docLaruex").filter(id_doc__nombre=formato.procedimiento).order_by('-version')[0]

        tarea = None
        registro = None
        if RegistroTareaProgramada.objects.using("docLaruex").filter(id_formato=formato.id_doc.id).exists():
            registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_formato=formato.id_doc.id)[0]
            
            if TareasProgramadas.objects.using("docLaruex").filter(id=registro.id_tarea_programada.id).exists():
                tarea = TareasProgramadas.objects.using("docLaruex").filter(id=registro.id_tarea_programada.id).values()[0]
                print('\033[91m'+'tarea: ' + '\033[92m', tarea)

        #comprobamos si el formato tiene un cargo
        if formato is not None:
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/formato.html",
                {"itemsMenu": itemsMenu, "formato": formato, "estados":list(estados),
                    "procedimiento": procedimiento, "habilitacionesUsuario": list(habilitacionesUsuario),  "media":media, "cargo":cargo, "administrador":administrador, "habilitaciones":list(habilitaciones), "editores":list(editores), "procedimientos":list(procedimientos), "tarea":tarea, "registro":registro},
            )
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif objeto.tipo == "Curriculum":
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)
        formaciones = FormacionCurriculum.objects.using("docLaruex").filter(id_curriculum=id).values('titulo','descripcion','horas','ruta','fecha_inicio','fecha_fin')
        if Curriculum.objects.using("docLaruex").filter(id=id, id_usuario=request.user.id) or (Curriculum.objects.using("docLaruex").filter(id=id) and administrador) or (Curriculum.objects.using("docLaruex").filter(id=id) and direccion):
            curriculum = Curriculum.objects.using("docLaruex").filter(id=id).values('id','id__id','id_usuario__id', 'id_usuario__first_name', 'id_usuario__last_name', 'id_contacto__id','id_contacto__telefono','id_contacto__telefono_fijo','id_contacto__email','id_contacto__direccion','id_contacto__info_adicional','id_contacto__puesto', 'id_contacto__nombre','id_contacto__extension', 'id__id_habilitacion','id__tipo', 'id__nombre', 'id__tipo','id__ruta').first()
                 
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/curriculum.html",
                {"itemsMenu": itemsMenu,"estados":list(estados), "curriculum": curriculum, "habilitacionesUsuario": list(habilitacionesUsuario),  "media":media, "administrador":administrador, "formaciones":list(formaciones),"secretaria":secretaria, "direccion":direccion}
            )

        elif (Curriculum.objects.using("docLaruex").filter(id=id, id__id_habilitacion__in = habilitacionesUsuario)):
            curriculum = Curriculum.objects.using("docLaruex").filter(id=id, id__id_habilitacion__in = habilitacionesUsuario).values('id','id_usuario__id', 'id_usuario__first_name', 'id_usuario__last_name', 'id_contacto__id','id_contacto__telefono','id_contacto__telefono_fijo','id_contacto__email','id_contacto__direccion','id_contacto__info_adicional','id_contacto__puesto','id_contacto__extension', 'id__id_habilitacion','id__tipo', 'id__nombre').first()        
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/curriculum.html",
                {"itemsMenu": itemsMenu,"estados":list(estados), "curriculum": curriculum, "habilitacionesUsuario": list(habilitacionesUsuario),  "media":media, "administrador":administrador, "formaciones":list(formaciones),"secretaria":secretaria, "direccion":direccion }
            )
        else: 
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
            
    elif objeto.tipo == "Documento":
        
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)
        
        #documento = Documento.objects.using("docLaruex").filter(id_doc=id)[0]
        documento = Documento.objects.using("docLaruex").filter(id_doc=id,id_doc__id_habilitacion__in=habilitacionesUsuario).first()
        
        #comprobamos si el formato tiene un cargo
        if documento is not None:
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/documento.html",
                {"itemsMenu": itemsMenu, "estados":list(estados), "documento": documento, "habilitacionesUsuario": list(habilitacionesUsuario),  "media":media, "cargo":cargo, "administrador":administrador, "rol":rol, "habilitaciones":list(habilitaciones)}
            )
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
        

    elif objeto.tipo == "Curso":
        
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)

        patrocinadores = Entidades.objects.using("docLaruex").values('id', 'nombre')
        contactos = Contacto.objects.using("docLaruex").filter(tipo_contacto__contains="Persona").values('id', 'nombre')
        tipoCursos = TipoCurso.objects.using("docLaruex").values('id', 'nombre')
        curso = Cursos.objects.using("docLaruex").filter(id=id,id__id_habilitacion__in=habilitacionesUsuario).first()
        infoCurso = Cursos.objects.using("docLaruex").filter(id=id).values('id__nombre','fecha_inicio', 'fecha_fin','resumen','descripcion', 'imagen', 'patrocinadores__nombre', 'tipo_curso__nombre', 'horas')[0]
        
        contenidoCurso = RelCursoContenido.objects.using("docLaruex").filter(id_curso=id).values('id_contenido','id_contenido__id','id_contenido__nombre_ponencia', 'id_contenido__fecha_ponencia','id_contenido__descripcion','id_contenido__ponente__nombre','id_contenido__archivo')

        #comprobamos si el formato tiene un cargo
        if curso is not None:
            media= "/media/archivos"
            return render(request, "docLaruex/curso.html" ,{"itemsMenu": itemsMenu, "infoCurso": infoCurso, "curso": curso, "contenidoCurso":list(contenidoCurso), "habilitacionesUsuario": list(habilitacionesUsuario), "administrador":administrador, "estados":list(estados), "media":media, "cargo":cargo,"secretaria":secretaria, "direccion":direccion, "habilitaciones":list(habilitaciones), "patrocinadores":list(patrocinadores), "tipoCursos":list(tipoCursos), "contactos":list(contactos)})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif objeto.tipo == "Proyecto":
        
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)
        colaboradores = RelProyectoColaboradores.objects.using("docLaruex").filter(id_proyecto=id).values('id_colaborador__nombre', 'id_colaborador__id', 'id_colaborador__imagen')
        financiadores = RelProyectoFinanciadores.objects.using("docLaruex").filter(id_proyecto=id).values('id_financiador__nombre', 'id_financiador__id', 'id_financiador__imagen')
        proyecto = Proyecto.objects.using(
            "docLaruex").filter(id=id,id__id_habilitacion__in=habilitacionesUsuario).first()
    
        if proyecto is not None:
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/proyecto.html",
                {"itemsMenu": itemsMenu, "proyecto": proyecto, "colaboradores":list(colaboradores),"financiadores":list(financiadores),"habilitaciones": list(habilitaciones), "habilitacionesUsuario": list(habilitacionesUsuario), "administrador":administrador, "media":media, "cargo":cargo, "estados":list(estados),"rol":rol},
            )
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif objeto.tipo == "Ubicacion":
        
        #llaves que abren la ubicación
        ubicacionLlave = Ubicaciones.objects.using('docLaruex').filter(id=id).first()
        llave = Llave.objects.using('docLaruex').filter(ubicacion=ubicacionLlave, nombre__contains="Original").values('imagen','id','responsable','responsable__first_name', 'responsable__last_name', 'color').first()

        #llaves almacenadas en la ubicación
        llavesUbicadas = False
        if RelLlavesUbicaciones.objects.using('docLaruex').filter(id_ubicacion=ubicacionLlave).exists():
            llavesUbicadas = True
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)

        padres = Ubicaciones.objects.using("docLaruex").filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id__padre__isnull=True).order_by('id__nombre').values('id', 'id__nombre')
        #ubicacion = Ubicaciones.objects.using("docLaruex").filter(id=id)[0]
        if Ubicaciones.objects.using("docLaruex").filter(id=id, id__id_habilitacion__in=habilitacionesUsuario).exists():
            ubicacion = Ubicaciones.objects.using("docLaruex").filter(id=id, id__id_habilitacion__in=habilitacionesUsuario)[0]
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
        tipoUbicaciones = TipoUbicacion.objects.using("docLaruex").values('id','nombre')
        

        tarea = None
        registro = None
        
        registros = []
        if TareasProgramadas.objects.using("docLaruex").filter(id_objeto=str(objeto.id)).exists():
            tarea = TareasProgramadas.objects.using("docLaruex").filter(id_objeto=str(objeto.id)).values('id', 'fecha_proximo_mantenimiento')[0]
            tareas = TareasProgramadas.objects.using("docLaruex").order_by('fecha_proximo_mantenimiento').filter(id_objeto=str(objeto.id)).values('id', 'fecha_proximo_mantenimiento')

            # comprobamos si tareas tiene más de un elemento
            if len(tareas) > 1:
                # tareas = tareas[1:] #eliminamos la primera tarea, pues ya la hemos obtenido antes
                # obtengo el último registro de cada tarea
                for t in tareas:
                    if RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=t['id']).exists():
                        registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=t['id']).order_by('-id').values('id', 'estado', 'estado__id', 'id_tarea_programada', 'id_tarea_programada','fecha_programada')[0]
                        # agrego información del evento al registro
                        registro['evento'] = TareasProgramadas.objects.using("docLaruex").filter(id=t['id']).values('id_evento__nombre','id_evento__id', 'id_evento__tipo_evento','id_evento__procedimiento_asociado', 'id_evento__estado', 'id_evento__periodicidad', 'id_evento__formato_asociado', 'observaciones')[0]
                        registros.append(registro)


            else: 
                if RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea['id']).exists():
                    registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea['id']).order_by('-id').values('id', 'estado', 'estado__id', 'id_tarea_programada', 'fecha_programada')[0]
                    # agrego información del evento asociado a la tarea
                    registro['evento'] = TareasProgramadas.objects.using("docLaruex").filter(id=tarea['id']).values('id_evento__nombre','id_evento__id', 'id_evento__tipo_evento','id_evento__procedimiento_asociado', 'id_evento__estado', 'id_evento__periodicidad', 'id_evento__formato_asociado', 'observaciones')[0]
                    registros.append(registro)

            # if RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea['id']).exists():
            #     registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea['id']).order_by('-id').values('id', 'estado', 'estado__id')[0]

         #comprobamos si el formato tiene un cargo
        if ubicacion is not None:
            
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/ubicacion.html",
                {"itemsMenu": itemsMenu, "ubicacion": ubicacion, "habilitacionesUsuario": list(habilitacionesUsuario),  "media":media, "cargo":cargo, "estados":estados, "administrador":administrador, "habilitaciones":list(habilitaciones), "tipoUbicaciones":list(tipoUbicaciones), "llave":llave, "llavesUbicadas":llavesUbicadas, "tarea":tarea, "registro":registro, "padres":list(padres), "tareas":list(tareas), "registros":list(registros), "itemsRegistros":range(len(registros))}
            )
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


    elif objeto.tipo == "Equipo":
        tarea = None
        registro = None
        registros = []
        if TareasProgramadas.objects.using("docLaruex").filter(id_objeto=str(objeto.id)).exists():
            tarea = TareasProgramadas.objects.using("docLaruex").filter(id_objeto=str(objeto.id)).values('id', 'fecha_proximo_mantenimiento')[0]
            tareas = TareasProgramadas.objects.using("docLaruex").order_by('fecha_proximo_mantenimiento').filter(id_objeto=str(objeto.id)).values('id', 'fecha_proximo_mantenimiento')
        # comprobamos si tareas tiene más de un elemento 
        
            if len(tareas) > 1:
                # tareas = tareas[1:] #eliminamos la primera tarea, pues ya la hemos obtenido antes
                # obtengo el último registro de cada tarea
                for t in tareas:
                    if RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=t['id']).exists():
                        registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=t['id']).order_by('-id').values('id', 'estado', 'estado__id', 'id_tarea_programada', 'id_tarea_programada','fecha_programada')[0]
                        # agrego información del evento al registro
                        registro['evento'] = TareasProgramadas.objects.using("docLaruex").filter(id=t['id']).values('id_evento__nombre','id_evento__id', 'id_evento__tipo_evento','id_evento__procedimiento_asociado', 'id_evento__estado', 'id_evento__periodicidad', 'id_evento__formato_asociado', 'observaciones')[0]
                        registros.append(registro)


            else: 
                if RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea['id']).exists():
                    registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea['id']).order_by('-id').values('id', 'estado', 'estado__id', 'id_tarea_programada', 'fecha_programada')[0]
                    # agrego información del evento asociado a la tarea
                    registro['evento'] = TareasProgramadas.objects.using("docLaruex").filter(id=tarea['id']).values('id_evento__nombre','id_evento__id', 'id_evento__tipo_evento','id_evento__procedimiento_asociado', 'id_evento__estado', 'id_evento__periodicidad', 'id_evento__formato_asociado', 'observaciones')[0]
                    registros.append(registro)

  
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)
        
        #genera un código_laruex consecutivo
        # por el momento busca en un rango, para localizar el último valor
        # pues para agilizar la gestión se igualaron alguno cod_uex con cod_laruex
        ultimoCodigoLaruex = Equipo.objects.using("docLaruex").filter(cod_laruex__range =[2320,68000]).order_by('-cod_laruex').values('cod_laruex')[0]
        
        ultimoCodigo=ultimoCodigoLaruex['cod_laruex'] + 1
        
        habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values('id', 'titulo')
        #equipo = Equipo.objects.using("docLaruex").filter(id=id)[0]
        equipo = Equipo.objects.using("docLaruex").filter(id=id, id__id_habilitacion__in=habilitacionesUsuario).first()
        ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','id__nombre', 'id__padre__nombre')
        proveedores = Proveedor.objects.using("docLaruex").order_by('nombre').values('id','nombre')
        historicoUbicaciones = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).order_by('-fecha').values( 'id_ubicacion__id', 'id_ubicacion__id__id','id_ubicacion__id__nombre','id_equipo','fecha','id_ubicacion__alias', 'id_ubicacion__id__padre','id_ubicacion__id__padre__nombre')
        tipoDocumentos = TipoDocumentos.objects.using('docLaruex').values('id','nombre')

        restoUbicaciones = []
        ubicacionActual = []

        for h in historicoUbicaciones: 
            if h == historicoUbicaciones[0]:
                ubicacionActual.append(h)
            else:
                restoUbicaciones.append(h)
         #comprobamos si el formato tiene un cargo

        if equipo is not None:
            return render(
                request,
                "docLaruex/equipo.html",
                {"ultimoCodigo": ultimoCodigo,"itemsMenu": itemsMenu, "equipo": equipo, "historicoUbicaciones": historicoUbicaciones, "ubicacionActual":ubicacionActual, "restoUbicaciones":restoUbicaciones, "tipoDocumentos":tipoDocumentos, "ubicaciones":list(ubicaciones), "habilitaciones":list(habilitaciones), "habilitacionesUsuario": list(habilitacionesUsuario),"administrador": administrador, "estados":estados, "cargo":cargo, "proveedores":list(proveedores), "rol":rol, "tarea":tarea, "registro":registro, "tareas":list(tareas), "registros":list(registros), "itemsRegistros":range(len(registros))}
            ) 
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

    elif objeto.tipo == "Acta":    
        habilitacionesUsuario, cargo, rol = comprobarHabilitacion(request.user.id, objeto.id_habilitacion.id)        
        
        acta = Acta.objects.using(
            "docLaruex").filter(id=id,id__id_habilitacion__in=habilitacionesUsuario).first()

        miembros = RelActaMiembros.objects.using('docLaruex').filter(id_acta=id).values('id','id_miembro','id_miembro__id','id_miembro__first_name','id_miembro__last_name')

        convocantes = Convocantes.objects.using('docLaruex').order_by('first_name').values('id', 'first_name', 'last_name')
        secretarios = Secretarios.objects.using('docLaruex').order_by('first_name').values('id', 'first_name', 'last_name')
    
        puntos = PuntosYAcuerdos.objects.using('docLaruex').values('id','orden', 'tipo', 'descripcion').filter(acta_relacionada=id, tipo="Punto")
        acuerdos = PuntosYAcuerdos.objects.using('docLaruex').values('id','orden', 'tipo', 'descripcion').filter(acta_relacionada=id, tipo="Acuerdo")
        media = settings.MEDIA_URL +'archivos'
        if acta is not None:
            return render(
                    request,
                    "docLaruex/acta.html",
                    {"itemsMenu": itemsMenu, "acta": acta, "miembros": list(miembros), "convocantes":convocantes, "secretarios":secretarios,"puntos": list(puntos),"acuerdos": list(acuerdos),"administrador": administrador, "estados":estados, "habilitacionesUsuario": list(habilitacionesUsuario), "media": media,"range":range(20), "rol":rol})
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


    else:
        print("No existe ese archivo")



'''------------------------------------------
                                Módulo: verFabricante

- Descripción: 
Este módulo permite ver la información de un fabricante específico en la base de datos y renderizar la plantilla correspondiente con la información obtenida.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe haber pasado como argumento el id del fabricante que se desea ver.

- Postcondiciones:

Se muestra la información del fabricante seleccionado en la plantilla correspondiente.

-------------------------------------------'''
@login_required
def verFabricante(request, id):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    fabricante = Fabricante.objects.using('docLaruex').values('id','nombre', 'direccion', 'fijo', 'movil', 'correo', 'comentarios', 'web').filter(id=id)[0]

    return render(
            request,
            "docLaruex/fabricante.html",
            {"itemsMenu": itemsMenu, "fabricante": fabricante, "administrador": esAdministrador(request.user.id)})# Devuelve No editable un archivo dado un ID

'''------------------------------------------
                                Módulo: editarFabricante

- Descripción: 
Este módulo permite editar la información de un fabricante específico en la base de datos y renderizar la plantilla correspondiente con la información actualizada.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe haber pasado como argumento el id del fabricante que se desea editar.
El usuario debe ser administrador del sistema.

- Postcondiciones:

Se actualiza la información del fabricante en la base de datos con la información obtenida del formulario.
Se muestra la información actualizada del fabricante en la plantilla correspondiente.

-------------------------------------------'''
@login_required
def editarFabricante(request, id):


    itemsMenu = MenuBar.objects.using("docLaruex").values()
    fabricante = Fabricante.objects.using('docLaruex').filter(id=id)[0]

    if request.method == 'POST':
        print("POST", request.POST)
        fabricante.nombre = request.POST['nuevoNombre']
        fabricante.direccion = request.POST['nuevaDireccion']
        fabricante.fijo = request.POST['nuevoPrefijoFijo'] + request.POST['nuevoFijo']
        fabricante.movil = request.POST['nuevoPrefijoMovil'] + request.POST['nuevoMovil']
        fabricante.correo = request.POST['nuevoCorreo']
        
        fabricante.web = request.POST['nuevaWeb']
        fabricante.comentarios = request.POST['nuevosComentarios']
        fabricante.save(using="docLaruex")
        return render(
            request,
            "docLaruex/fabricante.html",
            {"itemsMenu": itemsMenu, "fabricante": fabricante})
    else:
        return render(
            request,
            "docLaruex/editarFabricante.html",
            {"itemsMenu": itemsMenu, "fabricante": fabricante})

'''------------------------------------------
                                Módulo: eliminarFabricante

- Descripción: 
Este módulo permite eliminar la información de un fabricante específico en la base de datos y redirigir a la página de listado de fabricantes.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe haber pasado como argumento el id del fabricante que se desea eliminar.
El usuario debe ser administrador del sistema.

- Postcondiciones:

Se elimina la información del fabricante de la base de datos.
Se redirige al usuario a la página de listado de fabricantes.

-------------------------------------------'''
@login_required
def eliminarFabricante(request, id):
    if esAdministrador(request.user.id):
        fabricante = Fabricante.objects.using('docLaruex').filter(id=id)[0]
        fabricante.delete(using="docLaruex")

        # volver a página listado de Fabricantes

        return ListadoFabricantes(request)

# =========================================================================
#                   MÓDULOS QUE PERMITEN EDITAR OBJETOS
# =========================================================================


'''------------------------------------------

                                Módulo: editarObjeto
La función editarObjeto, que recibe como argumento un objeto request y un id. Esta función se encarga de editar los datos de un objeto que se encuentra almacenado en la base de datos.

- Precondiciones:
    El usuario debe estar autenticado.
    El objeto con identificador id debe existir en la base de datos.

- Postcondiciones:
    El objeto en la base de datos se actualiza con los nuevos valores proporcionados por el usuario.
    
- Comentarios:
    La función comienza obteniendo todos los elementos del menú y comprobando si el usuario es administrador.
    Luego, se realiza una búsqueda del objeto en la base de datos y se recuperan los valores de los estados y las habilitaciones.
    Si el método de solicitud es POST, la función actualiza los campos del objeto con los nuevos valores proporcionados por el usuario.
    En función del tipo de objeto, se realizan diferentes acciones de actualización de los datos en la base de datos.
    La función devuelve la vista InfoVerObjeto con el objeto actualizado en caso de que todo haya ido bien.
-------------------------------------------'''


def editarObjeto(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    objeto = Objeto.objects.using('docLaruex').filter(id=id)[0]
    administrador = esAdministrador(request.user.id)

    if esAdministrador(request.user.id) or objeto.tipo == "Equipo":
        estados = Estado.objects.using("docLaruex").values()
        habilitaciones = Habilitaciones.objects.using('docLaruex').values()

        if request.method == 'POST':    
            if request.POST.get('nuevoNombre') is not None:
                objeto.nombre = request.POST['nuevoNombre']
            if request.POST.get('nuevoEstado') is not None:
                objeto.id_estado = Estado.objects.using('docLaruex').filter(id=request.POST['nuevoEstado'])[0]
            if request.POST.get('nuevaHabilitacion') is not None:
                objeto.id_habilitacion = Habilitaciones.objects.using('docLaruex').filter(id=request.POST['nuevaHabilitacion'])[0]
            objeto.save(using="docLaruex")

            if objeto.tipo == "Procedimiento":    
                procedimiento = Procedimiento.objects.using('docLaruex').filter(id_doc=id)[0]

                procedimiento.titulo = request.POST['nuevoTitulo']
                procedimiento.version = request.POST['nuevaVersion']
                procedimiento.fecha_verificacion = request.POST['nuevaFechaVerificacion'] 
                procedimiento.revisor = Revisores.objects.using('docLaruex').filter(id=request.POST['nuevoRevisor'])[0]    
                procedimiento.responsable = Responsables.objects.using('docLaruex').filter(id=request.POST['nuevoResponsable'])[0]   
                procedimiento.modificaciones = request.POST['nuevaModificacion']
                if request.POST.get('nuevoAdjuntoProcedimiento') is None:
                    if objeto.ruta is not None:
                        # find file name matches with *
                        procedimientoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(id) +  '.*')
                        if procedimientoOld:
                            os.remove(procedimientoOld[0])
                            rutaProcedimiento = settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(id) + '.' + request.FILES['nuevoAdjuntoProcedimiento'].name.split('.')[-1]
                            procedimientoFile = str(id) + '.' + request.FILES['nuevoAdjuntoProcedimiento'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoProcedimiento'], rutaProcedimiento)
                            objeto.ruta = procedimientoFile
                    else:
                        procedimientoFile = str(id) + '.' + request.FILES['nuevoAdjuntoProcedimiento'].name.split('.')[-1]
                        
                        rutaProcedimiento = settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(id) + '.' + request.FILES['nuevoAdjuntoProcedimiento'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoProcedimiento'], rutaProcedimiento)
                        objeto.ruta = procedimientoFile

                
                if request.POST.get('nuevoAdjuntoEditableProcedimiento') is None:
                    if objeto.ruta_editable is not None:
                        # find file name matches with *
                        procedimientoEditableOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(id) + '_edit.*')
                        if procedimientoEditableOld:
                            os.remove(procedimientoEditableOld[0])
                            rutaEditableProcedimiento = settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProcedimiento'].name.split('.')[-1]
                            procedimientoEditableFile = str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProcedimiento'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoEditableProcedimiento'], rutaEditableProcedimiento)
                            objeto.ruta_editable = procedimientoEditableFile
                    else:
                        procedimientoEditableFile = str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProcedimiento'].name.split('.')[-1]

                        rutaEditableProcedimiento = settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProcedimiento'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoEditableProcedimiento'], rutaEditableProcedimiento)
                        objeto.ruta_editable = procedimientoEditableFile
                objeto.save(using="docLaruex")
                procedimiento.save(using="docLaruex")
        
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+ id +'/')

            elif objeto.tipo == "Proyecto":    
                proyecto = Proyecto.objects.using('docLaruex').filter(id=id)[0]
                proyecto.codigo = request.POST['nuevoCodigo']
                proyecto.expediente = request.POST['nuevoExpediente']
                proyecto.fecha_inicio = request.POST['nuevaFechaInicio']
                proyecto.fecha_fin = request.POST['nuevaFechaFin']
                proyecto.presupuesto = request.POST['nuevoPresupuesto']
                if request.POST.get('nuevoAdjuntoProyecto') is None:
                    if objeto.ruta is not None:
                        # find file name matches with *
                        proyectoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Proyecto/' + str(id) +  '.*')
                        if proyectoOld:
                            os.remove(proyectoOld[0])
                            rutaProyecto = settings.MEDIA_ROOT + 'archivos/Proyecto/' + str(id) + '.' + request.FILES['nuevoAdjuntoProyecto'].name.split('.')[-1]
                            proyectoFile = str(id) + '.' + request.FILES['nuevoAdjuntoProyecto'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoProyecto'], rutaProyecto)
                            objeto.ruta = proyectoFile
                    else:
                        proyectoFile = str(id) + '.' + request.FILES['nuevoAdjuntoProyecto'].name.split('.')[-1]
                        
                        rutaProyecto = settings.MEDIA_ROOT + 'archivos/Proyecto/' + str(id) + '.' + request.FILES['nuevoAdjuntoProyecto'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoProyecto'], rutaProyecto)
                        objeto.ruta = proyectoFile

                
                if request.POST.get('nuevoAdjuntoEditableProyecto') is None:
                    if objeto.ruta_editable is not None:
                        # find file name matches with *
                        proyectoEditableOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Proyecto/' + str(id) + '_edit.*')
                        if proyectoEditableOld:
                            os.remove(proyectoEditableOld[0])
                            rutaEditableProyecto = settings.MEDIA_ROOT + 'archivos/Proyecto/' + str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProyecto'].name.split('.')[-1]
                            procedimientoEditableFile = str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProyecto'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoEditableProyecto'], rutaEditableProyecto)
                            objeto.ruta_editable = procedimientoEditableFile
                    else:
                        procedimientoEditableFile = str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProyecto'].name.split('.')[-1]

                        rutaEditableProyecto = settings.MEDIA_ROOT + 'archivos/Proyecto/' + str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableProyecto'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoEditableProyecto'], rutaEditableProyecto)
                        objeto.ruta_editable = procedimientoEditableFile
                objeto.save(using="docLaruex")
                proyecto.save(using="docLaruex")
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')

            elif objeto.tipo == "Acta":  
                
                acta = Acta.objects.using('docLaruex').filter(id=id)[0]      
                acta.fecha_inicio = request.POST['nuevaFechaInicio']
                acta.fecha_cierre = request.POST['nuevaFechaCierre']
                acta.convocante = Convocantes.objects.using('docLaruex').filter(id=request.POST.get('nuevoConvocante')).get()
                acta.secretario = Secretarios.objects.using("docLaruex").filter(id=request.POST.get("nuevoSecretario")).get()
                acta.ubicacion = request.POST['nuevaUbicacion']
                acta.sesion = request.POST['nuevaSesion']
                acta.consejo = request.POST['nuevoConsejo']
                acta.save(using="docLaruex")


                for i in range(len(request.POST.getlist('nuevoPuntoOrden'))):
                    print("punto", i, request.POST.getlist('nuevoPuntoOrden')[i], request.POST.getlist('nuevoPunto')[i])
                    PuntosYAcuerdos.objects.using('docLaruex').filter(acta_relacionada=id, tipo="Punto", orden=request.POST.getlist('nuevoPuntoOrden')[i]).update(descripcion=request.POST.getlist('nuevoPunto')[i])
                
                for i in range(len(request.POST.getlist('nuevoAcuerdoOrden'))):
                    print("acuerdo", i, request.POST.getlist('nuevoAcuerdoOrden')[i], request.POST.getlist('nuevoAcuerdo')[i])
                    PuntosYAcuerdos.objects.using('docLaruex').filter(acta_relacionada=id, tipo="Acuerdo", orden=request.POST.getlist('nuevoAcuerdoOrden')[i]).update(descripcion=request.POST.getlist('nuevoAcuerdo')[i])
            
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')


            elif objeto.tipo == "Equipo":
                equipo = Equipo.objects.using('docLaruex').filter(id=id)[0]   
                equipo.cod_laruex = request.POST['nuevoCodigoLaruex']
                equipo.cod_uex = request.POST['nuevoCodigoUex']   
                equipo.fecha_alta = request.POST['fechaAlta']       
                equipo.num_serie = request.POST['nuevoNumSerie']
                equipo.modelo = request.POST['nuevoModelo']
                equipo.descripcion = request.POST['nuevaDescripcion']
                equipo.precio = request.POST['nuevoPrecio']
                equipo.tipo_equipo = TipoEquipo.objects.using('docLaruex').filter(id=request.POST['nuevoTipoEquipo'])[0]
                equipo.fabricante = Fabricante.objects.using('docLaruex').filter(id=request.POST['nuevoFabricante'])[0]
                
                if request.POST.get("grupoEquipoEditar"):
                    grupo = GrupoEquipos.objects.using("docLaruex").filter(id=request.POST.get("grupoEquipoEditar"))[0]
                    equipo.grupo = grupo

                if 'altaUexEditar' in request.POST:
                    checkbox = request.POST['altaUexEditar']
                    if checkbox == "on":
                        equipo.alta_uex = 1
                else:
                    equipo.alta_uex = 0

                if request.POST.get('nuevaImagenEquipo') is None:
                    if objeto.ruta is not None:
                        # find file name matches with *
                        imagenOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Equipo/' + str(id) +  '.*')
                        if imagenOld:
                            os.remove(imagenOld[0])
                            rutaImagen = settings.MEDIA_ROOT + 'archivos/Equipo/' + str(id) + '.' + request.FILES['nuevaImagenEquipo'].name.split('.')[-1]
                            imagen = str(id) + '.' + request.FILES['nuevaImagenEquipo'].name.split('.')[-1]
                        subirDocumento(request.FILES['nuevaImagenEquipo'], rutaImagen)

                    else:
                        imagen = str(id) + '.' + request.FILES['nuevaImagenEquipo'].name.split('.')[-1]
                        
                        rutaImagen = settings.MEDIA_ROOT + 'archivos/Equipo/' + str(id) + '.' + request.FILES['nuevaImagenEquipo'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevaImagenEquipo'], rutaImagen)
                        objeto.ruta = imagen
                objeto.save(using="docLaruex")
                equipo.save(using="docLaruex")
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/') 
            
            elif objeto.tipo == "Ubicacion":     
                ubicacion = Ubicaciones.objects.using('docLaruex').filter(id=id)[0]       
                ubicacion.tipo_ubicacion = TipoUbicacion.objects.using('docLaruex').filter(id=request.POST['nuevoTipoUbicacion'])[0]
                ubicacion.latitud = request.POST['nuevaLatitud']
                ubicacion.longitud = request.POST['nuevaLongitud']    
                ubicacion.alias = request.POST['nuevoAlias']  
                objeto.nombre = request.POST['nuevoNombreUbicacion']
                if 'nuevoPadre' in request.POST:
                    padre = ObjetoPadre.objects.using('docLaruex').filter(id=request.POST['nuevoPadre'])[0]
                    objeto.padre = padre
                if 'eliminarPadre' in request.POST:
                    if request.POST['eliminarPadre'] == "1":
                        objeto.padre = None
                    else:
                        padre = ObjetoPadre.objects.using('docLaruex').filter(id=request.POST['nuevoPadre'])[0]
                        objeto.padre = padre
                objeto.save(using="docLaruex")
                ubicacion.save(using="docLaruex")
    
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/') 
            elif objeto.tipo == "Formato":        
                itemsMenu = MenuBar.objects.using("docLaruex").values()
                formato = Formatos.objects.using('docLaruex').filter(id_doc=id)[0]

                # objetos presentes en la vista de modifificar Procedimiento
                procedimientos = Procedimiento.objects.using("docLaruex").values('id_doc', 'id_doc__nombre', 'titulo','version')
                editores = Editores.objects.using("docLaruex").values('id', 'first_name', 'last_name')

                formato.titulo = request.POST['nuevoTitulo']
                formato.version = request.POST['nuevaVersion']

                plantilla = request.POST['nuevaPlantilla']
                if plantilla == 0 or plantilla == "" or plantilla == "None":
                    formato.plantilla = 0
                else:
                    formato.plantilla = 1

                formato.fecha_edicion = request.POST['nuevaFechaEdicion'] 
                formato.procedimiento = request.POST['nuevoProcedimiento']    
                formato.editor = Editores.objects.using('docLaruex').filter(id=request.POST['nuevoEditor'])[0]

                editable = request.POST['nuevoEditable'] 
                if editable == 0 or editable == "" or editable == "None":
                    formato.editable = 0
                else:
                    formato.editable = 1
                
                if request.POST.get('nuevoAdjuntoFormato') is None:
                    if objeto.ruta is not None:
                        # find file name matches with *
                        formatoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Formato/' + str(id) +  '.*')
                        if formatoOld:
                            os.remove(formatoOld[0])
                            rutaFormato = settings.MEDIA_ROOT + 'archivos/Formato/' + str(id) + '.' + request.FILES['nuevoAdjuntoFormato'].name.split('.')[-1]
                            formatoFile = str(id) + '.' + request.FILES['nuevoAdjuntoFormato'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoFormato'], rutaFormato)
                            objeto.ruta = formatoFile
                    else:
                        formatoFile = str(id) + '.' + request.FILES['nuevoAdjuntoFormato'].name.split('.')[-1]
                        
                        rutaFormato = settings.MEDIA_ROOT + 'archivos/Formato/' + str(id) + '.' + request.FILES['nuevoAdjuntoFormato'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoFormato'], rutaFormato)
                        objeto.ruta = formatoFile

                
                if request.POST.get('nuevoAdjuntoEditableFormato') is None:
                    if objeto.ruta_editable is not None:
                        # find file name matches with *
                        formatoEditableOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Formato/' + str(id) + '_edit.*')
                        if formatoEditableOld:
                            os.remove(formatoEditableOld[0])
                            rutaEditableFormato = settings.MEDIA_ROOT + 'archivos/Formato/' + str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableFormato'].name.split('.')[-1]
                            formatoEditableFile = str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableFormato'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoEditableFormato'], rutaEditableFormato)
                            objeto.ruta_editable = formatoEditableFile
                    else:
                        formatoEditableFile = str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableFormato'].name.split('.')[-1]

                        rutaEditableFormato = settings.MEDIA_ROOT + 'archivos/Formato/' + str(id) + '_edit.' + request.FILES['nuevoAdjuntoEditableFormato'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoEditableFormato'], rutaEditableFormato)
                        objeto.ruta_editable = formatoEditableFile
                objeto.save(using="docLaruex")
                formato.save(using="docLaruex")
        
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')

            elif objeto.tipo == "Curso":       
                curso = Cursos.objects.using('docLaruex').filter(id=id)[0]
                curso.resumen = request.POST['nuevoResumen']
                curso.descripcion = request.POST['nuevaDescripcion']
                curso.fecha_inicio = request.POST['nuevaFechaInicio']
                curso.fecha_fin = request.POST['nuevaFechaFin']
                curso.horas = request.POST['nuevasHoras']
                curso.patrocionadores = Entidades.objects.using('docLaruex').filter(id=request.POST['nuevoPatrocinador'])[0]
                curso.tipo_curso = TipoCurso.objects.using('docLaruex').filter(id=request.POST['nuevoTipoCurso'])[0]
                curso.save(using="docLaruex")
                
                if 'nuevoFicheroAdjuntoCurso' in request.FILES:
                    
                    rutaCurso = settings.MEDIA_ROOT + 'archivos/Curso/' + str(id) + '.' + request.FILES['nuevoFicheroAdjuntoCurso'].name.split('.')[-1]
                    archivoCurso = str(id) + '.' + request.FILES['nuevoFicheroAdjuntoCurso'].name.split('.')[-1]
                    if objeto.ruta is not None:
                        cursoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Curso/' + str(id) + '.*')
                        if cursoOld:
                            os.remove(cursoOld[0])
                    subirDocumento(request.FILES['nuevoFicheroAdjuntoCurso'], rutaCurso)
                    objeto.ruta = archivoCurso
                    objeto.save(using="docLaruex")

                    curso.save(using="docLaruex")
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')
               

            elif objeto.tipo == "Documento":
                documento = Documento.objects.using('docLaruex').filter(id_doc=id)[0]

                documento.editable = request.POST['nuevoEditable']
                documento.fecha_actualizacion = request.POST['nuevaFechaActualizacion']
                if request.POST.get('nuevoNumModificaciones') is not None:
                    documento.num_modificaciones = request.POST['nuevoNumModificaciones']
                if request.POST.get('nuevoTipoDocumento') is not None:
                    documento.tipo_documento = TipoDocumentos.objects.using('docLaruex').filter(id=request.POST['nuevoTipoDocumento'])[0]

                if 'nuevaVersion' in request.POST:
                    documento.version = request.POST['nuevaVersion']
                else:
                    documento.version = None
                
                if request.POST.get('nuevoAdjuntoDocumento') is None:
                    if objeto.ruta is not None:
                        # find file name matches with *
                        documentoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Documento/' + str(id) +  '.*')
                        if documentoOld:
                            os.remove(documentoOld[0])
                            rutaDocumento = settings.MEDIA_ROOT + 'archivos/Documento/' + str(id) + '.' + request.FILES['nuevoAdjuntoDocumento'].name.split('.')[-1]
                            documentoFile = str(id) + '.' + request.FILES['nuevoAdjuntoDocumento'].name.split('.')[-1]
                            subirDocumento(request.FILES['nuevoAdjuntoDocumento'], rutaDocumento)
                            objeto.ruta = documentoFile
                    else:
                        documentoFile = str(id) + '.' + request.FILES['nuevoAdjuntoDocumento'].name.split('.')[-1]
                        
                        rutaProcedimiento = settings.MEDIA_ROOT + 'archivos/Documento/' + str(id) + '.' + request.FILES['nuevoAdjuntoDocumento'].name.split('.')[-1]
                        
                        subirDocumento(request.FILES['nuevoAdjuntoDocumento'], rutaDocumento)
                        objeto.ruta = documentoFile
                objeto.save(using="docLaruex")
                documento.save(using="docLaruex")
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')

            elif objeto.tipo == "Curriculum":
                curriculum = Curriculum.objects.using('docLaruex').filter(id=id)[0]

                if 'nuevoFicheroAdjuntoCurriculum' in request.FILES:
                    if objeto.ruta is not None:
                        curriculumOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Curriculum/' + str(id) + '.*')
                        if curriculumOld:
                            os.remove(curriculumOld[0])
                            rutaCurriculum = settings.MEDIA_ROOT + 'archivos/Curriculum/' + str(id) + '.' + request.FILES['nuevoFicheroAdjuntoCurriculum'].name.split('.')[-1]
                            archivoCurriculum = str(id) + '.' + request.FILES['nuevoFicheroAdjuntoCurriculum'].name.split('.')[-1]
                    else:
                        archivoCurriculum = str(id) + '.' + request.FILES['nuevoFicheroAdjuntoCurriculum'].name.split('.')[-1]
                        rutaCurriculum = settings.MEDIA_ROOT + 'archivos/Curriculum/' + str(id) + '.' + request.FILES['nuevoFicheroAdjuntoCurriculum'].name.split('.')[-1]
                    subirDocumento(request.FILES['nuevoFicheroAdjuntoCurriculum'], rutaCurriculum)
                    objeto.ruta = archivoCurriculum
                    objeto.save(using="docLaruex")

                    curriculum.save(using="docLaruex")
                return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')

            else: 
                return render(request,"docLaruex/404.html", {"itemsMenu": itemsMenu})

            return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/') 

        else:
            if objeto.tipo == "Procedimiento":
                procedimiento = Procedimiento.objects.using('docLaruex').filter(id_doc=id)[0]
                responsables = Responsables.objects.using("docLaruex").values('id', 'first_name', 'last_name')
                revisores = Revisores.objects.using("docLaruex").values('id', 'first_name', 'last_name')
                return render(request,"docLaruex/editarProcedimiento.html",{"itemsMenu": itemsMenu, "procedimiento": procedimiento,"habilitaciones":list(habilitaciones), "revisores":list(revisores), "responsables":list(responsables)})

            elif objeto.tipo == "Proyecto":
                proyecto = Proyecto.objects.using('docLaruex').filter(id=id)[0]
                return render(request,"docLaruex/editarProyecto.html",{"itemsMenu": itemsMenu, "proyecto": proyecto, "estados":list(estados)})
            elif objeto.tipo == "Acta":
                acta = Acta.objects.using('docLaruex').filter(id=id)[0]
                return render(request,"docLaruex/editarActa.html",{"itemsMenu": itemsMenu, "acta": acta})
            elif objeto.tipo == "Equipo":
                equipo = Equipo.objects.using('docLaruex').filter(id=id)[0]
                tipoEquipo = TipoEquipo.objects.using('docLaruex').values('id','nombre') 
                fabricante = Fabricante.objects.using('docLaruex').values('id','nombre')
                gruposEquipos = GrupoEquipos.objects.using('docLaruex').values('id','nombre')
                return render(request,"docLaruex/editarEquipo.html",{"itemsMenu": itemsMenu, "equipo": equipo, "tipoEquipo":tipoEquipo, "fabricante":fabricante, "habilitaciones":list(habilitaciones), "administrador":administrador, "gruposEquipos":list(gruposEquipos)})

            elif objeto.tipo == "Ubicacion": 
                
                ubicacion = Ubicaciones.objects.using('docLaruex').filter(id=id)[0]
                tiposUbicaciones = TipoUbicacion.objects.using('docLaruex').values()
                return render(request,"docLaruex/editarUbicacion.html",{"itemsMenu":itemsMenu, "ubicacion": ubicacion, "habilitaciones":list(habilitaciones), "tiposUbicaciones":list(tiposUbicaciones)})

            elif objeto.tipo == "Formato":
                formato = Formatos.objects.using('docLaruex').filter(id_doc=id)[0]
                # objetos presentes en la vista de modifificar Procedimiento
                procedimientos = Procedimiento.objects.using("docLaruex").values('id_doc', 'id_doc__nombre', 'titulo','version')
                editores = Editores.objects.using("docLaruex").values('id', 'first_name', 'last_name')

                return render(request,"docLaruex/editarFormato.html",{"itemsMenu": itemsMenu, "formato": formato, "habilitaciones":list(habilitaciones), "procedimientos":list(procedimientos), "editores":list(editores)})

            elif objeto.tipo == "Curso":
                curso = Cursos.objects.using('docLaruex').filter(id=id)[0]
                patrocinadores = Entidades.objects.using("docLaruex").values('id', 'nombre')
                tipoCursos = TipoCurso.objects.using("docLaruex").values('id', 'nombre')


                
                return render(request, "docLaruex/editarCurso.html",{"itemsMenu": itemsMenu, "curso": curso, "habilitaciones":list(habilitaciones),"patrocinadores":list(patrocinadores), "tipoCursos":list(tipoCursos)})
            
            elif objeto.tipo == "Documento":
                documento = Documento.objects.using('docLaruex').filter(id_doc=id)[0]
                tipoDocumentos = TipoDocumentos.objects.using("docLaruex").values('id', 'nombre')
                return render(request,"docLaruex/editarDocumento.html",{"itemsMenu": itemsMenu, "documento": documento, "objeto":objeto,  "habilitaciones":list(habilitaciones), "tipoDocumentos":list(tipoDocumentos)})
            
            else: 
                return render(request,"docLaruex/404.html", {"itemsMenu": itemsMenu})

    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})



'''-------------------------------------------

                                Módulo: editarEstado

- Descripción: 
Este módulo permite editar el estado de un objeto en la base de datos.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe recibir como parámetros el id del objeto y el id del nuevo estado.

- Postcondiciones:

Se actualiza el estado del objeto en la base de datos.
Se redirecciona al usuario a la página de visualización del objeto.

-------------------------------------------'''

@login_required
def editarEstado(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    objeto = Objeto.objects.using('docLaruex').filter(id=id)[0]
    estado = Estado.objects.using('docLaruex').filter(id=request.POST['nuevoEstado'])[0]
    objeto.id_estado = estado
    objeto.save(using="docLaruex")
    return redirect('/private/docLaruex/verObjeto/'+str(id)+'/')



'''-------------------------------------------

                                Módulo: editarEstadoNotificacion

- Descripción: 
Este módulo permite editar el estado de un objeto en la base de datos.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe recibir como parámetros el id del objeto y el id del nuevo estado.

- Postcondiciones:

Se actualiza el estado del objeto en la base de datos.
Se redirecciona al usuario a la página de visualización del objeto.

-------------------------------------------'''

@login_required
def editarEstadoNotificacion(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    notificacion = Notificacion.objects.using('docLaruex').filter(id=id)[0]
    estado = EstadosNotificaciones.objects.using('docLaruex').filter(id=request.POST['nuevoEstadoNotificacion'])[0]
    notificacion.estado_notificacion = estado
    notificacion.save(using="docLaruex")
    return verNotificacion(request, id)


'''-------------------------------------------

                                Módulo: ArchivosAsociadosFormatos

- Descripción: 
Este módulo devuelve una lista de archivos asociados a un procedimiento en formato JSON.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe recibir como parámetro el id del procedimiento.

- Postcondiciones:

Se devuelve una lista de archivos asociados al procedimiento en formato JSON.

-------------------------------------------'''
@login_required
def ArchivosAsociadosFormatos(request, id_procedimiento):
    ArchivosAsociadosFormatos = Procedimiento.objects.using('docLaruex').order_by('-version').filter(procedimiento=id_procedimiento).values(
        'id_doc', 'id_doc__nombre', 'titulo', 'version', 'fecha_verificacion', 'responsable__first_name', 'responsable__last_name', 'revisor__first_name', 'revisor__last_name', 'modificaciones', 'id_estado')
    archivosExistentes = []
    salida = []
    for a in ArchivosAsociadosFormatos:
        if not a["id_doc__nombre"] in archivosExistentes:
            salida.append(a)
            archivosExistentes.append(a["id_doc__nombre"])
    return JsonResponse(list(salida), safe=False)



'''-------------------------------------------

                                Módulo: FormatosAsociadosProcedimiento

- Descripción: 
Este módulo devuelve una lista de formatos asociados a un procedimiento en formato JSON.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe recibir como parámetro el id del procedimiento.

- Postcondiciones:

Si el usuario es administrador, se devuelve una lista de todos los formatos asociados al procedimiento en formato JSON.
Si el usuario no es administrador, se devuelve una lista de los formatos asociados al procedimiento y que además estén habilitados para el usuario en formato JSON.
-------------------------------------------'''
@login_required
def FormatosAsociadosProcedimiento(request, id_procedimiento):
    
    formatosAsociados = Formatos.objects.using('docLaruex').order_by('-version').filter(procedimiento=id_procedimiento, plantilla=1,id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values(
            'id_doc', 'id_doc__nombre', 'titulo', 'version', 'editor__first_name', 'editor__last_name', 'fecha_edicion', 'plantilla' , 'id_doc__id_estado__id')
    formatosExistentes = []
    salida = []
    for f in formatosAsociados:
        if not f["id_doc__nombre"] in formatosExistentes:
            salida.append(f)
            formatosExistentes.append(f["id_doc__nombre"])
    return JsonResponse(list(salida), safe=False)

'''-------------------------------------------
                                Módulo: historialProcedimiento

- Descripción: 
Este módulo muestra el historial de un procedimiento específico en forma de una lista de objetos JSON. La lista incluye información sobre la versión, el responsable y el revisor del procedimiento, así como la fecha de verificación y el estado actual del procedimiento.

- Precondiciones:
 
El usuario debe haber iniciado sesión.
El procedimiento debe existir en la base de datos.

- Postcondiciones:

Se muestra el historial del procedimiento específico en forma de una lista de objetos JSON.
-------------------------------------------'''

@login_required
def historialProcedimiento(request, codigo_procedimiento):
    historialProcedimiento = Procedimiento.objects.using('docLaruex').order_by('-version').filter(id_doc__nombre=codigo_procedimiento, id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values(
            'id_doc', 'id_doc__nombre', 'titulo', 'version', 'responsable__first_name', 'responsable__last_name', 'revisor__first_name', 'revisor__last_name', 'fecha_verificacion', 'modificaciones', 'id_doc__id_estado')
    return JsonResponse(list(historialProcedimiento), safe=False)


'''-------------------------------------------
                                Módulo: historialFormato

- Descripción: 
Esta función devuelve el historial de versiones de un formato de documento en particular. Solo se mostrarán las versiones a las que el usuario tiene acceso.

- Precondiciones:
 
El usuario debe estar autenticado, el formato de documento y el procedimiento deben existir en la base de datos. Además, el usuario debe tener acceso a la habilitación a la que pertenece el formato de documento.

- Postcondiciones:

Se devuelve un objeto JsonResponse con una lista de diccionarios que representan cada versión del formato de documento. Cada diccionario contiene información sobre la versión, como el número de versión, si es editable, la fecha de edición y el nombre del editor.
-------------------------------------------'''
@login_required
def historialFormato(request, nombre,  procedimiento):
    historialFormato = Formatos.objects.using('docLaruex').order_by('-version').filter(id_doc__nombre=nombre, procedimiento=procedimiento, id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id), plantilla=1).values('id_doc','id_doc__padre','id_doc__padre', 'id_doc__nombre', 'titulo', 'version','editable','editor__first_name', 'editor__last_name', 'fecha_edicion', 'procedimiento', 'info_adicional')
    print('--------------')
    print('--------------')
    return JsonResponse(list(historialFormato), safe=False)

'''-------------------------------------------
                                Módulo: historialFormatoRellenos

- Descripción: 
Este módulo recupera el historial de formularios rellenados para un determinado nombre y procedimiento de un documento en particular. Retorna un objeto JSON que contiene información como el ID del documento, nombre del documento, título, si es editable o no, versión, nombre y apellido del editor, y la fecha de edición.

- Precondiciones:
El usuario debe estar autenticado y tener permiso para acceder a la información. 

- Postcondiciones:
Retorna un objeto JSON que contiene el historial de formularios rellenados para un determinado nombre y procedimiento de un documento en particular.
-------------------------------------------'''
@login_required
def historialFormatoRellenos(request, nombre,  procedimiento):
    historialFormato = Formatos.objects.using('docLaruex').order_by('-fecha_edicion').filter(id_doc__nombre=nombre, procedimiento=procedimiento, plantilla=0,id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values(
        'id_doc', 'id_doc__ruta', 'id_doc__nombre', 'titulo', 'editable', 'version', 'editor__first_name', 'editor__last_name', 'fecha_edicion', 'id_doc__padre', 'id_doc__padre__nombre','procedimiento', 'info_adicional')
    return JsonResponse(list(historialFormato), safe=False)


'''-------------------------------------------
                                Módulo: archivosAsociados

- Descripción: 
Este módulo recupera los archivos asociados a un documento en particular. Retorna un objeto JSON que contiene información como el ID del documento asociado, nombre del documento, tipo de documento, ID de habilitación, título de habilitación, apellido y nombre del creador, fecha de subida, ID de estado y nombre de estado.

- Precondiciones:
El usuario debe estar autenticado y tener permiso para acceder a la información.

- Postcondiciones:
Retorna un objeto JSON que contiene la lista de archivos asociados a un documento en particular.
-------------------------------------------'''
@login_required
def archivosAsociados(request, id_documento):
    archivoAsociado = RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc__id=id_documento,id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values(
        'id_relacionado', 'id_relacionado__id','id_relacionado__nombre', 'id_relacionado__tipo', 'id_relacionado__id_habilitacion','id_relacionado__id_habilitacion__id','id_relacionado__id_habilitacion__titulo','id_relacionado__creador__last_name', 'id_relacionado__creador__first_name', 'id_relacionado__fecha_subida', 'id_relacionado__id_estado__id', 'id_relacionado__id_estado__nombre')
    archivoAsociadoInverso = RelacionDocumentacionesInverso.objects.using('docLaruex').filter(id_doc__id=id_documento,id_doc__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values(
        'id_relacionado', 'id_relacionado__id','id_relacionado__nombre', 'id_relacionado__tipo', 'id_relacionado__id_habilitacion','id_relacionado__id_habilitacion__id','id_relacionado__id_habilitacion__titulo', 'id_relacionado__creador__last_name', 'id_relacionado__creador__first_name', 'id_relacionado__fecha_subida', 'id_relacionado__id_estado__id', 'id_relacionado__id_estado__nombre')
    salida = list(archivoAsociado) + list(archivoAsociadoInverso)
    return JsonResponse(salida, safe=False)


'''-------------------------------------------
                                Módulo: asociarArchivos

- Descripción: 
Este módulo asocia archivos a un formato de documento en particular. Toma como entrada el ID del objeto actual y los IDs de los objetos asociados seleccionados. Luego, itera a través de los IDs de los objetos asociados y los asocia al objeto actual si aún no se han asociado previamente.

- Precondiciones:
 El usuario debe estar autenticado y tener permiso para asociar archivos.

- Postcondiciones:
Asocia archivos a un formato de documento en particular. Retorna un objeto JSON que indica si la asociación de archivos se realizó correctamente o no.
-------------------------------------------'''
@login_required
def asociarArchivos(request):
    objetoActual = Objeto.objects.using('docLaruex').filter(
        id=request.POST.get('idFormatoActual')).get()
    for id in request.POST.get("idArchivosSeleccionados").split("#"):
        if id != '':
            objetoAsociado = ObjetoRelacionado.objects.using(
                'docLaruex').filter(id=id).get()
            if not RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoActual, id_relacionado=objetoAsociado).exists() and not RelacionDocumentacionesInverso.objects.using('docLaruex').filter(id_doc=objetoAsociado, id_relacionado=objetoActual).exists():
                relacion = RelacionDocumentaciones(
                    id_doc=objetoActual, id_relacionado=objetoAsociado)
                relacion.save(using="docLaruex")

    
    return JsonResponse({"salida": "ok"}, safe=False)

'''-------------------------------------------
                                Módulo: agregarArchivo

- Descripción: 
Agrega un archivo a la base de datos y almacenarlo en el servidor en la ubicación correspondiente. La función recibe una solicitud HTTP (request) que contiene los detalles del archivo que se va a agregar, incluyendo el tipo de archivo, su nombre, su estado y su ubicación.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
El formulario de agregación de archivo debe haber sido enviado por el usuario.

- Postcondiciones:
El archivo debe ser agregado correctamente a la base de datos.
El archivo debe ser almacenado en el servidor en la ubicación especificada.
Si el archivo es editable, la versión editable también debe ser almacenada en el servidor.

-------------------------------------------'''
@login_required
def agregarArchivo(request):
    ficheroAdjunto = "ficheroAdjunto"+request.POST.get("tipoObjeto")


    
    ficheroAdjuntoEditable = "ficheroAdjunto"+request.POST.get("tipoObjeto")+"Editable"

    # obtener tipo de icono
    if request.POST.get("tipoObjeto") == "Procedimiento":
        icono = '<i class="fa-duotone fa-books fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Formato":
        icono = '<i class="fa-duotone fa-file-invoice fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Curriculum":
        icono = '<i class="fa-duotone fa-file-contract fa-2x" ></i>'
    elif request.POST.get("tipoObjeto") == "Documento": 
        icono = '<i class="fa-duotone fa-file fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Ubicacion":
        icono = '<i class="fa-solid fa-building fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Equipo":
        icono = '<i class="fa-solid fa-plug fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Proyecto":
        icono = '<i class="fa-duotone fa-handshake fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Acta":
        icono = '<i class="fa-duotone fa-typewriter fa-2x"></i>'
    elif request.POST.get("tipoObjeto") == "Curso":
        icono = '<i class="fa-regular fa-graduation-cap fa-2x"></i>'
    else:
        icono = ' '

    creador = AuthUser.objects.using('docLaruex').filter(id=request.user.id)[0]
    estado = Estado.objects.using('docLaruex').filter(id=1)[0]

    


    if 'versionActualizada' in request.POST:
        #estado obsoleto
        estadoObsoleto = Estado.objects.using('docLaruex').filter(id=5)[0]

        procedimientosObsoletos = Procedimiento.objects.using('docLaruex').filter(id_doc__nombre=request.POST.get("nombreObjeto")).values('id_doc')

        for p in procedimientosObsoletos:
            objetoObsoleto = Objeto.objects.using('docLaruex').filter(id=p['id_doc'])[0]
            objetoObsoleto.id_estado = estadoObsoleto
            objetoObsoleto.save(using="docLaruex")

    if 'estado' in request.POST:
        estado = Estado.objects.using('docLaruex').filter(id=request.POST.get("estado"))[0]
        
    habilitacion = Habilitaciones.objects.using(
        'docLaruex').filter(id=request.POST.get("habilitacion"))[0]
    
    print("---------------- Paso 4: paso las habilitaciones ----------------")
    # comprueba si ese objeto hereda de otro y crea el objeto en la tabla Objeto
    if 'padre' in request.POST:
        padreObjeto = ObjetoPadre.objects.using("docLaruex").filter(id=request.POST.get("padre"))[0]
        nuevoObjeto = Objeto(nombre=request.POST.get("nombreObjeto"), fecha_subida=datetime.now(
        ), tipo=request.POST.get("tipoObjeto"), creador=creador, id_estado=estado, id_habilitacion=habilitacion, icono=icono, padre=padreObjeto)
        nuevoObjeto.save(using='docLaruex')
    else:
        nuevoObjeto = Objeto(nombre=request.POST.get("nombreObjeto"), fecha_subida=datetime.now(
        ), tipo=request.POST.get("tipoObjeto"), creador=creador, id_estado=estado, id_habilitacion=habilitacion, icono=icono)
        nuevoObjeto.save(using='docLaruex')
    print("---------------- Paso 5: vemos si tiene padre o no  ----------------")

    # subida de archivo no editable siempre que no sea una ubicación o un equipo
    if (ficheroAdjunto != "ficheroAdjuntoUbicacion") and (ficheroAdjunto != "ficheroAdjuntoEquipo"):
        if request.FILES.get(ficheroAdjunto) is not None:
            ruta = settings.MEDIA_ROOT + 'archivos/' + nuevoObjeto.tipo + '/' + str(nuevoObjeto.id) + '.' + request.FILES[ficheroAdjunto].name.split('.')[-1]   
            subirDocumento(request.FILES[ficheroAdjunto], ruta)
        
        
            nuevoObjeto.ruta = str(nuevoObjeto.id) + '.' + request.FILES[ficheroAdjunto].name.split('.')[-1]
    nuevoObjeto.save(using='docLaruex')
    print("---------------- Paso 6: agregro el objeto  ----------------")
    
    
    # subida de archivo editable (DOCX / Excel) 
    if 'ficheroAdjuntoEditable' in request.FILES:
    # if request.FILES.get(ficheroAdjuntoEditable):
        ruta_editable = settings.MEDIA_ROOT + 'archivos/' + nuevoObjeto.tipo + '/' + str(nuevoObjeto.id) + '_edit.' + request.FILES[ficheroAdjuntoEditable].name.split('.')[-1]
        subirDocumento(request.FILES[ficheroAdjuntoEditable], ruta_editable)
        nuevoObjeto.ruta_editable = str(nuevoObjeto.id) + '_edit.' + request.FILES[ficheroAdjuntoEditable].name.split('.')[-1]
    nuevoObjeto.save(using='docLaruex')
    

    if request.POST.get("tipoObjeto") == "Procedimiento":
        agregarProcedimiento(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Formato":
        agregarFormato(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Curriculum":
        agregarCurriculum(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Documento":
        agregarDocumento(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Ubicacion":
        agregarUbicacion(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Equipo":
        agregarEquipo(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Proyecto":
        
        print ("---------VOY A AGREGAR ACTA----------")
        agregarProyecto(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Acta":
        
        print ("---------vOY A AGREGAR ACTA----------")
        agregarActa(request, nuevoObjeto)
    elif request.POST.get("tipoObjeto") == "Curso":
        agregarCurso(request, nuevoObjeto)
    else:

        return JsonResponse({"Sin documento": "Error"}, safe=False)
    # return ListadoObjetos(request)
    
    return JsonResponse({"idObjeto": nuevoObjeto.id}, safe=False)


'''-------------------------------------------
                                Módulo: agregarProcedimiento

- Descripción: 
s una vista que se encarga de crear un nuevo objeto de procedimiento en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar procedimiento.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar el procedimiento.
En la solicitud POST deben incluirse los campos "responsable", "revisor", "fechaVerificacion", "tituloProcedimiento", "version" y "modificaciones" para crear el objeto de procedimiento.

- Postcondiciones:
Se crea un nuevo objeto de procedimiento en la tabla Procedimientos de la base de datos.
El objeto de procedimiento creado tiene los siguientes campos: ID del objeto al que se le agregó el procedimiento, fecha de verificación, responsable, revisor, título, versión y modificaciones.

-------------------------------------------'''
@login_required
def agregarProcedimiento(request, nuevoObjeto):
    # crear objeto en la tabla Procedimientos
    responsable = Responsables.objects.using('docLaruex').filter(
        id=request.POST.get("responsable"))[0]
    revisor = Revisores.objects.using('docLaruex').filter(
        id=request.POST.get("revisor"))[0]

    nuevoProcedimiento = Procedimiento(id_doc=nuevoObjeto, fecha_verificacion=request.POST.get("fechaVerificacion"), responsable=responsable, revisor=revisor, titulo=request.POST.get(
        "tituloProcedimiento"),  version=request.POST.get("version"), modificaciones=request.POST.get("modificaciones"))
    nuevoProcedimiento.save(using='docLaruex')



'''-----------------------------------------------------------
        MÉTODOS PARA ELIMINAR ARCHIVOS / OBJETOS
-----------------------------------------------------------'''


'''-------------------------------------------
                                Módulo: eliminarObjeto

- Descripción: 
s una vista que se encarga de eliminar un nuevo objetode la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar procedimiento.
El objeto/archivo que se va a eliminar debe existir en la base de datos.
El tipo de objeto/archivo que se va a eliminar debe ser uno de los tipos válidos (Procedimiento, Formato, Curriculum, Documento, Ubicacion, Equipo, Proyecto, Acta o Curso).

- Postcondiciones:
El objeto/archivo con el ID especificado se elimina de la base de datos.
Si se eliminó con éxito, se renderiza la plantilla 'docLaruex/eliminadoExito.html' con el diccionario "itemsMenu" que contiene la información necesaria para construir la barra de menú en la plantilla.

-------------------------------------------'''
@login_required
def eliminarObjeto(request,id_objeto):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    objetoEliminar = Objeto.objects.using("docLaruex").filter(id=id_objeto)[0]  
    if objetoEliminar.tipo == "Procedimiento":
        eliminarProcedimiento(request, objetoEliminar)
    elif objetoEliminar.tipo == "Formato":
        eliminarFormato(request, objetoEliminar)
    elif objetoEliminar.tipo == "Curriculum":
        eliminarCurriculum(request, objetoEliminar)
    elif objetoEliminar.tipo == "Documento":
        eliminarDocumento(request, objetoEliminar)
    elif objetoEliminar.tipo == "Ubicacion":
        eliminarUbicacion(request, objetoEliminar)
    elif objetoEliminar.tipo == "Equipo":
        eliminarEquipo(request, objetoEliminar)
    elif objetoEliminar.tipo == "Proyecto":
        eliminarProyecto(request, objetoEliminar)
    elif objetoEliminar.tipo == "Acta":
        eliminarActa(request, objetoEliminar)
    elif objetoEliminar.tipo == "Curso":
        eliminarCurso(request, objetoEliminar)
    else:
        return JsonResponse({"Sin documento": "Error"}, safe=False)
    # return ListadoObjetos(request)
    
    return render(request, 'docLaruex/eliminadoExito.html', {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: eliminarProcedimiento ¡¡¡¡¡ AUN EN PROCESO!!!

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
 Esta función elimina un objeto de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
el usuario debe estar autenticado

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarProcedimiento(request, objetoEliminar):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    procedimiento = Procedimiento.objects.using("docLaruex").filter(id_doc=objetoEliminar)[0]
    relDocumentaciones = RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoEliminar)
    evento = None
    archivoProcedimiento = glob.glob(settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(objetoEliminar.id) + '.*')
    archivoProcedimientoEditable = glob.glob(settings.MEDIA_ROOT + 'archivos/Procedimiento/' + str(objetoEliminar.id) + '_edit.*')

    if archivoProcedimiento:
        os.remove(archivoProcedimiento[0])
    if archivoProcedimientoEditable:
        os.remove(archivoProcedimientoEditable[0])

    if Eventos.objects.using('docLaruex').filter(procedimiento_asociado=procedimiento).exists():
        evento = Eventos.objects.using('docLaruex').filter(procedimiento_asociado=procedimiento)[0]
        evento.delete()

    relDocumentaciones.delete()
    procedimiento.delete()
    objetoEliminar.delete()

    return render(request,"docLaruex/eliminadoExito.html", {"itemsMenu": itemsMenu, "tipo":"Procedimiento"})


'''-------------------------------------------
                                Módulo: eliminarDocumento

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Documento de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarDocumento(request, objetoEliminar): 

    archivoDocumento = glob.glob(settings.MEDIA_ROOT + 'archivos/Documento/' + str(objetoEliminar.id) + '.*')
    archivoDocumentoEditable = glob.glob(settings.MEDIA_ROOT + 'archivos/Documento/' + str(objetoEliminar.id) + '_edit.*')

    if archivoDocumento:
        os.remove(archivoDocumento[0])
    if archivoDocumentoEditable:
        os.remove(archivoDocumentoEditable[0])
        
    RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoEliminar).delete()
    Documento.objects.using('docLaruex').filter(id_doc=objetoEliminar).delete()
    objetoEliminar.delete()

    return eliminadoExito(request)


'''-------------------------------------------
                                Módulo: eliminarFormato

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Formato de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
Muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarFormato(request, objetoEliminar):  
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    archivoFormato = glob.glob(settings.MEDIA_ROOT + 'archivos/Formato/' + str(objetoEliminar.id) + '.*')
    archivoFormatoEditable = glob.glob(settings.MEDIA_ROOT + 'archivos/Formato/' + str(objetoEliminar.id) + '_edit.*')
    formato = Formatos.objects.using('docLaruex').filter(id_doc=objetoEliminar)[0]
    evento = None
    if archivoFormato:
        os.remove(archivoFormato[0])
    if archivoFormatoEditable:
        os.remove(archivoFormatoEditable[0])


    if RegistroTareaProgramada.objects.using('docLaruex').filter(id_formato=formato).exists():
        RegistroTareaProgramada.objects.using('docLaruex').filter(id_formato=formato).delete()
    

    if Eventos.objects.using('docLaruex').filter(procedimiento_asociado=formato).exists():
        evento = Eventos.objects.using('docLaruex').filter(formato_asociado=formato)[0]
        evento.formato_asociado = None
        evento.save(using="docLaruex")
    formato.delete()
    objetoEliminar.delete()
    
    return render(request,"docLaruex/eliminadoExito.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: eliminarCurriculum

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Curriculum de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarCurriculum(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    formacionID = FormacionCurriculum.objects.using('docLaruex').filter(id_curriculum=id).values('id')
    archivoCurriculum = glob.glob(settings.MEDIA_ROOT + 'archivos/Curriculum/' + id + '.*')
    if archivoCurriculum:
        os.remove(archivoCurriculum[0])
    for formacion in formacionID:
        archivoFormacion = glob.glob(settings.MEDIA_ROOT + 'archivos/Curriculum/'+ id +'/' + str(formacion['id'])+ '.*')
        if archivoFormacion:
            os.remove(archivoFormacion[0])

    objetoCurriculum = Objeto.objects.using('docLaruex').filter(id=id).get()
    curriculum = Curriculum.objects.using('docLaruex').filter(id=objetoCurriculum).get()
    
    FormacionCurriculum.objects.using('docLaruex').filter(id_curriculum=curriculum).delete()
    Curriculum.objects.using('docLaruex').filter(id=objetoCurriculum).delete()
    Objeto.objects.using('docLaruex').filter(id=id).delete()
    rutaFormaciones = settings.MEDIA_ROOT + 'archivos/Curriculum/'+ id + '/'

    if os.path.exists(rutaFormaciones):
        if len(os.listdir(settings.MEDIA_ROOT + 'archivos/Curriculum/'+ id + '/')) == 0:
            os.rmdir(settings.MEDIA_ROOT + 'archivos/Curriculum/'+ id + '/')

    return render(request,"docLaruex/eliminadoExito.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: eliminarUbicación

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Ubicación de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarUbicacion(request, objetoEliminar): 
    
    ubicacion =Ubicaciones.objects.using('docLaruex').filter(id=objetoEliminar).get()
    ubicacion_eliminada = Ubicaciones.objects.using('docLaruex').get(id=Objeto.objects.using('docLaruex').get(id=1).id)
    
    archivoUbicacion = glob.glob(settings.MEDIA_ROOT + 'archivos/Ubicacion/' + str(objetoEliminar.id) + '.*')
    archivoUbicacionEditable = glob.glob(settings.MEDIA_ROOT + 'archivos/Ubicacion/' + str(objetoEliminar.id) + '_edit.*')

    if archivoUbicacion:
        os.remove(archivoUbicacion[0])
    if archivoUbicacionEditable:
        os.remove(archivoUbicacionEditable[0])
    
    
    if Objeto.objects.using('docLaruex').filter(padre=objetoEliminar).exists():
        Objeto.objects.using('docLaruex').filter(padre=objetoEliminar).update(padre=None)

    if RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoEliminar).exists():
        RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoEliminar).delete()

    if RegistroRetiradaStock.objects.using('docLaruex').filter(ubicacion=ubicacion).exists():
        RegistroRetiradaStock.objects.using('docLaruex').filter(ubicacion=ubicacion).update(ubicacion=ubicacion_eliminada)

    if RelUbicacionesEquipos.objects.using('docLaruex').filter(id_ubicacion=ubicacion).exists():
        RelUbicacionesEquipos.objects.using('docLaruex').filter(id_ubicacion=ubicacion).update(id_ubicacion=1)

    Ubicaciones.objects.using('docLaruex').filter(id=objetoEliminar).delete()
    objetoEliminar.delete()

    return eliminadoExito(request)

'''-------------------------------------------
                                Módulo: eliminarEquipo ¡¡¡¡¡ AUN EN PROCESO!!!

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Equipo de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarEquipo(request, objetoEliminar):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    archivoEquipo = glob.glob(settings.MEDIA_ROOT + 'archivos/Equipo/' + str(objetoEliminar.id) + '.*')

    if archivoEquipo:
        os.remove(archivoEquipo[0])
        
    RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoEliminar).delete()
    RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=Equipo.objects.using('docLaruex').filter(id=objetoEliminar).get()).delete()
    Equipo.objects.using('docLaruex').filter(id=objetoEliminar).delete()
    objetoEliminar.delete()
    return eliminadoExito(request)

@login_required
def agregarCodUex(request, id):
    equipo = Equipo.objects.using('docLaruex').filter(id=id)[0]
    equipo.cod_uex = request.POST.get("nuevoCodUex")
    equipo.save(using="docLaruex")
    return redirect('docLaruex:docLaruexInfoVerObjeto', id=id)


    
'''-------------------------------------------
                                Módulo: eliminarProyecto ¡¡¡¡¡ AUN EN PROCESO!!!

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Proyecto de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarProyecto(request, objetoEliminar):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()

    return eliminadoExito(request)

'''-------------------------------------------
                                Módulo: eliminarActa

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Acta de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarActa(request, objetoEliminar):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()

    PuntosYAcuerdos.objects.using('docLaruex').filter(acta_relacionada=objetoEliminar.id).delete()
    archivoActa = glob.glob(settings.MEDIA_ROOT + 'archivos/Acta/' + str(objetoEliminar.id) + '.*')
    if archivoActa:
        os.remove(archivoActa[0])
        
    archivoActaEditable = glob.glob(settings.MEDIA_ROOT + 'archivos/Acta/' + str(objetoEliminar.id) + '_edit.*')
    if archivoActaEditable:
        os.remove(archivoActaEditable[0])
        
    acta = Acta.objects.using('docLaruex').filter(id=objetoEliminar.id).get()
    RelActaMiembros.objects.using('docLaruex').filter(id_acta=acta).delete()
    RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=objetoEliminar).delete()
    Acta.objects.using('docLaruex').filter(id=objetoEliminar).delete()
    Objeto.objects.using('docLaruex').filter(id=objetoEliminar.id).delete()

    return eliminadoExito(request)


'''-------------------------------------------
                                Módulo: eliminarCurso ¡¡¡AUN EN PROCESO!!!!

- Parámetros de entrada: 
request y objetoEliminar

- Descripción: 
Esta función elimina un objeto de tipo Acta de la base de datos y los archivos asociados a él. Para eliminar los archivos, busca en una ubicación específica en la carpeta de medios de la aplicación web. Después de eliminar el objeto y los archivos, se muestra una página de éxito al usuario.

- Precondiciones:
El usuario debe estar autenticado para poder ejecutar esta función. Esto se indica mediante el decorador @login_required que precede a la definición de la función.

- Postcondiciones:
El objeto y los archivos asociados a él se eliminan de la base de datos y del sistema de archivos. La función muestra una página de éxito al usuario.


HAY QUE PONER RESTRICCIÓN PARA ADMINISTRADORES 
-------------------------------------------'''
@login_required
def eliminarCurso(request, objetoEliminar):    
    itemsMenu = MenuBar.objects.using("docLaruex").values()

    return eliminadoExito(request)



'''-------------------------------------------
                                Módulo: agregarFormato

- Descripción: 
s una vista que se encarga de crear un nuevo objeto de procedimiento en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar procedimiento.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar el procedimiento.

- Postcondiciones:
Se crea un nuevo objeto de formato en la tabla Formato de la base de datos.

-------------------------------------------'''
@login_required
def agregarFormato(request, nuevoObjeto):

    # crear objeto en la tabla Formatos
    infoAdicional = ""
    if request.POST.get("infoMuestra") is not None:
        if request.POST.get("infoAlicuota") is not None:
            infoAdicional = request.POST.get("infoMuestra") + "-" + request.POST.get("infoAlicuota")
        else:
            infoAdicional = request.POST.get("infoMuestra")


    editor = Editores.objects.using('docLaruex').filter(
        id=request.POST.get("editor"))[0]

    if(request.POST.get("editable")):
        nuevoFormato = Formatos(id_doc=nuevoObjeto, titulo=request.POST.get("tituloFormato"),  version=request.POST.get("versionFormato"), plantilla=request.POST.get(
            "plantilla"), editor=editor, fecha_edicion=request.POST.get("fechaEdicion"), procedimiento=request.POST.get("procedimientoAsociado"),editable=request.POST.get("editable"), info_adicional=infoAdicional)
    else:
        nuevoFormato = Formatos(id_doc=nuevoObjeto, titulo=request.POST.get("tituloFormato"),  version=request.POST.get("versionFormato"), plantilla=request.POST.get(
            "plantilla"), editor=editor, fecha_edicion=request.POST.get("fechaEdicion"), procedimiento=request.POST.get("procedimientoAsociado"), info_adicional=infoAdicional)
    nuevoFormato.save(using='docLaruex')

    if 'idRegistroTarea' in request.POST:     
        registroActual = RegistroTareaProgramada.objects.using('docLaruex').filter(id=request.POST.get('idRegistroTarea'))[0]
        formatoRelleno = Formatos.objects.using('docLaruex').filter(id_doc=nuevoFormato.id_doc.id )[0]
        registroActual.id_formato = formatoRelleno
        registroActual.save(using="docLaruex")
        return redirect('docLaruex:docLaruexVerTarea', id=registroActual.id_tarea_programada.id)
        agregarFormatoRellenoRegistroTarea(request, id_registro, id_formato_relleno)
    

'''-------------------------------------------
                                Módulo: actualizarFormato

- Descripción: 


- Precondiciones:


- Postcondiciones:

-------------------------------------------'''
@login_required
def actualizarFormato (request, id):
    # seleccionamos el objeto en la tabla Formatos   
    formato = Formatos.objects.using('docLaruex').filter(id_doc=id)[0]
    objeto = Objeto.objects.using('docLaruex').filter(id=id)[0]

    #indicamos el nuevo estado de editable
    if request.POST.get("editable"):
        formato.editable = request.POST.get("editable")
    
    print("Recibo", request.POST, request.FILES)
    if request.FILES.get("ficheroAdjuntoFormatoModificado"):

        # find file name matches with *
        filesOld2 = glob.glob(settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + str(objeto.id) + '_old2.*')
        if filesOld2:
            os.remove(filesOld2[0])

        filesOld = glob.glob(settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + str(objeto.id) + '_old.*')
        if filesOld:
            os.rename(filesOld[0], filesOld[0].replace('_old.', '_old2.'))


        ruta = settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + objeto.ruta
        ruta_old = settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + str(objeto.id) + '_old.' + objeto.ruta.split('.')[-1]
        if os.path.exists(ruta):
            os.rename(ruta, ruta_old)
        
        objeto.ruta = str(objeto.id) + '.' + request.FILES["ficheroAdjuntoFormatoModificado"].name.split('.')[-1]
        ruta = settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + str(objeto.id) + '.' + request.FILES["ficheroAdjuntoFormatoModificado"].name.split('.')[-1]
        subirDocumento(request.FILES["ficheroAdjuntoFormatoModificado"], ruta)

        # registrar id en la tabla HistoricoFormatosEditable
        creador = AuthUser.objects.using('docLaruex').filter(id=request.user.id)[0]
        historico = HistoricoFormatosEditable(id_formato=formato, creador=creador, fecha_edicion=datetime.now())
        objeto.save(using='docLaruex')
        historico.save(using='docLaruex')
    formato.save(using='docLaruex')
    return InfoVerObjeto(request, id)  

 
'''-------------------------------------------
                                Módulo: agregarCurriculum

- Descripción: 
s una vista que se encarga de crear un nuevo objeto de Curriculum en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar Curriculum.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar el curriculum.

- Postcondiciones:
Se crea un nuevo objeto de Curriculum en la tabla Curriculum de la base de datos.

-------------------------------------------'''
@login_required
def agregarCurriculum(request, nuevoObjeto):
    nuevoCurriculum = Curriculum(id=nuevoObjeto, id_usuario=UserCurriculum.objects.using("docLaruex").filter(id=request.POST.get("propietario")).get(),id_contacto=Contacto.objects.using("docLaruex").filter(id=request.POST.get("idContacto")).get())
    nuevoCurriculum.save(using='docLaruex')

 
'''-------------------------------------------
                                Módulo: verCurriculumUsuario

- Descripción: 
Este módulo permite ver la información de un curriculum específico en la base de datos y renderizar la plantilla correspondiente con la información obtenida.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
Se debe haber pasado como argumento el id del fabricante que se desea ver.

- Postcondiciones:

Se muestra la información del fabricante seleccionado en la plantilla correspondiente.

-------------------------------------------'''
@login_required
def verCurriculumUsuario(request):

    loginUser = request.user.id
    #habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    secretaria = esSecretaria(request.user.id)
    direccion = esDirector(request.user.id)
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    if Curriculum.objects.using("docLaruex").filter(id_usuario=loginUser):
        curriculumUsuarioActual = Curriculum.objects.using("docLaruex").filter(id_usuario=loginUser).get()
        if Curriculum.objects.using("docLaruex").filter(id_usuario=loginUser) or administrador:
            curriculum = Curriculum.objects.using("docLaruex").filter(id_usuario=loginUser).values('id','id_usuario__id', 'id_usuario__first_name', 'id_usuario__last_name', 'id_contacto__id','id_contacto__telefono','id_contacto__telefono_fijo','id_contacto__email','id_contacto__direccion','id_contacto__info_adicional','id_contacto__puesto', 'id_contacto__nombre','id_contacto__extension', 'id__id_habilitacion','id__tipo', 'id__nombre', 'id__tipo','id__ruta')[0]

            formaciones = FormacionCurriculum.objects.using("docLaruex").filter(id_curriculum=curriculumUsuarioActual).values('titulo','descripcion','horas','ruta','fecha_inicio','fecha_fin')
                    
            media= "/media/archivos"
            return render(
                request,
                "docLaruex/curriculum.html",
                {"itemsMenu": itemsMenu, "formaciones":list(formaciones), "curriculum": curriculum, "media":media, "administrador":administrador,"secretaria":secretaria, "direccion":direccion}
            )
        else:
            return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
        
    else:
        return noEncontrado(request)


'''-------------------------------------------
                                Módulo: descargarZipCurriculum

- Descripción: 

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.

- Postcondiciones:


-------------------------------------------'''
@login_required
def descargarZipCurriculum(request):
    # Crear un archivo zip
    id_usuario = request.user.id
    curriculum = Curriculum.objects.using("docLaruex").filter(id_usuario=id_usuario).values('id')[0]
    id_curriculum = str(curriculum['id'])

    # Ruta de la carpeta que quieres comprimir
    ruta_carpeta = settings.MEDIA_ROOT + 'archivos/Curriculum/' + id_curriculum

    # Nombre del archivo zip que se va a generar
    nombre_archivo = "formaciones"
    nombre_archivo_enviar = "formaciones_" + request.user.first_name
    shutil.make_archive(settings.MEDIA_ROOT + 'archivos/Curriculum/' +nombre_archivo, 'zip', ruta_carpeta)
    response = FileResponse(open(settings.MEDIA_ROOT + 'archivos/Curriculum/' +nombre_archivo+".zip", 'rb'))
    response['Content-Disposition'] = 'attachment;filename='+nombre_archivo_enviar+".zip"
        
    return response

'''-------------------------------------------
                                Módulo: agregarDocumento

- Descripción: 
s una vista que se encarga de crear un nuevo objeto de Documento en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar Documento.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar al documento.

- Postcondiciones:
Se crea un nuevo objeto de tipo Documento en la tabla Documentos de la base de datos.

-------------------------------------------'''
@login_required
def agregarDocumento(request, nuevoObjeto):
    if request.POST.get("tipoDocumento") is not None:
        tipoDocumento=TipoDocumentos.objects.using("docLaruex").filter(id=request.POST.get("tipoDocumento")).get()
    else:
        tipoDocumento = TipoDocumentos.objects.using("docLaruex").filter(id=99).get()

    # si no hay fecha de actualización obtener fecha actual
    if(request.POST.get("fechaActualizacion") == '' or request.POST.get("fechaActualizacion") == None):

        fechaActualizacion = datetime.now();
    else:
        fechaActualizacion = request.POST.get("fechaActualizacion");
    
    if request.POST.get("versionDocumento") is not None:
        nuevoDocumento = Documento(id_doc=nuevoObjeto, editable=request.POST.get(
        "editable"), fecha_actualizacion=fechaActualizacion, num_modificaciones="0", tipo_documento=tipoDocumento, version=request.POST.get("versionDocumento"))
        nuevoDocumento.save(using='docLaruex')
    
    else:
        nuevoDocumento = Documento(id_doc=nuevoObjeto, editable=request.POST.get(
        "editable"), fecha_actualizacion=fechaActualizacion, num_modificaciones="0", tipo_documento=tipoDocumento)
        nuevoDocumento.save(using='docLaruex')
    
    
    if request.POST.get("padre") is not None:
        objetoAsociado = ObjetoRelacionado.objects.using('docLaruex').filter(id=request.POST.get("padre"))[0]
        RelacionDocumentaciones.objects.using("docLaruex").create(id_doc=nuevoObjeto, id_relacionado=objetoAsociado)

        

'''-------------------------------------------
                                Módulo: agregarDocumento

- Descripción: 
s una vista que se encarga de crear un nuevo objeto de Ubicación en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar una Ubicación.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar a la ubicación.

- Postcondiciones:
Se crea un nuevo objeto de tipo Ubicación en la tabla Ubicaciones de la base de datos.

-------------------------------------------'''
@login_required
def agregarUbicacion(request, nuevoObjeto):
    
    nuevaUbicacion = Ubicaciones(id=nuevoObjeto, latitud=request.POST.get(
        "latitud"), longitud=request.POST.get(
        "longitud"), tipo_ubicacion=TipoUbicacion.objects.using("docLaruex").filter(id=request.POST.get("tipo_ubicacion")).get(), alias=request.POST.get(
        "alias"))
    nuevaUbicacion.save(using='docLaruex')

'''-------------------------------------------
                                Módulo: agregarEquipo

- Descripción: 
Es una vista que se encarga de crear un nuevo objeto de Equipo en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar una Equipo.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar el Equipo.

- Postcondiciones:
Se crea un nuevo objeto de tipo Equipo en la tabla Equipos de la base de datos.

-------------------------------------------'''
@login_required
def agregarEquipo(request, nuevoObjeto):
        
    if (Equipo.objects.using('docLaruex').filter(cod_uex=request.POST.get("cod_uex")).exists() and request.POST.get("cod_uex") is not None and int(request.POST.get("cod_uex")) != 0) or (Equipo.objects.using('docLaruex').filter(cod_laruex=request.POST.get("cod_laruex")).exists() and request.POST.get("cod_laruex") is not None and int(request.POST.get("cod_laruex")) != 0):
        print("Ya existe un equipo registrado con ese código")
    else:
        if request.POST.get("cod_spida"):
            cod_spida = request.POST.get("cod_spida")
        else:
            cod_spida = None

        if request.POST.get("propietario"):
            propietario = Propietarios.objects.using("docLaruex").filter(id=request.POST.get("propietario"))
        else:
            propietario = None

        if request.POST.get("proyecto"):
            proyecto=Proyecto.objects.using("docLaruex").filter(id=request.POST.get("proyecto"))
        else:
            proyecto=None
        
        grupo = GrupoEquipos.objects.using("docLaruex").filter(id=1)[0]        
        if request.POST.get("grupoEquipo"):
            grupo = GrupoEquipos.objects.using("docLaruex").filter(id=request.POST.get("grupoEquipo"))[0]

        altaUex = 0
        if 'altaUex' in request.POST:
            checkbox = request.POST['altaUex']
            if checkbox == "on":
                altaUex = 1
        
        proveedor=Proveedor.objects.using("docLaruex").filter(id=request.POST.get("proveedor"))[0]
        
        ubicacion = Ubicaciones.objects.using("docLaruex").filter(id=request.POST.get("ubicacion"))[0]

        nuevoEquipo = Equipo(id=nuevoObjeto, cod_laruex=request.POST.get("cod_laruex"), cod_uex=request.POST.get("cod_uex"), tipo_equipo=TipoEquipo.objects.using("docLaruex").filter(id=request.POST.get("tipo_equipo")).get(), fecha_alta=request.POST.get("fechaAlta"), fabricante=Fabricante.objects.using("docLaruex").filter(id=request.POST.get("fabricante")).get(), num_serie=request.POST.get("num_serie"), descripcion=request.POST.get("descripcion"), precio = request.POST.get("importe"), modelo= request.POST.get("modeloEquipo"), propietario=propietario, proyecto=proyecto,cod_spida=cod_spida, proveedor=proveedor, grupo=grupo, alta_uex=altaUex, ubicacion_actual=ubicacion)
        nuevoEquipo.save(using='docLaruex')

        try: 
            if request.FILES['imagenEquipo']:
                imagenAdjunta = "imagen"+ request.POST.get("tipoObjeto")
                rutaImagen = settings.MEDIA_ROOT + 'archivos/' + nuevoObjeto.tipo + '/' + str(nuevoObjeto.id) + '.' + request.FILES[imagenAdjunta].name.split('.')[-1]
            
                subirDocumento(request.FILES[imagenAdjunta], rutaImagen)
                nuevoObjeto.ruta = str(nuevoObjeto.id) + '.' + request.FILES[imagenAdjunta].name.split('.')[-1]
                nuevoObjeto.save(using='docLaruex')
        except:
            #cambiar
            print("Error al subir la foto del equipo")

        

        nuevoEquipoUbicado=RelUbicacionesEquipos(id_equipo=nuevoEquipo, id_ubicacion=Ubicaciones.objects.using("docLaruex").filter(id=request.POST.get("ubicacion")).get(), fecha=request.POST.get("fechaAlta"))  
        nuevoEquipoUbicado.save(using='docLaruex')
 




'''-------------------------------------------
                                Módulo: agregarProyecto

- Descripción: 
Es una vista que se encarga de crear un nuevo objeto de Proyectos en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar una Proyectos.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar el Proyecto.

- Postcondiciones:
Se crea un nuevo objeto de tipo Proyecto en la tabla Proyectos de la base de datos.

-------------------------------------------'''
@login_required
def agregarProyecto(request, nuevoObjeto):

    print("----- entro en proyecto----------")
    nuevoProyecto = Proyecto(id=nuevoObjeto, codigo=request.POST.get(
        "codigoProyecto"), fecha_inicio=request.POST.get(
        "fechaInicioProyecto"), fecha_fin=request.POST.get(
        "fechaFinProyecto"), presupuesto=request.POST.get("presupuestoProyecto"), objetivo=request.POST.get(
        "objetivoProyecto"))
    nuevoProyecto.save(using='docLaruex')

    for colaborador in request.POST.getlist("colaboradoresProyecto"):

        nuevoColaborador = RelProyectoColaboradores(id_proyecto=nuevoProyecto, id_colaborador=Entidades.objects.using("docLaruex").filter(id=colaborador).get())
        nuevoColaborador.save(using='docLaruex')
    
    for financiador in request.POST.getlist("financiadoresProyecto"):

        nuevoFinanciador = RelProyectoFinanciadores(id_proyecto=nuevoProyecto, id_financiador=EntidadesFinanciadoras.objects.using("docLaruex").filter(id=financiador).get())
        nuevoFinanciador.save(using='docLaruex')



'''-------------------------------------------
                                Módulo: agregarCurso

- Descripción: 
Es una vista que se encarga de crear un nuevo objeto de Curso en la base de datos. La vista está protegida por el decorador "@login_required", lo que significa que solo los usuarios autenticados pueden acceder a ella.

- Precondiciones:
El usuario debe estar autenticado para poder acceder a la vista de agregar una Cursos.
La solicitud debe tener una variable llamada "nuevoObjeto" que corresponde al ID del objeto al que se le va a agregar el Cursos.

- Postcondiciones:
Se crea un nuevo objeto de tipo Curso en la tabla Cursos de la base de datos.

-------------------------------------------'''
@login_required
def agregarCurso(request, nuevoObjeto):
    patrocinador=Entidades.objects.using("docLaruex").filter(id=request.POST.get("patrocinador")).get()
    tipoCurso=TipoCurso.objects.using("docLaruex").filter(id=request.POST.get("tipoCurso")).get()
    imagenCurso = "imagen"+ request.POST.get("tipoObjeto")
    
    rutaImagen = 'static/niceAdminAssets/img/' + nuevoObjeto.tipo + '/' + str(nuevoObjeto.id) + '.' + request.FILES[imagenCurso].name.split('.')[-1]
    imagen = str(nuevoObjeto.id) + '.' + request.FILES[imagenCurso].name.split('.')[-1]


    subirDocumento(request.FILES[imagenCurso], rutaImagen)

    nuevoCurso = Cursos(id=nuevoObjeto, fecha_inicio=request.POST.get(
        "fechaInicioCurso"), fecha_fin=request.POST.get(
        "fechaFinCurso"), resumen=request.POST.get(
        "resumenCurso"), descripcion=request.POST.get(
        "descripcionCurso"),tipo_curso=tipoCurso,horas=request.POST.get(
        "horas"), imagen=imagen, patrocinadores=patrocinador)
    nuevoCurso.save(using='docLaruex')
    

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


'''-------------------------------------------
                                Módulo: datosCalendario

- Descripción: 
Proporciona información de las tareas programadas en la vista de calendario

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Devuelve una lista con los eventos que se van a mostrar en el calendario

-------------------------------------------'''
@login_required
def datosCalendario(request):


    tareas = TareasProgramadas.objects.using('docLaruex').values('id','id_evento__nombre','fecha_proximo_mantenimiento','id_evento__tipo_evento__color')
    # creo una lista vacía para guardar los datos de los festivos
    salida = []

    # recorro los festivos y los guardo en la lista
    for tarea in tareas:
        # inserto los datos en la lista siguiendo la estructura que requiere el calendario
        fechaFormateada = tarea['fecha_proximo_mantenimiento'].strftime("%Y-%m-%d")
        salida.append({
            'id':tarea['id'],
            'title':tarea['id_evento__nombre'],
            'start':fechaFormateada,
            'color':'#ffffff',
            'borderColor': tarea['id_evento__tipo_evento__color'],
            'textColor': tarea['id_evento__tipo_evento__color']            
        })

    # devuelvo la lista en formato json
    return JsonResponse(salida, safe=False)                

'''-------------------------------------------
                                Módulo: calendario

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def calendario(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    return render(request, "docLaruex/calendario.html",{"itemsMenu":itemsMenu})




'''-------------------------------------------
                                Módulo: consultarArchivo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def consultarArchivo(request, id):
    objeto = Objeto.objects.using('docLaruex').filter(id=id)[0]
    ruta = settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + objeto.ruta
    # compruebo si la ruta devuelve algo 
    if os.path.exists(ruta):
        return FileResponse(open(ruta, 'rb'))
    else:
        return JsonResponse({'status': 'error', 'message': 'El archivo no esta disponible, compruebe que la ruta y el archivo tengan la misma extensión'})



'''-------------------------------------------
                                Módulo: consultarArchivoEditable

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def consultarArchivoEditable(request, id):
    objeto = Objeto.objects.using('docLaruex').filter(id=id)[0]
    ruta = settings.MEDIA_ROOT + 'archivos/' + objeto.tipo + '/' + objeto.ruta_editable
    return FileResponse(open(ruta, 'rb'))


register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    return value.replace(arg, '')

'''
############## Carga la vista de todas las Ubicaciones ¿¿¿¿ BORRAR ??? ##############
@login_required
def ListadoUbicaciones(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    responsables = Responsables.objects.using(
        "docLaruex").values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").values(
        'id', 'titulo')
    tipoUbicacionesExistentes = TipoUbicacion.objects.using(
        "docLaruex").values('id', 'nombre')
    ubicacionesExistentes = Ubicaciones.objects.using(
        "docLaruex").values('id', 'id__nombre', 'id__padre')
    return render(request, 'docLaruex/ListaUbicaciones.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicacionesExistentes": list(ubicacionesExistentes), "administrador": esAdministrador(request.user.id), "habilitaciones": list(habilitaciones), "tipoUbicacionesExistentes": list(tipoUbicacionesExistentes)})
'''


'''-------------------------------------------
                                Módulo: DatosUbicaciones

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosUbicaciones(request):
    ubicaciones = Ubicaciones.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('-id').values('id', 'id__padre','id__padre__nombre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_ubicacion__nombre', 'latitud', 'id__creador', 'id__id_estado', 'longitud', 'id__icono')
    return JsonResponse(list(ubicaciones), safe=False)

'''-------------------------------------------
                                Módulo: ListadoUbicacionesSonPadre

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ListadoUbicacionesSonPadre(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    tipoUbicacionesExistentes = TipoUbicacion.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
    ubicacionesExistentes = Ubicaciones.objects.using(
        "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'id__padre')
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador: 
        return render(request, 'docLaruex/ListaUbicacionesPadre.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicacionesExistentes": list(ubicacionesExistentes),"administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario), "habilitaciones": list(habilitaciones), "tipoUbicacionesExistentes": list(tipoUbicacionesExistentes)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})



'''-------------------------------------------
                                Módulo: DatosUbicacionesSonPadre

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosUbicacionesSonPadre(request):
    ubicaciones = Ubicaciones.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id__padre__isnull=True).order_by('-id__padre').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_ubicacion__nombre', 'latitud', 'id__creador', 'id__id_estado__nombre', 'id__id_estado', 'longitud', 'id__icono')  

    ubicacionesExistentes = []
    salida = []
    for u in ubicaciones:
        if not u["id"] in ubicaciones:
            salida.append(u)
            ubicacionesExistentes.append(u["id"])
    
    return JsonResponse(list(salida), safe=False)

'''-------------------------------------------
                                Módulo: DatosUbicacionesPadre

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosUbicacionesPadre(request,id):
    ubicaciones = Ubicaciones.objects.using('docLaruex').order_by('-id__padre').filter(id__padre=id).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_ubicacion__nombre', 'latitud', 'id__creador', 'id__id_estado', 'id__id_estado__nombre', 'longitud', 'id__icono')  

    ubicacionesExistentes = []
    salida = []
    for u in ubicaciones:
        if not u["id"] in ubicaciones:
            salida.append(u)
            ubicacionesExistentes.append(u["id"])
    
    return JsonResponse(list(salida), safe=False)

from django.db.models import Exists, OuterRef, Q


'''-------------------------------------------
                                Módulo: EquiposAsociados

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def EquiposAsociados(request, id):

    equipos = Equipo.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id), ubicacion_actual__id=id).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__icono', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'fabricante__nombre', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio','modelo', 'ubicacion_actual', 'ubicacion_actual__id__nombre')  

    '''
    ultimaUbicacion = RelUbicacionesEquipos.objects.using('docLaruex').filter(
        ~Exists(RelUbicacionesEquipos.objects.using('docLaruex').filter(
            Q(fecha__gt=OuterRef('fecha')) | Q(fecha=OuterRef('fecha'), pk__lt=OuterRef('pk')),
        id_equipo=OuterRef('id_equipo')
        ))
    )

    equiposAsociados = ultimaUbicacion.filter(id_ubicacion=id, id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values(
        'id_equipo','id_equipo__id', 'id_equipo__id__nombre', 'id_equipo__cod_laruex', 'id_equipo__id__ruta','id_equipo__id__fecha_subida','id_equipo__id__tipo','id_equipo__tipo_equipo__nombre','id_equipo__id__creador','id_equipo__id__id_estado__nombre','id_equipo__tipo_equipo__nombre','id_equipo__cod_uex','id_equipo__id__icono','id_equipo__fabricante', 'id_equipo__num_serie', 'id_equipo__descripcion', 'id_equipo__fecha_alta', 'id_equipo__fecha_baja', 'id_equipo__precio')
    equiposExistentes = []
    salida = []
    for e in equiposAsociados:
        if not e["id_equipo"] in equiposExistentes:
            salida.append(e)
            equiposExistentes.append(e["id_equipo"])
    '''
    return JsonResponse(list(equipos), safe=False)


'''-------------------------------------------
                                Módulo: EquiposAsociados

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DocumentosAsociados(request, id):
    documentoAsociado = RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=id).values(
        'id_relacionado', 'id_relacionado__icono','id_relacionado__nombre', 'id_relacionado__tipo', 'id_relacionado__creador__last_name', 'id_relacionado__creador__first_name', 'id_relacionado__fecha_subida', 'id_relacionado__id_estado__nombre')
    salida = list(documentoAsociado)
    return JsonResponse(salida, safe=False)



'''
############## Carga la vista de todos los Equipos ¿¿¿ BORRAR ???##############
@login_required
def ListadoEquipos(request):
    #genera un código_laruex consecutivo
    # por el momento busca en un rango, para localizar el último valor
    # pues para agilizar la gestión se igualaron alguno cod_uex con cod_laruex
    ultimoCodigoLaruex = Equipo.objects.using("docLaruex").filter(cod_laruex__range =[847,2000]).order_by('-cod_laruex').values('cod_laruex')[0]
    ultimoCodigo=ultimoCodigoLaruex['cod_laruex'] + 1

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    responsables = Responsables.objects.using(
        "docLaruex").values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").values(
        'id', 'titulo')
    fabricantes = Fabricante.objects.using(
        "docLaruex").values('id', 'nombre')
    proveedores = Proveedor.objects.using(
        "docLaruex").values('id', 'nombre')
    tipoEquipoExistentes = TipoEquipo.objects.using(
    "docLaruex").values('id', 'nombre')
    equiposExistentes = Equipo.objects.using(
        "docLaruex").values('id')
    
    equipos = Equipo.objects.using(
        "docLaruex").values('id', 'cod_laruex')
    ubicaciones = Ubicaciones.objects.using(
    "docLaruex").values('id', 'id__nombre', 'latitud', 'longitud')

    return render(request, 'docLaruex/ListaEquipos.html', {"ultimoCodigo": ultimoCodigo,"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicaciones": list(ubicaciones), "habilitaciones": list(habilitaciones), "fabricantes": list(fabricantes),"proveedores": list(proveedores), "tipoEquipo": list(tipoEquipoExistentes),"equiposExistentes":list(equiposExistentes),"administrador": esAdministrador(request.user.id), "equipos":list(equipos)})

'''

'''-------------------------------------------
                                Módulo: DatosEquipos

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquipos(request):
    equipos = Equipo.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'fabricante__nombre', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio','modelo', 'ubicacion_actual', 'ubicacion_actual__id__nombre')                         
    
    return JsonResponse(list(equipos), safe=False)


'''-------------------------------------------
                                Módulo: DatosEquiposSinEtiqueta

- Descripción: 
Devuelve el listado de equipos que aún no tienen etiqueta de la uex asignada desde el año 2021. 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Devuelve el listado de equipos. 

-------------------------------------------'''
@login_required
def DatosEquiposSinEtiqueta(request):
    fecha_limite = datetime(2021, 1, 1)
    equipos = Equipo.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id), cod_uex=0, fecha_alta__gt=fecha_limite, fecha_baja=None, alta_uex=1).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'fabricante__nombre', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio','modelo', 'ubicacion_actual', 'ubicacion_actual__id__nombre')                         
    
    return JsonResponse(list(equipos), safe=False)



'''-------------------------------------------
                                Módulo: ListadoEquiposBaja

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ListadoEquiposBaja(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id) 
    secretaria = esSecretaria(request.user.id)

    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    fabricantes = Fabricante.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
    tipoEquipoExistentes = TipoEquipo.objects.using(
    "docLaruex").order_by('nombre').values('id', 'nombre')
    equiposExistentes = Equipo.objects.using(
        "docLaruex").values('id')
    ubicaciones = Ubicaciones.objects.using(
    "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'latitud', 'longitud', 'id__padre', 'id__padre__nombre')

    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador or secretaria or direccion:

        return render(request, 'docLaruex/ListaEquiposBaja.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicaciones": list(ubicaciones), "habilitaciones": list(habilitaciones), "fabricantes": list(fabricantes), "tipoEquipo": list(tipoEquipoExistentes),"administrador": administrador, "secretaria":secretaria, "direccion":direccion,"habilitacionesUsuario":list(habilitacionesUsuario),"equiposExistentes":list(equiposExistentes)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

'''-------------------------------------------
                                Módulo: ListadoEquiposTipo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ListadoEquiposTipo(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id) 
    secretaria = esSecretaria(request.user.id)

    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    fabricantes = Fabricante.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
    tipoEquipoExistentes = TipoEquipo.objects.using(
    "docLaruex").order_by('nombre').values('id', 'nombre')
    equiposExistentes = Equipo.objects.using(
        "docLaruex").values('id')
    ubicaciones = Ubicaciones.objects.using(
    "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'latitud', 'longitud', 'id__padre', 'id__padre__nombre')
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador or secretaria or direccion:
        return render(request, 'docLaruex/ListaEquiposTipo.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicaciones": list(ubicaciones), "habilitaciones": list(habilitaciones), "fabricantes": list(fabricantes), "tipoEquipoExistentes": list(tipoEquipoExistentes),"administrador": administrador, "secretaria":secretaria, "direccion":direccion,"habilitacionesUsuario":list(habilitacionesUsuario),"equiposExistentes":list(equiposExistentes)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: ListadoEquiposGrupo

- Descripción: 
    Muestra un listado de los equipos que pertenecen a un grupo

- Precondiciones:
    El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ListadoEquiposGrupo(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id) 
    secretaria = esSecretaria(request.user.id)

    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    fabricantes = Fabricante.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
    tipoEquipoExistentes = TipoEquipo.objects.using(
    "docLaruex").order_by('nombre').values('id', 'nombre')
    grupoEquipos = GrupoEquipos.objects.using(
    "docLaruex").order_by('nombre').values('id', 'nombre')
    equiposExistentes = Equipo.objects.using("docLaruex").values('id')
    ubicaciones = Ubicaciones.objects.using(
    "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'latitud', 'longitud', 'id__padre', 'id__padre__nombre')
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador or secretaria or direccion:
        return render(request, 'docLaruex/ListaEquiposGrupo.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicaciones": list(ubicaciones), "habilitaciones": list(habilitaciones), "fabricantes": list(fabricantes), "tipoEquipoExistentes": list(tipoEquipoExistentes),"administrador": administrador, "secretaria":secretaria, "direccion":direccion,"habilitacionesUsuario":list(habilitacionesUsuario),"equiposExistentes":list(equiposExistentes), "grupoEquipos": list(grupoEquipos)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})
    


'''-------------------------------------------
                                Módulo: ListadoEquiposCedidos

- Descripción: 
    Muestra un listado de los equipos que no son del laruex

- Precondiciones:
    El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ListadoEquiposCedidos(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)
    direccion = esDirector(request.user.id) 
    secretaria = esSecretaria(request.user.id)

    responsables = Responsables.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    fabricantes = Fabricante.objects.using(
        "docLaruex").order_by('nombre').values('id', 'nombre')
    tipoEquipoExistentes = TipoEquipo.objects.using(
    "docLaruex").order_by('nombre').values('id', 'nombre')
    grupoEquipos = GrupoEquipos.objects.using(
    "docLaruex").order_by('nombre').values('id', 'nombre')
    equiposExistentes = Equipo.objects.using("docLaruex").values('id')
    ubicaciones = Ubicaciones.objects.using(
    "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'latitud', 'longitud', 'id__padre', 'id__padre__nombre')
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador or secretaria or direccion:
        return render(request, 'docLaruex/ListaEquiposCedidos.html', {"itemsMenu": itemsMenu, "responsables": list(responsables), "ubicaciones": list(ubicaciones), "habilitaciones": list(habilitaciones), "fabricantes": list(fabricantes), "tipoEquipoExistentes": list(tipoEquipoExistentes),"administrador": administrador, "secretaria":secretaria, "direccion":direccion,"habilitacionesUsuario":list(habilitacionesUsuario),"equiposExistentes":list(equiposExistentes), "grupoEquipos": list(grupoEquipos)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

'''-------------------------------------------
                                Módulo: ListadoStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def listadoStock(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    administrador = esAdministrador(request.user.id)
    
    responsableAlmacen = comprobarResponsableAlmacen(comprobarHabilitacionesTitulo(request.user.id))

    unidades = UnidadesStock.objects.using("docLaruex").order_by('nombre').values('id', 'nombre')
    empleados = AuthUser.objects.using("docLaruex").order_by('first_name').values('id', 'first_name','last_name')
    categorias = CategoriasStock.objects.using("docLaruex").order_by('categoria').values('id', 'categoria')
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')
    itemsAlmacenes = Stock.objects.using(
        "docLaruex").values('id','item','descripcion','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','cantidad', 'min_cantidad', 'categoria', 'categoria__id')
    proveedores = Proveedor.objects.using("docLaruex").order_by('nombre').values('id', 'nombre')
    
    if responsableAlmacen or administrador:    
        return render(request, 'docLaruex/listadoStock.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": list(itemsAlmacenes), "ubicaciones": list(ubicaciones), "unidades": list(unidades), "empleados": list(empleados), "categorias": list(categorias),"administrador": administrador, "proveedores":list(proveedores)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: stockTotal

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def stockTotal(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()   
    administrador = esAdministrador(request.user.id)   
    responsableAlmacen = comprobarResponsableAlmacen(comprobarHabilitacionesTitulo(request.user.id))

    empleados = AuthUser.objects.using("docLaruex").values('id', 'first_name','last_name')
    categorias = CategoriasStock.objects.using("docLaruex").order_by('categoria').values('id', 'categoria')
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')

    if responsableAlmacen or administrador:
        return render(
            request,
            "docLaruex/stockTotal.html",
            {"itemsMenu": itemsMenu, "administrador":administrador, "ubicaciones":list(ubicaciones), "categorias":list(categorias), "empleados":list(empleados)}
        )
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: stockDatosCategoria

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def stockDatosCategoria(request, idCategoria):
    itemsStockCategoria = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), categoria__id=idCategoria).values('id','item','descripcion','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria__categoria')
    
    return JsonResponse(list(itemsStockCategoria), safe=False)

'''-------------------------------------------
                                Módulo: DatosListadoStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosListadoStock(request):  

    itemsAlmacenes = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id)).values('id','item','descripcion','num_estanteria','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria__categoria')
    return JsonResponse(list(itemsAlmacenes), safe=False)





'''-------------------------------------------
                                Módulo: listadoStockAlmacen

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def listadoStockAlmacen(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    unidades = UnidadesStock.objects.using("docLaruex").order_by('nombre').values('id', 'nombre')
    empleados = AuthUser.objects.using("docLaruex").order_by('first_name').values('id', 'first_name','last_name')
    categorias = CategoriasStock.objects.using("docLaruex").order_by('categoria').values('id', 'categoria')
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id','latitud', 'longitud','tipo_ubicacion')
    itemsAlmacenes = Stock.objects.using("docLaruex").values('id','item','descripcion','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','cantidad', 'min_cantidad', 'categoria', 'categoria__id')
     
    return render(request, 'docLaruex/listadoStockAlmacen.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": list(itemsAlmacenes), "ubicaciones": list(ubicaciones), "unidades": list(unidades), "empleados": list(empleados), "categorias": list(categorias),"administrador": esAdministrador(request.user.id)})

    
'''-------------------------------------------
                                Módulo: DatosStockAlmacen

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosStockAlmacen(request, id):
    itemsAlmacenes = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), id_ubicacion__id=id).values('id','item','descripcion','num_contenedor','num_estanteria','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria__categoria')
    
    
    return JsonResponse(list(itemsAlmacenes), safe=False)


'''-------------------------------------------
                                Módulo: DatosStckUbicacion

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosStockUbicacion(request, id_ubicacion):
    itemsAlmacenes = Stock.objects.using(
    "docLaruex").filter(id_ubicacion__id=id_ubicacion).values('id','item','descripcion','num_contenedor','num_estanteria','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria__categoria')
    itemsUbicacion = RegistroRetiradaStock.objects.using(
    "docLaruex").filter(ubicacion__id__id=id_ubicacion).values('id','item','item__descripcion','item__num_contenedor','item__num_estanteria','ubicacion_id','ubicacion_id__id__nombre','ubicacion_id__id','item__unidad__nombre','item__cantidad', 'item__min_cantidad', 'item__categoria__categoria')
    stockTotal = list(itemsAlmacenes) + list(itemsUbicacion)

    
    return JsonResponse(list(stockTotal), safe=False)
'''-------------------------------------------
                                Módulo: ListadoStockMinimo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def listadoStockMinimo(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')
    itemsAlmacenes = Stock.objects.using(
        "docLaruex").values('id','item','descripcion','num_contenedor','num_estanteria', 'id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','cantidad', 'min_cantidad', 'categoria', 'categoria__id')
    
    return render(request, 'docLaruex/listadoStockMinimo.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": list(itemsAlmacenes), "ubicaciones": list(ubicaciones),"administrador": esAdministrador(request.user.id)})

'''-------------------------------------------
                                Módulo: DatosListadoStockMinimo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosListadoStockMinimo(request):
    itemsAlmacenes = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), cantidad__exact=F('min_cantidad')).values('id','item','descripcion','num_contenedor','num_estanteria','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria__categoria')
    return JsonResponse(list(itemsAlmacenes), safe=False)

'''-------------------------------------------
                                Módulo: ListadoFueraStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def listadoFueraStock(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')
    itemsAlmacenes = Stock.objects.using(
        "docLaruex").values('id','item','descripcion','num_contenedor','num_estanteria','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','cantidad', 'min_cantidad', 'categoria', 'categoria__id')
    
    return render(request, 'docLaruex/listadoFueraStock.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": list(itemsAlmacenes), "ubicaciones": list(ubicaciones),"administrador": esAdministrador(request.user.id)})

'''-------------------------------------------
                                Módulo: DatosListadoFueraStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosListadoFueraStock(request):
    itemsAlmacenes = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), cantidad__lt=F('min_cantidad')).values('id','item','descripcion','num_contenedor','num_estanteria','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria__categoria','urgente')
    return JsonResponse(list(itemsAlmacenes), safe=False)


'''-------------------------------------------
                                Módulo: hojaPedidoStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def hojaPedidoStock(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    administrador = esAdministrador(request.user.id)
    responsableAlmacen = comprobarResponsableAlmacen(comprobarHabilitacionesTitulo(request.user.id))

    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')
    
    itemsAlmacenes = list(Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), cantidad__lt=F('min_cantidad')).values('id','item','descripcion','num_estanteria','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria', 'categoria__id'))
    
    for item in itemsAlmacenes:
        item["min_cantidad"] = item["min_cantidad"] - item["cantidad"]

    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values('id', 'titulo')
    if administrador or responsableAlmacen:
        return render(request, 'docLaruex/hojaPedidoStock.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": itemsAlmacenes, "ubicaciones": list(ubicaciones),"administrador": administrador, "habilitaciones":habilitaciones})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: hojaPedidoStockAlmacen

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''   
@login_required
def hojaPedidoStockAlmacen(request,id_almacen):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    responsableAlmacen = comprobarResponsableAlmacen(comprobarHabilitacionesTitulo(request.user.id))
    administrador = esAdministrador(request.user.id)

    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')
    ubicacionActual = Ubicaciones.objects.using("docLaruex").filter(id=id_almacen).values('id__nombre')[0]

    itemsAlmacenes = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), id_ubicacion=id_almacen, cantidad__lt=F('min_cantidad')).values('id','item','descripcion','num_estanteria','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria', 'categoria__id')

    if responsableAlmacen or administrador:
        return render(request, 'docLaruex/hojaPedidoStock.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": list(itemsAlmacenes), "ubicaciones": list(ubicaciones),"administrador": administrador, "id_almacen":id_almacen, "ubicacionActual":ubicacionActual})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: hojaPedidoStockCategoria

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''   
@login_required
def hojaPedidoStockCategoria(request,id_categoria):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    responsableAlmacen = comprobarResponsableAlmacen(comprobarHabilitacionesTitulo(request.user.id)) 
    administrador = esAdministrador(request.user.id)

    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','tipo_ubicacion', 'id__nombre', 'id__padre', 'id__padre__nombre', 'tipo_ubicacion__id')
    categoriaActual = CategoriasStock.objects.using("docLaruex").filter(id=id_categoria).values('categoria')[0]

    itemsAlmacenes = Stock.objects.using(
        "docLaruex").filter(id_ubicacion__id__nombre__in=comprobarHabilitacionesTitulo(request.user.id), categoria=id_categoria, cantidad__lt=F('min_cantidad')).values('id','item','descripcion','num_estanteria','num_contenedor','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria', 'categoria__id')


    if responsableAlmacen or administrador:
        return render(request, 'docLaruex/hojaPedidoStock.html', {"itemsMenu": itemsMenu, "itemsAlmacenes": list(itemsAlmacenes), "ubicaciones": list(ubicaciones),"administrador": administrador, "id_categoria":id_categoria, "categoriaActual":categoriaActual})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})

'''-------------------------------------------
                                Módulo: verItemStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''   
@login_required
def verItemStock (request, id):    
    empleados = AuthUser.objects.using("docLaruex").order_by('first_name').values('id','first_name','last_name')
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    categorias = CategoriasStock.objects.using("docLaruex").order_by('categoria').values('id','categoria')
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('id__padre').values('id','id__nombre', 'id__padre','id__padre__nombre')
    unidades = UnidadesStock.objects.using("docLaruex").order_by('nombre').values('id','nombre')

    labels =[]
    datas = []
    fechas = []

    datos = RelStockProveedores.objects.using("docLaruex").filter(item=id).values('proveedor__nombre', 'coste', 'cantidad', 'unidad__nombre', 'fecha')
    for dato in datos:
        labels.append(dato["proveedor__nombre"])
        datas.append("Precio: " + str(dato["coste"]) +" \n"+ "Cantidad: " + str(dato["cantidad"]) + " \n"+ "Formato: " + str(dato["unidad__nombre"]))
        fechas.append(dato["fecha"])


    itemStock = Stock.objects.using("docLaruex").filter(id=id).values('id','item','descripcion','num_contenedor','num_estanteria','id_ubicacion','id_ubicacion__id__nombre','id_ubicacion__id','unidad__id','unidad__nombre','cantidad', 'min_cantidad', 'categoria','categoria__categoria','avisado','urgente').first()
    infoProveedor = RelStockProveedores.objects.using("docLaruex").filter(item=id).values('id','fecha','coste','proveedor','proveedor__id','proveedor__nombre', 'proveedor__telefono','cantidad','unidad')
    proveedores = Proveedor.objects.using("docLaruex").order_by('nombre').values('id','nombre')
    ultimoProveedor = RelStockProveedores.objects.using("docLaruex").filter(item=id).order_by('-fecha').values('id','fecha','coste','proveedor','proveedor__id','proveedor__nombre', 'proveedor__telefono','cantidad','unidad').first()
    

    habilitacionesUsuario = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=request.user.id).values('id','tipo','fecha','id_habilitacion','id_habilitacion__id', 'id_habilitacion__titulo')

    administrador = esAdministrador(request.user.id)
    return render(request, 'docLaruex/itemStock.html', {"itemsMenu": itemsMenu, "unidades":list(unidades),"categorias":list(categorias),"ubicaciones":list(ubicaciones), "itemStock": itemStock, "administrador": administrador, "habilitacionesUsuario": list(habilitacionesUsuario), "infoProveedor":list(infoProveedor),"ultimoProveedor":ultimoProveedor, "fechas":fechas, "empleados":list(empleados), "proveedores":list(proveedores), "labels":labels, "datas": datas, "datos":list(datos)})


'''-------------------------------------------
                                Módulo: agregarStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def agregarStock(request):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    estanteria = request.POST.get("estanteria")
    contenedor = request.POST.get("contenedor")
    cantidad = request.POST.get("cantidad")
    unidad = UnidadesStock.objects.using('docLaruex').get(id=request.POST.get("unidad"))

    nuevoStock = Stock(item=request.POST.get("item"), descripcion=request.POST.get("descripcionItem"), num_contenedor=contenedor, num_estanteria=estanteria, id_ubicacion=Ubicaciones.objects.using('docLaruex').get(id=request.POST['ubicacion']), unidad=unidad, cantidad =cantidad, min_cantidad=request.POST.get("minCantidad"), categoria=CategoriasStock.objects.using('docLaruex').get(id=request.POST.get("categoria")), urgente=request.POST.get("urgente"))
    nuevoStock.save(using='docLaruex')

    if request.POST.get("informacionProveedor") == "1":
        nuevoProveedor = RelStockProveedores(item=nuevoStock, fecha=request.POST.get("fechaCompraProveedor"), coste=request.POST.get("costeProveedor"), proveedor=Proveedor.objects.using('docLaruex').get(id=request.POST.get("proveedor")), cantidad=cantidad, unidad=unidad)
        nuevoProveedor.save(using='docLaruex')
    return listadoStock(request)

'''-------------------------------------------
                                Módulo: retirarStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def retirarStock (request, item):  
    error = None
    objetoItem = Stock.objects.using("docLaruex").filter(id=item).get()
    objetoEmpleado = AuthUser.objects.using("docLaruex").filter(id=request.POST['empleadoQueRetira']).get()
    RegistroRetiradaStock.objects.using(
        "docLaruex").filter(item=item).values('id','cantidad','fecha','empleado', 'empleado__id', 'empleado__first_name','empleado__last_name','error')
    if 'error' in request.POST:
        error = request.POST['error']
        if error == "on":
            error = 1

    nuevaRetiradaStock = RegistroRetiradaStock(item=objetoItem, fecha=request.POST['fechaRetirada'], cantidad=request.POST['cantidadRetirada'], empleado=objetoEmpleado, error=error)
    nuevaRetiradaStock.save(using='docLaruex')

    #acualizamos el stock del item    
    stock = Stock.objects.using('docLaruex').filter(id=item)[0]

    stock.cantidad -= float(request.POST['cantidadRetirada'])
    stock.save(using="docLaruex")

    return redirect('docLaruex:docLaruexVerItemStock', id=item)
 


'''-------------------------------------------
                                Módulo: retirarStockUbicacion

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def retirarStockUbicacion (request, item):    
    objetoItem = Stock.objects.using("docLaruex").filter(id=item).get()
    objetoEmpleado = AuthUser.objects.using("docLaruex").filter(id=request.POST['empleadoQueRetira']).get()
    RegistroRetiradaStock.objects.using(
        "docLaruex").filter(item=item).values('id','cantidad','fecha','empleado', 'empleado__id', 'empleado__first_name','empleado__last_name')
    nuevaRetiradaStock = RegistroRetiradaStock(item=objetoItem, fecha=request.POST['fechaRetirada'], cantidad=request.POST['cantidadRetirada'], empleado=objetoEmpleado, ubicacion=Ubicaciones.objects.using("docLaruex").filter(id=request.POST['nuevaUbicacion']).get())
    nuevaRetiradaStock.save(using='docLaruex')

    #acualizamos el stock del item    
    stock = Stock.objects.using('docLaruex').filter(id=item)[0]

    stock.cantidad -= float(request.POST['cantidadRetirada'])
    stock.save(using="docLaruex")


    return redirect('docLaruex:docLaruexVerItemStock', id=item)


'''-------------------------------------------
                                Módulo: agregarUnidadesStockagregarUnidadesStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def agregarUnidadesStock (request, item):
    stock = Stock.objects.using('docLaruex').filter(id=item)[0]

    stock.cantidad += float(request.POST['cantidadAgregada'])
    stock.save(using="docLaruex")

    return HttpResponseRedirect('/private/docLaruex/verItemStock/'+item+'/')

'''-------------------------------------------
                                Módulo: agregarUnidadesStockProveedor

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def agregarUnidadesStockProveedor (request, item):
    stock = Stock.objects.using('docLaruex').filter(id=item)[0]
    stock.cantidad += float(request.POST['cantidadAgregadaProveedor'])
    stock.save(using="docLaruex")
    
    nuevoProveedor =  RelStockProveedores(item=stock, fecha=request.POST.get("fechaAgregarStockProveedor"), coste=request.POST.get("costeAgregarStockProveedor"), proveedor=Proveedor.objects.using('docLaruex').get(id=request.POST.get("proveedorAgregarStock")), cantidad=request.POST['cantidadAgregadaProveedor'], unidad=stock.unidad)
    nuevoProveedor.save(using='docLaruex')

    return HttpResponseRedirect('/private/docLaruex/verItemStock/'+item+'/')

'''-------------------------------------------
                                Módulo: DatosRetiradasStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosRetiradasStock(request,item):
    datosRetiradaSinUbicacion = RegistroRetiradaStock.objects.using(
        "docLaruex").filter(item=item, ubicacion=None, error=None).values('id','cantidad','fecha','empleado', 'empleado__id', 'empleado__first_name','empleado__last_name', 'ubicacion')
    datosRetiradas = RegistroRetiradaStock.objects.using(
        "docLaruex").filter(item=item, error=None).values('id','cantidad','fecha','empleado', 'empleado__id', 'empleado__first_name','empleado__last_name', 'ubicacion','ubicacion__id', 'ubicacion__id__nombre')
    salida = list(datosRetiradas) + list(datosRetiradaSinUbicacion)
    return JsonResponse(list(salida), safe=False)


'''-------------------------------------------
                                Módulo: DatosRetiradasStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosRetiradasStockError(request,item):
    datosRetiradaSinUbicacion = RegistroRetiradaStock.objects.using(
        "docLaruex").filter(item=item, ubicacion=None, error=1).values('id','cantidad','fecha','empleado', 'empleado__id', 'empleado__first_name','empleado__last_name', 'ubicacion')
    datosRetiradas = RegistroRetiradaStock.objects.using(
        "docLaruex").filter(item=item, error=1).values('id','cantidad','fecha','empleado', 'empleado__id', 'empleado__first_name','empleado__last_name', 'ubicacion','ubicacion__id', 'ubicacion__id__nombre')
    salida = list(datosRetiradas) + list(datosRetiradaSinUbicacion)
    return JsonResponse(list(salida), safe=False)
'''-------------------------------------------
                                Módulo: editarStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def editarStock(request, id):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    itemStock = Stock.objects.using('docLaruex').filter(id=id)[0]
    ubicaciones = Ubicaciones.objects.using('docLaruex').order_by('-id__padre').values('id','tipo_ubicacion', 'tipo_ubicacion__nombre','id__nombre', 'id__padre__nombre', 'id__padre__id', 'id__padre')
    categorias = CategoriasStock.objects.using('docLaruex').order_by('categoria').values()
    unidades = UnidadesStock.objects.using('docLaruex').order_by('nombre').values()

    if request.method == 'POST':
        print("POST", request.POST)
        itemStock.nombre = request.POST['nuevoNombre']
        itemStock.id_ubicacion =  Ubicaciones.objects.using("docLaruex").filter(id=request.POST['nuevaUbicacion'])[0]
        itemStock.categoria = CategoriasStock.objects.using("docLaruex").filter(id=request.POST['nuevaCategoria'])[0]
        
        itemStock.num_estanteria = request.POST['nuevaEstanteria'] 
        itemStock.num_contenedor =  request.POST['nuevoContenedor']
        itemStock.cantidad = request.POST['nuevaCantidad']
        itemStock.min_cantidad = request.POST['nuevaCantidadMinima']
        itemStock.unidad = UnidadesStock.objects.using("docLaruex").filter(id=request.POST['nuevaUnidad'])[0]
        
        itemStock.urgente = request.POST['nuevoUrgente']

        if (request.POST['nuevoAvisado'] == "None"): 

            itemStock.avisado = None
        else:
            itemStock.avisado = request.POST['nuevoAvisado']
        itemStock.descripcion = request.POST['nuevaDescripcion']
        itemStock.save(using="docLaruex")
        return render(
            request,
            "docLaruex/itemStock.html",
            {"itemsMenu": itemsMenu, "itemStock": itemStock})
    else:
        return render(
            request,
            "docLaruex/editarStock.html",
            {"itemsMenu": itemsMenu, "itemStock": itemStock, "ubicaciones":list(ubicaciones), "categorias":list(categorias), "unidades":list(unidades)})

'''-------------------------------------------
                                Módulo: DatosHistoricoProveedores

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosHistoricoProveedores(request, id):
    itemStock = Stock.objects.using("docLaruex").filter(id=id)[0]
    historicoProveedores =RelStockProveedores.objects.using("docLaruex").filter(item=itemStock).values('fecha', 'coste', 'proveedor__id', 'proveedor__nombre', 'cantidad', 'unidad__nombre')
    return JsonResponse(list(historicoProveedores), safe=False)
            
'''-------------------------------------------
                                Módulo: eliminarStock

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def eliminarStock(request, id):
    stock = Stock.objects.using('docLaruex').filter(id=id)[0]
    RelStockProveedores.objects.using('docLaruex').filter(item=stock).delete()
    RegistroRetiradaStock.objects.using('docLaruex').filter(item=stock).delete()
    stock.delete(using="docLaruex")
    return eliminadoExito(request)

'''-------------------------------------------
                                Módulo: contacto

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def verContacto(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    contacto = Contacto.objects.using("docLaruex").filter(id=id).values('id','nombre','telefono', 'empresa', 'telefono_fijo','email','direccion', 'info_adicional', 'puesto','id_habilitacion__titulo','id_habilitacion__id','extension','dni', 'img', 'fecha_nacimiento').first()

    return render(request, 'docLaruex/contacto.html', {"itemsMenu": itemsMenu, "administrador": esAdministrador(request.user.id),"direccion": esDirector(request.user.id), "habilitaciones": list(habilitaciones), "contacto":contacto})


'''-------------------------------------------
                                Módulo: DatosContactos

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosContactos(request):
    contactos = Contacto.objects.using('docLaruex').order_by('id').values('id','nombre','telefono', 'empresa', 'telefono_fijo','email','direccion', 'info_adicional', 'puesto','id_habilitacion__titulo','id_habilitacion__id','extension')
    return JsonResponse(list(contactos), safe=False)

'''-------------------------------------------
                                Módulo: ListadoContactos

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ListadoContactos(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)    
    administrador = esAdministrador(request.user.id)

    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:

        return render(request, 'docLaruex/ListadoContactos.html', {"itemsMenu": itemsMenu, "administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario), "habilitaciones": list(habilitaciones)})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


'''-------------------------------------------
                                Módulo: agregarContacto

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------''' 
@login_required
def agregarContacto(request):

    
    if len(request.POST['telefono']) == 0:
        telefono = None
    else:
        telefono = request.POST['prefijoTelefono'] + request.POST['telefono']

    if len(request.POST['telefono_fijo']) == 0:
        telefono_fijo = None
    else:
        telefono_fijo = request.POST['prefijoTelefonoFijo'] + request.POST['telefono_fijo']

    if 'DNI' in request.POST: 
        dni = request.POST['DNI']

    if 'fechaNacimiento' in request.POST: 
        fechaNacimiento = request.POST['fechaNacimiento']

    if 'tipoContacto' in request.POST: 
        tipoContacto = request.POST['tipoContacto']


    nuevoContacto = Contacto(nombre=request.POST['nombreContacto'], telefono=telefono, telefono_fijo=telefono_fijo, email=request.POST['email'], empresa=request.POST['empresaContacto'], direccion=request.POST['direccionContacto'], info_adicional=request.POST['info_adicional_contacto'], puesto=request.POST['puestoContacto'], extension=request.POST['extension'], id_habilitacion=Habilitaciones.objects.using('docLaruex').get(id=request.POST['habilitacion']), dni=dni, fecha_nacimiento=fechaNacimiento, tipo_contacto=tipoContacto)
    nuevoContacto.save(using='docLaruex')

    #agregamos la imagen al contacto si existe
    if request.FILES.get('imagenContacto') is not None:
        print("--------------")
        print(request.FILES['imagenContacto'], "\n",request.FILES.get('imagenContacto'))
        print("--------------")
        ruta = settings.MEDIA_ROOT + 'archivos/Contacto/' + str(nuevoContacto.id) + '.' + request.FILES['imagenContacto'].name.split('.')[-1]   
        subirDocumento(request.FILES['imagenContacto'], ruta)
        nuevoContacto.img = str(nuevoContacto.id) + '.' + request.FILES['imagenContacto'].name.split('.')[-1]
        nuevoContacto.save(using='docLaruex')

    return JsonResponse({"Notificacion": "ok"}, safe=False)

'''-------------------------------------------
                                Módulo: editarContacto

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def editarContacto(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    contacto = Contacto.objects.using('docLaruex').filter(id=id)[0]

    if 'nuevoTelefono' in request.POST:
        if len(request.POST['nuevoTelefono']) == 0:
            telefono = None
        else:
            telefono = request.POST['nuevoPrefijoTelefono'] + request.POST['nuevoTelefono']
    else: 
        telefono = None

    if 'nuevoTelefonoFijo' in request.POST:
        if len(request.POST['nuevoTelefonoFijo']) == 0:
            telefono_fijo = None
        else:
            telefono_fijo = request.POST['nuevoPrefijoTelefonoFijo'] + request.POST['nuevoTelefonoFijo']
    else: 
        telefono_fijo = None

    if 'nuevaFechaNacimiento' in request.POST:        
        nuevaFechaNacimiento = request.POST['nuevaFechaNacimiento']
        if len(nuevaFechaNacimiento) == 0:
            nuevaFechaNacimiento = None
    else:
         nuevaFechaNacimiento = None 

    if 'nuevoDNI' in request.POST:
        nuevoDNI = request.POST['nuevoDNI']
    else:
        nuevoDNI = None

    if 'nuevaImagenContacto' in request.FILES:
        rutaImagen = settings.MEDIA_ROOT + 'archivos/Contacto/' + str(id) + '.' + request.FILES['nuevaImagenContacto'].name.split('.')[-1]
        archivoImagenContacto = str(id) + '.' + request.FILES['nuevaImagenContacto'].name.split('.')[-1]

        if contacto.img is not None:
            imagenContactoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Contacto/' + str(id) + '.*')
            if imagenContactoOld:
                os.remove(imagenContactoOld[0])
        subirDocumento(request.FILES['nuevaImagenContacto'], rutaImagen)
        contacto.img = archivoImagenContacto
        contacto.save(using="docLaruex")

    if request.method == 'POST':
        print("POST", request.POST)
        contacto.nombre = request.POST['nuevoNombreContacto']
        contacto.puesto = request.POST['nuevoPuestoContacto']
        contacto.empresa = request.POST['nuevaEmpresaContacto']
        contacto.direccion = request.POST['nuevaDireccionContacto']
        contacto.telefono = telefono
        contacto.telefono_fijo = telefono_fijo
        contacto.email = request.POST['nuevoEmailContacto']
        contacto.info_adicional = request.POST['nuevaInfoAdicionalContacto']
        contacto.dni = nuevoDNI
        contacto.fecha_nacimiento = nuevaFechaNacimiento
        contacto.extension = request.POST['nuevaExtension']
        contacto.save(using="docLaruex")
        return redirect('docLaruex:docLaruexVerContacto', id=id)
    else:
        return render(
            request,
            "docLaruex/editarContacto.html",
            {"itemsMenu": itemsMenu, "contacto": contacto})

'''-------------------------------------------
                                Módulo: eliminarContacto

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def eliminarContacto(request, id):
    fotoContacto = glob.glob(settings.MEDIA_ROOT + 'archivos/Contacto/' + id + '.*')
    if fotoContacto:
        os.remove(fotoContacto[0])
    contacto = Contacto.objects.using('docLaruex').filter(id=id)[0]
    contacto.delete(using="docLaruex")

    # volver a página ListadoContactos

    return ListadoContactos(request)


'''  
############## Carga la vista de todos los BORRAR ??? Curriculums ##############
@login_required
def ListadoCurriculums(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitaciones = Habilitaciones.objects.using("docLaruex").values(
        'id', 'titulo')

    return render(request, 'docLaruex/listaCurriculums.html', {"itemsMenu": itemsMenu, "administrador": esAdministrador(request.user.id), "habilitaciones": list(habilitaciones)})
'''


'''-------------------------------------------
                                Módulo: formacionesAsociadas

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def formacionesAsociadas(request, id_curriculum):
    formacionesAsociadas = FormacionCurriculum.objects.using('docLaruex').filter(id_curriculum=id_curriculum).values('id','titulo','descripcion','horas','ruta','fecha_inicio','fecha_fin')
    return JsonResponse(list(formacionesAsociadas),  safe=False)


'''-------------------------------------------
                                Módulo: formacionesAsociadasCurriculum

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def formacionesAsociadasCurriculum(request, id_curriculum, yearSelected):
    # filtrar la lista de formaciones por el año seleccionado 
    formacionesAsociadas = FormacionCurriculum.objects.using('docLaruex').filter(id_curriculum=id_curriculum,fecha_fin__year=yearSelected).values('id','titulo','descripcion','horas','ruta','fecha_inicio','fecha_fin')
    return JsonResponse(list(formacionesAsociadas), safe=False)
# FIN metodos para rellenar tablas en la vsita de procedimientos

'''-------------------------------------------
                                Módulo: eliminarItemCurriculum

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def eliminarItemCurriculum(request, id_curriculum, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    administrador = esAdministrador(request.user.id)
    archivoFormacion = glob.glob(settings.MEDIA_ROOT + 'archivos/Curriculum/'+ id_curriculum +'/' + id + '.*')
    if archivoFormacion:
        os.remove(archivoFormacion[0])

    FormacionCurriculum.objects.using('docLaruex').filter(id=id).delete()

    return render (request, 'docLaruex/listaCurriculums.html', {"itemsMenu": itemsMenu,  "administrador":administrador })

'''-------------------------------------------
                                Módulo: DatosEquiposBaja

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquiposBaja(request):
    
    equipos = Equipo.objects.using('docLaruex').order_by('-id').filter(fecha_baja__isnull=False, id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio', 'ubicacion_actual__id__nombre')

    '''
    for equipo in equipos:

        ubicacionActual = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=equipo["id"]).order_by('-fecha').values( 'id_ubicacion__id__nombre')[0]
    
        equipo["ubicacion"] = ubicacionActual["id_ubicacion__id__nombre"]
    '''
    
    return JsonResponse(list(equipos), safe=False)

'''-------------------------------------------
                                Módulo: DatosEquiposTipo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquiposTipo(request, id):

    equipos = Equipo.objects.using('docLaruex').order_by('-id').filter(tipo_equipo__id=id, fecha_baja__isnull=True, id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'num_serie', 'descripcion','fecha_alta', 'precio', 'grupo__nombre', 'ubicacion_actual__id__nombre')
    
    return JsonResponse(list(equipos), safe=False)


'''-------------------------------------------
                                Módulo: DatosEquiposGrupo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquiposGrupo(request, id):
    if id == "0":
        equipos = Equipo.objects.using('docLaruex').order_by('-id').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'num_serie', 'descripcion','fecha_alta', 'precio', 'grupo__nombre', 'grupo', 'ubicacion_actual__id__nombre')
    else:
        equipos = Equipo.objects.using('docLaruex').order_by('-id').filter(grupo__id=id, id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'num_serie', 'descripcion','fecha_alta', 'precio', 'grupo__nombre', 'ubicacion_actual__id__nombre')
    
    return JsonResponse(list(equipos), safe=False)


'''-------------------------------------------
                                Módulo: DatosEquiposCedidos

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquiposCedidos(request):
    equipos = Equipo.objects.using('docLaruex').order_by('-id').filter(propietario__isnull=False).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'num_serie', 'descripcion','fecha_alta', 'precio', 'grupo__nombre', 'grupo', 'ubicacion_actual__id__nombre')
    return JsonResponse(list(equipos), safe=False)

'''-------------------------------------------
                                Módulo: CambiarUbicacionEquipo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def CambiarUbicacionEquipo(request,id):
    auxEquipo = Equipo.objects.using("docLaruex").filter(id=id).get()
    auxUbicacion =Ubicaciones.objects.using("docLaruex").filter(id=request.POST.get("nuevaUbicacion")).get()


    # actualizamos la nueva ubicación en el equipo
    auxEquipo.ubicacion_actual = auxUbicacion
    auxEquipo.save(using='docLaruex')
    
    nuevaUbicacion = RelUbicacionesEquipos(id_equipo=auxEquipo, id_ubicacion=auxUbicacion, fecha=request.POST.get("fechaCambioUbicacion"))
    nuevaUbicacion.save(using='docLaruex')
    
    return HttpResponseRedirect('/private/docLaruex/verObjeto/'+id+'/')

'''-------------------------------------------
                                Módulo: EliminarEquipo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def EliminarEquipo(request,id):
    equipo = Objeto.objects.using('docLaruex').filter(id=id).get()
    Equipo.objects.using('docLaruex').filter(id=equipo).delete()
    Objeto.objects.using('docLaruex').filter(id=id).delete()
    RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).delete()
    RelacionDocumentaciones.objects.using('docLaruex').filter(id_doc=id).delete()
    RelacionDocumentacionesInverso.objects.using('docLaruex').filter(id_doc=id).delete()
    return render(request, 'docLaruex/ListaEquipos.html')



'''-------------------------------------------
                                Módulo: DarBajaEquipo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DarBajaEquipo(request,id):

    fecha_baja=datetime.now()
    if 'fechaBaja' in request.POST:
        fecha_baja=request.POST.get("fechaBaja")
    fecha_fin_mantenimiento=datetime.now()
    
    tarea = TareasProgramadas.objects.using('docLaruex').filter(id_objeto=id)[0]
    estadoCancelado = EstadoTareas.objects.using("docLaruex").filter(id=5)[0]
    estados = [1,2,4]

    registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea, estado__id__in=estados)[0]
    
    registro.fecha=fecha_fin_mantenimiento
    registro.estado = estadoCancelado
    registro.observaciones = "Mantenimiento cancelado por baja del equipo. \nMotivo: " + request.POST.get("motivoBaja")
    registro.empleado = AuthUser.objects.using("docLaruex").filter(id=request.user.id)[0]
    registro.save(using='docLaruex')
    Equipo.objects.using('docLaruex').filter(id=id).update(fecha_baja=fecha_baja, motivo_baja=request.POST.get("motivoBaja"))
    
    return ListadoObjetosPorTipo(request,"Equipo")
    
    
'''
############## Carga la vista de todos los Cursos BORRAR ##############
@login_required
def ListadoCursos(request):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    responsables = Responsables.objects.using(
        "docLaruex").values('id', 'first_name', 'last_name')
    habilitaciones = Habilitaciones.objects.using("docLaruex").values(
        'id', 'titulo')
    patrocinadores = Entidades.objects.using("docLaruex").values(
        'id', 'nombre', 'imagen')
    tipoCursos = TipoCurso.objects.using("docLaruex").values(
        'id', 'nombre')
    cursos = Cursos.objects.using("docLaruex").values('id','fecha_inicio', 'fecha_fin', 'id__nombre', 'id__ruta','id__ruta_editable','id__id_estado__id', 'id__id_estado__nombre', 'id__id_habilitacion__id', 'id__id_habilitacion__titulo', 'imagen', 'patrocinadores__nombre', 'tipo_curso__id', 'tipo_curso__nombre', 'horas')
    

    return render(request, 'docLaruex/listaCursos.html', {"itemsMenu": itemsMenu,"cursos":list(cursos), "responsables": list(responsables), "habilitaciones": list(habilitaciones), "patrocinadores":list(patrocinadores), "administrador": esAdministrador(request.user.id),"tipoCursos":list(tipoCursos)})
'''

'''-------------------------------------------
                                Módulo: DatosCursos

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosCursos(request):
    cursos = Cursos.objects.using('docLaruex').order_by('id').values('id','fecha_inicio', 'fecha_fin', 'id__nombre', 'id__ruta','id__ruta_editable','id__id_estado__id', 'id__id_estado__nombre', 'id__id_habilitacion__id', 'id__id_habilitacion__titulo', 'imagen', 'patrocinadores__nombre', 'tipo_curso__id', 'tipo_curso__nombre', 'horas')

    return JsonResponse(list(cursos),  safe=False)




'''-------------------------------------------
                                Módulo: CertificadoCurso

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def CertificadoCurso(request, id):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitaciones = Habilitaciones.objects.using("docLaruex").order_by('titulo').values(
        'id', 'titulo')
    
    curso = Cursos.objects.using('docLaruex').filter(id=id)[0]
    ponentes = AuthUser.objects.using('docLaruex').order_by('first_name').values()

    print("--------------------")
    print(curso)
    print("--------------------")

    return render(request, 'docLaruex/certificadoCurso.html', {"itemsMenu": itemsMenu,"administrador": esAdministrador(request.user.id), "habilitaciones": list(habilitaciones),"curso":curso, "ponentes":list(ponentes)})

'''-------------------------------------------
                                Módulo: datosArchivosAsociar

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def datosArchivosAsociar(request):
    objetosExcluidos = ["Equipo", "Ubicacion"]
    archivos =  Objeto.objects.using("docLaruex").exclude(tipo__in=objetosExcluidos).values()
    return JsonResponse(list(archivos), safe=False)



'''------------------------------------------
                                Módulo: asociarAsistentesCurso

- Descripción: 
Este módulo es utilizado para asociar una habilitación a uno o varios usuarios del sistema.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
El usuario debe ser un administrador.
Se debe recibir el id de la habilitación que se desea asociar.
Se deben recibir los ids de los usuarios a los que se desea asociar la habilitación, separados por "#".

- Postcondiciones:

Se crea una relación entre la habilitación y los usuarios especificados.

-------------------------------------------'''
@login_required
def asociarAsistentesCurso(request):
    # crear objeto en la tabla Objetos
    if esAdministrador(request.user.id):
        usuarios=request.POST.get("idUsuariosSeleccionados").split('#')
        for u in usuarios:
            usuario = u.split('@')
            if u != "":
                auxCurso= Cursos.objects.using("docLaruex").filter(id=request.POST.get("nombreObjeto")).get() 
                auxUser =  Contacto.objects.using("docLaruex").filter(id= usuario[0]).get()
                nuevaRelacion = RelCursoAsistentes(id_curso=auxCurso, id_asistente=auxUser, tipo=usuario[1])
                nuevaRelacion.save(using='docLaruex')
        # return ListadoObjetos(request)
        return JsonResponse({"documento": "ok"}, safe=False)



'''------------------------------------------
                                Módulo: datosAsistentesCurso

- Descripción: 
Este módulo obtiene los datos de todos los asistentes de un curso dado su id.

- Precondiciones:
El usuario debe estar autenticado.
Debe existir el curso.

- Postcondiciones:
Retorna una respuesta JSON con los datos de todos los currículums en la base de datos.
-------------------------------------------'''
@login_required
def datosAsistentesCurso(request, id):
    asistentes = RelCursoAsistentes.objects.using('docLaruex').filter(id_curso=id).order_by('id').values('id', 'tipo', 'id_asistente','id_asistente__id', 'id_asistente__nombre', 'id_asistente__telefono', 'id_asistente__telefono_fijo', 'id_asistente__email', 'id_asistente__info_adicional','id_asistente__id_habilitacion', 'id_asistente__puesto', 'id_asistente__direccion', 'id_asistente__empresa', 'id_asistente__extension', 'id_asistente__img', 'id_asistente__dni', 'id_asistente__fecha_nacimiento','id_asistente__tipo_contacto' )
    
    return JsonResponse(list(asistentes), safe=False)


'''------------------------------------------
                                Módulo: datosAsistentesCursoTipo

- Descripción: 
Este módulo obtiene los datos de todos los asistentes de un curso dado su id y su tipo de asistente.

- Precondiciones:
El usuario debe estar autenticado.
Debe existir el curso.

- Postcondiciones:
Retorna una respuesta JSON con los datos de todos los currículums en la base de datos.
-------------------------------------------'''
@login_required
def datosAsistentesCursoTipo(request, id, tipo):
    asistentes = RelCursoAsistentes.objects.using('docLaruex').filter(id_curso=id, tipo=tipo).order_by('id').values('id', 'tipo', 'id_asistente','id_asistente__id', 'id_asistente__nombre', 'id_asistente__telefono', 'id_asistente__telefono_fijo', 'id_asistente__email', 'id_asistente__info_adicional','id_asistente__id_habilitacion', 'id_asistente__puesto', 'id_asistente__direccion', 'id_asistente__empresa', 'id_asistente__extension', 'id_asistente__img', 'id_asistente__dni', 'id_asistente__fecha_nacimiento','id_asistente__tipo_contacto' )
    
    return JsonResponse(list(asistentes), safe=False)



'''-------------------------------------------
                                Módulo: eliminarAsistente

- Descripción: 
Permite eliminar una asociación entre dos objetos de la base de datos. id_actual es el objeto que estamos visualizando, mientras que id_objeto_eliminar es el objeto de la tabla de referencias que deseamos eliminar la asociación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def eliminarAsistente(request, id_asistente, id_curso):
    asistente = Contacto.objects.using("docLaruex").filter(id=id_asistente)[0]
    curso = Cursos.objects.using("docLaruex").filter(id=id_curso)[0]
    
    if RelCursoAsistentes.objects.using("docLaruex").filter(Q(id_curso=curso), Q(id_asistente=asistente)).exists():

        RelCursoAsistentes.objects.using("docLaruex").filter(Q(id_curso=curso), Q(id_asistente=asistente)).delete()
        

        return redirect('docLaruex:docLaruexInfoVerObjeto', id=id_curso)
    else: 
        return noEncontrado(request)


    
'''------------------------------------------
                                Módulo: agregarContenidoCurso

- Descripción: 
Este módulo agrega un nuevo contenido de curso a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.

- Postcondiciones:
La página del curso se renderiza de nuevo.
Se agrega un nuevo registro de proveedor a la base de datos.
-------------------------------------------'''    
@login_required
def agregarContenidoCurso(request):
    idCurso = request.POST.get("idCurso")
    curso = Cursos.objects.using('docLaruex').filter(id=request.POST.get("idCurso"))[0]
    ponente = Contacto.objects.using('docLaruex').filter(id=request.POST.get("ponente"))[0]

    # The above code is not doing anything as it only contains a single word "directorio" and no
    # actual code or syntax.
    # The above code is not doing anything as it only contains a single word "directorio" and no
    # actual code or syntax.
    directorio = settings.MEDIA_ROOT +"archivos/Curso/" + str(idCurso)
    
    if not os.path.exists(directorio):
        print("--- Creo la carpeta ---")
        os.makedirs(directorio)
    print("::::::::::::::::::")
    print(" he agregado contenido ")
    print("::::::::::::::::::")
    #agregamos el contenido
    nuevoContenido = ContenidoCurso(nombre_ponencia=request.POST.get("nombrePonencia"), fecha_ponencia=request.POST.get("fechaPonencia"), descripcion=request.POST.get("descripcionPonencia"), ponente=ponente)

    nuevoContenido.save(using='docLaruex')

    #relacionamos el contenido con el curso
    nuevaRelacionContenido = RelCursoContenido(id_curso=curso, id_contenido=nuevoContenido)
    nuevaRelacionContenido.save(using='docLaruex')

    #agregamos el archivo
    if 'archivoPonencia' in request.FILES:
        ficheroPonencia = request.FILES["archivoPonencia"] 

        nuevoContenido.archivo = str(nuevoContenido.id) + '.' + ficheroPonencia.name.split('.')[-1]
        nuevoContenido.save(using='docLaruex')

        rutaContenidoCurso = settings.MEDIA_ROOT + 'archivos/Curso/' + str(idCurso) +"/"+ nuevoContenido.archivo 

        #subimos el documento a la carpeta
        subirDocumento(ficheroPonencia, rutaContenidoCurso)

    return redirect('docLaruex:docLaruexInfoVerObjeto', id=idCurso)



    '''------------------------------------------
                                Módulo: eliminarContenidoCurso

- Descripción: 
Este módulo agrega un nuevo contenido de curso a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.
Se requiere el id del curso y el id del contenido que se desea borrar.

- Postcondiciones:
La página del curso se renderiza de nuevo.
Se agrega un nuevo registro de proveedor a la base de datos.
-------------------------------------------'''  

@login_required
def eliminarContenidoCurso(request, idCurso, idContenido):
    curso = Cursos.objects.using('docLaruex').filter(id=idCurso)[0]

    #eliminamos la relación del contenido
    RelCursoContenido.objects.using('docLaruex').filter(id_curso=idCurso, id_contenido=idContenido).delete()
    
    archivoContenido = glob.glob(settings.MEDIA_ROOT + 'archivos/Curso/'+ idCurso +'/' + idContenido + '.*')
    if archivoContenido:
        os.remove(archivoContenido[0])

    ContenidoCurso.objects.using('docLaruex').filter(id=idContenido).delete()


    return redirect('docLaruex:docLaruexInfoVerObjeto', id=idCurso)

'''-------------------------------------------
                                Módulo: editarContenidoCurso

- Descripción: 
Permite eliminar una asociación entre dos objetos de la base de datos. id_actual es el objeto que estamos visualizando, mientras que id_objeto_eliminar es el objeto de la tabla de referencias que deseamos eliminar la asociación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def editarContenidoCurso(request, id_curso, id_contenido):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    curso = Cursos.objects.using('docLaruex').filter(id=id_curso)[0]
    contenidoCurso = ContenidoCurso.objects.using('docLaruex').filter(id=id_contenido)[0]
    contactos = Contacto.objects.using("docLaruex").filter(tipo_contacto__contains="Persona").values()

    if request.method == 'POST':
        print("POST", request.POST)
        contenidoCurso.nombre_ponencia = request.POST['nuevoNombrePonencia']
        contenidoCurso.fecha_ponencia = request.POST['nuevaFechaPonencia']
        contenidoCurso.descripcion = request.POST['nuevaDescripcionPonencia']
        if request.POST.get("nuevoPonente"):
            contenidoCurso.ponente = Contacto.objects.using('docLaruex').filter(id=request.POST['nuevoPonente'])[0]
        '''
        if 'nuevaImagenContacto' in request.FILES:
            rutaImagen = settings.MEDIA_ROOT + 'archivos/Contacto/' + str(id) + '.' + request.FILES['nuevaImagenContacto'].name.split('.')[-1]
            archivoImagenContacto = str(id) + '.' + request.FILES['nuevaImagenContacto'].name.split('.')[-1]

            if contacto.img is not None:
                imagenContactoOld = glob.glob(settings.MEDIA_ROOT + 'archivos/Contacto/' + str(id) + '.*')
                if imagenContactoOld:
                    os.remove(imagenContactoOld[0])
            subirDocumento(request.FILES['nuevaImagenContacto'], rutaImagen)
            contacto.img = archivoImagenContacto
            contacto.save(using="docLaruex")
        '''
        contenidoCurso.save(using="docLaruex")
        return InfoVerObjeto(request, id_curso)


    else:
        return render(
            request,
            "docLaruex/editarContenidoCurso.html",
            {"itemsMenu": itemsMenu, "curso":curso, "contenidoCurso":contenidoCurso, "contactos":list(contactos)})



'''-------------------------------------------
                                Módulo: asociarArchivo

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def asociarArchivo(request,id):
    # crear objeto en la tabla Objetos
    print("REQUEST", request)

    archivos=request.POST.get("idArchivosSeleccionados").split('#')
    print("ARCHIVOS:", archivos)
    archivoActual=Objeto.objects.using("docLaruex").filter(id=id).get()
    for a in archivos:
        if a is not None:
            archivo = a.split('#')
        if a != "" and a != None:
            auxArch = ObjetoRelacionado.objects.using("docLaruex").filter(id=archivo[0]).get()
            nuevaRelacionArchivos = RelacionDocumentaciones(id_doc=archivoActual, id_relacionado=auxArch)
            nuevaRelacionArchivos.save(using='docLaruex')
            
    # return ListadoObjetos(request)
    return JsonResponse({"documento": "ok"}, safe=False)
    


'''-------------------------------------------
                                Módulo: eliminarAsocicion

- Descripción: 
Permite eliminar una asociación entre dos objetos de la base de datos. id_actual es el objeto que estamos visualizando, mientras que id_objeto_eliminar es el objeto de la tabla de referencias que deseamos eliminar la asociación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def eliminarAsocicion(request, id_objeto_eliminar, id_actual):
    
    if RelacionDocumentaciones.objects.using("docLaruex").filter(Q(id_doc=id_actual) | Q(id_doc=id_objeto_eliminar), Q(id_relacionado=id_objeto_eliminar) | Q(id_relacionado=id_actual)).exists():

        RelacionDocumentaciones.objects.using("docLaruex").filter(Q(id_doc=id_actual) | Q(id_doc=id_objeto_eliminar), Q(id_relacionado=id_objeto_eliminar) | Q(id_relacionado=id_actual)).delete()
        return InfoVerObjeto(request, id_actual)
    else: 
        return noEncontrado(request)


# class reportEquipoPDF(PDFTemplateView,id):
#     equipo = Equipo.objects.using("docLaruex").filter(id=id)[0]
#     ubicaciones = Ubicaciones.objects.using("docLaruex").values('id','id__nombre')
#     historicoUbicaciones = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).order_by('-fecha').values( 'id_ubicacion__id__nombre','id_equipo','fecha')

#     filename = 'report_equipo_%s.pdf' % equipo
#     html = ReportEquipo(id)

#     def get_context_data(self, **kwargs):
#         context = super(reportEquipoPDF, self).get_context_Data(**kwargs)
#         return context

'''
############### --------------- Prueba 1 --------------- ###############
# modulo que imprima un reporte de un equipo desde un template
def ReportEquipo(request,id):
    equipo = Equipo.objects.using("docLaruex").filter(id=id)[0]
    ubicaciones = Ubicaciones.objects.using("docLaruex").values('id','id__nombre')
    historicoUbicaciones = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).order_by('-fecha').values( 'id_ubicacion__id__nombre','id_equipo','fecha')

    html = render_to_string('docLaruex/reportEquipo.html', {'equipo': equipo, 'ubicaciones': ubicaciones, 'historicoUbicaciones': historicoUbicaciones})
    return generar_pdf(html)

# modulo que genera un pdf a partir de un html
def generar_pdf(html):
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('Error al generar el PDF: %s' % cgi.escape(html))   # escape the output in case of errors   
'''



'''
############### --------------- Prueba 2 --------------- ###############
def reportEquipoPDF(request,id):
    equipo = Equipo.objects.using("docLaruex").filter(id=id)[0]
    ubicaciones = Ubicaciones.objects.using("docLaruex").values('id','id__nombre')
    historicoUbicaciones = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).order_by('-fecha').values( 'id_ubicacion__id__nombre','id_equipo','fecha')

    filename = 'report_equipo_%s.pdf' % equipo
    html = ReportEquipo(id)

    return render_to_pdf(html, filename)
'''


'''-------------------------------------------
                                Módulo: ImprimirEquipo

- Descripción: 
Permite eliminar una asociación entre dos objetos de la base de datos. id_actual es el objeto que estamos visualizando, mientras que id_objeto_eliminar es el objeto de la tabla de referencias que deseamos eliminar la asociación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ImprimirEquipo(request,id):

    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

    pdf = pdfkit.from_url('http://localhost:8000/private/docLaruex/reportEquipo/'+str(id)+'/', False, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response


'''-------------------------------------------
                                Módulo: ReportEquipo

- Descripción: 
Permite eliminar una asociación entre dos objetos de la base de datos. id_actual es el objeto que estamos visualizando, mientras que id_objeto_eliminar es el objeto de la tabla de referencias que deseamos eliminar la asociación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def ReportEquipo(request,id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    equipo = Equipo.objects.using("docLaruex").filter(id=id)[0]
    ubicaciones = Ubicaciones.objects.using("docLaruex").order_by('-id__padre').values('id','id__nombre','id__padre','id__padre__nombre')
    PrimerHistorico = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).order_by('-fecha')[0]

    historicoUbicaciones = RelUbicacionesEquipos.objects.using('docLaruex').filter(id_equipo=id).order_by('-fecha').values( 'id','id_ubicacion__id__nombre','id_equipo','fecha', 'id_ubicacion__alias', 'id_ubicacion__id__padre', 'id_ubicacion__id','id_ubicacion__id__padre__nombre')
    reportEquipo=True
    ruta = settings.MEDIA_URL 
    return render(request, "docLaruex/reportEquipo.html",{"itemsMenu": itemsMenu, "PrimerHistorico": PrimerHistorico, "equipo": equipo, "historicoUbicaciones": list(historicoUbicaciones), "ubicaciones":list(ubicaciones), "ruta":ruta, "reportEquipo":reportEquipo})


'''-------------------------------------------
                                Módulo: comprobarPropietario

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def comprobarPropietario(request,id_objeto):
    resultado = False
    if Curriculum.objects.using("docLaruex").filter(id=id_objeto, id_usuario=request.user.id).exists():
        resultado =True
        return JsonResponse({'resultado': resultado}) 
    else:
        return JsonResponse({'resultado': resultado}) 


'''------------------------------------------
                                Módulo: ListadoLlaves

- Descripción: 

Este módulo muestra una lista de proveedores.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.

- Postcondiciones:
Renderiza la página que muestra la lista de proveedores.

-------------------------------------------'''
@login_required
def listadoLlaves(request):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    habilitacionesUsuario = comprobarHabilitaciones(request.user.id)
    administrador = esAdministrador(request.user.id)

    llaves = Llave.objects.using("docLaruex").values()
    ubicaciones =  Ubicaciones.objects.using(
        "docLaruex").order_by('-id__padre').values('id', 'id__nombre', 'id__padre', 'id__padre__nombre')
    responsables =  Responsables.objects.using(
        "docLaruex").values('id', 'first_name', 'last_name')
    # Desde aquí es desde donde se pasan los datos para realizar el bucle que muestra los usuarios/empleados
    if Habilitaciones.objects.using("docLaruex").filter(id__in=habilitacionesUsuario) or administrador:
        return render(request, 'docLaruex/listaLlaves.html', {"itemsMenu": itemsMenu,"administrador": administrador,"habilitacionesUsuario":list(habilitacionesUsuario),"llaves":llaves, "ubicaciones":ubicaciones, "responsables":responsables})
    else:
        return render(request,"docLaruex/accesoDenegado.html", {"itemsMenu": itemsMenu})


    

'''------------------------------------------
                                Módulo: DatosLlaves

- Descripción: 
Este módulo devuelve los datos de las llaves ordenados por ID  en formato JSON.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.

- Postcondiciones:
Devuelve los datos de las llaves en formato JSON.
-------------------------------------------'''
@login_required
def DatosLlaves(request):
    llaves = Llave.objects.using('docLaruex').order_by('id').values(
        'id','nombre', 'imagen', 'ubicacion', 'ubicacion__id__padre', 'ubicacion__id__padre__nombre', 'ubicacion__id__nombre', 'responsable', 'responsable__first_name', 'responsable__last_name', 'color', 'id_habilitacion__titulo', 'fecha')
    return JsonResponse(list(llaves), safe=False)  


    
'''------------------------------------------
                                Módulo: agregarLlave

- Descripción: 
Este módulo agrega un nueva llave a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.

- Postcondiciones:
La página de lista de proveedores se renderiza de nuevo.
Se agrega un nuevo registro de proveedor a la base de datos.
-------------------------------------------'''    
@login_required
def agregarLlave(request):
    habilitacion = Habilitaciones.objects.using('docLaruex').filter(id=6)[0]
    fecha = datetime.now()
    ubicacion = Ubicaciones.objects.using('docLaruex').filter(id=request.POST.get("ubicacion"))[0]
    responsable = AuthUser.objects.using('docLaruex').filter(id=request.POST.get("responsable"))[0]
    localizacion = Ubicaciones.objects.using('docLaruex').filter(id=request.POST.get("localizacion"))[0]

    #agregamos la llave
    nuevaLlave = Llave(nombre=request.POST.get("nombre"), ubicacion=ubicacion, responsable=responsable, color=request.POST.get("color"), id_habilitacion=habilitacion, fecha=fecha)

    nuevaLlave.save(using='docLaruex')

    #agregamos la imagen de la llave
    if request.FILES.get('imagenLlave') is not None:
        print("--------------")
        print(request.FILES['imagenLlave'], "\n",request.FILES.get('imagenLlave'))
        print("--------------")
        ruta = settings.MEDIA_ROOT + 'archivos/Llave/' + str(nuevaLlave.id) + '.' + request.FILES['imagenLlave'].name.split('.')[-1]   
        subirDocumento(request.FILES['imagenLlave'], ruta)
        nuevaLlave.imagen = str(nuevaLlave.id) + '.' + request.FILES['imagenLlave'].name.split('.')[-1]
        nuevaLlave.save(using='docLaruex')
    #asociamos donde se encuentra
    ubicacionLlave = RelLlavesUbicaciones(fecha=fecha, id_llave=nuevaLlave, id_ubicacion=localizacion)
    ubicacionLlave.save(using='docLaruex')

    return listadoLlaves(request)
'''------------------------------------------
                                Módulo: verLlave

- Descripción: 
Este módulo se encarga de mostrar la información detallada de un proveedor seleccionado por el usuario. Se utiliza para ver los datos del proveedor en pantalla.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un proveedor existente en la base de datos para visualizar su información.

- Postcondiciones:
Se debe mostrar la información detallada del proveedor seleccionado.
El proveedor debe existir en la base de datos.

-------------------------------------------'''   
@login_required
def verLlave(request, id):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    llave = Llave.objects.using('docLaruex').values(
        'id','nombre', 'imagen', 'ubicacion', 'ubicacion__id__padre', 'ubicacion__id__padre__nombre', 'ubicacion__id__nombre', 'ubicacion__id', 'responsable','responsable__id', 'responsable__first_name', 'responsable__last_name', 'color', 'id_habilitacion__titulo','id_habilitacion__id', 'fecha').filter(id=id)[0]

    responsables = AuthUser.objects.using(
        "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser','last_login')
        
    habilitaciones = Habilitaciones.objects.using('docLaruex').values('id', 'titulo')
    ubicacionesLlave = RelLlavesUbicaciones.objects.using('docLaruex').filter(id_llave=id).order_by('-fecha').values('id', 'fecha', 'id_ubicacion__id','id_ubicacion__id__nombre', 'id_ubicacion__id__padre', 'id_ubicacion__id__padre__nombre')
    ubicaciones = Ubicaciones.objects.using('docLaruex').order_by('-id__padre__nombre').values('id', 'id__nombre', 'id__padre', 'id__padre__nombre')


    restoUbicaciones = []
    ubicacionActual = []

    for h in ubicacionesLlave: 
        if h == ubicacionesLlave[0]:
            ubicacionActual.append(h)
        else:
            restoUbicaciones.append(h)
   
    return render(request,"docLaruex/llave.html",{"itemsMenu": itemsMenu, "llave": llave, "administrador": esAdministrador(request.user.id),"ubicacionesLlave":list(ubicacionesLlave), "ubicacionActual":ubicacionActual, "restoUbicaciones":restoUbicaciones,  "responsables":list(responsables), "habilitaciones":list(habilitaciones), "ubicaciones":list(ubicaciones)})



'''------------------------------------------
                                Módulo: editarLlave

- Descripción:  
Este módulo permite al usuario editar la información de un proveedor existente en la base de datos. Se utiliza para actualizar los datos del proveedor.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un proveedor existente en la base de datos para editar su información.

- Postcondiciones:
Los datos del proveedor deben ser actualizados en la base de datos.
Se debe mostrar la información actualizada del proveedor en pantalla.

-------------------------------------------'''   
@login_required
def editarLlave(request, id):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    llave = Llave.objects.using('docLaruex').filter(id=id)[0]

    if request.method == 'POST':
        print("POST", request.POST)
        llave.nombre = request.POST['nuevoNombre']
        if request.POST.get("nuevoResponsable"):
            llave.responsable = AuthUser.objects.using('docLaruex').filter(id=request.POST['nuevoResponsable'])[0]
        if request.POST.get("nuevaHabilitacion"):
            llave.id_habilitacion = Habilitaciones.objects.using('docLaruex').filter(id=request.POST['nuevaHabilitacion'])[0]
        if request.POST.get("nuevaUbicacion"):
            llave.ubicacion = Ubicaciones.objects.using('docLaruex').filter(id=request.POST['nuevaUbicacion'])[0]
        llave.fecha = request.POST['nuevaFecha']
        llave.color = request.POST['nuevoColor']

        #agregamos una nueva localización
        if request.POST.get("nuevaLocalizacion"):

            fecha = datetime.now()
            nuevaLocalizacion = Ubicaciones.objects.using('docLaruex').filter(id=request.POST.get("nuevaLocalizacion"))[0]
            nuevaUbicacionLlave = RelLlavesUbicaciones(fecha=fecha, id_llave=llave, id_ubicacion=nuevaLocalizacion)
            nuevaUbicacionLlave.save(using='docLaruex')

        llave.save(using="docLaruex")

        return redirect('docLaruex:docLaruexVerLlave', id=id)
    else:
        responsables = AuthUser.objects.using(
            "docLaruex").order_by('first_name').values('id', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser','last_login')
            
        habilitaciones = Habilitaciones.objects.using('docLaruex').values('id', 'titulo')
        ubicacionesLlave = RelLlavesUbicaciones.objects.using('docLaruex').filter(id_llave=id).order_by('-fecha').values('id', 'fecha', 'id_ubicacion__id','id_ubicacion__id__nombre', 'id_ubicacion__id__padre', 'id_ubicacion__id__padre__nombre')
        ubicaciones = Ubicaciones.objects.using('docLaruex').order_by('-id__padre__nombre').values('id', 'id__nombre', 'id__padre', 'id__padre__nombre')
        return render(
            request,
            "docLaruex/editarLlave.html",
            {"itemsMenu": itemsMenu, "llave": llave, "ubicacionesLlave":list(ubicacionesLlave), "responsables":list(responsables), "habilitaciones":list(habilitaciones), "ubicaciones":list(ubicaciones)})



'''------------------------------------------
                                Módulo: eliminarLlave

- Descripción:  
Este módulo se encarga de eliminar una llave existente en la base de datos. Se utiliza para borrar los datos de un proveedor que ya no es necesario.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado una llave existente en la base de datos para eliminar.

- Postcondiciones:
El proveedor debe ser eliminado de la base de datos.
Se debe mostrar la página de listado de proveedores sin el proveedor eliminado.

-------------------------------------------''' 
@login_required
def eliminarLlave(request, id):
    print("--------------- eliminar -------------------")
    llave = Llave.objects.using('docLaruex').filter(id=id)[0]
    ubicacionesLlave = RelLlavesUbicaciones.objects.using('docLaruex').filter(id_llave=llave)

    #eliminamos cada una de las ubicaciones de la llave
    for u in ubicacionesLlave:
        u.delete(using='docLaruex')

    archivoLlave = glob.glob(settings.MEDIA_ROOT + 'archivos/Llave/' + id + '.*')
    if archivoLlave:
        os.remove(archivoLlave[0])

    llave.delete(using="docLaruex")
    return redirect('docLaruex:docLaruexLlaves')



'''-------------------------------------------
                                Módulo: llavesAsociadasUbicacion

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def llavesDeUbicacion(request, id_ubicacion):
    ubicacion = Ubicaciones.objects.using('docLaruex').filter(id=id_ubicacion)[0]
    llave = Llave.objects.using('docLaruex').filter(ubicacion=ubicacion, nombre__contains="Original").values('imagen','id','responsable','responsable__first_name', 'responsable__last_name', 'color').first()
    return JsonResponse(llave, safe=False)



'''-------------------------------------------
                                Módulo: llavesAsociadasUbicacion

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def datosLlavesAlmacenadasUbicacion(request, id_ubicacion):
    ubicacion = Ubicaciones.objects.using('docLaruex').filter(id=id_ubicacion)[0]
    llavesUbicadas = RelLlavesUbicaciones.objects.using('docLaruex').filter(id_ubicacion=ubicacion).values('id_llave','id_llave__id', 'id_llave__nombre', 'id_llave__imagen', 'id_ubicacion', 'id_ubicacion__id__padre', 'id_ubicacion__id__padre__nombre', 'id_ubicacion__id__nombre', 'id_llave__responsable', 'id_llave__responsable__first_name', 'id_llave__responsable__last_name', 'id_llave__color', 'id_llave__id_habilitacion__titulo', 'id_llave__fecha')


    return JsonResponse(list(llavesUbicadas), safe=False)

'''------------------------------------------
                                Módulo: datosContactosAsociarCurso

- Descripción: 
Este módulo es utilizado para obtener una lista de contactos en el sistema que pueden ser asociados a una habilitación específica. Retorna una lista de objetos JSON con la información de los usuarios.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
El usuario debe ser un administrador.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosContactosAsociarCurso(request):
    
    if esAdministrador(request.user.id):
        contactos =  Contacto.objects.using("docLaruex").filter(tipo_contacto__contains="Persona").values()
        return JsonResponse(list(contactos), safe=False)


def generarQR(request, url, codigo):
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
    text = f"ID: {codigo}"
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

    # Crear un objeto HttpResponse con el contenido de la imagen final
    response = HttpResponse(buffer2.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{codigo}.png"'

    return response



def generadorQR(request):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    if request.method == "POST":
        url = request.POST.get("url")
        codigo = request.POST.get("codigo")
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

        # Crear un objeto HttpResponse con el contenido de la imagen final
        response = HttpResponse(buffer2.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{codigo}.png"'

        return response
    else:
        return render(request, "docLaruex/generarQR.html", {"itemsMenu": itemsMenu})




# =========================================================================
#            MÓDULOS QUE PERMITEN GESTIONAR LOS MANTENIMIENTOS
# =========================================================================

'''------------------------------------------
La función accesoDenegado, renderiza la plantilla "docLaruex/accesoDenegado.html" cuando el usuario no tiene los permisos necesarios para acceder a una determinada funcionalidad.

- Precondiciones:
    Debe haber recibido una solicitud de "request"

- Postcondiciones:
    devuelve una respuesta renderizada utilizando la función "render" de Django.
-------------------------------------------'''
def eventos(request):
    tipoObjeto = ['Equipo', 'Ubicacion']
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    tiposEvento = TiposEventos.objects.using("docLaruex").values('id','nombre')

    procedimientos =[]

    procedimientosSinFiltrar = Procedimiento.objects.using("docLaruex").values('id_doc', 'id_doc__id', 'id_doc__nombre', 'version')
    formatos = Formatos.objects.using("docLaruex").filter(plantilla=1).values('id_doc', 'id_doc__id', 'id_doc__nombre', 'version')
    for p in procedimientosSinFiltrar:
        if p['id_doc__nombre'] not in [pf['id_doc__nombre'] for pf in procedimientos]:
            procedimientos.append(p)
        else:
            for pf in procedimientos:
                if pf['id_doc__nombre'] == p['id_doc__nombre']:
                    if p['version'] > pf['version']:
                        procedimientos.remove(pf)
                        procedimientos.append(p)
                    break
    print(len(procedimientos))

    objetos = Objeto.objects.using("docLaruex").filter(tipo__in=tipoObjeto).values('id','nombre', 'tipo')
    # Renderiza la plantilla accesoDenegado.html con los elementos del menú
    return render(request, 'docLaruex/listadoEventos.html', {"itemsMenu": itemsMenu, "tiposEvento":list(tiposEvento), "procedimientos":list(procedimientos), "objetos":list(objetos), "formatos":list(formatos)})

'''------------------------------------------
                                Módulo: datosEventos

- Descripción: 
Este módulo es utilizado para obtener una lista de contactos en el sistema que pueden ser asociados a una habilitación específica. Retorna una lista de objetos JSON con la información de los usuarios.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.
El usuario debe ser un administrador.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosEventos(request):
    if esAdministrador(request.user.id):
        eventos = Eventos.objects.using("docLaruex").values( 'id', 'tipo_periodicidad', 'tipo_evento__id','tipo_evento__nombre', 'nombre', 'procedimiento_asociado','datos','procedimiento_asociado__id_doc__nombre', 'periodicidad__id', 'periodicidad__cantidad', 'periodicidad__unidad')
        return JsonResponse(list(eventos), safe=False)

@login_required
def datosEventosTipo(request, tipoEvento):
    eventos = tipoEvento.split(',')
    eventosFiltrados = Eventos.objects.using("docLaruex").filter(tipo_evento__id__in=eventos).values( 'id', 'tipo_periodicidad', 'tipo_evento__id','tipo_evento__nombre', 'nombre', 'procedimiento_asociado','datos','procedimiento_asociado__id_doc__nombre', 'periodicidad__id', 'periodicidad__cantidad', 'periodicidad__unidad')
    print('\033[91m'+'eventosFiltrados: ' + '\033[92m', eventosFiltrados)
    return JsonResponse(list(eventosFiltrados), safe=False)


    
'''------------------------------------------
                                Módulo: agregarEvento

- Descripción: 
Este módulo agrega un nuevo evento a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.

- Postcondiciones:
La página de lista de proveedores se renderiza de nuevo.
Se agrega un nuevo registro de proveedor a la base de datos.
-------------------------------------------'''    
@login_required
def agregarEvento(request):
    # compruebo si existe periodicidad en la tabla y la agrego en caso de que no exista
    cantidad = request.POST.get("cantidad")
    unidad = request.POST.get("unidad")
    procedimientoAsociado = None
    plantillaFormatoAsociado = None
    print('\033[91m'+'request.POST.get("formatoPlantilla"): ' + '\033[92m', request.POST.get("formatoPlantilla"), type(request.POST.get("formatoPlantilla")))
    
    print('\033[91m'+'request.POST.get("procedimiento"): ' + '\033[92m', request.POST.get("procedimiento"), type(request.POST.get("procedimiento")))

    if Periodicidad.objects.using("docLaruex").filter(cantidad=cantidad, unidad=unidad).exists():
        periodicidad = Periodicidad.objects.using("docLaruex").filter(cantidad=cantidad, unidad=unidad)[0]
    else: 
        periodicidad = Periodicidad(cantidad=cantidad, unidad=unidad)
        periodicidad.save(using='docLaruex')

    # agrego los campos al eventos
    tipoEvento = TiposEventos.objects.using("docLaruex").filter(id=request.POST.get("tipoEvento"))[0]
    tipoPeriodicidad = TipoPeriodicidad.objects.using("docLaruex").filter(id=request.POST.get("tipoPeriodicidad"))[0]
    if request.POST.get("procedimiento") != "0":
        procedimientoAsociado = Procedimiento.objects.using("docLaruex").filter(id_doc=request.POST.get("procedimiento"))[0]
        if request.POST.get("formatoPlantilla") != "0":
            plantillaFormatoAsociado = Formatos.objects.using("docLaruex").filter(id_doc=request.POST.get("formatoPlantilla"))[0]

    estado = Estado.objects.using("docLaruex").filter(id=request.POST.get("estado"))[0]

    datos = request.POST.get("estructuraDatos") 

    nuevoEvento = Eventos(tipo_periodicidad=tipoPeriodicidad, tipo_evento=tipoEvento, nombre=request.POST.get("nombreEvento"), procedimiento_asociado=procedimientoAsociado, datos=datos, periodicidad=periodicidad, formato_asociado=plantillaFormatoAsociado, estado=estado)
    nuevoEvento.save(using='docLaruex')
    
    return redirect('docLaruex:docLaruexEventos')


    '''------------------------------------------
                                Módulo: editarEvento

- Descripción:  
Este módulo permite al usuario editar la información de un evento existente en la base de datos. Se utiliza para actualizar los datos del evento.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un evento existente en la base de datos para editar su información.

- Postcondiciones:
Los datos del evento deben ser actualizados en la base de datos.
Se debe mostrar la información actualizada del evento en pantalla.

-------------------------------------------'''   
@login_required
def editarEvento(request, id):

    itemsMenu = MenuBar.objects.using("docLaruex").values()
    evento = Eventos.objects.using('docLaruex').filter(id=id)[0]
    
    procedimientos = Procedimiento.objects.using("docLaruex").values('id_doc__id','id_doc__nombre')

    if request.method == 'POST':    
        cantidad = request.POST.get("nuevaCantidad")
        unidad = request.POST.get("nuevaUnidad")
        
        if Periodicidad.objects.using("docLaruex").filter(cantidad=cantidad, unidad=unidad).exists():
            periodicidad = Periodicidad.objects.using("docLaruex").filter(cantidad=cantidad, unidad=unidad)[0]
        else: 
            periodicidad = Periodicidad(cantidad=cantidad, unidad=unidad)
            periodicidad.save(using='docLaruex')

        if 'datos' in request.POST:
            datos = request.POST.get("nuevosDatos")
        else:
            datos = None

        # agrego los campos al eventos
        tipoEvento = TiposEventos.objects.using("docLaruex").filter(id=request.POST.get("nuevoTipoEvento"))[0]
        tipoPeriodicidad = TipoPeriodicidad.objects.using("docLaruex").filter(id=request.POST.get("nuevoTipoPeriodicidad"))[0]
        procedimientoAsociado = Procedimiento.objects.using("docLaruex").filter(id_doc=request.POST.get("nuevoProcedimiento"))[0]

        evento.tipo_periodicidad = tipoPeriodicidad
        evento.tipo_evento = tipoEvento
        evento.procedimiento_asociado = procedimientoAsociado
        evento.nombre = request.POST['nuevoNombreEvento']
        evento.periodicidad = periodicidad
        evento.datos = datos
        
        evento.save(using="docLaruex")

        return redirect('docLaruex:docLaruexEventos')
    else:
        return render(
            request,
            "docLaruex/editarEvento.html",
            {"itemsMenu": itemsMenu, "evento": evento, "procedimientos":list(procedimientos)})

'''------------------------------------------
                                Módulo: eliminarEvento

- Descripción: 
Este módulo se encarga de eliminar un evento.
- Precondiciones:
El usuario debe estar autenticado y ser un administrador.

- Postcondiciones:
Se elimina la reserva de un procedimiento de la base de datos y se muestra la lista actualizada de habilitaciones.
-------------------------------------------'''
@login_required
def eliminarEvento(request,id_evento):
    if esAdministrador(request.user.id):
        Eventos.objects.using("docLaruex").filter(id=id_evento).delete()
        return redirect('docLaruex:docLaruexEventos')
    else:
        return accesoDenegado(request)


def calcularPeriodicidad(id_evento, fecha_aux, boolString):
    evento = Eventos.objects.using("docLaruex").filter(id=id_evento)[0]
    periodicidad = evento.periodicidad
    

    fecha = fecha_aux
    if boolString == True:
        fecha = datetime.strptime(fecha_aux, '%Y-%m-%dT%H:%M')

    if periodicidad.unidad == 'Hora':
        # add periodicidad.cantidad hours to fecha using timedelta
        fecha = fecha + timedelta(hours=periodicidad.cantidad)
    if periodicidad.unidad == 'Día':
        # add periodicidad.cantidad days to fecha using timedelta
        fecha = fecha + timedelta(days=periodicidad.cantidad)
    if periodicidad.unidad == 'Semana':
        # add periodicidad.cantidad weeks to fecha using timedelta
        fecha = fecha + timedelta(weeks=periodicidad.cantidad)
    if periodicidad.unidad == 'Mes': 
        # add periodicidad.cantidad months to fecha using timedelta
        fecha = fecha + relativedelta(months=periodicidad.cantidad)
    if periodicidad.unidad == 'Año':  
        # add periodicidad.cantidad years to fecha using timedelta
        fecha = fecha + relativedelta(years=periodicidad.cantidad)
    
    return fecha



 
'''------------------------------------------
                                Módulo: agregarEvento

- Descripción: 
Este módulo agrega un nuevo evento a la base de datos.

- Precondiciones:
El usuario debe haber iniciado sesión en la aplicación.
Los campos del formulario deben haber sido validados.

- Postcondiciones:
La página de lista de proveedores se renderiza de nuevo.
Se agrega un nuevo registro de proveedor a la base de datos.
-------------------------------------------'''    
@login_required
def agregarTarea(request, id_evento):
    # compruebo si existe periodicidad en la tabla y la agrego en caso de que no exista
    
    evento = Eventos.objects.using("docLaruex").filter(id=id_evento)[0]
    objeto = Objeto.objects.using("docLaruex").filter(id=request.POST.get("idObjeto"))[0]
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    if TareasProgramadas.objects.using("docLaruex").filter(id_evento=evento, id_objeto=objeto).exists():
        return render(request,"docLaruex/404_tarea.html", {"itemsMenu": itemsMenu})

    else:
        nuevaTarea = TareasProgramadas(id_evento=evento, id_objeto=objeto, fecha_inicial=request.POST.get("fecha_inicio"), observaciones=request.POST.get("observaciones"))
        nuevaTarea.save(using='docLaruex')
        fechaTarea = nuevaTarea.fecha_inicial

        if evento.tipo_periodicidad.id == 1:
            fechaProgramada = calcularPeriodicidad(id_evento, nuevaTarea.fecha_inicial, True)
        elif evento.tipo_periodicidad.id == 2:
            fechaProgramada = calcularPeriodicidad(id_evento, nuevaTarea.fecha_inicial, True)
        else:
            fechaProgramada = None

        estadoProgramado = EstadoTareas.objects.using("docLaruex").filter(id=1)[0]
        
        nuevoRegistro = RegistroTareaProgramada(id_tarea_programada=nuevaTarea, fecha_programada=fechaProgramada, fecha=None, empleado=None,conforme=None, observaciones=None, estado=estadoProgramado )
        nuevoRegistro.save(using='docLaruex')
        
        nuevaTarea.fecha_proximo_mantenimiento = fechaProgramada
        nuevaTarea.save(using='docLaruex')
        
        return redirect('docLaruex:docLaruexTareas')

@login_required
def completarHistorico(request):
    fechaRealizado = request.POST.get("fecha_realizado")
    tarea = TareasProgramadas.objects.using("docLaruex").filter(id=request.POST.get("tareaProgramada"))[0]
    evento = tarea.id_evento     
    registro = RegistroTareaProgramada.objects.using("docLaruex").filter(id=request.POST.get("historico"))[0]
    empleado = AuthUser.objects.using("docLaruex").filter(id=request.user.id)[0] 
    if evento.tipo_periodicidad.id == 1:
        fecha_tarea = tarea.fecha_proximo_mantenimiento 
        proximaFecha = calcularPeriodicidad(evento.id, fecha_tarea, False)
    elif evento.tipo_periodicidad.id == 2:
        proximaFecha = calcularPeriodicidad(evento.id, fechaRealizado, True)
    else:
        proximaFecha = None
    # completamos lo datos del registro incompleto
    registro.empleado = empleado
    registro.fecha = fechaRealizado
    registro.fecha_programada = proximaFecha
    registro.conforme = request.POST.get("conforme")
    registro.estado = EstadoTareas.objects.using("docLaruex").filter(id=3)[0]
    registro.observaciones = request.POST.get("observacionesRegistro")

    # obtengo el json de evento (esquema)
    esquemaNuevo =  json.loads(tarea.id_evento.datos)
    # recorro el json evento.datos y voy rellenando usando la clave del json y haciendo get con esa clave en request.POST.get(clave)
    for e in esquemaNuevo:
        esquemaNuevo[e] = request.POST.get(e)

    # guardo el json en registro.datos
    registro.datos = esquemaNuevo
    registro.save(using='docLaruex')
    
    # creamos un nuevo registro vacio
    estadoProgramado = EstadoTareas.objects.using("docLaruex").filter(id=1)[0]
    nuevoRegistro = RegistroTareaProgramada(id_tarea_programada=tarea, fecha_programada=proximaFecha, fecha=None, empleado=None,conforme=None, observaciones=None, estado=estadoProgramado )
    nuevoRegistro.save(using='docLaruex')

    # actualizamos los datos de la tarea
    tarea.fecha_ultimo_mantenimiento = fechaRealizado
    tarea.fecha_proximo_mantenimiento = proximaFecha
    tarea.save(using='docLaruex')

    return redirect('docLaruex:docLaruexVerTarea', id=request.POST.get("tareaProgramada"))



@login_required
def verHistorico(request, id_historico):
    return redirect('docLaruex:docLaruexTareas')

'''
form fiels de django
CharField: Campo de texto para cadenas de caracteres.
IntegerField: Campo numérico entero.
FloatField: Campo numérico de punto flotante.
DecimalField: Campo numérico decimal.
BooleanField: Campo booleano para representar valores verdadero/falso.
DateField: Campo de fecha.
TimeField: Campo de tiempo.
DateTimeField: Campo de fecha y tiempo.
EmailField: Campo para direcciones de correo electrónico.
URLField: Campo para URLs.
FileField: Campo para subir archivos.
ImageField: Campo para subir imágenes.
ChoiceField: Campo para selección única de opciones.
MultipleChoiceField: Campo para selección múltiple de opciones.
ModelChoiceField: Campo para selección de un objeto de modelo.
ModelMultipleChoiceField: Campo para selección múltiple de objetos de modelo.
'''

def crearFieldTipo(tipo):
    if tipo == "datetime":
        return forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    elif tipo == "date":
        return forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'})
        )
    elif tipo == "time":
        return forms.TimeField(input_formats=['%H:%M'],widget=forms.TimeInput(attrs={'type': 'time', 'class':'form-control'}))
    elif tipo == "string":
        return forms.CharField(widget=forms.TextInput(attrs={'type': 'text', 'class':'form-control'}))
    elif tipo == "boolean":
        return forms.BooleanField(widget=forms.CheckboxInput(attrs={'type': 'checkbox', 'class':'form-check-input'}))
    elif tipo == "integer":
        return forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number', 'placeholder':'15', 'class':'form-control'}))
    elif tipo == "float":
        return forms.FloatField(widget=forms.NumberInput(attrs={'type': 'number', 'step':'0.01', 'placeholder':'15.23', 'class':'form-control'}))
    elif tipo == "select":
        return forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}))
    elif tipo == "file":
        return forms.FileField(widget=forms.FileInput(attrs={'class':'form-control-file'}))
    else:
        print("tipo no reconocido:", tipo)
        return forms.CharField()


def form_from_json(json_data):
    form = forms.Form()
    for field in json_data:
        form.fields[field] = crearFieldTipo(json_data[field])
    return form


'''-------------------------------------------
                                Módulo: DatosEquiposUbicaciones

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquiposUbicaciones(request):
    equipos = Equipo.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'fabricante__nombre', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio','modelo', 'id__padre__nombre')  

    ubicaciones = Ubicaciones.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id)).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo',
     'id__creador', 'id__id_estado', 'id__icono', 'alias', 'tipo_ubicacion__nombre', 'id__padre__nombre')

    objetos = list(equipos) + list(ubicaciones)                
    
    return JsonResponse(list(objetos), safe=False)

'''-------------------------------------------
                                Módulo: DatosEquiposUbicaciones

- Descripción: 


- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def DatosEquiposUbicacionesFiltro(request, tipo):
    
    tipoFiltrado = tipo.split(',')
    equipos = Equipo.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id__tipo__in=tipoFiltrado).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'fabricante__nombre', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio','modelo', 'id__padre__nombre')  
    print('\033[91m'+'equipos: ' + '\033[92m', equipos)
    ubicaciones = Ubicaciones.objects.using('docLaruex').filter(id__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id__tipo__in=tipoFiltrado).order_by('-id').values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','id__creador', 'id__id_estado', 'id__icono', 'alias', 'tipo_ubicacion__nombre', 'id__padre__nombre')
    print('\033[91m'+'ubicaciones: ' + '\033[92m', ubicaciones)
    objetos = list(equipos) + list(ubicaciones)                
    
    return JsonResponse(list(objetos), safe=False)


def formatosDatosFiltrados(request, procedimiento):
    formatosFiltrados = []
    # Si procedimiento es 0, no se ha seleccionado ningún procedimiento, por lo que no se filtra por procedimiento
    if procedimiento != 0:
        # Obtiene los formatos de los datos filtrados
        formatosFiltrados = Formatos.objects.using("docLaruex").filter(id_doc__padre=procedimiento, plantilla=1).values('id_doc', 'id_doc__id', 'id_doc__nombre', 'id_doc__padre', 'version', 'titulo')
    return JsonResponse(list(formatosFiltrados), safe=False)


'''------------------------------------------
La función accesoDenegado, renderiza la plantilla "docLaruex/accesoDenegado.html" cuando el usuario no tiene los permisos necesarios para acceder a una determinada funcionalidad.

- Precondiciones:
    Debe haber recibido una solicitud de "request"

- Postcondiciones:
    devuelve una respuesta renderizada utilizando la función "render" de Django.
-------------------------------------------'''
def tareas(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Renderiza la plantilla accesoDenegado.html con los elementos del menú
    return render(request, 'docLaruex/listadoTareas.html', {"itemsMenu": itemsMenu})

'''------------------------------------------
                                Módulo: datosTareas

- Descripción: 
Este módulo es utilizado para obtener una lista de tareas en el sistema que pueden ser asociados a una habilitación específica. Retorna una lista de objetos JSON con la información de las tareas.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosTareas(request):
        tareas = TareasProgramadas.objects.using("docLaruex").filter(id_objeto__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id_evento__estado__id=2).values( 'id', 'id_evento', 'id_evento__id', 'id_evento__nombre', 'id_evento__tipo_evento__nombre', 'fecha_proximo_mantenimiento', 'fecha_ultimo_mantenimiento', 'fecha_inicial','id_objeto', 'id_objeto__id', 'id_objeto__nombre', 'id_objeto__tipo')
        return JsonResponse(list(tareas), safe=False)


'''------------------------------------------
                                Módulo: verTarea

- Descripción: 
Este módulo se encarga de mostrar la información detallada de una tarea seleccionado por el usuario. Se utiliza para ver los datos de la tarea en pantalla.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado una tarea existente en la base de datos para visualizar su información.

- Postcondiciones:
Se debe mostrar la información detallada del tarea seleccionado.
El tarea debe existir en la base de datos.

-------------------------------------------'''   
@login_required
def verTarea(request, id):
    
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    tarea = TareasProgramadas.objects.using('docLaruex').filter(id=id).values('id','id_evento__tipo_evento__id','id_evento__nombre','id_evento__tipo_evento__nombre', 'id_objeto', 'id_objeto__id', 'fecha_proximo_mantenimiento', 'fecha_inicial','fecha_ultimo_mantenimiento','observaciones', 'id_evento__datos', 'id_evento__id', 'id_evento', 'id_evento__tipo_periodicidad__periodicidad','id_evento__periodicidad__cantidad', 'id_evento__periodicidad__unidad', 'id_evento__procedimiento_asociado__id_doc__nombre', 'id_evento__procedimiento_asociado__id_doc', 'id_evento__procedimiento_asociado__id_doc__id', 'id_evento__procedimiento_asociado__id_doc__id_habilitacion', 'id_evento__formato_asociado','id_evento__formato_asociado__id_doc__id', 'id_evento__formato_asociado__id_doc__nombre', 'id_evento__formato_asociado__id_doc__id_habilitacion', 'id_evento__formato_asociado__titulo', 'id_evento__formato_asociado__version','id_evento__estado', 'id_evento__estado__id', 'id_evento__estado__nombre' )[0]

    eventos = Eventos.objects.using("docLaruex").values('id', 'nombre','tipo_evento__nombre', 'procedimiento_asociado__id_doc__nombre', 'tipo_periodicidad__periodicidad', 'periodicidad__cantidad', 'periodicidad__unidad')
    registro =  RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=id).order_by('-id').values('id','empleado', 'fecha', 'fecha_programada', 'conforme', 'datos', 'observaciones', 'estado','estado__id','estado__nombre','id_tarea_programada', 'estado__nombre')[0]

    if Equipo.objects.using('docLaruex').filter(id=tarea['id_objeto__id']).exists():
        objeto = Equipo.objects.using('docLaruex').filter(id=tarea['id_objeto__id']).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','tipo_equipo__nombre', 'cod_laruex', 'id__creador', 'id__id_estado', 'cod_uex', 'id__icono', 'fabricante', 'fabricante__nombre', 'num_serie', 'descripcion','fecha_alta','fecha_baja', 'precio','modelo', 'id__padre__nombre')[0]
    else:
        objeto = Ubicaciones.objects.using('docLaruex').filter(id=tarea['id_objeto__id']).values('id', 'id__padre','id__nombre', 'id__ruta', 'id__fecha_subida','id__tipo','id__creador', 'id__id_estado', 'id__icono', 'alias', 'tipo_ubicacion__nombre', 'id__padre__nombre')[0]

    esquemaNuevo =  json.loads(tarea["id_evento__datos"])

    return render(request,"docLaruex/tarea.html",{"itemsMenu": itemsMenu, "tarea": tarea, "administrador": esAdministrador(request.user.id), "objeto": objeto, "registro":registro, 'form':form_from_json(esquemaNuevo), "eventos":eventos})


@login_required
def editarTarea(request, id):
    tarea = TareasProgramadas.objects.using('docLaruex').filter(id=id)[0]
    eventos = Eventos.objects.using("docLaruex").values('id', 'nombre','tipo_evento__nombre', 'procedimiento_asociado__id_doc__nombre', 'tipo_periodicidad__periodicidad', 'periodicidad__cantidad', 'periodicidad__unidad')

    itemsMenu = MenuBar.objects.using("docLaruex").values()

    if request.method == 'POST':
        evento = Eventos.objects.using('docLaruex').filter(id=request.POST['evento'])[0]
        tarea.id_evento = evento
        tarea.fecha_inicial = request.POST['nuevaFechaInicial']
        tarea.observaciones = request.POST['nuevasObservaciones']
        tarea.save(using="docLaruex")
        return redirect('docLaruex:docLaruexVerTarea', id=id)
    else:
        return render(
            request,
            "docLaruex/editarTarea.html",
            {"itemsMenu": itemsMenu, "tarea": tarea, "eventos":eventos})
    

def editarRegistroTarea(request, id):
    registroTareaProgramada = RegistroTareaProgramada.objects.using('docLaruex').filter(id=id)[0]
    empleados = AuthUser.objects.using("docLaruex").values('id', 'first_name', 'last_name')
    tarea = registroTareaProgramada.id_tarea_programada
    estados = EstadoTareas.objects.using("docLaruex").values('id', 'nombre')

    itemsMenu = MenuBar.objects.using("docLaruex").values()

    if request.method == 'POST':
        registroTareaProgramada.empleado = AuthUser.objects.using('docLaruex').filter(id=request.POST['nuevoEmpleado'])[0]
        registroTareaProgramada.fecha = request.POST['nuevaFechaUltimoMantenimiento']
        if tarea.id_evento.tipo_periodicidad.id == 1:
            fecha_tarea = datetime.strptime(registroTareaProgramada.fecha , '%Y-%m-%dT%H:%M')
            print('\033[91m'+'fecha_tarea: ' + '\033[92m', type(request.POST['nuevaFechaUltimoMantenimiento']))
            
            proximaFecha = calcularPeriodicidad(tarea.id_evento.id, fecha_tarea, False)
            registroTareaProgramada.fecha_programada = proximaFecha
            tarea.fecha_proximo_mantenimiento = proximaFecha

        registroTareaProgramada.conforme = request.POST['nuevoConforme']
        registroTareaProgramada.datos = request.POST['nuevosDatos']
        registroTareaProgramada.observaciones = request.POST['nuevasObservaciones']
        registroTareaProgramada.estado = EstadoTareas.objects.using('docLaruex').filter(id=request.POST['nuevoEstado'])[0]
        registroTareaProgramada.save(using="docLaruex")

        tarea.fecha_fecha_ultimo_mantenimiento = request.POST['nuevaFechaUltimoMantenimiento']
        tarea.save(using="docLaruex")
        return redirect('docLaruex:docLaruexReportRegistroTarea', id=id)
    else:
        return render(
            request,
            "docLaruex/editarRegistroTarea.html",
            {"itemsMenu": itemsMenu, "registroTareaProgramada": registroTareaProgramada, "empleados":empleados, "estados":estados})
'''------------------------------------------


                                Módulo: datosRegistroTareas

- Descripción: 
Este módulo es utilizado para obtener una lista de registros de una tarea concreta en el sistema. Retorna una lista de objetos JSON con la información de las tareas.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosRegistroTareas(request, id_tarea):
    tarea = TareasProgramadas.objects.using('docLaruex').filter(id=id_tarea)[0]

    registrosTarea = RegistroTareaProgramada.objects.using("docLaruex").filter(id_tarea_programada=tarea).values( 'id','empleado', 'fecha', 'fecha_programada', 'conforme', 'datos', 'observaciones', 'estado','estado__id','id_tarea_programada', 'id_formato', 'id_formato__id_doc','id_formato__id_doc__id')
    return JsonResponse(list(registrosTarea), safe=False)

'''------------------------------------------
                                Módulo: eliminarTarea

- Descripción:  
Este módulo se encarga de eliminar una tarea existente en la base de datos. Se utiliza para borrar los datos de una tarea que ya no es necesario.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado una tarea existente en la base de datos para eliminar.

- Postcondiciones:
El proveedor debe ser eliminado de la base de datos.
Se debe mostrar la página de listado de proveedores sin el proveedor eliminado.

-------------------------------------------''' 
@login_required
def eliminarTarea(request, id):
    
    tarea = TareasProgramadas.objects.using('docLaruex').filter(id=id)[0]
    if RegistroTareaProgramada.objects.using('docLaruex').filter(id_tarea_programada=tarea).exists():
        RegistroTareaProgramada.objects.using('docLaruex').filter(id_tarea_programada=tarea).delete()
    
    tarea.delete(using="docLaruex")
    return redirect('docLaruex:docLaruexTareas')

'''------------------------------------------
                                Módulo: cancelarRegistroTarea

- Descripción:  
Este módulo se encarga de cancelar un registro de tarea que se encuentra programado en la base de datos. 

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un registro existente en la base de datos para eliminar.

- Postcondiciones:
El registro actual se modifica a cancelado.
Se programa un nuevo registro en estado programado (Si el usuario así lo desea).

-------------------------------------------''' 
@login_required
def cancelarRegistroTarea(request):
    id_registro = request.POST['id_registro']
    id_tarea = TareasProgramadas.objects.using('docLaruex').filter(id=request.POST['id_tarea'] )[0]

    # ponemos a cancelado el registro actual e indicamos el motivo y el usuario que lo cancela
    registroActual = RegistroTareaProgramada.objects.using('docLaruex').filter(id=id_registro)[0]
    registroActual.estado = EstadoTareas.objects.using('docLaruex').filter(id=5)[0]
    registroActual.empleado = AuthUser.objects.using('docLaruex').filter(id=request.user.id)[0]
    registroActual.observaciones = request.POST['motivoCancelacion']
    registroActual.fecha = datetime.now()
    registroActual.save(using="docLaruex")

    # programamos un nuevo registro si el usuario así lo desea
    if request.POST['programarSiguiente'] == '1':
        fecha_programada = request.POST['FechaReprogramada']
        estadoProgramado = EstadoTareas.objects.using("docLaruex").filter(id=1)[0]
        nuevoRegistro = RegistroTareaProgramada(id_tarea_programada=id_tarea, fecha_programada=fecha_programada, fecha=None, empleado=None,conforme=None, observaciones=None, estado=estadoProgramado )
        nuevoRegistro.save(using='docLaruex')

    return redirect('docLaruex:docLaruexTareas')


'''------------------------------------------
                                Módulo: cancelarRegistroTarea

- Descripción:  
Este módulo se encarga de eliminar un registro un registro de tarea que se encuentra en la base de datos, siempre que este no sea un registro que se encuentra en estado programado. 

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado un registro existente en la base de datos para eliminar.

- Postcondiciones:
El registro actual se elimina.
Nos muestra la tarea a la que pertenece el registro.

-------------------------------------------''' 
@login_required
def eliminarRegistroTarea(request, id):
    # ponemos a cancelado el registro actual e indicamos el motivo y el usuario que lo cancela
    registroActual = RegistroTareaProgramada.objects.using('docLaruex').filter(id=id)[0]
    
    tarea = registroActual.id_tarea_programada.id
    if registroActual.estado != EstadoTareas.objects.using('docLaruex').filter(id=1)[0] and registroActual.estado != EstadoTareas.objects.using('docLaruex').filter(id=6)[0]:
        registroActual.delete(using="docLaruex")
        
    return redirect('docLaruex:docLaruexVerTarea', id=tarea)
 
'''-------------------------------------------
                                Módulo: agregarArchivo2

- Descripción: 
Agrega un archivo a la base de datos y almacenarlo en el servidor en la ubicación correspondiente. La función recibe una solicitud HTTP (request) que contiene los detalles del archivo que se va a agregar, incluyendo el tipo de archivo, su nombre, su estado y su ubicación.

- Precondiciones:
El usuario debe estar autenticado en el sistema.
El formulario de agregación de archivo debe haber sido enviado por el usuario.

- Postcondiciones:
El archivo debe ser agregado correctamente a la base de datos.
El archivo debe ser almacenado en el servidor en la ubicación especificada.
Si el archivo es editable, la versión editable también debe ser almacenada en el servidor.

-------------------------------------------'''
@login_required
def agregarArchivo2(request):

    ficheroAdjunto = "ficheroAdjunto"+request.POST.get("tipoObjeto")
    ficheroAdjuntoEditable = "ficheroAdjunto"+request.POST.get("tipoObjeto")+"Editable"

    icono = '<i class="fa-duotone fa-file-invoice fa-2x"></i>'
    creador = AuthUser.objects.using('docLaruex').filter(id=request.user.id)[0]
    estado = Estado.objects.using('docLaruex').filter(id=1)[0]
    habilitacion = Habilitaciones.objects.using(
        'docLaruex').filter(id=request.POST.get("habilitacion"))[0]
    padre = None
    # comprueba si ese objeto hereda de otro y crea el objeto en la tabla Objeto
    if 'padre' in request.POST:
        padre = ObjetoPadre.objects.using("docLaruex").filter(id=request.POST.get("padre"))[0]
        
    nuevoObjeto = Objeto(nombre=request.POST.get("nombreObjeto"), fecha_subida=datetime.now(
    ), tipo=request.POST.get("tipoObjeto"), creador=creador, id_estado=estado, id_habilitacion=habilitacion, icono=icono, padre=padre)
    nuevoObjeto.save(using='docLaruex')

    if request.FILES.get(ficheroAdjunto) is not None:
        ruta = settings.MEDIA_ROOT + 'archivos/' + nuevoObjeto.tipo + '/' + str(nuevoObjeto.id) + '.' + request.FILES[ficheroAdjunto].name.split('.')[-1]   
        subirDocumento(request.FILES[ficheroAdjunto], ruta)
        nuevoObjeto.ruta = str(nuevoObjeto.id) + '.' + request.FILES[ficheroAdjunto].name.split('.')[-1]
    if request.FILES.get(ficheroAdjuntoEditable):
        ruta_editable = settings.MEDIA_ROOT + 'archivos/' + nuevoObjeto.tipo + '/' + str(nuevoObjeto.id) + '_edit.' + request.FILES[ficheroAdjuntoEditable].name.split('.')[-1]
        subirDocumento(request.FILES[ficheroAdjuntoEditable], ruta_editable)
        nuevoObjeto.ruta_editable = str(nuevoObjeto.id) + '_edit.' + request.FILES[ficheroAdjuntoEditable].name.split('.')[-1]
    nuevoObjeto.save(using='docLaruex')




    agregarFormato(request, nuevoObjeto)





'''-------------------------------------------
                                Módulo: reportRegistroTarea

- Descripción: 
Permite eliminar una asociación entre dos objetos de la base de datos. id_actual es el objeto que estamos visualizando, mientras que id_objeto_eliminar es el objeto de la tabla de referencias que deseamos eliminar la asociación.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
@login_required
def reportRegistroTarea(request,id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    
    registrosTarea = RegistroTareaProgramada.objects.using("docLaruex").filter(id=id)[0]
    print("::::::::::::::::", registrosTarea)
    tarea = TareasProgramadas.objects.using('docLaruex').filter(id=registrosTarea.id_tarea_programada.id)[0]
    evento = Eventos.objects.using('docLaruex').filter(id=tarea.id_evento.id)[0]
    
    equipo = None
    datos = None
    if Equipo.objects.using('docLaruex').filter(id=tarea.id_objeto.id).exists():
        equipo = Equipo.objects.using('docLaruex').filter(id=tarea.id_objeto.id)[0]
    if registrosTarea.datos:
        datos = json.loads(registrosTarea.datos.replace("'",'"'))
        print(datos)
    return render(request, "docLaruex/reportRegistroTarea.html",{"itemsMenu": itemsMenu, "tarea": tarea, "registrosTarea":registrosTarea, "equipo": equipo, "datos":datos, "evento":evento})


'''------------------------------------------
La función accesoDenegado, renderiza la plantilla "docLaruex/accesoDenegado.html" cuando el usuario no tiene los permisos necesarios para acceder a una determinada funcionalidad.

- Precondiciones:
    Debe haber recibido una solicitud de "request"

- Postcondiciones:
    devuelve una respuesta renderizada utilizando la función "render" de Django.
-------------------------------------------'''
def tareasProximas(request):
    # Obtiene los elementos del menú desde la base de datos
    itemsMenu = MenuBar.objects.using("docLaruex").values()
    # Renderiza la plantilla accesoDenegado.html con los elementos del menú
    return render(request, 'docLaruex/listadoTareasProximas.html', {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: datosTareasProximas

- Descripción: 
Este módulo es utilizado para obtener una lista de tareas en el sistema que pueden ser asociados a una habilitación específica. Retorna una lista de objetos JSON con la información de las tareas, cuyo estado es avisado, programado y caducado.

- Precondiciones:
El usuario debe estar autenticado en el sistema.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosTareasProximas(request):
    estados = [1, 2, 4]
    tareasFiltradas = []

    if TareasProgramadas.objects.using("docLaruex").order_by('fecha_proximo_mantenimiento').filter(id_objeto__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id_evento__estado__id=2).exists():

        tareas = TareasProgramadas.objects.using("docLaruex").order_by('fecha_proximo_mantenimiento').filter(id_objeto__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id_evento__estado__id=2).values('id', 'id_evento', 'id_evento__id', 'id_evento__nombre', 'id_evento__tipo_evento__nombre', 'fecha_proximo_mantenimiento', 'fecha_ultimo_mantenimiento', 'fecha_inicial','id_objeto', 'id_objeto__id', 'id_objeto__nombre', 'id_objeto__tipo')
        
        for t in tareas:
            if RegistroTareaProgramada.objects.using("docLaruex").order_by('id').filter(id_tarea_programada=t['id'], fecha_programada=t['fecha_proximo_mantenimiento'], estado__id__in=estados).exists():
                registro = RegistroTareaProgramada.objects.using("docLaruex").order_by('id').filter(id_tarea_programada=t['id'], fecha_programada=t['fecha_proximo_mantenimiento'], estado__id__in=estados)[0]
                if registro:
                    t['registro'] = {
                        'id': registro.id,
                        'fecha_programada': registro.fecha_programada,
                        'fecha': registro.fecha,
                        'conforme': registro.conforme,
                        'observaciones': registro.observaciones,
                        'datos': registro.datos,
                        'id_tarea_programada': registro.id_tarea_programada.id,
                        'id_tarea_programada_id': registro.id_tarea_programada.id,
                        'estado': {
                            'id': registro.estado.id,
                            'nombre': registro.estado.nombre,
                        }
                    } 
                    tareasFiltradas.append(t)
        

    return JsonResponse(list(tareasFiltradas), safe=False)



'''------------------------------------------
                                Módulo: verMantenimientosAsociados

- Descripción: 
Este módulo se encarga de mostrar la información de los mantenimientos asociados a una ubicación o a un equipo.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado una ubicacion u equipo existente en la base de datos para visualizar su información.

- Postcondiciones:
Se debe mostrar la información detallada del objeto seleccionado.
El objeto debe existir debe existir en la base de datos.
Deben existir mantenimientos asociados en la base de datos de lo contrario mostrá una página que indica que no existen.
-------------------------------------------'''   
@login_required
def verMantenimientosAsociados(request, id):
    itemsMenu = MenuBar.objects.using("docLaruex").values()

    if TareasProgramadas.objects.using("docLaruex").filter(id_objeto=id).exists():
        
        objeto = Objeto.objects.using('docLaruex').filter(id=id)[0]

        return render(request,"docLaruex/listaMantenimientosAsociados.html",{"itemsMenu": itemsMenu, "objeto":objeto, "administrador": esAdministrador(request.user.id)})
    else:
        return render(request,"docLaruex/404_sinMantenimientos.html", {"itemsMenu": itemsMenu})


'''------------------------------------------
                                Módulo: datosMantenimientosAsociados

- Descripción: 
Este módulo es utilizado para obtener una lista de tareas en el sistema que pueden ser asociados a una habilitación específica. Retorna una lista de objetos JSON con la información de las tareas.

- Precondiciones:
 
El usuario debe estar autenticado en el sistema.

- Postcondiciones:

Se retorna una lista de objetos JSON con la información de los usuarios.

-------------------------------------------'''       
@login_required
def datosMantenimientosAsociados(request,id):
        mantenimientos = TareasProgramadas.objects.using("docLaruex").filter(id_objeto=id,id_objeto__id_habilitacion__in=comprobarHabilitaciones(request.user.id), id_evento__estado__id=2).values( 'id', 'id_evento', 'id_evento__id', 'id_evento__nombre', 'id_evento__tipo_evento__nombre', 'id_evento__procedimiento_asociado', 'id_evento__procedimiento_asociado__id_doc__nombre', 'fecha_proximo_mantenimiento', 'fecha_ultimo_mantenimiento', 'fecha_inicial','id_objeto', 'id_objeto__id', 'id_objeto__nombre', 'id_objeto__tipo', 'id_evento__periodicidad__id', 'id_evento__periodicidad__cantidad', 'id_evento__periodicidad__unidad')
        return JsonResponse(list(mantenimientos), safe=False)