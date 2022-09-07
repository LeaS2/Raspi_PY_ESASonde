import socket
from datetime import datetime
import pandas as pd
import logging
import time
import numpy as np


# Konstanten
BUTTON_PORT = 16
ETHERNET_PORT = 7
RASPI_IP = "192.168.0.5"
SENSORBOARD_IP = "192.168.0.3"
COLUMN_HEADER = ['StartSign', 'Timestamp', 'Counter', 'Pressure 1', 'Pressure 2', 'Pressure 3', 'Pressure 4', 'Pressure 5', 'Pressure 6',
                 'Pressure 7', 'Temperature 1', 'Temperature 2', 'Temperature 3', 'Temperature 4', 'Temperature 5', 'Temperature 6', 'Temperature 7']
RUNTIME = 2            # in Sekunden

def run(druck, sps):

    # Socket etrstellen und binden
    udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSock.bind((RASPI_IP, ETHERNET_PORT))
    logging.debug("run:    UDP Socket erstellt.")

    data_matrix = []
    print(type(data_matrix))
    t_end = time.time() + RUNTIME
    while  time.time() < t_end:                                            

        # Einlesen der Datenpakete
        data = udpSock.recv(100)                   
        data_matrix = data_matrix.append(data)
        #print(data.decode())
 
    
    # cleanUp(data_matrix, druck, sps)


def cleanUp(data, druck, sps):

    # Data Frame zum Speichern der Sensordaten
    df = pd.DataFrame(columns=COLUMN_HEADER)
    logging.debug("run:    Data Frame erstellt.")
    
    # Benennung und Speicherung des DataFrame als CSV Datei
    for i in data:

        df.loc[df.shape[0]] = (data[i].decode()).split(",")

    now = datetime.now()
    filename = sps + '_' + druck + now.strftime("_%Y-%m-%d_%H:%M") + ".csv"
    df.to_csv(filename, index=False)
    logging.debug("cleanUp:    CSV Datei gespeichert.")


if __name__ == '__main__':

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")

    while True:

        userInput = input("Drücke: j [Messung starten] | n [Programm beenden] ")
        if userInput == 'j':
            druck = input("Anliegender Druck: ")
            sps = input("Eingestellte SPS: ")
            print('Eingabe:' + druck + ' - ' + sps)
            bestaetigung = input("Korrekte Eingabe? j[ja] / n[nein]")
            if bestaetigung == 'j':
                run(druck, sps)
            else: 
                continue
        elif userInput == 'n':
            break
        else: 
            continue
