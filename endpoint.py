import paho-mqtt.client as mqtt
import json
import sqlite3

class Endpoint:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.state = {"status": "BOOT"}
        self.db = sqlite3.connect("buffer.db")
        self.db.execute("CREATE TABLE IF NOT EXISTS events(czas TEXT, id_urzadzenia TEXT, dane_czujnikow TEXT)")

    def on_message(self, client, userdata, message):
        if message.topic.startswith("labs/lab_01"):
            message_payload = message.payload.decode("utf-8")
            data = json.loads(message_payload)
            if data.get("action") == "LOCKDOWN":
                self.state = {"status": "LOCKDOWN"}
            cmd_id = data.get("cmd_id")
            client.publish(f"labs/lab_01/response/{cmd_id}", json.dumps({"status": "success", "cmd_id": cmd_id}))

    def save_offline_event(self, czas, id_urzadzenia, dane_czujnikow):
        self.db.execute("INSERT INTO events(czas, id_urzadzenia, dane_czujnikow) VALUES (?, ?, ?)", (czas, id_urzadzenia, dane_czujnikow))
        self.db.commit()

    def authorization(self):
        start_time = time.time()
        while time.time() - start_time < 10:
            if self.state.get("status") == "success":
                return True
            return False
