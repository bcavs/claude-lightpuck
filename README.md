# Claude Lightpuck

A physical LED progress bar that visualizes your [Claude](https://claude.ai) usage limits in real time.

As your usage increases, the light fills up — just like the usage bars in the Claude UI.

## Architecture

```
Claude Web App (claude.ai)
        |
Browser Extension / Userscript
  (fetch /api/organizations/.../usage)
        |
Local Network (HTTP POST)
        |
Raspberry Pi (Pico 2 W or Pi 5)
        |
LED Strip (progress bar)
```

## How It Works

Claude's web app exposes an internal API:

```
GET /api/organizations/{org_id}/usage
```

```json
{
  "five_hour": { "utilization": 65.0 },
  "seven_day": { "utilization": 54.0 }
}
```

A browser extension fetches this from your logged-in session, extracts the usage percentages, and POSTs them to the Pi, which converts the percentage to an LED fill level.

## Hardware

**Required:**
- Raspberry Pi Pico 2 W (or Pi 5 for development)
- WS2812B (NeoPixel) LED strip (recommended: 30-60 LEDs)
- 5V power supply (for LEDs)
- Breadboard + wires

**Recommended:**
- 330 ohm resistor (data line)
- 1000uF capacitor (power smoothing)
- Logic level shifter (optional but safer for long strips)

### Wiring

```
Pico 2 W          LED Strip
─────────          ─────────
GPIO (data)  ───>  DIN
GND          ───>  GND
External 5V  ───>  VCC
```

> Do NOT power LEDs from the Pico. Always share ground between Pico and LED power supply.

## Getting Started

### 1. Start the server on your Pi

**Pico 2 W (MicroPython):** Flash MicroPython, copy `pico/*.py` and a `secrets.py` (see `pico/secrets.example.py`) to the device. It runs `main.py` on boot.

**Raspberry Pi 5 (development):**

```bash
cd rpi-5 && python3 main.py
```

Server listens on `0.0.0.0:8080`.

### 2. Install the browser extension

1. Go to `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `browser/extension/` folder
4. Edit `content.js` to set your `ORG_ID` and `background.js` to set your Pi's IP
5. Navigate to claude.ai — polling starts automatically every 30 seconds

### 3. Test without a browser

```bash
cd tools && python3 mock_sender.py
```

Edit `PICO_URL` in `mock_sender.py` to point at your Pi. Sends test payloads from `test_payloads.json` at 5-second intervals. Requires `requests` (`pip install requests`).

## Project Structure

```
browser/          Browser extension and userscript
  extension/      Chrome extension (content script + background worker)
  userscript/     Standalone console script alternative
pico/             MicroPython firmware for Pico 2 W
rpi-5/            CPython server for Raspberry Pi 5
shared/           Payload schema shared across components
tools/            Mock sender for testing
docs/             Hardware and API notes
```

## Notes

- This uses an internal Claude API (not officially supported)
- It may break if API endpoints, auth/session behavior, or UI changes
- LED driving is currently stubbed — `led_controller.py` logs a text progress bar to the console. GPIO/NeoPixel integration is not yet implemented.
