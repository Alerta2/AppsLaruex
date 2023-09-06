import glob
import os
from django import forms
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.http import FileResponse, Http404, HttpResponse
from django.utils.translation import templatize
from public.models import *
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from public.forms import InformeForm
import requests

import random
import hashlib
from hashlib import md5

import json

from .forms import formularioNoticia, formularioInvestigacion, formularioMedida, formularioCaptcha

def homePublic(request):
    sliders= WeblaruexSliders.objects.filter(Q(pagina__icontains="principal")| Q(pagina__icontains="home"))
    empleados= list(WeblaruexEmpleados.objects.all())
    random.shuffle(empleados)
    noticias= WeblaruexNoticias.objects.filter(visible=1).order_by('-fecha')[:3]
    medidas = WeblaruexMedidas.objects.using('default').values()
    responsables= WeblaruexResponsables.objects.filter(apartado__contains="home")

    return render(
        request,
        "public/index.html",
        {"sliders": sliders, "noticias":noticias, "empleados":empleados, "responsables": responsables, "site_key":settings.RECAPTCHA_SITE_KEY, "medidas":medidas}
    )

def homePublicSeccion(request, seccion):
    sliders= WeblaruexSliders.objects.filter(Q(pagina__icontains="principal")| Q(pagina__icontains="home"))
    empleados= list(WeblaruexEmpleados.objects.all())
    random.shuffle(empleados)
    noticias= WeblaruexNoticias.objects.filter(visible=1).order_by('-fecha')[:3]  
    responsables= WeblaruexResponsables.objects.filter(apartado__contains="home")
    return render(
        request,
        "public/index.html",
        {"sliders": sliders, "seccion":seccion, "noticias":noticias, "empleados":empleados, "responsables": responsables}
    )

def laboratorios(request):
    sliders= WeblaruexSliders.objects.filter(pagina__icontains="laboratorios")
    responsables= WeblaruexResponsables.objects.filter(apartado__contains="laboratorios")
    investigaciones= WeblaruexInvestigaciones.objects.filter(seccion="LABORATORIOS")
    tesis = investigaciones.filter(tipo="Tesis").order_by('-fecha','-id')[0]
    publicacion = investigaciones.filter(tipo="Publicación").order_by('-fecha','-id')[0]
    proyecto = investigaciones.filter(tipo="Proyecto").order_by('-fecha','-id')[0]
    acreditaciones = WeblaruexAcreditaciones.objects.filter(seccion="laboratorios")
    return render(
        request,
        "public/laboratorios.html",
        {"apartado": 'Laboratorios', "sliders": sliders, "responsables": responsables, "tesis": tesis,"publicacion": publicacion, "proyecto": proyecto, "acreditaciones":acreditaciones}
    )

def laboratoriosCompuesto(request, seccion):
    sliders= WeblaruexSliders.objects.filter(pagina__icontains="laboratorios")
    responsables= WeblaruexResponsables.objects.filter(apartado__icontains="laboratorios")
    investigaciones= WeblaruexInvestigaciones.objects.filter(seccion="LABORATORIOS")
    tesis = investigaciones.filter(tipo="Tesis").order_by('-fecha','-id')[0]
    publicacion = investigaciones.filter(tipo="Publicación").order_by('-fecha','-id')[0]
    proyecto = investigaciones.filter(tipo="Proyecto").order_by('-fecha','-id')[0]
    return render(
        request,
        "public/laboratorios.html",
        {"apartado": 'Laboratorios', "sliders": sliders, "seccion":seccion, "responsables": responsables, "tesis": tesis,"publicacion": publicacion, "proyecto": proyecto}
    )


def redes(request):
    sliders= WeblaruexSliders.objects.filter(Q(pagina__icontains="alerta2")| Q(pagina__icontains="redes"))
    responsables= WeblaruexResponsables.objects.filter(apartado__contains="redes")
    investigaciones= WeblaruexInvestigaciones.objects.filter(seccion="REDES")
    tesis = investigaciones.filter(tipo="Tesis").order_by('-fecha','-id')[0]
    publicacion = investigaciones.filter(tipo="Publicación").order_by('-fecha','-id')[0]
    proyecto = investigaciones.filter(tipo="Proyecto").order_by('-fecha','-id')[0]
    acreditaciones = WeblaruexAcreditaciones.objects.filter(seccion="redes")

    data = [
        {"nombre":"Almaraz", "red":"RARE", "lat":"39.81", "lon":"-5.68"},
        {"nombre":"Caceres", "red":"RARE", "lat":"39.48", "lon":"-6.35"},
        {"nombre":"Casas de Miravete", "red":"RARE", "lat":"39.73", "lon":"-5.74"},
        {"nombre":"Fregenal de la Sierra", "red":"RARE", "lat":"38.17", "lon":"-6.66"},
        {"nombre":"Castelo Branco", "red":"RARE", "lat":"39.82", "lon":"-7.51"},
        {"nombre":"Navalmoral de la Mata", "red":"RARE", "lat":"39.90", "lon":"-5.54"},
        {"nombre":"Romangordo", "red":"RARE", "lat":"39.74", "lon":"-5.70"},
        {"nombre":"Saucedilla", "red":"RARE", "lat":"39.86", "lon":"-5.68"},
        {"nombre":"Serrejon", "red":"RARE", "lat":"39.82", "lon":"-5.80"},
        {"nombre":"Talayuela", "red":"RARE", "lat":"39.95", "lon":"-5.60"},
        {"nombre":"Valdecañas monitor de aguas", "red":"RARE", "lat":"39.83", "lon":"-5.45"},
        {"nombre":"Arrocampo monitor de aguas", "red":"RARE", "lat":"39.78", "lon":"-5.74"},
        {"nombre":"Estacion piloto: SAU", "red":"RARE", "lat":"39.86", "lon":"-5.68"},
        {"nombre":"Azuaga", "red":"RARE", "lat":"38.26", "lon":"-5.69"},
        {"nombre":"Portalegre", "red":"RARE", "lat":"39.27", "lon":"-7.43"},
        {"nombre":"Evora", "red":"RARE", "lat":"38.55", "lon":"-7.92"},
        {"nombre":"Atalaya", "red":"RARE", "lat":"39.60", "lon":"-7.22"},
        {"nombre":"Badajoz Monitor de Aguas", "red":"RARE", "lat":"38.85", "lon":"-7.04"},
        {"nombre":"Castuera", "red":"SPIDA", "lat":"38.72", "lon":"-5.55"},
        {"nombre":"Fregenal de la Sierra", "red":"SPIDA", "lat":"38.18", "lon":"-6.66"},
        {"nombre":"Fuente de Cantos", "red":"SPIDA", "lat":"38.21", "lon":"-6.31"},
        {"nombre":"Garganta la Olla", "red":"SPIDA", "lat":"40.11", "lon":"-5.79"},
        {"nombre":"Guadalupe", "red":"SPIDA", "lat":"39.46", "lon":"-5.33"},
        {"nombre":"Guijo de Granadilla", "red":"SPIDA", "lat":"40.19", "lon":"-6.17"},
        {"nombre":"Hervas", "red":"SPIDA", "lat":"40.27", "lon":"-5.86"},
        {"nombre":"Hoyos", "red":"SPIDA", "lat":"40.17", "lon":"-6.72"},
        {"nombre":"Jaraicejo", "red":"SPIDA", "lat":"39.67", "lon":"-5.80"},
        {"nombre":"Monesterio", "red":"SPIDA", "lat":"38.08", "lon":"-6.27"},
        {"nombre":"Montehermoso", "red":"SPIDA", "lat":"40.08", "lon":"-6.34"},
        {"nombre":"Navalvillar de pela", "red":"SPIDA", "lat":"39.10", "lon":"-5.46"},
        {"nombre":"Muñomoral", "red":"SPIDA", "lat":"40.41", "lon":"-6.24"},
        {"nombre":"Peraleda del Zaucejo", "red":"SPIDA", "lat":"38.48", "lon":"-5.58"},
        {"nombre":"Puebla de Obando", "red":"SPIDA", "lat":"39.18", "lon":"-6.60"},
        {"nombre":"Puerto del Rey", "red":"SPIDA", "lat":"39.45", "lon":"-5.02"},
        {"nombre":"Valverde del Fresno", "red":"SPIDA", "lat":"40.21", "lon":"-6.90"},
        {"nombre":"Villafranca de los Barros", "red":"SPIDA", "lat":"38.55", "lon":"-6.31"},
        {"nombre":"Villanueva del Fresno", "red":"SPIDA", "lat":"38.37", "lon":"-7.16"},
        {"nombre":"Zarza la Mayor", "red":"SPIDA", "lat":"39.87", "lon":"-6.86"},
        {"nombre":"Zorita", "red":"SPIDA", "lat":"39.28", "lon":"-5.71"},
    ];

    return render(
        request,
        "public/redes.html",
        {"apartado": 'Redes', "sliders": sliders, "estaciones":data, "responsables": responsables, "tesis": tesis,"publicacion": publicacion, "proyecto": proyecto, "acreditaciones":acreditaciones}
    )


def rare(request):
    return render(
        request,
        "public/parts/rare.html",
    )
def spida(request):
    return render(
        request,
        "public/parts/spida.html",
    )
