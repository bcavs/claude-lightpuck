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


def clock_sweep():
    """A dim blue dot sweeps around the ring once per minute, with a fading tail."""
    seconds = time.time() % 60
    pos = seconds / 60.0 * LED_COUNT
    tail = 4
    for i in range(LED_COUNT):
        dist = (pos - i) % LED_COUNT
        if dist < tail:
            fade = 1.0 - (dist / tail)
            _strip[i] = (0, 0, int(80 * fade * fade))
        else:
            _strip[i] = (0, 0, 0)
    _strip.show()


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


def startup_animation():
    """Quick rainbow comet swirl that collapses into a white flash."""
    tail = 8
    # Two laps of rainbow comet, accelerating
    steps = LED_COUNT * 2
    for step in range(steps):
        head = step % LED_COUNT
        speed_factor = 1.0 - (step / steps) * 0.7  # accelerate
        hue_offset = step * 10
        for i in range(LED_COUNT):
            dist = (head - i) % LED_COUNT
            if dist < tail:
                fade = 1.0 - (dist / tail)
                hue = (hue_offset + i * 256 // LED_COUNT) % 256
                r, g, b = _wheel(hue)
                _strip[i] = (int(r * fade), int(g * fade), int(b * fade))
            else:
                _strip[i] = (0, 0, 0)
        _strip.show()
        time.sleep(0.02 * speed_factor)

    # Converge: all LEDs light up in a quick cascade
    for count in range(LED_COUNT):
        _strip[count] = (255, 255, 255)
        _strip.show()
        time.sleep(0.015)

    # Brief white hold then fade out
    time.sleep(0.2)
    for bright in range(100, -1, -4):
        val = int(255 * bright / 100)
        _strip.fill((val, val, val))
        _strip.show()
        time.sleep(0.015)

    _strip.fill((0, 0, 0))
    _strip.show()


def _wheel(pos):
    """Color wheel: 0-255 -> RGB."""
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


def clear_strip():
    """Turn off all LEDs."""
    if _strip is not None:
        _strip.fill((0, 0, 0))
        _strip.show()
