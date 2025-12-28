// Matches backend response from GET /api/live/?site=UFPR04
export type LiveSnapshot = {
  timestamp: string;
  empty: number;
  occupied: number;
  annotated_url: string; // backend currently returns localhost URL
};

export type LiveResponse = {
  site: string;
  latest_snapshot: LiveSnapshot;
};
