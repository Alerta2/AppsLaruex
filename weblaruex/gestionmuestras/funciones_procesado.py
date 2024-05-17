import unittest
import re

from dbfread import DBF
import json

import sys  
from django.conf import settings
import pandas as pd
from gestionmuestras.modelalfabeta import *
from gestionmuestras.models_nuevo import *

from datetime import datetime
import pytz
import PyPDF2

# procesamiento de codigos viejos

def separar_codigo_viejo(cadena):
    cadena = cadena.upper().replace(" ","")
    match_numeros = re.match(r'^(\d+)', cadena)
    numeros = int(match_numeros.group(1)) if match_numeros else ""

    match_letras = re.search(r'([A-Za-z]+)', cadena)
    letras = match_letras.group(1) if match_letras else ""

    match_fecha = re.search(r'(\d{2})(\d{2})(\d{2,4})$', cadena)
    dia = int(match_fecha.group(1)) if match_fecha else ""
    mes = int(match_fecha.group(2)) if match_fecha else ""
    anio = int(match_fecha.group(3)) if match_fecha else ""

    return numeros, letras, dia, mes, anio

class TestSepararCodigoViejo(unittest.TestCase):
    def test_separar_cadena_numeros_letras_fecha(self):
        cadena = "461PO220322"
        resultado_esperado = ("461", "PO", "22", "03", "22")
        resultado_obtenido = separar_codigo_viejo(cadena)
        self.assertEqual(resultado_obtenido, resultado_esperado)

    def test_separar_cadena_sin_numeros(self):
        cadena = "PO220322"
        resultado_esperado = ("", "PO", "22", "03", "22")
        resultado_obtenido = separar_codigo_viejo(cadena)
        self.assertEqual(resultado_obtenido, resultado_esperado)

    def test_separar_cadena_sin_letras(self):
        cadena = "461220322"
        resultado_esperado = ("461", "", "22", "03", "22")
        resultado_obtenido = separar_codigo_viejo(cadena)
        self.assertEqual(resultado_obtenido, resultado_esperado)

    def test_separar_cadena_sin_fecha(self):
        cadena = "461PO"
        resultado_esperado = ("461", "PO", "", "", "")
        resultado_obtenido = separar_codigo_viejo(cadena)
        self.assertEqual(resultado_obtenido, resultado_esperado)

    def test_separar_cadena_vacia(self):
        cadena = ""
        resultado_esperado = ("", "", "", "", "")
        resultado_obtenido = separar_codigo_viejo(cadena)
        self.assertEqual(resultado_obtenido, resultado_esperado)

# procesado dbf recogida general

def procesarDBFgestmues(fichero):
    recogida_general = json.load(open(settings.MEDIA_ROOT+'/gestionMuestras/recogida.json'))
    # recogida_general = {"recogidas":[]}
    
    for record in DBF(fichero, encoding='latin-1'):
        elementos = [elemento for elemento in recogida_general["recogidas"] if elemento["NUMERO"] == record['NUMERO']]
        recogida = {"NUMERO":record['NUMERO'],"CSN":record['CSN'],"COD_PRO":record['COD_PRO'],"COD_MEMO":record['COD_MEMO'],"RECOGE":record["RECOGE"],"SUMINIST":record["SUMINIST"],"OBSERV":record["OBSERV"],"MOD_NOMBRE":record["MOD_NOMBRE"],"MOD_FECHA":str(record["MOD_FECHA"]),"C_TRILLO":record["C_TRILLO"]}
        if len(elementos) == 0:
            print("nuevo elemento", recogida)
            recogida_general["recogidas"].append(recogida)
        else:
            print("elemento encontrado", recogida)
            if len(elementos) == 1:
                print("elemento encontrado", elementos[0])
                if elementos[0]["CSN"] == recogida["CSN"]:
                    print("el elemento coincide")
                else:
                    print("el elemento no coincide")
                    recogida_general["recogidas"].append(recogida)
            else:
                print("elementos encontrados", elementos)
                input("pulsa una tecla para continuar")

    with open(settings.MEDIA_ROOT+'/gestionMuestras/recogida.json', 'w') as archivo:
        json.dump(recogida_general, archivo, indent=4)
    
    return recogida_general


