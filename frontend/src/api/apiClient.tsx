import axios from "axios";
//Bridge between frontend and backend(React---->Django)
const apiClient = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
});

export default apiClient;
