#!/usr/bin/env python3
"""Lightpuck LED test animations. Run with: sudo python3 puck_test.py [animation]"""
import sys
import time
import math
import board
import neopixel

NUM_PIXELS = 24
PIN = board.D18
BRIGHTNESS = 0.2

pixels = neopixel.NeoPixel(
    PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False, pixel_order=neopixel.GRB
)


def fill_up():
    """Simulate usage filling from 0 to 100% with green->yellow->red gradient."""
    for count in range(NUM_PIXELS + 1):
        pct = count / NUM_PIXELS
        if pct <= 0.5:
            r, g = int(255 * pct * 2), 255
        else:
            r, g = 255, int(255 * (1 - pct) * 2)
        for i in range(NUM_PIXELS):
            pixels[i] = (r, g, 0) if i < count else (0, 0, 0)
        pixels.show()
        time.sleep(0.08)
    time.sleep(1)


def rainbow_cycle(duration=5):
    """Smooth rainbow wave across the strip."""
    start = time.time()
    while time.time() - start < duration:
        offset = (time.time() - start) * 50
        for i in range(NUM_PIXELS):
            hue = ((i * 256 // NUM_PIXELS) + int(offset)) % 256
            pixels[i] = _wheel(hue)
        pixels.show()
        time.sleep(0.02)


def breathe(color=(0, 180, 255), cycles=3):
    """Pulse all LEDs on and off like breathing."""
    for _ in range(cycles):
        for step in range(100):
            bright = (math.sin(step * math.pi / 50 - math.pi / 2) + 1) / 2
            c = tuple(int(v * bright) for v in color)
            pixels.fill(c)
            pixels.show()
            time.sleep(0.02)


def chase(color=(0, 150, 255), cycles=4):
    """Theater chase / marching lights."""
    for _ in range(cycles):
        for offset in range(3):
            for i in range(NUM_PIXELS):
                pixels[i] = color if (i + offset) % 3 == 0 else (0, 0, 0)
            pixels.show()
            time.sleep(0.12)


def comet(color=(100, 0, 255), tail=6, laps=3):
    """A comet with a fading tail sweeps around the strip."""
    for _ in range(laps):
        for head in range(NUM_PIXELS + tail):
            for i in range(NUM_PIXELS):
                dist = head - i
                if 0 <= dist < tail:
                    fade = 1.0 - (dist / tail)
                    pixels[i] = tuple(int(v * fade * fade) for v in color)
                else:
                    pixels[i] = (0, 0, 0)
            pixels.show()
            time.sleep(0.04)


def sparkle(duration=4):
    """Random twinkling sparkles."""
    import random
    start = time.time()
    pixels.fill((0, 0, 0))
    while time.time() - start < duration:
        # Fade existing
        for i in range(NUM_PIXELS):
            r, g, b = pixels[i]
            pixels[i] = (max(0, r - 15), max(0, g - 15), max(0, b - 15))
        # Light a random pixel
        idx = random.randint(0, NUM_PIXELS - 1)
        pixels[idx] = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255),
        )
        pixels.show()
        time.sleep(0.05)


def fire(duration=5):
    """Flickering fire effect in red/orange/yellow."""
    import random
    start = time.time()
    heat = [0] * NUM_PIXELS
    while time.time() - start < duration:
        # Cool down
        for i in range(NUM_PIXELS):
            heat[i] = max(0, heat[i] - random.randint(0, 30))
        # Heat rises
        for i in range(NUM_PIXELS - 1, 1, -1):
            heat[i] = (heat[i - 1] + heat[i - 2]) // 2
        # Random ignition near bottom
        if random.random() < 0.6:
            idx = random.randint(0, min(3, NUM_PIXELS - 1))
            heat[idx] = min(255, heat[idx] + random.randint(160, 255))
        # Map heat to color
        for i in range(NUM_PIXELS):
            h = heat[i]
            if h < 85:
                pixels[i] = (h * 3, 0, 0)
            elif h < 170:
                pixels[i] = (255, (h - 85) * 3, 0)
            else:
                pixels[i] = (255, 255, (h - 170) * 3)
        pixels.show()
        time.sleep(0.03)


def heartbeat(duration=6):
    """Slow amber breathing pulse — disconnected indicator."""
    start = time.time()
    while time.time() - start < duration:
        bright = (math.sin(time.time() * 1.5 - math.pi / 2) + 1) / 2
        r = int(255 * bright)
        g = int(100 * bright)
        pixels.fill((r, g, 0))
        pixels.show()
        time.sleep(0.02)


def clock(duration=10):
    """Blue dot with fading tail sweeps the ring — one lap per minute."""
    start = time.time()
    tail = 4
    while time.time() - start < duration:
        seconds = time.time() % 60
        pos = seconds / 60.0 * NUM_PIXELS
        for i in range(NUM_PIXELS):
            dist = (pos - i) % NUM_PIXELS
            if dist < tail:
                fade = 1.0 - (dist / tail)
                pixels[i] = (0, 0, int(80 * fade * fade))
            else:
                pixels[i] = (0, 0, 0)
        pixels.show()
        time.sleep(0.05)


def dual_ring(duration=5):
    """Simulate dual mode: first half = 5h usage, second half = 7d usage."""
    half = NUM_PIXELS // 2
    five_pct = 65
    seven_pct = 40

    def usage_color(pct):
        if pct <= 50:
            return (int(255 * pct / 50), 255, 0)
        return (255, int(255 * (100 - pct) / 50), 0)

    five_on = int(five_pct / 100.0 * half)
    seven_on = int(seven_pct / 100.0 * half)
    five_color = usage_color(five_pct)
    seven_color = usage_color(seven_pct)

    for i in range(half):
        pixels[i] = five_color if i < five_on else (0, 0, 0)
    for i in range(half):
        pixels[half + i] = seven_color if i < seven_on else (0, 0, 0)
    pixels.show()
    print("  5h: %d%% (%d/%d)  7d: %d%% (%d/%d)" % (five_pct, five_on, half, seven_pct, seven_on, half))
    time.sleep(duration)