# procesado informe pdf alfa

def procesarInformeAlfa(fichero):
    from pdfquery import PDFQuery

    datos = {}
    pdf = PDFQuery(fichero)
    pdf.load()

    text_elements = pdf.pq('LTTextBoxHorizontal')

    def convertir(text):
        if "E-" in text:
            numero = text.replace("E-","E-0").replace(",",".")
        elif "E" in text:
            numero = text.replace("E","E+0").replace(",",".")
        elif "E0" in text:
            numero = text.replace("E0","").replace(",",".")
        else:
            numero = text.replace(",",".")
        return float(numero)


    datos["codigo_muestra"] = text_elements[6].text.replace("Código de la muestra: ","")

    recogida = json.load(open(settings.MEDIA_ROOT+'/gestionMuestras/recogida.json'))
    codigo_parseado = separar_codigo_viejo(datos["codigo_muestra"])


    elementos = [elemento for elemento in recogida["recogidas"] if elemento["NUMERO"] == codigo_parseado[0] and elemento["CSN"] == codigo_parseado[1]]

    datos["muestras_encontradas"] = elementos
    datos["codigo_reducido"] = text_elements[7].text.replace(" ","")
    datos["tipo"] = text_elements[8].text.replace(" ","")
    datos["fecha_recogida"] = text_elements[9].text.replace(" ","")
    datos["fecha_medida"] = text_elements[10].text.replace(" ","")
    datos["tiempo_medida"] = text_elements[11].text.replace(" ","")
    datos["masa"] = text_elements[12].text.replace(" ","")
    datos["detector"] = text_elements[13].text.replace(" ","")
    datos["archivo_fondo"] = text_elements[15].text.replace(" ","")
    datos["tiempo_fondo"] = text_elements[16].text.replace(" ","")

    datos["medidas"] = []
    actividad = False
    # loop over elements in text_elements getting index

    for i, text in enumerate(text_elements):        
        if "actividades" in text.text:
            actividad = True
        if actividad:
            if "Ae " in text.text:
                datos["unidad"] = text_elements[i+1].text.replace("(","").replace(")","").replace(" ","")
            if any(item == text.text.replace(" ","") for item in ["U-234","U-235","U-238","U-total"]):
                datos["medidas"].append({"medida":text_elements[i].text,"valor": convertir(text_elements[i+1].text), "error": convertir(text_elements[i+3].text), "amd": convertir(text_elements[i+2].text)})
            elif any(item == text.text.replace(" ","") for item in ["TH-230","TH-229","TH-228","TH-232","RA-226","RA-224","RA-228","PU-239+240","PO-210","PB-210","AM-241"]):
                datos["medidas"].append({"medida":text_elements[i].text,"valor": convertir(text_elements[i+1].text), "error": convertir(text_elements[i+2].text), "amd": convertir(text_elements[i+3].text)})
            if "RendimientoQuímico:" == text.text.replace(" ",""):
                if text_elements[i+3].text.replace(" ","") == "±":
                    datos["rendimiento"] = {"valor": convertir(text_elements[i+1].text.replace(" %","")), "error": convertir(text_elements[i+2].text.replace(" %",""))}
                elif text_elements[i+2].text.replace(" ","") == "±":
                    datos["rendimiento"] = {"valor": convertir(text_elements[i+1].text.replace(" %","")), "error": convertir(text_elements[i-1].text.replace(" %",""))}
                else:
                    datos["rendimiento"] = {"valor": convertir(text_elements[i+2].text.replace(" %","")), "error": convertir(text_elements[i+3].text.replace(" %",""))}

    return datos