def redesCompuesto(request, seccion):
    sliders= WeblaruexSliders.objects.filter(pagina="alerta2")
    responsables= WeblaruexResponsables.objects.filter(apartado="redes")
    investigaciones= WeblaruexInvestigaciones.objects.filter(seccion="REDES")
    tesis = investigaciones.filter(tipo="Tesis").order_by('-fecha','-id')[0]
    publicacion = investigaciones.filter(tipo="Publicación").order_by('-fecha','-id')[0]
    proyecto = investigaciones.filter(tipo="Proyecto").order_by('-fecha','-id')[0]

    data = [
        {"nombre":"Almaraz", "red":"RARE", "lat":"39.81", "lon":"-5.68"},
        {"nombre":"Caceres", "red":"RARE", "lat":"39.48", "lon":"-6.35"},
        {"nombre":"Casas de Miravete", "red":"RARE", "lat":"39.73", "lon":"-5.74"},
        {"nombre":"Fregenal de la Sierra", "red":"RARE", "lat":"38.17", "lon":"-6.66"},
        {"nombre":"Castelo Branco", "red":"RARE", "lat":"39.82", "lon":"-7.51"},
        {"nombre":"Navalmoral de la Mata", "red":"RARE", "lat":"39.90", "lon":"-5.54"},
        {"nombre":"Romangordo", "red":"RARE", "lat":"39.74", "lon":"-5.70"},
        {"nombre":"Saucedilla", "red":"RARE", "lat":"39.86", "lon":"-5.68"},
        {"nombre":"Serrejon", "red":"RARE", "lat":"39.82", "lon":"-5.80"},
        {"nombre":"Talayuela", "red":"RARE", "lat":"39.95", "lon":"-5.60"},
        {"nombre":"Valdecañas monitor de aguas", "red":"RARE", "lat":"39.83", "lon":"-5.45"},
        {"nombre":"Arrocampo monitor de aguas", "red":"RARE", "lat":"39.78", "lon":"-5.74"},
        {"nombre":"Estacion piloto: SAU", "red":"RARE", "lat":"39.86", "lon":"-5.68"},
        {"nombre":"Azuaga", "red":"RARE", "lat":"38.26", "lon":"-5.69"},
        {"nombre":"Portalegre", "red":"RARE", "lat":"39.27", "lon":"-7.43"},
        {"nombre":"Evora", "red":"RARE", "lat":"38.55", "lon":"-7.92"},
        {"nombre":"Atalaya", "red":"RARE", "lat":"39.60", "lon":"-7.22"},
        {"nombre":"Badajoz Monitor de Aguas", "red":"RARE", "lat":"38.85", "lon":"-7.04"},
        {"nombre":"Castuera", "red":"SPIDA", "lat":"38.72", "lon":"-5.55"},
        {"nombre":"Fregenal de la Sierra", "red":"SPIDA", "lat":"38.18", "lon":"-6.66"},
        {"nombre":"Fuente de Cantos", "red":"SPIDA", "lat":"38.21", "lon":"-6.31"},
        {"nombre":"Garganta la Olla", "red":"SPIDA", "lat":"40.11", "lon":"-5.79"},
        {"nombre":"Guadalupe", "red":"SPIDA", "lat":"39.46", "lon":"-5.33"},
        {"nombre":"Guijo de Granadilla", "red":"SPIDA", "lat":"40.19", "lon":"-6.17"},
        {"nombre":"Hervas", "red":"SPIDA", "lat":"40.27", "lon":"-5.86"},
        {"nombre":"Hoyos", "red":"SPIDA", "lat":"40.17", "lon":"-6.72"},
        {"nombre":"Jaraicejo", "red":"SPIDA", "lat":"39.67", "lon":"-5.80"},
        {"nombre":"Monesterio", "red":"SPIDA", "lat":"38.08", "lon":"-6.27"},
        {"nombre":"Montehermoso", "red":"SPIDA", "lat":"40.08", "lon":"-6.34"},
        {"nombre":"Navalvillar de pela", "red":"SPIDA", "lat":"39.10", "lon":"-5.46"},
        {"nombre":"Muñomoral", "red":"SPIDA", "lat":"40.41", "lon":"-6.24"},
        {"nombre":"Peraleda del Zaucejo", "red":"SPIDA", "lat":"38.48", "lon":"-5.58"},
        {"nombre":"Puebla de Obando", "red":"SPIDA", "lat":"39.18", "lon":"-6.60"},
        {"nombre":"Puerto del Rey", "red":"SPIDA", "lat":"39.45", "lon":"-5.02"},
        {"nombre":"Valverde del Fresno", "red":"SPIDA", "lat":"40.21", "lon":"-6.90"},
        {"nombre":"Villafranca de los Barros", "red":"SPIDA", "lat":"38.55", "lon":"-6.31"},
        {"nombre":"Villanueva del Fresno", "red":"SPIDA", "lat":"38.37", "lon":"-7.16"},
        {"nombre":"Zarza la Mayor", "red":"SPIDA", "lat":"39.87", "lon":"-6.86"},
        {"nombre":"Zorita", "red":"SPIDA", "lat":"39.28", "lon":"-5.71"},
    ];

    return render(
        request,
        "public/redes.html",
        {"apartado": 'Redes', "sliders": sliders, "seccion":seccion, "estaciones":data, "responsables": responsables, "tesis": tesis,"publicacion": publicacion, "proyecto": proyecto}
    )

