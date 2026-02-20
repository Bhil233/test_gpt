export const apiBase = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export function getWsBaseUrl(httpBase = apiBase) {
  if (httpBase.startsWith("https://")) {
    return `wss://${httpBase.slice("https://".length)}`;
  }
  if (httpBase.startsWith("http://")) {
    return `ws://${httpBase.slice("http://".length)}`;
  }
  return httpBase;
}
