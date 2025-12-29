import apiClient from "./apiClient";
import { Reservation } from "../types/reservations";

export async function fetchAllReservations(): Promise<Reservation[]> {
  const res = await apiClient.get("/reservations/list/");
  return res.data.reservations;
}

export async function cancelReservation(id: number) {
  const res = await apiClient.delete(`/reservations/${id}/`);
  return res.data;
}