def procesarExcelCopuma(fichero):
    # read excel file line by line defining header
    df = pd.read_excel(fichero, sheet_name=None, header=None)
    # print the rows of the first sheet
    # print the first and sencond column of every row one by one
    no_analizadas = []
    varias_muestras = []
    for index, row in df['Hoja1'].iterrows():
        
        recogida = json.load(open(settings.MEDIA_ROOT+'/gestionMuestras/recogida.json'))
        codigo_parseado = separar_codigo_viejo(row[0])
        elementos = [elemento for elemento in recogida["recogidas"] if elemento["NUMERO"] == codigo_parseado[0] and elemento["CSN"] == codigo_parseado[1]]
        
        if len(elementos) == 0:
            no_analizadas.append(row[0])
        else:
            if len(elementos) > 1:
                varias_muestras.append(row[0])
            else:
                correctoRecogida, recogida, historico = obtenerRecogidaEHistorico(row[0], elementos, codigo_parseado)
                muestraAB, alicuotaAB, medidaAB, cantidadMedidasAB = consultarRegistrosAlfabeta(row[0], row[1])
                if correctoRecogida and alicuotaAB is not None:
                    usuario = Usuarios.objects.using('gestion_muestras').filter(identificador=1).get()
                    analitica = Determinaciones.objects.using('gestion_muestras').filter(nombre="ESTRONCIO-90").get()
                    alicuota = obtenerAlicuota(historico, analitica, usuario, alicuotaAB.fechafinpreparacion, alicuotaAB.volumen)

                    if cantidadMedidasAB > 0:
                        if cantidadMedidasAB > 1:
                            medidaID = medidaAB[0].medida.split("-")
                        else:
                            medidaID = medidaAB.medida.split("-")
                        fecha_medida = medidaID[2]+"-"+medidaID[3]+"-"+medidaID[4]+"+00:00"
                        tratamiento = Tratamiento.objects.using('gestion_muestras').filter(descripcion="Medida Estroncio").get()
                        analiticaTratamiento = obtenerTratamiento(alicuota, tratamiento, alicuotaAB.fechafinpreparacion, fecha_medida, alicuotaAB.codigoreducido, usuario)

                        equipo_medida = medidaID[1][0]
                        if cantidadMedidasAB == 1:
                            medidas = crearMedidas(alicuota, fecha_medida, medidaAB.tblanco, equipo_medida, medidaAB.actividad, medidaAB.incertidumbrecombinada, medidaAB.actividadminimadetectable, medidaAB.rq, "Bq/L")
                        else:
                            for m in medidaAB:
                                medidas = crearMedidas(alicuota, fecha_medida, m.tblanco, equipo_medida, m.actividad, m.incertidumbrecombinada, m.actividadminimadetectable, m.rq, "Bq/L")
                    else:
                        print("No se ha encontrado la medida")
                    input("pulse enter para continuar")
                else:
                    print("Hay un problema con la recogida", recogida)

    print(no_analizadas)
    print(varias_muestras)


def crearMedidas(alicuota, fecha_medida, tiempo_medida, equipo_medida, actividad, error, amd, rendimiento, unidad):
    if ResultadosMedidas.objects.using('gestion_muestras').filter(id_alicuota=alicuota, fecha_medida=fecha_medida, equipo_medida=equipo_medida).exists():
        return ResultadosMedidas.objects.using('gestion_muestras').filter(id_alicuota=alicuota, fecha_medida=fecha_medida, equipo_medida=equipo_medida)
    else:
        medida = ResultadosMedidas.objects.using('gestion_muestras').create(id_alicuota=alicuota, fecha_medida=fecha_medida, tiempo_medida=tiempo_medida, equipo_medida=equipo_medida, actividad=actividad, error=error, amd=amd, rendimiento=rendimiento, validacion=1, unidad=unidad)
        medida.save(using='gestion_muestras')
        return medida
    
