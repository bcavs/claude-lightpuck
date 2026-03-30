#!/usr/bin/env python3
"""
Raspberry Pi 4 LED server for Claude Lightpuck.

Run on the Pi:
  cd claude-lightpuck/rpi-5 && sudo python3 main.py
"""
import time
import threading

from http.server import ThreadingHTTPServer

from config import HOST, HTTP_PORT, LED_COUNT, MODE, HEARTBEAT_TIMEOUT
from led_controller import (
    init_strip, update_strip, update_strip_dual, clear_strip, percent_to_leds,
    heartbeat_breathe, flash, clock_sweep, startup_animation,
)
import server


def _is_connected():
    return server.last_update_time > 0 and (time.monotonic() - server.last_update_time) < HEARTBEAT_TIMEOUT


def main() -> None:
    init_strip()
    startup_animation()

    httpd = ThreadingHTTPServer((HOST, HTTP_PORT), server.LightpuckHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print("HTTP server on http://%s:%s (POST /update, GET /health)" % (HOST, HTTP_PORT))

    stop = threading.Event()
    last_seen = 0.0
    try:
        while not stop.is_set():
            if _is_connected():
                # Green flash when new data arrives
                if server.last_update_time != last_seen:
                    last_seen = server.last_update_time
                    flash((0, 255, 0))

                if MODE == "dual":
                    five = server.latest_usage.get("five_hour_utilization", 0)
                    seven = server.latest_usage.get("seven_day_utilization", 0)
                    is_idle = five == 0 and seven == 0
                else:
                    percent = server.latest_usage.get(f"{MODE}_utilization", 0)
                    is_idle = percent == 0

                if is_idle:
                    clock_sweep()
                    stop.wait(0.05)
                elif MODE == "dual":
                    update_strip_dual(five, seven)
                    stop.wait(5)
                else:
                    leds_on = percent_to_leds(percent, LED_COUNT)
                    update_strip(percent, leds_on, LED_COUNT, MODE)
                    stop.wait(5)
            else:
                heartbeat_breathe()
                stop.wait(0.05)
    except KeyboardInterrupt:
        pass

    print("Shutting down...")
    clear_strip()
    httpd.shutdown()
    httpd.server_close()


if __name__ == "__main__":
    main()
