// Reads API base URL from Expo environment variables.
// Must be prefixed with EXPO_PUBLIC_ to be available in the app bundle.
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

// Converts backend "localhost" URLs to device-accessible URLs
export function normalizeMediaUrl(url: string): string {
  if (!url) return url;

  // API_BASE_URL example: http://192.168.2.3:8000/api
  const hostBase = API_BASE_URL.replace("/api", ""); // -> http://192.168.2.3:8000

  return url
    .replace("http://localhost:8000", hostBase)
    .replace("http://127.0.0.1:8000", hostBase);
}
