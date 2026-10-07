import paho.mqtt.client as mqtt
import random
import json

# Adres brokera
broker_address = "localhost"
# Tworzenie klienta MQTT
client = mqtt.Client(client_id="Lab_thermometer")
client.connect(broker_address)


def simulate_temperature():
    """
    Symulacja odczytu wartosći temperatury

    :return:
    """
    # Generowanie wartości None, szansa 5 procent
    if random.random() < 0.05:
        return None

    # Rozkład normalny (wartość środkowa, odchylenie standardowe), wartość w stopniach C
    temperature = random.gauss(22.0,0.5)
    return temperature

def simulate_humidity():
    """
    Symulacja odczytu wartości wilgotności

    :return:
    """
    # Generowanie wartości None, szansa 5 procent
    if random.random() < 0.05:
        return None
    # Rozkład normalny (wartość środkowa, odchylenie standardowe), wartość w procentach
    humidity = random.gauss(45.0,1.0)
    return humidity

def simulate_lights():
    """
    Symulacja odczytu wartości światłą

    :return:
    """
    # Generowanie wartości None, szansa 5 procent
    if random.random() < 0.05:
        return None

    # Rozkład normalny (wartość środkowa, odchylenie standardowe), wartość w Lux
    light = random.gauss(400.0,5.0)
    return light

def simulate_noise():
    """
    Symulacja odczytu wartości poziomu dźwięku

    :return:
    """
    # Generowanie wartości None, szansa 5 procent
    if random.random() < 0.05:
        return None

    # Rozkład normalny (wartość środkowa, odchylenie standardowe), wartość w Lux
    light = random.gauss(50.0,5.0)
    return light


environment_data = {
    "temperature" : simulate_temperature,
    "humidity" : simulate_humidity,
    "lights" : simulate_lights,
    "noise" : simulate_noise,
}

client.publish("labs/lab_01/hardware/environment", json.dumps(environment_data))