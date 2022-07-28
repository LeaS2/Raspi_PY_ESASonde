import socket
from datetime import datetime
import pandas as pd
import logging


# Konstanten
BUTTON_PORT = 16
ETHERNET_PORT = 7
RASPI_IP = "192.168.0.5"
SENSORBOARD_IP = "192.168.0.3"
COLUMN_HEADER = ['Timestamp', 'Counter', 'Pressure 1', 'Pressure 2', 'Pressure 3', 'Pressure 4', 'Pressure 5', 'Pressure 6',
                 'Pressure 7', 'Temperature 1', 'Temperature 2', 'Temperature 3', 'Temperature 4', 'Temperature 5', 'Temperature 6', 'Temperature 7']


def run(druck):

    # Socket etrstellen und binden
    udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSock.bind((RASPI_IP, ETHERNET_PORT))
    logging.debug("run:    UDP Socket erstellt.")

    # Data Frame zum Speichern der Sensordaten
    df = pd.DataFrame(columns=COLUMN_HEADER)
    logging.debug("run:    Data Frame erstellt.")

    while True:                                             # Timer einfügen

        # Einlesen der ersten beiden Bytes 
        checkBuf = udpSock.recv(1) 
        print(checkBuf)                   
        # checkBuf = checkBuf.decode()

        # Prüft Start-Sign und Senderadresse
        if checkBuf[0] == '$':
            
            size = ""

            while True:
                temp = udpSock.recv(1)
                if temp == ',':
                    break

                size = size + temp
            
            print(size)    

            data = udpSock.recv(ord(size))
            df.loc[df.shape[0]] = (data.decode()).split(",")                            
        #elif checkBuf[1] == '$':
            #dataSize = udpSock.recv(1)
            #data = udpSock.recv(ord(dataSize.decode()))
            #df.loc[df.shape[0]] = (data.decode()).split(",")
        else: 
            break 


def cleanUp(df):
    
    # Benennung und Speicherung des DataFrame als CSV Datei
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H:%M_") + "Sensordata.csv"
    df.to_csv(filename, index=False)
    logging.debug("cleanUp:    CSV Datei gespeichert.")


if __name__ == '__main__':

    ''' To Do:  
                - Verknüpfung mit pi-Top 
                - Müssen GPIO Kofigurationen zurücksetzten werden? 
                - sleep einfügen in ReadData oder while True in Main um Leistung zu sparen?          
    '''

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")

    while True:

        userInput = input("Drücke: j [Messung starten] | n [Programm beenden] ")
        if userInput == 'j':
            druck = input("Anliegender Druck: ")
            print('Eingabe: %s', druck)
            bestaetigung = input("Korrekte Eingabe? j[ja] / n[nein]")
            if bestaetigung == 'j':
                run(int(druck))
            else: 
                continue
        elif userInput == 'n':
            break
        else: 
            continue
