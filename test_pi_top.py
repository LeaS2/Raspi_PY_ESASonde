import threading
import socket
from datetime import datetime
import pandas as pd
import logging
from time import sleep
from pitop import Pitop
from PIL import Image, ImageDraw


# Konstanten
BUTTON_PORT = 16
ETHERNET_PORT = 7
RASPI_IP = "192.168.0.5"
SENSORBOARD_IP = "192.168.0.3"
COLUMN_HEADER = ['StartSign', 'Timestamp', 'Counter', 'Pressure 1', 'Pressure 2', 'Pressure 3', 'Pressure 4', 'Pressure 5', 'Pressure 6',
                 'Pressure 7', 'Temperature 1', 'Temperature 2', 'Temperature 3', 'Temperature 4', 'Temperature 5', 'Temperature 6', 'Temperature 7']

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


# Übersetzt Nutzereingabe
def handleStartButton():
    global readData
    readData = not readData
    logging.debug("handleStartButton:    True.")


def cleanUp(df):
    
    # Benennung und Speicherung des DataFrame als CSV Datei
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H:%M_") + "Sensordata.csv"
    df.to_csv(filename, index=False)
    miniscreen.display_multiline_text("Daten wurden erfolgreich gespeichert.")
    logging.debug("cleanUp:    CSV Datei gespeichert.")
    sleep(2)


if __name__ == '__main__':

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")

    pitop = Pitop()
    miniscreen = pitop.miniscreen
    image = Image.open("segelflugzeug_icon.png")
    start = miniscreen.select_button
    stop = miniscreen.cancel_button
    start.when_released = handleStartButton

    while not stop:
        
        miniscreen.display_multiline_text("Programm läuft: Drücke Kreis, um die Messung zu starten!")
        if readData:
            t1 = threading.Thread(target=run, args=(lambda: readData,)) # need to create new Thread -> evtl. eigene Funktion
            miniscreen.display_multiline_text("Messung läuft.")
            sleep(0.5)
            miniscreen.display_multiline_text("Drücke erneut Kreis, um die Messung zu beenden.")
            t1.start()
            logging.debug("Main:    Thread gestartet. Messung sollte starten.")
            t1.join()
            ("Main:    Thread beendet. Messung sollte gespeichert sein.")
    
    miniscreen.display_multiline_text("Programm beendet. Tschau! :)")

