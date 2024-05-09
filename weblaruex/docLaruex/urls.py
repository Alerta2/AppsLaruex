from django.urls import path
from django.conf.urls import url
from .views import *
from django.conf.urls.static import static
from django.conf.urls import url
#patterns

app_name = 'docLaruex'

urlpatterns = [
     
    path('private/docLaruex/accesoDenegado', accesoDenegado, name='docLaruexAccesoDenegado'),

    # vista de la portada 
    path('docLaruex/', home, name='docLaruexHome'),

    # vista que permite 
    path('private/docLaruex/', portada, name='docLaruexPortada'), 

    # vista que permite 
    path('private/docLaruex/eliminadoExito', eliminadoExito, name='docLaruexEliminadoExito'),

    # vista que permite 
    path('private/docLaruex/noEncontrado', noEncontrado, name='docLaruexNoEncontrado'),

# ---------------------------------------------------------
#                         USUARIOS 
# ---------------------------------------------------------
    # vista y rellanado de la página con todos los objetos
    path('private/docLaruex/usuarios', listadoUsuarios, name='docLaruexListadoUsuarios'),
    
    path('private/docLaruex/usuariosDatos',
         DatosUsuarios, name='docLaruexUsuarioDatos'),

    # vista de los datos de un usuario 
    path('private/docLaruex/verUsuario/<slug:id>/', verUsuario, name='docLaruexVerUsuario'),

    # vista de los datos de un usuario 
    path('private/docLaruex/verMiPerfil/', verMiPerfil, name='docLaruexVerMiPerfil'),

    # vista que elimina los permisos de un usuario
    path('private/docLaruex/inhabilitarUsuario/<slug:id>/', inhabilitarUsuario, name='docLaruexInhabilitarUsuario'),
    

    # vista que edita los datos de un usuario
    path('private/docLaruex/editarUsuario/<slug:id>/', editarUsuario, name='docLaruexEditarUsuario'),


    # vista y rellanado de la página con todos los objetos
    path('private/docLaruex/objetos', ListadoObjetos, name='docLaruexObjeto'),
    
    path('private/docLaruex/objetosDatos',
         DatosObjetos, name='docLaruexObjetoDatos'),

    # vista y rellenado de las tablas para asociar archivos
    path('private/docLaruex/objetosDatosAsociar',
         DatosObjetosAsociar, name='docLaruexObjetoDatosAsociar'),



# ---------------------------------------------------------
#                         FABRICANTE 
# ---------------------------------------------------------

    # vista/html de la página de listaFabricantes
    path('private/docLaruex/fabricantes',
         ListadoFabricantes, name='docLaruexFabricantes'),

    # vista/html de la página de un fabricante en particular 
    path('private/docLaruex/verFabricante/<slug:id>/',
         verFabricante, name='docLaruexVerFabricante'),

    # vista/html de la página de un fabricante en particular 
    path('private/docLaruex/editarFabricante/<slug:id>/',
         editarFabricante, name='docLaruexEditarFabricante'), 


    # vista/html de la página de listaProveedores
    path('private/docLaruex/proveedores',
         ListadoProveedores, name='docLaruexProveedores'),

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Habilitaciones (listaHabilitaciones.html)
    path('private/docLaruex/proveedoresDatos',
         DatosProveedores, name='docLaruexProveedoresDatos'),

    # vista/html de la página de un fabricante en particular 
    path('private/docLaruex/verProveedor/<slug:id>/',
         verProveedor, name='docLaruexVerProveedor'),

    # vista/html de la página de un fabricante en particular 
    path('private/docLaruex/editarProveedor/<slug:id>/',
         editarProveedor, name='docLaruexEditarProveedor'), 

    # tras pulsar el boton [+] añade un nuevo proveedor a la 
    # lista de proveedores (listaProveedores.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarProveedor/',
         agregarProveedor, name='docLaruexAgregarProveedor'),

     # vista/html para eliminar un Proveedor            
    path('private/docLaruex/eliminarProveedor/<slug:id>/', eliminarProveedor, name='docLaruexEliminarProveedor'),



     # vista/html para eliminar un fabricante            
    path('private/docLaruex/eliminarFabricante/<slug:id>/', eliminarFabricante, name='docLaruexEliminarFabricante'),


    # vista/html de la página de un fabricante en particular 
    path('private/docLaruex/editarEstado/<slug:id>/',
         editarEstado, name='docLaruexEditarEstado'),


    # vista/html de la página de un fabricante en particular 
    path('private/docLaruex/editarEstadoNotificacion/<slug:id>/',
         editarEstadoNotificacion, name='docLaruexEditarEstado'),

    # vista/html que permite editar un equipo en particular
    path('private/docLaruex/editarObjeto/<slug:id>/',
         editarObjeto, name='docLaruexeditarObjeto'),


