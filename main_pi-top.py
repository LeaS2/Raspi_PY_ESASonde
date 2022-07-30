import threading
import socket
from datetime import datetime
import pandas as pd
import logging

from pitop import Pitop


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

    # Socket etrstellen und binden
    udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSock.bind((RASPI_IP, ETHERNET_PORT))
    logging.debug("run:    UDP Socket erstellt.")

    # Data Frame zum Speichern der Sensordaten
    df = pd.DataFrame(columns=COLUMN_HEADER)
    logging.debug("run:    Data Frame erstellt.")

    while True:

        # Abbruchbedingung prüfen
        if not start():
            cleanUp(df)
            udpSock.close()
            break

        data = udpSock.recv(1024)                   
        df.loc[df.shape[0]] = (data.decode()).split(",")


# Übersetzt Nutzereingabe
def handleStartButton():
    global readData
    readData = True
    logging.debug("handleStartButton:    True.")

def handleStopButton():
    global readData
    readData = False
    logging.debug("handleStopButton:    False.")

def cleanUp(df):
    
    # Benennung und Speicherung des DataFrame als CSV Datei
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H:%M_") + "Sensordata.csv"
    df.to_csv(filename, index=False)
    logging.debug("cleanUp:    CSV Datei gespeichert.")



if __name__ == '__main__':

    ''' To Do:  
                - Verknüpfung mit pi-Top 
                - sleep einfügen in ReadData oder while True in Main um Leistung zu sparen?          
    '''

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")

    pitop = Pitop()
    miniscreen = pitop.miniscreen
    start = miniscreen.select_button
    stop = miniscreen.cancel_button
    start.when_released = handleStartButton
    stop.when_released = handleStopButton

    while True:

        t1 = threading.Thread(target=run, args=(lambda: readData,)) # need to create new Thread -> evtl. eigene Funktion

        if readData and not t1.is_alive():
            t1.start()
            t1.join()
            logging.debug("Main:    Thread gestartet. Messung sollte starten.")

