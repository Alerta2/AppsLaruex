
#from timetrackpro.views import *
from django.urls import path
from django.conf.urls import url
from .views import *
from django.conf.urls.static import static
from django.conf.urls import url

app_name = 'timetrackpro'

urlpatterns = [
    path('private/timetrackpro/', home ,name='home'),
    path('private/timetrackpro/documentacion', documentacion ,name='documentacion'),
    path('private/timetrackpro/perfil', perfil ,name='perfil'),
    path('private/timetrackpro/dashboard', dashBoard ,name='dashBoard'),
    path('private/timetrackpro/tablas', tablas ,name='tablas'),
    path('private/timetrackpro/facturacion', facturacion ,name='facturacion'),
    path('private/timetrackpro/realidadVirtual', realidadVirtual ,name='realidadVirtual'),
    path('private/timetrackpro/sign-in', signIn ,name='sign-in'),
    path('private/timetrackpro/sign-up', signUp ,name='sign-up'),
    path('private/timetrackpro/tarjetas-de-acceso', tarjetasAcceso ,name='tarjetas-de-acceso'),
    path('private/timetrackpro/agregar-tarjeta', agregarTarjetaAcceso ,name='agregar-tarjeta'),
    path('private/timetrackpro/tarjeta-de-acceso/<slug:id>', verTarjetaAcceso ,name='ver-tarjeta-acceso'),
    # registros insertados en la base de datos  
    path('private/timetrackpro/agregar-registro', agregarRegistro ,name='agregar-registro'),
    path('private/timetrackpro/registros-insertados', registrosInsertados ,name='registros-insertados'),
    
]