# ---------------------------------------------------------
#                         PROCEDIMIENTOS 
# ---------------------------------------------------------
     #¿¿¿¿¿BORRAR?????
    # listado de items de tipo Procedimiento vista listaProcedimientos.html
    #path('private/docLaruex/procedimientos',ListadoProcedimientos, name='docLaruexProcedimientos'),

    # listado de items de tipo Procedimiento vista listaProcedimientos.html
    path('private/docLaruex/procedimientosDatos',
         DatosProcedimientos, name='docLaruexProcedimientoDatos'),
         # vista y rellanado de la página con todas los equipos,

    # listado de items de tipo Procedimiento vista listaProcedimientos.html
    path('private/docLaruex/procedimientosTipo',
         ListadoProcedimientosTipo, name='docLaruexProcedimientosTipo'),

    # listado de items de tipo Procedimiento vista listaProcedimientos.html
    path('private/docLaruex/procedimientosDatosTipo/<slug:tipo>/',
         DatosProcedimientosTipo, name='docLaruexProcedimientoDatosTipo'),

    # listado de items de tipo Procedimiento vista listaProcedimientos.html
    path('private/docLaruex/reservaProcedimientos',
         ListadoReservaProcedimientos, name='docLaruexReservaProcedimientos'),

    # listado de items de tipo Procedimiento vista listaProcedimientos.html
    path('private/docLaruex/reservaProcedimientosDatos',
         ReservaDatosProcedimientos, name='docLaruexReservaProcedimientoDatos'),

     
    # vista/html para eliminar una reserva de Procedimiento            
    path('private/docLaruex/eliminarReservaProcedimiento/<slug:id>/', eliminarReservaProcedimiento, name='docLaruexEliminarReservaProcedimiento'),


    # buscar los procedimientos en función de su nombre
    path('private/docLaruex/buscarProcedimiento/<slug:codigo>/',
         BuscarCodigoProcedimiento, name='docLaruexBuscarCodigoProcedimiento'),

# ---------------------------------------------------------
#                         CURRICULUMS 
# ---------------------------------------------------------

    # listado de items de tipo curriculum vista listaCurriculums.html
    path('private/docLaruex/curriculumsDatos',
         DatosCurriculums, name='docLaruexCurriculumsDatos'),
     
    # vista individualizada de cada curriculum 
    path('private/docLaruex/verCurriculumUsuario',
         verCurriculumUsuario, name='docLaruexVerCurriculumUsuario'),

    # vista que permite descargar un zip con las formaciones de un usuario
    path('private/docLaruex/descargarZipCurriculum',
         descargarZipCurriculum, name='docLaruexDescargarZipCurriculumUsuario'),
         
    # vista/html que permite visualizar las formaciones asociadas a un curriculum 
    path('private/docLaruex/formacionesAsociadas/<slug:id_curriculum>/',
         formacionesAsociadas, name='docLaruexFormacionesAsociadas'),
         
    # vista/html que permite visualizar las formaciones asociadas a un curriculum 
    path('private/docLaruex/formacionesAsociadasCurriculum/<slug:id_curriculum>/<slug:yearSelected>/',
         formacionesAsociadasCurriculum, name='docLaruexFormacionesAsociadasCurriculum'),

         # vista/html que permite agregar una formación a un curriculum 
    path('private/docLaruex/agregarFormacionCurriculum/<slug:id_curriculum>/',
         agregarFormacionCurriculum, name='docLaruexAgregarFormacionCurriculum'),

         # vista/html que permite agregar una formación a un curriculum 
    path('private/docLaruex/consultarFormacionCurriculum/<slug:id_curriculum>/<slug:id>/',
         consultarFormacionCurriculum, name='docLaruexConsultarFormacionCurriculum'),
     
     

         # vista/html que comprobar quien es el propietario de un objeto
    path('private/docLaruex/comprobarPropietario/<slug:id_objeto>/',
         comprobarPropietario, name='docLaruexComprobarPropietario'),

     
     # vista/html para eliminar un curriculum            
    path('private/docLaruex/eliminarCurriculum/<slug:id>/', eliminarCurriculum, name='docLaruexEliminarCurriculum'),

     # vista/html de la página de habilitaciones que permite desde la tabla eliminar una habilitacion dado el id_habilitacion
    path('private/docLaruex/eliminarItemCurriculum/<slug:id_curriculum>/<slug:id>/',
         eliminarItemCurriculum, name='docLaruexEliminarItemCurriculum'),


# ---------------------------------------------------------
#                         DOCUMENTOS 
# ---------------------------------------------------------

    # listado de items de tipo documento vista listaDocumentos.html
    path('private/docLaruex/documentosDatos',
         DatosDocumentos, name='docLaruexDocumentosDatos'),


