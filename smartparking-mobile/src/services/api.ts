import axios from "axios";

// Read from EAS/Expo env vars.
// In Expo, only variables prefixed with EXPO_PUBLIC_ are available in the app bundle.
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

// Central axios instance for backend requests
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});
