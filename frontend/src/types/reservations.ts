export type ReservationStatus = "ACTIVE" | "CANCELLED" | "EXPIRED";

export type Reservation = {
  id: number;
  site: string;
  device_id: string;
  start_time: string;
  end_time: string;
  status: ReservationStatus;
  created_at?: string | null;
};
