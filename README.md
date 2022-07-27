# Speicherung serieller Daten auf einem Raspberry Pi 3
***
Eingehende Sensordaten (Differenzdrücke mbar, Temperatur in °C) werden über eine Ethernetschnittstelle an Raspi gesendet
und dort in Form von CSV Dateien gespeichert. 

## Generelle Informationen
***
Das Projekt befindet sich in der Testphase und wird laufend an die Versuchsumgebungen angepasst.
Der Code läuft auf einem Raspberry Pi 3 Model B vi 2. Der Ethernet Port des Raspi ist mit einer statische IP Adresse versehen. 

## Installation
***
Informationen zur erfolgreichen Installation auf dem Raspberry Pi: 
```
$ git clone https://github.com/LeaS2/Raspi_ESASonde.git
$ sudo apt update
$ sudo apt upgrade
```
### Zusatzinformation:  
Es ist notwendig die Pandas Library auf dem Raspi zu installieren, die zur Verarbeitung der CSV Dateien verwendet wird. 
```
$ sudo apt-get install python-pandas
```

## Spezifikation des verwendeten Protokolls für die Schnittstelle Sensorboard/Raspi
***
Datenformat: 
* Das Datenformat folgt dem des NMEA Protokolls, sodass die Daten auf der Sensorplatine nur einmal geparsed werden müssen, um an die serielle Schnittstelle und den Raspi versendet werden zu können. 
* Messdaten werden in Form von Strings versendet
* Am Anfang jedes Strings findet sich ein Start-Sign ($) 
* Auf das Start-Sign folgt ein Integerwert, der die Größe des folgenden Datenpakets angibt
* Alle versendeten Daten (Drücke, Temperatur) werden danach hintereinander, getrennt durch Komma (!kein Semikolon!) in den String geschrieben

Datenpaket:
* $ 'Stringgröße', 'Counter', 'Timestamp', 'Latency', 'Pressure 1', 'Pressure 2', 'Pressure 3', 'Pressure 4', 'Pressure 5', 'Pressure 6', 'Pressure 7', 'Temperature 1', 'Temperature 2', 'Temperature 3', 'Temperature 4', 'Temperature 5', 'Temperature 6', 'Temperature 7'

Protokoll: 
* Übertragungsprotokoll ist UDP basiert
* Es werden zuerst die ersten beiden Bytes einer Nachricht eingelesen und geprüft, ob das erste der beiden Zeichen das vordefinierte Start-Sign ist. 
* Wenn es sich um das Start-Sign handelt, wird die Größe des Nachricht im zweiten Bytes ausgelesen und die Nachricht in dem entsprechenden Umfang empfangen
* Handelt es sich nicht um das Start-Sign, geht das Programm in eine Suchschleife und wertet jedes neu ankommende Byte einzeln aus, bis ein neues Start-Sign empfangen wird. 
* Es wird toleriert, dass einzelne Datenpakete verloren gehen können. Jedes Datenpaket ist mit einer ID gekennzeichnet, die aufsteigend vergeben werden. So kann im Nachhinein die Menge verlorener Datenpakete analysiert werden. 

## Code-Anforderungen
***
* User-Schnittstelle: 
    * Aufzeichnung der Sensordaten wird per Knopfdruck gestartet und beendet
    * Über einen Bildschirm gibt der Raspi Auskunft über seinen aktuellen Zustand
* Nachdem das Programm gestartete wurde, wird die Datenverbindung zur Platine hergestellt 
* Die Daten werden in ein CSV Datei geschrieben
    * Im Header des Files sind folgenden Informationen enthalten: Datum, aktuelle Uhrzeit (UTC+2), 
    * Alle weiteren Zeilen haben folgende Spaltenaufteilung: 
    * Nachdem wegschreiben jeder Zeile wird der RAM geflushed, sodass einem Überlauf vorgebeugt werden kann 
    * Im Falle eines Verbindungsabbruch:
        * Error- Meldung wird auf Bildschirm ausgeben (und in Log Datei gespeichert)
        * Verbindung wird geschlossen und die Datei gespeichert. Das Programm springt zurück zum Anfang und wartet auf eine Eingabe, um ggfs. eine neue Messreihe zu starten. 
* Wird der Knopf ein zweites Mal gedrückt, wird die Verbindung zur Sensorplatine sowie das CSV File geschlossen. Die Datei mit den Messdaten ist auf der SD Karte des Raspi gespeichert.


## Nächste Schritte
***
* Soll-Feature: 
    * Autostart: Programm startet automatisch beim Anschalten des Raspi
    * Log-Datei im Programm mitschreiben, die später die Analyse von Fehlern und das Debugging in der Testphase erleichtert 
    
* Kann-Feature: 
    * Aufzeichnungsfrequenz auf Platine (SPS) via Raspi setzten können
        * Idee: Konfig-Datei auf Raspi hinterlegen. Dort lassen sich die entsprechenden Werte zur Konfigurierung der Sensorplatine ändern. Die Datei wird mit dem Start der Messungen eingelesen und an die Sensorplatine geschickt. Diese sendet Acknowledge sobald die Konfiguierung abgeschlossen ist. Dann erst startet der Messdurchgang. 
* Testlauf: 
    * gesamte Messstrecke über Zeit testen (Überhitzung, Speicherüberlauf, sonstige Störeinflüsse die bisher unbeachtet waren) mit anschließender Analyse des Log File