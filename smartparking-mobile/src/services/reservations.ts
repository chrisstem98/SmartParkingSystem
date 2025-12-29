import { api } from "./api";
import { CreateReservationRequest, Reservation } from "../types/reservations";

// Create reservation (mobile)
export async function createReservation(payload: CreateReservationRequest): Promise<Reservation> {
  const res = await api.post<Reservation>("/reservations/", payload);
  return res.data;
}
