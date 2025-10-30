import { useEffect, useState } from "react";
import apiClient from "../api/apiClient";

interface StatsResponse {
  total_snapshots: number;
  total_empty: number;
  total_occupied: number;
  occupancy_rate: number;
  latest_snapshot?: {
    image_name: string;
    timestamp: string;
    empty: number;
    occupied: number;
  };
  results?: {
    date: string;
    total_snapshots: number;
    total_empty: number;
    total_occupied: number;
    occupancy_rate: number;
  }[];
}

export default function Statistics() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [error, setError] = useState("");
  const [groupBy, setGroupBy] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  const fetchStats = async () => {
    try {
      const params: Record<string, string> = {};
      if (groupBy) params.group_by = groupBy;
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

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-3xl font-semibold text-center">Parking Statistics</h2>

      {/* Filters */}
      <div className="flex justify-center gap-4 flex-wrap">
        <div>
          <label className="text-sm text-gray-600">Start Date</label>
          <input
            type="date"
            className="border rounded p-2 ml-2"
            value={start}
            onChange={(e) => setStart(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm text-gray-600">End Date</label>
          <input
            type="date"
            className="border rounded p-2 ml-2"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </div>

        <select
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value)}
          className="border rounded p-2"
        >
          <option value="">No grouping</option>
          <option value="date">Group by Date</option>
        </select>

        <button
          onClick={fetchStats}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Apply Filters
        </button>
      </div>

      {error && <p className="text-red-500 text-center">{error}</p>}

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
                <td className="px-4 py-2 border text-green-700">{item.total_empty}</td>
                <td className="px-4 py-2 border text-red-700">{item.total_occupied}</td>
                <td className="px-4 py-2 border font-semibold">{item.occupancy_rate}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        stats && (
          <div className="text-center text-lg">
            <p>
              Total Snapshots: <strong>{stats.total_snapshots}</strong> |
              Empty: <strong className="text-green-600">{stats.total_empty}</strong> |
              Occupied: <strong className="text-red-600">{stats.total_occupied}</strong> |
              Occupancy: <strong>{stats.occupancy_rate}%</strong>
            </p>
          </div>
        )
      )}
    </div>
  );
}
