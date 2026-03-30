from wifi import connect
from server import latest_usage
from led_controller import percent_to_leds
from config import LED_COUNT, MODE

# Placeholder main loop
connect()

print("Starting main loop...")

while True:
    percent = latest_usage.get(f"{MODE}_utilization", 0)
    leds_on = percent_to_leds(percent, LED_COUNT)

    print(f"Mode: {MODE} | Percent: {percent} | LEDs: {leds_on}")

    # TODO: update LED strip here

    import time
    time.sleep(5)
