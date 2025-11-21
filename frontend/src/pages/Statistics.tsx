import { useEffect, useState } from "react";
import apiClient from "../api/apiClient";

// Represents a single daily statistics entry when grouping by date.
interface DailyResult {
  date: string;
  total_snapshots: number;
  total_empty: number;
  total_occupied: number;
  occupancy_rate: number;
}

// Response shape of the /stats/ endpoint.
// It can either return aggregated totals or a list of daily grouped results.
interface StatsResponse {
  total_snapshots?: number;
  total_empty?: number;
  total_occupied?: number;
  occupancy_rate?: number;
  latest_snapshot?: {
    image_name: string;
    timestamp: string;
    empty: number;
    occupied: number;
  };
  results?: DailyResult[];
  filters?: {
    site?: string | null;
    date?: string | null;
    start?: string | null;
    end?: string | null;
    search?: string | null;
    group_by?: string | null;
  };
}

// Basic parking lot structure used in the dropdown.
interface ParkingLot {
  code: string;
  name: string;
}

// Response shape of /parking-lots/ endpoint.
interface ParkingLotsResponse {
  parking_lots: ParkingLot[];
}

export default function Statistics() {
  // Current stats response (either aggregated or grouped).
  const [stats, setStats] = useState<StatsResponse | null>(null);

  // Error message for failed API calls.
  const [error, setError] = useState("");

  // groupBy: "" or "date".
  const [groupBy, setGroupBy] = useState("");

  // Date range filters.
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  // List of parking lots fetched from backend.
  const [parkingLots, setParkingLots] = useState<ParkingLot[]>([]);

  // Currently selected parking lot in dropdown ("ALL" = all parking lots combined).
  const [selectedSite, setSelectedSite] = useState<string>("ALL");

  // Fetch all parking lots from backend to populate the dropdown.
  const fetchParkingLots = async () => {
    try {
      const res = await apiClient.get<ParkingLotsResponse>("/parking-lots/");
      setParkingLots(res.data.parking_lots);
    } catch {
      // Parking lots list is nice to have, but not critical.
      console.warn("Failed to fetch parking lots.");
    }
  };

  // Fetch statistics from backend using current filters.
  const fetchStats = async () => {
    try {
      const params: Record<string, string> = {};

      // Only send site parameter when user selects a specific parking lot.
      if (selectedSite && selectedSite !== "ALL") {
        params.site = selectedSite;
      }

      // group_by filter (e.g. "date").
      if (groupBy) params.group_by = groupBy;

      // Date range filters.
      if (start && end) {
        params.start = start;
        params.end = end;
      }

      const res = await apiClient.get<StatsResponse>("/stats/", { params });
      setStats(res.data);
      setError("");
    } catch {
      setError("Failed to fetch statistics from backend.");
    }
  };

  // Initial load: fetch parking lots and initial stats.
  useEffect(() => {
    fetchParkingLots();
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Re-fetch stats when parking lot changes
  useEffect(() => {
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSite]);

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-3xl font-semibold text-center">Parking Statistics</h2>

      {/* Filter controls (parking lot + date range + grouping) */}
      <div className="flex justify-center gap-4 flex-wrap">
        {/* Parking lot dropdown. "ALL" means aggregated stats for all parking lots. */}
        <div>
          <label className="text-sm text-gray-600">Parking Lot</label>
          <select
            className="border rounded p-2 ml-2"
            value={selectedSite}
            onChange={(e) => setSelectedSite(e.target.value)}
          >
            <option value="ALL">All parking lots</option>
            {parkingLots.map((lot) => (
              <option key={lot.code} value={lot.code}>
                {lot.name} ({lot.code})
              </option>
            ))}
          </select>
        </div>

        {/* Start date filter */}
        <div>
          <label className="text-sm text-gray-600">Start Date</label>
          <input
            type="date"
            className="border rounded p-2 ml-2"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </div>

        {/* End date filter */}
        <div>
          <label className="text-sm text-gray-600">End Date</label>
          <input
            type="date"
            className="border rounded p-2 ml-2"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </div>

        {/* Grouping select (no grouping or grouped by date) */}
        <select
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value)}
          className="border rounded p-2"
        >
          <option value="">No grouping</option>
          <option value="date">Group by Date</option>
        </select>

        {/* Apply filters button triggers API call with current filter state */}
        <button
          onClick={fetchStats}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Apply Filters
        </button>
      </div>

      {/* Error display, if API call fails */}
      {error && <p className="text-red-500 text-center">{error}</p>}

      {/* If backend returned grouped 'results', show table view */}
      {stats && stats.results ? (
        <table className="min-w-full border border-gray-300 rounded-lg shadow mt-6">
          <thead className="bg-blue-100">
            <tr>
              <th className="px-4 py-2 border">Date</th>
              <th className="px-4 py-2 border">Snapshots</th>
              <th className="px-4 py-2 border">Empty</th>
              <th className="px-4 py-2 border">Occupied</th>
              <th className="px-4 py-2 border">% Occupancy</th>
            </tr>
          </thead>
          <tbody>
            {stats.results.map((item, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-4 py-2 border">{item.date}</td>
                <td className="px-4 py-2 border">{item.total_snapshots}</td>
                <td className="px-4 py-2 border text-green-700">
                  {item.total_empty}
                </td>
                <td className="px-4 py-2 border text-red-700">
                  {item.total_occupied}
                </td>
                <td className="px-4 py-2 border font-semibold">
                  {item.occupancy_rate}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        // Otherwise show aggregated totals (no grouping mode)
        stats && (
          <div className="text-center text-lg">
            <p>
              Total Snapshots:{" "}
              <strong>{stats.total_snapshots ?? 0}</strong> | Empty:{" "}
              <strong className="text-green-600">
                {stats.total_empty ?? 0}
              </strong>{" "}
              | Occupied:{" "}
              <strong className="text-red-600">
                {stats.total_occupied ?? 0}
              </strong>{" "}
              | Occupancy:{" "}
              <strong>{stats.occupancy_rate ?? 0}%</strong>
            </p>
          </div>
        )
      )}
    </div>
  );
}
