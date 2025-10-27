# --- Django bootstrap (force the correct path) ---
import os, sys, json
from pathlib import Path
import paho.mqtt.client as mqtt

# project root: .../smart_store
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# put the *inner* phase1 (the one that contains settings.py) first on sys.path
sys.path.insert(0, str((PROJECT_ROOT / "phase1").resolve()))

# now phase1.settings will resolve to the right module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phase1.settings")

import django
django.setup()

from smartstore.models import Fridge
from django.utils import timezone
from email_alerts import send_alert

# ---- MQTT bits (unchanged) ----
BROKER = "localhost"
PORT = 1883
TOPICS = ["frig1", "frig2"]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Connected to MQTT broker")
        for t in TOPICS:
            client.subscribe(t)
            print("📡 Subscribed to", t)
    else:
        print(" Connection failed with rc =", rc)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        temp = float(data.get("temperature"))
        hum  = float(data.get("humidity"))
    except Exception as e:
        print(" Bad payload on", msg.topic, ":", msg.payload, "| err:", e)
        return

    try:
        f = Fridge.objects.get(topic=msg.topic)
        f.temperature = temp
        f.humidity = hum
        f.save(update_fields=["temperature", "humidity", "updated_at"])
        print(f" Updated {f.name}: {temp}°C, {hum}%")
        
        if f.alert_email and f.temp_threshold is not None and temp > f.temp_threshold:
           
            should = not f.last_alert_ts or (timezone.now() - f.last_alert_ts).total_seconds() > 600
            if should:
                send_alert(f.alert_email, f.id, f.name, f.topic, temp)
                f.last_alert_ts = timezone.now()
                f.save(update_fields=["last_alert_ts"])
    except Fridge.DoesNotExist:
        print(" No Fridge row for topic:", msg.topic)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()
