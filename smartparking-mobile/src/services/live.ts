import { api } from "./api";
import { LiveResponse } from "../types/live";
import { normalizeMediaUrl } from "./url";

// Fetch live data for a specific parking lot (site is required by backend)
export async function fetchLive(site: string): Promise<LiveResponse> {
  const res = await api.get<LiveResponse>("/live/", {
    params: { site },
  });

  // Fix localhost in annotated_url so it loads on the phone
  const data = res.data;
  return {
    ...data,
    latest_snapshot: {
      ...data.latest_snapshot,
      annotated_url: normalizeMediaUrl(data.latest_snapshot.annotated_url),
    },
  };
}
