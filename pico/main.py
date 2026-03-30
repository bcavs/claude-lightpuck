import asyncio

from wifi import connect
from server import latest_usage, start_http_server
from led_controller import percent_to_leds, log_strip_state
from config import LED_COUNT, MODE


async def main():
    connect()
    await start_http_server()
    print("Starting usage log loop...")

    while True:
        percent = latest_usage.get(f"{MODE}_utilization", 0)
        leds_on = percent_to_leds(percent, LED_COUNT)
        log_strip_state(percent, leds_on, LED_COUNT, MODE)
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