def noticias(request):
    
    noticias= WeblaruexNoticias.objects.filter(visible=1).order_by('-fecha')
    paginator = Paginator(noticias, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categorias = CategoriasNoticias.objects.all()
    return render(
        request,
        "public/news.html",
        {"noticias": noticias, "page_obj": page_obj, "categorias": list(categorias)}
    )


def noticia(request, id):
    if WeblaruexNoticias.objects.using("default").filter(id=id).exists():
        noticia = WeblaruexNoticias.objects.using("default").filter(id=id).values()[0]
        # cambiar esta consulta a que filtre por id, modificar el template para mostrarla info que pasa
        return render(request,"public/new.html",{"noticia": noticia})
    else:
        return HttpResponse(request,"public/404.html")


@login_required
def noticiasPrivadas(request):
    
    noticias= WeblaruexNoticias.objects.filter(visible=0).order_by('-fecha')
    paginator = Paginator(noticias, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categorias = CategoriasNoticias.objects.all()
    return render(
        request,
        "public/news.html",
        {"noticias": noticias, "page_obj": page_obj, "categorias": list(categorias)}
    )




def noticiasFiltradas(request, categorias):
    if request.method == 'GET':
        categoriasFiltradas = categorias.split(',')
        noticias= WeblaruexNoticias.objects.filter(categoria_noticia__id__in=categoriasFiltradas, visible=1).order_by('-fecha')
        paginator = Paginator(noticias, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        categorias = CategoriasNoticias.objects.all()
        return render(request,"public/news.html",{"noticias": noticias, "page_obj": page_obj, "categorias": list(categorias)})
    return HttpResponse(request,"public/404.html")


def buscarNoticias(request):
    noticias= WeblaruexNoticias.objects.filter(Q(resumen__icontains = request.POST.get('busqueda'))|Q(titulo__icontains = request.POST.get('busqueda'))|Q(noticia__icontains = request.POST.get('busqueda')), visible=1).order_by('-fecha')
    paginator = Paginator(noticias, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "public/news.html",
        {"noticias": noticias, "page_obj": page_obj}
    )


def publicaciones(request):
    publicaciones= WeblaruexInvestigaciones.objects.order_by('-fecha')
    paginator = Paginator(publicaciones, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "public/idi.html",
        {"publicaciones": publicaciones, "page_obj": page_obj}
    )
    
    
def publicacionesLaboratorios(request):
    publicaciones= WeblaruexInvestigaciones.objects.filter(seccion="LABORATORIOS").order_by('-fecha')
    paginator = Paginator(publicaciones, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "public/idi.html",
        {"publicaciones": publicaciones, "page_obj": page_obj}
    )
    
def publicacionesRedes(request):
    publicaciones= WeblaruexInvestigaciones.objects.filter(seccion="REDES").order_by('-fecha')
    paginator = Paginator(publicaciones, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "public/idi.html",
        {"publicaciones": publicaciones, "page_obj": page_obj}
    )
    

def publicacion(request, id):
    if WeblaruexInvestigaciones.objects.using("default").filter(id=id).exists():
        publicacion = WeblaruexInvestigaciones.objects.using("default").filter(id=id).values()[0]
        return render(
            request,
            "public/idi-id.html",
            {"publicacion": publicacion}
        )
    else:
        raise Http404()


def editarPublicacion(request, id): 
    imagenInvestigacion = {
        "Intercomparación": "comparar.jpeg",
        "Proyecto": "contrato.png", 
        "Publicación": "periodicos.png",
        "Tesis": "lupa y libro.png",
    }
    publicacion = WeblaruexInvestigaciones.objects.using("default").filter(id=id)[0] 
    formResumenInvestigacionEditar = formularioInvestigacion(initial={'resumenInvestigacion': publicacion.resumen})
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Publicación editada correctamente."
    }


    if request.method == 'POST':
        alerta['mensaje'] = "La publicacion " + str(publicacion.id) + "-" + str(publicacion.titulo) + " se han modificado correctamente."


        publicacion.fecha = str(request.POST.get('yearInvestigacionEditar'))
        publicacion.titulo = request.POST.get('tituloInvestigacionEditar')

        if 'checkboxEditarInvestigacion' in request.POST:
            publicacion.seccion = request.POST.get('checkboxEditarInvestigacion')
        if 'categoriaInvestigacionEditar' in request.POST:
            publicacion.tipo = request.POST.get('categoriaInvestigacionEditar')
            publicacion.imagen = imagenInvestigacion[publicacion.tipo]

        if 'enlaceInvestigacionEditar' in request.POST and (request.POST.get('enlaceInvestigacionEditar') != "" or 'None'):
            publicacion.enlace = request.POST.get('enlaceInvestigacionEditar')
        publicacion.save(using="default")

        if publicacion.tipo == "Tesis":

            formResumenInvestigacionEditar = formularioInvestigacion(request.POST)
            if formResumenInvestigacionEditar.is_valid():
                resumen = formResumenInvestigacionEditar.cleaned_data['resumenInvestigacion']
                publicacion.resumen = resumen
            if 'autorInvestigacionEditar' in request.POST and (request.POST.get('autorInvestigacionEditar') != "" or 'None'):
                publicacion.autor = request.POST.get('autorInvestigacionEditar')
            publicacion.revista = None
            publicacion.localizacion = None
            publicacion.informacion = None
            publicacion.entidad_financiadora = None
            publicacion.fecha_final = None

        if publicacion.tipo == "Publicación":
            if 'revistaInvestigacionEditar' in request.POST and (request.POST.get('revistaInvestigacionEditar') != "" or 'None'):
                publicacion.revista = request.POST.get('revistaInvestigacionEditar')
            
            if 'localizacionInvestigacionEditar' in request.POST and (request.POST.get('localizacionInvestigacionEditar') != "" or 'None'):
                publicacion.localizacion = request.POST.get('localizacionInvestigacionEditar')
            publicacion.resumen = None
            publicacion.autor = None
            publicacion.informacion = None
            publicacion.entidad_financiadora = None
            publicacion.fecha_final = None

        if publicacion.tipo == "Proyecto":
            if 'infoAdicionalInvestigacionEditar' in request.POST and (request.POST.get('infoAdicionalInvestigacionEditar') != "" or 'None'):
                publicacion.informacion = request.POST.get('infoAdicionalInvestigacion')
            if 'entidadInvestigacionEditar' in request.POST and (request.POST.get('entidadInvestigacionEditar') != "" or 'None'):
                publicacion.entidad_financiadora = request.POST.get('entidadInvestigacionEditar')

            if 'lastYearInvestigacionEditar' in request.POST and (request.POST.get('lastYearInvestigacionEditar') != "" or 'None'):
                publicacion.fecha_final = str(request.POST.get('lastYearInvestigacionEditar'))
            publicacion.resumen = None
            publicacion.autor = None
            publicacion.revista = None
            publicacion.localizacion = None
        publicacion.save(using="default")

        request.session['alerta'] = alerta
        return redirect('public:publicPublicacion', id=id)
    
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar la investigación."
        request.session['alerta'] = alerta
        return render(request, "public/edit-investigacion.html", {"publicacion": publicacion, "formResumenInvestigacionEditar": formResumenInvestigacionEditar})


def buscarPublicacion(request):
    publicaciones= WeblaruexInvestigaciones.objects.filter(Q(resumen__icontains = request.POST.get('busqueda'))|Q(autor__icontains = request.POST.get('busqueda'))|Q(titulo__icontains = request.POST.get('busqueda'))).order_by('-fecha')
    paginator = Paginator(publicaciones, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "public/idi.html",
        {"publicaciones": publicaciones, "page_obj": page_obj}
    )

def filtrarPublicacion(request, tipo):
    if tipo=="Publicacion":
        tipo = "Publicación"
    if tipo=="Intercomparacion":
        tipo = "Intercomparación"
    publicaciones= WeblaruexInvestigaciones.objects.filter(tipo = tipo).order_by('-fecha')
    paginator = Paginator(publicaciones, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "public/idi.html",
        {"publicaciones": publicaciones, "page_obj": page_obj}
    )

def contacto(request):
    site_key = settings.RECAPTCHA_SITE_KEY
    if request.method == "POST":
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        ''' if reCAPTCHA returns True '''
        if result['success'] and result['score'] >= 0.5:

            #form = formularioCaptcha(request.POST)
            fecha = datetime.now()
            consulta = WeblaruexContacto(nombre=request.POST.get('name'), email=request.POST.get('email'), asunto=request.POST.get('subject'), mensaje=request.POST.get('message'), fecha=fecha)
            consulta.save()
            subject = 'Gracias por contactarnos '+request.POST.get('name')
            message = 'Nos pondremos en contacto con usted en la mayor brevedad posible'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.POST.get('email'),]
            send_mail( subject, message, email_from, recipient_list )
            subject = 'Nuevo mensaje de contacto recibido'
            message = 'Hemos recibido el siguiente formulario \nNombre: '+request.POST.get('name')+'\nEmail:'+request.POST.get('email')+'\nAsunto:'+request.POST.get('subject')+'\nMensaje:'+request.POST.get('message')
            recipient_list = [settings.EMAIL_HOST_USER,]
            send_mail( subject, message, email_from, recipient_list )
            return render(
                request,
                "public/thank-you-page.html",
                {}
            )
        else:
            raise Http404()
    else:
        
        form = formularioCaptcha()
        return render(
            request,
            "public/contact.html",
            {"form":form, "site_key":site_key})

def nosotros(request):
    return redirect('public:publicNuestraHistoria')

 

@permission_required('auth.laruex')
def areaPrivada(request):
    alerta = request.session.pop('alerta', None)
    if alerta and alerta['tipo'] != 'servicios':
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    servicios = WeblaruexServicios.objects.using('default').values()
    return render(request,"public/private-part.html",{"servicios":servicios, "alerta":alerta})




def consultaInforme(request):
    raise Http404()

def comprobacionInforme(request):
    informe = request.POST.get('informe')
    password = request.POST.get('password')
    return render(
        request,
        "public/consultaInforme.html",
        {"informe": informe}
    )

def gracias(request):
    return render(
        request,
        "public/than-you-page.html",
        {}
    )

def handle_not_found(request, exception):
    return render(
        request,
        "public/404.html"
    )

def cursos(request):
    cursos = WeblaruexCursos.objects.all()
    return render(
        request,
        "public/cursos-section.html",
        {"cursos":cursos}
    )


def cursoInfo(request, id):
    # cambiar esta consulta a que filtre por id, modificar el template para mostrarla info que pasa
    cursos=WeblaruexCursos.objects.filter(id=id)    
 # si noticias tiene longitud > 0 poner en la variable noticia el primer elemento (el [0]) sino error
    if len(cursos) > 0 :
        curso = cursos[0]
        patrocinadores = WeblaruexPatrocinadorescurso.objects.filter(id_curso=curso.id)
        return render(
            request,
            "public/curso-info.html",
            {"curso": curso, "patrocinadores": patrocinadores}
        )
    else:
        raise Http404()

def formulario(request, id):
    cursos=WeblaruexCursos.objects.filter(id=id)
    if len(cursos) > 0 :
        curso = cursos[0]
        patrocinadores = WeblaruexPatrocinadorescurso.objects.filter(id_curso=curso.id)
        return render(
            request,
            "public/formulario-curso.html",
            {"curso": curso, "patrocinadores": patrocinadores}
        )
    else:
        raise Http404()


def solicitarInfo(request, id):
    password = request.POST.get('password')   
    password= md5( password.encode("utf-8") ).hexdigest()
    if WeblaruexCursos.objects.filter(id=id, password=password).exists():
        contenidos=WeblaruexContenidocurso.objects.filter(id_curso=id).order_by('fecha_contenido')
        streaming = WeblaruexStreaming.objects.filter(id_curso=id).order_by('fecha')
        html = render_to_string('public/parts/contenido-privado-curso.html', {'contenidos': contenidos, 'streaming': streaming})
        return HttpResponse(html)
    else:
        return HttpResponse("")

def solicitarContenido(request, id_curso, codigo):
    contenido = WeblaruexContenidocurso.objects.filter(id_curso=id_curso, codigo=codigo)[0]
    return FileResponse(open(settings.MEDIA_ROOT + "/cursos/"+contenido.id_curso+"/"+contenido.url , 'rb'), content_type='application/force-download')


def formularioCurso(request):
    fecha = datetime.now()
    consulta = WeblaruexFormularioCursos(id_curso= request.POST.get('IDCurso'), nombre=request.POST.get('name'), apellidos=request.POST.get('surnames'), dni=request.POST.get('ID'), telefono=request.POST.get('Phone'),  email=request.POST.get('email'), grupo_investigacion=request.POST.get('work'), curriculum=request.POST.get('curriculum'), fecha=fecha)
    consulta.save()
    # correo enviado al usuario
    subject = 'Solicitud Inscripcion'+ request.POST.get('IDCurso')
    message = 'Gracias por contactar con nosotros ' + request.POST.get('name')  +  '\nHemos recibido su solicitud de inscripcion para el curso "' +  request.POST.get('IDCurso') + '". Valoraremos su solicitud y nos pondremos en contacto con usted. \n\nReciba un cordial saludo.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.POST.get('email'),]
    send_mail( subject, message, email_from, recipient_list )

    # correo recibido al correo de la empresa
    subject = 'Nueva solicitud de inscripción recibida.'
    message = '\nDon/Doña: '+ request.POST.get('name') + ' ' + request.POST.get('surnames') + ' ha enviado una solicitud de inscripción al curso "' + request.POST.get('IDCurso') + '" con los siguientes datos de contacto. \n' + '\nNombre y Apellido: '+ request.POST.get('name') + request.POST.get('surnames') + '\nDNI o Pasaporte: ' + request.POST.get('ID') + '\nTeléfono: '+request.POST.get('Phone') + '\nEmail: '+ request.POST.get('email') + '\nInstitución o Grupo de investigación: ' + request.POST.get('work') + '\nCurriculum: ' + request.POST.get('curriculum')

    recipient_list = [settings.EMAIL_HOST_USER,settings.EMAIL_CURSOS_GESTOR,]
    send_mail( subject, message, email_from, recipient_list )
    return render(
        request,
        "public/thank-you-page.html",
        {}
    )



'''-------------------------------------------
                                Módulo: subirDocumento

- Descripción: Permite subir un documento a la web.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:

-------------------------------------------'''
def subirDocumento(f, destino):
    with open(destino, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



'''-------------------------------------------
                                Módulo: agregarNoticia

- Descripción: Permite subir un documento a la web.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones: Agrega la noticia a la base de datos y renderiza al usuario a la página de éxito.

-------------------------------------------'''
@login_required
def agregarNoticia(request):

    if request.method == 'POST':
        alerta = {
            "alerta": True,
            "tipo": "success",
            "mensaje": "Noticia creada correctamente."
        }
        visible = 0
        if 'visibleNoticia' in request.POST:
            valor = request.POST.get("visibleNoticia")
            if valor == "1":
                visible = 1
        if 'categoriaNoticia' in request.POST:
            categoria = CategoriasNoticias.objects.filter(id=request.POST.get('categoriaNoticia'))[0]
        fecha = datetime.now()
        if 'fechaNoticia' in request.POST:
            fecha = request.POST.get('fechaNoticia')
        nuevaNoticia = WeblaruexNoticias(n_comentarios=0, fecha=fecha, titulo=request.POST.get('tituloNoticia'), resumen=request.POST.get('resumenNoticia'), noticia=request.POST.get('contenidoNoticia'), categoria=categoria.categoria, categoria_noticia=categoria, meta_descripcion=request.POST.get('metaDescriptionNoticia'), meta_keywords=request.POST.get('keywordsNoticia'), visible=visible)
        nuevaNoticia.save(using='default')

        #agregamos la imagen de la noticia
        if request.FILES.get('imagenNoticiaAgregar') is not None:
            ruta = settings.STATIC_ROOT + 'news/' + str(nuevaNoticia.id) + '.' + request.FILES['imagenNoticiaAgregar'].name.split('.')[-1]    
            subirDocumento(request.FILES['imagenNoticiaAgregar'], ruta)
            nuevaNoticia.img_portada = str(nuevaNoticia.id) + '.' + request.FILES['imagenNoticiaAgregar'].name.split('.')[-1]
            nuevaNoticia.save(using='default')
        request.session['alerta'] = alerta
        
        # mando un correo al responsable de la web de que se ha agregado una nueva noticia
        url = 'http://alerta2.es/noticiasPrivadas/'
        hyperlink = f'<a href="{url}">Ver listado de noticias sin publicar</a>'
        message = 'Se ha registrado una nueva noticia en la web. \n\nConsulta el listado de noticias pendientes de revisar.'
        html_message = f'{message}<br>{hyperlink}'
        subject = 'Nueva noticia recibida' 
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_NOTICIAS_GESTOR,]
        send_mail(subject, message, email_from, recipient_list, html_message=html_message)
        return redirect('public:publicNoticia', id=nuevaNoticia.id)
    else:    
        categorias = CategoriasNoticias.objects.using('default').values()
        formContenido = formularioNoticia()
        return render(request, "public/add-new.html", {'formularioNoticia': formContenido, "categorias":categorias})
    



'''-------------------------------------------
                                Módulo: editarNoticia

- Descripción: 
    Permite editar los datos de una noticia existente en la base de datos.

- Precondiciones:
    El usuario debe estar autenticado.

- Postcondiciones:
    Renderiza a la vista individual de la noticia editada.

-------------------------------------------'''
@login_required
def editarNoticia(request, id):
    noticia = WeblaruexNoticias.objects.using("default").filter(id=id)[0] 

    formResumenNoticiaEditar = formularioNoticia(initial={'resumenNoticia': noticia.resumen})
    formContenidoNoticiaEditar = formularioNoticia(initial={'contenidoNoticia': noticia.noticia})
    
    categorias = CategoriasNoticias.objects.using('default').values()
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Noticia editada correctamente."
    }


    if request.method == 'POST':
        alerta['mensaje'] = "La noticia " + str(noticia.id) + "-" + request.POST.get('tituloNoticiaEditar') + " se han modificado correctamente."
        if  'visibleEditar' in request.POST:
            visible = request.POST.get("visibleEditar")
            if visible == "1":
                noticia.visible = 1
            else:
                noticia.visible = 0
        if 'categoriaNoticiaEditar' in request.POST:
            categoria = CategoriasNoticias.objects.filter(id=request.POST.get("categoriaNoticiaEditar"))[0]
            noticia.categoria_noticia = categoria
            noticia.categoria = categoria.categoria
        if 'fechaNoticiaEditar' in request.POST:
            noticia.fecha = request.POST.get('fechaNoticiaEditar')

        formResumenNoticiaEditar = formularioNoticia(request.POST)
        if formResumenNoticiaEditar.is_valid():
            resumenNoticia = formResumenNoticiaEditar.cleaned_data['resumenNoticia']
            
        formContenidoNoticiaEditar = formularioNoticia(request.POST)
        if formContenidoNoticiaEditar.is_valid():
            contenidoNoticia = formContenidoNoticiaEditar.cleaned_data['contenidoNoticia']
        
        noticia.titulo = request.POST.get('tituloNoticiaEditar')
        noticia.resumen = resumenNoticia
        noticia.noticia = contenidoNoticia
        noticia.meta_descripcion = request.POST.get('metaDescriptionNoticiaEditar')
        noticia.meta_keywords = request.POST.get('keywordsNoticiaEditar')


        if 'nuevaImagenNoticiaEditar' in request.FILES:
            if noticia.img_portada:
                fotoNoticia = glob.glob(settings.STATIC_ROOT + 'img/news/' + str(noticia.img_portada))
                if fotoNoticia:
                    os.remove(fotoNoticia[0])
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/news/' + str(noticia.id) + '.' + request.FILES['nuevaImagenNoticiaEditar'].name.split('.')[-1]   
            subirDocumento(request.FILES['nuevaImagenNoticiaEditar'], rutaNuevaFoto)
            noticia.img_portada = str(noticia.id) + '.' + request.FILES['nuevaImagenNoticiaEditar'].name.split('.')[-1]
        noticia.save(using="default")

        request.session['alerta'] = alerta
        
        return redirect('public:publicNoticia', id=id)
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar la noticia."
        request.session['alerta'] = alerta
        return render(request, "public/edit-new.html", {'formResumenNoticiaEditar': formResumenNoticiaEditar, "formContenidoNoticiaEditar": formContenidoNoticiaEditar, "noticia": noticia, "categorias": categorias})

