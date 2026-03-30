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
_last_log_msg = None
_last_log_time = 0.0
LOG_INTERVAL = 5.0


def _log(msg):
    """Only print if the message changed or LOG_INTERVAL has elapsed."""
    global _last_log_msg, _last_log_time
    now = time.time()
    if msg != _last_log_msg or (now - _last_log_time) >= LOG_INTERVAL:
        print(msg)
        _last_log_msg = msg
        _last_log_time = now


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


SPARK_PERIOD = 3.0  # seconds per sweep across the lit LEDs


def _spark_overlay(base_color, index, leds_on, stale=False):
    """Blend a spark onto a lit LED. White when connected, red when stale."""
    if leds_on <= 0:
        return base_color
    pos = (time.time() % SPARK_PERIOD) / SPARK_PERIOD * leds_on
    dist = abs(index - pos)
    if dist > 1.0:
        return base_color
    blend = (1.0 - dist) * 0.7
    if stale:
        target = (255, 0, 0)
    else:
        target = (255, 255, 255)
    r = int(base_color[0] + (target[0] - base_color[0]) * blend)
    g = int(base_color[1] + (target[1] - base_color[1]) * blend)
    b = int(base_color[2] + (target[2] - base_color[2]) * blend)
    return (r, g, b)


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
    """Drive the NeoPixel strip with a trailing spark on lit LEDs."""
    color = _usage_color(percent)
    for i in range(total_leds):
        if i < leds_on:
            _strip[i] = _spark_overlay(color, i, leds_on)
        else:
            _strip[i] = (0, 0, 0)
    _strip.show()

    if total_leds <= 0:
        _log("[LED] mode=%s — no pixels configured" % mode)
        return
    bar = "#" * leds_on + "." * (total_leds - leds_on)
    _log(
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
        if i < five_on:
            _strip[i] = _spark_overlay(five_color, i, five_on)
        else:
            _strip[i] = (0, 0, 0)
    for i in range(half):
        if i < seven_on:
            _strip[half + i] = _spark_overlay(seven_color, i, seven_on)
        else:
            _strip[half + i] = (0, 0, 0)
    _strip.show()

    bar5 = "#" * five_on + "." * (half - five_on)
    bar7 = "#" * seven_on + "." * (half - seven_on)
    _log(
        "[LED] dual | 5h=%s%% %d/%d %s | 7d=%s%% %d/%d %s"
        % (five_hour_pct, five_on, half, bar5, seven_day_pct, seven_on, half, bar7)
    )


def clock_sweep():
    """A dim blue dot sweeps around the full ring once per minute, with a fading tail."""
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


def update_strip_split(percent):
    """Split personality: top half (0-11) = usage fill, bottom half (12-23) = clock sweep."""
    half = LED_COUNT // 2

    # Top half: usage fill from LED 0 clockwise
    leds_on = percent_to_leds(percent, half)
    color = _usage_color(percent)
    for i in range(half):
        if i < leds_on:
            _strip[i] = _spark_overlay(color, i, leds_on)
        else:
            _strip[i] = (0, 0, 0)

    # Bottom half: clock sweep (one lap per minute across 12 LEDs)
    seconds = time.time() % 60
    pos = seconds / 60.0 * half
    tail = 3
    for i in range(half):
        dist = (pos - i) % half
        if dist < tail:
            fade = 1.0 - (dist / tail)
            _strip[half + i] = (0, 0, int(80 * fade * fade))
        else:
            _strip[half + i] = (0, 0, 0)

    _strip.show()

    bar = "#" * leds_on + "." * (half - leds_on)
    _log(
        "[LED] split | util=%s%% %d/%d %s | clock active"
        % (percent, leds_on, half, bar)
    )


def heartbeat_breathe(percent=None, leds_on=None, total_leds=None):
    """Breathing pulse showing last known usage level, or amber if no data."""
    bright = (math.sin(time.time() * 1.5 - math.pi / 2) + 1) / 2
    # Keep between 0.15 and 1.0 so usage is always readable
    bright = 0.15 + bright * 0.85

    if percent is not None and leds_on is not None and leds_on > 0:
        base = (0, 0, int(150 * bright))
        for i in range(total_leds):
            if i < leds_on:
                _strip[i] = _spark_overlay(base, i, leds_on, stale=True)
            else:
                _strip[i] = (0, 0, 0)
    else:
        _strip.fill((0, 0, int(150 * bright)))

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
