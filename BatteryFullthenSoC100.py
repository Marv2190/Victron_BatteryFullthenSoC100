# Dieses Script überprüft wieviel Energie exportiert wird und ob der Akku dementsprechend geladen wird.
# Wenn der Akku nicht geladen wird, muss er voll sein -> 100% SoC wid gesetzt.
# Script funktioniert nur in On-Grid Systemen, da sonst nicht exportiert wird.

import time
import paho.mqtt.client as mqtt
import logging
import json


cerboserial = "123456789"    # Ist auch gleich VRM Portal ID
broker_address = "192.168.1.xxx"


#  Einstellen der Limits

Watttreshold = 200  # LadeLimit unter dessen das Script aktiv wird.
minexportwatt = -1000  # Wattlimit, darunter wird das Script nicht aktiv.
timetresholsoll = 5  # Wieviel Minuten müssen andere Limits erreicht sein, um Akku auf 100% zu setzen.

# Variblen setzen
verbunden = 0
timetresholdis = 0
durchlauf = 1
grid = 0
soc = 0
power = 0

logging.basicConfig(filename='Error.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def on_disconnect(client, userdata, rc):
    global verbunden
    print("Client Got Disconnected")
    if rc != 0:
        print('Unexpected MQTT disconnection. Will auto-reconnect')

    else:
        print('rc value:' + str(rc))

    try:
        print("Trying to Reconnect")
        client.connect(broker_address)
        verbunden = 1
    except Exception as e:
        logging.exception("Fehler beim reconnecten mit Broker")
        print("Error in Retrying to Connect with Broker")
        verbunden = 0
        print(e)

def on_connect(client, userdata, flags, rc):
        global verbunden
        if rc == 0:
            print("Connected to MQTT Broker!")
            verbunden = 1
            client.subscribe("N/" + cerboserial + "/vebus/276/Ac/ActiveIn/P")
            client.subscribe("N/" + cerboserial + "/vebus/276/Soc")
            client.subscribe("N/" + cerboserial + "/system/0/Dc/Battery/Power")
        else:
            print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:

        global grid, soc, power
        if msg.topic == "N/" + cerboserial + "/vebus/276/Ac/ActiveIn/P":   # Grid Import/Export

            grid = json.loads(msg.payload)
            grid = round(float(grid['value']), 2)

        if msg.topic == "N/" + cerboserial + "/vebus/276/Soc":   # Aktueller SoC

            soc = json.loads(msg.payload)
            soc = round(float(soc['value']), 2)

        if msg.topic == "N/" + cerboserial + "/system/0/Dc/Battery/Power":   # Akku Power

            power = json.loads(msg.payload)
            power = round(float(power['value']), 2)

    except Exception as e:
        print(e)
        print("Im BFtS100 Programm ist etwas beim auslesen der Nachrichten schief gegangen")

# Konfiguration MQTT
client = mqtt.Client("BFtS100")  # create new instance
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)  # connect to broker

logging.debug("Programm BFtS100 wurde gestartet")

client.loop_start()
time.sleep(2)
print(grid, soc, power)
while(1):
    print(durchlauf)
    durchlauf = durchlauf + 1
    if soc >= 98:
        print("Akku SoC ist bereits über 98% =)\n")
    elif grid <= minexportwatt and power <= Watttreshold:
        if power <= minexportwatt+100:
            print("Aus dem Akku wird aktuell zuviel ins Netz exportiert!")
        elif timetresholdis == timetresholsoll:
            print("Akku scheint voll zu sein, setze SoC auf 100%")
            client.publish("W/" + cerboserial + "/vebus/276/Soc", '{"value": 100 }')
            timetresholdis = 0
        else:
            print("Limits wurden erreicht. Wartezeit: " + str(timetresholdis) + " Minuten von " + str(timetresholsoll) + " Minuten")
            timetresholdis = timetresholdis + 1
    else:
        if grid <= minexportwatt:
            print("Akku wird noch zuviel geladen. Aktueller Energiefluss: " + str(power) + " Limit: " + str(Watttreshold))
            timetresholdis = 0
        else:
            print("Es wird zuwenig exportiert! Aktueller Energiefluss: " + str(grid) + " Limit: " + str(minexportwatt))
            timetresholdis = 0
    time.sleep(60)
