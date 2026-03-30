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


ANIMATIONS = {
    "fill": fill_up,
    "rainbow": rainbow_cycle,
    "breathe": breathe,
    "chase": chase,
    "comet": comet,
    "sparkle": sparkle,
    "fire": fire,
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
