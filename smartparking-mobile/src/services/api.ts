import axios from "axios";
import { API_BASE_URL } from "../config/env";

// Central axios instance for backend requests
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});
