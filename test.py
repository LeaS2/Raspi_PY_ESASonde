import threading
import socket
import datetime
import pandas as pd
import logging
import RPi.GPIO as GPIO


# Konstanten
BUTTON_PORT = 16
ETHERNET_PORT = 7
RASPI_IP = "192.168.0.5"
SENSORBOARD_IP = "192.168.0.3"
COLUMN_HEADER = ['Counter', 'Timestamp', 'Latency', 'Pressure 1', 'Pressure 2', 'Pressure 3', 'Pressure 4', 'Pressure 5', 'Pressure 6',
                 'Pressure 7', 'Temperature 1', 'Temperature 2', 'Temperature 3', 'Temperature 4', 'Temperature 5', 'Temperature 6', 'Temperature 7']

# Globale Variable 
readData = False


def run(start):

    # Data Frame zum Speichern der Sensordaten
    df = pd.DataFrame(columns=COLUMN_HEADER)
    logging.debug("run:    Data Frame erstellt.")

    while True:

        # Abbruchbedingung prüfen
        if not start():
            cleanUp(df)
            break

    

        
def handleButtonPressed():

    # Übersetzt Nutzereingabe
    global readData
    readData = not readData
    logging.debug("handleButtonPressed:    Nutzereingabe erkannt.")

def cleanUp(df):

    # Benennung und Speicherung des DataFrame als CSV Datei
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H:%M_") + "Sensordata.csv"
    df.to_csv(filename, index=False)
    logging.debug("cleanUp:    CSV Datei gespeichert.")



if __name__ == '__main__':

    ''' To Do:  
                - LCD Lib -> Bildschirmausgaben einfügen 
                - GPIO Kofigurationen zurücksetzten?
                - Read Data Funktion schreiben
                - sleep einfügen in ReadData oder while True in Main?          
    '''

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")

    # GPIO Konfigurationen erstellen
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PORT, GPIO.FALLING, callback=handleButtonPressed, bouncetime=100)
    logging.debug("Main:    GPIO Eingänge konfiguriert. Wartet auf Nutzereingabe.")

    t1 = threading.Thread(target=run, args=(lambda: readData,))

    while True:
        if readData and not t1.is_alive():
            t1.start()
            t1.join()
            logging.debug("Main:    Thread gestartet. Messung sollte starten.")
