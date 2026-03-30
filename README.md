🧠 Claude Lightpuck

A physical LED progress bar that visualizes your Claude (claude.ai) usage limits in real time.

As your usage increases, the light fills up — just like the usage bars in the Claude UI.

⸻

✨ Features
• 🔄 Real-time tracking of Claude usage
• 📊 Supports:
• 5-hour session usage
• 7-day usage
• 💡 LED progress bar (WS2812 / NeoPixel)
• 📡 Wireless updates via Pico 2 W (Wi-Fi)
• ⚡ Smooth animations + color transitions (optional)

⸻

🏗️ Architecture

Claude Web App (claude.ai)
↓
Browser Script / Extension
(fetch /api/organizations/.../usage)
↓
Local Network (HTTP POST)
↓
Raspberry Pi Pico 2 W
↓
LED Strip (progress bar)

⸻

🔍 How It Works

Claude’s web app exposes an internal API:
GET /api/organizations/{org_id}/usage

Example response:
{
"five_hour": { "utilization": 65.0 },
"seven_day": { "utilization": 54.0 }
}

We: 1. Fetch this from a logged-in browser session 2. Extract usage percentages 3. Send them to the Pico 4. Convert % → LED fill

⸻

📦 Hardware

Required
• Raspberry Pi Pico 2 W
• WS2812B (NeoPixel) LED strip (recommended: 30–60 LEDs)
• 5V power supply (for LEDs)
• Breadboard + wires

Recommended
• 330Ω resistor (data line)
• 1000µF capacitor (power smoothing)
• Logic level shifter (optional but safer for long strips)

⸻

🔌 Wiring

Pico 2 W LED Strip

---

GPIO (data) --> DIN
GND ----------> GND
External 5V --> VCC

⚠️ Important:
• Do NOT power LEDs from the Pico
• Always share ground between Pico and LED power supply

⸻

💻 Software Components

1. Browser Script (Claude → JSON)

Runs in your browser (or extension) while logged into Claude:

const orgId = "<your-org-id>";

async function fetchUsage() {
const res = await fetch(`/api/organizations/${orgId}/usage`, {
credentials: "include"
});

const data = await res.json();

return {
five_hour: data.five_hour?.utilization ?? 0,
seven_day: data.seven_day?.utilization ?? 0
};
}

2. Sender (Browser → Pico)

async function sendToPico(usage) {
await fetch("http://<pico-ip>/update", {
method: "POST",
headers: {"Content-Type": "application/json"},
body: JSON.stringify(usage)
});
}

⸻

3. Pico Firmware (MicroPython)
   • Hosts a small HTTP server
   • Receives usage %
   • Updates LEDs

Example mapping:

def percent_to_leds(percent, total_leds):
return int((percent / 100) \* total_leds)

⸻

🚀 Getting Started

1. Flash Pico 2 W
   • Install MicroPython
   • Upload firmware code

2. Connect Hardware
   • Wire LED strip
   • Power externally

3. Run Browser Script
   • Open Claude usage page
   • Run script (or extension)
   • Confirm values are being sent

4. Watch the Lights
   • LEDs fill based on usage
   • Updates every ~30 seconds

⸻

🎨 Behavior Ideas
• 🟢 Green → 🟡 Yellow → 🔴 Red as usage increases
• 🔥 Pulse when >90%
• 🔄 Reset animation when limits reset
• 🔀 Toggle between 5-hour and 7-day modes

⸻

⚠️ Notes
• This uses an internal Claude API (not officially supported)
• It may break if:
• API endpoints change
• Auth/session behavior changes
• UI updates

⸻

🧩 Future Improvements
• Chrome extension (auto background polling)
• Multiple LED zones (session vs weekly)
• OLED display for exact %
• Home assistant / MQTT integration
• Sound/voice alerts

⸻

🧠 Why This Exists

Because staring at a tiny progress bar in a settings page is boring.

And a glowing, physical representation of your AI usage is objectively cooler.
