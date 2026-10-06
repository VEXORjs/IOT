import paho-mqtt.client as mqtt
import json
import sqlite3
import time
import hashlib

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
            if cmd_id:
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
