function showHermesAlert(payload) {
  if (!payload || payload.risk !== "elevated") return;
  const existing = document.getElementById("hermes-sentinel-alert");
  if (existing) existing.remove();
  const panel = document.createElement("div");
  panel.id = "hermes-sentinel-alert";
  panel.textContent = `Hermes-X Alert: ${payload.entity} matches prior investigation patterns.`;
  panel.style.cssText = [
    "position:fixed",
    "top:16px",
    "right:16px",
    "z-index:2147483647",
    "background:#071014",
    "color:#e6fbff",
    "border:1px solid #00d1ff",
    "border-radius:8px",
    "padding:12px 14px",
    "font:14px system-ui,sans-serif",
    "max-width:320px",
    "box-shadow:0 12px 32px rgba(0,0,0,.35)"
  ].join(";");
  document.documentElement.appendChild(panel);
}

chrome.runtime.sendMessage({ type: "HERMES_SCAN_URL", url: location.href }, (response) => {
  if (response && response.ok) showHermesAlert(response.payload);
});