def consultarRegistrosAlfabeta(codigo_viejo, codigo_reducido):
    try:
        muestra = Muestra.objects.using('alfabeta').get(clave=codigo_viejo)
    except:
        muestra = None
    try:
        alicuota = Alicuota.objects.using('alfabeta').get(codigoreducido=codigo_reducido)
    except:
        alicuota = None
    try:
        if Actividadeficienciabeta.objects.using('alfabeta').filter(medida__icontains = codigo_reducido).exists():
            if len(Actividadeficienciabeta.objects.using('alfabeta').filter(medida__icontains = codigo_reducido)) == 1:
                medida = Actividadeficienciabeta.objects.using('alfabeta').filter(medida__icontains = codigo_reducido).get()
                cantidadMedidas = 1
            else:
                medida = Actividadeficienciabeta.objects.using('alfabeta').filter(medida__icontains = codigo_reducido)
                cantidadMedidas = len(medida)
    except:
        medida = None
        cantidadMedidas = 0
    
    return muestra, alicuota, medida, cantidadMedidas


def obtenerAlicuota(historico, analitica, usuario, fecha_entrega, cantidad):
    if RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=historico, id_analiticas=analitica).exists():
        return RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=historico, id_analiticas=analitica).get()
    else:
        tz = pytz.timezone('Europe/Madrid')
        estado = EstadoMuestras.objects.using('gestion_muestras').filter(identificador_estado=3).get()
        alicuota = RelacionHistoricoMuestraAnaliticas(id_historico_recogida=historico, id_analiticas=analitica, fecha_hora_entrega=fecha_entrega, analista_tecnico=usuario, estado_alicuota=estado, cantidad_muestra_analizada=cantidad, descripcion="FTOTAL", alicuota="Analitica")
        alicuota.save(using='gestion_muestras')
        alicuota.codigo_barras = "2" + "{:06}".format(historico.identificador) + "{:06}".format(alicuota.identificador)
        alicuota.save(using='gestion_muestras')
        return alicuota

def obtenerTratamiento(alicuota, tratamiento, fechaPreparacion, fechaMedida, codReducido, usuario):
    if RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota, tratamiento=tratamiento, cod_reducido=codReducido).exists():
        return RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota, tratamiento=tratamiento, cod_reducido=codReducido).get()
    else:
        analiticaTratamiento = RelacionAnaliticasTratamiento(id_muestra_analitica=alicuota, tratamiento=tratamiento, cod_reducido=codReducido, fecha_inicio=fechaPreparacion, fecha_fin=fechaMedida, analista=usuario, paso_actual=1)
        analiticaTratamiento.save(using='gestion_muestras')
        return analiticaTratamiento

def obtenerRecogidaEHistorico(codigo_viejo, elementos, codigo_parseado):
    correctoRecogida, recogida = comprobarRecogidaGeneralBD(elementos[0]["COD_PRO"],elementos[0]["CSN"],elementos[0]["COD_MEMO"],elementos[0]["OBSERV"])
    
    if correctoRecogida:
        gobex = Clientes.objects.using('gestion_muestras').filter(identificador=3).get()
        laruex = Suministradores.objects.using('gestion_muestras').filter(identificador=1).get()
        estado = EstadoMuestras.objects.using('gestion_muestras').filter(identificador_estado=3).get()
        historico = comprobarHistoricoRecogida(recogida, "20"+"{:02}".format(codigo_parseado[4])+"-"+"{:02}".format(codigo_parseado[3])+"-"+"{:02}".format(codigo_parseado[2]), gobex, laruex, estado, codigo_viejo)
        return correctoRecogida, recogida, historico
    else:
        return correctoRecogida, None, None

def comprobarRecogidaGeneralBD(cod_procedencia, cod_csn, cod_memoria, observaciones):
    
    if Procedencias.objects.using('gestion_muestras').filter(codigo=cod_procedencia).exists():
        print("Procedencia existe")
        procedencia = Procedencias.objects.using('gestion_muestras').filter(codigo=cod_procedencia).get()
    else:
        print("Procedencia no existe")
        return False, None
    if RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn=cod_csn, codigo_procedencia=cod_procedencia, codigo_memoria=cod_memoria).exists():
        print("Recogida existe")
        recogidaGeneral = RecogidaGeneral.objects.using('gestion_muestras').filter(codigo_csn=cod_csn, codigo_procedencia=cod_procedencia, codigo_memoria=cod_memoria)
        if len(recogidaGeneral) == 1:
            # print in color green the coincidence in recogidaGeneral[0]
            return True, recogidaGeneral[0]
        else:
            return False, recogidaGeneral
    else:
        print("Recogida no existe")
        recogida = RecogidaGeneral(
            codigo_csn = CodMuestras.objects.using('gestion_muestras').get(codigo=cod_csn),
            codigo_procedencia = procedencia,
            codigo_memoria = Memorias.objects.using('gestion_muestras').get(codigo_memoria=cod_memoria),
            observaciones = observaciones)
        recogida.save(using='gestion_muestras')
        return True, recogida
    
