from django.http.response import JsonResponse
from docLaruex.models import *

############## Comprobar habilitación dado un objeto  ##############
def comprobarHabilitacionObjeto(id_objeto):
    habilitacionNecesaria = Objeto.objects.using("docLaruex").filter(id=id_objeto).values('id_habilitacion').first()
    return habilitacionNecesaria.get('id_habilitacion')

############## Comprobar habilitación dado un usuario  ##############
def comprobarHabilitaciones(id_user):
    if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo__in=['Administrador', 'Auditor', 'Director Técnico', 'Subdirector Técnico']).exists():
        habilitaciones = Habilitaciones.objects.using("docLaruex").values_list('id', flat=True)
        return list(habilitaciones)
    else:
        habilitaciones = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user).values_list('id_habilitacion', flat=True)
        return list(habilitaciones)

############## Comprobar habilitación almacen dado un usuario  ##############
def comprobarHabilitacionesTitulo(id_user):
    if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo__in=['Administrador', 'Auditor', 'Director Técnico', 'Subdirector Técnico']).exists():
        habilitaciones = Habilitaciones.objects.using("docLaruex").values_list('titulo', flat=True)
        return list(habilitaciones)
    else:
        habilitaciones = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user).values_list('id_habilitacion__titulo', flat=True)
        return list(habilitaciones)

def esAdministrador(id_user):
    return RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Administrador').exists()


def esDirector(id_user):
    if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Director Técnico') or RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Subdirector Técnico') :
        return True
    else:
        return False
    
def esSecretaria(id_user):
    return RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Administración y Secretaría').exists()

############## Comprobar habilitación dado un usuario y una habilitación ##############

def comprobarHabilitacion(id_user, id_hab):
    rol = "nada"
    if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo='Administrador').exists():
        habilitaciones = Habilitaciones.objects.using("docLaruex").values_list('id', flat=True)
        cargoEncontrado = "Responsable"
        return list(habilitaciones),cargoEncontrado,"Administrador"
    elif RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo__in=['Director Técnico', 'Subdirector Técnico']).exists():
        habilitaciones = Habilitaciones.objects.using("docLaruex").values_list('id', flat=True)
        cargoEncontrado = "Técnico"
        if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user, id_habilitacion=id_hab).exists():
            cargoEncontrado = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user, id_habilitacion=id_hab).values('tipo').first()
        return list(habilitaciones),cargoEncontrado,"Director"
    elif RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user,id_habilitacion__titulo__in=['Administración y Secretaría']).exists():
        habilitaciones = Habilitaciones.objects.using("docLaruex").values_list('id', flat=True)
        cargoEncontrado = "Nada"
        if RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user, id_habilitacion=id_hab).exists():
            cargoEncontrado = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user, id_habilitacion=id_hab).values('tipo').first()
        return list(habilitaciones),cargoEncontrado,"Secretaria"
    else:
        habilitaciones = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user).values_list('id_habilitacion', flat=True)
        cargo = RelUsuarioHabilitaciones.objects.using("docLaruex").filter(id_usuario=id_user, id_habilitacion=id_hab).values('tipo').first()
        if 11 in list(habilitaciones):
            rol = "Secretaria"
        if cargo:
            cargoEncontrado = cargo.get('tipo')
        else:
            cargoEncontrado = "Ninguno"
        return list(habilitaciones),cargoEncontrado,rol


############## Comprobar habilitación dado un usuario y una habilitación ##############
def comprobarResponsableAlmacen(habilitaciones):

    existe = next((s for s in habilitaciones if "Almacén".lower() in s.lower()), None)
    if existe:
        return True
    else:
        return False

