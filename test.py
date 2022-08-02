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
    print('DataFrame - Messung läuft')

    while True:

        # Abbruchbedingung prüfen
        if not start():
            cleanUp(df)
            break

        pseudoMessage = ['Was', 'will', 'man', 'mehr']
        df.loc[df.shape[0]] = pseudoMessage
        sleep(1)                 
      
def handleButtonPressed(BUTTON_PORT):

    # Übersetzt Nutzereingabe
    print('read Data aufgerufen')
    global readData
    readData = not readData
    print('read Data geändert: %b', readData)

def cleanUp(df):

    # Benennung und Speicherung des DataFrame als CSV Datei
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H:%M_") + "Sensordata.csv"
    df.to_csv(filename, index=False)
    GPIO.cleanup()
    print('CleanUp aufgerufen')

if __name__ == '__main__':

    # Log-File erstellen
    # logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    # logging.info("Main:     Programm gestartet.")

    # GPIO Konfigurationen erstellen
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PORT, GPIO.FALLING, callback=handleButtonPressed, bouncetime=200)

    print('Programm läuft')

    try: 
        while True:
            if readData:
                t1 = threading.Thread(target=run, args=(lambda: readData,))
                print('Thread erstellt')
                GPIO.output(19, GPIO.HIGH)
                t1.start()
                t1.join()
                GPIO.output(19, GPIO.LOW)
                print('Thread schließt')

    except KeyboardInterrupt: 
        GPIO.cleanup()