def comprobarHistoricoRecogida(recogida, fecha, cliente, suministrador, estado, cod_antiguo):
    print("comprobarHistoricoRecogida", recogida, fecha)
    if not HistoricoRecogida.objects.using('gestion_muestras').filter(codigo_recogida=recogida, fecha_hora_recogida__gte=fecha+" 00:00:00", fecha_hora_recogida__lte=fecha+" 23:59:59").exists():
        # get actual datetime with timezone Europe/Madrid
        tz = pytz.timezone('Europe/Madrid')
        now = datetime.now(tz)
        print("inserto historico recogida")
        historico = HistoricoRecogida(codigo_recogida=recogida, recepcionado_por=Usuarios.objects.using('gestion_muestras').filter(identificador=1).get(), cliente=cliente, suministrador=suministrador, fecha_hora_recogida=fecha+" 12:00:00+00:00", fecha_hora_recogida_2=fecha+" 12:00:00+00:00", fecha_hora_recogida_ref=fecha+" 12:00:00+00:00", fecha_hora_recepcion=now, estado_de_muestra=estado, referencia_cliente=" ", comentarios=" ", cod_antiguo=cod_antiguo)
        historico.save(using='gestion_muestras')
        historico.codigo_barras = "1" + "{:06}".format(historico.identificador) + "000000"
        historico.save(using='gestion_muestras')
        return historico
    else:
        return HistoricoRecogida.objects.using('gestion_muestras').filter(cod_antiguo=cod_antiguo).get()
    

