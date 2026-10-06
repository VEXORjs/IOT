import paho.mqtt.client as mqtt
import time
import json
import random

# Adres brokera
broker_address = "localhost"
# Tworzenie klienta MQTT
client = mqtt.Client(client_id="Door_Terminal")
client.connect(broker_address)

def simulate_card(rfid_uid):
    """
    Symulacja identyfikatora karty

    :param rfid_uid:
    :return:
    """
    content = {
        "event_type": "RFID_READ",
        "uid": rfid_uid
    }
    # Publikacja komunikatu (etykieta, dane) do brokera
    client.publish("labs/lab_01/hardware/rfid", json.dumps(content))


def simulate_pin(pin):
    """
    Symulacja podania wartości PIN na klawiaturze

    :param pin:
    :return:
    """
    content = {
        "event_type": "PIN_READ",
        "pin": pin
    }
    # Publikacja komunikatu (etykieta, dane) do brokera
    client.publish("labs/lab_01/hardware/pin", json.dumps(content))