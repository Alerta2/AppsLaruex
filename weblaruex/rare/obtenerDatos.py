# -*- coding: utf-8 -*- 
from .models import Canales,EstMeteorologicas,EstGamYRadioyodos,UltimosValoresRecibidos,Estaciones,RelacionDetectoresEstacion,RelacionDetectoresIsotopos,Isotopos,Relacion,EstEspecGamma,Espectros,MediasDiarias
import datetime
import pytz

from datetime import datetime as dtdatetime
from datetime import timedelta
import threading
import queue
import json
import math
from django.utils.encoding import iri_to_uri
#Modelo de uso
using='rvra'
using_estaciones='localhost'



def distancia(lat1, lon1, lat2, lon2):

	theta = lon1 - lon2;
	dist = math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) +  math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(theta));
	dist = math.acos(dist);
	dist = math.degrees(dist);
	kilometros = dist * 60 * 1.1515* 1.609344;
	return kilometros
 






def convertir_subindice(texto):
	try:
		nombre_isotopo=""
		elemento=texto.split("-")[0]

		numero=texto.split("-")[1]

#Modificado DAVID 16/02/17
#		for l in range(len(numero)):
#			if(int(numero[l])==0):
#				nombre_isotopo+="&#8304;"
#			if(int(numero[l])==1):
#				nombre_isotopo+="&#185;"
#			if(int(numero[l])==2):
#				nombre_isotopo+="&#178;"
#			if(int(numero[l])==3):
#				nombre_isotopo+="&#179;"
#			if(int(numero[l])>3 and int(numero[l])<=5):
#				nombre_isotopo+="&#830"+str(int(numero[l])+4)+";"
#			if(int(numero[l])>5):
#				nombre_isotopo+="&#83"+str(int(numero[l])+4)+";"
		nombre_isotopo="<sup>"+numero+"</sup>";

		primero=True
		elemento_final=elemento[0]
		for l in range(len(elemento)):
			if primero==False:
				elemento_final+=elemento[l].lower()
			primero=False


		return nombre_isotopo+elemento_final

	except:
		return texto


#Modificado por David para poder mostrar la gráfica
def getMediaVientoDiaria(id_estacion,cola):
	# 1------- Calculamos los valores para la grafica de tasa de dosis gamma media diaria
	#print "Entro en media diaria"
	idEst= id_estacion
	ayer = datetime.date.today()-datetime.timedelta(days=2)
	mediasDiarias=MediasDiarias.objects.using(using).filter(id_canal=7).filter(fecha__gt=ayer).filter(id_estacion=idEst).order_by('fecha').values_list('valor')
	#estGamYRadioyodos=EstGamYRadioyodos.objects.using(using).filter(fecha_hora__gt=ayer).filter(canales=1).filter(estaciones=id_estacion).order_by('fecha_hora').values_list('fecha_hora', 'valor')
	#relacion=Relacion.objects.using(using).filter(estac=id_estacion).filter(canal=1)
	#if len(relacion)!=0:
	#	amd=relacion[0].monitorizar

	lista_dir=[-1]
	if (len(mediasDiarias)>0):
		lista_dir=mediasDiarias[0]
	
	#print "David"
	#print lista_dir[0]
	cola.put(lista_dir[0])
	# Fin 1


#Modificado por David para poder mostrar la gráfica
def getMediaDiaria(id_estacion,cola):
	# 1------- Calculamos los valores para la grafica de tasa de dosis gamma media diaria
	#print "Entro en media diaria"
	idEst= id_estacion
	semana = datetime.date.today()-datetime.timedelta(days=7)
	mediasDiarias=MediasDiarias.objects.using(using).filter(id_canal=1).filter(fecha__gt=semana).filter(id_estacion=idEst).order_by('fecha').values_list('fecha', 'valor')
	#estGamYRadioyodos=EstGamYRadioyodos.objects.using(using).filter(fecha_hora__gt=ayer).filter(canales=1).filter(estaciones=id_estacion).order_by('fecha_hora').values_list('fecha_hora', 'valor')
	relacion=Relacion.objects.using(using).filter(estac=id_estacion).filter(canal=1)
	if len(relacion)!=0:
		amd=relacion[0].monitorizar

	lista_dosis=""
	for val in mediasDiarias:
		valorMes=int(val[0].strftime("%-m"))-1
		lista_dosis+="[new Date("+val[0].strftime("%Y")+","+str(valorMes)+","+val[0].strftime("%-d")+",0,0,0,0),"+str(val[1])+","+str(amd+0.114)+","+str(amd+0.228)+"],"

	if lista_dosis!="":
		lista_dosis=lista_dosis [:-1]


	#print lista_dosis
	cola.put(lista_dosis)
	# Fin 1



