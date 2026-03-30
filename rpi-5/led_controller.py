import math
import time

import board
import neopixel

from config import LED_COUNT, LED_PIN

# Map config pin number to board pin
_BOARD_PINS = {
    18: board.D18,
    21: board.D21,
    10: board.D10,
    12: board.D12,
}

_strip = None


def init_strip():
    """Initialize the NeoPixel strip. Must be called from the thread that will update it."""
    global _strip
    _strip = neopixel.NeoPixel(
        _BOARD_PINS[LED_PIN],
        LED_COUNT,
        brightness=0.2,
        auto_write=False,
        pixel_order=neopixel.GRB,
    )
    print("[LED] Strip initialized: %d pixels on GPIO%d" % (LED_COUNT, LED_PIN))


def percent_to_leds(percent, total_leds):
    percent = max(0, min(100, float(percent)))
    return int((percent / 100.0) * total_leds)


def _usage_color(percent):
    """Green at 0%, yellow at 50%, red at 100%."""
    p = max(0, min(100, float(percent)))
    if p <= 50:
        r = int(255 * (p / 50))
        g = 255
    else:
        r = 255
        g = int(255 * ((100 - p) / 50))
    return (r, g, 0)


def update_strip(percent, leds_on, total_leds, mode):
    """Drive the NeoPixel strip and log state to console."""
    color = _usage_color(percent)
    for i in range(total_leds):
        _strip[i] = color if i < leds_on else (0, 0, 0)
    _strip.show()

    if total_leds <= 0:
        print("[LED] mode=%s — no pixels configured" % mode)
        return
    bar = "#" * leds_on + "." * (total_leds - leds_on)
    print(
        "[LED] mode=%s util=%s%% | %d/%d on | %s"
        % (mode, percent, leds_on, total_leds, bar)
    )


def update_strip_dual(five_hour_pct, seven_day_pct):
    """Drive two halves of the ring: first 12 = five-hour, last 12 = seven-day."""
    half = LED_COUNT // 2

    five_on = percent_to_leds(five_hour_pct, half)
    five_color = _usage_color(five_hour_pct)

    seven_on = percent_to_leds(seven_day_pct, half)
    seven_color = _usage_color(seven_day_pct)

    for i in range(half):
        _strip[i] = five_color if i < five_on else (0, 0, 0)
    for i in range(half):
        _strip[half + i] = seven_color if i < seven_on else (0, 0, 0)
    _strip.show()

    bar5 = "#" * five_on + "." * (half - five_on)
    bar7 = "#" * seven_on + "." * (half - seven_on)
    print(
        "[LED] dual | 5h=%s%% %d/%d %s | 7d=%s%% %d/%d %s"
        % (five_hour_pct, five_on, half, bar5, seven_day_pct, seven_on, half, bar7)
    )


def heartbeat_breathe():
    """Slow amber breathing pulse — called repeatedly from the main loop."""
    bright = (math.sin(time.time() * 1.5 - math.pi / 2) + 1) / 2
    r = int(255 * bright)
    g = int(100 * bright)
    _strip.fill((r, g, 0))
    _strip.show()


def flash(color=(0, 255, 0), duration=0.4):
    """Brief full-ring flash, then off. Called from the main thread."""
    _strip.fill(color)
    _strip.show()
    time.sleep(duration)
    _strip.fill((0, 0, 0))
    _strip.show()


def clear_strip():
    """Turn off all LEDs."""
    if _strip is not None:
        _strip.fill((0, 0, 0))
        _strip.show()
