import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D18, 24, brightness=0.2, auto_write=True)

pixels.fill((255, 0, 0))  # RED
time.sleep(10)