# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Lightpuck is a physical LED progress bar that visualizes Claude (claude.ai) usage limits in real time. A browser script polls Claude's internal usage API, sends the data over the local network to a microcontroller, which drives a WS2812/NeoPixel LED strip as a fill bar.

## Architecture

The system has three layers connected over HTTP:

1. **Browser layer** (`browser/`) — A userscript or Chrome extension runs on claude.ai, polls `GET /api/organizations/{org_id}/usage`, and POSTs a JSON payload to the device.
2. **Device layer** — An HTTP server receives `POST /update` with `{five_hour_utilization, seven_day_utilization}` and stores it in a shared `latest_usage` dict. A polling loop reads that dict every 5s and drives the LED output.
3. **LED controller** (`led_controller.py`) — Converts a usage percentage to an LED count. Currently logs to console (no GPIO/NeoPixel driver yet).

There are two device implementations with the same logical structure but different Python stacks:

- **`pico/`** — Targets Raspberry Pi Pico 2 W running MicroPython. Uses `asyncio` streams for the HTTP server (no stdlib `http.server`). Wi-Fi credentials come from `secrets.py` (not committed; see `secrets.example.py`).
- **`rpi-5/`** — Targets Raspberry Pi 5 running CPython. Uses `http.server.BaseHTTPRequestHandler` + `ThreadingHTTPServer`. Runs on port 8080 by default (no root needed).

Both share the same payload schema (`shared/payload-schema.json`) and the same `config.py` shape (`LED_PIN`, `LED_COUNT`, `MODE`, `HTTP_PORT`, `CORS_ALLOW_ORIGIN`).

## Running

### Pico (MicroPython)
Flash MicroPython, copy `pico/*.py` and a `secrets.py` (from `secrets.example.py`) to the device, then it auto-runs `main.py` on boot.

### Raspberry Pi 5
```bash
cd rpi-5 && python3 main.py
```
Server listens on `0.0.0.0:8080`.

### Mock testing
```bash
cd tools && python3 mock_sender.py
```
Edit `PICO_URL` in `mock_sender.py` to point at your device. Sends payloads from `test_payloads.json` with 5s intervals. Requires `requests`.

## Key Conventions

- `MODE` in config selects which utilization field to display: `"five_hour"` or `"seven_day"`. The dict key is `{MODE}_utilization`.
- The Pico HTTP server is a hand-rolled async implementation (MicroPython lacks `http.server`). The RPi 5 server uses stdlib. Keep these in sync when changing the API contract.
- LED driving is stubbed out — `log_strip_state` prints a text bar to console. Actual NeoPixel/GPIO integration is not yet implemented.
- CORS is set to `*` by default since the device lives on a LAN and receives POSTs from claude.ai origin.
