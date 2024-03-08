from django.urls import path
from .views import *

app_name = 'gestionmuestras'

urlpatterns = [
    path('private/gestionmuestras/', opcionesGestionMuestras, name='gestmuesOpciones'),
    path('private/gestionmuestras/listadoMuestras/', listadoMuestras, name='gestmuesListadoMuestras'),
    path('private/gestionmuestras/listadoMuestrasDatos/', listadoMuestrasDatos, name='gestmuesListadoMuestras2'),
    path('private/gestionmuestras/infoMuestraForm/', getInfoMuestraForm, name='gestmuesGetInfoMuestraForm'),
    path('private/gestionmuestras/infoMuestra/solicitarAlicuotas/<slug:id_muestra>/', getAlicuotasMuestra, name='gestmuesGetAlicuotasMuestra'),
    path('private/gestionmuestras/botonesGestion/', getBotonesGestion, name='gestmuesGetBotonesGestion'),

    # insertar muetras
    path('private/gestionmuestras/insertarMuestra/', insertarMuestra, name='gestmuesInsertarMuestra'),
    path('private/gestionmuestras/insertarMuestra/consultarParametrosTipo/<slug:tipo>/', consultarParametrosTipo, name='gestmuesConsultarParametrosTipo'),
    path('private/gestionmuestras/modificarMuestra/<slug:id_muestra>/', modificarMuestra, name='gestmuesModificarMuestra'),
    path('private/gestionmuestras/insertarAlicuotas/<slug:id_muestra>/', insertarAlicuotas, name='gestmuesInsertarAlicuotas'),
    path('private/gestionmuestras/insertarDeterminaciones/', insertarDeterminaciones, name='gestmuesInsertarDeterminaciones'),
    path('private/gestionmuestras/insertarTratamientos/', insertarTratamientos, name='gestmuesInsertarTratamientos'),
    path('private/gestionmuestras/finalizarInsercion/', finalizarInsercion, name='gestmuesFinalizarInsercion'),
    path('private/gestionmuestras/obtenerValoresUltimaMuestra/', obtenerValoresUltimaMuestra, name='gestmuesObtenerValoresUltimaMuestra'),
    path('private/gestionmuestras/obtenerComentarioRecogidaGeneral/', obtenerComentarioRecogidaGeneral, name='gestmuesObtenerComentarioRecogidaGeneral'),

    # informes
    path('private/gestionmuestras/muestrasInforme/', muestrasInforme, name='gestmuesMuestrasInformes'),
    path('private/gestionmuestras/muestrasInformeDatos/', muestrasInformeDatos, name='gestmuesMuestrasInformesDatos'),

    
    path('private/gestionmuestras/listadoChurros/', listadoChurros, name='gestmuesListadoChurros'),
    path('private/gestionmuestras/listadoChurrosDatos/', listadoChurrosDatos, name='gestmuesListadoChurros2'),

    # gestion muestras
    path('private/gestionmuestras/infoMuestra/<slug:id_muestra>/', getInfoMuestra, name='gestmuesGetInfoMuestra'),
    #eliminar alicutoa
    path('private/gestionmuestras/borrarAlicuota/<slug:id_alicuota>/', borrarAlicuota, name='gestmuesBorrarAlicuota'),
    # duplicar alicutoa
    path('private/gestionmuestras/duplicarAlicuota/', duplicarAlicuota, name='gestmuesDuplicarAlicuota'),

    # consultor de medidas
    path('private/gestionmuestras/consultorMedidas/', consultorMedidas, name='gestmuesConsultorMedidas'),
    path('private/gestionmuestras/infoAlicuota/<slug:id_alicuota>/', infoAlicuota, name='gestmuesInfoAlicuota'),

    # finalizar muestras
    path('private/gestionmuestras/verificarMuestra/', verificarMuestra, name='gestmuesVerificarMuestra'),

    # alfa
    path('private/gestionmuestras/capturarInformeAlfa/', capturarInformeAlfa, name='gestmuesCapturarInformeAlfa'),
    # copuma
    path('private/gestionmuestras/capturarExcelCopuma/', capturarExcelCopuma, name='gestmuesCapturarExcelCopuma'),
    # capturar dbf
    path('private/gestionmuestras/capturarDBFgestmues/', capturarDBFgestmues, name='gestmuesCapturarDBFgestmues'),
    # Consulta duplicados alfa beta
    path('private/gestionmuestras/consultaDuplicados/', consultaDuplicados, name='gestmuesConsultaDuplicados'),


    # Consulta de muestras a recoger   
    path('private/gestionmuestras/consultarMuestrasRecoger/', consultarMuestrasRecoger, name='gestmuesConsultarMuestrasRecoger'), 
    path('private/gestionmuestras/consultarMuestrasRecogerDatos/', consultarMuestrasRecogerDatos, name='gestmuesConsultarMuestrasRecogerDatos'),



    # Consulta muestras VRAEX
    path('private/gestionmuestras/consultarVRAEx/', consultarVRAEx, name='gestmuesConsultarVRAEx'),

    # Creacion de codigos de barras
    path('private/gestionmuestras/almacenarCodigosBarras/', almacenarCodigosBarras, name='gestmuesAlmacenarCodigosBarras'),
    path('private/gestionmuestras/renovarCodigosBarras/', renovarCodigosBarras, name='gestmuesRenovarCodigosBarras'),
    path('private/gestionmuestras/consultarEtiquetas/', consultarEtiquetas, name='gestmuesConsultarEtiquetas'),
    path('private/gestionmuestras/consultarEtiquetasSeleccionadas/', consultarEtiquetasSeleccionadas, name='gestmuesConsultarEtiquetasSeleccionadas'),
    path('private/gestionmuestras/crearCodigosBarras/', crearCodigosBarras, name='gestmuesCrearCodigosBarras'),
    path('private/gestionmuestras/vaciarCodigosBarras/', vaciarCodigosBarras, name='gestmuesCrearCodigosBarras'),
    path('private/gestionmuestras/modificarCodigosExistentes/', modificarCodigosExistentes, name='gestmuesModificarCodigosExistentes'),
    path('private/gestionmuestras/eliminarCodigosExistentes/<slug:codigo>/', eliminarCodigosExistentes, name='gestmuesEliminarCodigosExistentes'),
    path('private/gestionmuestras/etiquetasSeleccionar/<slug:id>/', etiquetasSeleccionar, name='gestmuesEtiquetasSeleccionar'),



    # CRUD Gestion de muestras
    # urls para gestion de codigos de muestras
    path('private/gestionmuestras/gestionCodigosMuestras/', gestionCodigosMuestras, name='gestmuesGestionCodigosMuestras'),
    path('private/gestionmuestras/gestionCodigosMuestrasDatos/', gestionCodigosMuestrasDatos, name='gestmuesGestionCodigosMuestrasDatos'),
    path('private/gestionmuestras/gestionCodigosMuestrasNuevo/', gestionCodigosMuestrasNuevo, name='gestmuesGestionCodigosMuestrasNuevo'),
    path('private/gestionmuestras/gestionCodigosMuestrasEditar/', gestionCodigosMuestrasEditar, name='gestmuesGestionCodigosMuestrasEditar'),
    path('private/gestionmuestras/gestionCodigosMuestrasBorrar/', gestionCodigosMuestrasBorrar, name='gestmuesGestionCodigosMuestrasBorrar'),

    # urls para gestion de clientes
    path('private/gestionmuestras/gestionClientes/', gestionClientes, name='gestmuesGestionClientes'),
    path('private/gestionmuestras/gestionClientesDatos/', gestionClientesDatos, name='gestmuesGestionClientesDatos'),
    path('private/gestionmuestras/gestionClientesNuevo/', gestionClientesNuevo, name='gestmuesGestionClientesNuevo'),
    path('private/gestionmuestras/gestionClientesEditar/', gestionClientesEditar, name='gestmuesGestionClientesEditar'),
    path('private/gestionmuestras/gestionClientesBorrar/', gestionClientesBorrar, name='gestmuesGestionClientesBorrar'),

    # urls para memorias
    path('private/gestionmuestras/gestionMemorias/', gestionMemorias, name='gestmuesGestionMemorias'),
    path('private/gestionmuestras/gestionMemoriasDatos/', gestionMemoriasDatos, name='gestmuesGestionMemoriasDatos'),
    path('private/gestionmuestras/gestionMemoriasNuevo/', gestionMemoriasNuevo, name='gestmuesGestionMemoriasNuevo'),
    path('private/gestionmuestras/gestionMemoriasEditar/', gestionMemoriasEditar, name='gestmuesGestionMemoriasEditar'),
    path('private/gestionmuestras/gestionMemoriasBorrar/', gestionMemoriasBorrar, name='gestmuesGestionMemoriasBorrar'),

    # urls para muestra actual codigo
    path('private/gestionmuestras/gestionMuestraActualCodigo/', gestionMuestraActualCodigo, name='gestmuesGestionMuestraActualCodigo'),
    path('private/gestionmuestras/gestionMuestraActualCodigoDatos/', gestionMuestraActualCodigoDatos, name='gestmuesGestionMuestraActualCodigoDatos'),
    path('private/gestionmuestras/gestionMuestraActualCodigoNuevo/', gestionMuestraActualCodigoNuevo, name='gestmuesGestionMuestraActualCodigoNuevo'),
    path('private/gestionmuestras/gestionMuestraActualCodigoEditar/', gestionMuestraActualCodigoEditar, name='gestmuesGestionMuestraActualCodigoEditar'),
    path('private/gestionmuestras/gestionMuestraActualCodigoBorrar/', gestionMuestraActualCodigoBorrar, name='gestmuesGestionMuestraActualCodigoBorrar'),

    # urls para parametros
    path('private/gestionmuestras/gestionParametro/', gestionParametro, name='gestmuesGestionParametros'),
    path('private/gestionmuestras/gestionParametroDatos/', gestionParametroDatos, name='gestmuesGestionParametrosDatos'),
    path('private/gestionmuestras/gestionParametroNuevo/', gestionParametroNuevo, name='gestmuesGestionParametrosNuevo'),
    path('private/gestionmuestras/gestionParametroEditar/', gestionParametroEditar, name='gestmuesGestionParametrosEditar'),
    path('private/gestionmuestras/gestionParametroBorrar/', gestionParametroBorrar, name='gestmuesGestionParametrosBorrar'),


    # urls para gestion de la relacion de controles con tratamientos
    path('private/gestionmuestras/gestionRelacionControlTratamiento/', gestionRelacionControlTratamiento, name='gestmuesGestionRelacionControlTratamiento'),
    path('private/gestionmuestras/gestionRelacionControlTratamientoDatos/', gestionRelacionControlTratamientoDatos, name='gestmuesGestionRelacionControlTratamientoDatos'),
    path('private/gestionmuestras/gestionRelacionControlTratamientoNuevo/', gestionRelacionControlTratamientoNuevo, name='gestmuesGestionRelacionControlTratamientoNuevo'),
    path('private/gestionmuestras/gestionRelacionControlTratamientoEditar/', gestionRelacionControlTratamientoEditar, name='gestmuesGestionRelacionControlTratamientoEditar'),
    path('private/gestionmuestras/gestionRelacionControlTratamientoBorrar/', gestionRelacionControlTratamientoBorrar, name='gestmuesGestionRelacionControlTratamientoBorrar'),

    # urls para gestion de relaciones determinaciones con tratamientos
    path('private/gestionmuestras/gestionRelacionDeterminacionTratamiento/', gestionRelacionDeterminacionTratamiento, name='gestmuesGestionRelacionDeterminacionTratamiento'),
    path('private/gestionmuestras/gestionRelacionDeterminacionTratamientoDatos/', gestionRelacionDeterminacionTratamientoDatos, name='gestmuesGestionRelacionDeterminacionTratamientoDatos'),
    path('private/gestionmuestras/gestionRelacionDeterminacionTratamientoNuevo/', gestionRelacionDeterminacionTratamientoNuevo, name='gestmuesGestionRelacionDeterminacionTratamientoNuevo'),
    path('private/gestionmuestras/gestionRelacionDeterminacionTratamientoEditar/', gestionRelacionDeterminacionTratamientoEditar, name='gestmuesGestionRelacionDeterminacionTratamientoEditar'),
    path('private/gestionmuestras/gestionRelacionDeterminacionTratamientoBorrar/', gestionRelacionDeterminacionTratamientoBorrar, name='gestmuesGestionRelacionDeterminacionTratamientoBorrar'),

    # urls para gestion de frases predefinidas
    path('private/gestionmuestras/gestionFrasePredefinida/', gestionFrasePredefinida, name='gestmuesGestionFrasePredefinida'),
    path('private/gestionmuestras/gestionFrasePredefinidaDatos/', gestionFrasePredefinidaDatos, name='gestmuesGestionFrasePredefinidaDatos'),
    path('private/gestionmuestras/gestionFrasePredefinidaNuevo/', gestionFrasePredefinidaNuevo, name='gestmuesGestionFrasePredefinidaNuevo'),
    path('private/gestionmuestras/gestionFrasePredefinidaEditar/', gestionFrasePredefinidaEditar, name='gestmuesGestionFrasePredefinidaEditar'),
    path('private/gestionmuestras/gestionFrasePredefinidaBorrar/', gestionFrasePredefinidaBorrar, name='gestmuesGestionFrasePredefinidaBorrar'),

    # urls para gestion de determinaciones
    path('private/gestionmuestras/gestionDeterminacion/', gestionDeterminacion, name='gestmuesGestionDeterminacion'),
    path('private/gestionmuestras/gestionDeterminacionDatos/', gestionDeterminacionDatos, name='gestmuesGestionDeterminacionDatos'),
    path('private/gestionmuestras/gestionDeterminacionNuevo/', gestionDeterminacionNuevo, name='gestmuesGestionDeterminacionNuevo'),
    path('private/gestionmuestras/gestionDeterminacionEditar/', gestionDeterminacionEditar, name='gestmuesGestionDeterminacionEditar'),
    path('private/gestionmuestras/gestionDeterminacionBorrar/', gestionDeterminacionBorrar, name='gestmuesGestionDeterminacionBorrar'),

    # urls para gestion de tratamientos
    path('private/gestionmuestras/gestionTratamiento/', gestionTratamiento, name='gestmuesGestionTratamiento'),
    path('private/gestionmuestras/gestionTratamientoDatos/', gestionTratamientoDatos, name='gestmuesGestionTratamientoDatos'),
    path('private/gestionmuestras/gestionTratamientoNuevo/', gestionTratamientoNuevo, name='gestmuesGestionTratamientoNuevo'),
    path('private/gestionmuestras/gestionTratamientoEditar/', gestionTratamientoEditar, name='gestmuesGestionTratamientoEditar'),
    path('private/gestionmuestras/gestionTratamientoBorrar/', gestionTratamientoBorrar, name='gestmuesGestionTratamientoBorrar'),

    # urls para gestion de relacion tratamiento con responsables
    path('private/gestionmuestras/gestionRelacionTratamientoResponsable/', gestionRelacionTratamientoResponsable, name='gestmuesGestionRelacionTratamientoResponsable'),
    path('private/gestionmuestras/gestionRelacionTratamientoResponsableDatos/', gestionRelacionTratamientoResponsableDatos, name='gestmuesGestionRelacionTratamientoResponsableDatos'),
    path('private/gestionmuestras/gestionRelacionTratamientoResponsableNuevo/', gestionRelacionTratamientoResponsableNuevo, name='gestmuesGestionRelacionTratamientoResponsableNuevo'),
    path('private/gestionmuestras/gestionRelacionTratamientoResponsableEditar/', gestionRelacionTratamientoResponsableEditar, name='gestmuesGestionRelacionTratamientoResponsableEditar'),
    path('private/gestionmuestras/gestionRelacionTratamientoResponsableBorrar/', gestionRelacionTratamientoResponsableBorrar, name='gestmuesGestionRelacionTratamientoResponsableBorrar'),
    
    # urls para gestion de relacion tratamiento con muestras codigos
    path('private/gestionmuestras/gestionRelacionTratamientoMuestraCodigo/', gestionRelacionTratamientoMuestraCodigo, name='gestmuesGestionRelacionTratamientoMuestraCodigo'),
    path('private/gestionmuestras/gestionRelacionTratamientoMuestraCodigoDatos/', gestionRelacionTratamientoMuestraCodigoDatos, name='gestmuesGestionRelacionTratamientoMuestraCodigoDatos'),
    path('private/gestionmuestras/gestionRelacionTratamientoMuestraCodigoNuevo/', gestionRelacionTratamientoMuestraCodigoNuevo, name='gestmuesGestionRelacionTratamientoMuestraCodigoNuevo'),
    path('private/gestionmuestras/gestionRelacionTratamientoMuestraCodigoEditar/', gestionRelacionTratamientoMuestraCodigoEditar, name='gestmuesGestionRelacionTratamientoMuestraCodigoEditar'),
    path('private/gestionmuestras/gestionRelacionTratamientoMuestraCodigoBorrar/', gestionRelacionTratamientoMuestraCodigoBorrar, name='gestmuesGestionRelacionTratamientoMuestraCodigoBorrar'),


]