# ---------------------------------------------------------
#                      HABILITACIONES 
# ---------------------------------------------------------
    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Habilitaciones (listaHabilitaciones.html)
    path('private/docLaruex/habilitacionesDatos',
         DatosHabilitaciones, name='docLaruexHabilitacionesDatos'),

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse listado relacionado  de habilitaciones con usuarios (listaHabilitaciones.html)
    path('private/docLaruex/habilitacionesDatosRelacionados',
         DatosHabilitacionesRelacionadas, name='docLaruexHabilitacionesDatosRelacionados'),

    # collapse listado relacionado  de habilitaciones con usuarios (listaHabilitaciones.html)
    path('private/docLaruex/habilitacionesDatosRelacionados/<slug:id>/',
         DatosHabilitacionesRelacionadas, name='docLaruexHabilitacionesDatosRelacionados'),

# ---------------------------------------------------------
#                         FABRICANTES 
# ---------------------------------------------------------

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Habilitaciones (listaHabilitaciones.html)
    path('private/docLaruex/fabricantesDatos',
         DatosFabricantes, name='docLaruexFabricantesDatos'),

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Habilitaciones (listaHabilitaciones.html)

# ---------------------------------------------------------
#                         PROYECTOS 
# ---------------------------------------------------------
    path('private/docLaruex/proyectosDatos',
         DatosProyectos, name='docLaruexProyectosDatos'),

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Habilitaciones (listaHabilitaciones.html)

# ---------------------------------------------------------
#                           ACTAS 
# ---------------------------------------------------------
    path('private/docLaruex/actasDatos',
         DatosActas, name='docLaruexActasDatos'),

# ---------------------------------------------------------
#                           CURSOS 
# ---------------------------------------------------------
    # Obtiene los datos que rellenan la tabla lista de Cursos
    path('private/docLaruex/cursosDatos',
         DatosCursos, name='docLaruexCursosDatos'),

# ---------------------------------------------------------
#                         OBJETOS 
# ---------------------------------------------------------

    # vista individualizada de cada objeto
    path('private/docLaruex/verObjeto/<slug:id>/',
         InfoVerObjeto, name='docLaruexInfoVerObjeto'),


    # url que permite visualizar un listado completo filtrado por el tipo de objeto
    path('private/docLaruex/tipoObjeto/<slug:tipo>/',
         ListadoObjetosPorTipo, name='docLaruexListadoObjetosPorTipo'),

    path('private/docLaruex/objetosDatosSeleccionados/<slug:id>/',
         DatosObjetosSeleccionados, name='docLaruexObjetoDatosSeleccionados'),

    path('private/docLaruex/formatosAsociados/<slug:id_procedimiento>/',
         FormatosAsociadosProcedimiento, name='docLaruexformatosAsociadosProcedimiento'),
    path('private/docLaruex/historialProcedimiento/<slug:codigo_procedimiento>/',
         historialProcedimiento, name='docLaruexHistorialProcedimiento'),
    path('private/docLaruex/archivosAsociados/<slug:id_documento>/',
         archivosAsociados, name='docLaruexArchivosAsociados'),
    path('private/docLaruex/agregarArchivo/',
         agregarArchivo, name='docLaruexAgregarArchivo'),
    path('private/docLaruex/eliminarObjeto/<slug:id_objeto>/',
         eliminarObjeto, name='docLaruexEliminarObjeto'),


