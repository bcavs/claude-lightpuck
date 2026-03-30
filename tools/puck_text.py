import time
import board
import neopixel

# ===== CONFIG =====
NUM_PIXELS = 24       # change if needed
PIN = board.D18      # GPIO18 (Pin 12)
BRIGHTNESS = 0.2     # keep low for testing
ORDER = neopixel.GRB # try RGB if colors look wrong
# ==================

pixels = neopixel.NeoPixel(
    PIN,
    NUM_PIXELS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER,
)

def color_wipe(color, wait=0.02):
    for i in range(NUM_PIXELS):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

try:
    print("Running LED test...")

    # Red
    color_wipe((255, 0, 0))
    time.sleep(0.5)

    # Green
    color_wipe((0, 255, 0))
    time.sleep(0.5)

    # Blue
    color_wipe((0, 0, 255))
    time.sleep(0.5)

    # Loop animation
    while True:
        for i in range(NUM_PIXELS):
            pixels[i] = (255, 255, 255)
        pixels.show()
        time.sleep(1)

        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(1)

except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()