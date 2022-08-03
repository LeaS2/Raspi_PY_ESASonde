import threading
import socket
from datetime import datetime
import pandas as pd
import logging
from time import sleep
from pitop import Pitop

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
    logging.info("handleStartButton:    True.")

# Daten sichern sobald Batteriezustand kritisch
def handleLowBattery():
    global readData
    if readData: 
        readData = False
    logging.info("handleLowBattery:    Set ReadData False.")


def cleanUp(df):
    
    # Benennung und Speicherung des DataFrame als CSV Datei
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
    sleep(1)

    # Log-File erstellen
    logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Main:     Programm gestartet.")
    
    start = miniscreen.select_button
    stop = miniscreen.cancel_button
    battery = Pitop().battery
    battery.when_critical = handleLowBattery
    start.when_released = handleStartButton

    while not stop.is_pressed:
        
        miniscreen.display_multiline_text("Programm: O: Starten   X: Beenden")

        if readData:
            t1 = threading.Thread(target=run, args=(lambda: readData,)) # need to create new Thread -> evtl. eigene Funktion
            miniscreen.display_multiline_text("Messung läuft.")
            sleep(2)
            miniscreen.display_multiline_text("O: Messung beenden.")
            t1.start()
            logging.info("Main:    Thread gestartet. Messung sollte starten.")
            t1.join()
            logging.info("Main:    Thread beendet. Messung sollte gespeichert sein.")
            miniscreen.display_multiline_text("Akkustand: " + str(battery.capacity) + '%' )
            sleep(2)
        

    
    miniscreen.display_multiline_text("Programm beendet.")
    

