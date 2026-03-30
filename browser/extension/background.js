const PICO_URL = "http://100.81.93.115:8080/update";

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type !== "usage") return;
  fetch(PICO_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(msg.payload),
  })
    .then((res) => console.log("[Lightpuck] Sent, status:", res.status))
    .catch((err) => console.error("[Lightpuck] Send error:", err));
});