def parsearFicheroGamma(fichero):
    """
    Parsea el fichero de laboratorio de radiactividad ambiental y devuelve un diccionario con los datos.

    Args:
    fichero: Ruta al fichero.

    Returns:
    Diccionario con los datos del fichero.
    """
    date_format = '%d/%m/%Y %H:%M:%S'

    datos = {}
    with open(fichero, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[0]
        fichero = pageObj.extract_text()
        lineas = fichero.split("\n")
        

        # Parsear la cabecera del fichero
        detector = ""
        for linea in lineas[:15]:
            if re.match(r'^Detector+', linea):
                datos['detector'] = linea.split(":")[1].strip()
            elif re.match(r'^Fichero GENIE+', linea):
                datos['muestra'] = linea.split(":")[1].split("-")[0].strip()
                detector = "genie"
            if re.match(r'^Fichero GAMMAVISION+', linea):
                datos['muestra'] = linea.split(":")[1].split("-")[0].strip()
                detector = "gammavision"
            elif re.match(r'^Fecha/Hora Correción Decay+', linea):
                date_str = (linea.split(":")[1].strip()+":"+linea.split(":")[2].strip()+":00").replace("  ", " ")
                datos['fecha_hora_correccion_decay'] = datetime.strptime(date_str, date_format)
            elif re.match(r'^Fecha/Hora Análisis+', linea):
                date_str = (linea.split(":")[1].strip()+":"+linea.split(":")[2].strip()+":00").replace("  ", " ")
                datos['fecha_hora_analisis'] = datetime.strptime(date_str, date_format)
            elif re.match(r'^Cantidad de muestra+', linea):
                datos['cantidad_muestra'] = linea.split(":")[1].strip()
            elif re.match(r'^Unidades de la media+', linea):
                datos['unidades_media'] = linea.split(":")[1].strip().replace(("Nº Submuestras"), "").strip().replace(" ", "")
            elif re.match(r'^Tiempo de contaje+', linea):
                datos['tiempo_contaje'] = int(linea.split(":")[1].replace("Seg.", "").strip())
            elif re.match(r'^Fichero de Fondo+', linea):
                datos['fichero_fondo_utilizado'] = linea.strip().split(':')[-1].strip()
            elif re.match(r'^Geometría del Calibrado+', linea):
                datos['geometria_calibrado'] = linea.split(":")[1].strip()

        # find the index that start with ISOTOPO
        if detector == "genie":
            for i, linea in enumerate(lineas):
                if re.match(r'^ISOTOPO\s+', linea):
                    break
            i = i + 2
        elif detector == "gammavision":
            for i, linea in enumerate(lineas):
                if 'ACTIVIDAD CORREGIDA' in linea:
                    break
            i = i + 3
        isótopos = []

        for linea in lineas[i:]:
            if "--------------------------" in linea:
                break
            else:
                if detector == "genie":
                    valores = linea.split()
                    if len(valores) == 5:
                        isotopo = {"iso": valores[0], "lid": valores[1], "actividad": float(valores[2]), "error": valores[4]}
                    else:
                        isotopo = {"iso": valores[0], "lid": valores[1], "actividad": 0.0, "error": 0.0}
                    isótopos.append(isotopo)
                elif detector == "gammavision":
                    if "HALFLIVES" not in linea:
                        valores = linea.split()
                        if len(valores) == 5:
                            isotopo = {"iso": valores[0], "lid": valores[4], "actividad": float(valores[1]), "error": valores[3]}
                        else:
                            isotopo = {"iso": valores[0], "lid": valores[3], "actividad": 0.0, "error": 0.0}
                        isótopos.append(isotopo)
        # Parsear la tabla de isótopos
        

        datos['isotopos'] = isótopos

    return datos
    
    '''
    dir = "C:/Users/jbaezami/Downloads/Jose luis/Analizar"
    # list files in dir
    for f in os.listdir(dir):
        if f.endswith(".pdf"):
            datosEspectrometria = parsearFicheroGamma(dir+"/"+f)
            muestra = HistoricoRecogida.objects.using('gestion_muestras').get(identificador=datosEspectrometria['muestra'])
            alicuotas = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(id_historico_recogida=muestra)
            if alicuotas.filter(id_analiticas__identificador=8).exists():
                insertarDatosEspectrometria(alicuotas.filter(id_analiticas__identificador=8).get(), datosEspectrometria)
            elif alicuotas.filter(id_analiticas__identificador=24).exists():
                insertarDatosYodo(alicuotas.filter(id_analiticas__identificador=24).get(), datosEspectrometria)
    '''
def insertarDatosEspectrometria(alicuota, datos):
    """
    Inserta los datos de un fichero de espectrometría en la base de datos.

    Args:
    alicuota: Alicuota de E(Gamma) a la que pertenecen los datos.
    datos: Diccionario con los datos del fichero.

    Returns:
    None.
    """

    for dato in datos["isotopos"]:
        if not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=alicuota, determinacion_medida=DeterminacionMedidaInforme.objects.using('gestion_muestras').filter(nombre_medida=dato["iso"]).get()).exists():
            print("Insertando medida", dato["iso"], dato["actividad"], dato["error"], dato["lid"], datos["fecha_hora_analisis"], datos["tiempo_contaje"], datos["unidades_media"], alicuota.cantidad_muestra_analizada)

            cod_reducido = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota)[0].cod_reducido
            RelacionAlicuotasMedidas(id_alicuota=alicuota, cod_reducido=cod_reducido, determinacion_medida=DeterminacionMedidaInforme.objects.using('gestion_muestras').filter(nombre_medida=dato["iso"]).get(), fecha_analisis=datos["fecha_hora_analisis"], actividad=dato["actividad"], actividad_error=dato["error"], amd=dato["lid"], tiempo_medida=datos["tiempo_contaje"], cantidad=alicuota.cantidad_muestra_analizada, rendimiento=1, seleccionado=0).save(using='gestion_muestras')