# ---------------------------------------------------------
#                         NOTIFICACIONES 
# ---------------------------------------------------------
    path('private/docLaruex/agregarNotificacion/',
         agregarNotificacion, name='docLaruexAgregarNotificacion'),
         # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Habilitaciones (listaHabilitaciones.html)
    path('private/docLaruex/notificacionesDatos/<slug:id_doc>/',
         datosNotificaciones, name='docLaruexNotificacionesDatos'),

    # Consulta las notificaciones que hay en la base de datos 
    path('private/docLaruex/consultarNotificaciones/',
         consultarNotificaciones, name='docLaruexConsultarNotificaciones'),
    path('private/docLaruex/consultarNotificacionesNuevas/<slug:id_ultima_notificacion>/',
         consultarNotificacionesNuevas, name='docLaruexConsultarNotificacionesNuevas'),

    # Muestra el listado completo de todas las notas
    path('private/docLaruex/notificaciones/',
         listaNotificaciones, name='docLaruexListaNotificaciones'),
    # Muestra el listado completo de todas las notas
    path('private/docLaruex/verNotificacion/<slug:id>/',
         verNotificacion, name='docLaruexVerNotificacion'),

    # Muestra el listado completo de todas las notas
    path('private/docLaruex/editarNotificacion/<slug:id>/',
         editarNotificacion, name='docLaruexEditarNotificacion'),

     # vista/html para eliminar una Notificación            
    path('private/docLaruex/eliminarNotificacion/<slug:id>/', eliminarNotificacion, name='docLaruexEliminarNotificacion'),



    # Carga los datos del listado de notas
    path('private/docLaruex/notificacionesDatos/',
         listaNotificacionesDatos, name='docLaruexListaNotificacionesDatos'),

     # carga los datos del listado de las notas
    path('private/docLaruex/notificacionesUsuario/', listaNotificacionesUsuario, name='docLaruexListaNotificacionesUsuario'),

    # Carga los datos del listado de usuarios
    path('private/docLaruex/notificacionesUsuarioDatos/',
         listaNotificacionesUsuarioDatos, name='docLaruexListaNotificacionesUsuarioDatos'),

     # permite agregar una reserva de procedimiento
    path('private/docLaruex/agregarReservaProcedimiento/',
         agregarReservaProcedimiento, name='docLaruexAgregarReservaProcedimiento'),

     # permite agrgar una categoria a un equipo
    path('private/docLaruex/agregarTipoEquipo/',
         agregarTipoEquipo, name='docLaruexTipoEquipo'),


    path('private/docLaruex/actualizarFormato/<slug:id>',
         actualizarFormato, name='docLaruexActualizarFormato'),

    # tras pulsar el boton [+] añade una nueva habilitación a la 
    # lista de habilitaciones (listaHabilitaciones.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarHabilitacion/',
         agregarHabilitacion, name='docLaruexAgregarHabilitacion'),

    # tras pulsar el boton [+] añade un nuevo fabricante a la 
    # lista de fabricantes (listaFabricante.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarFabricante/',
         agregarFabricante, name='docLaruexAgregarFabricante'),

    # tras pulsar el boton [+] añade un nuevo proyecto a la 
    # lista de proyectos (listaProyectos.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarProyecto/',
         agregarProyecto, name='docLaruexAgregarProyecto'),

    # url que sirve para asociar varios habilitaciones a un usuario desde 
    # la vista de Habilitaciones (listaHabilitaciones.html)
    path('private/docLaruex/asociarHabilitacion/',
         asociarHabilitacion, name='docLaruexAsociarHabilitacion'),

    # url que sirve para asociar una habilitación a todos los usuarios desde 
    # la vista de Habilitaciones (listaHabilitaciones.html)
    path('private/docLaruex/asociarHabilitacionTodosUsuarios/',
         asociarHabilitacionTodosUsuarios, name='docLaruexAsociarHabilitacionTodosUsuarios'),


    # tras pulsar el boton [+] añade un nueva acta a la 
    # lista de actas (listaActas.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarActa/',
         agregarActa, name='docLaruexAgregarActa'),
     
          
     # vista/html para eliminar un acta            
    path('private/docLaruex/eliminarActa/<slug:id>/', eliminarActa, name='docLaruexEliminarActa'),


     # tras pulsar el boton [argregar Acuerdos] añade un acuerdos al acta 
    # en (acta.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarAcuerdos/<slug:id>/',
         agregarAcuerdos, name='docLaruexAgregarAcuerdos'),

    # url que sirve para asociar varios archivos desde 
    # la tabla de archivos seleccionados en formato.html
    path('private/docLaruex/asociarArchivos/',
         asociarArchivos, name='docLaruexAsociarArchivos'),

    # la elimina una asociación de archivos 
    path('private/docLaruex/eliminarAsocicion/<slug:id_objeto_eliminar>/<slug:id_actual>/',
         eliminarAsocicion, name='docLaruexEliminarAsociacion'),

    path('private/docLaruex/calendario/',
         calendario, name='docLaruexCalendario'),

     # muestra los datos para rellanar el calendario
    path('private/docLaruex/datosCalendario/',
         datosCalendario, name='docLaruexDatosCalendario'),


# ---------------------------------------------------------
#                         FORMATOS 
# ---------------------------------------------------------
     # muestra aquellos formatos que son versiones del actual
    path('private/docLaruex/historialFormato/<slug:nombre>/<slug:procedimiento>/',
         historialFormato, name='docLaruexHistorialFormato'),
     # muestra aquellos formatos que han sido rellenados
    path('private/docLaruex/historialFormatoRellenos/<slug:nombre>/<slug:procedimiento>/',
         historialFormatoRellenos, name='docLaruexHistorialFormatoRellenos'),


# ---------------------------------------------------------
#                         OTROS 
# ---------------------------------------------------------
    path('private/docLaruex/consultarArchivo/<slug:id>/',
         consultarArchivo, name='docLaruexConsultarArchivo'),
    path('private/docLaruex/consultarArchivoEditable/<slug:id>/',
         consultarArchivoEditable, name='docLaruexConsultarArchivoEditable'),
     
    #path('private/docLaruex/tipoObjeto/<slug:tipo>', tipoObjeto, name='docLaruextipoObjeto'),

