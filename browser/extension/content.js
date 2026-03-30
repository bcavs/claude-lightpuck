const ORG_ID = "2597a8c5-04b5-4cc5-8f80-b5240e6bd9ff";

async function fetchUsage() {
  const res = await fetch(`/api/organizations/${ORG_ID}/usage`, {
    credentials: "include",
  });
  const data = await res.json();
  return {
    five_hour_utilization: data.five_hour?.utilization ?? 0,
    seven_day_utilization: data.seven_day?.utilization ?? 0,
    timestamp: new Date().toISOString(),
  };
}

async function poll() {
  try {
    const payload = await fetchUsage();
    console.log("[Lightpuck] Sending:", payload);
    chrome.runtime.sendMessage({ type: "usage", payload });
  } catch (err) {
    console.error("[Lightpuck] Error:", err);
  }
}

poll();
setInterval(poll, 30000);