'''------------------------------------------
                                Módulo: eliminarNoticia

- Descripción:  
Este módulo se encarga de eliminar una noticia existente en la base de datos. Se utiliza para borrar los datos de un noticia que ya no es necesaria.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado una noticia existente en la base de datos para eliminar.

- Postcondiciones:
El proveedor debe ser eliminado de la base de datos.
Se debe mostrar la página de listado de proveedores sin el proveedor eliminado.

-------------------------------------------''' 
@login_required
def eliminarNoticia(request):
    idNoticia = request.POST.get('idNoticia')
    if request.method == 'POST':
        noticia = WeblaruexNoticias.objects.using('default').filter(id=idNoticia)[0]
        if noticia.img_portada:
            fotoNoticia = glob.glob(settings.STATIC_ROOT + 'img/news/' + str(noticia.img_portada))
            if fotoNoticia:
                os.remove(fotoNoticia[0])
        noticia.delete(using="default")
        return redirect('public:publicHome')






'''-------------------------------------------
                                Módulo: politicaCookies

- Descripción: Permite subir un documento a la web.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de cookies.

-------------------------------------------'''
def politicaCookies(request):
    return render(request,"public/politica-cookies.html")







'''-------------------------------------------
                                Módulo: agregarServicio

- Descripción: Permite agregar un nuevo servicio a la web.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def agregarServicio(request):
    alerta = {
        "alerta": True,
        "tipo": "error",
        "mensaje": "No se ha creado el servicio."
    }
    if request.method == 'POST':
        alerta['mensaje'] = "El servicio " + request.POST.get('nombreServicio') + " se ha creado correctamente."
        nuevoServicio = WeblaruexServicios(nombre=request.POST.get('nombreServicio'), grupo=request.POST.get('grupoServicio'), descripcion=request.POST.get('descripcionServicio'), enlace=request.POST.get('urlServicio'), categoria=request.POST.get('categoriaServicio'))
        nuevoServicio.save(using='default')
        #agregamos la imagen de la noticia
        if request.FILES.get('imagenServicio') is not None:
            ruta = settings.STATIC_ROOT + 'img/servicios/' + str(nuevoServicio.id) + '_service.' + request.FILES['imagenServicio'].name.split('.')[-1]   
            subirDocumento(request.FILES['imagenServicio'], ruta)
            nuevoServicio.imagen = str(nuevoServicio.id) + '_service.' + request.FILES['imagenServicio'].name.split('.')[-1]
            nuevoServicio.save(using='default')
            alerta["tipo"] = "success"
            alerta["mensaje"] = "Se ha creado el servicio correctamente."
            request.session['alerta'] = alerta
            return redirect('public:servicios')
        else:
            request.session['alerta'] = alerta
            return redirect('public:servicios')
    return redirect('public:servicios')


'''-------------------------------------------
                                Módulo: editarServicio

- Descripción: 
    Permite editar los datos de un servicio existente en la base de datos.

- Precondiciones:
    El usuario debe estar autenticado.

- Postcondiciones:
    Renderiza a la vista individual de la noticia editada.