# ---------------------------------------------------------
#                         HABILITACIONES 
# ---------------------------------------------------------

     # devuelve el lista de usuarios disponibles para asociar las habilitaciones
    path('private/docLaruex/habilitacionesDatosAsociar',
         datosHabilitacionesAsociar, name='docLaruexHabilitacionesDatosAsociar'),

    # vista/html de la página con la lista de habilitaciones
    path('private/docLaruex/habilitaciones',
         ListadoHabilitaciones, name='docLaruexHabilitaciones'),

     # vista/html de la página de habilitaciones que permite desde la tabla eliminar una habilitacion dado el id_habilitacion
    path('private/docLaruex/eliminarHabilitacion/<slug:id>/',
         eliminarHabilitacion, name='docLaruexEliminarHabilitaciones'),

     # vista/html de la página de habilitaciones que permite desde la tabla 
     # eliminar una habilitacion asignada a un usuario dado el id_habilitacion y el id_usuario
     #          
    path('private/docLaruex/eliminarHabilitacionUsuario/<slug:id>/<slug:id_usuario>/',
         eliminarHabilitacionUsuario, name='docLaruexEliminarHabilitaciones'),

# ---------------------------------------------------------
#                         CONTACTOS 
# ---------------------------------------------------------
    # vista y rellanado de la página con todas los equipos
    path('private/docLaruex/contactos', ListadoContactos, name='docLaruexListadoContactos'),
    path('private/docLaruex/contactosDatos', DatosContactos, name='docLaruexContactosDatos'),
    path('private/docLaruex/contacto/<slug:id>/', verContacto, name='docLaruexVerContacto'),
    path('private/docLaruex/agregarContacto/',
         agregarContacto, name='docLaruexAgregarContacto'),         
    path('private/docLaruex/editarContacto/<slug:id>/', editarContacto, name='docLaruexEditarContacto'),         
    path('private/docLaruex/eliminarContacto/<slug:id>/', eliminarContacto, name='docLaruexEliminarContacto'),

     # devuelve el lista de usuarios disponibles para asociar las habilitaciones
     path('private/docLaruex/contactosDatosAsociarCurso', datosContactosAsociarCurso, name='docLaruexContactosDatosAsociarCurso'),

     # ---------------------------------------------------------
     #                         UBICACIONES 
     # ---------------------------------------------------------
    # vista y rellanado de la página con todas las ubicaciones ¿¿¿BORRAR???
    # path('private/docLaruex/ubicaciones', ListadoUbicaciones, name='docLaruexUbicaciones'),

    path('private/docLaruex/ubicacionesSonPadre', ListadoUbicacionesSonPadre, name='docLaruexUbicacionesSonPadre'),
    path('private/docLaruex/ubicacionesDatosSonPadre', DatosUbicacionesSonPadre, name='docLaruexUbicacionesSonPadre'),

    path('private/docLaruex/ubicacionesDatosPadre/<slug:id>/',
         DatosUbicacionesPadre, name='docLaruexUbicacionesDatosPadre'),
    path('private/docLaruex/ubicacionesDatos',
         DatosUbicaciones, name='docLaruexUbicacionesDatos'),
    path('private/docLaruex/equiposAsociados/<slug:id>/',
         EquiposAsociados, name='docLaruexequiposAsociados'),
     path('private/docLaruex/documentosAsociados/<slug:id>/',
          DocumentosAsociados, name='docLaruexdocumentosAsociados'),



# ---------------------------------------------------------
#                         EQUIPOS 
# ---------------------------------------------------------

    # vista y rellanado de la página con todas los equipos ¿¿¿BORRAR??
    #path('private/docLaruex/equipos', ListadoEquipos, name='docLaruexEquipos'),
    path('private/docLaruex/equiposDatos',
         DatosEquipos, name='docLaruexEquiposDatos'),

     
    # vista y rellanado de la página con todas los equipos
    path('private/docLaruex/equiposTipo', ListadoEquiposTipo, name='docLaruexEquiposTipo'),
    path('private/docLaruex/equiposGrupo', ListadoEquiposGrupo, name='docLaruexEquiposGrupo'),
    path('private/docLaruex/equiposCedidos', ListadoEquiposCedidos, name='docLaruexEquiposCedidos'),
    path('private/docLaruex/equiposDatosTipo/<slug:id>/',DatosEquiposTipo, name='docLaruexEquiposDatosTipo'),
    path('private/docLaruex/equiposDatosGrupo/<slug:id>/',DatosEquiposGrupo, name='docLaruexEquiposDatosGrupo'),
    path('private/docLaruex/equiposCedidosDatos/',DatosEquiposCedidos, name='docLaruexEquiposDatosCedidos'),
    path('private/docLaruex/cambiarUbicacionEquipo/<slug:id>/', CambiarUbicacionEquipo, name='docLaruexCambiarUbicacionEquipo'),
    path('private/docLaruex/agregarCodUex/<slug:id>/', agregarCodUex, name='docLaruexAgregarCodUex'),
    
    path('private/docLaruex/eliminarEquipo/<slug:id>/', EliminarEquipo, name='docLaruexEliminarEquipo'),
    path('private/docLaruex/darBajaEquipo/<slug:id>/', DarBajaEquipo, name='docLaruexDarBajaEquipo'),
    path('private/docLaruex/imprimirEquipo/<slug:id>/', ImprimirEquipo, name='docLaruexImprimirEquipo'),
    path('private/docLaruex/reportEquipo/<slug:id>/', ReportEquipo, name='docLaruexReportEquipo'),

        # vista y rellanado de la página con los equipos dados de baja 
    path('private/docLaruex/equiposBaja', ListadoEquiposBaja, name='docLaruexEquiposBaja'),
    path('private/docLaruex/equiposDatosBaja',
         DatosEquiposBaja, name='docLaruexEquiposDatosBaja'),
    #path('private/docLaruex/equipos', ListadoEquipos, name='docLaruexEquipos'),
    path('private/docLaruex/equiposDatosSinEtiqueta',
         DatosEquiposSinEtiqueta, name='docLaruexEquiposDatosSinEtiqueta'),




