import network
import time
from secrets import WIFI_SSID, WIFI_PASSWORD

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)

    print("Connected:", wlan.ifconfig())
    return wlan