-------------------------------------------'''
@login_required
def editarServicio(request, id):

    servicio = WeblaruexServicios.objects.using("default").filter(id=id)[0] 
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Servicio editada correctamente."
    }

    if request.method == 'POST':
        alerta['mensaje'] = "El servicio " + str(servicio.id) + "-" + request.POST.get('nombreServicioEditar') + " se ha modificado correctamente."        
        servicio.nombre = request.POST.get('nombreServicioEditar')
        if 'grupoServicioEditar' in request.POST:
            servicio.grupo = request.POST.get('grupoServicioEditar')
        servicio.descripcion = request.POST.get('descripcionServicioEditar')
        servicio.enlace = request.POST.get('urlServicioEditar')
        if 'categoriaServicioEditar' in request.POST:
            servicio.categoria = request.POST.get('categoriaServicioEditar')

        if 'imagenServicioEditar' in request.FILES:
            if servicio.imagen:
                imagenServicio = glob.glob(settings.STATIC_ROOT + 'img/servicios/' + str(servicio.imagen))
                if imagenServicio:
                    os.remove(imagenServicio[0])
            nuevaImagenServicio = settings.STATIC_ROOT + 'img/servicios/' + str(servicio.id) + '.' + request.FILES['imagenServicioEditar'].name.split('.')[-1]   
            subirDocumento(request.FILES['imagenServicioEditar'], nuevaImagenServicio)
            servicio.imagen = str(servicio.id) + '.' + request.FILES['imagenServicioEditar'].name.split('.')[-1]
        servicio.save(using="default")

        request.session['alerta'] = alerta
        
        return redirect('public:servicios')
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar el servicio."
        request.session['alerta'] = alerta
        return render(request, "public/edit-servicio.html", {"servicio": servicio, "alerta": alerta})


'''-------------------------------------------
                                Módulo: eliminarServicio

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def eliminarServicio(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Servicio eliminado correctamente."
    }
    idServicio = request.POST.get('idServicio')
    if request.method == 'POST':
        alerta['mensaje'] = "El servicio " + request.POST.get('inputNombreServicioEliminar') + " se ha eliminado correctamente."
        servicio = WeblaruexServicios.objects.using('default').filter(id=idServicio)[0]
        fotoServicio = glob.glob(settings.STATIC_ROOT + 'img/servicios/' + str(servicio.imagen))
        if fotoServicio:
            os.remove(fotoServicio[0])
        servicio.delete(using="default")
        request.session['alerta'] = alerta
        return redirect('public:servicios')



'''-------------------------------------------
                                Módulo: empleados

- Descripción: Permite visualizar la lista de empleados que hay en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de con el listado de empleados

-------------------------------------------'''
@login_required
def empleados(request):
    
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    empleados = WeblaruexEmpleados.objects.all()

    return render(request,"public/empleados-section.html", {"empleados": empleados, "alerta":alerta})


'''-------------------------------------------
                                Módulo: empleados

- Descripción: Permite visualizar la lista de empleados que hay en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de con el listado de empleados

-------------------------------------------'''
@login_required
def empleadoInfo(request, id):
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    if WeblaruexEmpleados.objects.using("default").filter(id=id).exists():
        empleado= WeblaruexEmpleados.objects.filter(id=id)[0]
        empleado.grupo_trabajo = empleado.grupo.split(' ')
        # cambiar esta consulta a que filtre por id, modificar el template para mostrarla info que pasa
        return render(request,"public/empleado-info.html",{"empleado": empleado, "alerta":alerta})
    else:
        return HttpResponse(request,"public/404.html")
    

'''-------------------------------------------
                                Módulo: editarEmpleado

- Descripción: Permite visualizar la lista de empleados que hay en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de con el listado de empleados

-------------------------------------------'''
@login_required
def editarEmpleado(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Empleado editado correctamente."
    }
    grupos = ""
    idEmpleado = request.POST.get('idEmpleadoEditar')
    if request.method == 'POST':
        alerta['mensaje'] = "Los datos del empleado" + request.POST.get('nuevoNombreEmpleado') + " se han modificado correctamente."
        empleado = WeblaruexEmpleados.objects.using('default').filter(id=idEmpleado)[0]
        empleado.nombre = request.POST.get('nuevoNombreEmpleado')
        empleado.puesto = request.POST.get('nuevoPuestoEmpleado')
        if 'checkbox' in request.POST:
            for i in request.POST.getlist('checkbox'):
                grupos = grupos + i + " "
            empleado.grupo = grupos
            if empleado.grupo == "":
                empleado.grupo = None
        if 'nuevaImagenEmpleado' in request.FILES:
            fotoEmpleado = glob.glob(settings.STATIC_ROOT + 'img/personal/trabajadores/' + str(empleado.imagen))
            if fotoEmpleado:
                os.remove(fotoEmpleado[0])
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/personal/trabajadores/' + str(idEmpleado) + '_empleado.' + request.FILES['nuevaImagenEmpleado'].name.split('.')[-1]
            subirDocumento(request.FILES['nuevaImagenEmpleado'], rutaNuevaFoto)
            empleado.imagen = idEmpleado + '_empleado.' + request.FILES['nuevaImagenEmpleado'].name.split('.')[-1]
        empleado.save(using="default")
        request.session['alerta'] = alerta
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar el empleado."
        request.session['alerta'] = alerta
    return redirect('public:publicEmpleadoInfo', id=idEmpleado)
    


'''-------------------------------------------
                                Módulo: agregarEmpleado

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def agregarEmpleado(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Empleado creado correctamente."
    }
    grupos = ""
    if request.method == 'POST':
        alerta['mensaje'] = "El empleado " + request.POST.get('nombreEmpleado') + " se han creado correctamente."
        if 'checkbox' in request.POST:
            for i in request.POST.getlist('checkbox'):
                grupos = grupos + i + " "
        nuevoEmpleado = WeblaruexEmpleados(nombre=request.POST.get('nombreEmpleado'), puesto=request.POST.get('puestoEmpleado'), grupo=grupos)
        nuevoEmpleado.save(using='default')
        
        if 'imagenEmpleadoAgregar' in request.FILES:
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/personal/trabajadores/' + str(nuevoEmpleado.id) + '_empleado.' + request.FILES['imagenEmpleadoAgregar'].name.split('.')[-1]
            subirDocumento(request.FILES['imagenEmpleadoAgregar'], rutaNuevaFoto)
            nuevoEmpleado.imagen = str(nuevoEmpleado.id) + '_empleado.' + request.FILES['imagenEmpleadoAgregar'].name.split('.')[-1]
            nuevoEmpleado.save(using='default')
        request.session['alerta'] = alerta
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar el empleado."
        request.session['alerta'] = alerta
    return redirect('public:publicEmpleadoInfo', id=str(nuevoEmpleado.id))




'''-------------------------------------------
                                Módulo: eliminarEmpleado

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def eliminarEmpleado(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Empleado eliminado correctamente."
    }
    idEmpleado = request.POST.get('idEmpleado')
    if request.method == 'POST':
        alerta['mensaje'] = "Empleado " + request.POST.get('inputNombreEmpleadoEliminar') +  "eliminado correctamente."

        empleado = WeblaruexEmpleados.objects.using('default').filter(id=idEmpleado)[0]
        if empleado.imagen:
            fotoEmpleado = glob.glob(settings.STATIC_ROOT + 'img/personal/trabajadores/' + str(empleado.imagen))
            if fotoEmpleado:
                os.remove(fotoEmpleado[0])
        empleado.delete(using="default")
        request.session['alerta'] = alerta
        return redirect('public:publicEmpleados')





'''-------------------------------------------
                                Módulo: responsables

- Descripción: Permite visualizar la lista de empleados que hay en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de con el listado de empleados

-------------------------------------------'''
@login_required
def responsables(request):    
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    responsables = WeblaruexResponsables.objects.all()

    return render(request,"public/responsables-section.html", {"responsables": responsables, "alerta":alerta})


'''-------------------------------------------
                                Módulo: responsableInfo

- Descripción: 
    Permite visualizar la información concreta de un responsable que hay en la base de datos
- Precondiciones:
    El usuario debe estar autenticado.
- Postcondiciones:
    Renderiza a la vista individual del responsable

-------------------------------------------'''
@login_required
def responsableInfo(request, id):
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    if WeblaruexResponsables.objects.using("default").filter(id=id).exists():
        responsable= WeblaruexResponsables.objects.filter(id=id)[0]
        responsable.secciones = responsable.apartado.split(' ')
        # cambiar esta consulta a que filtre por id, modificar el template para mostrarla info que pasa
        return render(request,"public/responsable-info.html",{"responsable": responsable, "alerta":alerta})
    else:
        return HttpResponse(request,"public/404.html")
    

