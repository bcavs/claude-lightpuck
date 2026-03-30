#!/usr/bin/env python3
"""
Raspberry Pi 4 LED server for Claude Lightpuck.

Run on the Pi:
  cd claude-lightpuck/rpi-5 && sudo python3 main.py
"""
import threading

from http.server import ThreadingHTTPServer

from config import HOST, HTTP_PORT, LED_COUNT, MODE
from led_controller import init_strip, update_strip, clear_strip, percent_to_leds
from server import LightpuckHandler, latest_usage


def main() -> None:
    # Initialize strip in main thread
    init_strip()

    # Run HTTP server in a background thread
    httpd = ThreadingHTTPServer((HOST, HTTP_PORT), LightpuckHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print("HTTP server on http://%s:%s (POST /update, GET /health)" % (HOST, HTTP_PORT))

    # LED update loop runs in main thread
    stop = threading.Event()
    try:
        while not stop.is_set():
            percent = latest_usage.get(f"{MODE}_utilization", 0)
            leds_on = percent_to_leds(percent, LED_COUNT)
            update_strip(percent, leds_on, LED_COUNT, MODE)
            stop.wait(5)
    except KeyboardInterrupt:
        pass

    print("Shutting down...")
    clear_strip()
    httpd.shutdown()
    httpd.server_close()


if __name__ == "__main__":
    main()
