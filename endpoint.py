import threading
import paho.mqtt.client as mqtt
import json
import sqlite3
import time
import hashlib


class Endpoint:
    def __init__(self):
        # Konfiguracja MQTT
        self.client = mqtt.Client()
        self.client.on_message = self.on_message

        # Stan maszyny
        self.state = {"status": "BOOT"}

        # Baza danych offline
        self.db = sqlite3.connect("buffer.db")
        self.db.execute("CREATE TABLE IF NOT EXISTS events(czas TEXT, id_urzadzenia TEXT, dane_czujnikow TEXT)")

        # Zmienne dla mechanizmu autoryzacji
        self.auth_in_progress = False
        self.current_rfid = None
        self.auth_timer = None

        # Wczytanie białej listy
        try:
            with open("auth_config.json", "r") as f:
                config = json.loads(f.read())
                self.whitelist = config["whitelist_rfid"]
                self.pins = config["valid_pins"]
        except FileNotFoundError:
            print("Błąd")
            self.whitelist = {}
            self.pins = {}

    def on_message(self, client, userdata, message):
        """
        Zarządzanie przyjmowanymi wiadomościami

        :param client:
        :param userdata:
        :param message:
        :return:
        """
        topic = message.topic
        message_payload = message.payload.decode("utf-8")
        data = json.loads(message_payload)

        match topic:
            case "labs/lab_01/hardware/rfid":
                self.handle_rfid(data.get("uid"))

            case "labs/lab_01/hardware/pin":
                self.handle_pin(data.get("pin"))

            case "labs/lab_01/control":
                if data.get("action") == "LOCKDOWN":
                    self.state["status"] = "LOCKDOWN"

                cmd_id = data.get("cmd_id")
                if cmd_id:
                    client.publish(f"labs/lab_01/response/{cmd_id}",
                                   json.dumps({"status": "success", "cmd_id": cmd_id}))

    def handle_rfid(self, entered_uid):
        """
        Rozpoznawanie poprawnosci RFID

        :param entered_uid:
        :return:
        """

        # W przypadku niepoprawnego uwierzytelnienia
        if self.auth_in_progress or entered_uid not in self.whitelist:
            print("Błąd karty")
            return
        else:
            print("Karta rozpoznana")

        self.auth_in_progress = True
        self.current_rfid = entered_uid

        self.auth_timer = threading.Timer(10.0, self.auth_timeout)
        self.auth_timer.start()

    def handle_pin(self, entered_pin):
        """
        Sprawdzenie czy podany PIN jest przypisany do danego pracownika

        :param entered_pin:
        :return:
        """
        # Nie wpisujemy PIN bez karty
        if not self.auth_in_progress:
            return

        # Zatrzymanie stopera, wpisano PIN
        if self.auth_timer:
            self.auth_timer.cancel()

        # Moment sprawdzenia poprawności PIN-u
        if self.pins.get(self.current_rfid) == entered_pin:
            self.state["status"] = "DISARMED"
        else:
            self.state["status"] = "ALARM"

        self.auth_in_progress = False
        self.current_rfid = None

    def auth_timeout(self):
        """
        Przekroczono 10 sekund na wpisanie PIN-u

        :return:
        """
        if self.auth_in_progress:
            print("Nie podano PIN-u")
            self.state["status"] = "ALARM"

            # Reset systemu
            self.auth_in_progress = False
            self.current_rfid = None

    def save_offline_event(self, czas, id_urzadzenia, dane_czujnikow):
        """
        Zapis odebranych dane z czujników bezpośrednio do lokalnej bazy danych SQLite w przypadku braku połączenia do siecu
        :param czas:
        :param id_urzadzenia:
        :param dane_czujnikow:
        :return: None
        """
        self.db.execute("INSERT INTO events(czas, id_urzadzenia, dane_czujnikow) VALUES (?, ?, ?)",
                        (czas, id_urzadzenia, dane_czujnikow))
        self.db.commit()

    def sha256_hash(self, file):
        sha256 = hashlib.sha256()
        with open(file, "rb") as f:
            data_chunk = f.read(4096)
            while data_chunk:
                sha256.update(data_chunk)
                data_chunk = f.read(4096)
        return sha256.hexdigest()

    def send_video(self, file_path):
        video_hash = self.sha256_hash(file_path)
        self.client.publish("labs/lab_01/video_hash", json.dumps({"file_path": file_path, "hash": video_hash}))


usage = Endpoint()
usage.client.connect("localhost", 1883, 60)
usage.client.loop_forever()