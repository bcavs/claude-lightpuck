import requests
import json
import time

PICO_URL = "http://100.81.93.115:8080/update"

with open("test_payloads.json") as f:
    payloads = json.load(f)

for payload in payloads:
    print("Sending:", payload)
    try:
        requests.post(PICO_URL, json=payload, timeout=2)
    except Exception as e:
        print("Error:", e)
    time.sleep(5)