'''-------------------------------------------
                                Módulo: agregarResponsable

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def agregarResponsable(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Responsable creado correctamente."
    }
    secciones = ""
    frase = ""
    telefono = ""
    if request.method == 'POST':
        alerta['mensaje'] = "El responsable " + request.POST.get('nombreResponsable') + " se ha creado correctamente."
        if 'telefonoResponsable' in request.POST:
            telefono = request.POST.get('telefonoResponsable')
            telefono = telefono.replace(" ", "")
            if not telefono.startswith("+34"):
                telefono = "+34"+ telefono
        if request.method == 'POST':
            if 'checkbox' in request.POST:
                for i in request.POST.getlist('checkbox'):
                    secciones = secciones + i + " "
            if 'fraseResponsable' in request.POST:
                frase = request.POST.get('fraseResponsable')
            nuevoResponsable = WeblaruexResponsables(nombre=request.POST.get('nombreResponsable'), cargo=request.POST.get('puestoResponsable'), frase=frase, telefono=telefono, email=request.POST.get('correoResponsable'), apartado=secciones)
            nuevoResponsable.save(using='default')
            
            if 'imagenResponsableAgregar' in request.FILES:
                rutaNuevaFoto = settings.STATIC_ROOT + 'img/personal/responsables/' + str(nuevoResponsable.id) + '_responsable.' + request.FILES['imagenResponsableAgregar'].name.split('.')[-1]
                subirDocumento(request.FILES['imagenResponsableAgregar'], rutaNuevaFoto)
                nuevoResponsable.imagen = str(nuevoResponsable.id) + '_responsable.' + request.FILES['imagenResponsableAgregar'].name.split('.')[-1]
                nuevoResponsable.save(using='default')
            request.session['alerta'] = alerta
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido crear el responsable."
        request.session['alerta'] = alerta
    return redirect('public:publicResponsableInfo', id=str(nuevoResponsable.id))




'''-------------------------------------------
                                Módulo: editarResponsable

- Descripción: Permite editar los datos de un responsable existente en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la vista individual del responsable

-------------------------------------------'''
@login_required
def editarResponsable(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Empleado editado correctamente."
    }
    secciones = ""
    
    idResponsable = request.POST.get('idResponsableEditar')
    if request.method == 'POST':
        alerta['mensaje'] = "Los datos del responsable" + request.POST.get('nuevoNombreResponsable') + " se han modificado correctamente."
        responsable = WeblaruexResponsables.objects.using('default').filter(id=idResponsable)[0]
        responsable.nombre = request.POST.get('nuevoNombreResponsable')
        responsable.cargo = request.POST.get('nuevoPuestoResponsable')
        responsable.email = request.POST.get('nuevoCorreoResponsable')
        telefono = responsable.telefono
        if 'nuevoTelefonoResponsable' in request.POST:
            telefono = request.POST.get('nuevoTelefonoResponsable')
            telefono = telefono.replace(" ", "")
            if not telefono.startswith("+34"):
                telefono = "+34 "+ telefono
            responsable.telefono = telefono
        if 'nuevaFraseResponsable' in request.POST:
            responsable.frase = request.POST.get('nuevaFraseResponsable')

        if 'checkbox' in request.POST:
            for i in request.POST.getlist('checkbox'):
                secciones = secciones + i + " "
            responsable.apartado = secciones
            if responsable.apartado == "":
                responsable.apartado = None
        if 'nuevaImagenResponsable' in request.FILES:
            fotoResponsable = glob.glob(settings.STATIC_ROOT + 'img/personal/responsables/' + str(responsable.imagen))
            if fotoResponsable:
                os.remove(fotoResponsable[0])
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/personal/responsables/' + str(idResponsable) + '_responsable.' + request.FILES['nuevaImagenResponsable'].name.split('.')[-1]
            subirDocumento(request.FILES['nuevaImagenResponsable'], rutaNuevaFoto)
            responsable.imagen = idResponsable + '_responsable.' + request.FILES['nuevaImagenResponsable'].name.split('.')[-1]
        responsable.save(using="default")
        request.session['alerta'] = alerta
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar el responsable."
        request.session['alerta'] = alerta
    return redirect('public:publicResponsableInfo', id=idResponsable)


'''-------------------------------------------
                                Módulo: eliminarResponsable

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def eliminarResponsable(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Responsable eliminado correctamente."
    }
    idResponsable = request.POST.get('idResponsable')
    if request.method == 'POST':
        alerta['mensaje'] = "Responsable " + request.POST.get('inputNombreResponsableEliminar') +  "eliminado correctamente."
        responsable = WeblaruexResponsables.objects.using('default').filter(id=idResponsable)[0]
        if responsable.imagen:
            fotoResponsable = glob.glob(settings.STATIC_ROOT + 'img/personal/responsables/' + str(responsable.imagen))
            if fotoResponsable:
                os.remove(fotoResponsable[0])
        responsable.delete(using="default")
        request.session['alerta'] = alerta
        return redirect('public:publicResponsables')





'''-------------------------------------------
                                Módulo: sliders

- Descripción: Permite visualizar la lista de empleados que hay en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de con el listado de empleados

-------------------------------------------'''
@login_required
def sliders(request):    
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    slidersHome = WeblaruexSliders.objects.filter(Q(pagina__icontains="principal")| Q(pagina__icontains="home"))
    slidersRedes = WeblaruexSliders.objects.filter(Q(pagina__icontains="alerta2")| Q(pagina__icontains="redes"))
    slidersLaboratorios = WeblaruexSliders.objects.filter(pagina__icontains="laboratorios")

    return render(request,"public/sliders-section.html", {"slidersHome": list(slidersHome), "slidersRedes": list(slidersRedes), "slidersLaboratorios": list(slidersLaboratorios), "alerta":alerta})


'''-------------------------------------------
                                Módulo: sliderInfo

- Descripción: 
    Permite visualizar la información concreta de un responsable que hay en la base de datos
- Precondiciones:
    El usuario debe estar autenticado.
- Postcondiciones:
    Renderiza a la vista individual del responsable

-------------------------------------------'''
@login_required
def sliderInfo(request, id):
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    if WeblaruexSliders.objects.using("default").filter(id=id).exists():
        slider = WeblaruexSliders.objects.filter(id=id)[0]
        #slider.secciones = slider.pagina.split(' ')
        # cambiar esta consulta a que filtre por id, modificar el template para mostrarla info que pasa
        return render(request,"public/slider-info.html",{"slider": slider, "alerta":alerta})
    else:
        return HttpResponse(request,"public/404.html")
    

'''-------------------------------------------
                                Módulo: comprobarPagina

- Descripción: Permite comprobar en que lista se encuentra la pagina que se le pasa.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Devuelve la lista en la que se encuentra la pagina.
-------------------------------------------'''
def comprobarPagina(pagina):
    paginaPrincipal = ['home', 'principal', 'PRINCIPAL', 'HOME', 'Home', 'Principal']
    paginaRedes = ['redes', 'ALERTA2', 'REDES', 'alerta2', 'Alerta2', 'Redes']
    paginaLaboratorio = ['laboratorios', 'LABORATORIOS', 'Laboratorios']
    paginaVacia = ['']
    if pagina != "":
        if pagina in paginaPrincipal:
            return paginaPrincipal
        if pagina in paginaRedes:
            return paginaRedes
        if pagina in paginaLaboratorio:
            return paginaLaboratorio
    else:
        return paginaVacia


'''-------------------------------------------
                                Módulo: agregarSlider

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def agregarSlider(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Slider creado correctamente."
    }
    pagina = ""
    descripcion = ""
    principal = 0
    if request.method == 'POST':
        alerta['mensaje'] = "El slider " + request.POST.get('tituloSlider') + " se ha creado correctamente."
        if 'checkboxAgregarSlider' in request.POST:
            pagina = request.POST.get('checkboxAgregarSlider')
        if 'checkboxPrincipal' in request.POST:
            if request.POST.get('checkboxPrincipal') == "1":
                principal = 1
        if principal == 1:
            paginaActual = comprobarPagina(pagina)
            if WeblaruexSliders.objects.filter(slider_principal=1, pagina__in=paginaActual).exists():
                sliderPrincipalActual = WeblaruexSliders.objects.filter(slider_principal=1, pagina__in=paginaActual)[0]
                sliderPrincipalActual.slider_principal = 0
                sliderPrincipalActual.save(using="default")
        if 'descripcionSlider' in request.POST:
            descripcion = request.POST.get('descripcionSlider')
       
        nuevoSlider = WeblaruexSliders(pagina=pagina,titulo=request.POST.get('tituloSlider'), descripcion=descripcion, enlace=request.POST.get('urlSlider'), slider_principal=principal)
        nuevoSlider.save(using='default')
        if 'imagenSliderAgregar' in request.FILES:
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/slider/' + str(nuevoSlider.id) + '_slider.' + request.FILES['imagenSliderAgregar'].name.split('.')[-1]
            subirDocumento(request.FILES['imagenSliderAgregar'], rutaNuevaFoto)
            nuevoSlider.imagen_slider = str(nuevoSlider.id) + '_slider.' + request.FILES['imagenSliderAgregar'].name.split('.')[-1]
            nuevoSlider.save(using='default')
        request.session['alerta'] = alerta
        return redirect('public:publicSliderInfo', id=str(nuevoSlider.id))
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido crear el slider."
        request.session['alerta'] = alerta
        return redirect('public:publicSliders')





'''-------------------------------------------
                                Módulo: editarSlider

- Descripción: Permite editar los datos de un responsable existente en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la vista individual del responsable

