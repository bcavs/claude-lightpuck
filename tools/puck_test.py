import logging
import time
import board
import neopixel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

NUM_PIXELS = 24
PIN = board.D18
BRIGHTNESS = 0.2
ORDER = neopixel.GRB

log.info(
    "Starting puck test: pixels=%s pin=%s brightness=%s order=%s",
    NUM_PIXELS,
    PIN,
    BRIGHTNESS,
    ORDER,
)

pixels = neopixel.NeoPixel(PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER)
log.info("NeoPixel strip initialized")

log.info("Filling red (255, 0, 0) and showing")
pixels.fill((255, 0, 0))
pixels.show()
time.sleep(1)

log.info("Clearing strip and showing")
pixels.fill((0, 0, 0))
pixels.show()
time.sleep(1)

log.info("Puck test finished successfully")