# ---------------------------------------------------------
#                         STOCK 
# ---------------------------------------------------------
    # Vista de la página con todos los items de los almacenes que no son inventariables
    path('private/docLaruex/listadoStock', listadoStock, name='docLaruexListadoStock'),
    
    # Rellanado de la página con todos los items de los almacenes que no son inventariables
    path('private/docLaruex/listadoStockDatos',
         DatosListadoStock, name='docLaruexListadoStockDatos'), 
         
    # Rellanado de la página con todos los items de los almacenes que no son inventariables
    path('private/docLaruex/stockDatosCategoria/<slug:idCategoria>/',
         stockDatosCategoria, name='docLaruexListadoStockDatos'), 
         
   # vista y rellanado de la página con todas los item de Stock
    path('private/docLaruex/listadoStockAlmacen', listadoStockAlmacen, name='docLaruexListadoStockAlmacen'),
         
   # vista y rellanado de la página con todas los item de Stock
    path('private/docLaruex/stockTotal', stockTotal, name='docLaruexStockTotal'),
    path('private/docLaruex/stockDatosAlmacen/<slug:id>/',
         DatosStockAlmacen, name='docLaruexStockDatosAlmacen'),
         
     # vista que permite ver el stock de una ubicación
    path('private/docLaruex/stockDatosUbicacion/<slug:id_ubicacion>/',
         DatosStockUbicacion, name='docLaruexDatosStockUbicacion'),

    # Vista de la página con todos los items en minimos de Stock de los almacenes que no son inventariables
    path('private/docLaruex/listadoStockMinimo', listadoStockMinimo, name='docLaruexListadoStockMinimo'),
    
    # Rellanado de la página con todos los item en minimos de Stock de los almacenes que no son inventariables
    path('private/docLaruex/listadoStockMinimoDatos',
         DatosListadoStockMinimo, name='docLaruexListadoStockMinimoDatos'),

    # Vista de la página con todos los items fuera de Stock de los almacenes que no son inventariables
    path('private/docLaruex/listadoFueraStock', listadoFueraStock, name='docLaruexListadoFueraStock'),
    
    # Rellanado de la página con todos los items fuera de Stock de los almacenes que no son inventariables
    path('private/docLaruex/listadoStockFueraDatos',
         DatosListadoFueraStock, name='docLaruexListadoFueraStockDatos'),
         
     
    # Edita un item de Stock en particular 
    path('private/docLaruex/hojaPedidoStock',hojaPedidoStock, name='docLaruexHojaPedidoStock'),
     

    # Edita un item de Stock en particular 
    path('private/docLaruex/hojaPedidoStockAlmacen/<slug:id_almacen>/',
         hojaPedidoStockAlmacen, name='docLaruexHojaPedidoStockAlmacen'), 

    # Edita un item de Stock en particular 
    path('private/docLaruex/hojaPedidoStockCategoria/<slug:id_categoria>/',
         hojaPedidoStockCategoria, name='docLaruexHojaPedidoStockCategoria'), 

    # vista de los datos de un item de stock 
    path('private/docLaruex/verItemStock/<slug:id>/', verItemStock, name='docLaruexVerItemStock'),

    
    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/retiradasStockDatos/<slug:item>',
         DatosRetiradasStock, name='docLaruexRetiradasStockDatos'),

    
    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/retiradasStockErrorDatos/<slug:item>',
         DatosRetiradasStockError, name='docLaruexRetiradasStockErrorDatos'),  

    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/agregarStock',
         agregarStock, name='docLaruexAgregarStock'),

    
    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/agregarUnidadesStock/<slug:item>/',
         agregarUnidadesStock, name='docLaruexAgregarUnidadesStock'),

    
    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/agregarUnidadesStockProveedor/<slug:item>/',
         agregarUnidadesStockProveedor, name='docLaruexAgregarUnidadesStockProveedor'),

    
    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/retirarStock/<slug:item>/',
         retirarStock, name='docLaruexRetirarStock'),

     # devuelve una retirada el item de stock 
    path('private/docLaruex/devolverStock/<slug:id>/',
         devolverStock, name='docLaruexDevolverStock'),

    # Rellanado de la página con el listado de retiradas de un item no inventariables en concreto 
    path('private/docLaruex/retirarStockUbicacion/<slug:item>/',
         retirarStockUbicacion, name='docLaruexRetirarStockUbicacion'),

    # Edita un item de Stock en particular 
    path('private/docLaruex/editarStock/<slug:id>/',
         editarStock, name='docLaruexEditarStock'), 

    # Devuelve el historico de compras de un item en particular 
    path('private/docLaruex/historicoProveedoresDatos/<slug:id>/',
         DatosHistoricoProveedores, name='docLaruexDatosHistoricoProveedores'), 


    # Elimina un un item de Stock en particular 
    path('private/docLaruex/eliminarStock/<slug:id>/',
         eliminarStock, name='docLaruexEliminarStock'), 


    # Elimina un un item de Stock en particular 
    path('private/docLaruex/solicitarMaterial/',
         solicitarMaterial, name='docLaruexSolicitarMaterial'),    
     # Elimina un un item de Stock en particular 
    path('private/docLaruex/materialDisponible/',
         materialDisponible, name='docLaruexMaterialDisponible'),  
    ################### Generación de PDF ####################

    #url(r'^simple_pdf/$', PDFTemplateView.as_view(template_name='reportEquipo.html', filename='report_Equipo.pdf'), name='report_Equipo'),

