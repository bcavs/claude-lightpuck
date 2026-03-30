(async () => {
  const ORG_ID = "2597a8c5-04b5-4cc5-8f80-b5240e6bd9ff";
  const PICO_URL = "http://100.81.93.115:8080/update";

  async function poll() {
    try {
      const res = await fetch(`/api/organizations/${ORG_ID}/usage`, {
        credentials: "include",
      });

      const data = await res.json();

      const payload = {
        five_hour_utilization: data.five_hour?.utilization ?? 0,
        seven_day_utilization: data.seven_day?.utilization ?? 0,
        timestamp: new Date().toISOString(),
      };

      console.log("Sending:", payload);

      await fetch(PICO_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (err) {
      console.error("Error polling usage:", err);
    }
  }

  await poll();
  setInterval(poll, 30000);
})();
