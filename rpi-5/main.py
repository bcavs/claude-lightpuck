#!/usr/bin/env python3
"""
Raspberry Pi 5 test harness: same HTTP API and console LED logging as pico/.

Run on the Pi (repo cloned via SSH):
  cd claude-lightpuck/rpi-5 && python3 main.py

Point the browser userscript at http://<pi-ip>:8080/update (see config.HTTP_PORT).
"""
import signal
import threading

from http.server import ThreadingHTTPServer

from config import HOST, HTTP_PORT, LED_COUNT, MODE
from led_controller import log_strip_state, percent_to_leds
from server import LightpuckHandler, latest_usage


def _usage_log_loop(stop: threading.Event) -> None:
    while not stop.is_set():
        percent = latest_usage.get(f"{MODE}_utilization", 0)
        leds_on = percent_to_leds(percent, LED_COUNT)
        log_strip_state(percent, leds_on, LED_COUNT, MODE)
        if stop.wait(5):
            break


def main() -> None:
    stop = threading.Event()
    poller = threading.Thread(target=_usage_log_loop, args=(stop,), daemon=True)
    poller.start()

    httpd = ThreadingHTTPServer((HOST, HTTP_PORT), LightpuckHandler)

    def _shutdown(*_args):
        print("Shutting down...")
        stop.set()
        httpd.shutdown()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    print("HTTP server on http://%s:%s (POST /update, GET /health)" % (HOST, HTTP_PORT))
    httpd.serve_forever()
    httpd.server_close()


if __name__ == "__main__":
    main()
