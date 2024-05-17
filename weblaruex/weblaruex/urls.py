"""weblaruex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, re_path, path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns

# imports apps propias
from public.views import consultaInforme

from django.contrib import admin

from django.contrib.auth.decorators import login_required
from django.views.static import serve

@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


urlpatterns = [
    path('admin/',                          admin.site.urls),

    #Forzamos que se requiera estar logueado para consultar ficheros de media
    url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve, {'document_root': settings.MEDIA_ROOT}),

    #Basicas
    path('consultaInforme/', consultaInforme),

    # Structure
    path('', include('structure.urls', namespace='structure')),

    # Public
    path('', include('public.urls', namespace='public')),

    # VRAEX
    path('', include('copuma.urls', namespace='copuma')),

    # Rare
    path('', include('rare.urls', namespace='rare')),

    # Gestion Muestras
    path('', include('gestionmuestras.urls', namespace='gestionmuestras')),

    # SPIDA
    path('', include('spida.urls', namespace='spida')),

    # Spida prueba
    path('', include('spd.urls', namespace='spd')),

    # Calendario Guardias
    path('', include('calendario_guardias.urls', namespace='calendario_guardias')),

    # Aplicacion de documentacion del LARUEX
    path('', include('docLaruex.urls', namespace='docLaruex')),

    # Veiex
    path('', include('veiex.urls', namespace='veiex')),

    # TimeTrackPro
    path('', include('timetrackpro.urls', namespace='timetrackpro')),
    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns (
    path('', include('structure.urls', namespace='structure')),
    path('', include('public.urls', namespace='public')),
    path('', include('copuma.urls', namespace='vraex')),
    path('', include('rare.urls', namespace='rare')),
    path('', include('gestionmuestras.urls', namespace='gestionmuestras')),
    path('', include('spida.urls', namespace='spida')),
    path('', include('spd.urls', namespace='spd')),
    path('', include('calendario_guardias.urls', namespace='calendario_guardias')),
    path('', include('docLaruex.urls', namespace='docLaruex')),
    path('', include('veiex.urls', namespace='veiex')),
    path('', include('timetrackpro.urls', namespace='timetrackpro')),
)

#if settings.DEBUG:
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