-------------------------------------------'''
@login_required
def editarSlider(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Slider editado correctamente."
    }

    idSlider = request.POST.get('idSliderEditar')
    principal = 0
    pagina = ""
    if request.method == 'POST':
        alerta['mensaje'] = "El slider " + str(idSlider) + "-" +request.POST.get('nuevoTituloSlider') + " se han modificado correctamente."
        slider = WeblaruexSliders.objects.using('default').filter(id=idSlider)[0]
        slider.titulo = request.POST.get('nuevoTituloSlider')
        slider.descripcion = request.POST.get('nuevaDescripcionSlider')
        slider.enlace = request.POST.get('nuevoUrlSlider')
        if 'checkboxEditarSlider' in request.POST:
            pagina = request.POST.get('checkboxEditarSlider')
            slider.pagina = pagina
        if 'checkboxSliderPrincipalEditar' in request.POST:
            if request.POST.get('checkboxSliderPrincipalEditar') == "1":
                principal = 1
        slider.slider_principal = principal
        if principal == 1:
            paginaActual = comprobarPagina(pagina)
            if WeblaruexSliders.objects.filter(slider_principal=1, pagina__in=paginaActual).exists():
                sliderPrincipalActual = WeblaruexSliders.objects.filter(slider_principal=1, pagina__in=paginaActual)[0]
                sliderPrincipalActual.slider_principal = 0
                sliderPrincipalActual.save(using="default")
        if 'nuevaImagenSliderEditar' in request.FILES:
            if slider.imagen_slider:
                fotoSlider = glob.glob(settings.STATIC_ROOT + 'img/slider/' + str(slider.imagen_slider))
                if fotoSlider:
                    os.remove(fotoSlider[0])
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/slider/' + str(idSlider) + '_slider.' + request.FILES['nuevaImagenSliderEditar'].name.split('.')[-1]
            subirDocumento(request.FILES['nuevaImagenSliderEditar'], rutaNuevaFoto)
            slider.imagen_slider = idSlider + '_slider.' + request.FILES['nuevaImagenSliderEditar'].name.split('.')[-1]
        slider.save(using="default")

        request.session['alerta'] = alerta
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar el slider."
        request.session['alerta'] = alerta
    return redirect('public:publicSliderInfo', id=idSlider)


'''-------------------------------------------
                                Módulo: eliminarSlider

- Descripción: Permite eliminar un slider que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la páginan con la lista de sliders.

-------------------------------------------'''
@login_required
def eliminarSlider(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Slider eliminado correctamente."
    }
    idSlider = request.POST.get('idSlider')
    if request.method == 'POST':
        alerta['mensaje'] = "Slider " + request.POST.get('inputNombreSliderEliminar') +  " eliminado correctamente."
        slider = WeblaruexSliders.objects.using('default').filter(id=idSlider)[0]
        if slider.imagen_slider:
            fotoSlider = glob.glob(settings.STATIC_ROOT + 'img/slider/' + str(slider.imagen_slider))
            if fotoSlider:
                os.remove(fotoSlider[0])
        slider.delete(using="default")
        request.session['alerta'] = alerta
        return redirect('public:publicSliders')
    

    


'''-------------------------------------------
                                Módulo: acreditaciones

- Descripción: Permite visualizar la lista de empleados que hay en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de con el listado de empleados

-------------------------------------------'''
@login_required
def acreditaciones(request):    
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    acreditaciones = WeblaruexAcreditaciones.objects.order_by('seccion')

    return render(request,"public/acreditaciones-section.html", {"acreditaciones": acreditaciones, "alerta":alerta})



'''-------------------------------------------
                                Módulo: acreditacionInfo

- Descripción: 
    Permite visualizar la información concreta de un responsable que hay en la base de datos
- Precondiciones:
    El usuario debe estar autenticado.
- Postcondiciones:
    Renderiza a la vista individual del responsable

-------------------------------------------'''
@login_required
def acreditacionInfo(request, id):
    alerta = request.session.pop('alerta', None)
    if alerta:
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    if WeblaruexAcreditaciones.objects.using("default").filter(id=id).exists():
        acreditacion = WeblaruexAcreditaciones.objects.filter(id=id)[0]
        acreditacion.secciones = acreditacion.seccion.split(' ')
        return render(request,"public/acreditacion-info.html",{"acreditacion": acreditacion, "alerta":alerta})
    else:
        return HttpResponse(request,"public/404.html")
    


'''-------------------------------------------
                                Módulo: agregarAcreditacion

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def agregarAcreditacion(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Acreditación creada correctamente."
    }
    seccion = ""
    if request.method == 'POST':
        alerta['mensaje'] = "La acreditación " + request.POST.get('nombreAcreditacion') + " se ha creado correctamente."
        if 'checkboxAgregarAcreditacion' in request.POST:
            seccion = request.POST.get('checkboxAgregarAcreditacion')
        if 'descripcionSlider' in request.POST:
            descripcion = request.POST.get('descripcionSlider')
       
        nuevaAcreditacion = WeblaruexAcreditaciones(nombre=request.POST.get('nombreAcreditacion'), seccion=seccion)
        nuevaAcreditacion.save(using='default')
        if 'archivoAcreditacionAgregar' in request.FILES:
            nombreArchivo = str(nuevaAcreditacion.id) + '_acreditacion.' + request.FILES['archivoAcreditacionAgregar'].name.split('.')[-1]
            rutaArchivo = settings.STATIC_ROOT + 'files/' + nombreArchivo
            subirDocumento(request.FILES['archivoAcreditacionAgregar'], rutaArchivo)
            nuevaAcreditacion.archivo = nombreArchivo
            nuevaAcreditacion.save(using='default')
        request.session['alerta'] = alerta
        return redirect('public:publicAcreditacionInfo', id=str(nuevaAcreditacion.id))
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido crear el slider."
        request.session['alerta'] = alerta
        return redirect('public:publicSliders')





'''-------------------------------------------
                                Módulo: editarAcreditacion

- Descripción: Permite editar los datos de un responsable existente en la base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la vista individual del responsable

-------------------------------------------'''
@login_required
def editarAcreditacion(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Acreditación editada correctamente."
    }
    seccion = ""
    idAcreditacion = request.POST.get('idAcreditacionEditar')
    if request.method == 'POST':
        alerta['mensaje'] = "Acreditación" + str(idAcreditacion) + "-" + request.POST.get('nuevoNombreAcreditacion') + " editada correctamente."
        acreditacion = WeblaruexAcreditaciones.objects.using('default').filter(id=idAcreditacion)[0]
        acreditacion.nombre = request.POST.get('nuevoNombreAcreditacion')
        if 'checkboxEditarAcreditacion' in request.POST:
            seccion = request.POST.get('checkboxEditarAcreditacion')
            acreditacion.seccion = seccion
        if 'nuevoArchivoAcreditacionEditar' in request.FILES:
            if acreditacion.archivo:
                archivoAcreditacion = glob.glob(settings.STATIC_ROOT + 'files/' + acreditacion.archivo)
                if archivoAcreditacion:
                    os.remove(archivoAcreditacion[0])
            rutaNuevaFoto = settings.STATIC_ROOT + 'files/' + str(idAcreditacion) + '_acreditacion.' + request.FILES['nuevoArchivoAcreditacionEditar'].name.split('.')[-1]
            subirDocumento(request.FILES['nuevoArchivoAcreditacionEditar'], rutaNuevaFoto)
            acreditacion.archivo = idAcreditacion + '_acreditacion.' + request.FILES['nuevoArchivoAcreditacionEditar'].name.split('.')[-1]
        acreditacion.save(using="default")
        request.session['alerta'] = alerta
    else:
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar la acreditacion."
        request.session['alerta'] = alerta
    return redirect('public:publicAcreditacionInfo', id=idAcreditacion)

       

'''-------------------------------------------
                                Módulo: eliminarAcreditacion

- Descripción: Permite eliminar un slider que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la páginan con la lista de sliders.

-------------------------------------------'''
@login_required
def eliminarAcreditacion(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Acreditación eliminada correctamente." 
    }
    idAcreditacion = request.POST.get('idAcreditacionEliminar')
    if request.method == 'POST':
        alerta['mensaje'] = request.POST.get('inputNombreAcreditacionEliminar') + " eliminada correctamente."
        acreditacion = WeblaruexAcreditaciones.objects.using('default').filter(id=idAcreditacion)[0]
        if acreditacion.archivo:
            archivoAcreditacion = glob.glob(settings.STATIC_ROOT + 'files/' + acreditacion.archivo)
            if archivoAcreditacion:
                os.remove(archivoAcreditacion[0])
        acreditacion.delete(using="default")
        request.session['alerta'] = alerta
        return redirect('public:publicAcreditaciones')
    


'''-------------------------------------------
                                Módulo: agregarInvestigacion

- Descripción: Permite subir una nueva investigacion esta puede ser una tesis  a la web.

- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones: Agrega la noticia a la base de datos y renderiza al usuario a la página de éxito.

-------------------------------------------'''
@login_required
def agregarInvestigacion(request):
    imagenInvestigacion = {
        "Intercomparación": "comparar.jpeg",
        "Proyecto": "contrato.png", 
        "Publicación": "periodicos.png",
        "Tesis": "lupa y libro.png",
    }
    tipoInvestigacion = request.POST.get('categoriaInvestigacion')
    fechaIncial = str(request.POST.get('yearInvestigacion'))
    titulo = request.POST.get('tituloInvestigacion')
    seccion = request.POST.get('checkboxAgregarInvestigacion')
    enlace = None
    if 'enlaceInvestigacion' in request.POST:
        enlace = request.POST.get('enlaceInvestigacion')
    infoAdicional = None
    if 'infoAdicionalInvestigacion' in request.POST:
        infoAdicional = request.POST.get('infoAdicionalInvestigacion')
    resumen = None
    if 'resumenInvestigacion' in request.POST:
        resumen = request.POST.get('resumenInvestigacion')
    revista = None
    if 'revistaInvestigacion' in request.POST:
        revista = request.POST.get('revistaInvestigacion')
    
    autor = None
    if 'autorInvestigacion' in request.POST:
        autor = request.POST.get('autorInvestigacion')
    entidad = None
    if 'entidadInvestigacion' in request.POST:
        entidad = request.POST.get('entidadInvestigacion')
    fechaFinal = None
    if 'lastYearInvestigacion' in request.POST:
        fechaFinal = str(request.POST.get('lastYearInvestigacion'))
    localizacion = None
    if 'localizacionInvestigacion' in request.POST:
        localizacion = request.POST.get('localizacionInvestigacion')
    if request.method == 'POST':
        nuevaInvestigacion = WeblaruexInvestigaciones(imagen=imagenInvestigacion[tipoInvestigacion], fecha=fechaIncial, titulo=titulo, tipo=tipoInvestigacion, enlace=enlace, seccion=seccion, informacion=infoAdicional, revista=revista, autor=autor, entidad_financiadora=entidad, resumen=resumen,fecha_final=fechaFinal, localizacion=localizacion)
        nuevaInvestigacion.save(using='default')
        return redirect('public:publicPublicaciones')
    else:    
        formInvestigacion = formularioInvestigacion()
        return render(request, "public/add-investigacion.html", {'formularioInvestigacion': formInvestigacion})