import pandas as pd
def filtrarBD():
    
    df = pd.read_excel("C:\\Users\\San\\Downloads\\INVEN.xlsx")
    df.sort_values(by='FECHA_ALTA', ascending = False, inplace = True) 

    for i in range(len(df)):
        if df.iloc[i]["LIBRO"] != "S":
            # variables que necesito almacenar en mi nueva base de datos en objeto
            nombre, tipo, estado, habilitacion = "", "Equipo", "", 6

            camposTexto= df.iloc[i]["TEXTO"].split(" ")
            if camposTexto[0].isnumeric():
                nombre = df.iloc[i]["TEXTO"].replace(camposTexto[0]+" ","")
            elif df.iloc[i]["TEXTO"].startswith('UN '):
                nombre = df.iloc[i]["TEXTO"].replace("UN ","")
            else:
                nombre = df.iloc[i]["TEXTO"]

            if df.iloc[i]["A_B"] == "A":
                estado = 1
            else:
                estado = 7
            
            print("-----------------------\nNombre: ", nombre, "\nTipo: ", tipo, "\nEstado: ", estado, "\nHabilitacion: ", habilitacion, "\n-----------------------")
            
            # variables que necesito almacenar en mi nueva base de datos en equipos¡
            codLaruex, numSerie, descripcion, fechaAlta, fechaBaja, precio, fabricante, tipoEquipo, modelo = "", "", nombre, "","","","",23,""

            codLaruex = df.iloc[i]["NUMERO"]
            print("Numero de serie es ", df.iloc[i]["N_SERIE"])
            if "NaN" in str(df.iloc[i]["N_SERIE"]) or "-  -  -" in str(df.iloc[i]["N_SERIE"]) or "nan" in str(df.iloc[i]["N_SERIE"]):
                numSerie = "-"
            else:
                numSerie = df.iloc[i]["N_SERIE"]

            from datetime import datetime

            fechaAlta = datetime.strptime(str(df.iloc[i]["FECHA_ALTA"]), '%Y-%m-%d %H:%M:%S')
            if not "NaT" in str(df.iloc[i]["FECHA_BAJA"]):
                fechaBaja = datetime.strptime(str(df.iloc[i]["FECHA_BAJA"]), '%Y-%m-%d %H:%M:%S')
            else:
                fechaBaja = None

            precio = df.iloc[i]["EUROS"]

            if "NaN" in str(df.iloc[i]["MODELO"]) or "XX" in str(df.iloc[i]["MODELO"]) or "xx" in str(df.iloc[i]["MODELO"]) or "-  -  -" in str(df.iloc[i]["MODELO"]) or "nan" in str(df.iloc[i]["MODELO"]):
                modelo = None
            else:
                modelo = df.iloc[i]["MODELO"]

            if "NaN" in str(df.iloc[i]["FABRICANTE"]) or "XX" in str(df.iloc[i]["FABRICANTE"]) or "xx" in str(df.iloc[i]["FABRICANTE"]) or "-  -  -" in str(df.iloc[i]["FABRICANTE"]) or "nan" in str(df.iloc[i]["FABRICANTE"]):
                fabricante = None
            else:
                fabricante = df.iloc[i]["FABRICANTE"]
        
            #buscar el fabricante

            if not fabricante:
                print("buscamos por la marca")
                if "NaN" in str(df.iloc[i]["MARCA"]) or "XX" in str(df.iloc[i]["MARCA"]) or "xx" in str(df.iloc[i]["MARCA"]) or "-  -  -" in str(df.iloc[i]["MARCA"]) or "nan" in str(df.iloc[i]["MARCA"]):
                    fabricante = None
                else:
                    fabricante = df.iloc[i]["MARCA"]

            if fabricante:
                fabricantes = Fabricante.objects.using("docLaruex").filter(nombre__icontains=fabricante)
                if fabricantes:
                    fabricante = fabricantes.first().id                    
                else:
                    fabricante = 21
            else:
                fabricante = 21
            print("-----------------------\nCodLARUEX: ", codLaruex, "\nNumSerie: ", numSerie, "\nDescripcion: ", descripcion, "\nFechaAlta: ", fechaAlta, "\nFechaBaja: ", fechaBaja, "\nPrecio: ", precio, "\nFabricante: ", fabricante, "\nTipo: ", tipoEquipo, "\nModelo: ", modelo, "\n-----------------------")
            ubicacion = 1

            if Equipo.objects.using('docLaruex').filter(cod_laruex=codLaruex).exists():
                print("Ya existe un equipo registrado con ese código")
            else:
                icono = '<i class="fa-solid fa-plug fa-2x"></i>'
                creador = AuthUser.objects.using('docLaruex').filter(id=50)[0]
                estado = Estado.objects.using('docLaruex').filter(id=estado)[0]
                habilitacion = Habilitaciones.objects.using('docLaruex').filter(id=habilitacion)[0]
                nuevoObjeto = Objeto(nombre=nombre, fecha_subida=datetime.now(), tipo=tipo, creador=creador, id_estado=estado, id_habilitacion=habilitacion, icono=icono)
                nuevoObjeto.save(using='docLaruex')

                nuevoEquipo = Equipo(id=nuevoObjeto, cod_laruex=codLaruex, cod_uex=0, tipo_equipo=TipoEquipo.objects.using("docLaruex").filter(id=tipoEquipo).get(), fecha_alta=fechaAlta, fecha_baja=fechaBaja, fabricante=Fabricante.objects.using("docLaruex").filter(id=fabricante).get(), num_serie=numSerie, descripcion=descripcion, precio = precio, modelo= modelo)
                nuevoEquipo.save(using='docLaruex')

                nuevoEquipoUbicado=RelUbicacionesEquipos(id_equipo=nuevoEquipo, id_ubicacion=Ubicaciones.objects.using("docLaruex").filter(id=ubicacion).get(), fecha=fechaAlta)  
                nuevoEquipoUbicado.save(using='docLaruex')