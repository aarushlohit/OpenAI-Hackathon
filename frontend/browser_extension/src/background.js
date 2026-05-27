import { validateMessage } from "./message_validator.js";

const API_BASE = "http://localhost:8000/v1/protection";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!validateMessage(message)) {
    sendResponse({ ok: false, error: "invalid_message" });
    return false;
  }
  const domain = new URL(message.url).hostname.toLowerCase();
  fetch(`${API_BASE}/domain/${encodeURIComponent(domain)}`)
    .then((response) => response.json())
    .then((payload) => sendResponse({ ok: true, payload }))
    .catch(() => sendResponse({ ok: false, error: "lookup_failed" }));
  return true;
});