# ---------------------------------------------------------
#                         CURSOS 
# ---------------------------------------------------------
    # vista que permite ver el listado de cursos cursos.
    #path('private/docLaruex/cursos', ListadoCursos, name='docLaruexCursos'),
    
    # vista que permite generar un certificado para un curso.
    path('private/docLaruex/generarCertificadoCurso/<slug:id>/', CertificadoCurso, name='docLaruexCertificadoCurso'),

     ################# Relación de Archivos #################   
    
     # devuelve el lista de los usuarios
    path('private/docLaruex/archivosDatosAsociar',
         datosArchivosAsociar, name='docLaruexArchivosDatosAsociar'),

     # devuelve el lista de los usuarios

    path('private/docLaruex/asociarArchivo/<slug:id>/',
         asociarArchivo, name='docLaruexAsociarArchivo'),

    path('private/docLaruex/asociarAsistentesCurso/', asociarAsistentesCurso, name='docLaruexAsociarAsistentesCurso'),


    path('private/docLaruex/asistentesCursoDatos/<slug:id>/',
         datosAsistentesCurso, name='docLaruexDatosAsistentesCurso'),


    path('private/docLaruex/asistentesCursoTipoDatos/<slug:id>/<slug:tipo>/',
         datosAsistentesCursoTipo, name='docLaruexDatosAsistentesCursoTipo'),
         
    path('private/docLaruex/eliminarAsistente/<slug:id_asistente>/<slug:id_curso>/',
         eliminarAsistente, name='docLaruexEliminarAsistente'),
         
    path('private/docLaruex/editarContenidoCurso/<slug:id_curso>/<slug:id_contenido>/',
         editarContenidoCurso, name='docLaruexEditarContenidoCurso'),
         
    path('private/docLaruex/agregarContenidoCurso/',
         agregarContenidoCurso, name='docLaruexAgregarContenidoCurso'),
         
    path('private/docLaruex/eliminarContenidoCurso/<slug:idCurso>/<slug:idContenido>/',
         eliminarContenidoCurso, name='docLaruexEliminarContenidoCurso'),
     
     

# ---------------------------------------------------------
#                         LLAVES 
# ---------------------------------------------------------    
# # vista/html de la página de listaLlaves
    path('private/docLaruex/llaves',
         listadoLlaves, name='docLaruexLlaves'),

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Llaves (listaLlaves.html)
    path('private/docLaruex/llavesDatos',
         DatosLlaves, name='docLaruexLlavessDatos'),

    # Obtiene los datos que rellenan la tabla que se encuentra en el 
    # collapse lista de Llaves (listaLlaves.html)
    path('private/docLaruex/llavesAlmacenadasUbicacionsDatos/<slug:id_ubicacion>/',
         datosLlavesAlmacenadasUbicacion, name='docLaruexLlavesAlmacenadasUbicacionDatos'),

    # vista/html de la página de una llave en particular 
    path('private/docLaruex/verLlave/<slug:id>/',
         verLlave, name='docLaruexVerLlave'),

    # permite editar una llave 
    path('private/docLaruex/editarLlave/<slug:id>/',
         editarLlave, name='docLaruexEditarLlave'), 

    # tras pulsar el boton [+] añade un nuevo proveedor a la 
    # lista de proveedores (listaLlaves.html), esto queda registrado en la BBDD
    path('private/docLaruex/agregarLlave/',
         agregarLlave, name='docLaruexAgregarLlave'),

     # vista/html para eliminar un Llave            
    path('private/docLaruex/eliminarLlave/<slug:id>/', eliminarLlave, name='docLaruexEliminarLlave'),


    
