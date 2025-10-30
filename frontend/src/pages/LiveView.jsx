import { useEffect, useState } from "react";
import apiClient from "../api/apiClient";

export default function LiveView() {
  const [snapshot, setSnapshot] = useState(null);
  const [error, setError] = useState("");

  // Fetch the latest snapshot from the backend
  const fetchLive = async () => {
    try {
      const res = await apiClient.get("/live/");
      setSnapshot(res.data.latest_snapshot);
      setError("");
    } catch (e) {
      console.error("Failed to fetch live data", e);
      setError("Cannot connect to backend");
    }
  };

  // Run fetchLive every 5 seconds
  useEffect(() => {
    fetchLive();
    const id = setInterval(fetchLive, 5000);
    return () => clearInterval(id);
  }, []);

  if (error) {
    return <div className="p-6 text-red-600">{error}</div>;
  }

  if (!snapshot) {
    return <div className="p-6 text-gray-500">Waiting for data...</div>;
  }

  // Use annotated image for display
  const imageUrl = `${snapshot.annotated_url}?t=${Date.now()}`;

  return (
    <div className="p-6 space-y-4 text-center">
      <h2 className="text-3xl font-semibold mb-2">Live Parking Status</h2>

      <div className="flex justify-center gap-3 flex-wrap mb-4">
        <span className="px-4 py-2 bg-green-100 text-green-800 rounded">
            Empty: {snapshot.empty}
        </span>
        <span className="px-4 py-2 bg-red-100 text-red-800 rounded">
            Occupied: {snapshot.occupied}
        </span>
        <span className="px-4 py-2 bg-gray-100 text-gray-700 rounded">
          ⏱ {new Date(snapshot.timestamp).toLocaleString()}
        </span>
      </div>

      <div className="flex justify-center">
        <img
          src={imageUrl}
          alt="YOLO detected parking"
          className="rounded-xl shadow-lg max-h-[75vh] object-contain"
          onError={() => setError("Failed to load image")}
        />
      </div>
    </div>
  );
}