def getGamaYodo(id_estacion,cola):
	# 1------- Calculamos los valores para la grafica de gama yodo
	ayer = datetime.datetime.now().replace( minute=0,second=0)+datetime.timedelta(hours=-4)
	estGamYRadioyodos=EstGamYRadioyodos.objects.using(using).filter(fecha_hora__gt=ayer).filter(canales=1).filter(estaciones=id_estacion).order_by('fecha_hora').values_list('fecha_hora', 'valor')
	relacion=Relacion.objects.using(using).filter(estac=id_estacion).filter(canal=1)
	if len(relacion)!=0:
		amd=relacion[0].monitorizar

	lista_dosis=""
	for val in estGamYRadioyodos:
		# corregido
		#valorMes=int(val[0].strftime("%-m"))-1
		#lista_dosis+="[new Date("+val[0].strftime("%Y")+","+str(valorMes)+","+val[0].strftime("%-d")+","+val[0].strftime("%-H")+","+val[0].strftime("%-M")+",0,0),"+str(val[1])+","+str(amd+0.114)+","+str(amd+0.228)+"],"
		lista_dosis+="[new Date("+str(val[0].year)+","+str(val[0].month)+","+str(val[0].day)+","+str(val[0].hour)+","+str(val[0].minute)+",0,0),"+str(val[1])+","+str(amd+0.114)+","+str(amd+0.228)+"],"
		print (lista_dosis)

	if lista_dosis!="":
		lista_dosis=lista_dosis [:-1]

	#print lista_dosis
	cola.put(lista_dosis)
	# Fin 1


def getUltimaMediaDiaria(id_estacion,cola):
	# 2------- Calculamos el ultimo valor de radio yodo y la estacion
	ultimo_valor=""
	ayer = datetime.date.today()-datetime.timedelta(days=1)
	
	try:
		#ultimo_valor=UltimosValoresRecibidos.objects.using(using).filter(can_det_est=1).filter(estacion_id=id_estacion)[0]
		ultimo_valor=MediasDiarias.objects.using(using).filter(id_canal=1).filter(id_estacion=id_estacion).order_by('-fecha')[0]
	except:
		pass
	try:
		estacion=Estaciones.objects.using(using).filter(id=id_estacion)[0]
	except:
		estacion=Estaciones.objects.using(using_estaciones).filter(id=id_estacion)[0]

	d=False
	if ultimo_valor!="":
		if (datetime.date.today()-timedelta(days=1))>= ultimo_valor.fecha:
			d=True
		
	#print(d)
	cola.put(ultimo_valor)
	cola.put(estacion)
	cola.put(d)
	# Fin 2



def getUltimoRadioYodo(id_estacion,cola):
	# 2------- Calculamos el ultimo valor de radio yodo y la estacion
	ultimo_valor=""
	try:
		ultimo_valor=UltimosValoresRecibidos.objects.using(using).filter(can_det_est=1).filter(estacion_id=id_estacion)[0]
	except:
		pass
	try:
		estacion=Estaciones.objects.using(using).filter(id=id_estacion)[0]
	except:
		estacion=Estaciones.objects.using(using_estaciones).filter(id=id_estacion)[0]

	d=False
	if ultimo_valor!="":
		now = datetime.datetime.now()
		now = pytz.utc.localize(now)
		now = now.replace(tzinfo=pytz.utc)
		if (now-timedelta(hours=6))>= ultimo_valor.fecha_hora:
			d=True
		
	#print(d)
	cola.put(ultimo_valor)
	cola.put(estacion)
	cola.put(d)
	# Fin 2

