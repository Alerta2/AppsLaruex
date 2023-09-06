import random
from datetime import timedelta, datetime
from rare.models import *
from .encryptMethods import *

# generate random datetime between two dates
def random_date(start, end):
    """
    It generates a random date between two dates.
    
    :param start: The start date
    :param end: The end date of the range
    :return: A random datetime between two datetime objects.
    """
    """
    This function will return a random datetime between two datetime objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_seconds = random.randrange(int_delta)
    return start + timedelta(seconds=random_seconds)

# get trimester of a date
def get_trimester(date):
    """
    If the month is in the first quarter, return 1. If the month is in the second quarter, return 2.
    If the month is in the third quarter, return 3. If the month is in the fourth quarter, return 4
    
    :param date: The date to get the trimester for
    :return: The trimester of the date.
    """
    if date.month in [1, 2, 3]:
        return 1
    elif date.month in [4, 5, 6]:
        return 2
    elif date.month in [7, 8, 9]:
        return 3
    elif date.month in [10, 11, 12]:
        return 4

# get first day if a trimester
def get_first_day(trimester, year):
    """
    If the trimester is 1, return the first day of the year. If the trimester is 2, return the first
    day of the second quarter. If the trimester is 3, return the first day of the third quarter. If
    the trimester is 4, return the first day of the fourth quarter
    
    :param trimester: 1, 2, 3, or 4
    :param year: the year of the trimester
    :return: The first day of the trimester.
    """
    if trimester == 1:
        return datetime(year, 1, 1)
    elif trimester == 2:
        return datetime(year, 4, 1)
    elif trimester == 3:
        return datetime(year, 7, 1)
    elif trimester == 4:
        return datetime(year, 10, 1)

def get_last_day(trimester, year):
    """
    It returns the last day of the month for the given trimester and year
    
    :param trimester: 1, 2, 3, or 4
    :param year: the year of the trimester
    :return: The last day of the trimester.
    """
    if trimester == 1:
        return datetime(year, 3, 31)
    elif trimester == 2:
        return datetime(year, 6, 30)
    elif trimester == 3:
        return datetime(year, 9, 30)
    elif trimester == 4:
        return datetime(year, 12, 31)

def generateSimulacronDate():
    """
    It generates a random date that is in the next trimester and between 8AM and 2PM or between 4PM and 8PM
    :return: A date object
    """
    posibleDate = calculatePossibleDate()
    while posibleDate.hour < 9 or (posibleDate.hour > 13 and posibleDate.hour < 16) or posibleDate.hour > 19:
        posibleDate = calculatePossibleDate()
    return posibleDate

def calculatePossibleDate():
    """
    It returns a random date between the first and last day of the next quarter
    :return: A random date between the first and last day of the next trimester.
    """
    # get current trimestre
    trimestreProximo = get_trimester(datetime.now()) + 1
    correcionAnio = 0
    if trimestreProximo == 5:
        correcionAnio = 1
        trimestreProximo = 1
    # get first day of the next trimestre
    firstDay = get_first_day(trimestreProximo, datetime.now().year + correcionAnio)
    # get last day of the next trimestre
    lastDay = get_last_day(trimestreProximo, datetime.now().year + correcionAnio)
    # get random date between first and last day
    randomDate = random_date(firstDay, lastDay)
    return randomDate

def crearNuevoSimulacro():
    fechaSimulacro = random_date(datetime(2022, 5, 25, 12, 30, 0, 0, pytz.timezone("Europe/Madrid")), datetime(2022, 5, 25, 12, 41, 59, 0, pytz.timezone("Europe/Madrid")))
    fechaSimulacroEncriptada = encryptText(str(fechaSimulacro), load_key("monitoriza"))
    SimulacrosRarex(fecha= bytesToString(fechaSimulacroEncriptada), estado=0).save(using='rvra')

def cargarSimulacro():
    if SimulacrosRarex.objects.using('rvra').filter(estado=0).exists():
        simulacro = SimulacrosRarex.objects.using('rvra').filter(estado=0).get()
        fechaSimulacroDesencriptada = stringToDatetime(bytesToString(decryptText(stringToBytes(simulacro.fecha), load_key("monitoriza"))))
        return fechaSimulacroDesencriptada
    else:
        return False

def compararFechas(fecha):
    if fecha is None:
        return 0
    else:
        fechaActual = datetime.now(pytz.timezone("UTC")) + timedelta(hours=2)
        diferencia = int(((fechaActual - fecha).total_seconds())/60)
        #print("Calculando diferencia", "fecha:", fecha, "fecha actual:",fechaActual, "diferencia:", diferencia)
        return diferencia

def compararFechasGMT2(fecha):
    if fecha is None:
        return 0
    else:
        fechaActual = datetime.now(pytz.timezone("Europe/Madrid"))
        diferencia = int(((fechaActual - fecha).total_seconds())/60)
        #print("Calculando diferencia", "fecha:", fecha, "fecha actual:",fechaActual, "diferencia:", diferencia)
        return diferencia