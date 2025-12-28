import { API_BASE_URL } from "../config/env";

// Converts backend "localhost" URLs to device-accessible URLs
export function normalizeMediaUrl(url: string): string {
  // API_BASE_URL is like: http://192.168.2.3:8000/api
  const hostBase = API_BASE_URL.replace("/api", ""); // -> http://192.168.2.3:8000

  // Replace any localhost base with the correct host base
  return url.replace("http://localhost:8000", hostBase).replace("http://127.0.0.1:8000", hostBase);
}