def status_flash():
    """Green flash simulating data received."""
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.4)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.3)
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.4)
    pixels.fill((0, 0, 0))
    pixels.show()


def _wheel(pos):
    """Color wheel: 0-255 -> RGB, cycling R->G->B."""
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


def startup(num_pixels=NUM_PIXELS):
    """Rainbow comet swirl that collapses into a white flash."""
    tail = 8
    steps = num_pixels * 2
    for step in range(steps):
        head = step % num_pixels
        speed_factor = 1.0 - (step / steps) * 0.7
        hue_offset = step * 10
        for i in range(num_pixels):
            dist = (head - i) % num_pixels
            if dist < tail:
                fade = 1.0 - (dist / tail)
                hue = (hue_offset + i * 256 // num_pixels) % 256
                r, g, b = _wheel(hue)
                pixels[i] = (int(r * fade), int(g * fade), int(b * fade))
            else:
                pixels[i] = (0, 0, 0)
        pixels.show()
        time.sleep(0.02 * speed_factor)

    for count in range(num_pixels):
        pixels[count] = (255, 255, 255)
        pixels.show()
        time.sleep(0.015)

    time.sleep(0.2)
    for bright in range(100, -1, -4):
        val = int(255 * bright / 100)
        pixels.fill((val, val, val))
        pixels.show()
        time.sleep(0.015)

    pixels.fill((0, 0, 0))
    pixels.show()


def split(duration=10):
    """Split personality: top half usage fill, bottom half clock sweep."""
    half = NUM_PIXELS // 2
    pct = 65
    tail = 3

    def usage_color(p):
        if p <= 50:
            return (int(255 * p / 50), 255, 0)
        return (255, int(255 * (100 - p) / 50), 0)

    leds_on = int(pct / 100.0 * half)
    color = usage_color(pct)

    start = time.time()
    while time.time() - start < duration:
        # Top half: static usage
        for i in range(half):
            pixels[i] = color if i < leds_on else (0, 0, 0)
        # Bottom half: clock sweep
        seconds = time.time() % 60
        pos = seconds / 60.0 * half
        for i in range(half):
            dist = (pos - i) % half
            if dist < tail:
                fade = 1.0 - (dist / tail)
                pixels[half + i] = (0, 0, int(80 * fade * fade))
            else:
                pixels[half + i] = (0, 0, 0)
        pixels.show()
        time.sleep(0.05)


def _test_usage_color(pct):
    """Dimmed usage color matching the server's _BASE_BRIGHTNESS=0.5."""
    b = 0.5
    if pct <= 50:
        return (int(255 * (pct / 50) * b), int(255 * b), 0)
    return (int(255 * b), int(255 * ((100 - pct) / 50) * b), 0)


def _test_spark(base, index, leds_on, t):
    """Cyan-tinted spark matching the server's active spark."""
    period = 3.0
    pos = (t % period) / period * leds_on
    dist = abs(index - pos)
    if dist > 1.0:
        return base
    blend = (1.0 - dist) * 0.7
    return (
        int(max(0, base[0] * (1 - blend * 0.5))),
        int(min(255, base[1] + (255 - base[1]) * blend * 0.4)),
        int(min(255, base[2] + 200 * blend)),
    )


def spark(duration=8):
    """Usage fill at 65% with a cyan spark sweeping across the lit LEDs."""
    pct = 65
    leds_on = int(pct / 100.0 * NUM_PIXELS)
    color = _test_usage_color(pct)

    start = time.time()
    while time.time() - start < duration:
        for i in range(NUM_PIXELS):
            if i < leds_on:
                pixels[i] = _test_spark(color, i, leds_on, time.time())
            else:
                pixels[i] = (0, 0, 0)
        pixels.show()
        time.sleep(0.03)


def levels():
    """Show usage at 10%, 25%, 50%, 75%, 90%, 100% with spark — 5 seconds each."""
    test_pcts = [10, 25, 50, 75, 90, 100]
    for pct in test_pcts:
        leds_on = int(pct / 100.0 * NUM_PIXELS)
        color = _test_usage_color(pct)
        print("  %d%% — %d/%d LEDs — color %s" % (pct, leds_on, NUM_PIXELS, color))
        start = time.time()
        while time.time() - start < 5:
            for i in range(NUM_PIXELS):
                if i < leds_on:
                    pixels[i] = _test_spark(color, i, leds_on, time.time())
                else:
                    pixels[i] = (0, 0, 0)
            pixels.show()
            time.sleep(0.03)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.3)


ANIMATIONS = {
    "fill": fill_up,
    "rainbow": rainbow_cycle,
    "breathe": breathe,
    "chase": chase,
    "comet": comet,
    "sparkle": sparkle,
    "fire": fire,
    "heartbeat": heartbeat,
    "clock": clock,
    "dual": dual_ring,
    "flash": status_flash,
    "startup": startup,
    "split": split,
    "spark": spark,
    "levels": levels,
}


def run_all():
    for name, fn in ANIMATIONS.items():
        print("Running: %s" % name)
        fn()
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.5)


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "all"

    if choice == "all":
        run_all()
    elif choice in ANIMATIONS:
        print("Running: %s" % choice)
        ANIMATIONS[choice]()
    else:
        print("Available animations: all, %s" % ", ".join(ANIMATIONS))
        sys.exit(1)

    pixels.fill((0, 0, 0))
    pixels.show()
    print("Done.")