# ---------------------------------------------------------
#                         Generar QR 
# ---------------------------------------------------------  
     # vista/html para generar un qr            
    path('private/docLaruex/generarQR/<path:url>/<slug:codigo>', generarQR, name='docLaruexGenerarQR'),
     # vista/html para generar un qr            
    path('private/docLaruex/generadorQR', generadorQR, name='docLaruexGeneradorQR'),

    

        
# ---------------------------------------------------------
#                         Eventos 
# ---------------------------------------------------------  
    path('private/docLaruex/eventos', eventos, name='docLaruexEventos'),
    path('private/docLaruex/eventosDatos', datosEventos, name='docLaruexEventosDatos'),
    path('private/docLaruex/eventosDatosTipo/<str:tipoEvento>/', datosEventosTipo, name='docLaruexEventosDatosTipo'),
    path('private/docLaruex/eliminarEvento/<slug:id_evento>/', eliminarEvento, name='docLaruexEliminarEvento'),
    path('private/docLaruex/agregarEvento/', agregarEvento, name='docLaruexAgregarEvento'),
    path('private/docLaruex/editarEvento/<slug:id>/', editarEvento, name='docLaruexEditarEvento'), 
    path('private/docLaruex/equiposUbicacionesDatos', DatosEquiposUbicaciones, name='docLaruexEquiposUbicacionesDatos'),
    path('private/docLaruex/equiposUbicacionesDatosFiltro/<str:tipo>/', DatosEquiposUbicacionesFiltro, name='docLaruexEquiposUbicacionesDatosFiltro'),
    path('private/docLaruex/formatoDatosFiltrados/<slug:procedimiento>/', formatosDatosFiltrados, name='docLaruexFormatosDatosFiltrados'),
    
# ---------------------------------------------------------
#                         Tareas 
# ---------------------------------------------------------  
    path('private/docLaruex/agregarTarea/<slug:id_evento>/', agregarTarea, name='docLaruexAgregarTarea'), 
    path('private/docLaruex/tareas', tareas, name='docLaruexTareas'),
    path('private/docLaruex/tareasDatos', datosTareas, name='docLaruexTareasDatos'),
    path('private/docLaruex/verTarea/<slug:id>/', verTarea, name='docLaruexVerTarea'), 
    path('private/docLaruex/eliminarTarea/<slug:id>/', eliminarTarea, name='docLaruexEliminarTarea'),
    path('private/docLaruex/registrosTareaDatos/<slug:id_tarea>/', datosRegistroTareas, name='docLaruexRegistroTareasDatos'),
    path('private/docLaruex/verHistorico/<slug:id_historico>/', verHistorico, name='docLaruexVerHistorico'),
    path('private/docLaruex/completarHistorico', completarHistorico, name='docLaruexCompletarHistorico'),
    path('private/docLaruex/reportRegistroTarea/<slug:id>/', reportRegistroTarea, name='docLaruexReportRegistroTarea'),
    path('private/docLaruex/editarTarea/<slug:id>/',editarTarea, name='docLaruexEditarTarea'),
    path('private/docLaruex/editarRegistroTarea/<slug:id>/',editarRegistroTarea, name='docLaruexEditarRegistroTarea'),
    path('private/docLaruex/cancelarRegistroTarea', cancelarRegistroTarea, name='docLaruexCancelarRegistroTarea'),
    path('private/docLaruex/eliminarRegistroTarea/<slug:id>/', eliminarRegistroTarea, name='docLaruexEliminarRegistroTarea'),
    path('private/docLaruex/tareasProximas', tareasProximas, name='docLaruexTareasProximas'),
    path('private/docLaruex/tareasProximasDatos', datosTareasProximas, name='docLaruexTareasProximasDatos'),

    #vista de los mantenimientos asociados al equipo o ubicacion

    path('private/docLaruex/verMantenimientosAsociados/<slug:id>/', verMantenimientosAsociados, name='docLaruexVerMantenimientosAsociados'), 
    path('private/docLaruex/datosMantenimientosAsociados/<slug:id>/', datosMantenimientosAsociados, name='docLaruexMantenimientosAsociadosDatos'),
    


    
# ---------------------------------------------------------
#              OPERATIVIDAD DE LAS APLICACIONES 
# ---------------------------------------------------------
    path('private/docLaruex/operatividadAplicaciones', operatividadAplicaciones, name='docLaruexOperatividadAplicaciones'),
    path('private/docLaruex/datosOperatividadAplicaciones', datosOperatividadAplicaciones, name='docLaruexDatosOperatividadAplicaciones'),
    path('private/docLaruex/eliminarProceso/<str:proceso>/<str:nombre>/', eliminarProcesoAplicaciones, name='docLaruexEliminarProceso'),
    path('private/docLaruex/paralizarProceso/<str:proceso>/<str:nombre>/', paralizarProcesoAplicaciones, name='docLaruexParalizarProceso'),


]