def insertarDatosYodo(alicuota, datos):
    for dato in datos["isotopos"]:
        if dato["iso"] == "I-131" and not RelacionAlicuotasMedidas.objects.using('gestion_muestras').filter(id_alicuota=alicuota, determinacion_medida=DeterminacionMedidaInforme.objects.using('gestion_muestras').filter(identificador=41).get()).exists():
            print("Insertando medida", dato["iso"], dato["actividad"], dato["error"], dato["lid"], datos["fecha_hora_analisis"], datos["tiempo_contaje"], datos["unidades_media"], alicuota.cantidad_muestra_analizada)

            cod_reducido = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota)[0].cod_reducido
            RelacionAlicuotasMedidas(id_alicuota=alicuota, cod_reducido=cod_reducido, determinacion_medida=DeterminacionMedidaInforme.objects.using('gestion_muestras').filter(identificador=41).get(), fecha_analisis=datos["fecha_hora_analisis"], actividad=dato["actividad"], actividad_error=dato["error"], amd=dato["lid"], tiempo_medida=datos["tiempo_contaje"], cantidad=alicuota.cantidad_muestra_analizada, rendimiento=1, seleccionado=0).save(using='gestion_muestras')


def obtenerDatosBetaTotalContadores(alicuota):
    alicuota = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=alicuota).get()
    muestraContadores = Muestra.objects.using('alfabeta').filter(clave=alicuota.id_historico_recogida.identificador).get()
    alicuotasContadores = Alicuota.objects.using('alfabeta').filter(muestra_clave=muestraContadores)
    for alicuotaContadores in alicuotasContadores:
        medidas = Actividadeficienciabeta.objects.using('alfabeta').filter(medida__icontains=alicuotaContadores.codigoreducido+"-")
        for m in medidas:
            infoMedida = Medida.objects.using('alfabeta').filter(id=m.medida).get()
            cod_reducido = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota)[0].cod_reducido
            RelacionAlicuotasMedidas(id_alicuota=alicuota, cod_reducido=cod_reducido, determinacion_medida=DeterminacionMedidaInforme.objects.using('gestion_muestras').filter(identificador=2).get(), fecha_analisis=infoMedida.fecha, actividad=m.actividad, actividad_error=m.errorrecuento, amd=m.actividadminimadetectable, tiempo_medida=infoMedida.tiempo, cantidad=alicuota.cantidad_muestra_analizada, rendimiento=m.rq, seleccionado=0).save(using='gestion_muestras')

def obtenerDatosYodoContadores(alicuota):
    alicuota = RelacionHistoricoMuestraAnaliticas.objects.using('gestion_muestras').filter(identificador=alicuota).get()
    muestraContadores = Muestra.objects.using('alfabeta').filter(clave=alicuota.id_historico_recogida.identificador).get()
    alicuotasContadores = Alicuota.objects.using('alfabeta').filter(muestra_clave=muestraContadores, tipoanalitica__nombre="Radioyodos")
    for alicuotaContadores in alicuotasContadores:
        medidas = Actividadeficienciabeta.objects.using('alfabeta').filter(medida__icontains=alicuotaContadores.codigoreducido+"-")
        for m in medidas:
            infoMedida = Medida.objects.using('alfabeta').filter(id=m.medida).get()
            cod_reducido = RelacionAnaliticasTratamiento.objects.using('gestion_muestras').filter(id_muestra_analitica=alicuota)[0].cod_reducido
            RelacionAlicuotasMedidas(id_alicuota=alicuota, cod_reducido=cod_reducido, determinacion_medida=DeterminacionMedidaInforme.objects.using('gestion_muestras').filter(identificador=41).get(), fecha_analisis=infoMedida.fecha, actividad=m.actividad, actividad_error=m.errorrecuento, amd=m.actividadminimadetectable, tiempo_medida=infoMedida.tiempo, cantidad=alicuota.cantidad_muestra_analizada, rendimiento=m.rq, seleccionado=0).save(using='gestion_muestras')