'''------------------------------------------
                                Módulo: eliminarNoticia

- Descripción:  
Este módulo se encarga de eliminar una noticia existente en la base de datos. Se utiliza para borrar los datos de un noticia que ya no es necesaria.

- Precondiciones:
El usuario debe haber iniciado sesión.
Se debe haber seleccionado una noticia existente en la base de datos para eliminar.

- Postcondiciones:
El proveedor debe ser eliminado de la base de datos.
Se debe mostrar la página de listado de proveedores sin el proveedor eliminado.
-------------------------------------------''' 
@login_required
def eliminarInvestigacion(request):
    idInvestigacion = request.POST.get('idInvestigacionEliminar')
    if request.method == 'POST':
        investigacion = WeblaruexInvestigaciones.objects.using('default').filter(id=idInvestigacion)[0]
    investigacion.delete(using="default")
    return redirect('public:publicHome')


'''------------------------------------------
                                Módulo: nuestraHistoria

- Descripción:  
Este módulo carga la página que muestra los origenes del Laruex.

- Precondiciones:

- Postcondiciones:
rederiza a la página de nuestra historia.
-------------------------------------------''' 
def nuestraHistoria(request):
    return render(
        request,
        "public/nuestraHistoria.html",
        {}
    )





'''------------------------------------------
                                Módulo: nuestrasMedidas

- Descripción:  
Este módulo carga la sección donde se encuentra el slider de las medidas que se realizan en el laruex.

- Precondiciones:

- Postcondiciones:
rederiza el slider con el listado de medidas.
-------------------------------------------''' 
def nuestrasMedidas(request):

    medidas = WeblaruexMedidas.objects.using('default').values()

    return render(
        request,
        "public/nuestrasMedidas.html",
        {'medidas': medidas}
    )



'''------------------------------------------
                                Módulo: medidas

- Descripción:  
Este módulo carga la página donde se encuentran todas las medidas listadas del laruex.

- Precondiciones:

- Postcondiciones:
rederiza a la página con el listado de medidas.
-------------------------------------------''' 
def medidas(request):
    alerta = request.session.pop('alerta', None)
    if alerta and alerta['tipo'] != 'medida':
        # Procesar el mensaje de alerta
        tipo = alerta['tipo']
        mensaje = alerta['mensaje']
    medidas = WeblaruexMedidas.objects.using('default').values()
    formDescripcionMedida = formularioMedida()
    
    return render(
        request,
        "public/medidas.html",
        {'medidas': medidas, "formMedida":formDescripcionMedida, "alerta":alerta}
    )



'''-------------------------------------------
                                Módulo: medidaInfo

- Descripción: 
    Permite visualizar la información concreta de una medida que hay en la base de datos
- Precondiciones:
    Debe existir esa medida
- Postcondiciones:
    Renderiza a la vista individual del responsable

-------------------------------------------'''
def medidaInfo(request, url):
    if WeblaruexMedidas.objects.using("default").filter(url=url).exists():
        medida = WeblaruexMedidas.objects.filter(url=url)[0]
        return render(request,"public/medida-info.html",{"medida": medida})
    else:
        return HttpResponse(request,"public/404.html")



'''-------------------------------------------
                                Módulo: agregarMedida

- Descripción: Permite eliminar un nuevo servicio que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la página de política de servicios.

-------------------------------------------'''
@login_required
def agregarMedida(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Medida creada correctamente."
    }

    if request.method == 'POST':
        # campos del formulario
        nombreMedida= request.POST.get('nombreMedida')
        norma = request.POST.get('normaMedida')
        resumenTarjeta = request.POST.get('resumenMedidaTarjeta')
        resumen = request.POST.get('resumenMedida')
        descripcion = request.POST.get('descripcionMedida')
        keywords = request.POST.get('keywordsMedida')
        metaDescripcion = request.POST.get('metaDescriptionMedida')
        url = request.POST.get('urlMedida')

        alerta['mensaje'] = nombreMedida + " agregada correctamente."

        # creamos la nueva medida en la base de datos
        nuevaMedida = WeblaruexMedidas(nombre=nombreMedida, resumen_tarjeta=resumenTarjeta, resumen_medida=resumen, descripcion_medida=descripcion, meta_descripcion=metaDescripcion, meta_keywords=keywords, norma=norma, url=url)
        nuevaMedida.save(using='default')

        #agregamos la imagen de la noticia
        if request.FILES.get('imagenMedidaAgregar') is not None:
            ruta = settings.STATIC_ROOT + 'img/medidas/' + str(nuevaMedida.id) + '.' + request.FILES['imagenMedidaAgregar'].name.split('.')[-1]   
            subirDocumento(request.FILES['imagenMedidaAgregar'], ruta)
            nuevaMedida.img_portada = str(nuevaMedida.id) + '.' + request.FILES['imagenMedidaAgregar'].name.split('.')[-1]
            nuevaMedida.save(using='default')
        request.session['alerta'] = alerta
        return redirect('public:publicMedidas')
    else: 
        formMedida = formularioMedida()
        return render(request, "public/add-medida.html", {'formMedida': formMedida})


'''-------------------------------------------
                                Módulo: editarMedida

- Descripción: 
    Permite editar los datos de una medida existente en la base de datos.

- Precondiciones:
    El usuario debe estar autenticado.

- Postcondiciones:
    Renderiza a la vista individual de la medida

-------------------------------------------'''
@login_required
def editarMedida(request, id):
    
    medida = WeblaruexMedidas.objects.using("default").filter(id=id)[0]    
    url = str(medida.url)

    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Medida editado correctamente."
    }

    if request.method == 'POST':
        
        formEditarMedida = formularioMedida(request.POST)
        
        if formEditarMedida.is_valid():
            descripcion_medida = formEditarMedida.cleaned_data['descripcionMedida']

        alerta['mensaje'] = "La medida " + str(medida.id) + "-" +request.POST.get('nombreMedidaEditar') + " se han modificado correctamente."
        medida.nombre = request.POST.get('nombreMedidaEditar')
        medida.resumen_tarjeta = request.POST.get('resumenMedidaTarjetaEditar')
        medida.resumen_medida = request.POST.get('resumenMedidaEditar')
        medida.descripcion_medida = descripcion_medida
        medida.meta_descripcion = request.POST.get('metaDescriptionMedidaEditar')
        medida.meta_keywords = request.POST.get('keywordsMedidaEditar')
        medida.norma = request.POST.get('normaMedidaEditar')
        if 'urlMedidaEditar' in request.POST:
            medida.url = request.POST.get('urlMedidaEditar')
            url = str(medida.url)
        if 'nuevaImagenMedidaEditar' in request.FILES:
            if medida.imagen:
                fotoMedida = glob.glob(settings.STATIC_ROOT + 'img/medidas/' + str(medida.imagen))
                if fotoMedida:
                    os.remove(fotoMedida[0])
            rutaNuevaFoto = settings.STATIC_ROOT + 'img/medidas/' + str(medida.id) + '_medida.' + request.FILES['nuevaImagenMedidaEditar'].name.split('.')[-1]
            subirDocumento(request.FILES['nuevaImagenMedidaEditar'], rutaNuevaFoto)
            medida.imagen = str(medida.id) + '_medida.' + request.FILES['nuevaImagenMedidaEditar'].name.split('.')[-1]
        medida.save(using="default")

        request.session['alerta'] = alerta
        
        return redirect('public:publicMedidaInfo', url=url)
    else:
        formEditarMedida = formularioMedida(initial={'descripcionMedida': medida.descripcion_medida})
        alerta["tipo"] = "error"
        alerta["mensaje"] = "No se ha podido editar la medida."
        request.session['alerta'] = alerta
        return render(request, "public/edit-medida.html", {'formEditarMedida': formEditarMedida, "medida": medida})



'''-------------------------------------------
                                Módulo: eliminarMedida

- Descripción: Permite eliminar un slider que esta en base de datos
- Precondiciones:
El usuario debe estar autenticado.

- Postcondiciones:
Renderiza a la páginan con la lista de sliders.

-------------------------------------------'''
@login_required
def eliminarMedida(request):
    alerta = {
        "alerta": True,
        "tipo": "success",
        "mensaje": "Medida eliminada correctamente."
    }
    idMedida = request.POST.get('idMedida')
    if request.method == 'POST':
        alerta['mensaje'] = "Medida " + request.POST.get('inputNombreMedidaEliminar') +  " eliminada correctamente."
        medida = WeblaruexMedidas.objects.using('default').filter(id=idMedida)[0]
        if medida.imagen:
            fotoMedida = glob.glob(settings.STATIC_ROOT + 'img/medidas/' + str(medida.imagen))
            if fotoMedida:
                os.remove(fotoMedida[0])
        medida.delete(using="default")
        request.session['alerta'] = alerta
        return redirect('public:publicMedidas')
