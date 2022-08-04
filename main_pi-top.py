import threading
import socket
from datetime import datetime
import pandas as pd
import logging
from time import sleep
from pitop import Pitop


# Konstanten
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
    logging.info("run:    UDP Socket erstellt.")

    # Data Frame zum Speichern der Sensordaten
    df = pd.DataFrame(columns=COLUMN_HEADER)
    logging.info("run:    Data Frame erstellt.")

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
    readData = not readData
    logging.info("handleStartButton:    True.")

# Daten sichern sobald Batteriezustand kritisch
def handleLowBattery():
    global readData
    if readData: 
        readData = False
    logging.info("handleLowBattery:    Set ReadData False.")

# Benennung und Speicherung des DataFrame als CSV Datei
def cleanUp(df):
    
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H:%M_") + "Sensordata.csv"
    df.to_csv(filename, index=False)
    miniscreen.display_multiline_text("Daten wurden erfolgreich gespeichert.")
    logging.info("cleanUp:    CSV Datei gespeichert.")
    sleep(2)


if __name__ == '__main__':

    pitop = Pitop()
    miniscreen = pitop.miniscreen
    miniscreen.display_image_file("/home/pi/Raspi_PY_ESASonde/segelflugzeug_icon.png")

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")

    # Button-Funktionen initialisieren
    start = miniscreen.select_button
    stop = miniscreen.cancel_button
    battery = Pitop().battery
    battery.when_critical = handleLowBattery            # Text ausgeben / Code beenden
    start.when_released = handleStartButton

    miniscreen.display_multiline_text("Programm: O:Starten X:Beenden")

    while not stop.is_pressed:
        
        if readData:
            t1 = threading.Thread(target=run, args=(lambda: readData,)) # need to create new Thread -> evtl. eigene Funktion
            miniscreen.display_multiline_text("Messung läuft.")
            sleep(0.5)
            miniscreen.display_multiline_text("O:Messung beenden.")
            t1.start()
            logging.info("Main:    Thread gestartet. Messung sollte starten.")
            t1.join()
            logging.info("Main:    Thread beendet. Messung sollte gespeichert sein.")
            miniscreen.display_multiline_text("Akkustand: " + str(battery.capacity) + '%' )
            sleep(2)
    
    miniscreen.display_multiline_text("Programm beendet.")

