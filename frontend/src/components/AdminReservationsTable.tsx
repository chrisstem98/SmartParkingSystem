import { useEffect, useMemo, useState } from "react";
import { Reservation } from "../types/reservations";
import {
  fetchAllReservations,
  cancelReservation,
} from "../api/reservations";

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

export default function AdminReservationsTable() {
  const [data, setData] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    const rows = await fetchAllReservations();
    setData(rows);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return data.filter(
      (r) =>
        r.site.toLowerCase().includes(q) ||
        r.device_id.toLowerCase().includes(q) ||
        String(r.id).includes(q)
    );
  }, [data, search]);

  async function onCancel(id: number) {
    if (!window.confirm(`Cancel reservation #${id}?`)) return;
    setBusyId(id);
    await cancelReservation(id);
    await load();
    setBusyId(null);
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Reservations</h1>
        <button
          onClick={load}
          className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
        >
          Refresh
        </button>
      </div>

      <input
        className="mb-4 px-3 py-2 border rounded w-80"
        placeholder="Search by site / device / id"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">ID</th>
                <th className="p-2 border">Site</th>
                <th className="p-2 border">Device</th>
                <th className="p-2 border">Start</th>
                <th className="p-2 border">End</th>
                <th className="p-2 border">Status</th>
                <th className="p-2 border">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id}>
                  <td className="p-2 border">{r.id}</td>
                  <td className="p-2 border">{r.site}</td>
                  <td className="p-2 border font-mono">{r.device_id}</td>
                  <td className="p-2 border">{formatDate(r.start_time)}</td>
                  <td className="p-2 border">{formatDate(r.end_time)}</td>
                  <td className="p-2 border">{r.status}</td>
                  <td className="p-2 border">
                    <button
                      disabled={r.status === "CANCELLED" || busyId === r.id}
                      onClick={() => onCancel(r.id)}
                      className="px-3 py-1 bg-red-500 text-white rounded disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-4 text-center opacity-60">
                    No reservations
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
