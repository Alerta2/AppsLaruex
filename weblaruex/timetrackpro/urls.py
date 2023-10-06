
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

    # registros de las tarjetas de acceso
    path('private/timetrackpro/tarjetas-de-acceso', tarjetasAcceso ,name='tarjetas-de-acceso'),
    path('private/timetrackpro/agregar-tarjeta', agregarTarjetaAcceso ,name='agregar-tarjeta'),
    path('private/timetrackpro/tarjeta-de-acceso/<slug:id>', verTarjetaAcceso ,name='ver-tarjeta-acceso'),
    # registros insertados en la base de datos  
    path('private/timetrackpro/agregar-registro', agregarRegistro , name='agregar-registro'),
    path('private/timetrackpro/registros-insertados', registrosInsertados , name='registros-insertados'),
    path('private/timetrackpro/datos-registros-insertados', datosRegistrosInsertados , name='registros-insertados'),
    path('private/timetrackpro/ver-registro/<slug:id>/', verRegistro , name='ver-registro'),
    path('private/timetrackpro/datos-registro/<slug:id>/', datosRegistro , name='datos-registro'),
    # información de los empleados del Laruex
    path('private/timetrackpro/agregar-usuario', agregarUsuario , name='agregar-usuario'),
    path('private/timetrackpro/datos-empleados/', datosEmpleados , name='datos-empleados'),
    path('private/timetrackpro/empleados/', empleados , name='empleados'),
    path('private/timetrackpro/ver-empleado/<slug:id>/', verEmpleado , name='ver-empleado'),
    path('private/timetrackpro/editar-empleado/<slug:id>/', editarEmpleado , name='editar-empleado'),

    # información de las tarjetas de acceso
    
    path('private/timetrackpro/editar-tarjeta-acceso/<slug:id>/', editarTarjetaAcceso , name='editar-tarjeta-acceso'),

    # información de los usuarios del sistema
    path('private/timetrackpro/asociar-usuario/', asociarUsuario , name='asociar-usuario'),

    # información de los usuarios del control de acceso 
    path('private/timetrackpro/agregar-usuario-maquina', agregarUsuarioMaquina , name='agregar-usuario-maquina'),
    path('private/timetrackpro/usuarios-maquina/', usuariosMaquina , name='usuarios-maquina'),
    path('private/timetrackpro/datos-usuarios-maquina/', datosUsuariosMaquina , name='datos-usuarios-maquina'),
    path('private/timetrackpro/ver-usuario-maquina/<slug:id>/', verUsuarioMaquina , name='ver-usuario-maquina'),

    #solicitudes de vacaciones
    path('private/timetrackpro/solicitudes/', solicitudes , name='solicitudes'),

    # festivos
    path('private/timetrackpro/datos-festivos-calendario/', datosFestivosCalendario , name='datos-festivos-calendario'),
    path('private/timetrackpro/calendario-anual-festivos/', calendarioAnualFestivos , name='calendario-anual-festivos'),
    path('private/timetrackpro/calendario-festivos/<slug:mes>/', calendarioFestivos , name='calendario-festivos'),
    path('private/timetrackpro/festivos/', festivos , name='festivos'),
    path('private/timetrackpro/festivos/<slug:year>/', festivos , name='festivos-year'),
    path('private/timetrackpro/agregar-festivo/', agregarFestivo , name='agregar-festivo'),
    path('private/timetrackpro/agregar-festivo/<slug:id>/', editarFestivo , name='editar-festivo'),
    path('private/timetrackpro/agregar-festivo/<slug:id>/', eliminarFestivo , name='eliminar-festivo'),

    # información relacionada con los empleados
    path('private/timetrackpro/errores-en-registros/<slug:mes>/', erroresRegistro , name='errores-en-registros'),
    path('private/timetrackpro/errores-en-registros/<slug:idEmpleado>/<slug:year>/<slug:mes>/', erroresRegistroEmpleado , name='errores-en-registros-empleado'),
    
]
