import { api } from "./api";

export type ParkingLot = { code: string; name: string };

// Calls GET /api/parking-lots/ and returns parking_lots array
export async function fetchParkingLots(): Promise<ParkingLot[]> {
  const res = await api.get("/parking-lots/");
  return res.data.parking_lots;
}
