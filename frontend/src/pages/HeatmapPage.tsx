import { useEffect, useState } from "react";
import api from "../api/apiClient";
import HeatmapCanvas from "../components/HeatmapCanvas";

interface ParkingLot {
  code: string;
  name: string;
}

export default function HeatmapPage() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [selectedLot, setSelectedLot] = useState<string>("");

  // Load parking lots once on mount
  useEffect(() => {
    async function fetchLots() {
      try {
        const res = await api.get("/parking-lots/");
        setLots(res.data.parking_lots);

        if (res.data.parking_lots.length > 0) {
          setSelectedLot(res.data.parking_lots[0].code);
        }
      } catch (err) {
        console.error("Error loading parking lots:", err);
      }
    }
    fetchLots();
  }, []);

  return (
    // Outer container centers everything vertically & horizontally
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      {/* Card container */}
      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-4xl">
        {/* Title */}
        <h2 className="text-2xl font-semibold mb-4 text-center">
          Parking Heatmap
        </h2>

        {/* Selector row */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-4">
          <label className="font-medium">
            Select Parking Lot:
          </label>
          <select
            value={selectedLot}
            onChange={(e) => setSelectedLot(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {lots.map((lot) => (
              <option key={lot.code} value={lot.code}>
                {lot.name} ({lot.code})
              </option>
            ))}
          </select>
        </div>

        {/* Separator */}
        <hr className="my-4" />

        {/* Heatmap area centered */}
        <div className="flex items-center justify-center">
          {selectedLot ? (
            <HeatmapCanvas site={selectedLot} />
          ) : (
            <p className="text-gray-500">Loading heatmap…</p>
          )}
        </div>
      </div>
    </div>
  );
}
