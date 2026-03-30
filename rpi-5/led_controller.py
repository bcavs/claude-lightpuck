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


def clear_strip():
    """Turn off all LEDs."""
    if _strip is not None:
        _strip.fill((0, 0, 0))
        _strip.show()
