from rpi_ws281x import PixelStrip, Color
import time

LED_COUNT = 24
LED_PIN = 10
LED_BRIGHTNESS = 50

strip = PixelStrip(LED_COUNT, LED_PIN, brightness=LED_BRIGHTNESS)
strip.begin()

for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(255, 0, 0))
strip.show()

print("LEDs should be red. Waiting 10 seconds...")
time.sleep(10)

for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(0, 0, 0))
strip.show()
print("Done.")