def getIsotopos(id_estacion,cola):
	# 3------- Calculamos los isotopos
	lista_detectores_isotopos=""
	nombre_detectores=[]
	detectores=RelacionDetectoresEstacion.objects.using(using).filter(id_estacion=id_estacion)
	for detector in detectores:
		nombre_detectores.append(detector.dir_datos)
		#Aqui tengo que filtrar por los isotopos que ha indicado Antonio. Añado el filter(isototo.id)
		#Modificado 06/09/17 quito el actinio 228 (que es el id 1) de ambas consultas de abajo de esto
		if (detector.id == 1001 or detector.id == 1002):
			relacionDetectoresIsotopos=RelacionDetectoresIsotopos.objects.using(using).filter(rel_det_est=detector.id).filter(isototo__in=[4,6,9,11,12,14,15,20,1000])
		else:
			relacionDetectoresIsotopos=RelacionDetectoresIsotopos.objects.using(using).filter(rel_det_est=detector.id).filter(isototo__in=[4,6,9,11,12,14,15,20,1000])
		for relacion in relacionDetectoresIsotopos:
			if relacion.isototo.id != 1000:
					#success warning danger
				print (id_estacion)
				print ("ISO: "+str(relacion.isototo.id))
				ultimo_valor_isotopo=UltimosValoresRecibidos.objects.using(using).filter(isotopo_id=relacion.isototo.id).filter(estacion_id=id_estacion)[0]
				icono='btn-success'
				if ultimo_valor_isotopo.valor > ultimo_valor_isotopo.amd:
					icono='btn-danger'
				nombre=convertir_subindice(relacion.isototo.n_iso)
				#Modificado DAVID 17/02/17
				if relacion.isototo.n_iso=='I-131':
					if "BRLA" in detector.dir_datos:
						nombre=nombre+"(P)"
					else:
						nombre=nombre+"(G)"

				if relacion.isototo.n_iso=='Pb-214':
					if "BRLA" in detector.dir_datos:
						nombre=nombre+"(P)"
					else:
						nombre=nombre+"(G)"

				if relacion.isototo.n_iso=='Bi-214':
					if "BRLA" in detector.dir_datos:
						nombre=nombre+"(P)"
					else:
						nombre=nombre+"(G)"
			else:
				nombre="GT"
				if (detector.id == 1001 or detector.id == 1002 or detector.id == 1006 or detector.id == 1007):
					if "BRLA" in detector.dir_datos:
						nombre=nombre+" (P)"
					else:
						nombre=nombre+" (G)"

			lista_detectores_isotopos+="{'id':'"+str(relacion.isototo.id)+"','id_detector':'"+str(detector.id)+"','abreviado':'"+nombre+"','nombre':'"+relacion.isototo.n_iso+"','artificial':'"+str(relacion.isototo.artificial)+"','icono':'"+icono+"','valor':'"+str(ultimo_valor_isotopo.valor)+"','amd':'"+str(ultimo_valor_isotopo.amd)+"','fecha':'"+ultimo_valor_isotopo.fecha_hora.strftime("%d-%m-%Y %H:%M")+"'},"
	if lista_detectores_isotopos!="":
		lista_detectores_isotopos=lista_detectores_isotopos [:-1]
	lista_detectores_isotopos=eval("["+lista_detectores_isotopos+"]")

	cola.put(lista_detectores_isotopos)
	cola.put(nombre_detectores)
	# Fin 3

def getRadioYodo(id_estacion,cola):
	lista_radon_yodo=""
	relaciones=Relacion.objects.using(using).filter(estac=id_estacion).filter(canal__in=[14,15,16,17])

	for relacion in relaciones:
		try:
			nombre=Canales.objects.using(using).filter(id=relacion.canal)[0].nombre
			nomCad=str(nombre)
			nombreFin=nomCad
			if (nomCad=='ALPHA'):
				nombreFin='ALFA'
			if (nomCad=='IODINE'):
				nombreFin='YODO'
			if (nomCad=='RADON'):
				nombreFin=u'RADÓN'
			#success warning danger
			ultimo_valor_radon_yodo=UltimosValoresRecibidos.objects.using(using).filter(can_det_est=relacion.canal).filter(estacion_id=id_estacion)[0]  
			icono='btn-success'
			lista_radon_yodo+="{"+"'id_estacion':"+id_estacion+",'id_canal':"+str(relacion.canal)+",'nombre':'"+nombreFin+"','icono':'"+icono+"','valor':'"+str(ultimo_valor_radon_yodo.valor)+"','amd':'"+str(ultimo_valor_radon_yodo.amd)+"','fecha':'"+ultimo_valor_radon_yodo.fecha_hora.strftime("%d-%m-%Y %H:%M")+"'},"
		except:
			print ("Error Estacion "+str(id_estacion))
	if lista_radon_yodo!="":
		lista_radon_yodo=lista_radon_yodo [:-1]
	lista_radon_yodo=eval("["+lista_radon_yodo+"]")

	cola.put(lista_radon_yodo)


def getYodoCesio(id_estacion,cola):
	lista_yodo_cesio=""
	relaciones=Relacion.objects.using(using).filter(estac=id_estacion).filter(canal__in=[2,3])

	for relacion in relaciones:
		nombre=Canales.objects.using(using).filter(id=relacion.canal)[0].nombre
		#success warning danger
		ultimo_valor_yodo_cesio=UltimosValoresRecibidos.objects.using(using).filter(can_det_est=relacion.canal).filter(estacion_id=id_estacion)[0]
		icono='btn-success'
		lista_yodo_cesio+="{"+"'id_estacion':"+id_estacion+",'id_canal':"+str(relacion.canal)+",'nombre':'"+str(nombre)+"','icono':'"+icono+"','valor':'"+str(ultimo_valor_yodo_cesio.valor)+"','amd':'"+str(ultimo_valor_yodo_cesio.amd)+"','fecha':'"+ultimo_valor_yodo_cesio.fecha_hora.strftime("%d-%m-%Y %H:%M")+"'},"
	if lista_yodo_cesio!="":
		lista_yodo_cesio=lista_yodo_cesio [:-1]
	lista_yodo_cesio=eval("["+lista_yodo_cesio+"]")
	cola.put(lista_yodo_cesio)

