from copuma.models import ValorMuestra,Isotopo,MotivoMuestreo,Laboratorio,Muestra,Procedencia,Instalacion,ValorMuestraCopumaVolatil,GestionMemoriaDocumentcopuma
from datetime import datetime, timedelta
from time import gmtime, strftime
import os
from django.conf import settings
from multiprocessing import Pool,Lock,Value,Array
from functools import partial
from ctypes import c_char_p
import sys
from dbfread import DBF
import pandas as pd
from simpledbf import Dbf5
from copuma.models import *

def procesar_texto_copuma_volatil(infile,file_path):
	print("PROCESO TEXTO")
	inicio=datetime.now()
	cont=0
	today=(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')
	Valor_repetido=False
	mensaje_error=""
	mensaje_warning=""
	mensaje_correcto=""
	mensaje_resumen=""
	tipos_muestras=[]
	if file_path.endswith(".dbf"):
		print("Es un archivo de base de datos")
		dbf2 = Dbf5(settings.MEDIA_ROOT+file_path, codec='latin')
		df = pd.DataFrame(dbf2.to_dataframe())
		procedencias = Procedencia.objects.using('gestion_memoria')
		
		for index, row in df.iterrows():
    			
			'''
			if row['SIGNOAC'] == "-":
				print(row['AC_ESP'], row['SIGNOAC'], row['EXPAC'], " -- ", row['AC_ESP']*10**(-1*row['EXPAC']))
			else:
				print(row['AC_ESP'], row['SIGNOAC'], row['EXPAC'], " -- ", row['AC_ESP']*10**row['EXPAC'])
			if procedencias.filter(name=row['PROCEDENCI'].replace('Ñ','N')).exists():
				print(row['PROCEDENCI'], procedencias.filter(name=row['PROCEDENCI'].replace('Ñ','N')).values()[0]["codprocedencia"])
			else:
				print(row['PROCEDENCI'],-1)
			'''

			valorMuestra=""
			#Calculamos el motivo del muestreo, laboratorio, muestra, procedencia e instalacion
			motivoMuestreo=row['MEMO']
			laboratorio=23
			muestra=row['CODIGO']
			procedencia=-1
			if procedencias.filter(name=row['PROCEDENCI'].replace('Ñ','N')).exists():
				procedencia= procedencias.filter(name=row['PROCEDENCI'].replace('Ñ','N')).values()[0]["codprocedencia"]
			instalacion="ALM"
			tipos_muestras.append(muestra)
			valorMuestra=ValorMuestraCopumaVolatil(motivo_muestreo_codmuestreo=motivoMuestreo,laboratorio_codlaboratorio=laboratorio,instalacion_codinstalacion=instalacion,estacion_codprocedencia=procedencia,muestra_codmuestra=muestra)
			
			valorMuestra.isotopo_codisotopo,valorMuestra.isotopo_analisis_codanalisis,valorMuestra.masa = calcularIsotopos(row['ANALISIS'])
			valorMuestra.metaestable=""
			valorMuestra.compartida="N"

			"""Calculamos las fechas"""
			valorMuestra.fecha_recogida_inicial=row['F_REC'].strftime('%Y-%m-%d')
			valorMuestra.fecha_recogida_final=row['F_FIN'].strftime('%Y-%m-%d')
			valorMuestra.fecha_analisis=row['F_MED'].strftime('%Y-%m-%d')
			valorMuestra.fecha_subida_fichero=today
			"""Fin Calculo Fechas"""

			medida = LimitesMaximos.objects.using('gestion_memoria').filter(muestra_codmuestra=valorMuestra.muestra_codmuestra, isotopo_codisotopo=valorMuestra.isotopo_codisotopo, isotopo_analisis_codanalisis=valorMuestra.isotopo_analisis_codanalisis,masa=valorMuestra.masa).values_list('medida', flat=True)[0]
			factorConversion = calcularFactorMedida(row['UNIT'], medida)
			#Calculamos la actividad
			if row['SIGNOAC'] == "-":
				valorMuestra.actividad_medida=float(row['AC_ESP']*10**(-1*row['EXPAC']))*factorConversion
			else:
				valorMuestra.actividad_medida=float(row['AC_ESP']*10**row['EXPAC'])*factorConversion
				
			if row['SIGNOEAC'] == "-":
				valorMuestra.error_actividad_medida=float(row['ERR_AC']*10**(-1*row['EXPEAC']))*factorConversion
			else:
				valorMuestra.error_actividad_medida=float(row['ERR_AC']*10**row['EXPEAC'])*factorConversion
				
			if row['SIGNOLID'] == "-":
				valorMuestra.lid_medida=float(row['LID']*10**(-1*row['EXPLID']))*factorConversion
			else:
				valorMuestra.lid_medida=float(row['LID']*10**row['EXPLID'])*factorConversion

			valorMuestra.tiempo_recuento =int(row['T_MUES'])
			valorMuestra.rendimiento_quimico =float(row['RENDI'])
			valorMuestra.csn=0
			valorMuestra.verificado=0

			valorMuestraCopumaVolatil=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(motivo_muestreo_codmuestreo = valorMuestra.motivo_muestreo_codmuestreo, fecha_recogida_inicial=valorMuestra.fecha_recogida_inicial,fecha_recogida_final=valorMuestra.fecha_recogida_final, instalacion_codinstalacion=valorMuestra.instalacion_codinstalacion, laboratorio_codlaboratorio=valorMuestra.laboratorio_codlaboratorio,muestra_codmuestra=valorMuestra.muestra_codmuestra, isotopo_codisotopo=valorMuestra.isotopo_codisotopo, isotopo_analisis_codanalisis=valorMuestra.isotopo_analisis_codanalisis, estacion_codprocedencia=valorMuestra.estacion_codprocedencia, masa=valorMuestra.masa)
			if valorMuestraCopumaVolatil.exists():
				Valor_repetido=True
				if((valorMuestraCopumaVolatil[0].actividad_medida!=valorMuestra.actividad_medida) or (valorMuestraCopumaVolatil[0].error_actividad_medida!=valorMuestra.error_actividad_medida) or (valorMuestraCopumaVolatil[0].lid_medida!=valorMuestra.lid_medida)):
					mensaje_error+="<div id='linea_"+str(cont)+"' class='bg-danger'><h3 ><b>Linea "+str(cont)+" ya existente en la base de datos con valores diferentes</b></h3>"
					mensaje_error+="<table class='table'><tr>"+mostrar_valormuestra(valorMuestra)+"</tr>"
					mensaje_error+="<tr>"+mostrar_valormuestra(valorMuestraCopumaVolatil[0])+"</tr>"
					mensaje_error+="<tr>"+ "<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"enviar('"+str(valorMuestra.motivo_muestreo_codmuestreo)+"','"+ str(valorMuestra.fecha_recogida_inicial)+"','"+str(valorMuestra.fecha_recogida_final)+"','"+str(valorMuestra.fecha_analisis)+"','"+ str(valorMuestra.instalacion_codinstalacion)+"','"+str(valorMuestra.laboratorio_codlaboratorio)+"','"+str(valorMuestra.muestra_codmuestra)+"','"+ str(valorMuestra.isotopo_codisotopo)+"','"+ str(valorMuestra.isotopo_analisis_codanalisis)+"','"+ str(valorMuestra.estacion_codprocedencia)+"','"+ str(valorMuestra.masa)+"','0','"+str(valorMuestra.actividad_medida).replace(".","-")+"','"+   str(valorMuestra.error_actividad_medida).replace(".","-")+"','"+  str(valorMuestra.lid_medida).replace(".","-")+"','"+  str(cont)+"');\">Insertar</button>"
					#mensaje_error+="<tr>"+ "<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"enviar('"+str(valorMuestra.motivo_muestreo_codmuestreo)+"','"+ str(valorMuestra.fecha_recogida_inicial)+"');\">Insertar</button>"

					mensaje_error+="<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"this.parentNode.style.display='none';\">Cancelar</button>"+"</tr></table>"
					mensaje_error+="</div>"
				else:
					mensaje_warning+="<div id='linea_"+str(cont)+"' class='bg-warning'><h3 ><b>Linea "+str(cont)+" ya existente en la base de datos</b></h3><table class='table'><tr>"+mostrar_valormuestra(valorMuestra)+"</tr>"
					mensaje_warning+="<tr>"+ "<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"this.parentNode.style.display='none';\">Ocultar</button>"+"</tr></table></div>"

			else:
				print("inserta el valor")
				valorMuestra.save(using='gestion_memoria',force_insert=True)
				mensaje_correcto+="<div class='bg-success'>"
				mensaje_correcto+="<table class='table'><tr>"+mostrar_valormuestra(valorMuestra)+"</tr></table>"
				mensaje_correcto+="</div>"

		return mensaje_error,mensaje_correcto,mensaje_resumen
	else:		
		for line in infile:
			print(line)
			try:
				valorMuestra=""
				#Calculamos el motivo del muestreo, laboratorio, muestra, procedencia e instalacion
				motivoMuestreo=line[0:1]
				laboratorio=line[2:4]
				muestra=line[10:13]
				procedencia=line[7:10]
				instalacion=line[4:7]

				tipos_muestras.append(muestra)

				valorMuestra=ValorMuestraCopumaVolatil(motivo_muestreo_codmuestreo=motivoMuestreo,
					laboratorio_codlaboratorio=laboratorio,
					instalacion_codinstalacion=instalacion,
					estacion_codprocedencia=procedencia,
					muestra_codmuestra=muestra)

				#Calculamos los isotopos
				valorMuestra.isotopo_codisotopo=line[16:18]
				valorMuestra.isotopo_analisis_codanalisis=line[14:16]
				try:
					valorMuestra.masa=int(line[18:21])
				except:
					valorMuestra.masa=-1

				valorMuestra.metaestable=line[21:22]


				valorMuestra.compartida=line[39:40]


				"""Calculamos las fechas"""
				try:
					valorMuestra.fecha_recogida_inicial=datetime.strptime(line[22:30], '%d-%m-%y').strftime('%Y-%m-%d')

				except:
					valorMuestra.fecha_recogida_inicial=""
				try:
					valorMuestra.fecha_recogida_final=datetime.strptime(line[31:39], '%d-%m-%y').strftime('%Y-%m-%d')
				except:
					valorMuestra.fecha_recogida_final=""
				try:
					valorMuestra.fecha_analisis=datetime.strptime(line[40:48], '%d-%m-%y').strftime('%Y-%m-%d')

				except:
					valorMuestra.fecha_analisis=""

				valorMuestra.fecha_subida_fichero=today

				"""Fin Calculo Fechas"""




				#Calculamos la actividad
				try:
					valorMuestra.actividad_medida=float(line[49:58])

				except:
					valorMuestra.actividad_medida=-1

				try:
					valorMuestra.error_actividad_medida=float(line[59:68])
				except:
					valorMuestra.error_actividad_medida=-1

				try:
					valorMuestra.lid_medida=float(line[69:78])
				except:
					valorMuestra.lid_medida=-1
				try:
					valorMuestra.numero_muestras=int(line[79:81])
				except:
					valorMuestra.numero_muestras=-1

				try:
					valorMuestra.tiempo_recuento =int(line[82:89])
				except:
					pass
				try:
					valorMuestra.c_muestra_recogida =float(line[90:99])
				except:
					pass
				try:
					valorMuestra.c_muestra_analizada=float(line[100:109])
				except:
					pass
				try:
					valorMuestra.rendimiento_quimico =float(line[110:116])
				except:
					pass
				try:
					valorMuestra.relac_ceni_pes_hum =float(line[117:123])
				except:
					pass
				try:
					valorMuestra.semana_recogida =int(line[124:126])
				except:
					pass
				try:
					valorMuestra.cod_laboratorio_prep=int(line[127:130])
				except:
					pass


				valorMuestra.csn=0
				valorMuestra.verificado=0

				valorMuestraCopumaVolatil=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(motivo_muestreo_codmuestreo = valorMuestra.motivo_muestreo_codmuestreo, fecha_recogida_inicial=valorMuestra.fecha_recogida_inicial,fecha_recogida_final=valorMuestra.fecha_recogida_final, fecha_analisis=valorMuestra.fecha_analisis, instalacion_codinstalacion=valorMuestra.instalacion_codinstalacion, laboratorio_codlaboratorio=valorMuestra.laboratorio_codlaboratorio,muestra_codmuestra=valorMuestra.muestra_codmuestra, isotopo_codisotopo=valorMuestra.isotopo_codisotopo, isotopo_analisis_codanalisis=valorMuestra.isotopo_analisis_codanalisis, estacion_codprocedencia=valorMuestra.estacion_codprocedencia, masa=valorMuestra.masa, metaestable=valorMuestra.metaestable)

				if valorMuestraCopumaVolatil.exists():
					Valor_repetido=True
					if((valorMuestraCopumaVolatil[0].actividad_medida!=valorMuestra.actividad_medida) or (valorMuestraCopumaVolatil[0].error_actividad_medida!=valorMuestra.error_actividad_medida) or (valorMuestraCopumaVolatil[0].lid_medida!=valorMuestra.lid_medida)):
						mensaje_error+="<div id='linea_"+str(cont)+"' class='bg-danger'><h3 ><b>Linea "+str(cont)+" ya existente en la base de datos con valores diferentes</b></h3>"
						mensaje_error+="<table class='table'><tr>"+mostrar_valormuestra(valorMuestra)+"</tr>"
						mensaje_error+="<tr>"+mostrar_valormuestra(valorMuestraCopumaVolatil[0])+"</tr>"
						mensaje_error+="<tr>"+ "<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"enviar('"+str(valorMuestra.motivo_muestreo_codmuestreo)+"','"+ str(valorMuestra.fecha_recogida_inicial)+"','"+str(valorMuestra.fecha_recogida_final)+"','"+str(valorMuestra.fecha_analisis)+"','"+ str(valorMuestra.instalacion_codinstalacion)+"','"+str(valorMuestra.laboratorio_codlaboratorio)+"','"+str(valorMuestra.muestra_codmuestra)+"','"+ str(valorMuestra.isotopo_codisotopo)+"','"+ str(valorMuestra.isotopo_analisis_codanalisis)+"','"+ str(valorMuestra.estacion_codprocedencia)+"','"+ str(valorMuestra.masa)+"','"+str(valorMuestra.metaestable)+"','"+str(valorMuestra.actividad_medida)+"','"+   str(valorMuestra.error_actividad_medida)+"','"+  str(valorMuestra.lid_medida)+"','"+  str(cont)+"');\">Insertar</button>"
						#mensaje_error+="<tr>"+ "<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"enviar('"+str(valorMuestra.motivo_muestreo_codmuestreo)+"','"+ str(valorMuestra.fecha_recogida_inicial)+"');\">Insertar</button>"

						mensaje_error+="<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"this.parentNode.style.display='none';\">Cancelar</button>"+"</tr></table>"
						mensaje_error+="</div>"
					else:
						mensaje_warning+="<div id='linea_"+str(cont)+"' class='bg-warning'><h3 ><b>Linea "+str(cont)+" ya existente en la base de datos</b></h3><table class='table'><tr>"+mostrar_valormuestra(valorMuestra)+"</tr>"
						mensaje_warning+="<tr>"+ "<button style=\"cursor: pointer; cursor: hand;border-radius: 25px;\" class=\"btn btn-primary\" onClick=\"this.parentNode.style.display='none';\">Ocultar</button>"+"</tr></table></div>"

				else:
					print("inserta el valor")
					valorMuestra.save(using='gestion_memoria',force_insert=True)
					mensaje_correcto+="<div class='bg-success'>"
					mensaje_correcto+="<table class='table'><tr>"+mostrar_valormuestra(valorMuestra)+"</tr></table>"
					mensaje_correcto+="</div>"

				cont=cont+1;
			except Exception as inst:
				Valor_repetido=True
				mensaje_error+="<div class='bg-danger'><h3 ><b>Linea "+str(cont)+" otro tipo error</b></h3>"
				mensaje_error+="<table class='table'><tr>"+str(inst.args)+"</tr>"
				mensaje_error+="<tr>"+line+"</tr>"
				mensaje_error+="<tr>"+ "<button style='cursor: pointer; cursor: hand;border-radius: 25px;'' class='btn btn-primary' onClick=\"this.parentNode.style.display='none';\">Ocultar</button>"+"</tr></table>"

				mensaje_error+="</div>"
				print("Error linea "+line+ " "+str(inst.args))
				cont=cont+1;


		print("TOTAL DE MUESTRAS " + str(cont))
		tipos_muestras = list(set(tipos_muestras))
		str_tipos_muestras = str(list(set(tipos_muestras))).replace("[","").replace("]","")
		print(str_tipos_muestras)
		mensaje_resumen+="<h4>Muestras leidas: "+str(cont)+"</h4><br><h4>Tipo de muestras: "+str_tipos_muestras+"</h4>"

		final=datetime.now()
		print (final-inicio)
		mensaje_error=mensaje_error+mensaje_warning
		#if(Valor_repetido==True):
		#	os.remove(settings.MEDIA_ROOT+file_path)
		#	ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(fecha_subida_fichero=today).delete()
		#	Documentcopuma.objects.using('gestion_memoria').filter(docfile=file_path).delete()
		#	return mensaje_error,mensaje_correcto

		#else:
		#	return mensaje_error,mensaje_correcto
		return mensaje_error,mensaje_correcto,mensaje_resumen

def calcularIsotopos(analisis):
	if CalcularIsotopos.objects.using("gestion_memoria").filter(analisis=analisis).exists():
		valores = CalcularIsotopos.objects.using("gestion_memoria").filter(analisis=analisis).values()[0]
		return valores["cod_isotopo"],valores["cod_analisis"],valores["masa"]
	else:
		return "", "", -1

def calcularFactorMedida(medidaDada, medidaPedida):
	factorNumerador, factorDenominador = 1, 1
	numeradorMedidaDada = medidaDada.split("/")[0]
	denominadorMedidaDada = medidaDada.split("/")[1]
	numeradorMedidaPedida = medidaPedida.split("/")[0]
	denominadorMedidaPedida = medidaPedida.split("/")[1]

	if numeradorMedidaDada == "mBq" and numeradorMedidaPedida == "Bq":
		factorNumerador = 0.001
	elif numeradorMedidaDada == "Bq" and numeradorMedidaPedida == "mBq":
		factorNumerador = 1000
	if denominadorMedidaDada == "L" and denominadorMedidaPedida == "m3":
		factorDenominador = 0.001
	elif numeradorMedidaDada == "m3" and numeradorMedidaPedida == "L":
		factorDenominador = 1000
	return factorNumerador/factorDenominador

def guardar_muestra(motivo_muestreo_codmuestreo,fecha_recogida_inicial,fecha_recogida_final,fecha_analisis,instalacion_codinstalacion,laboratorio_codlaboratorio,muestra_codmuestra,isotopo_codisotopo,isotopo_analisis_codanalisis,estacion_codprocedencia,masa,metaestable,actividad_medida,error_actividad_medida,lid_medida):
	print(str(motivo_muestreo_codmuestreo)+str(fecha_recogida_inicial)+str(fecha_recogida_final)+str(fecha_analisis)+str(instalacion_codinstalacion)+str(laboratorio_codlaboratorio)+str(muestra_codmuestra)+str(isotopo_codisotopo)+str(isotopo_analisis_codanalisis)+str(estacion_codprocedencia) + str(masa) )
	valorMuestraCopumaVolatil=ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(motivo_muestreo_codmuestreo=motivo_muestreo_codmuestreo,fecha_recogida_inicial=fecha_recogida_inicial,fecha_recogida_final=fecha_recogida_final,fecha_analisis=fecha_analisis,instalacion_codinstalacion=instalacion_codinstalacion,laboratorio_codlaboratorio=laboratorio_codlaboratorio,muestra_codmuestra=muestra_codmuestra,isotopo_codisotopo=isotopo_codisotopo,isotopo_analisis_codanalisis=isotopo_analisis_codanalisis,estacion_codprocedencia=estacion_codprocedencia,masa=masa)

	if valorMuestraCopumaVolatil.exists():
		print(str(valorMuestraCopumaVolatil[0].lid_medida)+" "+str(lid_medida))
		print(len(valorMuestraCopumaVolatil))
		today=(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')
		ValorMuestraCopumaVolatil.objects.using('gestion_memoria').filter(motivo_muestreo_codmuestreo=motivo_muestreo_codmuestreo,fecha_recogida_inicial=fecha_recogida_inicial,fecha_recogida_final=fecha_recogida_final,fecha_analisis=fecha_analisis,instalacion_codinstalacion=instalacion_codinstalacion,laboratorio_codlaboratorio=laboratorio_codlaboratorio,muestra_codmuestra=muestra_codmuestra,isotopo_codisotopo=isotopo_codisotopo,isotopo_analisis_codanalisis=isotopo_analisis_codanalisis,estacion_codprocedencia=estacion_codprocedencia,masa=masa).update(actividad_medida=actividad_medida,error_actividad_medida=error_actividad_medida,lid_medida=lid_medida,fecha_subida_fichero=today)
		return 0
	else:
		return 1


def mostrar_valormuestra(v):
	mensaje=""
	mensaje+="<td>"+str(v.motivo_muestreo_codmuestreo)+"</td>"
	mensaje+="<td>"+str(v.laboratorio_codlaboratorio)+"</td>"
	mensaje+="<td>"+str(v.instalacion_codinstalacion)+"</td>"
	mensaje+="<td>"+str(int(v.estacion_codprocedencia))+"</td>"
	mensaje+="<td>"+str(v.muestra_codmuestra)+"</td>"
	mensaje+="<td>"+str(v.isotopo_analisis_codanalisis)+"</td>"
	mensaje+="<td>"+str(v.isotopo_codisotopo)+"</td>"
	mensaje+="<td>"+str(v.metaestable)+"</td>"
	mensaje+="<td>"+str(v.fecha_recogida_inicial)+"</td>"
	mensaje+="<td>"+str(v.fecha_recogida_final)+"</td>"
	mensaje+="<td>"+str(v.compartida)+"</td>"
	mensaje+="<td>"+str(v.fecha_analisis)+"</td>"
	mensaje+="<td>"+str(v.actividad_medida)+"</td>"
	mensaje+="<td>"+str(v.error_actividad_medida)+"</td>"
	mensaje+="<td>"+str(v.lid_medida)+"</td>"
	mensaje+="<td>"+str(v.numero_muestras)+"</td>"
	mensaje+="<td>"+str(v.fecha_subida_fichero)+"</td>"
	return mensaje
