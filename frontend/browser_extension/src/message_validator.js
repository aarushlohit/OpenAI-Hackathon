export function validateMessage(message) {
  if (!message || typeof message !== "object") return false;
  if (message.type !== "HERMES_SCAN_URL") return false;
  return typeof message.url === "string" && message.url.length <= 2048;
}

