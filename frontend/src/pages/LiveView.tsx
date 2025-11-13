import { useEffect, useState } from "react";
import api from "../api/apiClient";

// Shape of the nested snapshot object coming from backend
interface LatestSnapshot {
  annotated_url: string;
  empty: number;
  occupied: number;
  timestamp: string;
}

// Response from /api/parking-lots/
interface ParkingLot {
  code: string;
  name: string;
}

// Response from /api/live/?site=...
interface LiveApiResponse {
  site: string;
  latest_snapshot: LatestSnapshot | null;
}

export default function LiveView() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [selectedLot, setSelectedLot] = useState<string>("");
  const [snapshot, setSnapshot] = useState<LatestSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingLots, setLoadingLots] = useState<boolean>(true);
  const [loadingSnapshot, setLoadingSnapshot] = useState<boolean>(false);

  // Load parking lots on mount
  useEffect(() => {
    async function fetchLots() {
      try {
        setLoadingLots(true);
        setError(null);

        const res = await api.get("/parking-lots/");
        const parkingLots: ParkingLot[] = res.data.parking_lots || [];

        setLots(parkingLots);
        if (parkingLots.length > 0) {
          setSelectedLot(parkingLots[0].code);
        }
      } catch (err) {
        console.error("Error loading parking lots:", err);
        setError("Failed to load parking lots");
      } finally {
        setLoadingLots(false);
      }
    }

    fetchLots();
  }, []);

  // Load latest snapshot whenever selectedLot changes
  useEffect(() => {
    if (!selectedLot) return;

    let isCancelled = false;

    async function fetchSnapshot() {
      try {
        setLoadingSnapshot(true);
        setError(null);

        // IMPORTANT: match backend URL: /api/live/?site=UFPR04
        const res = await api.get<LiveApiResponse>(`/live/?site=${selectedLot}`);

        if (!isCancelled) {
          if (res.data.latest_snapshot) {
            setSnapshot(res.data.latest_snapshot);
          } else {
            setSnapshot(null);
          }
        }
      } catch (err) {
        console.error("Error loading latest snapshot:", err);
        if (!isCancelled) {
          setError("Failed to load latest snapshot");
          setSnapshot(null);
        }
      } finally {
        if (!isCancelled) {
          setLoadingSnapshot(false);
        }
      }
    }

    fetchSnapshot();

    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchSnapshot, 5000);

    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [selectedLot]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-4xl">
        <h2 className="text-2xl font-semibold mb-4 text-center">
          Live Parking Status
        </h2>

        {/* Parking lot selector */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-6">
          <label className="font-medium">Select Parking Lot:</label>

          {loadingLots ? (
            <span className="text-gray-500 text-sm">Loading lots…</span>
          ) : lots.length === 0 ? (
            <span className="text-red-500 text-sm">
              No parking lots registered.
            </span>
          ) : (
            <select
              value={selectedLot}
              onChange={(e) => setSelectedLot(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2 text-sm focus:ring-blue-500"
            >
              {lots.map((lot) => (
                <option key={lot.code} value={lot.code}>
                  {lot.name} ({lot.code})
                </option>
              ))}
            </select>
          )}
        </div>

        <hr className="my-4" />

        {/* Error message */}
        {error && (
          <p className="text-center text-red-500 mb-4 text-sm">{error}</p>
        )}

        {/* Metrics */}
        {snapshot && (
          <div className="flex justify-center gap-6 text-lg mb-4">
            <div className="bg-green-100 px-4 py-2 rounded-lg shadow">
              Empty: <b>{snapshot.empty}</b>
            </div>
            <div className="bg-red-100 px-4 py-2 rounded-lg shadow">
              Occupied: <b>{snapshot.occupied}</b>
            </div>
          </div>
        )}

        {/* Snapshot image */}
        <div className="flex items-center justify-center min-h-[280px]">
          {loadingSnapshot ? (
            <p className="text-gray-500">Loading latest image…</p>
          ) : snapshot ? (
            <img
              src={snapshot.annotated_url}
              alt="Latest snapshot"
              className="rounded-lg shadow-lg max-h-[500px]"
            />
          ) : (
            <p className="text-gray-500">
              No snapshot available for this parking lot yet.
            </p>
          )}
        </div>

        {/* Timestamp */}
        {snapshot && (
          <p className="text-center text-gray-500 text-sm mt-4">
            Updated at: {new Date(snapshot.timestamp).toLocaleString()}
          </p>
        )}
      </div>
    </div>
  );
}