def getMeteorologia(id_estacion,cola):
	ayer = datetime.datetime.now().replace( minute=0,second=0)+datetime.timedelta(hours=-4)
	temperatura=queue.Queue()
	precipitacion=queue.Queue()
	direccion=queue.Queue()
	velocidad=queue.Queue()
	threads = []
	def getTemperatura(id_estacion,cola):
		estMeteorologicas_temperatura=EstMeteorologicas.objects.using(using).filter(estaciones=id_estacion).filter(canales=8).filter(fecha_hora__gt=ayer)
		cola.put(estMeteorologicas_temperatura)
	def getPrecipitacion(id_estacion,cola):
		estMeteorologicas_precipitacion=EstMeteorologicas.objects.using(using).filter(estaciones=id_estacion).filter(canales=10).filter(fecha_hora__gt=ayer)
		cola.put(estMeteorologicas_precipitacion)
	def getDireccion(id_estacion,cola):
		estMeteorologicas_direccion_viento=EstMeteorologicas.objects.using(using).filter(estaciones=id_estacion).filter(canales=7).filter(fecha_hora__gt=ayer)
		cola.put(estMeteorologicas_direccion_viento)
	def getVelocidad(id_estacion,cola):
		estMeteorologicas_velocidad_viento=EstMeteorologicas.objects.using(using).filter(estaciones=id_estacion).filter(canales=6).filter(fecha_hora__gt=ayer)
		cola.put(estMeteorologicas_velocidad_viento)

	threads.append(threading.Thread(target=getTemperatura,args=(id_estacion,temperatura)))
	threads.append(threading.Thread(target=getPrecipitacion,args=(id_estacion,precipitacion)))
	threads.append(threading.Thread(target=getDireccion,args=(id_estacion,direccion)))
	threads.append(threading.Thread(target=getVelocidad,args=(id_estacion,velocidad)))
	

	for i in range(len(threads)):
		threads[i].start()

	for i in range(len(threads)):
		threads[i].join()

	estMeteorologicas_temperatura=temperatura.get()
	estMeteorologicas_precipitacion=precipitacion.get()
	estMeteorologicas_direccion_viento=direccion.get()
	estMeteorologicas_velocidad_viento=velocidad.get()

	meteorologia_maximas=""
	maximo_tem=-10000
	maximo_pre=-10000
	direccion_viento=-1
	if len(estMeteorologicas_precipitacion)!=0:
		fecha=(estMeteorologicas_precipitacion[0].fecha_hora+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H")
		for i in range(len(list(estMeteorologicas_precipitacion))):
			est=estMeteorologicas_precipitacion[i]
			fecha_est=(est.fecha_hora+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H")
			if(fecha!=fecha_est):
				maximo_tem=estMeteorologicas_temperatura[i].valor
				direccion_viento=estMeteorologicas_direccion_viento[i].valor+180
				if(direccion_viento>360):
					direccion_viento=direccion_viento-360

				velocidad_viento=estMeteorologicas_velocidad_viento[i].valor
				#Modificado, he quitado una ' del final antes de la llave
				meteorologia_maximas+="{'hora':'"+fecha.split(" ")[1]+"','maximo_tem':"+str(maximo_tem)+",'maximo_pre':'"+str(maximo_pre)+"','direccion_viento':'"+str(direccion_viento)+"','velocidad_viento':'"+str(velocidad_viento)+"','angulo':'"+"rotacion"+"','icometeo':'"+"sol"+"'},"
				fecha=fecha_est
				maximo_pre=-10000
			if(est.valor>maximo_pre):
				maximo_pre=est.valor
		meteorologia_maximas=meteorologia_maximas[:-1]
		meteorologia_maximas=eval("["+meteorologia_maximas+"]")
	cola.put(meteorologia_maximas)
	cola.put(direccion_viento)


def calculo_icono_viento(direccion_viento):
	 # 7----------Calculamos icono viento
	if(direccion_viento!=-1):
		direccion_viento+=180
		if direccion_viento >=360:
			direccion_viento-=360
		viento_icono=0
		if(direccion_viento<22.5):
			viento_icono=0
		elif(direccion_viento<67.5):
			viento_icono=45
		elif(direccion_viento<112.5):
			viento_icono=90
		elif(direccion_viento<157.5):
			viento_icono=135
		elif(direccion_viento<202):
			viento_icono=180
		elif(direccion_viento<247):
			viento_icono=225
		elif(direccion_viento<292):
			viento_icono=270
		elif(direccion_viento<337):
			viento_icono=315
		elif(direccion_viento<360):
			viento_icono=0
	else:
		viento_icono=-1

	return viento_icono
	# Fin 7
