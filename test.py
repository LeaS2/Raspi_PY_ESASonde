import threading
from datetime import datetime
import pandas as pd
import logging
import RPi.GPIO as GPIO
from time import sleep

# Konstanten
BUTTON_PORT = 16
ETHERNET_PORT = 7
RASPI_IP = "192.168.0.5"
SENSORBOARD_IP = "192.168.0.3"
COLUMN_HEADER = ['Eins', 'Zwei', 'Drei', 'Vier']

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

        pseudoMessage = ['Was', 'will', 'man', 'mehr']
        df.loc[df.shape[0]] = pseudoMessage
        sleep(10)                 
      
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
    GPIO.setup(19, GPIO.OUT)
    GPIO.add_event_detect(BUTTON_PORT, GPIO.FALLING, callback=handleButtonPressed, bouncetime=100)
    logging.debug("Main:    GPIO Eingänge konfiguriert. Wartet auf Nutzereingabe.")

    t1 = threading.Thread(target=run, args=(lambda: readData,))

    while True:
        if readData and not t1.is_alive():
            GPIO.output(19, GPIO.HIGH)
            t1.start()
            t1.join()
            logging.debug("Main:    Thread gestartet. Messung sollte starten.")
        elif not readData: 
            GPIO.output(19, GPIO.LOW)
